"""Posting the agent's answer back to Slack - in the thread, or privately when a tool asked for it."""

import logging

log = logging.getLogger(__name__)


def deliver(client, ctx, channel: str, thread_ts: str, replies: list):
    """Post `replies` in the thread, or - if a tool set ctx.private_reply - to that person privately.

    Private answers go to the bot's direct message with the person (read-only for them). If that fails,
    they fall back to ephemeral messages in the channel, which only that person can see.
    """
    replies = [r for r in replies if r]
    user = ctx.private_reply.get("user")
    if not user:
        for text in replies:
            client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=text)
        return
    try:
        for text in replies:
            client.chat_postMessage(channel=user, text=text)
        note = f"<@{user}> I've shared the details with you privately - check your messages from me."
    except Exception:
        log.exception("private DM failed; falling back to an ephemeral reply")
        for text in replies:
            client.chat_postEphemeral(channel=channel, thread_ts=thread_ts, user=user, text=text)
        note = f"<@{user}> I've shared the details with you privately (only you can see them here)."
    client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=f":lock: {note}")
