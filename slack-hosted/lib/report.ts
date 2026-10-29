/** Plain-text tables posted as Slack code blocks. */

import { amount, dayTypeLabel, money, SHIFT_LABEL } from "./policy.ts";
import type { Entry } from "./store.ts";
import { dayShort, prettyDate } from "./time.ts";

export const STATUS_LABEL: Record<Entry["review"], string> = {
  "": "Recorded",
  pending: "Awaiting review",
  accepted: "Accepted by reviewer",
  rejected: "Rejected",
  removed: "Removed",
};

export function renderTable(headers: string[], rows: (string | number)[][]): string {
  const cells = [headers, ...rows.map((r) => r.map(String))];
  const widths = headers.map((_, i) => Math.max(...cells.map((r) => [...r[i]].length)));
  const line = (r: string[]) => r.map((c, i) => c + " ".repeat(widths[i] - [...c].length)).join(" | ").trimEnd();
  return [line(cells[0]), widths.map((w) => "-".repeat(w)).join("-+-"), ...cells.slice(1).map(line)].join("\n");
}

/** Split a long table into several ``` blocks so each Slack message stays readable. */
export function codeBlocks(text: string, limit = 3500): string[] {
  const chunks: string[][] = [];
  let current: string[] = [], size = 0;
  for (const ln of text.split("\n")) {
    if (current.length && size + ln.length > limit) {
      chunks.push(current);
      current = [];
      size = 0;
    }
    current.push(ln);
    size += ln.length + 1;
  }
  if (current.length) chunks.push(current);
  return chunks.map((c) => "```\n" + c.join("\n") + "\n```");
}

export function clip(text: string | undefined, n = 40): string {
  const t = (text ?? "").replace(/\s+/g, " ").trim();
  return t.length <= n ? t : t.slice(0, n - 1) + "…";
}

export function priced(entries: Entry[]) {
  return entries.map((e) => ({ ...e, ...amount(e.support_date, e.shift, !!e.extra_task) }));
}

/** What a person sees after submitting: their details, no amounts. */
export function submissionTable(entries: Entry[]): string {
  return renderTable(
    ["Date", "Day", "Shift", "Day type", "Extra task", "Status"],
    entries.map((e) => [
      prettyDate(e.support_date),
      dayShort(e.support_date),
      SHIFT_LABEL[e.shift],
      dayTypeLabel(e.support_date),
      clip(e.extra_task) || "-",
      STATUS_LABEL[e.review],
    ]),
  );
}

/** Everyone's details for a month, without amounts (safe for the team channel). */
export function teamTable(entries: Entry[]): string {
  return renderTable(
    ["Employee", "Date", "Day", "Shift", "Day type", "Extra task", "Status"],
    entries.map((e) => [
      e.person_name,
      prettyDate(e.support_date),
      dayShort(e.support_date),
      SHIFT_LABEL[e.shift],
      dayTypeLabel(e.support_date),
      clip(e.extra_task, 30) || "-",
      STATUS_LABEL[e.review],
    ]),
  );
}

export type FinalReport = {
  detail: string;
  summary: string;
  people: number;
  entries: number;
  grandTotal: number;
  grandTotalText: string;
};

/** Detailed + per-person summary tables (with amounts) for the approver and HR. */
export function finalReport(entries: Entry[]): FinalReport {
  const items = priced(entries);
  const people = new Map<string, { name: string; day: number; night: number; extra: number; total: number }>();
  const detail = items.map((e, i) => {
    const p = people.get(e.person_id) ?? { name: e.person_name, day: 0, night: 0, extra: 0, total: 0 };
    if (e.shift === "day" || e.shift === "night") p[e.shift] += 1;
    if (e.extra_task) p.extra += 1;
    p.total += e.total;
    people.set(e.person_id, p);
    return [
      i + 1,
      e.person_name,
      prettyDate(e.support_date),
      dayShort(e.support_date),
      SHIFT_LABEL[e.shift],
      dayTypeLabel(e.support_date),
      clip(e.extra_task, 30) || "-",
      money(e.total),
      e.review === "accepted" ? clip(`Accepted: ${e.flag_reason}`, 45) : "",
    ];
  });
  const ps = [...people.values()].sort((a, b) => a.name.toLowerCase().localeCompare(b.name.toLowerCase()));
  const sum = (k: "day" | "night" | "extra" | "total") => ps.reduce((n, p) => n + p[k], 0);
  const summary = [
    ...ps.map((p) => [p.name, p.day, p.night, p.extra, money(p.total)]),
    ["TOTAL", sum("day"), sum("night"), sum("extra"), money(sum("total"))],
  ];
  return {
    detail: renderTable(["#", "Employee", "Date", "Day", "Shift", "Day type", "Extra task", "Amount", "Note"], detail),
    summary: renderTable(["Employee", "Day shifts", "Night shifts", "Extra tasks", "Total"], summary),
    people: ps.length,
    entries: items.length,
    grandTotal: sum("total"),
    grandTotalText: money(sum("total")),
  };
}
