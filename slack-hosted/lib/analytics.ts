/** Month-over-month comparison and trends. All numbers are computed here from stored entries. */

import { money } from "./policy.ts";
import { priced, renderTable } from "./report.ts";
import type { Store } from "./store.ts";
import { cycleLabel } from "./time.ts";

type Person = {
  name: string;
  shifts: number;
  night: number;
  weekend: number;
  holiday: number;
  extra: number;
  total: number;
};

export type CycleStats = {
  cycle: string;
  label: string;
  status: string;
  people: number;
  entries: number;
  day_shifts: number;
  night_shifts: number;
  weekday_shifts: number;
  weekend_shifts: number;
  holiday_shifts: number;
  extra_tasks: number;
  shift_amount: number;
  extra_amount: number;
  total: number;
  avg_per_person: number;
  flags: { accepted: number; rejected: number; removed: number; pending: number };
  by_person: Record<string, Person>;
};

export async function cycleStats(store: Store, cid: string, personId?: string): Promise<CycleStats> {
  const items = priced(await store.entries(cid, { personId, payableOnly: true }));
  const everything = (await store.cycleEntriesIncludingGone(cid)).filter((e) => !personId || e.person_id === personId);
  const shifts = items.filter((e) => e.shift !== "none");
  const byPerson: Record<string, Person> = {};
  for (const e of items) {
    const p = byPerson[e.person_id] ??= {
      name: e.person_name,
      shifts: 0,
      night: 0,
      weekend: 0,
      holiday: 0,
      extra: 0,
      total: 0,
    };
    if (e.shift !== "none") {
      p.shifts += 1;
      if (e.shift === "night") p.night += 1;
      if (e.dayType === "weekend") p.weekend += 1;
      if (e.dayType === "holiday") p.holiday += 1;
    }
    if (e.extra_task) p.extra += 1;
    p.total += e.total;
  }
  const total = items.reduce((n, e) => n + e.total, 0);
  const people = Object.keys(byPerson).length;
  const count = (f: (e: typeof items[number]) => boolean) => items.filter(f).length;
  return {
    cycle: cid,
    label: cycleLabel(cid),
    status: (await store.cycle(cid))?.status ?? "open",
    people,
    entries: items.length,
    day_shifts: count((e) => e.shift === "day"),
    night_shifts: count((e) => e.shift === "night"),
    weekday_shifts: shifts.filter((e) => e.dayType === "weekday").length,
    weekend_shifts: shifts.filter((e) => e.dayType === "weekend").length,
    holiday_shifts: shifts.filter((e) => e.dayType === "holiday").length,
    extra_tasks: count((e) => !!e.extra_task),
    shift_amount: items.reduce((n, e) => n + e.shiftAmount, 0),
    extra_amount: items.reduce((n, e) => n + e.extraAmount, 0),
    total,
    avg_per_person: people ? total / people : 0,
    flags: {
      accepted: everything.filter((e) => e.review === "accepted").length,
      rejected: everything.filter((e) => e.review === "rejected").length,
      removed: everything.filter((e) => e.review === "removed").length,
      pending: everything.filter((e) => e.review === "pending").length,
    },
    by_person: byPerson,
  };
}

function change(before: number, after: number, fmt: (n: number) => string = String): string {
  const diff = after - before;
  if (!diff) return "no change";
  const pct = before ? ` (${diff > 0 ? "+" : ""}${Math.round((diff / before) * 100)}%)` : "";
  return `${diff > 0 ? "+" : "-"}${fmt(Math.abs(diff))}${pct}`;
}

export function compare(a: CycleStats, b: CycleStats) {
  const counts: [string, keyof CycleStats][] = [
    ["Entries", "entries"],
    ["Day shifts", "day_shifts"],
    ["Night shifts", "night_shifts"],
    ["Weekday shifts", "weekday_shifts"],
    ["Weekend shifts", "weekend_shifts"],
    ["Holiday shifts", "holiday_shifts"],
    ["Extra tasks", "extra_tasks"],
  ];
  const rows: (string | number)[][] = [
    ["Total amount", money(a.total), money(b.total), change(a.total, b.total, money)],
    ["  shift allowance", money(a.shift_amount), money(b.shift_amount), change(a.shift_amount, b.shift_amount, money)],
    [
      "  extra-task allowance",
      money(a.extra_amount),
      money(b.extra_amount),
      change(a.extra_amount, b.extra_amount, money),
    ],
    ["People", a.people, b.people, change(a.people, b.people)],
    ...counts.map(([label, k]) => [label, a[k] as number, b[k] as number, change(a[k] as number, b[k] as number)]),
    [
      "Avg per person",
      money(a.avg_per_person),
      money(b.avg_per_person),
      change(a.avg_per_person, b.avg_per_person, money),
    ],
    [
      "Flagged: accepted/rejected",
      `${a.flags.accepted}/${a.flags.rejected}`,
      `${b.flags.accepted}/${b.flags.rejected}`,
      "",
    ],
  ];
  const zero: Person = { name: "", shifts: 0, night: 0, weekend: 0, holiday: 0, extra: 0, total: 0 };
  const ids = [...new Set([...Object.keys(a.by_person), ...Object.keys(b.by_person)])].sort((x, y) =>
    (a.by_person[x] ?? b.by_person[x]).name.toLowerCase().localeCompare(
      (a.by_person[y] ?? b.by_person[y]).name.toLowerCase(),
    )
  );
  const people = ids.map((id) => {
    const pa = a.by_person[id] ?? zero, pb = b.by_person[id] ?? zero;
    const name = (b.by_person[id] ?? a.by_person[id]).name;
    const note = !a.by_person[id] ? "new" : !b.by_person[id] ? `not in ${b.label.split(" ")[0]}` : "";
    return { id, name, pa, pb, note, change: pb.total - pa.total };
  });
  const arrow = (x: number, y: number) => `${x} → ${y}`;
  const personTable = people.length
    ? renderTable(
      ["Employee", "Shifts", "Night", "Wknd/Hol", "Extra", "Amount", "Change", "Note"],
      people.map((p) => [
        p.name,
        arrow(p.pa.shifts, p.pb.shifts),
        arrow(p.pa.night, p.pb.night),
        arrow(p.pa.weekend + p.pa.holiday, p.pb.weekend + p.pb.holiday),
        arrow(p.pa.extra, p.pb.extra),
        `${money(p.pa.total)} → ${money(p.pb.total)}`,
        change(p.pa.total, p.pb.total, money),
        p.note,
      ]),
    )
    : "";
  return {
    summaryTable: renderTable(["Metric", a.label, b.label, "Change"], rows),
    personTable,
    columnsNote: `Per-person columns read ${a.label} → ${b.label}.`,
    biggestChanges: people.sort((x, y) => Math.abs(y.change) - Math.abs(x.change)).slice(0, 15).map((p) => ({
      name: p.name,
      before: p.pa,
      after: p.pb,
      change: p.change,
      status: p.note || "both months",
    })),
  };
}

export function trendTable(series: CycleStats[]): string {
  return renderTable(
    ["Month", "Status", "People", "Entries", "Day", "Night", "Wknd/Hol", "Extra", "Total", "vs prev month"],
    series.map((s, i) => [
      s.label,
      s.entries || s.status !== "open" ? s.status.replace("_", " ") : "no data",
      s.people,
      s.entries,
      s.day_shifts,
      s.night_shifts,
      s.weekend_shifts + s.holiday_shifts,
      s.extra_tasks,
      money(s.total),
      i ? change(series[i - 1].total, s.total, money) : "-",
    ]),
  );
}
