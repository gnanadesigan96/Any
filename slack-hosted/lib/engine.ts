/**
 * The monthly support-allowance cycle (same behaviour as the tested Python version).
 *
 *   17th     reminder in the support channel
 *   19th     "last day" reminder; window closes at 19th EOD
 *   flags    dates outside the period / overlapping shifts go to the reviewer (Accept / Reject)
 *   close    final tables in the approval channel, approver tagged (Approve / Raise concern)
 *   concern  comes back to the reviewer as an editable table -> "Respond & send for approval"
 *   approve  HR tagged
 *   nudges   whoever a step waits on is re-tagged every N minutes (max M times, not in quiet hours)
 *
 * Cycle status: open -> [reviewing] -> pending_approval <-> concern -> approved   (or "empty")
 *
 * Run on Slack specifics: buttons on a message only work while the function execution that
 * posted it is still running. Every interactive message is therefore registered as "live" with its
 * execution id; once none of an execution's messages need clicks any more, it is completed.
 */

import { RATES, type Settings } from "../config/settings.ts";
import * as B from "./blocks.ts";
import { type Shift, SHIFT_LABEL } from "./policy.ts";
import { codeBlocks, finalReport } from "./report.ts";
import { type Cycle, type Entry, isPayable, type Store } from "./store.ts";
import {
  closeAt,
  cycleIdFor,
  cycleLabel,
  formatLocal,
  localDateIso,
  nextCycleId,
  parseIsoDate,
  period,
  periodText,
  prettyDate,
  prevCycleId,
  slotAt,
  toLocal,
  waitedText,
} from "./time.ts";

// deno-lint-ignore no-explicit-any
export type SlackClient = any;

export const EDITABLE: Cycle["status"][] = ["open", "reviewing", "concern"];

export type NewEntry = {
  date: string;
  shift: Shift;
  extra_task?: string;
  review?: Entry["review"];
  flag_reason?: string;
  reviewed_by?: string;
};

export class Engine {
  private names = new Map<string, string>();

  constructor(
    public client: SlackClient,
    public store: Store,
    public s: Settings,
    /** The function execution we are running in (owns any interactive message we post). */
    public executionId: string,
    private realNow: () => Date = () => new Date(),
  ) {}

  // -- clock ------------------------------------------------------------------------------

  /** Real time in production; in test mode a pretend time anchored by the test triggers. */
  async now(): Promise<Date> {
    const real = this.realNow();
    if (this.s.mode !== "test") return real;
    const anchor = await this.store.meta("pretend_anchor");
    if (!anchor) return real;
    const { pretend, at } = JSON.parse(anchor);
    return new Date(new Date(pretend).getTime() + (real.getTime() - new Date(at).getTime()));
  }

  /** Test mode: jump the pretend clock (called by the test schedule triggers). */
  async setPretendNow(pretendLocal: string): Promise<void> {
    const [d, t] = pretendLocal.split("T");
    const [y, m, day] = d.split("-").map(Number);
    const [hh, mm] = (t ?? "00:00").split(":").map(Number);
    const pretend = new Date(Date.UTC(y, m - 1, day, hh, mm) - this.s.utcOffsetMinutes * 60_000);
    await this.store.setMeta(
      "pretend_anchor",
      JSON.stringify({ pretend: pretend.toISOString(), at: this.realNow().toISOString() }),
    );
  }

  private tag(): string {
    return this.s.mode === "test" ? ":test_tube: *[TEST]* " : "";
  }

  // -- helpers -------------------------------------------------------------------------------

  async userName(id: string): Promise<string> {
    if (!this.names.has(id)) {
      try {
        const r = await this.client.users.info({ user: id });
        this.names.set(id, r.ok ? (r.user?.real_name || r.user?.name || id) : id);
      } catch {
        return id;
      }
    }
    return this.names.get(id)!;
  }

  private async post(args: Record<string, unknown>) {
    const r = await this.client.chat.postMessage(args);
    if (!r.ok) throw new Error(`chat.postMessage failed: ${r.error}`);
    return r;
  }

