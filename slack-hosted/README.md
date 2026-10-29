# Ops Agent: Slack-hosted ("Run on Slack") version

The same monthly support-allowance bot as `../slack-agent`, rebuilt to run **on Slack's own
servers**. No laptop, server or database file is involved: Slack runs the code, the schedule and
the storage. Your Business+ plan includes this.

What it does is unchanged:
- **Collection:** reminders on the 17th and 19th, and the window closes at 19th EOD IST. People
  @mention the bot with their days and get a table back without amounts.
- **Flags:** dates outside **21st → 20th**, and day/night shifts that overlap someone else's, go to
  the reviewer with **Accept / Reject** buttons.
- **Approval:** the final tables (with amounts) go to the approver with **Approve / Raise
  concern**. A concern comes back to the reviewer as an editable table. Approval tags HR.
- **Nudges:** whoever a step is waiting on is re-tagged every 2 hours, at most 3 times, and not
  between 21:00 and 09:00.
- **Comparisons and trends:** only for the people in `analyticsUsers`, shown "only visible to you".
- **Least privilege:** the bot only acts in the configured channels. It has no delete, file,
  reaction or DM permissions. It can call no outside service except the Claude API.

## How it's built

| Piece | File |
|---|---|
| Settings: channels, people, rates, holidays, test vs production | `config/settings.ts` |
| Mention → Claude agent → reply in the thread | `functions/handle_mention.ts`, `lib/agent.ts` |
| Schedule: reminders, closing, nudges | `functions/scheduler.ts`, `lib/engine.ts` |
| Buttons and forms | `lib/handlers.ts`, `lib/blocks.ts` |
| Storage (Slack datastores) | `datastores/datastores.ts`, `lib/store.ts` |
| Triggers | `triggers/` (mention per channel set, 2-hourly schedule, test timeline) |

**Run on Slack details:**
- **Buttons:** they only work while the run that posted them is still in progress. The bot keeps a
  run open until its buttons are no longer needed, then completes it.
- **Time limits:** a mention has 60 seconds to answer and a button click has 10 seconds. To fit,
  Claude runs at low effort with a 50-second budget, and button handlers only do quick work.
- **Schedule:** Slack schedules can't say "on the 17th", so one schedule runs **every 2 hours** and
  checks what's due. That's about 360 runs a month, plus one run per @mention.
- **Calling Claude:** it uses plain HTTPS (`api.anthropic.com`, declared in `manifest.ts`). Slack's
  bundler isn't guaranteed to handle npm packages.

## One-time setup on your Mac

1. **Install the Slack CLI** (it also installs Deno):
   ```bash
   curl -fsSL https://downloads.slack-edge.com/slack-cli/install.sh | bash
   ```
2. **Log in:** run `slack login`. It prints a `/slackauthticket …` command. Paste that into any
   Slack message box in the BetterCloud + CoreStack workspace, send it, and confirm in the
   terminal.
3. **Remove the old self-hosted "Ops Agent" app** you created on api.slack.com, so there aren't two
   bots with the same name. Do this at api.slack.com → Your Apps → Ops Agent → Basic Information
   → Delete App.

## Test run (about 2.5 hours, using #support-test and #support-approval-test)

Test settings are already filled in: Gnanadesigan reviews, Manoj approves and also stands in for
Uday, and Vijay is HR.

```bash
cd ~/Any && git pull
cd slack-hosted
slack deploy                                   # choose the BetterCloud + CoreStack workspace
slack env add APP_MODE test
slack env add ANTHROPIC_API_KEY sk-ant-...     # your key
```
- If `slack deploy` says the app needs **admin approval**, wait for a Slack admin to approve it,
  then run `slack deploy` again.
- After deploying, in Slack run `/invite @Ops Agent` in **#support-test** and
  **#support-approval-test**.

Then create the triggers:
```bash
slack trigger create --trigger-def triggers/mention_test.ts
for f in triggers/test/*.ts; do slack trigger create --trigger-def "$f"; done
```

The second command starts the clock. Each step runs once, counting from when you create it:

| After | Bot pretends it is | What you should see |
|---|---|---|
| 1 min | 17 Oct 10:00 | `[TEST]` reminder in #support-test |
| 61 min | 19 Oct 10:00 | `[TEST]` "Last day" reminder |
| 91 min | 19 Oct EOD | Window closed. Either flags are waiting for you, or the final table goes to Manoj |
| 101–141 min | (time runs on) | Nudges every 10 minutes while something is waiting (max 3) |

During the first hour, follow the scenarios in `../slack-agent/TESTING.md`. They're the same
here, except that there's no CSV. To watch what the bot is doing, run `slack activity --tail`.

**To run the test again:** in #support-test, Gnanadesigan says *"@Ops Agent reset test data"*.
This archives everything; nothing is deleted. Then create the `triggers/test/*` triggers again.

## Going live (production)

1. Send me, or fill in `PRODUCTION` in `config/settings.ts`:
   - the production support channel ID and approval channel ID
   - Poornodhaya's member ID
   - HR: a user-group ID (`S…`) or member IDs
   - Uday's member ID
   - the festival holidays, in `RATES.holidays`
2. In #support-test, say *"@Ops Agent reset test data"* so test records don't count.
3. Remove the test triggers: run `slack trigger list`, then
   `slack trigger delete --trigger-id <id>` for each one starting with "TEST" and the
   "(test)" mention trigger.
4. Switch to production and deploy:
   ```bash
   slack env remove APP_MODE
   slack deploy
   slack trigger create --trigger-def triggers/mention_production.ts
   slack trigger create --trigger-def triggers/schedule_production.ts
   ```
5. `/invite @Ops Agent` in the production channels.

**Model:** `slack env add AGENT_MODEL <model id>` overrides the default `claude-opus-5-5`.
`AGENT_EFFORT` overrides the default `low`. If replies ever time out, a faster setting helps.

## Developing

```bash
deno task test      # unit + flow tests (in-memory storage, fake Slack client)
deno task check     # type-check against the Slack SDK
```
