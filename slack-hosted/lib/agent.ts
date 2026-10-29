/**
 * The conversational agent: Claude reads the message, calls the tools below, and writes the reply.
 * Amounts, flags and permissions are all decided by the tools (code), never by the model.
 *
 * Claude is called over HTTPS (Messages API) instead of the npm SDK, because Slack's hosted Deno
 * runtime can't be relied on to bundle npm packages. A time budget keeps every reply inside Slack's
 * 60-second limit for hosted functions.
 */

import { codeBlocks, finalReport, submissionTable, teamTable } from "./report.ts";
import * as analytics from "./analytics.ts";
import { type Engine, type NewEntry } from "./engine.ts";
import type { Shift } from "./policy.ts";
import type { Entry } from "./store.ts";
import {
  cycleIdFor,
  cycleLabel,
  dayName,
  formatLocal,
  isoDate,
  parseIsoDate,
  periodText,
  prevCycleId,
  slotAt,
} from "./time.ts";

export type Request = {
  userId: string;
  userName: string;
  channelId: string;
  threadTs: string;
  attachments: string[]; // exact text (tables) posted after the reply
  privateTo: string; // set when the whole answer must be shown only to this person
};

const SYSTEM_PROMPT =
  `You are a helpful operations assistant in the team's Slack workspace. People @mention you in the \
team's support channels (you don't take direct messages). Answer what you can and use your tools whenever a request \
touches data they cover.

Support allowance workflow (monthly; reminders, closing, approval posts, nudges and the HR notification are automated, \
and the reviewer/approver mostly use buttons - but they can also just ask you):
- When someone shares the days they were on support, call submit_support_details right away. Work out exact YYYY-MM-DD \
dates (assume the most recent occurrence when no year/month is given; use expand_date_range for ranges). Shift is "day" or \
"night"; if they don't say, ask. Put any additional task they did on a date in extra_task.
- Each month's allocation period runs from the 21st of the previous month to the 20th (submissions open on the 17th, so \
the 18th-20th may be submitted in advance). Dates outside it, and day/night shifts that overlap another person's same shift \
on the same date, are still recorded but flagged for the reviewer; tell the person what was flagged and why. Extra tasks / \
night calls may overlap freely.
- If one message covers several people (with Slack IDs like U0123ABC), submit once per person using person_slack_id.
- Tables are posted automatically under your reply. Don't redraw them. Never mention or estimate amounts unless a tool \
returned them - money is shown only to the reviewer/approver in the approval channel. If a tool says amounts are hidden, say where to ask.
- If a tool says the window is closed, tell the person exactly that (with the next opening date) and that nothing was recorded.
- If a date, shift or person is genuinely ambiguous, ask instead of guessing.
- Comparisons and trends are restricted: if compare_support_months returns no_access, politely say the person doesn't have \
access (no numbers, no hints). When it works, the answer is shown only to the requester, so give the full story: the \
headline change, then what drove it (people, day vs night, weekends/holidays, extra tasks, new or missing people, flags) and \
caveats in "notes". Use only numbers from the tool.

Replies go to Slack: keep them short (1-3 lines when a table follows; analyses up to ~8 bullets) and use Slack mrkdwn \
(*bold*, _italic_, \`code\`, bullets with "•"). No markdown headings or tables.`;

// -- tools ---------------------------------------------------------------------------------

type Tool = { name: string; description: string; input_schema: Record<string, unknown> };
const str = (description: string) => ({ type: "string", description });

