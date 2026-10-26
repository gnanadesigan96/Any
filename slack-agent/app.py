"""Slack entry point: mention the bot in a channel (or DM it) and it replies in the thread.

Run:  python app.py   (needs SLACK_BOT_TOKEN, SLACK_APP_TOKEN, ANTHROPIC_API_KEY)
"""

import logging
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agent.context import RequestContext
from agent.core import run_agent

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
log = logging.getLogger("slack-agent")

app = App(token=os.environ["SLACK_BOT_TOKEN"])

_MENTION = re.compile(r"<@([A-Z0-9]+)>")
_name_cache = {}


def _user_name(client, user_id: str) -> str:
    if user_id not in _name_cache:
        try:
            profile = client.users_info(user=user_id)["user"]
            _name_cache[user_id] = (profile.get("real_name") or profile.get("name") or user_id)
        except Exception:
            _name_cache[user_id] = user_id
    return _name_cache[user_id]


def _readable(client, text: str, bot_user_id: str) -> str:
    """Turn <@U123> mentions into names so Claude knows who people are."""
    def repl(m):
        uid = m.group(1)
        return "" if uid == bot_user_id else f"@{_user_name(client, uid)}"
    return _MENTION.sub(repl, text or "").strip()


def _transcript(client, channel: str, thread_ts: str, bot_user_id: str) -> str:
    """The whole thread as plain text, oldest first, so follow-ups have context."""
    try:
        msgs = client.conversations_replies(channel=channel, ts=thread_ts, limit=50)["messages"]
    except Exception:
        log.exception("could not read thread history")
        return ""
    lines = []
    for m in msgs:
        speaker = "Assistant (you)" if m.get("user") == bot_user_id or m.get("bot_id") else _user_name(client, m.get("user", ""))
        lines.append(f"{speaker}: {_readable(client, m.get('text', ''), bot_user_id)}")
    return "\n".join(lines)


def _handle(event, client, context):
    channel = event["channel"]
    thread_ts = event.get("thread_ts") or event["ts"]
    bot_user_id = context.bot_user_id

    if event.get("thread_ts"):
        convo = "Slack thread so far (answer the last message):\n" + _transcript(client, channel, thread_ts, bot_user_id)
    else:
        convo = _readable(client, event.get("text", ""), bot_user_id)

    ctx = RequestContext(user_id=event["user"], user_name=_user_name(client, event["user"]), channel_id=channel)
    client.reactions_add(channel=channel, timestamp=event["ts"], name="eyes")
    try:
        reply = run_agent(convo, ctx)
    except Exception:
        log.exception("agent failed")
        reply = "Sorry, something went wrong while handling that. Please try again."
    finally:
        try:
            client.reactions_remove(channel=channel, timestamp=event["ts"], name="eyes")
        except Exception:
            pass
    client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=reply)


@app.event("app_mention")
def on_mention(event, client, context):
    _handle(event, client, context)


@app.event("message")
def on_message(event, client, context):
    # Channel messages arrive via app_mention; here we only answer direct messages from people.
    if event.get("channel_type") != "im" or event.get("bot_id") or event.get("subtype"):
        return
    _handle(event, client, context)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
