import * as Location from 'expo-location';
import * as TaskManager from 'expo-task-manager';
import * as Notifications from 'expo-notifications';
import { db, getKV, setKV, getVisit, unresolvedVisits, Visit } from './db';
import { distance, guessMode, pathLength, formatDuration, MODE_LABEL } from './geo';
import { resolveVisit } from './places';
import { emitChange } from './events';

export const LOCATION_TASK = 'daytracker-location';

// ---- Tuning ----
/** You count as "staying" somewhere if you remain within this many metres... */
const STAY_RADIUS_M = 100;
/** ...for at least this long. Shorter stops (traffic lights, a quick ATM stop) are part of the trip. */
const STAY_MIN_MS = 5 * 60 * 1000;
/** Ignore GPS fixes worse than this. */
const MAX_ACCURACY_M = 80;
/** Speed assumed when estimating when you left a place after a gap in GPS updates. */
const GAP_TRAVEL_SPEED_MPS = 5;

interface Anchor { lat: number; lon: number; n: number; startTs: number; lastTs: number }
interface EngineState {
  anchor: Anchor | null;      // cluster of recent points that might become a visit
  visitId: number | null;     // currently open visit (you are there now)
  tripId: number | null;      // currently open trip (you are on the move)
  outside: number;            // consecutive fixes outside the open visit
  lastTs: number;
}
const EMPTY: EngineState = { anchor: null, visitId: null, tripId: null, outside: 0, lastTs: 0 };

export type TrackingMode = 'precise' | 'balanced';

// ---------- Background task ----------
// Must be defined at module scope, before the app renders (index.ts imports this file first).
TaskManager.defineTask<{ locations: Location.LocationObject[] }>(LOCATION_TASK, async ({ data, error }) => {
  if (error || !data?.locations?.length) return;
  await ingest(data.locations);
});

let queue: Promise<void> = Promise.resolve();
/** Process fixes one batch at a time, in order. */
export function ingest(locations: Location.LocationObject[]): Promise<void> {
  queue = queue.then(() => processBatch(locations)).catch((e) => console.warn('ingest failed', e));
  return queue;
}

async function processBatch(locations: Location.LocationObject[]) {
  const toResolve: number[] = [];
  const closedTrips: number[] = [];
  const state = getKV<EngineState>('engine.state', EMPTY);
  const sorted = [...locations].sort((a, b) => a.timestamp - b.timestamp);

  db.withTransactionSync(() => {
    for (const loc of sorted) {
      const acc = loc.coords.accuracy ?? 999;
      if (loc.timestamp <= state.lastTs || acc > MAX_ACCURACY_M) continue;
      const p = { lat: loc.coords.latitude, lon: loc.coords.longitude, ts: loc.timestamp };
      db.runSync('INSERT INTO points (ts, lat, lon, acc, speed) VALUES (?,?,?,?,?)',
        p.ts, p.lat, p.lon, acc, loc.coords.speed ?? null);
      step(state, p, acc, toResolve, closedTrips);
      state.lastTs = p.ts;
    }
    setKV('engine.state', state);
  });

  emitChange();
  for (const id of toResolve) {
    const v = getVisit(id);
    if (!v) continue;
    await resolveVisit(v);
    await notifyArrival(id, closedTrips);
    emitChange();
  }
}

function step(s: EngineState, p: { lat: number; lon: number; ts: number }, acc: number,
  toResolve: number[], closedTrips: number[]) {
  // 1) You're at a place. Have you left?
  if (s.visitId != null && s.anchor) {
    const d = distance(s.anchor, p);
    if (d <= STAY_RADIUS_M + Math.min(acc, 50)) {
      s.outside = 0;
      s.anchor.lastTs = p.ts;
      return;
    }
    s.outside += 1;
    // Two fixes outside in a row (filters GPS jumps), or clearly far away.
    if (s.outside < 2 && d < 400) return;
    const left = Math.max(s.anchor.lastTs, p.ts - d / GAP_TRAVEL_SPEED_MPS);
    db.runSync('UPDATE visits SET end_ts=? WHERE id=?', left, s.visitId);
    s.tripId = db.runSync('INSERT INTO trips (start_ts, from_visit) VALUES (?,?)', left, s.visitId).lastInsertRowId;
    s.visitId = null;
    s.outside = 0;
    s.anchor = newAnchor(p);
    return;
  }

  // 2) You're moving (or we just started). Did you stop somewhere?
  const a = s.anchor;
  if (a && distance(a, p) <= STAY_RADIUS_M) {
    // still near the same spot – grow the cluster (running centroid)
    a.lat = (a.lat * a.n + p.lat) / (a.n + 1);
    a.lon = (a.lon * a.n + p.lon) / (a.n + 1);
    a.n += 1;
    a.lastTs = p.ts;
    if (a.lastTs - a.startTs >= STAY_MIN_MS) confirmVisit(s, a, toResolve, closedTrips);
    return;
  }

  // Moved away from the cluster. Phones send few updates while you sit still, so a long
  // gap followed by a fix elsewhere usually means you stayed put and then travelled.
  if (a) {
    const d = distance(a, p);
    const leftEstimate = p.ts - d / GAP_TRAVEL_SPEED_MPS;
    if (leftEstimate - a.startTs >= STAY_MIN_MS) {
      a.lastTs = Math.max(a.lastTs, leftEstimate);
      confirmVisit(s, a, toResolve, closedTrips);
      db.runSync('UPDATE visits SET end_ts=? WHERE id=?', a.lastTs, s.visitId);
      s.tripId = db.runSync('INSERT INTO trips (start_ts, from_visit) VALUES (?,?)', a.lastTs, s.visitId).lastInsertRowId;
      s.visitId = null;
    }
  }
  if (s.tripId == null) {
    s.tripId = db.runSync('INSERT INTO trips (start_ts, from_visit) VALUES (?, NULL)', p.ts).lastInsertRowId;
  }
  s.anchor = newAnchor(p);
}

