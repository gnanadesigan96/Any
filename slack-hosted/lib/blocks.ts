/** Block Kit: review rows, approval buttons, the concern table and modals. */

import type { Settings } from "../config/settings.ts";
import { amount, dayTypeLabel, money, SHIFT_LABEL } from "./policy.ts";
import type { FinalReport } from "./report.ts";
import { STATUS_LABEL } from "./report.ts";
import type { Cycle, Entry } from "./store.ts";
import { cycleLabel, dayShort, periodText, prettyDate } from "./time.ts";

export const A = {
  reviewAccept: "review_accept",
  reviewReject: "review_reject",
  reviewAll: "review_all",
  approve: "allowance_approve",
  raiseConcern: "allowance_concern",
  concernRow: "concern_row",
  concernAdd: "concern_add",
  concernRespond: "concern_respond",
} as const;

export const V = {
  concern: "concern_modal",
  edit: "edit_entry_modal",
  add: "add_entry_modal",
  respond: "respond_modal",
} as const;

export const ROWS_PER_MESSAGE = 20; // Slack allows 50 blocks per message; review rows use 2 each

// deno-lint-ignore no-explicit-any
export type Block = Record<string, any>;

const md = (text: string) => ({ type: "mrkdwn", text });
const plain = (text: string) => ({ type: "plain_text", text: text.slice(0, 75), emoji: true });

function button(
  text: string,
  actionId: string,
  value: string,
  style?: "primary" | "danger",
  confirm?: [string, string, string],
) {
  const b: Block = { type: "button", text: plain(text), action_id: actionId, value };
  if (style) b.style = style;
  if (confirm) {
    b.confirm = { title: plain(confirm[0]), text: md(confirm[1]), confirm: plain(confirm[2]), deny: plain("Cancel") };
  }
  return b;
}

export function entryLine(e: Entry, withAmount: boolean): string {
  const parts = [
    `*${e.person_name}*`,
    `${dayShort(e.support_date)} ${prettyDate(e.support_date)}`,
    SHIFT_LABEL[e.shift],
    dayTypeLabel(e.support_date),
  ];
  if (withAmount) parts.push(money(amount(e.support_date, e.shift, !!e.extra_task).total));
  let line = parts.join(" · ");
  if (e.extra_task) line += `\n_Extra task: ${e.extra_task}_`;
  return line;
}

const option = (e: Entry) => ({
  text: plain(`${e.person_name} · ${prettyDate(e.support_date)} · ${SHIFT_LABEL[e.shift]}`),
  value: e.id,
});

/** Entry ids embedded (as block_id "row:<id>") in a message we posted. */
export const rowIds = (blocks: Block[] = []) =>
  blocks.map((b) => String(b.block_id ?? "")).filter((id) => id.startsWith("row:")).map((id) => id.slice(4));

// -- flagged entries (reviewer) ----------------------------------------------------------

export function reviewBlocks(s: Settings, cid: string, entries: Entry[]): Block[] {
  const blocks: Block[] = [{
    type: "section",
    text: md(
      `<@${s.reviewer}> these *${cycleLabel(cid)}* support entries need your decision - they are outside the ` +
        `allocation period (*${periodText(s, cid)}*) or overlap with someone else's shift. Accept or reject each one:`,
    ),
  }];
  const pending: string[] = [];
  for (const e of entries) {
    blocks.push({
      type: "section",
      block_id: `row:${e.id}`,
      text: md(`${entryLine(e, false)}\n:warning: ${e.flag_reason || "needs review"}`),
    });
    if (e.review === "pending") {
      pending.push(e.id);
      blocks.push({
        type: "actions",
        block_id: `act:${e.id}`,
        elements: [button("Accept", A.reviewAccept, e.id, "primary"), button("Reject", A.reviewReject, e.id, "danger")],
      });
    } else {
      const icon = e.review === "accepted" ? ":white_check_mark:" : ":x:";
      const who = e.reviewed_by ? ` by <@${e.reviewed_by}>` : "";
      blocks.push({ type: "context", elements: [md(`${icon} ${STATUS_LABEL[e.review]}${who}`)] });
    }
  }
  if (pending.length > 1) {
    blocks.push({
      type: "actions",
      elements: [
        button("Accept all", A.reviewAll, JSON.stringify({ d: "accepted", ids: pending })),
        button("Reject all", A.reviewAll, JSON.stringify({ d: "rejected", ids: pending }), "danger", [
          "Reject all?",
          `Reject all ${pending.length} entries?`,
          "Reject all",
        ]),
      ],
    });
  }
  return blocks;
}

// -- final approval (approver) -------------------------------------------------------------

export function approvalBlocks(s: Settings, cid: string, r: FinalReport, cycle: Cycle, response?: string) {
  const text = `<@${s.approver}> please review the support allowance for *${cycleLabel(cid)}* ` +
    `(period ${periodText(s, cid)}): ${r.people} people, ${r.entries} entries, total *${r.grandTotalText}*. ` +
    `The detailed tables are above.`;
  const blocks: Block[] = [{ type: "section", text: md(text) }];
  if (response) {
    blocks.push({
      type: "section",
      text: md(
        `*Your concern:* ${cycle.concern_text.slice(0, 1200)}\n*Response from <@${s.reviewer}>:* ${
          response.slice(0, 1200)
        }`,
      ),
    });
  }
  blocks.push({
    type: "actions",
    elements: [
      button("Approve", A.approve, cid, "primary", [
        "Approve?",
        `Approve ${cycleLabel(cid)} for ${r.grandTotalText} and notify HR?`,
        "Approve",
      ]),
      button("Raise concern", A.raiseConcern, cid, "danger"),
    ],
  });
  return { text, blocks };
}

