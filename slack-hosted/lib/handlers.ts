/**
 * Button / menu / form handlers. Slack routes a click to the function execution that posted the
 * message, so both functions (mention handler and scheduler) get the same handlers attached.
 */

import { settingsFor } from "../config/settings.ts";
import * as B from "./blocks.ts";
import { Engine } from "./engine.ts";
import type { Shift } from "./policy.ts";
import { DatastoreTables, Store } from "./store.ts";

// deno-lint-ignore no-explicit-any
type Any = any;

function engineFor(client: Any, env: Record<string, string>, body: Any) {
  return new Engine(client, new Store(new DatastoreTables(client)), settingsFor(env), body.function_data.execution_id);
}

async function finish(eng: Engine) {
  // Complete this execution once none of its messages need clicks any more.
  if (await eng.completeIfIdle(eng.executionId)) {
    await eng.client.functions.completeSuccess({ function_execution_id: eng.executionId, outputs: {} });
  }
}

async function ephemeral(client: Any, body: Any, text: string) {
  const channel = body.channel?.id ?? body.container?.channel_id;
  if (channel) await client.chat.postEphemeral({ channel, user: body.user.id, text });
}

const openModal = (client: Any, body: Any, view: unknown) =>
  client.views.open({ interactivity_pointer: body.interactivity.interactivity_pointer, view });

// deno-lint-ignore no-explicit-any
export function withHandlers<T extends { addBlockActionsHandler: any; addViewSubmissionHandler: any }>(fn: T): T {
  const review = async ({ action, body, client, env }: Any, decisions: [string, "accepted" | "rejected"][]) => {
    const eng = engineFor(client, env, body);
    const results = [];
    for (const [id, d] of decisions) results.push(await eng.review(id, d, body.user.id));
    if (results.includes("not_authorised")) {
      await ephemeral(client, body, `Only <@${eng.s.reviewer}> can accept or reject flagged entries.`);
      return;
    }
    const entry = await eng.store.entry(decisions[0][0]);
    if (entry) await eng.afterReviews(entry.cycle_id);
    void action;
    await finish(eng);
  };

  fn.addBlockActionsHandler(
    [B.A.reviewAccept, B.A.reviewReject],
    (ctx: Any) =>
      review(ctx, [[ctx.action.value, ctx.action.action_id === B.A.reviewAccept ? "accepted" : "rejected"]]),
  );

  fn.addBlockActionsHandler(B.A.reviewAll, (ctx: Any) => {
    const v = JSON.parse(ctx.action.value);
    return review(ctx, v.ids.map((id: string) => [id, v.d]));
  });

  fn.addBlockActionsHandler(B.A.approve, async ({ action, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    const result = await eng.approve(action.value, body.user.id);
    if (result === "not_authorised") {
      await ephemeral(client, body, `Only <@${eng.s.approver}> can give the final approval.`);
    } else if (result !== "approved") {
      await ephemeral(client, body, `Nothing to do - this month is *${result.replace("_", " ")}*.`);
    }
    await finish(eng);
  });

  fn.addBlockActionsHandler(B.A.raiseConcern, async ({ action, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    if (body.user.id !== eng.s.approver) {
      return void await ephemeral(client, body, `Only <@${eng.s.approver}> can raise a concern on the final approval.`);
    }
    await openModal(
      client,
      body,
      B.concernModal(action.value, await eng.store.entries(action.value, { payableOnly: true })),
    );
  });

  fn.addViewSubmissionHandler(B.V.concern, async ({ view, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    const v = B.modalValues(view);
    await eng.raiseConcern(JSON.parse(view.private_metadata).cid, body.user.id, v.concern, v.entries ?? []);
    await finish(eng);
  });

  fn.addBlockActionsHandler(B.A.concernRow, async ({ action, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    const [what, id] = (action.selected_option?.value ?? action.value).split(":");
    if (what === "edit") {
      const e = await eng.store.entry(id);
      const err = e ? await eng.checkReviewerEdit(e.cycle_id, body.user.id) : "Entry not found.";
      if (err) return void await ephemeral(client, body, err);
      return void await openModal(client, body, B.editModal(e!));
    }
    const err = await eng.setRowRemoved(id, body.user.id, what === "remove");
    if (err) await ephemeral(client, body, err);
  });

  fn.addViewSubmissionHandler(B.V.edit, async ({ view, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    const v = B.modalValues(view);
    const err = await eng.editEntry(
      JSON.parse(view.private_metadata).id,
      body.user.id,
      v.date,
      v.shift as Shift,
      v.extra ?? "",
    );
    return err ? { response_action: "errors", errors: { date: err } } : undefined;
  });

  fn.addBlockActionsHandler(B.A.concernAdd, async ({ action, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    const err = await eng.checkReviewerEdit(action.value, body.user.id);
    if (err) return void await ephemeral(client, body, err);
    await openModal(client, body, B.addModal(action.value));
  });

  fn.addViewSubmissionHandler(B.V.add, async ({ view, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    const v = B.modalValues(view);
    const err = await eng.addEntryByReviewer(
      JSON.parse(view.private_metadata).cid,
      body.user.id,
      v.person,
      v.date,
      v.shift as Shift,
      v.extra ?? "",
    );
    return err ? { response_action: "errors", errors: { date: err } } : undefined;
  });

  fn.addBlockActionsHandler(B.A.concernRespond, async ({ action, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    if (body.user.id !== eng.s.reviewer) {
      return void await ephemeral(client, body, `Only <@${eng.s.reviewer}> can respond to this concern.`);
    }
    await openModal(client, body, B.respondModal(action.value, (await eng.store.cycle(action.value))!));
  });

  fn.addViewSubmissionHandler(B.V.respond, async ({ view, body, client, env }: Any) => {
    const eng = engineFor(client, env, body);
    await eng.respondToConcern(JSON.parse(view.private_metadata).cid, body.user.id, B.modalValues(view).response);
    await finish(eng);
  });

  return fn;
}
