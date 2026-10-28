"""Slack entry point: mention the bot in a channel (or DM it) and it replies in the thread.
Also runs the monthly support-allowance workflow and handles its buttons and forms.

Run:  python app.py   (needs SLACK_BOT_TOKEN, SLACK_APP_TOKEN, ANTHROPIC_API_KEY)
"""

import logging
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agent import slack_actions, workflow
from agent.config import Workflow
from agent.context import RequestContext
from agent.core import run_agent
from agent.store import Store

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
        return "" if uid == bot_user_id else f"@{_user_name(client, uid)} ({uid})"
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

    ctx = RequestContext(user_id=event["user"], user_name=_user_name(client, event["user"]),
                         channel_id=channel, thread_ts=thread_ts)
    client.reactions_add(channel=channel, timestamp=event["ts"], name="eyes")
    try:
        replies = run_agent(convo, ctx)
    except Exception:
        log.exception("agent failed")
        replies = ["Sorry, something went wrong while handling that. Please try again."]
    finally:
        try:
            client.reactions_remove(channel=channel, timestamp=event["ts"], name="eyes")
        except Exception:
            pass
    for text in replies:
        if text:
            client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=text)


@app.event("app_mention")
def on_mention(event, client, context):
    _handle(event, client, context)


@app.event("message")
def on_message(event, client, context):
    # Channel messages arrive via app_mention; here we only answer direct messages from people.
    if event.get("channel_type") != "im" or event.get("bot_id") or event.get("subtype"):
        return
    _handle(event, client, context)


slack_actions.register(app)


def _channel_id(name: str) -> str:
    cursor = None
    while True:
        resp = app.client.conversations_list(types="public_channel,private_channel", limit=1000, cursor=cursor,
                                             exclude_archived=True)
        for ch in resp["channels"]:
            if ch["name"] == name:
                return ch["id"]
        cursor = (resp.get("response_metadata") or {}).get("next_cursor")
        if not cursor:
            raise SystemExit(f"Channel #{name} not found - check the name and invite the bot to it (/invite @ops-agent).")


def _user_id(email: str) -> str:
    try:
        return app.client.users_lookupByEmail(email=email)["user"]["id"]
    except Exception:
        raise SystemExit(f"No Slack user with e-mail {email} - use their member ID instead.") from None


def start_workflow():
    raw_cfg = Workflow.load()
    placeholders = [v for v in (raw_cfg.collection_channel, raw_cfg.approval_channel, raw_cfg.hr_channel,
                                raw_cfg.review_channel, raw_cfg.reviewer, raw_cfg.approver, raw_cfg.hr_group,
                                *raw_cfg.hr_users) if v and "REPLACE" in v]
    if placeholders:
        raise SystemExit(f"Fill these in the workflow config first: {', '.join(placeholders)}")
    bot_user_id = app.client.auth_test()["user_id"]
    # Channels may be given as #names and people as e-mails; Slack needs IDs.
    cfg = raw_cfg.resolve_emails(_user_id).resolve_channels(_channel_id)
    log.info("support workflow: reviewer=%s approver=%s hr=%s channels: collect=%s review=%s approve=%s hr=%s",
             cfg.reviewer, cfg.approver, cfg.hr_users or cfg.hr_group, cfg.collection_channel,
             cfg.review_target, cfg.approval_channel, cfg.hr_channel)
    default_db = "test_support_allowance.db" if cfg.test_timeline else "support_allowance.db"
    wf = workflow.SupportWorkflow(app.client, Store(os.environ.get("SUPPORT_DB_PATH", default_db)), cfg, bot_user_id)
    if wf.pretend_clock:
        for minutes, pretend in cfg.test_timeline:
            real = wf.pretend_clock.real_for(pretend).astimezone(cfg.tz)
            log.warning("TEST MODE: pretend %s at real %s", f"{pretend:%d %b %H:%M}", f"{real:%d %b %H:%M}")
        log.warning("TEST MODE: pretend time now is %s", f"{wf.now():%d %b %Y %H:%M}")
    workflow.set_instance(wf)
    wf.start()


if __name__ == "__main__":
    start_workflow()
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
