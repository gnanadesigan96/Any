import { assert, assertEquals, assertStringIncludes } from "jsr:@std/assert@1";
import { problems, PRODUCTION, type Settings, TEST } from "../config/settings.ts";
import { type Request, runTool } from "../lib/agent.ts";
import * as B from "../lib/blocks.ts";
import { Engine } from "../lib/engine.ts";
import { withHandlers } from "../lib/handlers.ts";
import { amount } from "../lib/policy.ts";
import { MemoryTables, Store } from "../lib/store.ts";
import { localInstant, period } from "../lib/time.ts";

const ME = "UGNANA00", BOSS = "UBOSS000", PRIYA = "UPRIYA00", ARUN = "UARUN000", UDAY = "UUDAY000";
const NAMES: Record<string, string> = {
  [ME]: "Gnanadesigan",
  [BOSS]: "Poornodhaya",
  [PRIYA]: "Priya Kumar",
  [ARUN]: "Arun",
  [UDAY]: "Uday",
};

const S: Settings = {
  ...PRODUCTION,
  collectionChannel: "CSUPPORT1",
  reviewChannel: null,
  approvalChannel: "CAPPROVE1",
  hrChannel: null,
  reviewer: ME,
  approver: BOSS,
  hrGroup: "SHRGROUP1",
  hrUsers: [],
  analyticsUsers: [UDAY],
};

// deno-lint-ignore no-explicit-any
type Any = any;

class FakeSlack {
  posts: Any[] = [];
  updates: Any[] = [];
  ephemeral: Any[] = [];
  opened: Any[] = [];
  completed: string[] = [];
  chat = {
    postMessage: (a: Any) => {
      this.posts.push(a);
      return Promise.resolve({ ok: true, channel: a.channel, ts: `${this.posts.length}.000` });
    },
    update: (a: Any) => (this.updates.push(a), Promise.resolve({ ok: true })),
    postEphemeral: (a: Any) => (this.ephemeral.push(a), Promise.resolve({ ok: true })),
  };
  users = { info: ({ user }: Any) => Promise.resolve({ ok: true, user: { real_name: NAMES[user] ?? user } }) };
  views = { open: (a: Any) => (this.opened.push(a.view), Promise.resolve({ ok: true })) };
  functions = {
    completeSuccess: (a: Any) => (this.completed.push(a.function_execution_id), Promise.resolve({ ok: true })),
  };
  texts = (channel?: string) =>
    this.posts.filter((p) => !channel || p.channel === channel).map((p) => p.text as string);
  withBlocks = (channel?: string) => this.posts.filter((p) => p.blocks && (!channel || p.channel === channel));
}

const ist = (y: number, m: number, d: number, hh = 0, mm = 0) => localInstant(S, y, m, d, hh, mm);

const fastStore = (tables: MemoryTables) => Object.assign(new Store(tables), { lockSettleMs: 0 });
const approvalPosts = (slack: FakeSlack) =>
  slack.withBlocks("CAPPROVE1").filter((p) => JSON.stringify(p.blocks).includes(B.A.approve));

function setup(settings: Settings = S, exec = "Fx_main") {
  const slack = new FakeSlack(), tables = new MemoryTables(), clock = { now: ist(2026, 10, 18, 12) };
  const make = (execId = exec) => new Engine(slack, fastStore(tables), settings, execId, () => clock.now);
  return { slack, clock, eng: make(), make };
}

async function asUser(eng: Engine, user: string, tool: string, input: Any, channel = "CSUPPORT1") {
  const req: Request = {
    userId: user,
    userName: NAMES[user] ?? user,
    channelId: channel,
    threadTs: `t-${user}`,
    attachments: [],
    privateTo: "",
  };
  return { out: JSON.parse(await runTool(eng, req, tool, input)), req };
}

// -- rates & periods ----------------------------------------------------------------------