// -- concern table (reviewer, edited in place) ------------------------------------------------

export function concernBlocks(s: Settings, cid: string, cycle: Cycle, entries: Entry[], closedNote?: string): Block[] {
  const blocks: Block[] = [{
    type: "section",
    text: md(
      `<@${s.reviewer}> <@${cycle.concern_by}> raised a concern on *${cycleLabel(cid)}*:\n>${
        cycle.concern_text.slice(0, 2000)
      }\n` +
        (closedNote ? "" : "Fix the entries below with the ⋮ menu, then press *Respond & send for approval*."),
    ),
  }];
  for (const e of entries.slice(0, 40)) {
    const gone = e.review === "rejected" || e.review === "removed";
    const text = gone ? `~${entryLine(e, true).split("\n")[0]}~  _${STATUS_LABEL[e.review]}_` : entryLine(e, true);
    const block: Block = { type: "section", block_id: `row:${e.id}`, text: md(text) };
    if (!closedNote && e.review === "removed") block.accessory = button("Restore", A.concernRow, `restore:${e.id}`);
    else if (!closedNote && e.review !== "rejected") {
      block.accessory = {
        type: "overflow",
        action_id: A.concernRow,
        options: [{ text: plain("Edit"), value: `edit:${e.id}` }, { text: plain("Remove"), value: `remove:${e.id}` }],
      };
    }
    blocks.push(block);
  }
  if (entries.length > 40) {
    blocks.push({
      type: "context",
      elements: [md(`_Showing 40 of ${entries.length} entries - ask me in chat to change the others._`)],
    });
  }
  if (closedNote) blocks.push({ type: "context", elements: [md(closedNote)] });
  else {
    blocks.push({
      type: "actions",
      elements: [
        button("Add entry", A.concernAdd, cid),
        button("Respond & send for approval", A.concernRespond, cid, "primary"),
      ],
    });
  }
  return blocks;
}

// -- modals ----------------------------------------------------------------------------------

function modal(callbackId: string, title: string, blocks: Block[], meta: unknown, submit = "Submit") {
  return {
    type: "modal",
    callback_id: callbackId,
    title: plain(title.slice(0, 24)),
    submit: plain(submit),
    close: plain("Cancel"),
    private_metadata: JSON.stringify(meta),
    blocks,
  };
}

function shiftSelect(initial?: string): Block {
  const opts = [
    { text: plain("Day shift"), value: "day" },
    { text: plain("Night shift"), value: "night" },
    { text: plain("No shift (extra task only)"), value: "none" },
  ];
  const el: Block = { type: "static_select", action_id: "v", options: opts };
  if (initial) el.initial_option = opts.find((o) => o.value === initial);
  return { type: "input", block_id: "shift", label: plain("Shift"), element: el };
}

function dateInput(initial?: string): Block {
  const el: Block = { type: "datepicker", action_id: "v" };
  if (initial) el.initial_date = initial;
  return { type: "input", block_id: "date", label: plain("Date"), element: el };
}

function extraInput(initial?: string): Block {
  const el: Block = {
    type: "plain_text_input",
    action_id: "v",
    placeholder: plain("Additional task performed (leave empty if none)"),
  };
  if (initial) el.initial_value = initial;
  return { type: "input", block_id: "extra", optional: true, label: plain("Extra task"), element: el };
}

export function concernModal(cid: string, entries: Entry[]) {
  const blocks: Block[] = [];
  if (entries.length) {
    blocks.push({
      type: "input",
      block_id: "entries",
      optional: true,
      label: plain("Which entries? (leave empty for the whole month)"),
      element: { type: "multi_static_select", action_id: "v", options: entries.slice(0, 100).map(option) },
    });
  }
  blocks.push({
    type: "input",
    block_id: "concern",
    label: plain("Concern"),
    element: { type: "plain_text_input", action_id: "v", multiline: true },
  });
  return modal(V.concern, "Raise a concern", blocks, { cid }, "Send to reviewer");
}

export function editModal(e: Entry) {
  return modal(
    V.edit,
    "Edit entry",
    [
      { type: "section", text: md(`*${e.person_name}*`) },
      dateInput(e.support_date),
      shiftSelect(e.shift),
      extraInput(e.extra_task),
    ],
    { id: e.id },
    "Save",
  );
}

export function addModal(cid: string) {
  return modal(
    V.add,
    "Add entry",
    [
      { type: "input", block_id: "person", label: plain("Person"), element: { type: "users_select", action_id: "v" } },
      dateInput(),
      shiftSelect(),
      extraInput(),
    ],
    { cid },
    "Add",
  );
}

export function respondModal(cid: string, cycle: Cycle) {
  return modal(
    V.respond,
    "Respond to concern",
    [
      { type: "section", text: md(`*Concern:* ${cycle.concern_text.slice(0, 2500)}`) },
      {
        type: "input",
        block_id: "response",
        label: plain("Your response"),
        element: { type: "plain_text_input", action_id: "v", multiline: true },
      },
    ],
    { cid },
    "Send for approval",
  );
}

/** Flatten a submitted modal's state into {block_id: value}. */
// deno-lint-ignore no-explicit-any
export function modalValues(view: any): Record<string, any> {
  // deno-lint-ignore no-explicit-any
  const out: Record<string, any> = {};
  for (const [blockId, actions] of Object.entries(view.state.values)) {
    // deno-lint-ignore no-explicit-any
    const v = (actions as any).v;
    out[blockId] = v.selected_date ?? v.selected_user ?? v.selected_option?.value ??
      (v.selected_options ? v.selected_options.map((o: { value: string }) => o.value) : undefined) ??
      ((v.value ?? "").trim() || null);
  }
  return out;
}
