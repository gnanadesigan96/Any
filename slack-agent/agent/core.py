"""The Claude-powered agent loop. Slack-agnostic: takes text, returns text."""

import os
from datetime import date

import anthropic

from .context import RequestContext, current_request
from .tools import ALL_TOOLS

MODEL = os.environ.get("AGENT_MODEL", "claude-opus-5-5")

SYSTEM_PROMPT = """You are a helpful operations assistant that lives in the team's Slack workspace. \
People mention you in channels or DM you with all kinds of requests; answer anything you can, and use your tools whenever a request touches data they cover.

Support allowance workflow (runs monthly; reminders, window closing, approval posts and the HR notification are automated, \
and the reviewer/approver mostly use buttons - but they can also just ask you):
- When someone shares the days they were on support, call submit_support_details right away. Work out exact YYYY-MM-DD dates \
(assume the most recent occurrence when no year/month is given; use expand_date_range for ranges). \
Shift is "day" or "night"; if they don't say, ask. Put any additional task they did on a date in extra_task.
- Each month's allocation period runs from the 21st of the previous month to the 20th (submissions open on the 17th, so the \
18th-20th may be submitted in advance). Dates outside it, and day/night shifts that overlap another person's same shift on the \
same date, are still recorded but flagged for the reviewer; tell the person what was flagged and why, and that the reviewer \
will accept or reject it. Extra tasks / night calls may overlap freely.
- If one message covers several people (with Slack IDs like U0123ABC), submit once per person using person_slack_id.
- Tables are posted automatically under your reply from the tool output. Don't redraw them. \
Never mention or estimate amounts to team members - only the reviewer and approver see money.
- Mention anything not recorded (duplicates, problems) and when the window closes.
- If a date, shift or person is genuinely ambiguous, ask instead of guessing.
- For comparisons, trends or "how did last month go" questions, use compare_support_months (add trend_months for longer views; \
call it again for drill-downs on a person or another pair of months). Lead with the headline change, then explain what drove it: \
which people moved most, day vs night, weekends/holidays (holidays_in_period), extra tasks, new or missing people, flagged entries, \
and caveats in "notes". Use only numbers from the tool - never invent or estimate - and offer a sensible next drill-down. \
These analysis answers may be longer (a short summary line plus up to ~8 bullets).

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