Deno.test("rates", () => {
  const cases: [string, "day" | "night" | "none", boolean, number, string][] = [
    ["2026-10-01", "day", false, 500, "weekday"],
    ["2026-10-03", "day", false, 1000, "weekend"],
    ["2026-10-02", "day", false, 1000, "holiday"],
    ["2026-10-01", "night", false, 1000, "weekday"],
    ["2026-10-03", "night", false, 500, "weekend"],
    ["2026-08-15", "day", false, 1000, "weekend"],
    ["2026-10-01", "day", true, 1000, "weekday"],
    ["2026-10-01", "none", true, 500, "weekday"],
  ];
  for (const [d, s, x, total, t] of cases) {
    const a = amount(d, s, x);
    assertEquals([a.total, a.dayType], [total, t], `${d} ${s}`);
  }
});

Deno.test("period is 21st to 20th and the window rolls over after 19th EOD", async () => {
  assertEquals(period(S, "2026-10"), { first: "2026-09-21", last: "2026-10-20" });
  assertEquals(period(S, "2026-01"), { first: "2025-12-21", last: "2026-01-20" });
  const { eng } = setup();
  assertEquals(await eng.submissionCycle(ist(2026, 10, 19, 23, 59)), "2026-10");
  assertEquals(await eng.submissionCycle(ist(2026, 10, 20, 0, 0)), "2026-11");
  assert(eng.flagReason("2026-10", "2026-09-20").startsWith("before"));
  assertEquals(eng.flagReason("2026-10", "2026-10-20"), "");
  assert(eng.flagReason("2026-10", "2026-10-21").startsWith("after"));
});

Deno.test("configs: test is complete, production placeholders are reported", () => {
  assertEquals(problems(TEST), []);
  assert(problems(PRODUCTION).some((p) => p.startsWith("approver")));
});

// -- the whole month -------------------------------------------------------------------------

