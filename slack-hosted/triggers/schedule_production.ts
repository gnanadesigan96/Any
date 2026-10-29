import type { Trigger } from "deno-slack-sdk/types.ts";
import { TriggerTypes } from "deno-slack-api/mod.ts";
import { SchedulerWorkflow } from "../workflows/scheduler_workflow.ts";

/**
 * Every 2 hours on the even hour (IST): covers the 10:00 reminders, closing at midnight after the 19th,
 * and 2-hourly nudges. Create with: slack trigger create --trigger-def triggers/schedule_production.ts
 */
const IST = 330 * 60_000;
const nowIst = new Date(Date.now() + IST);
const next = new Date(
  Date.UTC(nowIst.getUTCFullYear(), nowIst.getUTCMonth(), nowIst.getUTCDate(), nowIst.getUTCHours() + 1) - IST,
);
if (((next.getTime() + IST) / 3_600_000) % 2 !== 0) next.setTime(next.getTime() + 3_600_000); // align to an even IST hour

const trigger: Trigger<typeof SchedulerWorkflow.definition> = {
  type: TriggerTypes.Scheduled,
  name: "Support allowance scheduler (every 2 hours)",
  workflow: `#/workflows/${SchedulerWorkflow.definition.callback_id}`,
  inputs: {},
  schedule: { start_time: next.toISOString(), frequency: { type: "hourly", repeats_every: 2 } },
};
export default trigger;