  private get reviewTarget() {
    return this.s.reviewChannel || this.s.collectionChannel;
  }
  private get hrChannel() {
    return this.s.hrChannel || this.s.approvalChannel;
  }
  hrMention(): string {
    const parts = this.s.hrGroup ? [`<!subteam^${this.s.hrGroup}>`] : [];
    return [...parts, ...this.s.hrUsers.map((u) => `<@${u}>`)].join(" ") || "HR team";
  }
  get allowedChannels(): string[] {
    return [...new Set([this.s.collectionChannel, this.reviewTarget, this.s.approvalChannel, this.hrChannel])];
  }
  isAdmin(user: string): boolean {
    return user === this.s.reviewer || user === this.s.approver;
  }

  private async postInteractive(
    kind: "review" | "approval" | "concern",
    cid: string,
    args: Record<string, unknown>,
    entryIds: string[] = [],
  ) {
    const r = await this.post(args);
    await this.store.registerLive({
      channel: r.channel,
      ts: r.ts,
      kind,
      cycle_id: cid,
      execution_id: this.executionId,
      entry_ids: JSON.stringify(entryIds),
    });
    return r;
  }

  /** The message no longer needs clicks; complete its execution if nothing else of it is live. */
  private async retire(channel: string, ts: string) {
    const m = await this.store.retireLive(channel, ts);
    if (m) await this.completeIfIdle(m.execution_id);
  }

  /** TEST mode only: archive all data (nothing is deleted) so the test can be run again from scratch. */
  async resetTestData(user: string): Promise<string> {
    if (this.s.mode !== "test") return "Reset is only available in test mode.";
    if (user !== this.s.reviewer) return "Only the reviewer can reset the test data.";
    const r = await this.store.archiveAll();
    for (const ex of r.executions) await this.completeIfIdle(ex);
    return `Archived ${r.entries} entries and reset ${r.cycles} month(s). Create the test timeline triggers again to restart.`;
  }

  async completeIfIdle(executionId: string): Promise<boolean> {
    if (!executionId || (await this.store.liveMessages({ execution_id: executionId })).length) return false;
    if (executionId === this.executionId) return true; // the caller completes its own execution
    try {
      await this.client.functions.completeSuccess({ function_execution_id: executionId, outputs: {} });
    } catch { /* already completed */ }
    return true;
  }

  // -- window & flags ----------------------------------------------------------------------------

  async submissionCycle(now?: Date): Promise<string> {
    now ??= await this.now();
    let cid = cycleIdFor(this.s, now);
    if (now >= closeAt(this.s, cid)) cid = nextCycleId(cid);
    for (let c = await this.store.cycle(cid); c && c.status !== "open"; c = await this.store.cycle(cid)) {
      cid = nextCycleId(cid);
    }
    return cid;
  }

  async windowState(now?: Date) {
    now ??= await this.now();
    const cid = cycleIdFor(this.s, now);
    const opens = slotAt(this.s, cid, this.s.schedule.reminder), closes = closeAt(this.s, cid);
    const status = (await this.store.cycle(cid))?.status ?? "open";
    if (opens <= now && now < closes && status === "open") return { open: true as const, cycle: cid, closes };
    const next = now >= opens ? nextCycleId(cid) : cid;
    return {
      open: false as const,
      cycle: cid,
      nextCycle: next,
      nextOpens: slotAt(this.s, next, this.s.schedule.reminder),
    };
  }

  flagReason(cid: string, iso: string): string {
    const p = period(this.s, cid);
    if (iso < p.first) return `before the period (${periodText(this.s, cid)})`;
    if (iso > p.last) return `after the period (${periodText(this.s, cid)})`;
    return "";
  }

  private overlapText(others: { person_name: string }[], shift: Shift) {
    const names = [...new Set(others.map((o) => o.person_name))].sort().join(", ");
    return `overlaps with ${names}'s ${SHIFT_LABEL[shift].toLowerCase()} shift`;
  }

  async entryFlags(cid: string, personId: string, iso: string, shift: Shift): Promise<string> {
    const reasons = [this.flagReason(cid, iso)].filter(Boolean);
    const others = await this.store.overlaps(iso, shift, personId);
    if (others.length) reasons.push(this.overlapText(others, shift));
    return reasons.join("; ");
  }