export const TOOLS: Tool[] = [
  {
    name: "expand_date_range",
    description:
      'List every date between two dates (inclusive) with the weekday name. Use it to turn "1st to 7th Oct" into exact dates.',
    input_schema: {
      type: "object",
      properties: {
        start: str("First date, YYYY-MM-DD."),
        end: str("Last date, YYYY-MM-DD."),
        weekdays_only: { type: "boolean" },
      },
      required: ["start", "end"],
    },
  },
  {
    name: "submit_support_details",
    description:
      "Record support days someone was on duty. Call this whenever a person shares their support details. A table of " +
      "what was recorded is posted automatically below your reply - don't repeat it or mention amounts.",
    input_schema: {
      type: "object",
      properties: {
        entries: {
          type: "array",
          description: "One item per date and shift. Expand ranges into separate dates.",
          items: {
            type: "object",
            properties: {
              date: str("YYYY-MM-DD"),
              shift: {
                type: "string",
                enum: ["day", "night", "none"],
                description: '"none" only for an extra task on a day without a shift',
              },
              extra_task: str("Brief description of any additional task that day; omit if none."),
            },
            required: ["date", "shift"],
          },
        },
        person_slack_id: str("Slack user ID when submitting for someone else. Empty for the person asking."),
        cycle: str("Reviewer only: YYYY-MM month to add to after its window closed (e.g. while fixing a concern)."),
      },
      required: ["entries"],
    },
  },
  {
    name: "remove_support_details",
    description:
      'Remove wrongly submitted support days (e.g. "remove my 3 Oct night shift"). The updated table is posted automatically.',
    input_schema: {
      type: "object",
      properties: {
        dates: { type: "array", items: { type: "string" }, description: "Dates to remove, YYYY-MM-DD." },
        shift: str('"day" or "night" to remove only that shift; empty removes every entry on those dates.'),
        person_slack_id: str("Reviewer only: whose entries. Empty for the person asking."),
        cycle: str("Reviewer only: YYYY-MM month after its window closed."),
      },
      required: ["dates"],
    },
  },
  {
    name: "show_support_details",
    description:
      "Show recorded support details. Team members see their own (no amounts). The reviewer/approver can see anyone's, " +
      "or - with no person - the whole month (amounts only in the approval channel). Posted automatically.",
    input_schema: {
      type: "object",
      properties: {
        person_slack_id: str("Whose details. Empty = the person asking (or everyone for the reviewer/approver)."),
        cycle: str("YYYY-MM. Empty = the open window."),
      },
    },
  },
  {
    name: "support_window_status",
    description:
      "Which month is collecting details, its period, when the window closes, and where each month is in the approval process.",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "review_flagged_entries",
    description: "Reviewer only: accept or reject flagged entries (same as the Accept / Reject buttons).",
    input_schema: {
      type: "object",
      properties: {
        decision: { type: "string", enum: ["accepted", "rejected"] },
        person_slack_id: str("Only this person's flagged entries. Empty = all."),
        cycle: str("YYYY-MM. Empty = the open window."),
      },
      required: ["decision"],
    },
  },
  {
    name: "close_window_now",
    description: "Reviewer or approver only: close a month's window now and move it on to review / approval.",
    input_schema: { type: "object", properties: { cycle: str("YYYY-MM. Empty = the open window.") } },
  },
  {
    name: "approve_support_allowance",
    description: "Approver only: final approval for a month (same as the Approve button). HR is tagged.",
    input_schema: { type: "object", properties: { cycle: str("YYYY-MM") }, required: ["cycle"] },
  },
  {
    name: "raise_concern_on_allowance",
    description: "Approver only: send the month back to the reviewer with a concern.",
    input_schema: {
      type: "object",
      properties: { cycle: str("YYYY-MM"), concern: str("The concern") },
      required: ["cycle", "concern"],
    },
  },
  {
    name: "respond_to_concern",
    description: "Reviewer only: answer the approver's concern and re-send the updated tables for approval.",
    input_schema: {
      type: "object",
      properties: { cycle: str("YYYY-MM"), response: str("The response") },
      required: ["cycle", "response"],
    },
  },
  {
    name: "reset_test_data",
    description:
      "TEST mode, reviewer only: archive all test data so the test can be run again from scratch (nothing is deleted).",
    input_schema: { type: "object", properties: {} },
  },
  {
    name: "compare_support_months",
    description:
      "Compare support allowance between months and show trends (totals, people, day/night/weekend/holiday shifts, extra " +
      "tasks, flags, per-person changes). Only specific people have access; anyone else gets no_access. When allowed, the tables " +
      "and your reply are shown only to the person who asked.",
    input_schema: {
      type: "object",
      properties: {
        later_month: str("YYYY-MM. Empty = the most recent month whose window has closed."),
        earlier_month: str("YYYY-MM to compare against. Empty = the month before."),
        trend_months: {
          type: "integer",
          description: "Also show a trend over this many months (3-12). 0 = just two months.",
        },
        person_slack_id: str("Only this person's numbers. Empty = whole team."),
      },
    },
  },
];

