import * as Location from 'expo-location';
import { db, listPlaces, Place, savePlace, Visit } from './db';
import { distance, LatLon } from './geo';

export interface Candidate { name: string; category: string; lat: number; lon: number; distance: number }

const OVERPASS = 'https://overpass-api.de/api/interpreter';
const GOOGLE_PLACES = 'https://places.googleapis.com/v1/places:searchNearby';
// Optional. Set EXPO_PUBLIC_GOOGLE_PLACES_API_KEY in .env (or the GitHub secret) for Google's richer place data.
const GOOGLE_KEY = process.env.EXPO_PUBLIC_GOOGLE_PLACES_API_KEY ?? '';
export const usingGooglePlaces = GOOGLE_KEY.length > 0;

const CATEGORY_ICON: Record<string, string> = {
  home: '🏠', office: '🏢', restaurant: '🍽️', cafe: '☕', fast_food: '🍔', bar: '🍸', pub: '🍺',
  food_court: '🍱', ice_cream: '🍨', bakery: '🥐', supermarket: '🛒', mall: '🛍️', shop: '🛍️',
  hospital: '🏥', clinic: '🏥', pharmacy: '💊', doctors: '🩺', dentist: '🦷', school: '🏫',
  college: '🎓', university: '🎓', fitness_centre: '🏋️', gym: '🏋️', park: '🌳', place_of_worship: '🛕',
  bank: '🏦', atm: '🏧', fuel: '⛽', cinema: '🎬', hotel: '🏨', railway: '🚉', station: '🚉',
  bus_station: '🚌', airport: '✈️', other: '📍',
};
export function categoryIcon(category: string | null | undefined): string {
  return CATEGORY_ICON[category ?? 'other'] ?? '📍';
}

// Places people usually mean when they "go somewhere" rank above e.g. a bench or an ATM.
const PRIORITY: Record<string, number> = {
  restaurant: 30, cafe: 30, fast_food: 28, bar: 25, pub: 25, food_court: 25, ice_cream: 20, bakery: 20,
  cinema: 25, mall: 25, supermarket: 22, hospital: 25, clinic: 22, fitness_centre: 22, gym: 22,
  university: 20, college: 20, school: 18, place_of_worship: 18, hotel: 20, park: 10, station: 20,
  bank: 10, pharmacy: 12, fuel: 8, atm: -10, bench: -30, parking: -20, toilets: -30, waste_basket: -30,
};

/** Saved place (Home / Office / your own) that contains this point, if any. */
export function matchSavedPlace(p: LatLon, places: Place[] = listPlaces()): Place | null {
  let best: Place | null = null;
  let bestD = Infinity;
  for (const pl of places) {
    const d = distance(p, pl);
    if (d <= pl.radius && d < bestD) { best = pl; bestD = d; }
  }
  return best;
}

/**
 * Named businesses and places around a spot, most likely first.
 * Uses Google Places when a key is configured (best coverage), and OpenStreetMap as well/as a fallback.
 */
export async function nearbyCandidates(p: LatLon, radius = 80): Promise<Candidate[]> {
  const [g, o] = await Promise.all([usingGooglePlaces ? googleCandidates(p, radius) : Promise.resolve([]), osmCandidates(p, radius)]);
  const seen = new Set<string>();
  const out: Candidate[] = [];
  for (const c of [...g, ...o]) {
    const key = c.name.toLowerCase().replace(/[^a-z0-9]/g, '');
    if (seen.has(key)) continue;
    seen.add(key); out.push(c);
  }
  return out;
}

// Google place types → our categories.
function googleCategory(types: string[]): string {
  const t = types.join(' ');
  const rules: [RegExp, string][] = [
    [/coffee|cafe|tea_house/, 'cafe'], [/fast_food|hamburger|pizza|sandwich/, 'fast_food'], [/ice_cream|dessert/, 'ice_cream'],
    [/bakery/, 'bakery'], [/restaurant|food_court|meal_takeaway|diner/, 'restaurant'], [/\bbar\b|pub|night_club/, 'bar'],
    [/shopping_mall/, 'mall'], [/supermarket|grocery/, 'supermarket'], [/store|market/, 'shop'],
    [/hospital/, 'hospital'], [/dentist/, 'dentist'], [/doctor|clinic|medical/, 'clinic'], [/pharmacy|drugstore/, 'pharmacy'],
    [/gym|fitness/, 'gym'], [/university/, 'university'], [/school/, 'school'], [/church|hindu_temple|mosque|place_of_worship|synagogue/, 'place_of_worship'],
    [/movie_theater/, 'cinema'], [/lodging|hotel/, 'hotel'], [/train_station|subway_station|transit_station/, 'station'],
    [/bus_station/, 'bus_station'], [/airport/, 'airport'], [/park/, 'park'], [/bank/, 'bank'], [/atm/, 'atm'], [/gas_station/, 'fuel'],
  ];
  return rules.find(([re]) => re.test(t))?.[1] ?? 'other';
}

async function googleCandidates(p: LatLon, radius: number): Promise<Candidate[]> {
  try {
    const res = await fetchWithTimeout(GOOGLE_PLACES, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Goog-Api-Key': GOOGLE_KEY,
        'X-Goog-FieldMask': 'places.displayName,places.location,places.types,places.primaryType' },
      body: JSON.stringify({ maxResultCount: 10, rankPreference: 'DISTANCE',
        locationRestriction: { circle: { center: { latitude: p.lat, longitude: p.lon }, radius: Math.max(radius, 30) } } }),
    });
    if (!res.ok) return [];
    const json = (await res.json()) as { places?: any[] };
    const out = (json.places ?? []).filter((x) => x.displayName?.text && x.location).map((x) => {
      const category = googleCategory([x.primaryType ?? '', ...(x.types ?? [])]);
      const d = distance(p, { lat: x.location.latitude, lon: x.location.longitude });
      return { name: x.displayName.text as string, category, lat: x.location.latitude, lon: x.location.longitude, distance: d,
        score: (PRIORITY[category] ?? 0) - d * 0.6 };
    });
    out.sort((a, b) => b.score - a.score);
    return out.map(({ score: _s, ...c }) => c);
  } catch {
    return [];
  }
}

