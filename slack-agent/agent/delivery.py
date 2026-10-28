"""Posting the agent's answer back to Slack - in the thread, or privately when a tool asked for it."""


def deliver(client, ctx, channel: str, thread_ts: str, replies: list):
    """Post `replies` in the thread, or - if a tool set ctx.private_reply - privately to that person.

    Private answers are "only visible to you" (ephemeral) messages in the same thread: nobody else
    can see them, and Slack doesn't keep them (they vanish on reload). This needs no extra permission.
    """
    replies = [r for r in replies if r]
    user = ctx.private_reply.get("user")
    if not user:
        for text in replies:
            client.chat_postMessage(channel=channel, thread_ts=thread_ts, text=text)
        return
    for text in replies:
        client.chat_postEphemeral(channel=channel, thread_ts=thread_ts, user=user, text=text)
    client.chat_postMessage(channel=channel, thread_ts=thread_ts,
                            text=f":lock: <@{user}> I've shared the details with you privately in this thread "
                                 f"(only you can see them; they disappear if Slack reloads - just ask again).")
