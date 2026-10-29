import { DefineWorkflow, Schema } from "deno-slack-sdk/mod.ts";
import { SchedulerFunction } from "../functions/scheduler.ts";

export const SchedulerWorkflow = DefineWorkflow({
  callback_id: "scheduler_workflow",
  title: "Support allowance scheduler",
  input_parameters: { properties: { pretend_now: { type: Schema.types.string } }, required: [] },
});

SchedulerWorkflow.addStep(SchedulerFunction, { pretend_now: SchedulerWorkflow.inputs.pretend_now });
