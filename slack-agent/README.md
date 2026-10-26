# Slack Ops Agent

A multipurpose Slack bot powered by Claude. Mention it in a channel (or DM it)
and it replies in the thread. Its main job is the **monthly support allowance
workflow**. It can also answer general questions, using web search when needed.

## Monthly support allowance flow

| When (IST) | What the bot does |
|---|---|
| **17th, 10:00** | Posts in the support channel asking everyone to submit their support details, with the deadline. |
| 17th–19th | People mention the bot with their days. The bot records them and replies with a **table of their details (no amounts)**. |
| **19th, 10:00** | "Last day" reminder. |
| **19th, 23:59 (EOD)** | Window closes. The bot posts the **final tables (summary + per-day detail + CSV)** in the approval channel and **tags the approver**, with *Approve* / *Needs changes* buttons. |
| On approval | The bot **tags the HR group**: details for the month are updated and approved. |

Everything should be done by the 20th.

### Submitting (team members)

> **@ops-agent** night shift 3 and 4 Oct, day shift 11 Oct. On 11th I also did the DB failover

The bot replies:

```
Support details - Priya Kumar - October 2026 (3 entries)
Date        | Day | Shift | Day type | Extra task
------------+-----+-------+----------+---------------
03 Oct 2026 | Sat | Night | Weekend  | -
04 Oct 2026 | Sun | Night | Weekend  | -
11 Oct 2026 | Sun | Day   | Weekend  | DB failover
```

People can also say "remove my 4 Oct night shift", "show my support details",
or "when does the window close?". A lead can submit for someone else by
mentioning them: "@Arun was on day shift 5–7 Oct". The bot refuses:

- the same person + date + shift twice, even across months,
- dates in the future,
- edits to a month that is already approved.

**Late submissions:** anything sent after the 19th EOD goes into **next month's**
cycle, and the bot says so.

### Approving (approver)

- Click **Approve**. HR is tagged straight away. Only the configured approver's
  click is accepted, and a double click doesn't notify HR twice.
- Or click **Needs changes**, then tell the bot in that thread what to fix
  ("remove Priya's 3 Oct night shift", "add a day shift for Arun on 12 Oct").
  Then say "send it for approval again" and the updated tables are re-posted.
- Approver-only chat commands: "close the window now", "show the October
  report", "approve October".

### Rates (`config/allowance_policy.json`)

| Shift | Weekday | Weekend | Govt. holiday on a weekday |
|---|---|---|---|
| Day | ₹500 | ₹1,000 | ₹1,000 |
| Night | ₹1,000 | ₹500 | ₹1,000 (same as a normal weekday) |
| Extra task (anything additional, per day) | +₹500 | +₹500 | +₹500 |

A holiday that falls on a weekend uses the weekend rate. Amounts are always
calculated in code from this file and never by the AI. Team members never see
amounts. Only the approver and HR do.

**Holidays:** only fixed-date ones (Republic Day, Labour Day, Independence Day,
Gandhi Jayanti, Christmas) are pre-filled. Add your company's festival
holidays (Holi, Eid, Diwali, …) to `holidays`.

## Setup

1. **Create the Slack app:** https://api.slack.com/apps → *Create New App* →
   *From a manifest* → paste `manifest.yaml` → install it to the workspace.
   - Bot token (`xoxb-…`): *OAuth & Permissions*.
   - App token (`xapp-…`): *Basic Information → App-Level Tokens*, scope `connections:write`.
2. **Fill in `config/workflow.json`:** the bot needs Slack **IDs**, not names.
   - `collection_channel`: channel where the team submits (open the channel → channel name → *About* → Channel ID, `C…`).
   - `approval_channel`: the "other channel" where the final table goes.
   - `hr_channel`: leave `null` to tag HR in the approval channel. Set a channel ID to send the tables and the HR tag somewhere else.
   - `approvers`: the approver's member ID (profile → ⋮ → *Copy member ID*, `U…`).
   - `hr_group`: the HR user group ID (`S…`; from the group's page in *People → User groups*). Or list individual people in `hr_users`.
   - `schedule`: days and times; the defaults are 17th 10:00, 19th 10:00, 19th 23:59 in `Asia/Kolkata`.
3. **Invite the bot** to all those channels: `/invite @ops-agent`.
4. **Run** on a machine that stays on:
   ```bash
   cd slack-agent
   pip install -r requirements.txt
   cp .env.example .env   # fill in the tokens + ANTHROPIC_API_KEY
   set -a; source .env; set +a
   python app.py
   ```

Socket Mode means no public URL is needed. State is kept in
`support_allowance.db` (SQLite), so keep it on persistent storage and back it up.
If the bot is down at a scheduled moment, it catches up when it comes back and
never repeats a step.

## Adding another capability

The agent is a generic loop, and every capability is a tool.

1. Create `agent/tools/my_feature.py` with `@beta_tool` functions and a `TOOLS = [...]` list.
   The docstring and type hints become the tool definition Claude sees.
2. Register it in `agent/tools/__init__.py`.
3. Optionally add a line to `SYSTEM_PROMPT` in `agent/core.py` saying when to use it.

A tool can call `current_request.get().attachments.append(text)` to have exact
text, such as a table, posted under the bot's reply.

## Layout

```
app.py                      Slack events, Approve/Needs-changes buttons, starts the scheduler
agent/core.py               Claude tool-use loop + system prompt
agent/workflow.py           Monthly cycle: reminders, close, approval post, HR notification
agent/tools/                Tools Claude can call (support allowance, date helpers, ...)
agent/config.py             Loads rates + workflow settings
agent/store.py              SQLite: cycles and submitted entries
agent/report.py             Tables and CSV
config/allowance_policy.json  Rates and holidays
config/workflow.json          Channels, approver, HR group, schedule
```

## Configuration (environment)

| Variable | Default | Purpose |
|---|---|---|
| `SLACK_BOT_TOKEN` | – | Bot token (`xoxb-`) |
| `SLACK_APP_TOKEN` | – | App-level token for Socket Mode (`xapp-`) |
| `ANTHROPIC_API_KEY` | – | Claude API key |
| `SUPPORT_DB_PATH` | `support_allowance.db` | SQLite file |
| `ENABLE_WEB_SEARCH` | `true` | Let the bot search the web for general questions |
| `AGENT_MODEL` | `claude-opus-5-5` | Claude model |

## Tests

```bash
cd slack-agent && python -m pytest -q tests
```

The tests simulate a whole month: reminders, submissions, the window closing
at 19th EOD IST, approval, the HR tag, sending back for changes, and late
submissions rolling into the next month.