  /** A new entry overlapping someone's recorded shift puts that entry up for review too. Returns {cid: ids}. */
  async flagOverlapPartners(newEntries: Entry[]): Promise<Record<string, string[]>> {
    const flagged: Record<string, string[]> = {};
    for (const n of newEntries) {
      for (const o of await this.store.overlaps(n.support_date, n.shift, n.person_id)) {
        const status = (await this.store.cycle(o.cycle_id))?.status ?? "open";
        if (o.review !== "" || !EDITABLE.includes(status)) continue;
        await this.store.updateEntry(o.id, { review: "pending", flag_reason: this.overlapText([n], o.shift) });
        (flagged[o.cycle_id] ??= []).push(o.id);
        await this.threadNote(
          o,
          `<@${o.person_id}> heads up: ${n.person_name} also claimed the ${SHIFT_LABEL[o.shift].toLowerCase()} ` +
            `shift on ${prettyDate(o.support_date)}. <@${this.s.reviewer}> will decide which entry stands.`,
        );
      }
    }
    return flagged;
  }

  private async threadNote(e: Entry, text: string) {
    if (!e.thread_channel) return;
    try {
      await this.client.chat.postMessage({ channel: e.thread_channel, thread_ts: e.thread_ts, text });
    } catch { /* best effort */ }
  }

  // -- submissions (used by the chat tools) ---------------------------------------------------------

  async addEntries(
    cid: string,
    personId: string,
    personName: string,
    items: NewEntry[],
    submittedBy: string,
    thread: [string, string] = ["", ""],
  ): Promise<{ added: Entry[]; duplicates: (NewEntry & { already_in: string })[] }> {
    const added: Entry[] = [], duplicates: (NewEntry & { already_in: string })[] = [];
    for (const it of items) {
      const dup = await this.store.duplicateOf(personId, it.date, it.shift);
      if (dup) {
        duplicates.push({ ...it, already_in: dup });
        continue;
      }
      const e: Entry = {
        id: crypto.randomUUID(),
        cycle_id: cid,
        person_id: personId,
        person_name: personName,
        support_date: it.date,
        shift: it.shift,
        extra_task: it.extra_task ?? "",
        review: it.review ?? "",
        reviewed_by: it.reviewed_by ?? "",
        flag_reason: it.flag_reason ?? "",
        thread_channel: thread[0],
        thread_ts: thread[1],
        submitted_by: submittedBy,
        submitted_at: new Date().toISOString(),
      };
      await this.store.putEntry(e);
      added.push(e);
    }
    return { added, duplicates };
  }

  // -- scheduler ----------------------------------------------------------------------------------

  async tick(now?: Date): Promise<void> {
    now ??= await this.now();
    const thisMonth = cycleIdFor(this.s, now);
    for (const cid of [prevCycleId(thisMonth), thisMonth]) {
      const close = closeAt(this.s, cid);
      const c = await this.store.cycle(cid);
      if (cid === thisMonth && now < close) {
        const closingAt = this.s.schedule.closingReminder ? slotAt(this.s, cid, this.s.schedule.closingReminder) : null;
        if (!c?.reminder_sent_at && now >= slotAt(this.s, cid, this.s.schedule.reminder)) {
          await this.postReminder(cid);
          // Started late (bot was down): one reminder is enough, don't post two back to back.
          if (closingAt && now >= closingAt) {
            await this.store.updateCycle(cid, { closing_reminder_sent_at: now.toISOString() });
          }
        } else if (closingAt && c && !c.closing_reminder_sent_at && now >= closingAt) {
          await this.postClosingReminder(cid);
        }
      }
      const fresh = await this.store.cycle(cid);
      if (
        now >= close && fresh?.status === "open" && (fresh.reminder_sent_at || (await this.store.entries(cid)).length)
      ) {
        await this.closeCycle(cid);
      }
    }
    await this.sendNudges(now);
  }

  private deadlineText(cid: string) {
    return formatLocal(this.s, slotAt(this.s, cid, this.s.schedule.close));
  }

  async postReminder(cid: string) {
    await this.store.updateCycle(cid, { reminder_sent_at: (await this.now()).toISOString() });
    await this.post({
      channel: this.s.collectionChannel,
      text: `${this.tag()}<!channel> :wave: Time to submit your *support details for ${cycleLabel(cid)}* ` +
        `(support dates *${
          periodText(this.s, cid)
        }*).\nMention me in this channel with the dates and shifts, for example:\n` +
        `> @ops-agent Night shift 3, 4 Oct; day shift 11 Oct, on 11th also did the DB failover\n` +
        `I'll reply with a table of what I recorded so you can check it.\n*Window closes: ${this.deadlineText(cid)}.*`,
    });
  }