Deno.test("full month: flags, review, approval, concern fixed in the table, HR, nudges", async () => {
  const { slack, clock, eng, make } = setup();
  clock.now = ist(2026, 10, 17, 10, 0);
  await eng.tick();
  assertStringIncludes(slack.posts[0].text, "21 Sep 2026 - 20 Oct 2026");

  clock.now = ist(2026, 10, 18, 12);
  let r = await asUser(eng, PRIYA, "submit_support_details", {
    entries: [
      { date: "2026-10-03", shift: "night" },
      { date: "2026-10-02", shift: "day", extra_task: "Patched prod cluster" },
      { date: "2026-09-15", shift: "night" },
      { date: "2026-10-20", shift: "day" },
    ],
  });
  assertEquals(r.out.added, 4);
  assertEquals(r.out.flagged_for_reviewer.length, 1);
  const table = r.req.attachments.join("\n");
  assertStringIncludes(table, "Awaiting review");
  assert(!table.includes("₹"));
  // Flagged entries go to the approval channel by default (the team channel is visible to everyone).
  const reviewMsg = slack.withBlocks("CAPPROVE1").at(-1);
  assert(!slack.withBlocks("CSUPPORT1").length);
  const flaggedId = B.rowIds(reviewMsg.blocks)[0];

  // Overlap: Arun claims Priya's night shift -> both flagged.
  r = await asUser(eng, ARUN, "submit_support_details", {
    entries: [{ date: "2026-10-03", shift: "night" }, { date: "2026-10-05", shift: "day" }],
  });
  assertEquals(r.out.flagged_for_reviewer, ["2026-10-03 (overlaps with another person's night shift)"]);
  assertEquals((await eng.store.pendingReviews("2026-10")).length, 3);

  // Window closes; flags still open -> final table waits.
  clock.now = ist(2026, 10, 20, 0, 0);
  await eng.tick();
  assertEquals((await eng.store.cycle("2026-10"))!.status, "reviewing");
  assertEquals(approvalPosts(slack).length, 0);

  // After the window: "window is closed".
  r = await asUser(eng, ARUN, "submit_support_details", { entries: [{ date: "2026-10-10", shift: "day" }] });
  assert(r.out.window_closed);
  assertStringIncludes(r.out.message, "17 November");

  // Reviewer decides (only the reviewer may); last decision releases the final table.
  assertEquals(await eng.review(flaggedId, "accepted", PRIYA), "not_authorised");
  const arunNight = (await eng.store.entries("2026-10", { personId: ARUN })).find((e) => e.shift === "night")!;
  const priyaNight = (await eng.store.entries("2026-10", { personId: PRIYA })).find((e) =>
    e.support_date === "2026-10-03"
  )!;
  for (const [id, d] of [[flaggedId, "accepted"], [priyaNight.id, "accepted"], [arunNight.id, "rejected"]] as const) {
    assertEquals(await eng.review(id, d, ME), d);
  }
  await eng.afterReviews("2026-10");
  const approval = slack.withBlocks("CAPPROVE1").at(-1);
  assertStringIncludes(approval.text, `<@${BOSS}>`);
  // Priya: night Sat 500 + day holiday 1000 + extra 500 + 15 Sep night (Tue) 1000 + 20 Oct day 500; Arun: 5 Oct day 500
  assertStringIncludes(approval.text, "total *₹4,000*");

  // Nudge after 2 hours (production settings), at most 3, not in quiet hours.
  clock.now = ist(2026, 10, 20, 9, 30); // posted at 00:00; 21:00-09:00 is quiet, so the first nudge comes now
  await eng.tick();
  const nudges = () => slack.posts.filter((p) => String(p.text).includes(":alarm_clock:"));
  assertEquals(nudges().length, 1);
  assertStringIncludes(nudges()[0].text, `<@${BOSS}>`);

  // Concern -> interactive table for the reviewer in the thread.
  const arunDay = (await eng.store.entries("2026-10", { personId: ARUN }))[0];
  assertEquals(await eng.raiseConcern("2026-10", ME, "?"), "not_authorised");
  assertEquals(await eng.raiseConcern("2026-10", BOSS, "Arun was on leave on 5 Oct", [arunDay.id]), "concern");
  const concern = slack.posts.at(-1);
  assert(concern.reply_broadcast);
  assertEquals(B.rowIds(concern.blocks), [arunDay.id]);
  assertEquals(await eng.editEntry(arunDay.id, ME, "2026-10-06", "night", ""), "");
  assertStringIncludes(JSON.stringify(slack.updates.at(-1).blocks), "Tue 06 Oct 2026 · Night");
  assertStringIncludes(
    await eng.addEntryByReviewer("2026-10", ME, PRIYA, "2026-10-03", "night", ""),
    "Already claimed",
  );
  assertEquals(await eng.addEntryByReviewer("2026-10", ME, ARUN, "2026-10-07", "day", "Cert rotation"), "");
  assertEquals(await eng.respondToConcern("2026-10", ME, "Corrected Arun's dates"), "pending_approval");
  assertStringIncludes(JSON.stringify(slack.withBlocks("CAPPROVE1").at(-1).blocks), "Corrected Arun's dates");

  // Approved from a different execution (e.g. chat): HR tagged once, owner execution completed.
  const other = make("Fx_chat");
  assertEquals(await other.approve("2026-10", ME), "not_authorised");
  assertEquals(await other.approve("2026-10", BOSS), "approved");
  assertEquals(await other.approve("2026-10", BOSS), "approved");
  const hr = slack.texts("CAPPROVE1").filter((t) => t.includes("<!subteam^SHRGROUP1>"));
  assertEquals(hr.length, 1);
  assertStringIncludes(hr[0], "21 Sep 2026 - 20 Oct 2026");
  assertEquals(await eng.store.liveMessages({ cycle_id: "2026-10" }), []);
  assert(slack.completed.includes("Fx_main"));
  assertStringIncludes(await eng.addEntryByReviewer("2026-10", ME, ARUN, "2026-10-08", "day", ""), "approved");
});