// deno-lint-ignore no-explicit-any
type Input = Record<string, any>;
const uid = (v: unknown) => String(v ?? "").trim().replace(/^<@|>$/g, "");
const json = (v: unknown) => JSON.stringify(v);
const err = (message: string) => json({ error: message });

async function attachPersonTable(eng: Engine, req: Request, personId: string, name: string, cid: string) {
  const entries = await eng.store.entries(cid, { personId });
  if (!entries.length) {
    return void req.attachments.push(`_${name} has no support details recorded for ${cycleLabel(cid)}._`);
  }
  req.attachments.push(
    `*Support details - ${name} - ${cycleLabel(cid)}* (${entries.length} entries)`,
    ...codeBlocks(submissionTable(entries)),
  );
}

function parseEntries(raw: Input[]): { clean: NewEntry[]; problems: string[] } {
  const clean: NewEntry[] = [], problems: string[] = [];
  for (const e of raw ?? []) {
    const d = parseIsoDate(String(e?.date ?? ""));
    const shift = e?.shift as Shift, extra = String(e?.extra_task ?? "").trim();
    if (!d) problems.push(`'${e?.date}' is not a valid date`);
    else if (!["day", "night", "none"].includes(shift)) problems.push(`${e.date}: shift must be day or night`);
    else if (shift === "none" && !extra) problems.push(`${e.date}: no shift and no extra task - nothing to record`);
    else clean.push({ date: isoDate(d.y, d.m, d.d), shift, extra_task: extra });
  }
  return { clean, problems };
}

async function latestFinishedCycle(eng: Engine): Promise<string> {
  const cycles = await eng.store.cyclesWithEntries();
  const finished: string[] = [];
  for (const c of cycles) if (((await eng.store.cycle(c))?.status ?? "open") !== "open") finished.push(c);
  return (finished.length ? finished : cycles).at(-1) ?? await eng.submissionCycle();
}