  async postClosingReminder(cid: string) {
    await this.store.updateCycle(cid, { closing_reminder_sent_at: (await this.now()).toISOString() });
    await this.post({
      channel: this.s.collectionChannel,
      text:
        `${this.tag()}<!channel> :hourglass_flowing_sand: Last day to submit support details for ${
          cycleLabel(cid)
        } - ` +
        `the window closes *${this.deadlineText(cid)}*.`,
    });
  }

  private async startWaiting(): Promise<Partial<Cycle>> {
    return { waiting_since: (await this.now()).toISOString(), nudges_sent: 0 };
  }

  async closeCycle(cid: string): Promise<string> {
    await this.store.ensureCycle(cid);
    const now = (await this.now()).toISOString();
    if (!(await this.store.entries(cid)).length) {
      if (await this.store.transition(cid, ["open"], "empty", { closed_at: now })) {
        await this.post({
          channel: this.s.approvalChannel,
          text: `${this.tag()}No support details were submitted for ${cycleLabel(cid)} - nothing to approve.`,
        });
      }
      return "empty";
    }
    const pending = await this.store.pendingReviews(cid);
    const to = pending.length ? "reviewing" : "pending_approval";
    if (!(await this.store.transition(cid, ["open"], to, { closed_at: now, ...(await this.startWaiting()) }))) {
      return (await this.store.cycle(cid))!.status;
    }
    const next = slotAt(this.s, nextCycleId(cid), this.s.schedule.reminder);
    await this.post({
      channel: this.s.collectionChannel,
      text:
        `${this.tag()}:lock: The support details window for ${
          cycleLabel(cid)
        } is closed and has been sent for approval. ` +
        (this.s.outsideWindow === "next_cycle"
          ? "Anything new will go into next month's cycle."
          : `The next window opens on ${formatLocal(this.s, next).split(",")[0]}.`),
    });
    if (pending.length) {
      await this.post({
        channel: this.reviewTarget,
        text:
          `${this.tag()}<@${this.s.reviewer}> the ${cycleLabel(cid)} window is closed. *${pending.length} flagged ` +
          `entr${
            pending.length === 1 ? "y" : "ies"
          }* still need your decision before the final table goes to <@${this.s.approver}>:`,
      });
      await this.notifyReviewer(cid, pending.map((e) => e.id));
    } else {
      await this.postForApproval(cid);
    }
    return to;
  }

  // -- flag review ------------------------------------------------------------------------------

  async notifyReviewer(cid: string, ids: string[]) {
    for (let i = 0; i < ids.length; i += B.ROWS_PER_MESSAGE) {
      const chunk = await this.store.entries(cid, { ids: ids.slice(i, i + B.ROWS_PER_MESSAGE) });
      const names = [...new Set(chunk.map((e) => e.person_name))].sort().join(", ");
      await this.postInteractive("review", cid, {
        channel: this.reviewTarget,
        text: `Support entries for ${cycleLabel(cid)} need your review (${names}).`,
        blocks: B.reviewBlocks(this.s, cid, chunk),
      }, chunk.map((e) => e.id));
    }
  }

  async review(entryId: string, decision: "accepted" | "rejected", user: string): Promise<string> {
    if (user !== this.s.reviewer) return "not_authorised";
    const e = await this.store.entry(entryId);
    if (!e || e.review !== "pending") return "already_decided";
    await this.store.updateEntry(entryId, { review: decision, reviewed_by: user });
    await this.threadNote(
      e,
      `<@${e.person_id}> <@${user}> *${decision}* your ${SHIFT_LABEL[e.shift].toLowerCase()} shift entry for ` +
        `${prettyDate(e.support_date)} (${e.flag_reason}).`,
    );
    return decision;
  }

  /** Re-render every live review message of a cycle; retire the fully decided ones; release the cycle. */
  async afterReviews(cid: string) {
    for (const m of await this.store.liveMessages({ kind: "review", cycle_id: cid })) {
      const ids: string[] = JSON.parse(m.entry_ids || "[]");
      const entries = (await Promise.all(ids.map((id) => this.store.entry(id)))).filter((e): e is Entry => !!e);
      if (!entries.length) continue;
      await this.client.chat.update({
        channel: m.channel,
        ts: m.ts,
        text: "Support entries needing review",
        blocks: B.reviewBlocks(this.s, cid, entries),
      });
      if (!entries.some((e) => e.review === "pending")) await this.retire(m.channel, m.ts);
    }
    if (
      !(await this.store.pendingReviews(cid)).length &&
      await this.store.transition(cid, ["reviewing"], "pending_approval")
    ) {
      await this.post({
        channel: this.reviewTarget,
        text: `${this.tag()}All flagged entries for ${
          cycleLabel(cid)
        } are decided - sending the final table to <@${this.s.approver}>.`,
      });
      await this.postForApproval(cid);
    }
  }