Deno.test("members see only their own details and no money; amounts only in the approval channel", async () => {
  const { eng } = setup();
  await asUser(eng, ARUN, "submit_support_details", { entries: [{ date: "2026-10-05", shift: "day" }] });
  // Asking for someone else's details just shows your own.
  const mine = await asUser(eng, PRIYA, "show_support_details", { person_slack_id: ARUN });
  assert(!mine.req.attachments.join().includes("Arun") && !mine.req.privateTo);
  let r = await asUser(eng, BOSS, "show_support_details", {}, "CAPPROVE1");
  assertEquals(r.out.total, "₹500");
  // Everyone's details outside the approval channel: only visible to the admin, no money.
  r = await asUser(eng, BOSS, "show_support_details", {});
  assert(r.out.amounts_hidden && !r.req.attachments.join().includes("₹") && r.req.privateTo === BOSS);
  assert((await asUser(eng, PRIYA, "request_admin_action", { action: "close_window" })).out.error);
});

Deno.test("comparisons: only analytics users, shown privately", async () => {
  const { eng, clock } = setup();
  clock.now = ist(2026, 9, 18, 12);
  await asUser(eng, PRIYA, "submit_support_details", {
    entries: [{ date: "2026-09-05", shift: "night" }, { date: "2026-09-08", shift: "day" }],
  });
  await eng.closeCycle("2026-09");
  await eng.approve("2026-09", BOSS);
  clock.now = ist(2026, 10, 18, 12);
  await asUser(eng, PRIYA, "submit_support_details", {
    entries: [{ date: "2026-10-02", shift: "day", extra_task: "Prod patch" }],
  });
  await eng.closeCycle("2026-10");

  for (const who of [BOSS, ME, PRIYA]) {
    const r = await asUser(eng, who, "compare_support_months", {}, "CAPPROVE1");
    assert(r.out.no_access && r.req.attachments.length === 0 && !r.req.privateTo, who);
  }
  const r = await asUser(eng, UDAY, "compare_support_months", { trend_months: 3 }, "CAPPROVE1");
  assertEquals(r.req.privateTo, UDAY);
  assertEquals([r.out.earlier.total, r.out.later.total], [1000, 1500]);
  const text = r.req.attachments.join("\n");
  assertStringIncludes(text, "₹1,000 → ₹1,500");
  assertStringIncludes(text, "Trend - last 3 months");
});

Deno.test("extra tasks and different shifts may overlap", async () => {
  const { eng } = setup();
  await asUser(eng, PRIYA, "submit_support_details", { entries: [{ date: "2026-10-03", shift: "night" }] });
  const r = await asUser(eng, ARUN, "submit_support_details", {
    entries: [{ date: "2026-10-03", shift: "day" }, { date: "2026-10-04", shift: "none", extra_task: "Night call" }],
  });
  await asUser(eng, PRIYA, "submit_support_details", {
    entries: [{ date: "2026-10-04", shift: "none", extra_task: "Same call" }],
  });
  assertEquals(r.out.flagged_for_reviewer, []);
  assertEquals(await eng.store.pendingReviews("2026-10"), []);
});

Deno.test("test mode: pretend clock set by the test triggers, nudges every 10 minutes", async () => {
  const slack = new FakeSlack(), tables = new MemoryTables();
  let real = new Date("2026-10-29T09:00:00Z");
  const eng = new Engine(slack, new Store(tables), TEST, "Fx_tick", () => real);
  await eng.setPretendNow("2026-10-17T10:00");
  await eng.tick();
  assertStringIncludes(slack.posts[0].text, "[TEST]");
  real = new Date(real.getTime() + 20 * 60_000);
  assertEquals((await eng.windowState()).open, true);
  await eng.setPretendNow("2026-10-20T00:00");
  assertEquals((await eng.windowState()).open, false);
});

// -- buttons & forms ---------------------------------------------------------------------------

