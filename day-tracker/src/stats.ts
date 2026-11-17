import { getKV, dayBounds, getVisit, listPlaces, pointsBetween, Trip, tripsOverlapping, Visit, visitsOverlapping } from './db';

export type TimelineItem =
  | { type: 'visit'; visit: Visit; start: number; end: number; ongoing: boolean }
  | { type: 'trip'; trip: Trip; start: number; end: number; ongoing: boolean; from: Visit | null; to: Visit | null };

export interface DaySummary {
  timeline: TimelineItem[];
  placeTotals: { name: string; category: string | null; ms: number; visits: number }[];
  homeMs: number; officeMs: number; otherMs: number;
  travelMs: number; distanceM: number; walkedM: number;
  modeTotals: Record<string, { ms: number; m: number }>;
  commute: { toOffice: number | null; toHome: number | null };
  start: number; end: number;
}

const clip = (s: number, e: number, from: number, to: number) => Math.max(0, Math.min(e, to) - Math.max(s, from));

export function summarizeDay(day: Date, now = Date.now()): DaySummary {
  const [from, to] = dayBounds(day);
  const end = Math.min(to, now);
  const places = listPlaces();
  const kindOf = (v: Visit | null) => (v?.place_id ? places.find((p) => p.id === v.place_id)?.kind ?? null : null);

  const visits = visitsOverlapping(from, end);
  const openTrip = getKV<{ tripId: number | null }>('engine.state', { tripId: null }).tripId;
  // Only the trip you're on right now may be open-ended.
  const trips = tripsOverlapping(from, end).filter((t) => t.end_ts != null || t.id === openTrip);

  const timeline: TimelineItem[] = [];
  for (const v of visits) {
    const vEnd = v.end_ts ?? now;
    timeline.push({ type: 'visit', visit: v, start: Math.max(v.start_ts, from), end: Math.min(vEnd, end), ongoing: v.end_ts == null });
  }
  for (const t of trips) {
    const tEnd = t.end_ts ?? now;
    timeline.push({ type: 'trip', trip: t, start: Math.max(t.start_ts, from), end: Math.min(tEnd, end),
      ongoing: t.end_ts == null, from: getVisit(t.from_visit), to: getVisit(t.to_visit) });
  }
  timeline.sort((a, b) => a.start - b.start);

  let homeMs = 0, officeMs = 0, otherMs = 0;
  const byPlace = new Map<string, { name: string; category: string | null; ms: number; visits: number }>();
  for (const v of visits) {
    const ms = clip(v.start_ts, v.end_ts ?? now, from, end);
    const kind = kindOf(v);
    if (kind === 'home') homeMs += ms; else if (kind === 'office') officeMs += ms; else otherMs += ms;
    const key = v.name ?? v.address ?? 'Unknown place';
    const cur = byPlace.get(key) ?? { name: key, category: kind ?? v.category, ms: 0, visits: 0 };
    cur.ms += ms; cur.visits += 1;
    byPlace.set(key, cur);
  }

  let travelMs = 0, distanceM = 0, walkedM = 0;
  const modeTotals: DaySummary['modeTotals'] = {};
  let toOffice: number | null = null, toHome: number | null = null;
  for (const t of trips) {
    const tEnd = t.end_ts ?? now;
    const ms = clip(t.start_ts, tEnd, from, end);
    const frac = tEnd > t.start_ts ? ms / (tEnd - t.start_ts) : 0;
    const m = t.distance_m * frac;
    travelMs += ms; distanceM += m;
    const mode = t.mode ?? 'vehicle';
    modeTotals[mode] = { ms: (modeTotals[mode]?.ms ?? 0) + ms, m: (modeTotals[mode]?.m ?? 0) + m };
    if (mode === 'walk' || mode === 'run') walkedM += m;
    const fk = kindOf(getVisit(t.from_visit)), tk = kindOf(getVisit(t.to_visit));
    if (t.end_ts && fk === 'home' && tk === 'office') toOffice = (toOffice ?? 0) + (t.end_ts - t.start_ts);
    if (t.end_ts && fk === 'office' && tk === 'home') toHome = (toHome ?? 0) + (t.end_ts - t.start_ts);
  }

  return {
    timeline,
    placeTotals: [...byPlace.values()].sort((a, b) => b.ms - a.ms),
    homeMs, officeMs, otherMs, travelMs, distanceM, walkedM, modeTotals,
    commute: { toOffice, toHome },
    start: from, end,
  };
}

export function routeFor(item: TimelineItem, now = Date.now()) {
  if (item.type !== 'trip') return [];
  return pointsBetween(item.trip.start_ts, item.trip.end_ts ?? now);
}
