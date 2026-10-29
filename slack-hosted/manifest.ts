import { Manifest } from "deno-slack-sdk/mod.ts";
import { CyclesDatastore, EntriesDatastore, LiveMessagesDatastore, MetaDatastore } from "./datastores/datastores.ts";
import { HandleMentionFunction } from "./functions/handle_mention.ts";
import { SchedulerFunction } from "./functions/scheduler.ts";
import { MentionWorkflow } from "./workflows/mention_workflow.ts";
import { SchedulerWorkflow } from "./workflows/scheduler_workflow.ts";

/**
 * Least privilege: the bot can only read/post in channels it is invited to (and its mention trigger
 * only listens to the two configured channels). No channel listing, no e-mail lookup, no DMs,
 * no reactions, no files. The only outside service it can call is the Claude API.
 */
export default Manifest({
  name: "Ops Agent",
  description: "Monthly support allowance workflow",
  icon: "assets/icon.png",
  functions: [HandleMentionFunction, SchedulerFunction],
  workflows: [MentionWorkflow, SchedulerWorkflow],
  datastores: [CyclesDatastore, EntriesDatastore, LiveMessagesDatastore, MetaDatastore],
  outgoingDomains: ["api.anthropic.com"],
  botScopes: [
    "app_mentions:read",
    "chat:write",
    "channels:history",
    "groups:history",
    "users:read",
    "datastore:read",
    "datastore:write",
  ],
});