  // -- final approval ------------------------------------------------------------------------------

  private async postReport(channel: string, cid: string, title: string) {
    const r = finalReport(await this.store.entries(cid, { payableOnly: true }));
    await this.post({
      channel,
      text: `*${title}*\nPeriod ${
        periodText(this.s, cid)
      } · ${r.people} people · ${r.entries} entries · total *${r.grandTotalText}*\n\n*Summary*`,
    });
    for (const b of codeBlocks(r.summary)) await this.post({ channel, text: b });
    await this.post({ channel, text: "*Details*" });
    for (const b of codeBlocks(r.detail)) await this.post({ channel, text: b });
    return r;
  }

  async postForApproval(cid: string, response?: string) {
    const r = await this.postReport(
      this.s.approvalChannel,
      cid,
      `${this.tag()}Support allowance - ${cycleLabel(cid)}${response ? " (updated)" : ""}`,
    );
    const { text, blocks } = B.approvalBlocks(this.s, cid, r, (await this.store.cycle(cid))!, response);
    const msg = await this.postInteractive("approval", cid, { channel: this.s.approvalChannel, text, blocks });
    await this.store.updateCycle(cid, {
      approval_channel: msg.channel,
      approval_ts: msg.ts,
      ...(await this.startWaiting()),
    });
  }

  private async replaceMessage(channel: string, ts: string, text: string) {
    if (!ts) return;
    await this.client.chat.update({ channel, ts, text, blocks: [{ type: "section", text: { type: "mrkdwn", text } }] });
  }

  async approve(cid: string, user: string): Promise<string> {
    if (user !== this.s.approver) return "not_authorised";
    const now = await this.now();
    if (
      !(await this.store.transition(cid, ["pending_approval"], "approved", {
        decided_by: user,
        decided_at: now.toISOString(),
      }))
    ) {
      return (await this.store.cycle(cid))?.status ?? "unknown";
    }
    const c = (await this.store.cycle(cid))!;
    const r = finalReport(await this.store.entries(cid, { payableOnly: true }));
    await this.replaceMessage(
      c.approval_channel,
      c.approval_ts,
      `:white_check_mark: *${cycleLabel(cid)}* support allowance (${r.grandTotalText}) approved by <@${user}> on ${
        formatLocal(this.s, now)
      }.`,
    );
    if (this.hrChannel !== this.s.approvalChannel) {
      await this.postReport(this.hrChannel, cid, `Support allowance - ${cycleLabel(cid)} (approved)`);
    }
    await this.post({
      channel: this.hrChannel,
      text:
        `${this.tag()}${this.hrMention()} The support incentive data for *${periodText(this.s, cid)}* (${
          cycleLabel(cid)
        } cycle) ` +
        `is updated and approved by <@${user}>. ${r.people} people, total *${r.grandTotalText}*. ` +
        `Please find the detailed tables above for processing.`,
    });
    await this.retire(c.approval_channel, c.approval_ts);
    return "approved";
  }

  // -- concerns ----------------------------------------------------------------------------------

  async raiseConcern(cid: string, user: string, text: string, entryIds: string[] = []): Promise<string> {
    if (user !== this.s.approver) return "not_authorised";
    const ids = entryIds.length ? entryIds : (await this.store.entries(cid)).map((e) => e.id);
    if (
      !(await this.store.transition(cid, ["pending_approval"], "concern", {
        concern_text: text,
        concern_by: user,
        concern_entry_ids: JSON.stringify(ids),
      }))
    ) {
      return (await this.store.cycle(cid))?.status ?? "unknown";
    }
    const c = (await this.store.cycle(cid))!;
    await this.replaceMessage(
      c.approval_channel,
      c.approval_ts,
      `:warning: <@${user}> raised a concern on *${
        cycleLabel(cid)
      }* - <@${this.s.reviewer}> is addressing it in the thread.`,
    );
    const msg = await this.postInteractive("concern", cid, {
      channel: c.approval_channel,
      thread_ts: c.approval_ts,
      reply_broadcast: true,
      text: `<@${this.s.reviewer}> concern from <@${user}> on ${cycleLabel(cid)}: ${text}`,
      blocks: await this.concernBlocks(cid),
    });
    await this.store.updateCycle(cid, {
      concern_channel: msg.channel,
      concern_ts: msg.ts,
      ...(await this.startWaiting()),
    });
    await this.retire(c.approval_channel, c.approval_ts);
    return "concern";
  }

