/** Allowance rates: amounts are always computed here, never by the AI. */

import { RATES } from "../config/settings.ts";
import { weekday } from "./time.ts";

export type Shift = "day" | "night" | "none";
export type DayType = "weekday" | "weekend" | "holiday";

export function dayType(iso: string): DayType {
  if (RATES.weekendDays.includes(weekday(iso))) return "weekend";
  if (RATES.holidays[iso]) return "holiday";
  return "weekday";
}

export function dayTypeLabel(iso: string): string {
  const t = dayType(iso);
  return t === "holiday" ? `Holiday (${RATES.holidays[iso]})` : t[0].toUpperCase() + t.slice(1);
}

export function amount(iso: string, shift: Shift, hasExtraTask: boolean) {
  const t = dayType(iso);
  const shiftAmount = shift === "none" ? 0 : RATES.shift[shift][t];
  const extraAmount = hasExtraTask ? RATES.extraTask : 0;
  return { dayType: t, shiftAmount, extraAmount, total: shiftAmount + extraAmount };
}

export function money(n: number): string {
  if (RATES.currency === "INR") return `₹${Math.round(n).toLocaleString("en-IN")}`;
  return `${RATES.currency} ${n.toFixed(2)}`;
}

export const SHIFT_LABEL: Record<Shift, string> = { day: "Day", night: "Night", none: "-" };
