/**
 * Storage for cycles, entries, live interactive messages and small settings.
 *
 * `Store` is the interface the engine uses. `DatastoreStore` keeps the data in Slack's built-in
 * datastores (production); `MemoryStore` keeps it in memory (tests). Volumes are tiny (dozens of
 * rows a month), so queries read a datastore page by page and filter in code.
 *
 * Entry `review` values:
 *   ""          inside the period, no overlap - payable
 *   "pending"   flagged (outside period / overlapping shift), waiting for the reviewer
 *   "accepted"  flagged, accepted by the reviewer - payable
 *   "rejected"  flagged, rejected by the reviewer
 *   "removed"   taken out by the reviewer while addressing a concern
 */

import type { Shift } from "./policy.ts";

export type Entry = {
  id: string;
  cycle_id: string;
  person_id: string;
  person_name: string;
  support_date: string;
  shift: Shift;
  extra_task: string;
  review: "" | "pending" | "accepted" | "rejected" | "removed";
  reviewed_by: string;
  flag_reason: string;
  thread_channel: string;
  thread_ts: string;
  submitted_by: string;
  submitted_at: string;
};

export type CycleStatus = "open" | "reviewing" | "pending_approval" | "concern" | "approved" | "empty";

export type Cycle = {
  cycle_id: string;
  status: CycleStatus;
  reminder_sent_at: string;
  closing_reminder_sent_at: string;
  closed_at: string;
  approval_channel: string;
  approval_ts: string;
  decided_by: string;
  decided_at: string;
  concern_text: string;
  concern_by: string;
  concern_entry_ids: string; // JSON array of entry ids
  concern_channel: string;
  concern_ts: string;
  waiting_since: string;
  nudges_sent: number;
};

/** An interactive message we posted; its buttons route to the function execution that posted it. */
export type LiveMessage = {
  key: string; // channel:ts
  channel: string;
  ts: string;
  kind: "review" | "approval" | "concern";
  cycle_id: string;
  execution_id: string;
  entry_ids: string; // JSON array (review messages: which entries they show)
  live: boolean;
};

const GONE = ["rejected", "removed"];
export const isLive = (e: Entry) => !GONE.includes(e.review);
export const isPayable = (e: Entry) => e.review === "" || e.review === "accepted";

export function newCycle(cid: string): Cycle {
  return {
    cycle_id: cid,
    status: "open",
    reminder_sent_at: "",
    closing_reminder_sent_at: "",
    closed_at: "",
    approval_channel: "",
    approval_ts: "",
    decided_by: "",
    decided_at: "",
    concern_text: "",
    concern_by: "",
    concern_entry_ids: "[]",
    concern_channel: "",
    concern_ts: "",
    waiting_since: "",
    nudges_sent: 0,
  };
}

/** Low-level table access - the only thing that differs between Slack datastores and memory. */
export interface Tables {
  get<T>(table: string, id: string): Promise<T | null>;
  put<T>(table: string, item: T): Promise<void>;
  all<T>(table: string): Promise<T[]>;
}

const sortEntries = (a: Entry, b: Entry) =>
  a.person_name.toLowerCase().localeCompare(b.person_name.toLowerCase()) ||
  a.support_date.localeCompare(b.support_date) ||
  a.shift.localeCompare(b.shift);

export class Store {
  /** Entries are read many times per request (duplicate / overlap checks); cache them until a write. */
  private cache: Entry[] | null = null;

  constructor(private t: Tables) {}

  // -- cycles -------------------------------------------------------------------
  async cycle(cid: string): Promise<Cycle | null> {
    return await this.t.get<Cycle>("cycles", cid);
  }

  async ensureCycle(cid: string): Promise<Cycle> {
    const c = await this.cycle(cid);
    if (c) return c;
    const fresh = newCycle(cid);
    await this.t.put("cycles", fresh);
    return fresh;
  }

  async updateCycle(cid: string, fields: Partial<Cycle>): Promise<Cycle> {
    const c = { ...(await this.ensureCycle(cid)), ...fields };
    await this.t.put("cycles", c);
    return c;
  }

