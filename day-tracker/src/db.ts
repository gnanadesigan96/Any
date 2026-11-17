import * as SQLite from 'expo-sqlite';

// Everything is stored on the phone in a single SQLite file. Nothing is uploaded.
export const db = SQLite.openDatabaseSync('daytracker.db');

db.execSync(`
PRAGMA journal_mode = WAL;
CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY NOT NULL, value TEXT);
CREATE TABLE IF NOT EXISTS points (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts INTEGER NOT NULL, lat REAL NOT NULL, lon REAL NOT NULL,
  acc REAL, speed REAL
);
CREATE INDEX IF NOT EXISTS points_ts ON points(ts);
CREATE TABLE IF NOT EXISTS places (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL, kind TEXT NOT NULL,
  lat REAL NOT NULL, lon REAL NOT NULL, radius REAL NOT NULL DEFAULT 150,
  address TEXT
);
CREATE TABLE IF NOT EXISTS visits (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_ts INTEGER NOT NULL, end_ts INTEGER,
  lat REAL NOT NULL, lon REAL NOT NULL,
  place_id INTEGER, name TEXT, category TEXT, address TEXT,
  resolved INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS visits_start ON visits(start_ts);
CREATE TABLE IF NOT EXISTS trips (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  start_ts INTEGER NOT NULL, end_ts INTEGER,
  from_visit INTEGER, to_visit INTEGER,
  distance_m REAL NOT NULL DEFAULT 0,
  mode TEXT, mode_edited INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS trips_start ON trips(start_ts);
`);

// Lightweight migrations for columns added after the first release.
for (const sql of [
  'ALTER TABLE trips ADD COLUMN refined INTEGER NOT NULL DEFAULT 0',
  'ALTER TABLE trips ADD COLUMN steps INTEGER',
  'ALTER TABLE places ADD COLUMN learned INTEGER NOT NULL DEFAULT 0',
]) {
  try { db.execSync(sql); } catch { /* column already exists */ }
}

export type PlaceKind = 'home' | 'office' | 'other';

export interface Place {
  id: number; name: string; kind: PlaceKind;
  lat: number; lon: number; radius: number; address: string | null;
  /** 1 = created automatically when you named a visit (not added by hand). */
  learned?: number;
}
export interface Visit {
  id: number; start_ts: number; end_ts: number | null;
  lat: number; lon: number; place_id: number | null;
  name: string | null; category: string | null; address: string | null; resolved: number;
}
export interface Trip {
  id: number; start_ts: number; end_ts: number | null;
  from_visit: number | null; to_visit: number | null;
  distance_m: number; mode: string | null; mode_edited: number;
  refined: number; steps: number | null;
}
export interface Point { id: number; ts: number; lat: number; lon: number; acc: number | null; speed: number | null; }

// ---------- key/value ----------
export function getKV<T>(key: string, fallback: T): T {
  const row = db.getFirstSync<{ value: string }>('SELECT value FROM kv WHERE key = ?', key);
  if (!row) return fallback;
  try { return JSON.parse(row.value) as T; } catch { return fallback; }
}
export function setKV(key: string, value: unknown) {
  db.runSync('INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)', key, JSON.stringify(value));
}

// ---------- places ----------
export function listPlaces(): Place[] {
  return db.getAllSync<Place>("SELECT * FROM places ORDER BY CASE kind WHEN 'home' THEN 0 WHEN 'office' THEN 1 ELSE 2 END, name");
}
export function savePlace(p: Omit<Place, 'id' | 'learned'> & { id?: number; learned?: number }): number {
  // Only one Home and one Office: replace the existing one.
  if (!p.id && (p.kind === 'home' || p.kind === 'office')) {
    const existing = db.getFirstSync<{ id: number }>('SELECT id FROM places WHERE kind = ?', p.kind);
    if (existing) p = { ...p, id: existing.id };
  }
  if (p.id) {
    db.runSync('UPDATE places SET name=?, kind=?, lat=?, lon=?, radius=?, address=?, learned=? WHERE id=?',
      p.name, p.kind, p.lat, p.lon, p.radius, p.address, p.learned ?? 0, p.id);
    return p.id;
  }
  return db.runSync('INSERT INTO places (name, kind, lat, lon, radius, address, learned) VALUES (?,?,?,?,?,?,?)',
    p.name, p.kind, p.lat, p.lon, p.radius, p.address, p.learned ?? 0).lastInsertRowId;
}
export function deletePlace(id: number) {
  db.runSync('UPDATE visits SET place_id = NULL, resolved = 0 WHERE place_id = ?', id);
  db.runSync('DELETE FROM places WHERE id = ?', id);
}

// ---------- day queries ----------
export function dayBounds(day: Date): [number, number] {
  const s = new Date(day); s.setHours(0, 0, 0, 0);
  const e = new Date(s); e.setDate(e.getDate() + 1);
  return [s.getTime(), e.getTime()];
}
export function visitsOverlapping(from: number, to: number): Visit[] {
  return db.getAllSync<Visit>(
    'SELECT * FROM visits WHERE start_ts < ? AND (end_ts IS NULL OR end_ts > ?) ORDER BY start_ts', to, from);
}
export function tripsOverlapping(from: number, to: number): Trip[] {
  return db.getAllSync<Trip>(
    'SELECT * FROM trips WHERE start_ts < ? AND (end_ts IS NULL OR end_ts > ?) ORDER BY start_ts', to, from);
}
export function pointsBetween(from: number, to: number): Point[] {
  return db.getAllSync<Point>('SELECT * FROM points WHERE ts >= ? AND ts <= ? ORDER BY ts', from, to);
}
export function getVisit(id: number | null): Visit | null {
  if (id == null) return null;
  return db.getFirstSync<Visit>('SELECT * FROM visits WHERE id = ?', id);
}
export function unresolvedVisits(): Visit[] {
  return db.getAllSync<Visit>('SELECT * FROM visits WHERE resolved = 0 ORDER BY start_ts DESC LIMIT 20');
}
export function renameVisit(id: number, name: string) {
  db.runSync('UPDATE visits SET name = ?, resolved = 1 WHERE id = ?', name, id);
}
/** Times when tracking was interrupted (phone killed the app, location turned off…). */
export interface Gap { from: number; to: number; reason: string }
export function addGap(g: Gap) {
  const gaps = getKV<Gap[]>('engine.gaps', []);
  gaps.push(g);
  setKV('engine.gaps', gaps.slice(-100));
}
export function gapsBetween(from: number, to: number): Gap[] {
  return getKV<Gap[]>('engine.gaps', []).filter((g) => g.from < to && g.to > from);
}

export function setTripMode(id: number, mode: string) {
  db.runSync('UPDATE trips SET mode = ?, mode_edited = 1 WHERE id = ?', mode, id);
}

export function deleteAllData() {
  db.execSync("DELETE FROM points; DELETE FROM visits; DELETE FROM trips; DELETE FROM kv WHERE key LIKE 'engine.%';");
}