async function fetchWithTimeout(url: string, init: RequestInit, ms = 15000): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try { return await fetch(url, { ...init, signal: controller.signal }); } finally { clearTimeout(timer); }
}

async function osmCandidates(p: LatLon, radius: number): Promise<Candidate[]> {
  const a = `(around:${radius},${p.lat},${p.lon})`;
  const q = `[out:json][timeout:15];(` +
    ['amenity', 'shop', 'leisure', 'tourism', 'office', 'healthcare', 'railway', 'aeroway']
      .map((k) => `nwr${a}["name"]["${k}"];`).join('') +
    `);out center 40;`;
  try {
    const res = await fetchWithTimeout(OVERPASS, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'DayTracker/1.0' },
      body: 'data=' + encodeURIComponent(q),
    });
    if (!res.ok) return [];
    const json = (await res.json()) as { elements: any[] };
    const out: (Candidate & { score: number })[] = [];
    for (const el of json.elements ?? []) {
      const lat = el.lat ?? el.center?.lat;
      const lon = el.lon ?? el.center?.lon;
      if (lat == null || lon == null || !el.tags?.name) continue;
      const t = el.tags;
      const category: string =
        t.amenity ?? t.leisure ?? (t.shop ? (t.shop === 'mall' || t.shop === 'supermarket' ? t.shop : 'shop') : undefined) ??
        t.tourism ?? t.healthcare ?? (t.railway ? 'station' : undefined) ?? (t.aeroway ? 'airport' : undefined) ??
        (t.office ? 'office' : 'other');
      const d = distance(p, { lat, lon });
      out.push({ name: t.name, category, lat, lon, distance: d, score: (PRIORITY[category] ?? 0) - d * 0.6 });
    }
    out.sort((x, y) => y.score - x.score);
    const seen = new Set<string>();
    return out.filter((c) => (seen.has(c.name) ? false : (seen.add(c.name), true)))
      .map(({ score: _s, ...c }) => c);
  } catch {
    return [];
  }
}

async function addressFor(p: LatLon): Promise<string | null> {
  try {
    const [r] = await Location.reverseGeocodeAsync({ latitude: p.lat, longitude: p.lon });
    if (!r) return null;
    const parts = [r.name && r.name !== r.street ? r.name : null, r.street, r.district ?? r.subregion, r.city]
      .filter((x, i, arr) => x && arr.indexOf(x) === i);
    return parts.slice(0, 3).join(', ') || r.formattedAddress || null;
  } catch {
    return null;
  }
}

/**
 * Work out what a visit was: your saved place, a restaurant/shop/etc. nearby, or just the street address.
 * Network lookups can fail in the background; the visit stays "unresolved" and is retried when the app opens.
 */
export async function resolveVisit(v: Visit): Promise<void> {
  const p = { lat: v.lat, lon: v.lon };
  const saved = matchSavedPlace(p);
  if (saved) {
    const category = saved.kind !== 'other' ? saved.kind
      : db.getFirstSync<{ category: string }>('SELECT category FROM visits WHERE place_id=? AND category IS NOT NULL ORDER BY id DESC', saved.id)?.category ?? 'other';
    db.runSync('UPDATE visits SET place_id=?, name=?, category=?, address=?, resolved=1 WHERE id=?',
      saved.id, saved.name, category, saved.address, v.id);
    return;
  }
  const [cands, address] = await Promise.all([nearbyCandidates(p, 70), addressFor(p)]);
  const top = cands[0];
  const networkFailed = !cands.length && !address;
  db.runSync('UPDATE visits SET name=?, category=?, address=?, resolved=? WHERE id=?',
    top?.name ?? null, top?.category ?? 'other', address, networkFailed ? 0 : 1, v.id);
}

/** After saving/moving a place, re-label every past visit that falls inside it. */
export function relabelVisits(p: Place) {
  const visits = db.getAllSync<{ id: number; lat: number; lon: number }>('SELECT id, lat, lon FROM visits');
  db.withTransactionSync(() => {
    for (const v of visits) {
      if (distance(v, p) <= p.radius) {
        db.runSync('UPDATE visits SET place_id=?, name=?, category=?, resolved=1 WHERE id=?',
          p.id, p.name, p.kind === 'other' ? 'other' : p.kind, v.id);
      }
    }
  });
}

/**
 * You named a visit (picked a restaurant or typed "Mom's house"): remember that spot so the
 * next visit there gets the same name automatically. Shown as "Learned" in My places.
 */
export function learnName(v: Visit, name: string, category: string | null) {
  if (v.place_id) {
    const saved = listPlaces().find((p) => p.id === v.place_id);
    if (saved && !saved.learned) return; // don't override Home/Office/hand-made places
  }
  const existing = listPlaces().find((p) => p.learned && distance(p, v) <= 60);
  const id = savePlace({ id: existing?.id, name, kind: 'other', lat: v.lat, lon: v.lon, radius: 50, address: v.address, learned: 1 });
  db.runSync('UPDATE visits SET place_id=?, name=?, category=?, resolved=1 WHERE id=?', id, name, category ?? v.category, v.id);
}