export async function runTool(eng: Engine, req: Request, name: string, input: Input): Promise<string> {
  const s = eng.s;
  switch (name) {
    case "expand_date_range": {
      const a = parseIsoDate(input.start), b = parseIsoDate(input.end);
      if (!a || !b) return err("dates must be YYYY-MM-DD");
      const out: { date: string; weekday: string }[] = [];
      for (let t = Date.UTC(a.y, a.m - 1, a.d); t <= Date.UTC(b.y, b.m - 1, b.d) && out.length < 367; t += 86_400_000) {
        const iso = new Date(t).toISOString().slice(0, 10), wd = new Date(t).getUTCDay();
        if (!(input.weekdays_only && (wd === 0 || wd === 6))) out.push({ date: iso, weekday: dayName(iso) });
      }
      return json({ count: out.length, dates: out });
    }

    case "submit_support_details": {
      const personId = uid(input.person_slack_id) || req.userId;
      const personName = personId === req.userId ? req.userName : await eng.userName(personId);
      const { clean, problems } = parseEntries(input.entries);
      if (input.cycle) { // reviewer adding to a closed month - same rules as the "Add entry" button
        const e = await eng.checkReviewerEdit(input.cycle, req.userId);
        if (e) return err(e);
        let added = 0;
        for (const it of clean) {
          const r = await eng.addEntryByReviewer(
            input.cycle,
            req.userId,
            personId,
            it.date,
            it.shift,
            it.extra_task ?? "",
          );
          r ? problems.push(`${it.date} ${it.shift}: ${r}`) : added++;
        }
        await attachPersonTable(eng, req, personId, personName, input.cycle);
        return json({ person: personName, added, problems, cycle: cycleLabel(input.cycle) });
      }
      let cid: string;
      if (s.outsideWindow === "reject") {
        const w = await eng.windowState();
        if (!w.open) {
          return json({
            window_closed: true,
            nothing_recorded: true,
            message:
              `The support details window is closed. The next window opens on ${
                formatLocal(s, w.nextOpens).split(",")[0]
              } ` +
              `for ${cycleLabel(w.nextCycle)} (support dates ${
                periodText(s, w.nextCycle)
              }). For anything urgent, contact <@${s.reviewer}>.`,
          });
        }
        cid = w.cycle;
      } else cid = await eng.submissionCycle();
      await eng.store.ensureCycle(cid);
      const added: Entry[] = [], duplicates: string[] = [];
      for (const it of clean) { // one at a time so overlaps within the same message are caught too
        const reason = await eng.entryFlags(cid, personId, it.date, it.shift);
        if (reason) Object.assign(it, { review: "pending", flag_reason: reason });
        const r = await eng.addEntries(cid, personId, personName, [it], req.userName, [req.channelId, req.threadTs]);
        added.push(...r.added);
        duplicates.push(...r.duplicates.map((d) => `${d.date} ${d.shift} (in ${cycleLabel(d.already_in)})`));
      }
      const flagged = added.filter((e) => e.review === "pending");
      const toReview = await eng.flagOverlapPartners(added);
      (toReview[cid] ??= []).unshift(...flagged.map((e) => e.id));
      for (const [c, ids] of Object.entries(toReview)) if (ids.length) await eng.notifyReviewer(c, ids);
      await attachPersonTable(eng, req, personId, personName, cid);
      const closes = slotAt(s, cid, s.schedule.close);
      return json({
        person: personName,
        added: added.length,
        flagged_for_reviewer: flagged.map((e) => `${e.support_date} (${e.flag_reason})`),
        reviewer: `<@${s.reviewer}>`,
        already_submitted: duplicates,
        problems,
        cycle: cycleLabel(cid),
        allocation_period: periodText(s, cid),
        window_closes: formatLocal(s, closes),
      });
    }

    case "remove_support_details": {
      const personId = uid(input.person_slack_id) || req.userId;
      const personName = personId === req.userId ? req.userName : await eng.userName(personId);
      const dates: string[] = input.dates ?? [];
      let cid: string, removed = 0;
      if (input.cycle || personId !== req.userId) {
        cid = input.cycle || await eng.submissionCycle();
        const e = await eng.checkReviewerEdit(cid, req.userId);
        if (e) return err(req.userId === s.reviewer ? e : "You can only remove your own support details.");
        for (
          const x of (await eng.store.entries(cid, { personId })).filter((x) =>
            dates.includes(x.support_date) && (!input.shift || x.shift === input.shift)
          )
        ) {
          if (!(await eng.setRowRemoved(x.id, req.userId, true))) removed++;
        }
      } else {
        cid = await eng.submissionCycle();
        removed = await eng.store.withdraw(cid, personId, dates, input.shift ?? "");
      }
      await attachPersonTable(eng, req, personId, personName, cid);
      return json({ person: personName, removed, cycle: cycleLabel(cid) });
    }

    case "show_support_details": {
      const cid = input.cycle || await eng.submissionCycle();
      const admin = eng.isAdmin(req.userId), pid = uid(input.person_slack_id);
      if (admin && !pid) {
        const status = (await eng.store.cycle(cid))?.status ?? "open";
        const pending = (await eng.store.pendingReviews(cid)).length;
        const moneyOk = [s.approvalChannel, s.hrChannel].includes(req.channelId);
        if (!moneyOk) {
          const everyone = await eng.store.entries(cid);
          req.attachments.push(
            `*Support details - ${cycleLabel(cid)}* (${periodText(s, cid)}) · ${
              new Set(everyone.map((e) => e.person_id)).size
            } people · ${everyone.length} entries`,
          );
          if (everyone.length) req.attachments.push(...codeBlocks(teamTable(everyone)));
          return json({
            cycle: cycleLabel(cid),
            status,
            entries: everyone.length,
            awaiting_review: pending,
            amounts_hidden: "Amounts are only shown in the approval channel.",
          });
        }
        const r = finalReport(await eng.store.entries(cid, { payableOnly: true }));
        req.attachments.push(
          `*Support allowance - ${cycleLabel(cid)}* (${
            periodText(s, cid)
          }) · ${r.people} people · total *${r.grandTotalText}*`,
          ...codeBlocks(r.summary),
          ...codeBlocks(r.detail),
        );
        return json({
          cycle: cycleLabel(cid),
          status,
          people: r.people,
          entries: r.entries,
          total: r.grandTotalText,
          awaiting_review: pending,
        });
      }
      if (pid && pid !== req.userId && !admin) return err("You can only view your own support details.");
      const personId = pid || req.userId;
      await attachPersonTable(
        eng,
        req,
        personId,
        personId === req.userId ? req.userName : await eng.userName(personId),
        cid,
      );
      return json({ cycle: cycleLabel(cid), shown_for: personId });
    }

    case "support_window_status": {
      const cid = await eng.submissionCycle(), now = await eng.now(), thisMonth = cycleIdFor(s, now);
      const months: Record<string, unknown> = {};
      for (const m of [...new Set([thisMonth, cid])].sort()) {
        months[cycleLabel(m)] = {
          status: (await eng.store.cycle(m))?.status ?? "open",
          awaiting_review: (await eng.store.pendingReviews(m)).length,
        };
      }
      const w = await eng.windowState(now);
      return json({
        window_open: w.open,
        cycle: cycleLabel(cid),
        allocation_period: periodText(s, cid),
        window_closes: formatLocal(s, slotAt(s, cid, s.schedule.close)),
        months,
        reviewer: `<@${s.reviewer}>`,
        approver: `<@${s.approver}>`,
      });
    }

    case "review_flagged_entries": {
      if (req.userId !== s.reviewer) return err("Only the reviewer can accept or reject flagged entries.");
      const cid = input.cycle || await eng.submissionCycle(), pid = uid(input.person_slack_id);
      const targets = (await eng.store.pendingReviews(cid)).filter((e) => !pid || e.person_id === pid);
      for (const e of targets) await eng.review(e.id, input.decision, req.userId);
      await eng.afterReviews(cid);
      return json({
        cycle: cycleLabel(cid),
        [input.decision]: targets.map((e) => `${e.person_name} ${e.support_date} ${e.shift}`),
        status: (await eng.store.cycle(cid))?.status ?? "open",
      });
    }

    case "close_window_now": {
      if (!eng.isAdmin(req.userId)) return err("Only the reviewer or approver can close the window early.");
      const cid = input.cycle || await eng.submissionCycle();
      return json({ cycle: cycleLabel(cid), status: await eng.closeCycle(cid) });
    }

    case "approve_support_allowance":
      return json({ cycle: cycleLabel(input.cycle), status: await eng.approve(input.cycle, req.userId) });

    case "raise_concern_on_allowance":
      return json({
        cycle: cycleLabel(input.cycle),
        status: await eng.raiseConcern(input.cycle, req.userId, input.concern),
      });

    case "respond_to_concern":
      return json({
        cycle: cycleLabel(input.cycle),
        status: await eng.respondToConcern(input.cycle, req.userId, input.response),
      });

    case "reset_test_data":
      return json({ result: await eng.resetTestData(req.userId) });

    case "compare_support_months": {
      if (!s.analyticsUsers.includes(req.userId)) {
        return json({
          no_access: true,
          message: "Sorry, you don't have access to support allowance comparisons and trends.",
        });
      }
      req.privateTo = req.userId; // everything below is shown only to them
      const pid = uid(input.person_slack_id) || undefined;
      const later = input.later_month || await latestFinishedCycle(eng),
        earlier = input.earlier_month || prevCycleId(later);
      const a = await analytics.cycleStats(eng.store, earlier, pid),
        b = await analytics.cycleStats(eng.store, later, pid);
      const cmp = analytics.compare(a, b);
      const who = pid ? ` - ${await eng.userName(pid)}` : "";
      req.attachments.push(
        `*Support allowance: ${a.label} vs ${b.label}${who}*\nPeriods: ${periodText(s, earlier)} vs ${
          periodText(s, later)
        }`,
        ...codeBlocks(cmp.summaryTable),
      );
      if (cmp.personTable && !pid) {
        req.attachments.push(`*Per person* (${cmp.columnsNote})`, ...codeBlocks(cmp.personTable));
      }
      let series: analytics.CycleStats[] = [];
      if ((input.trend_months ?? 0) >= 3) {
        const cids = [later];
        while (cids.length < Math.min(input.trend_months, 12)) cids.unshift(prevCycleId(cids[0]));
        series = await Promise.all(cids.map((c) => analytics.cycleStats(eng.store, c, pid)));
        req.attachments.push(`*Trend - last ${cids.length} months${who}*`, ...codeBlocks(analytics.trendTable(series)));
      }
      const slim = (st: analytics.CycleStats) => ({
        ...st,
        by_person: undefined,
        holidays_in_period: eng.holidaysIn(st.cycle),
      });
      const notes: string[] = [];
      if (["open", "reviewing"].includes(b.status)) {
        notes.push(`${b.label} is still ${b.status} - its numbers may change.`);
      }
      if (b.flags.pending) {
        notes.push(`${b.flags.pending} entries in ${b.label} are still awaiting review and are not counted.`);
      }
      return json({
        earlier: slim(a),
        later: slim(b),
        biggest_person_changes: cmp.biggestChanges,
        trend: series.map(slim),
        delivered_privately: true,
        notes,
      });
    }
  }
  return err(`unknown tool ${name}`);
}

