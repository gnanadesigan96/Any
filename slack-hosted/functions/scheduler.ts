/** Runs on a schedule: reminders on the 17th / 19th, closing at 19th EOD, and nudges. */

import { DefineFunction, Schema, SlackFunction } from "deno-slack-sdk/mod.ts";
import { problems, settingsFor } from "../config/settings.ts";
import { Engine } from "../lib/engine.ts";
import { withHandlers } from "../lib/handlers.ts";
import { DatastoreTables, Store } from "../lib/store.ts";

export const SchedulerFunction = DefineFunction({
  callback_id: "support_scheduler",
  title: "Support allowance scheduler",
  description: "Posts reminders, closes the window, sends the final table for approval and nudges",
  source_file: "functions/scheduler.ts",
  input_parameters: {
    properties: {
      // Test mode only: the date/time the bot should pretend it is (e.g. "2026-10-17T10:00").
      pretend_now: { type: Schema.types.string },
    },
    required: [],
  },
  output_parameters: { properties: {}, required: [] },
});

export default withHandlers(SlackFunction(SchedulerFunction, async ({ inputs, client, env, event }) => {
  const s = settingsFor(env);
  const bad = problems(s);
  if (bad.length) {
    console.error("Fix config/settings.ts first:\n  " + bad.join("\n  "));
    return { error: "settings incomplete: " + bad.join("; ") };
  }
  const eng = new Engine(client, new Store(new DatastoreTables(client)), s, event.function_execution_id);
  if (s.mode === "test" && inputs.pretend_now) await eng.setPretendNow(inputs.pretend_now);
  await eng.tick();
  // Stay running while the approval / review message we posted still needs clicks.
  return (await eng.completeIfIdle(eng.executionId)) ? { outputs: {} } : { completed: false };
}));