Deno.test("button and form handlers", async () => {
  const handlers: Record<string, Any> = {};
  const fakeFn = {
    addBlockActionsHandler(ids: string | string[], h: Any) {
      for (const id of [ids].flat()) handlers[id] = h;
      return this;
    },
    addViewSubmissionHandler(id: string, h: Any) {
      handlers[id] = h;
      return this;
    },
  };
  withHandlers(fakeFn);
  // The handlers build their own Store on Slack datastores; give them an in-memory stand-in.
  const tables = new MemoryTables();
  const slack = new FakeSlack();
  // Each request builds its own Store in production; do the same here so no cache goes stale.
  const store = {
    entry: (id: string) => new Store(tables).entry(id),
    cycle: (c: string) => new Store(tables).cycle(c),
  };
  // deno-lint-ignore no-explicit-any
  (slack as any).apps = {
    datastore: {
      get: async ({ datastore, id }: Any) => ({ ok: true, item: (await tables.get(tableOf(datastore), id)) ?? {} }),
      put: async ({ datastore, item }: Any) => (await tables.put(tableOf(datastore), item), { ok: true }),
      query: async ({ datastore }: Any) => ({ ok: true, items: await tables.all(tableOf(datastore)) }),
    },
  };
  const env = { APP_MODE: "" };
  const freshEng = () => new Engine(slack, new Store(tables), S, "Fx_main", () => ist(2026, 10, 18, 12));
  const eng = freshEng();
  // Handlers use settingsFor(env) = PRODUCTION placeholders; patch the IDs for this test (restored below).
  const saved = structuredClone(PRODUCTION);
  Object.assign(PRODUCTION, {
    collectionChannel: "CSUPPORT1",
    approvalChannel: "CAPPROVE1",
    reviewer: ME,
    approver: BOSS,
    hrGroup: "SHRGROUP1",
    hrUsers: [],
    analyticsUsers: [UDAY],
  });

  await asUser(eng, PRIYA, "submit_support_details", {
    entries: [{ date: "2026-09-01", shift: "night" }, { date: "2026-10-01", shift: "day" }],
  });
  const msg = slack.withBlocks("CAPPROVE1").at(-1);
  const flaggedId = B.rowIds(msg.blocks)[0];
  const body = (user: string) => ({
    user: { id: user },
    channel: { id: msg.channel },
    function_data: { execution_id: "Fx_main" },
    interactivity: { interactivity_pointer: "ptr" },
    message: { ts: "1.000", blocks: msg.blocks },
  });

  await handlers[B.A.reviewAccept]({
    action: { action_id: B.A.reviewAccept, value: flaggedId },
    body: body(PRIYA),
    client: slack,
    env,
  });
  assertStringIncludes(slack.ephemeral.at(-1).text, "Only");
  assertEquals((await store.entry(flaggedId))!.review, "pending");
  await handlers[B.A.reviewAccept]({
    action: { action_id: B.A.reviewAccept, value: flaggedId },
    body: body(ME),
    client: slack,
    env,
  });
  assertEquals((await store.entry(flaggedId))!.review, "accepted");
  assert(!JSON.stringify(slack.updates.at(-1).blocks).includes(B.A.reviewAccept));

  await freshEng().closeCycle("2026-10");
  await handlers[B.A.raiseConcern]({ action: { value: "2026-10" }, body: body(PRIYA), client: slack, env });
  assertEquals(slack.opened.length, 0);
  await handlers[B.A.raiseConcern]({ action: { value: "2026-10" }, body: body(BOSS), client: slack, env });
  assertEquals(slack.opened.at(-1).callback_id, B.V.concern);
  await handlers[B.V.concern]({
    view: {
      private_metadata: JSON.stringify({ cid: "2026-10" }),
      state: { values: { entries: { v: { selected_options: [] } }, concern: { v: { value: "Why Sep 1?" } } } },
    },
    body: body(BOSS),
    client: slack,
    env,
  });
  assertEquals((await store.cycle("2026-10"))!.status, "concern");

  const editResult = await handlers[B.V.edit]({
    view: {
      private_metadata: JSON.stringify({ id: flaggedId }),
      state: {
        values: {
          date: { v: { selected_date: "2026-10-01" } },
          shift: { v: { selected_option: { value: "day" } } },
          extra: { v: { value: null } },
        },
      },
    },
    body: body(ME),
    client: slack,
    env,
  });
  assertEquals(editResult.response_action, "errors");

  await handlers[B.A.concernRow]({
    action: { selected_option: { value: `remove:${flaggedId}` } },
    body: body(ME),
    client: slack,
    env,
  });
  assertEquals((await store.entry(flaggedId))!.review, "removed");
  await handlers[B.V.respond]({
    view: {
      private_metadata: JSON.stringify({ cid: "2026-10" }),
      state: { values: { response: { v: { value: "Removed it" } } } },
    },
    body: body(ME),
    client: slack,
    env,
  });
  assertStringIncludes(slack.withBlocks("CAPPROVE1").at(-1).text, "total *₹500*");
  await handlers[B.A.approve]({ action: { value: "2026-10" }, body: body(BOSS), client: slack, env });
  assertEquals((await store.cycle("2026-10"))!.status, "approved");
  assert(slack.completed.includes("Fx_main"));
  Object.assign(PRODUCTION, saved);
});