// -- Claude loop ---------------------------------------------------------------------------------

type Content = { type: string; [k: string]: unknown };

export async function runAgent(
  eng: Engine,
  req: Request,
  conversation: string,
  env: Record<string, string>,
  budgetMs = 50_000,
): Promise<string> {
  const started = Date.now();
  const today = await eng.today();
  const messages: { role: string; content: string | Content[] }[] = [{
    role: "user",
    content: `Today is ${today} (${dayName(today)}). Request from ${req.userName} (${req.userId}).\n\n${conversation}`,
  }];
  for (let turn = 0; turn < 6; turn++) {
    const left = budgetMs - (Date.now() - started);
    if (left < 5_000) return "Sorry, that took too long - please ask again (or break it into smaller requests).";
    const res = await callClaude(env, messages, left);
    if (res.stop_reason === "refusal") return "Sorry, I can't help with that request.";
    messages.push({ role: "assistant", content: res.content });
    const uses = res.content.filter((c: Content) => c.type === "tool_use");
    if (res.stop_reason !== "tool_use" || !uses.length) {
      const text = res.content.filter((c: Content) => c.type === "text").map((c: Content) => c.text).join("\n").trim();
      return (text || "Done.") +
        (res.stop_reason === "max_tokens" ? "\n\n_(reply was cut off - ask me to continue)_" : "");
    }
    const results: Content[] = [];
    for (const u of uses) {
      let content: string, isError = false;
      try {
        content = await runTool(eng, req, u.name as string, (u.input ?? {}) as Input);
      } catch (e) {
        content = `Tool failed: ${e instanceof Error ? e.message : e}`;
        isError = true;
      }
      results.push({ type: "tool_result", tool_use_id: u.id, content, ...(isError ? { is_error: true } : {}) });
    }
    messages.push({ role: "user", content: results });
  }
  return "Sorry, I couldn't finish that - please try again.";
}

async function callClaude(env: Record<string, string>, messages: unknown[], timeoutMs: number) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const r = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      signal: ctrl.signal,
      headers: {
        "content-type": "application/json",
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2026-10-21",
        "anthropic-beta": "server-side-fallback-2026-07-01",
      },
      body: JSON.stringify({
        model: env.AGENT_MODEL || "claude-opus-5-5",
        max_tokens: 8000,
        system: [{ type: "text", text: SYSTEM_PROMPT, cache_control: { type: "ephemeral" } }],
        tools: TOOLS,
        messages,
        // Low effort keeps replies fast enough for Slack's 60-second function limit.
        output_config: { effort: env.AGENT_EFFORT || "low" },
        fallbacks: "default",
      }),
    });
    const body = await r.json();
    if (!r.ok) throw new Error(`Claude API ${r.status}: ${body?.error?.message ?? JSON.stringify(body)}`);
    return body;
  } finally {
    clearTimeout(timer);
  }
}
