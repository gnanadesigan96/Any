export interface LatLon { lat: number; lon: number }

/** Great-circle distance in metres. */
export function distance(a: LatLon, b: LatLon): number {
  const R = 6371000;
  const toRad = (d: number) => (d * Math.PI) / 180;
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lon - a.lon);
  const h = Math.sin(dLat / 2) ** 2 + Math.cos(toRad(a.lat)) * Math.cos(toRad(b.lat)) * Math.sin(dLon / 2) ** 2;
  return 2 * R * Math.asin(Math.min(1, Math.sqrt(h)));
}

export function pathLength(points: LatLon[]): number {
  let d = 0;
  for (let i = 1; i < points.length; i++) d += distance(points[i - 1], points[i]);
  return d;
}

export type TravelMode = 'walk' | 'run' | 'cycle' | 'vehicle' | 'train' | 'flight';

export const MODE_LABEL: Record<string, string> = {
  walk: '🚶 Walk', run: '🏃 Run', cycle: '🚴 Cycle', vehicle: '🚗 Vehicle',
  bus: '🚌 Bus', train: '🚆 Train', bike: '🛵 Two-wheeler', flight: '✈️ Flight',
};

/**
 * Guess how you travelled from speeds. Uses the 85th-percentile speed so a few
 * slow traffic-light moments don't turn a car ride into a walk.
 * The user can correct it on the trip screen.
 */
export function guessMode(speedsMps: number[], distanceM: number, durationMs: number): TravelMode {
  const valid = speedsMps.filter((s) => s >= 0 && s < 300).sort((a, b) => a - b);
  const avg = durationMs > 0 ? distanceM / (durationMs / 1000) : 0;
  const p85 = valid.length ? valid[Math.floor(valid.length * 0.85)] : avg;
  const top = Math.max(p85, avg);
  if (top > 70) return 'flight';      // > 250 km/h
  // Nobody walks 4 km at 7+ km/h on a normal day: long, steady trips at
  // "walking" speed are almost always slow city traffic.
  const km = distanceM / 1000;
  if (km > 4 && avg > 1.9) return avg > 4.5 || top > 7.5 ? 'vehicle' : 'cycle';
  if (top < 2.4) return 'walk';       // < ~8.5 km/h
  if (top < 3.6 && avg < 3.2) return 'run';
  if (top < 7.5) return 'cycle';      // < 27 km/h
  return 'vehicle';
}

export function formatDuration(ms: number): string {
  const mins = Math.max(0, Math.round(ms / 60000));
  if (mins < 60) return `${mins} min`;
  const h = Math.floor(mins / 60);
  const m = mins % 60;
  return m ? `${h} h ${m} min` : `${h} h`;
}

export function formatDistance(m: number): string {
  return m < 1000 ? `${Math.round(m)} m` : `${(m / 1000).toFixed(m < 10000 ? 1 : 0)} km`;
}

export function formatTime(ts: number): string {
  return new Date(ts).toLocaleTimeString([], { hour: 'numeric', minute: '2-digit' });
}