function newAnchor(p: { lat: number; lon: number; ts: number }): Anchor {
  return { lat: p.lat, lon: p.lon, n: 1, startTs: p.ts, lastTs: p.ts };
}

function confirmVisit(s: EngineState, a: Anchor, toResolve: number[], closedTrips: number[]) {
  const visitId = db.runSync('INSERT INTO visits (start_ts, lat, lon) VALUES (?,?,?)', a.startTs, a.lat, a.lon).lastInsertRowId;
  if (s.tripId != null) {
    finishTrip(s.tripId, a.startTs, visitId);
    closedTrips.push(s.tripId);
  }
  s.tripId = null;
  s.visitId = visitId;
  s.outside = 0;
  toResolve.push(visitId);
}

function finishTrip(tripId: number, endTs: number, toVisit: number) {
  const trip = db.getFirstSync<{ start_ts: number }>('SELECT start_ts FROM trips WHERE id=?', tripId);
  if (!trip) return;
  const pts = db.getAllSync<{ ts: number; lat: number; lon: number; speed: number | null }>(
    'SELECT ts, lat, lon, speed FROM points WHERE ts >= ? AND ts <= ? ORDER BY ts', trip.start_ts, endTs);
  const dist = pathLength(pts);
  const speeds: number[] = [];
  for (let i = 0; i < pts.length; i++) {
    if (pts[i].speed != null && pts[i].speed! >= 0) speeds.push(pts[i].speed!);
    else if (i > 0 && pts[i].ts > pts[i - 1].ts) speeds.push(distance(pts[i - 1], pts[i]) / ((pts[i].ts - pts[i - 1].ts) / 1000));
  }
  const mode = guessMode(speeds, dist, endTs - trip.start_ts);
  if (dist < 150) {
    // Wandered around but didn't really go anywhere – drop it.
    db.runSync('DELETE FROM trips WHERE id=?', tripId);
    return;
  }
  db.runSync('UPDATE trips SET end_ts=?, to_visit=?, distance_m=?, mode=? WHERE id=?', endTs, toVisit, dist, mode, tripId);
}

async function notifyArrival(visitId: number, closedTrips: number[]) {
  if (!getKV('settings.notify', true)) return;
  const v = getVisit(visitId);
  if (!v) return;
  const trip = closedTrips.length
    ? db.getFirstSync<{ start_ts: number; end_ts: number; mode: string; distance_m: number }>(
        'SELECT * FROM trips WHERE to_visit=?', visitId)
    : null;
  const where = v.name ?? v.address ?? 'a new place';
  const body = trip
    ? `${MODE_LABEL[trip.mode] ?? trip.mode} · ${formatDuration(trip.end_ts - trip.start_ts)} · ${(trip.distance_m / 1000).toFixed(1)} km`
    : 'Visit recorded';
  try {
    await Notifications.scheduleNotificationAsync({ content: { title: `Arrived at ${where}`, body }, trigger: null });
  } catch {}
}

// ---------- Start / stop ----------
export async function startTracking(mode: TrackingMode = getKV<TrackingMode>('settings.mode', 'precise')) {
  const precise = mode === 'precise';
  if (await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK).catch(() => false)) {
    await Location.stopLocationUpdatesAsync(LOCATION_TASK);
  }
  await Location.startLocationUpdatesAsync(LOCATION_TASK, {
    accuracy: precise ? Location.Accuracy.High : Location.Accuracy.Balanced,
    distanceInterval: precise ? 15 : 50,
    timeInterval: precise ? 15000 : 60000,
    pausesUpdatesAutomatically: false,
    activityType: Location.ActivityType.Other,
    showsBackgroundLocationIndicator: true,
    foregroundService: {
      notificationTitle: 'Day Tracker is recording your day',
      notificationBody: 'Tap to see today’s timeline',
      notificationColor: '#2563EB',
      killServiceOnDestroy: false,
    },
  });
  setKV('settings.mode', mode);
  setKV('settings.tracking', true);
}

export async function stopTracking() {
  if (await Location.hasStartedLocationUpdatesAsync(LOCATION_TASK).catch(() => false)) {
    await Location.stopLocationUpdatesAsync(LOCATION_TASK);
  }
  // Close whatever was in progress so nothing is left open-ended while tracking is off.
  const s = currentState();
  const now = Date.now();
  if (s.visitId != null) db.runSync('UPDATE visits SET end_ts=? WHERE id=?', s.anchor?.lastTs ?? now, s.visitId);
  if (s.tripId != null) db.runSync('DELETE FROM trips WHERE id=?', s.tripId);
  setKV('engine.state', EMPTY);
  setKV('settings.tracking', false);
  emitChange();
}

export async function isTracking(): Promise<boolean> {
  return Location.hasStartedLocationUpdatesAsync(LOCATION_TASK).catch(() => false);
}

/** Called when the app opens: restart tracking if it should be on, and finish any place lookups that failed offline. */
export async function resume() {
  if (getKV('settings.tracking', false) && !(await isTracking())) {
    try { await startTracking(); } catch (e) { console.warn('restart failed', e); }
  }
  const pending: Visit[] = unresolvedVisits();
  for (const v of pending) { await resolveVisit(v); }
  if (pending.length) emitChange();
}

/** Where you are right now, as the engine sees it. */
export function currentState(): EngineState {
  return getKV<EngineState>('engine.state', EMPTY);
}
