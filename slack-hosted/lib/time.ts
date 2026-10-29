/** Calendar maths in the company's fixed UTC offset (IST has no daylight saving). */

import type { Settings, Slot } from "../config/settings.ts";

export type Local = { y: number; m: number; d: number; hh: number; mm: number };

export function toLocal(s: Settings, instant: Date): Local {
  const t = new Date(instant.getTime() + s.utcOffsetMinutes * 60_000);
  return {
    y: t.getUTCFullYear(),
    m: t.getUTCMonth() + 1,
    d: t.getUTCDate(),
    hh: t.getUTCHours(),
    mm: t.getUTCMinutes(),
  };
}

export function localInstant(s: Settings, y: number, m: number, d: number, hh = 0, mm = 0): Date {
  return new Date(Date.UTC(y, m - 1, d, hh, mm) - s.utcOffsetMinutes * 60_000);
}

export const pad = (n: number) => String(n).padStart(2, "0");
export const isoDate = (y: number, m: number, d: number) => `${y}-${pad(m)}-${pad(d)}`;

export function localDateIso(s: Settings, instant: Date): string {
  const l = toLocal(s, instant);
  return isoDate(l.y, l.m, l.d);
}

export const cycleIdFor = (s: Settings, instant: Date) => {
  const l = toLocal(s, instant);
  return `${l.y}-${pad(l.m)}`;
};

export function nextCycleId(cid: string): string {
  const [y, m] = cid.split("-").map(Number);
  return m === 12 ? `${y + 1}-01` : `${y}-${pad(m + 1)}`;
}

export function prevCycleId(cid: string): string {
  const [y, m] = cid.split("-").map(Number);
  return m === 1 ? `${y - 1}-12` : `${y}-${pad(m - 1)}`;
}

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];
const SHORT = MONTHS.map((m) => m.slice(0, 3));
const DAYS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

export const cycleLabel = (cid: string) => {
  const [y, m] = cid.split("-").map(Number);
  return `${MONTHS[m - 1]} ${y}`;
};

/** Parse "YYYY-MM-DD" strictly; returns null when invalid. */
export function parseIsoDate(v: string): { y: number; m: number; d: number } | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec((v ?? "").trim());
  if (!match) return null;
  const [y, m, d] = match.slice(1).map(Number);
  const t = new Date(Date.UTC(y, m - 1, d));
  return t.getUTCFullYear() === y && t.getUTCMonth() === m - 1 && t.getUTCDate() === d ? { y, m, d } : null;
}

export const weekday = (iso: string) => new Date(iso + "T00:00:00Z").getUTCDay();
export const dayName = (iso: string) => DAYS[weekday(iso)];
export const dayShort = (iso: string) => DAYS[weekday(iso)].slice(0, 3);
export function prettyDate(iso: string): string {
  const [y, m, d] = iso.split("-").map(Number);
  return `${pad(d)} ${SHORT[m - 1]} ${y}`;
}

/** The moment a schedule slot happens in a cycle month. */
export function slotAt(s: Settings, cid: string, slot: Slot): Date {
  const [y, m] = cid.split("-").map(Number);
  const [hh, mm] = slot.time.split(":").map(Number);
  return localInstant(s, y, m, slot.day, hh, mm);
}

/** The window closes at the END of the configured minute, so "23:59" means midnight. */
export const closeAt = (s: Settings, cid: string) => new Date(slotAt(s, cid, s.schedule.close).getTime() + 60_000);

export function period(s: Settings, cid: string): { first: string; last: string } {
  const [y, m] = cid.split("-").map(Number);
  const [py, pm] = prevCycleId(cid).split("-").map(Number);
  return { first: isoDate(py, pm, s.period.startDay), last: isoDate(y, m, s.period.endDay) };
}

export function periodText(s: Settings, cid: string): string {
  const p = period(s, cid);
  return `${prettyDate(p.first)} - ${prettyDate(p.last)}`;
}

export function formatLocal(s: Settings, instant: Date, withDate = true): string {
  const l = toLocal(s, instant);
  const h12 = l.hh % 12 === 0 ? 12 : l.hh % 12;
  const time = `${pad(h12)}:${pad(l.mm)} ${l.hh < 12 ? "AM" : "PM"} ${s.tzLabel}`;
  return withDate ? `${pad(l.d)} ${MONTHS[l.m - 1]}, ${time}` : time;
}

export function waitedText(ms: number): string {
  const minutes = Math.round(ms / 60_000);
  if (minutes < 60) return `${minutes} minutes`;
  const hours = Math.round(minutes / 60);
  return `${hours} hour${hours === 1 ? "" : "s"}`;
}
