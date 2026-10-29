import type { Trigger } from "deno-slack-sdk/types.ts";
import { TriggerTypes } from "deno-slack-api/mod.ts";
import { SchedulerWorkflow } from "../../workflows/scheduler_workflow.ts";

/** TEST timeline step: runs once, 91 min after you create it, pretending it is 2026-10-20T00:00 IST. */
const trigger: Trigger<typeof SchedulerWorkflow.definition> = {
  type: TriggerTypes.Scheduled,
  name: "TEST t090_19th_eod_close",
  workflow: `#/workflows/${SchedulerWorkflow.definition.callback_id}`,
  inputs: { pretend_now: { value: "2026-10-20T00:00" } },
  schedule: { start_time: new Date(Date.now() + 91 * 60_000).toISOString(), frequency: { type: "once" } },
};
export default trigger;