  /** Move a cycle between statuses; false if it wasn't in `from` (e.g. a double click). */
  async transition(cid: string, from: CycleStatus[], to: CycleStatus, fields: Partial<Cycle> = {}): Promise<boolean> {
    const c = await this.ensureCycle(cid);
    if (!from.includes(c.status)) return false;
    await this.t.put("cycles", { ...c, ...fields, status: to });
    return true;
  }

  async waitingCycles(): Promise<Cycle[]> {
    return (await this.t.all<Cycle>("cycles")).filter((c) =>
      ["reviewing", "pending_approval", "concern"].includes(c.status)
    );
  }

  // -- entries ------------------------------------------------------------------
  async entry(id: string): Promise<Entry | null> {
    return await this.t.get<Entry>("entries", id);
  }

  async putEntry(e: Entry): Promise<void> {
    this.cache = null;
    await this.t.put("entries", e);
  }

  async updateEntry(id: string, fields: Partial<Entry>): Promise<Entry | null> {
    const e = await this.entry(id);
    if (!e) return null;
    const updated = { ...e, ...fields };
    await this.putEntry(updated);
    return updated;
  }

  /** Every entry except archived ones (see archiveAll). */
  async allEntries(): Promise<Entry[]> {
    this.cache ??= (await this.t.all<Entry>("entries")).filter((e) => !e.cycle_id.startsWith("archived:"));
    return this.cache.map((e) => ({ ...e }));
  }

  /**
   * Test clean-up without deleting anything: entries are moved to "archived:<cycle>", cycles are
   * reset to fresh, live messages are retired. Returns how many entries/cycles were archived and the
   * executions whose messages were retired (so they can be completed).
   */
  async archiveAll(): Promise<{ entries: number; cycles: number; executions: string[] }> {
    const entries = await this.allEntries();
    for (const e of entries) await this.t.put("entries", { ...e, cycle_id: `archived:${e.cycle_id}` });
    this.cache = null;
    const cycles = await this.t.all<Cycle>("cycles");
    for (const c of cycles) await this.t.put("cycles", newCycle(c.cycle_id));
    const live = await this.liveMessages();
    for (const m of live) await this.t.put("live_messages", { ...m, live: false });
    await this.t.put("meta", { key: "pretend_anchor", value: "" });
    return {
      entries: entries.length,
      cycles: cycles.length,
      executions: [...new Set(live.map((m) => m.execution_id))],
    };
  }

  /** Entries of a cycle (rejected/removed excluded unless asked for by id). */
  async entries(
    cid: string,
    opts: { personId?: string; payableOnly?: boolean; ids?: string[] } = {},
  ): Promise<Entry[]> {
    let rows = (await this.allEntries()).filter((e) => e.cycle_id === cid);
    rows = opts.ids ? rows.filter((e) => opts.ids!.includes(e.id)) : rows.filter(isLive);
    if (opts.payableOnly) rows = rows.filter(isPayable);
    if (opts.personId) rows = rows.filter((e) => e.person_id === opts.personId);
    return rows.sort(sortEntries);
  }

  async cycleEntriesIncludingGone(cid: string): Promise<Entry[]> {
    return (await this.allEntries()).filter((e) => e.cycle_id === cid).sort(sortEntries);
  }

  async pendingReviews(cid: string): Promise<Entry[]> {
    return (await this.entries(cid)).filter((e) => e.review === "pending");
  }

  async cyclesWithEntries(): Promise<string[]> {
    return [...new Set((await this.allEntries()).map((e) => e.cycle_id))].sort();
  }

  /** Cycle where this person already claimed this date + shift (rejected/removed don't count). */
  async duplicateOf(personId: string, date: string, shift: string, excludeId = ""): Promise<string | null> {
    const hit = (await this.allEntries()).find((e) =>
      e.person_id === personId && e.support_date === date && e.shift === shift && isLive(e) && e.id !== excludeId
    );
    return hit ? hit.cycle_id : null;
  }

  /** Other people's live entries for the same date and day/night shift (extra-task-only never overlaps). */
  async overlaps(date: string, shift: string, personId: string, excludeId = ""): Promise<Entry[]> {
    if (shift !== "day" && shift !== "night") return [];
    return (await this.allEntries()).filter((e) =>
      e.support_date === date && e.shift === shift && e.person_id !== personId && isLive(e) && e.id !== excludeId
    );
  }

