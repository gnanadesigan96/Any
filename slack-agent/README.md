# Slack Ops Agent

A multipurpose Slack bot powered by Claude. Mention it in a channel (or DM it)
and it replies in the thread. It can answer general questions (with web
search), and it has tools for specific jobs. The first job is **support
allowances**.

## Example

> **@ops-agent** Priya Kumar was on support 1st–4th Oct and Arun on 2nd Oct (half day). Please allocate.

```
Allocated ✅
*Priya Kumar*
• 2026-10-01 Thu – weekday – ₹1,000
• 2026-10-02 Fri – holiday (Gandhi Jayanti) – ₹3,000
• 2026-10-03 Sat – weekend – ₹2,000
• 2026-10-04 Sun – weekend – ₹2,000
*Total: ₹8,000*

*Arun*
• 2026-10-02 Fri – holiday, half day – ₹1,500
*Total: ₹1,500*
```

Other things you can ask:

- "How much would Priya get for 10–12 Oct?" – preview only, nothing saved
- "What has been allocated in October?" / "Show Arun's allowance total"
- "What are the allowance rates?"
- Anything else – general questions, drafting messages, summarising the thread, etc.

Follow-ups in the same thread keep context ("ok, allocate that").

## How it works

```
Slack (Socket Mode) ──> app.py ──> agent/core.py (Claude + tool runner) ──> agent/tools/*
                                                                         └─> config/allowance_policy.json
                                                                         └─> SQLite ledger
```

- **Amounts are computed in code, never by the model.** Claude parses the
  message into names + dates and calls `calculate_support_allowance` /
  `allocate_support_allowance`; rates come from `config/allowance_policy.json`.
- **No double payment.** The ledger rejects a person/date that was already allocated.
- **Approvers.** Set `ALLOWANCE_APPROVERS` to a comma-separated list of Slack user
  IDs to restrict who can allocate. Anyone can still preview.

## Setup

1. **Create the Slack app:** https://api.slack.com/apps → *Create New App* →
   *From a manifest* → paste `manifest.yaml`. Install it to the workspace.
   - Bot token (`xoxb-…`): *OAuth & Permissions*.
   - App token (`xapp-…`): *Basic Information → App-Level Tokens*, scope `connections:write`.
2. **Set the rates:** edit `config/allowance_policy.json`. The bundled numbers
   are placeholders – put in your real weekday / weekend / holiday rates,
   half-day factor and holiday calendar.
3. **Run:**
   ```bash
   cd slack-agent
   pip install -r requirements.txt
   cp .env.example .env   # fill in tokens + ANTHROPIC_API_KEY
   set -a; source .env; set +a
   python app.py
   ```
4. Invite the bot to a channel (`/invite @ops-agent`) and mention it.

Socket Mode means no public URL is needed – it runs on any machine or container
with outbound internet. Keep `allowance_ledger.db` on persistent storage.

## Adding a new capability

The agent is a generic loop; every capability is a tool.

1. Create `agent/tools/my_feature.py`:
   ```python
   from anthropic import beta_tool

   @beta_tool
   def create_leave_request(person: str, start: str, end: str) -> str:
       """Record a leave request.

       Args:
           person: Employee name.
           start: First day, YYYY-MM-DD.
           end: Last day, YYYY-MM-DD.
       """
       ...
       return "recorded"

   TOOLS = [create_leave_request]
   ```
2. Register it in `agent/tools/__init__.py` (`*my_feature.TOOLS`).
3. Optionally add a line to `SYSTEM_PROMPT` in `agent/core.py` on when to use it.

The docstring and type hints become the tool definition Claude sees, so
describe clearly what it does and when to use it. Ideas: leave tracking,
Zoho Desk / Jira ticket lookup, on-call roster, expense claims.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `SLACK_BOT_TOKEN` | – | Bot token (`xoxb-`) |
| `SLACK_APP_TOKEN` | – | App-level token for Socket Mode (`xapp-`) |
| `ANTHROPIC_API_KEY` | – | Claude API key |
| `ALLOWANCE_APPROVERS` | empty (anyone) | Slack user IDs allowed to allocate |
| `ALLOWANCE_DB_PATH` | `allowance_ledger.db` | SQLite ledger location |
| `ENABLE_WEB_SEARCH` | `true` | Let the bot search the web for general questions |
| `AGENT_MODEL` | `claude-opus-5-5` | Claude model |

Refusal fallback (`fallbacks: "default"`) is enabled, so if the primary model
declines a request it is retried on a fallback model automatically.

## Tests

```bash
cd slack-agent && python -m pytest -q tests
```
