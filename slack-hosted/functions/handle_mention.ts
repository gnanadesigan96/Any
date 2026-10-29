/** Someone @mentioned the bot in one of its channels: run the agent and reply in the thread. */

import { DefineFunction, Schema, SlackFunction } from "deno-slack-sdk/mod.ts";
import { problems, settingsFor } from "../config/settings.ts";
import { type Request, runAgent } from "../lib/agent.ts";
import { Engine } from "../lib/engine.ts";
import { withHandlers } from "../lib/handlers.ts";
import { DatastoreTables, Store } from "../lib/store.ts";

export const HandleMentionFunction = DefineFunction({
  callback_id: "handle_mention",
  title: "Answer a mention",
  description: "Reads a message that mentions the bot and replies in the thread",
  source_file: "functions/handle_mention.ts",
  input_parameters: {
    properties: {
      channel_id: { type: Schema.slack.types.channel_id },
      user_id: { type: Schema.slack.types.user_id },
      text: { type: Schema.types.string },
      message_ts: { type: Schema.types.string },
    },
    required: ["channel_id", "user_id", "text", "message_ts"],
  },
  output_parameters: { properties: {}, required: [] },
});

// deno-lint-ignore no-explicit-any
type Any = any;

async function readable(eng: Engine, text: string, botUserId: string): Promise<string> {
  let out = text ?? "";
  for (const m of [...out.matchAll(/<@([A-Z0-9]+)>/g)]) {
    out = out.replace(m[0], m[1] === botUserId ? "" : `@${await eng.userName(m[1])} (${m[1]})`);
  }
  return out.trim();
}

export default withHandlers(SlackFunction(HandleMentionFunction, async ({ inputs, client, env, event }) => {
  const s = settingsFor(env);
  const eng = new Engine(client, new Store(new DatastoreTables(client)), s, event.function_execution_id);
  if (!eng.allowedChannels.includes(inputs.channel_id) || problems(s).length) return { outputs: {} };

  if (s.mode === "test") await eng.tick(); // keeps the pretend timeline moving between test triggers

  const botUserId = (await client.auth.test({})).user_id as string;
  // The mention payload has no thread: look it up (works for both thread replies and top-level messages).
  const thread = await client.conversations.replies({ channel: inputs.channel_id, ts: inputs.message_ts, limit: 50 });
  const msgs: Any[] = thread.ok ? thread.messages : [];
  const threadTs: string = msgs[0]?.ts ?? inputs.message_ts;
  let conversation: string;
  if (threadTs !== inputs.message_ts && msgs.length) {
    const lines = [];
    for (const m of msgs) {
      const who = m.user === botUserId || m.bot_id ? "Assistant (you)" : await eng.userName(m.user);
      lines.push(`${who}: ${await readable(eng, m.text, botUserId)}`);
    }
    conversation = "Slack thread so far (answer the last message):\n" + lines.join("\n");
  } else {
    conversation = await readable(eng, inputs.text, botUserId);
  }

  const req: Request = {
    userId: inputs.user_id,
    userName: await eng.userName(inputs.user_id),
    channelId: inputs.channel_id,
    threadTs,
    attachments: [],
    privateTo: "",
  };
  let reply: string;
  try {
    reply = await runAgent(eng, req, conversation, env);
  } catch (e) {
    console.error("agent failed", e);
    reply = "Sorry, something went wrong while handling that. Please try again.";
  }
  const parts = [reply, ...req.attachments].filter(Boolean);
  if (req.privateTo) {
    // Comparisons: only the requester sees them ("only visible to you" in the thread).
    for (const text of parts) {
      await client.chat.postEphemeral({ channel: inputs.channel_id, thread_ts: threadTs, user: req.privateTo, text });
    }
    await client.chat.postMessage({
      channel: inputs.channel_id,
      thread_ts: threadTs,
      text: `:lock: <@${req.privateTo}> I've shared the details with you privately in this thread ` +
        `(only you can see them; they disappear if Slack reloads - just ask again).`,
    });
  } else {
    for (const text of parts) await client.chat.postMessage({ channel: inputs.channel_id, thread_ts: threadTs, text });
  }
  // Stay running while any message we posted still needs clicks (buttons route to this execution).
  return (await eng.completeIfIdle(eng.executionId)) ? { outputs: {} } : { completed: false };
}));
