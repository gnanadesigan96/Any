import * as Location from 'expo-location';
import { db, listPlaces, Place, Visit } from './db';
import { distance, LatLon } from './geo';

export interface Candidate { name: string; category: string; lat: number; lon: number; distance: number }

const OVERPASS = 'https://overpass-api.de/api/interpreter';

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

/** Named businesses and points of interest around a spot, from OpenStreetMap. Nearest/most likely first. */
export async function nearbyCandidates(p: LatLon, radius = 80): Promise<Candidate[]> {
  const a = `(around:${radius},${p.lat},${p.lon})`;
  const q = `[out:json][timeout:15];(` +
    ['amenity', 'shop', 'leisure', 'tourism', 'office', 'healthcare', 'railway', 'aeroway']
      .map((k) => `nwr${a}["name"]["${k}"];`).join('') +
    `);out center 40;`;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const res = await fetch(OVERPASS, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'DayTracker/1.0' },
      body: 'data=' + encodeURIComponent(q),
      signal: controller.signal,
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
  } finally {
    clearTimeout(timer);
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
    db.runSync('UPDATE visits SET place_id=?, name=?, category=?, address=?, resolved=1 WHERE id=?',
      saved.id, saved.name, saved.kind === 'other' ? 'other' : saved.kind, saved.address, v.id);
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
