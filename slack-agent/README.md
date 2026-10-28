# Slack Ops Agent

A multipurpose Slack bot powered by Claude. Mention it in one of its configured
channels and it replies in the thread. Its main job is the **monthly support allowance
workflow**. It can also answer general questions, using web search when needed.

## Monthly support allowance flow

**Allocation period:** each month's cycle pays support dates from the **21st of
last month to the 20th of this month**. For example, October covers
21 Sep – 20 Oct. Submissions open on the 17th and close at 19th EOD, so the
18th–20th can be submitted in advance and count normally. Anything after the
20th is flagged.

**Overlaps:** a day or night shift can only belong to one person on a given
date. If two people claim the same shift on the same date, both entries are
flagged for the reviewer. Different shifts on the same day (one day, one night)
are fine, and extra tasks / night calls may overlap freely.

| When (IST) | What happens |
|---|---|
| **17th, 10:00** | The bot asks the support channel to submit details for the period, and states the deadline. |
| 17th–19th | People mention the bot with their days. The bot records them and replies with a **table of their details (no amounts)**. |
| any time | Some entries are kept but **flagged**: a date **outside the period**, or a **day/night shift that overlaps another person's same shift on the same date**. They are posted in the review channel (by default the support channel) for the reviewer (Gnanadesigan), naming the member, date and reason, with **Accept / Reject** buttons for each entry. For overlaps, both people's entries are put up so the reviewer chooses which stands. Each submitter is told the outcome in their thread. |
| **19th, 10:00** | "Last day" reminder. |
| **19th, 23:59 (EOD)** | Window closes. If flagged entries are still undecided, the reviewer is reminded and the final table **waits** until they're decided. |
| then | The **final tables (summary + per-day detail)** are posted in the approval channel and the **approver (Poornodhaya)** is tagged with **Approve / Raise concern** buttons. |
| Raise concern | A form asks for the concern and, optionally, the specific entries. It comes back to the reviewer as an **interactive table** in the thread, with ⋮ *Edit* / *Remove* (or *Restore*) on each row, plus *Add entry* and *Respond & send for approval*. The table updates in place as rows are fixed. The approver then gets the updated tables plus the response, with the buttons again. |
| while waiting | **Nudges:** every 2 hours the bot re-tags whoever the next step is waiting on. That's the approver while approval is pending, and the reviewer while flags are undecided or a concern is open. At most 3 times per wait (`nudges` in the config). |
| Approve | The **HR group is tagged**: details for the month are updated and approved. |

All approvals and rejections are buttons. Each button only works for the right
person (others get a private "only X can do this"), and double clicks are harmless.
The bot is also conversational, so the same things can be done by asking it:
"accept all of Priya's flagged dates", "show the October report", "close the
window now", "approve October", "respond to the concern: fixed Arun's dates".

### Submitting (team members)

> **@ops-agent** night shift 3 and 4 Oct, day shift 11 Oct. On 11th I also did the DB failover

```
Support details - Priya Kumar - October 2026 (3 entries)
Date        | Day | Shift | Day type | Extra task  | Status
------------+-----+-------+----------+-------------+---------
03 Oct 2026 | Sat | Night | Weekend  | -           | Recorded
04 Oct 2026 | Sun | Night | Weekend  | -           | Recorded
11 Oct 2026 | Sun | Day   | Weekend  | DB failover | Recorded
```

People can also say "remove my 4 Oct night shift", "show my support details" or
"when does the window close?". A lead can submit for someone else by
mentioning them. The same person + date + shift can't be claimed twice, even
across months, and an approved month is locked. Anything sent after the 19th
EOD goes into **next month's** cycle, and is flagged there if its dates fall
outside that period.

### Comparisons and trends

Ask the bot in plain words, for example:

- "@ops-agent compare with last month and tell me the trend"
- "how did October go vs September?"
- "show the trend for the last 6 months"
- "why did night shifts go up?" / "show Priya's last 3 months"

The bot posts exact tables, all computed from the recorded data:

- **Month vs month:** total amount (split into shift and extra-task allowance),
  people, entries, day/night shifts, weekday/weekend/holiday shifts, extra
  tasks, average per person, and flagged entries accepted/rejected, each with
  its change and %.
- **Per person:** shifts, nights, weekend/holiday shifts, extra tasks and
  amount, shown as "Sep → Oct", plus who is new or missing.
- **Trend:** one row per month, with the change from the previous month.

