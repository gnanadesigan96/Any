import type { Trigger } from "deno-slack-sdk/types.ts";
import { TriggerTypes } from "deno-slack-api/mod.ts";
import { SchedulerWorkflow } from "../../workflows/scheduler_workflow.ts";

/** TEST timeline step: runs once, 61 min after you create it, pretending it is 2026-10-19T10:00 IST. */
const trigger: Trigger<typeof SchedulerWorkflow.definition> = {
  type: TriggerTypes.Scheduled,
  name: "TEST t060_19th_last_day",
  workflow: `#/workflows/${SchedulerWorkflow.definition.callback_id}`,
  inputs: { pretend_now: { value: "2026-10-19T10:00" } },
  schedule: { start_time: new Date(Date.now() + 61 * 60_000).toISOString(), frequency: { type: "once" } },
};
export default trigger;