  private async concernBlocks(cid: string, closedNote?: string) {
    const c = (await this.store.cycle(cid))!;
    const ids: string[] = JSON.parse(c.concern_entry_ids || "[]");
    return B.concernBlocks(this.s, cid, c, await this.store.entries(cid, { ids }), closedNote);
  }

  async refreshConcern(cid: string) {
    const c = await this.store.cycle(cid);
    if (c?.status === "concern" && c.concern_ts) {
      await this.client.chat.update({
        channel: c.concern_channel,
        ts: c.concern_ts,
        text: `Concern on ${cycleLabel(cid)}`,
        blocks: await this.concernBlocks(cid),
      });
    }
  }

  async checkReviewerEdit(cid: string, user: string): Promise<string> {
    if (user !== this.s.reviewer) return "Only the reviewer can change entries here.";
    const status = (await this.store.cycle(cid))?.status ?? "open";
    return EDITABLE.includes(status)
      ? ""
      : `${cycleLabel(cid)} is ${status.replace("_", " ")} - it can't be edited now.`;
  }

  private async validate(cid: string, personId: string, iso: string, shift: Shift, extra: string, excludeId = "") {
    if (!parseIsoDate(iso)) return { reason: "", error: "Pick a valid date." };
    if (shift === "none" && !extra) return { reason: "", error: "Pick a shift or describe the extra task." };
    const dup = await this.store.duplicateOf(personId, iso, shift, excludeId);
    if (dup) return { reason: "", error: `Already claimed for this date and shift in ${cycleLabel(dup)}.` };
    const others = await this.store.overlaps(iso, shift, personId, excludeId);
    if (others.length) {
      return {
        reason: "",
        error: `That ${this.overlapText(others, shift)} on this date - remove or change theirs first.`,
      };
    }
    return { reason: this.flagReason(cid, iso), error: "" };
  }

  async setRowRemoved(entryId: string, user: string, removed: boolean): Promise<string> {
    const e = await this.store.entry(entryId);
    if (!e) return "Entry not found.";
    const err = await this.checkReviewerEdit(e.cycle_id, user);
    if (err) return err;
    if (!removed) {
      const dup = await this.store.duplicateOf(e.person_id, e.support_date, e.shift, entryId);
      if (dup) return `Can't restore - already claimed in ${cycleLabel(dup)}.`;
      const others = await this.store.overlaps(e.support_date, e.shift, e.person_id, entryId);
      if (others.length) return `Can't restore - it ${this.overlapText(others, e.shift)}.`;
    }
    await this.store.updateEntry(entryId, {
      review: removed ? "removed" : (e.flag_reason ? "accepted" : ""),
      reviewed_by: user,
    });
    await this.refreshConcern(e.cycle_id);
    return "";
  }

  async editEntry(entryId: string, user: string, iso: string, shift: Shift, extra: string): Promise<string> {
    const e = await this.store.entry(entryId);
    if (!e) return "Entry not found.";
    const err = await this.checkReviewerEdit(e.cycle_id, user);
    if (err) return err;
    const v = await this.validate(e.cycle_id, e.person_id, iso, shift, extra, entryId);
    if (v.error) return v.error;
    await this.store.updateEntry(entryId, {
      support_date: iso,
      shift,
      extra_task: extra,
      review: v.reason ? "accepted" : "",
      reviewed_by: user,
      flag_reason: v.reason,
    });
    await this.refreshConcern(e.cycle_id);
    return "";
  }