It then explains what drove the change: who moved most, holidays in the
period, night vs day, extra tasks, and caveats such as a month not yet approved
or entries still awaiting review. It offers follow-ups like drilling into a
person.

**Access:** only the people listed in `analytics_users` (Uday) can ask for
comparisons and trends. When Uday asks, in either channel, the tables,
amounts and explanation are posted in the thread as **"only visible to you"**
messages that nobody else can see. Everyone sees only *"@Uday I've shared the
details with you privately"*. Slack doesn't keep these private messages: they
disappear when Slack reloads, so he just asks again. Anyone else who asks, including the reviewer and approver, gets
*"Sorry, you don't have access to support allowance comparisons and trends."*

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

## Testing before go-live

See **[TESTING.md](TESTING.md)**. Test mode runs the whole month in about 1.5
hours, using test channels and test approver/HR people.

## Setup

1. **Create the Slack app:** https://api.slack.com/apps → *Create New App* →
   *From a manifest* → paste `manifest.yaml` → install it to the workspace.
   - Bot token (`xoxb-…`): *OAuth & Permissions*.
   - App token (`xapp-…`): *Basic Information → App-Level Tokens*, scope `connections:write`.
2. **Fill in `config/workflow.json`:**
   - `collection_channel`: channel where the team submits (open the channel → channel name → *About* → Channel ID, `C…`).
   - `approval_channel`: the channel where the final table goes for approval.
   - `hr_channel`: leave `null` to tag HR in the approval channel. Set a channel ID to send the tables and the HR tag elsewhere.
   - `review_channel`: where flagged entries are posted for the reviewer (`null` = the collection channel).
   - `reviewer`: Gnanadesigan (`U0C2TN3B562`, already set). `approver`: Poornodhaya's **member ID** (profile → ⋮ → *Copy member ID*).
   - `hr_group`: the HR user group ID (`S…`; from the group's page in *People → User groups*). Or list member IDs in `hr_users`.
   - `period`: `{"start_day": 21, "end_day": 20}`.
   - `schedule`: defaults are 17th 10:00, 19th 10:00 and 19th 23:59, in `Asia/Kolkata`.
3. **Invite the bot** to those channels **only**: `/invite @ops-agent`.

### Access is limited to the configured channels

Slack always installs an app for the whole workspace, so the limit is enforced
by permissions and by the bot itself:

- **Permissions** (`manifest.yaml`): the bot can only read and post in channels
  it has been **invited** to. It has no permission to list channels, look people
  up by e-mail, or read or send direct messages. Its messages tab is off.
- **No delete permissions.** The bot has no reaction or file permissions. Slack
  has no delete permission for bots, and `chat:write` would only let it delete
  its *own* messages. The code never calls any delete, remove, archive, join,
  invite or settings method, and a test fails the build if one is added.
  Full permission list: post and edit its own messages (`chat:write`), see its
  @mentions and the threads in its two channels, look up people's names
  (`users:read`). Uday's private comparisons need no extra permission.
- **Bot behaviour:** it acts only in the channel IDs in the workflow config.
  Mentions in any other channel are ignored, even if someone invites it there.
- That's why the config takes **IDs only**: channel IDs (`C…`) and member IDs
  (`U…`). The bot refuses to start if it finds a name or an e-mail.
- Everyone talks to the bot by **@mentioning it in one of the two channels**,
  and it answers in the thread. Uday's comparisons arrive there too, as
  "only visible to you" messages.
- **Amounts appear only in the approval channel**, for the reviewer and
  approver. The support channel is visible to the whole team, so there the bot
  shows the same details (and, for the reviewer, everyone's entries) without money.
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
app.py                      Slack events, starts the scheduler
agent/core.py               Claude tool-use loop + system prompt
agent/workflow.py           Monthly cycle: reminders, close, flag review, approval, concerns, HR
agent/blocks.py             Buttons, interactive tables and forms (Block Kit)
agent/slack_actions.py      What happens when someone clicks / submits a form
agent/tools/                Tools Claude can call (support allowance, date helpers, ...)
agent/config.py             Loads rates + workflow settings
agent/store.py              SQLite: cycles and submitted entries
agent/report.py             Tables
agent/analytics.py          Month-over-month comparison and trends
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

The tests simulate a whole month: reminders, submissions, out-of-period flags
and the reviewer's decisions, the window closing at 19th EOD IST, final approval,
a concern fixed through the interactive table, the HR tag, and the button and
form handlers (including "only the right person can click").
