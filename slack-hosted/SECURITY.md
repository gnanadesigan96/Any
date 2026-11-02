# Security & compliance notes: Ops Agent (support allowance)

This document covers the Slack-hosted app in this folder, which is the version that goes to
production. The code was reviewed independently, and every finding is fixed and covered by tests in
`tests/engine_test.ts` (section "security").

## What the app can do (permissions)

Bot scopes (`manifest.ts`). The exact list is pinned by a test, which fails if anything is added.

| Scope | Why |
|---|---|
| `app_mentions:read` | Receive @mentions |
| `chat:write` | Post replies and update its own approval / review messages |
| `channels:history`, `groups:history` | Read the thread it is replying in (only channels it has been invited to) |
| `users:read` | Show names in tables |
| `datastore:read`, `datastore:write` | The app's own records (entries, months, audit log) |

- **Not granted:** no delete, file, reaction, DM, channel-listing or e-mail lookup permissions. A test
  fails the build if the code ever calls a delete, remove, archive, kick, leave, rename, invite, join
  or set method.
- **Outbound network:** only `api.anthropic.com` (`outgoingDomains`).
- **Channels:** the mention trigger listens only to the configured channel IDs, and the code also
  ignores any other channel.

## Who can do what (enforced in code, not by the AI)

| Action | Who | How |
|---|---|---|
| Submit / withdraw / view support days | Each person, **own data only** | Chat. There is no "on behalf of" |
| Accept / reject flagged entries | Reviewer | Buttons |
| Edit / remove / add rows while answering a concern | Reviewer | Concern table buttons and forms |
| Close the window early | Reviewer or approver | Chat request, then a **Confirm** button only the requester can click |
| Final approval / raise concern | Approver | Buttons |
| See amounts | Reviewer, approver, HR | Only in the approval channel. Everywhere else, team-wide views are "only visible to you" and have no amounts |
| Comparisons and trends | `analyticsUsers` only | Shown "only visible to you" |
| Reset test data | Reviewer, test mode only | Confirm button. Archives records and deletes nothing |

The AI only turns a person's own message into tool calls. Every tool checks the requester's Slack ID
(from Slack's event, not from the AI), and admin actions can't run from chat without a click. So
text planted in a thread can't make the bot approve, review, or act for someone else.

## Hardening in place

- **Prompt injection:**
  - Other people's thread messages are sent to the AI marked as context only.
  - Tools act only for the requester.
  - Admin actions need a click.
  - The AI's reply is cleaned before posting: `@channel` / `@here` / group pings are removed, and
    disguised links are shown in full.
- **Slack formatting injection:** all user-provided text (extra tasks, concerns, responses, names) is
  escaped before it's posted, so it can't ping, mention or hide links.
- **Input limits:**
  - At most 62 entries per message.
  - Extra task: 200 characters. Concern / response: 1,500 characters.
  - Dates more than about 2 months outside the period are refused.
  - Month IDs are validated (`YYYY-MM`).
- **Double clicks and races:** approving, raising a concern, responding, closing and releasing the
  final table each run once per message, under a lock. HR can't be tagged twice. Each person's
  submissions are processed one at a time.
- **Abuse and cost:** at most 8 mentions per person per 10 minutes. The AI gets at most 4 rounds and
  4,000 output tokens per request, inside a 50-second budget.
- **Errors:** internal errors are logged (`slack activity`), and users only see a generic message.
- **Test vs production:**
  - The pretend clock and reset only work when `APP_MODE=test`.
  - Test mode refuses to start if any of its channels is a production channel.
  - Production flagged-entry reviews go to the approval channel by default, not the team channel.

## Personal data

| Data | Where it lives | Notes |
|---|---|---|
| Support entries: person ID and name, dates, shifts, extra-task text, review status | Slack datastore (`support_entries`) | Inside your Slack workspace and covered by Slack's data handling |
| Months, approvals, concerns | `support_cycles` | |
| Audit log: actor ID, action, before/after, time | `support_audit` | **Append-only.** Export with `slack datastore query '{"datastore":"support_audit"}'` |
| Messages and tables | Slack channels | Subject to the workspace's Slack retention settings |

**Sent to the Claude API (Anthropic):**
- The requester's message.
- Up to 15 earlier thread messages, each capped at 600 characters.
- Tool results: dates, shifts, extra-task text, counts and amounts.
- People appear **only as Slack member IDs** (`<@U…>`). Names are never sent; Slack shows the names
  when the reply is posted.
- Under Anthropic's commercial terms, API data is not used to train models. **Check your organisation's
  agreement / DPA with Anthropic for retention**, and ask for zero data retention if your policy
  requires it.
- The API key is stored as an encrypted Slack app environment variable
  (`slack env add ANTHROPIC_API_KEY …`). It is never in the code or the logs.

## Decisions for CoreStack (policy, not code)

1. **Retention.** Records are kept until someone decides otherwise. You asked for no delete
   permissions, so nothing expires automatically. Decide how long allowance records and the audit log
   must be kept, for example the payroll retention period. If deletion is ever needed, it is done by an
   admin with the Slack CLI, not by the bot.
2. **Approval channel membership.** Amounts are visible to everyone in the approval channel. Keep it
   private, with only the reviewer, the approver and HR.
3. **Test workspace or app.** Test and production share the same app's datastores, separated by mode
   and archiving. For stricter separation, deploy the test as a separate app (`slack deploy` with a
   different app) or in a sandbox workspace.
4. **Admin approval.** Have your Slack admin review this document and the permission list when they
   approve the app.

## Known limits

- **Locks are best-effort.** Slack datastores have no atomic conditional writes. The locks make
  double processing very unlikely, and the audit log and status checks show it if it ever happens.
- **"Only visible to you" messages** disappear when Slack reloads, and Slack does not keep them.
- **The self-hosted Python version** in `../slack-agent` was a prototype for the laptop test. It is
  **not** hardened to this level and should not be deployed.
