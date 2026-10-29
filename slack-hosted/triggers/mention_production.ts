import type { Trigger } from "deno-slack-sdk/types.ts";
import { TriggerContextData, TriggerEventTypes, TriggerTypes } from "deno-slack-api/mod.ts";
import { PRODUCTION } from "../config/settings.ts";
import { MentionWorkflow } from "../workflows/mention_workflow.ts";

/** Mentions in the PRODUCTION channels only. Create with: slack trigger create --trigger-def triggers/mention_production.ts */
const channels = [
  ...new Set([PRODUCTION.collectionChannel, PRODUCTION.reviewChannel, PRODUCTION.approvalChannel, PRODUCTION.hrChannel]
    .filter((c): c is string => !!c)),
] as [string, ...string[]];

const trigger: Trigger<typeof MentionWorkflow.definition> = {
  type: TriggerTypes.Event,
  name: "Ops Agent mentions (production)",
  workflow: `#/workflows/${MentionWorkflow.definition.callback_id}`,
  event: { event_type: TriggerEventTypes.AppMentioned, channel_ids: channels },
  inputs: {
    channel_id: { value: TriggerContextData.Event.AppMentioned.channel_id },
    user_id: { value: TriggerContextData.Event.AppMentioned.user_id },
    text: { value: TriggerContextData.Event.AppMentioned.text },
    message_ts: { value: TriggerContextData.Event.AppMentioned.message_ts },
  },
};
export default trigger;
