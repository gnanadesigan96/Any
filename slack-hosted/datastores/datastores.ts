/** Slack-hosted datastores (names must match DATASTORES in lib/store.ts). */

import { DefineDatastore, Schema } from "deno-slack-sdk/mod.ts";

const str = { type: Schema.types.string };
const num = { type: Schema.types.number };
const bool = { type: Schema.types.boolean };

export const CyclesDatastore = DefineDatastore({
  name: "support_cycles",
  primary_key: "cycle_id",
  attributes: {
    cycle_id: str,
    status: str,
    reminder_sent_at: str,
    closing_reminder_sent_at: str,
    closed_at: str,
    approval_channel: str,
    approval_ts: str,
    decided_by: str,
    decided_at: str,
    concern_text: str,
    concern_by: str,
    concern_entry_ids: str,
    concern_channel: str,
    concern_ts: str,
    waiting_since: str,
    nudges_sent: num,
  },
});

export const EntriesDatastore = DefineDatastore({
  name: "support_entries",
  primary_key: "id",
  attributes: {
    id: str,
    cycle_id: str,
    person_id: str,
    person_name: str,
    support_date: str,
    shift: str,
    extra_task: str,
    review: str,
    reviewed_by: str,
    flag_reason: str,
    thread_channel: str,
    thread_ts: str,
    submitted_by: str,
    submitted_at: str,
  },
});

export const LiveMessagesDatastore = DefineDatastore({
  name: "support_live_messages",
  primary_key: "key",
  attributes: {
    key: str,
    channel: str,
    ts: str,
    kind: str,
    cycle_id: str,
    execution_id: str,
    entry_ids: str,
    live: bool,
  },
});

export const MetaDatastore = DefineDatastore({
  name: "support_meta",
  primary_key: "key",
  attributes: { key: str, value: str },
});
