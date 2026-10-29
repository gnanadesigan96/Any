import { DefineWorkflow, Schema } from "deno-slack-sdk/mod.ts";
import { HandleMentionFunction } from "../functions/handle_mention.ts";

export const MentionWorkflow = DefineWorkflow({
  callback_id: "mention_workflow",
  title: "Answer a mention",
  input_parameters: {
    properties: {
      channel_id: { type: Schema.slack.types.channel_id },
      user_id: { type: Schema.slack.types.user_id },
      text: { type: Schema.types.string },
      message_ts: { type: Schema.types.string },
    },
    required: ["channel_id", "user_id", "text", "message_ts"],
  },
});

MentionWorkflow.addStep(HandleMentionFunction, {
  channel_id: MentionWorkflow.inputs.channel_id,
  user_id: MentionWorkflow.inputs.user_id,
  text: MentionWorkflow.inputs.text,
  message_ts: MentionWorkflow.inputs.message_ts,
});
