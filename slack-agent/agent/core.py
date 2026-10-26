"""The Claude-powered agent loop. Slack-agnostic: takes text, returns text."""

import os
from datetime import date

import anthropic

from .context import RequestContext, current_request
from .tools import ALL_TOOLS

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-5-5")

SYSTEM_PROMPT = """You are a helpful operations assistant that lives in the team's Slack workspace. \
People mention you in channels or DM you with all kinds of requests; answer anything you can, and use your tools whenever a request touches data they cover.

Support allowance workflow (runs monthly; the reminders, window closing, approval post and HR notification are automated):
- When someone shares the days they were on support, call submit_support_details right away. Work out exact YYYY-MM-DD dates \
(assume the most recent past occurrence when no year/month is given; use expand_date_range for ranges). \
Shift is "day" or "night"; if they don't say, ask. Put any additional task they did on a date in extra_task.
- If one message covers several people (with Slack IDs like U0123ABC), submit once per person using person_slack_id.
- Tables are posted automatically under your reply from the tool output. Don't redraw them. \
Never mention or estimate amounts to team members - only approvers see money.
- Mention anything not recorded (duplicates, future dates, problems) and when the window closes.
- If a date, shift or person is genuinely ambiguous, ask instead of guessing.

Replies are posted to Slack, so keep them short (1-3 lines when a table follows) and use Slack mrkdwn: *bold*, _italic_, `code`, bullets with "•". \
No markdown headings or tables."""

# Server-side web search lets the bot answer general questions; set ENABLE_WEB_SEARCH=false to turn it off.
_WEB_SEARCH = {"type": "web_search_20260209", "name": "web_search", "max_uses": 5}

_client = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _tools():
    tools = list(ALL_TOOLS)
    if os.environ.get("ENABLE_WEB_SEARCH", "true").lower() != "false":
        tools.append(_WEB_SEARCH)
    return tools


def run_agent(conversation: str, ctx: RequestContext) -> list:
    """Answer the latest request in `conversation` (a plain-text thread transcript).

    Returns the Slack messages to post: Claude's reply, then any tables the tools attached.
    """
    token = current_request.set(ctx)
    try:
        return [_run(conversation, ctx), *ctx.attachments]
    finally:
        current_request.reset(token)


def _run(conversation: str, ctx: RequestContext) -> str:
    # Volatile details (date, requester) go in the user turn so the system prompt stays cacheable.
    messages = [{
        "role": "user",
        "content": f"Today is {date.today().isoformat()} ({date.today():%A}). "
                   f"Request from {ctx.user_name} ({ctx.user_id}).\n\n{conversation}",
    }]

    # The tool runner doesn't resume `pause_turn` (long server-side web searches), so restart it when that happens.
    last = None
    for _ in range(4):
        runner = _get_client().beta.messages.tool_runner(
            model=MODEL,
            max_tokens=16000,
            max_iterations=15,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            tools=_tools(),
            messages=messages,
            output_config={"effort": "medium"},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
        for message in runner:
            last = message
            messages.append({"role": "assistant", "content": message.content})
            tool_response = runner.generate_tool_call_response()
            if tool_response is not None:
                messages.append(tool_response)
        if last is None or last.stop_reason != "pause_turn":
            break

    if last is None:
        return "Sorry, I didn't get a response - please try again."
    if last.stop_reason == "refusal":
        return "Sorry, I can't help with that request."
    text = "\n".join(b.text for b in last.content if b.type == "text").strip()
    if last.stop_reason == "max_tokens":
        text += "\n\n_(reply was cut off - ask me to continue)_"
    return text or "Done."
