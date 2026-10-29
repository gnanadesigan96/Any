import type { Trigger } from "deno-slack-sdk/types.ts";
import { TriggerTypes } from "deno-slack-api/mod.ts";
import { SchedulerWorkflow } from "../../workflows/scheduler_workflow.ts";

/** TEST timeline step: runs once, 111 min after you create it. */
const trigger: Trigger<typeof SchedulerWorkflow.definition> = {
  type: TriggerTypes.Scheduled,
  name: "TEST t110_nudge_check",
  workflow: `#/workflows/${SchedulerWorkflow.definition.callback_id}`,
  inputs: {},
  schedule: { start_time: new Date(Date.now() + 111 * 60_000).toISOString(), frequency: { type: "once" } },
};
export default trigger;