function tableOf(datastore: string): string {
  return {
    support_cycles: "cycles",
    support_entries: "entries",
    support_live_messages: "live_messages",
    support_meta: "meta",
  }[datastore]!;
}

Deno.test("guard: only the expected scopes and no destructive Slack calls", async () => {
  const manifest = await Deno.readTextFile(new URL("../manifest.ts", import.meta.url));
  const scopes = [...manifest.matchAll(/"([a-z_.]+:[a-z_.]+)"/g)].map((m) => m[1]).sort();
  assertEquals(scopes, [
    "app_mentions:read",
    "channels:history",
    "chat:write",
    "datastore:read",
    "datastore:write",
    "groups:history",
    "users:read",
  ]);
  for await (const dir of ["lib", "functions"]) {
    for await (const f of Deno.readDir(new URL(`../${dir}/`, import.meta.url))) {
      const src = await Deno.readTextFile(new URL(`../${dir}/${f.name}`, import.meta.url));
      const calls = [...src.matchAll(/client\.([a-z]+)\.([A-Za-z.]+)\(/g)].map((m) => `${m[1]}.${m[2]}`);
      for (const c of calls) {
        assert(!/delete|remove|archive|kick|leave|rename|invite|join|set/i.test(c), `${f.name}: ${c}`);
      }
    }
  }
});

Deno.test("agent loop: tool call round-trip, request shape, reply text", async () => {
  const { runAgent } = await import("../lib/agent.ts");
  const { eng } = setup();
  const sent: Any[] = [];
  const responses = [
    {
      stop_reason: "tool_use",
      content: [{ type: "thinking", thinking: "", signature: "x" }, {
        type: "tool_use",
        id: "tu1",
        name: "submit_support_details",
        input: { entries: [{ date: "2026-10-05", shift: "day" }] },
      }],
    },
    { stop_reason: "end_turn", content: [{ type: "text", text: "Recorded your day shift on 5 Oct." }] },
  ];
  const realFetch = globalThis.fetch;
  globalThis.fetch = ((_url: string, init: Any) => {
    sent.push(JSON.parse(init.body));
    sent.at(-1).headers = init.headers;
    return Promise.resolve(new Response(JSON.stringify(responses.shift()), { status: 200 }));
  }) as typeof fetch;
  try {
    const req: Request = {
      userId: PRIYA,
      userName: "Priya Kumar",
      channelId: "CSUPPORT1",
      threadTs: "t1",
      attachments: [],
      privateTo: "",
    };
    const reply = await runAgent(eng, req, "day shift 5 Oct", { ANTHROPIC_API_KEY: "k" });
    assertEquals(reply, "Recorded your day shift on 5 Oct.");
    assertEquals(sent.length, 2);
    assertEquals(sent[0].model, "claude-opus-5-5");
    assertEquals(sent[0].headers["anthropic-version"], "2026-10-21");
    assertEquals(sent[0].output_config.effort, "low");
    // Second request carries the assistant turn unchanged (incl. thinking) plus the tool result.
    assertEquals(sent[1].messages[1].content[0].type, "thinking");
    assertEquals(sent[1].messages[2].content[0].type, "tool_result");
    assertStringIncludes(sent[1].messages[2].content[0].content, '"added":1');
    assert(req.attachments.join("\n").includes("05 Oct 2026"));
  } finally {
    globalThis.fetch = realFetch;
  }
});

Deno.test("reset test data archives everything (test mode, reviewer only)", async () => {
  const slack = new FakeSlack(), tables = new MemoryTables();
  const real = new Date("2026-10-29T09:00:00Z");
  const mk = () => new Engine(slack, new Store(tables), TEST, "Fx_t", () => real);
  await mk().setPretendNow("2026-10-17T10:30");
  await asUser(mk(), "U0CAAAAA1", "submit_support_details", { entries: [{ date: "2026-09-01", shift: "day" }] });
  assertEquals((await mk().store.entries("2026-10")).length, 1);
  assertStringIncludes(await mk().resetTestData("U0CAAAAA1"), "Only the reviewer");
  assertStringIncludes(await mk().resetTestData(TEST.reviewer), "Archived 1 entries");
  assertEquals((await mk().store.entries("2026-10")).length, 0);
  assertEquals((await mk().store.liveMessages()).length, 0);
  assertEquals(await mk().store.duplicateOf("U0CAAAAA1", "2026-09-01", "day"), null);
  assertStringIncludes(
    await new Engine(slack, new Store(tables), S, "Fx", () => real).resetTestData(ME),
    "only available in test mode",
  );
});

// -- security ------------------------------------------------------------------------------------

Deno.test("security: nobody can submit for someone else (the parameter is ignored)", async () => {
  const { eng } = setup();
  const r = await asUser(eng, PRIYA, "submit_support_details", {
    entries: [{ date: "2026-10-05", shift: "day" }],
    person_slack_id: ARUN,
  });
  assertEquals(r.out.added, 1);
  assertEquals((await eng.store.entries("2026-10", { personId: ARUN })).length, 0);
  assertEquals((await eng.store.entries("2026-10", { personId: PRIYA }))[0].submitted_by, PRIYA); // audit uses IDs
});

Deno.test("security: chat cannot run admin actions - they need the role holder's Confirm click", async () => {
  const { eng, slack } = setup();
  await asUser(eng, PRIYA, "submit_support_details", { entries: [{ date: "2026-10-05", shift: "day" }] });
  // No chat tool exists any more for approving / reviewing / raising concerns.
  for (
    const tool of [
      "approve_support_allowance",
      "review_flagged_entries",
      "raise_concern_on_allowance",
      "respond_to_concern",
      "close_window_now",
      "reset_test_data",
    ]
  ) {
    assert((await asUser(eng, ME, tool, { cycle: "2026-10" })).out.error, tool);
  }
  const r = await asUser(eng, ME, "request_admin_action", { action: "close_window" });
  assert(r.out.confirmation_posted);
  assertEquals((await eng.store.cycle("2026-10"))!.status, "open"); // nothing happened yet
  const confirm = slack.posts.at(-1);
  const value = JSON.parse(confirm.blocks[1].elements[0].value);
  assertEquals(await eng.confirmed(value, PRIYA, true, confirm.channel, "x"), "not_authorised");
  assertEquals(await eng.confirmed(value, BOSS, true, confirm.channel, "x"), "not_authorised"); // only the asker
  assertStringIncludes(await eng.confirmed(value, ME, true, confirm.channel, "1.000"), "pending_approval");
  assert((await asUser(eng, ME, "request_admin_action", { action: "reset_test_data" })).out.error); // production mode
});

Deno.test("security: user text can't ping or hide links (escaping) and the AI reply is sanitised", async () => {
  const { sanitizeModelText } = await import("../lib/safe.ts");
  const { eng, slack } = setup();
  await asUser(eng, PRIYA, "submit_support_details", {
    entries: [{
      date: "2026-09-10",
      shift: "night",
      extra_task: "<!channel> <https://evil.example|Approve here> " + "x".repeat(500),
    }],
  });
  const review = JSON.stringify(slack.withBlocks("CAPPROVE1").at(-1).blocks);
  assert(!review.includes("<!channel>") && !review.includes("<https://evil"));
  assertStringIncludes(review, "&lt;!channel&gt;");
  const stored = (await eng.store.entries("2026-10", { personId: PRIYA }))[0];
  assert(stored.extra_task.length <= 200);
  const out = sanitizeModelText("Hi <!here> <!subteam^S123|hr> see <https://evil.example|Approve here> <@U0123ABC>");
  assertEquals(out, "Hi @here @group see Approve here (https://evil.example) <@U0123ABC>");
});

Deno.test("security: junk input is refused (far-off dates, too many entries, bad month ids)", async () => {
  const { eng } = setup();
  const many = Array.from(
    { length: 80 },
    (_, i) => ({ date: `2026-10-${String((i % 20) + 1).padStart(2, "0")}`, shift: i < 20 ? "day" : "night" }),
  );
  let r = await asUser(eng, PRIYA, "submit_support_details", { entries: many });
  assert(r.out.added <= 62 && r.out.problems.some((p: string) => p.includes("only the first 62")));
  r = await asUser(eng, ARUN, "submit_support_details", {
    entries: [{ date: "1999-01-01", shift: "day" }, { date: "2027-06-01", shift: "day" }],
  });
  assertEquals(r.out.added, 0);
  assert(r.out.problems.every((p: string) => p.includes("too far outside")));
  r = await asUser(eng, BOSS, "show_support_details", { cycle: "<!channel>" }, "CAPPROVE1");
  assertEquals(r.out.cycle, "October 2026"); // invalid month id ignored, no junk cycle created
  assertEquals(await eng.store.cycle("<!channel>"), null);
});

Deno.test("security: a double click on Approve notifies HR only once", async () => {
  const { slack, clock } = setup();
  const tables = new MemoryTables();
  const mk = (ex: string) =>
    new Engine(slack, Object.assign(new Store(tables), { lockSettleMs: 30 }), S, ex, () => clock.now);
  await asUser(mk("Fx_a"), PRIYA, "submit_support_details", { entries: [{ date: "2026-10-05", shift: "day" }] });
  await mk("Fx_a").closeCycle("2026-10");
  const results = await Promise.all([mk("Fx_1").approve("2026-10", BOSS), mk("Fx_2").approve("2026-10", BOSS)]);
  assertEquals(results.filter((x) => x === "approved").length, 1);
  assertEquals(slack.texts("CAPPROVE1").filter((t) => t.includes("<!subteam^SHRGROUP1>")).length, 1);
});

Deno.test("security: per-person rate limit, audit trail, test-mode guard", async () => {
  const tables = new MemoryTables(), store = fastStore(tables);
  for (let i = 0; i < 8; i++) assert(await store.allowHit("mention:U1", 8, 600_000, 1000 + i));
  assertEquals(await store.allowHit("mention:U1", 8, 600_000, 2000), false);
  assert(await store.allowHit("mention:U1", 8, 600_000, 1000 + 600_001)); // window slides
  assert(await store.allowHit("mention:U2", 8, 600_000, 2000)); // per person

  const { eng } = setup();
  await asUser(eng, PRIYA, "submit_support_details", { entries: [{ date: "2026-09-01", shift: "day" }] });
  await eng.review((await eng.store.pendingReviews("2026-10"))[0].id, "rejected", ME);
  const log = await eng.store.auditLog();
  assertEquals(log.map((a) => [a.actor, a.action]), [[PRIYA, "submit"], [ME, "review_rejected"]]);

  assertEquals(problems({ ...TEST, approvalChannel: "C0PROD0001" }).length, 0);
  const prodLike = { ...TEST, collectionChannel: PRODUCTION.approvalChannel };
  assert(problems(prodLike).some((p) => p.includes("production") || p.includes("needs a channel ID")));
});

Deno.test("security: no names in what is sent to the AI for comparisons", async () => {
  const { eng, clock } = setup();
  clock.now = ist(2026, 10, 18, 12);
  await asUser(eng, PRIYA, "submit_support_details", { entries: [{ date: "2026-10-02", shift: "day" }] });
  await eng.closeCycle("2026-10");
  const r = await asUser(eng, UDAY, "compare_support_months", {}, "CAPPROVE1");
  const sentToAi = JSON.stringify(r.out);
  assert(!sentToAi.includes("Priya"), sentToAi);
  assert(r.req.attachments.join().includes("Priya")); // tables (posted to Slack directly) keep names
});