  async addEntryByReviewer(
    cid: string,
    user: string,
    personId: string,
    iso: string,
    shift: Shift,
    extra: string,
  ): Promise<string> {
    const err = await this.checkReviewerEdit(cid, user);
    if (err) return err;
    const v = await this.validate(cid, personId, iso, shift, extra);
    if (v.error) return v.error;
    const { added } = await this.addEntries(cid, personId, await this.userName(personId), [{
      date: iso,
      shift,
      extra_task: extra,
      review: v.reason ? "accepted" : "",
      reviewed_by: v.reason ? user : "",
      flag_reason: v.reason,
    }], await this.userName(user));
    const c = (await this.store.cycle(cid))!;
    if (c.status === "concern") {
      await this.store.updateCycle(cid, {
        concern_entry_ids: JSON.stringify([...JSON.parse(c.concern_entry_ids || "[]"), added[0].id]),
      });
      await this.refreshConcern(cid);
    }
    return "";
  }

  async respondToConcern(cid: string, user: string, response: string): Promise<string> {
    if (user !== this.s.reviewer) return "not_authorised";
    if (!(await this.store.transition(cid, ["concern"], "pending_approval"))) {
      return (await this.store.cycle(cid))?.status ?? "unknown";
    }
    const c = (await this.store.cycle(cid))!;
    await this.client.chat.update({
      channel: c.concern_channel,
      ts: c.concern_ts,
      text: `Concern on ${cycleLabel(cid)} addressed`,
      blocks: await this.concernBlocks(cid, `:speech_balloon: <@${user}> responded: ${response}`),
    });
    await this.postForApproval(cid, response);
    await this.retire(c.concern_channel, c.concern_ts);
    return "pending_approval";
  }

  // -- nudges -----------------------------------------------------------------------------------

  private inQuietHours(now: Date): boolean {
    const q = this.s.nudges.quietHours;
    if (!q) return false;
    const h = toLocal(this.s, now).hh;
    return q.from > q.to ? (h >= q.from || h < q.to) : (h >= q.from && h < q.to);
  }

  async sendNudges(now?: Date) {
    now ??= await this.now();
    if (this.inQuietHours(now)) return;
    const every = this.s.nudges.everyMinutes * 60_000;
    for (const c of await this.store.waitingCycles()) {
      if (!c.waiting_since || c.nudges_sent >= this.s.nudges.max) continue;
      const since = new Date(c.waiting_since).getTime();
      if (now.getTime() < since + every * (c.nudges_sent + 1)) continue;
      await this.store.updateCycle(c.cycle_id, { nudges_sent: c.nudges_sent + 1 });
      await this.nudge(c, waitedText(now.getTime() - since));
    }
  }

  private async nudge(c: Cycle, waited: string) {
    const cid = c.cycle_id, tag = this.tag();
    if (c.status === "pending_approval" && c.approval_ts) {
      const r = finalReport(await this.store.entries(cid, { payableOnly: true }));
      await this.post({
        channel: c.approval_channel,
        thread_ts: c.approval_ts,
        reply_broadcast: true,
        text: `${tag}:alarm_clock: <@${this.s.approver}> reminder: the support allowance for *${cycleLabel(cid)}* ` +
          `(total *${r.grandTotalText}*) has been waiting for your approval for ${waited}. ` +
          `Please use the *Approve* / *Raise concern* buttons on the message above.`,
      });
    } else if (c.status === "reviewing") {
      const pending = await this.store.pendingReviews(cid);
      if (pending.length) {
        await this.post({
          channel: this.reviewTarget,
          text:
            `${tag}:alarm_clock: <@${this.s.reviewer}> reminder: ${pending.length} flagged entr${
              pending.length === 1 ? "y" : "ies"
            } ` +
            `for *${cycleLabel(cid)}* still need your Accept / Reject (${waited} so far). The final table goes to ` +
            `<@${this.s.approver}> once they're decided.`,
        });
      }
    } else if (c.status === "concern" && c.concern_ts) {
      await this.post({
        channel: c.concern_channel,
        thread_ts: c.concern_ts,
        text:
          `${tag}:alarm_clock: <@${this.s.reviewer}> reminder: <@${c.concern_by}>'s concern on *${
            cycleLabel(cid)
          }* is still open ` +
          `(${waited}). Fix the rows above and press *Respond & send for approval*.`,
      });
    }
  }

  // -- misc for tools ---------------------------------------------------------------------------

  today = async () => localDateIso(this.s, await this.now());
  holidaysIn(cid: string): string[] {
    const p = period(this.s, cid);
    return Object.entries(RATES.holidays).filter(([d]) => d >= p.first && d <= p.last).map(([d, n]) => `${d} ${n}`);
  }
  payable = isPayable;
}