  /** A person withdrawing their own entries while the window is open (marked removed, kept for history). */
  async withdraw(cid: string, personId: string, dates: string[], shift = ""): Promise<number> {
    const targets = (await this.entries(cid, { personId })).filter((e) =>
      dates.includes(e.support_date) && (!shift || e.shift === shift)
    );
    for (const e of targets) await this.putEntry({ ...e, review: "removed", reviewed_by: personId });
    return targets.length;
  }

  // -- live interactive messages ------------------------------------------------------
  async registerLive(m: Omit<LiveMessage, "key" | "live">): Promise<void> {
    await this.t.put("live_messages", { ...m, key: `${m.channel}:${m.ts}`, live: true });
  }

  async retireLive(channel: string, ts: string): Promise<LiveMessage | null> {
    const m = await this.t.get<LiveMessage>("live_messages", `${channel}:${ts}`);
    if (!m) return null;
    await this.t.put("live_messages", { ...m, live: false });
    return m;
  }

  async liveMessages(filter: Partial<LiveMessage> = {}): Promise<LiveMessage[]> {
    return (await this.t.all<LiveMessage>("live_messages")).filter((m) =>
      m.live && Object.entries(filter).every(([k, v]) => (m as Record<string, unknown>)[k] === v)
    );
  }

  // -- settings ---------------------------------------------------------------------
  async meta(key: string): Promise<string | null> {
    const row = await this.t.get<{ key: string; value: string }>("meta", key);
    return row?.value ? row.value : null;
  }

  async setMeta(key: string, value: string): Promise<void> {
    await this.t.put("meta", { key, value });
  }
}

// -- implementations -------------------------------------------------------------------

export const DATASTORES = {
  cycles: "support_cycles",
  entries: "support_entries",
  live_messages: "support_live_messages",
  meta: "support_meta",
} as const;

// deno-lint-ignore no-explicit-any
type AnyClient = any;

/** Slack's built-in datastores (Run on Slack). */
export class DatastoreTables implements Tables {
  constructor(private client: AnyClient) {}

  private name(table: string): string {
    const n = (DATASTORES as Record<string, string>)[table];
    if (!n) throw new Error(`unknown table ${table}`);
    return n;
  }

  async get<T>(table: string, id: string): Promise<T | null> {
    const r = await this.client.apps.datastore.get({ datastore: this.name(table), id });
    if (!r.ok) throw new Error(`datastore get ${table}: ${r.error}`);
    return r.item && Object.keys(r.item).length ? r.item as T : null;
  }

  async put<T>(table: string, item: T): Promise<void> {
    const r = await this.client.apps.datastore.put({ datastore: this.name(table), item });
    if (!r.ok) throw new Error(`datastore put ${table}: ${r.error}`);
  }

  async all<T>(table: string): Promise<T[]> {
    const out: T[] = [];
    let cursor: string | undefined;
    do {
      const r = await this.client.apps.datastore.query({ datastore: this.name(table), limit: 1000, cursor });
      if (!r.ok) throw new Error(`datastore query ${table}: ${r.error}`);
      out.push(...(r.items as T[]));
      cursor = r.response_metadata?.next_cursor || undefined;
    } while (cursor);
    return out;
  }
}

/** In-memory tables (tests). */
export class MemoryTables implements Tables {
  data: Record<string, Map<string, unknown>> = {};
  private keyOf: Record<string, string> = {
    cycles: "cycle_id",
    entries: "id",
    live_messages: "key",
    meta: "key",
  };

  private table(t: string) {
    return this.data[t] ??= new Map();
  }

  get<T>(table: string, id: string): Promise<T | null> {
    const v = this.table(table).get(id);
    return Promise.resolve(v ? structuredClone(v) as T : null);
  }

  put<T>(table: string, item: T): Promise<void> {
    this.table(table).set((item as Record<string, string>)[this.keyOf[table]], structuredClone(item));
    return Promise.resolve();
  }

  all<T>(table: string): Promise<T[]> {
    return Promise.resolve([...this.table(table).values()].map((v) => structuredClone(v) as T));
  }
}
