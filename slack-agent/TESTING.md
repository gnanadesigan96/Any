# Test run (before going live)

The bot has a **test mode** that squeezes the month into about 1.5 hours. It
uses its own config (`config/workflow.test.json`) and its own database, so
production settings and data are untouched.

| Real time after you start the bot | Bot pretends it is | What happens |
|---|---|---|
| 0 min | **17 Oct, 10:00** | `[TEST]` reminder in the test support channel. The window is open for 21 Sep – 20 Oct. |
| 0–60 min | 17th → 19th | Members submit fake data. Flagged entries go to the review in the same channel, for Gnanadesigan. |
| 60 min | **19 Oct, 10:00** | `[TEST]` "Last day" reminder. |
| 90 min | **19 Oct, EOD** | `[TEST]` "window is closed" message. From now on, anyone who submits gets *"The window is closed. The next window opens on 17 November…"*. |
| after close | – | If flags are still undecided, Gnanadesigan is reminded and the final table waits. Once all are decided, the **summary + details + CSV** go to the test approval channel and **Manoj** is tagged with *Approve / Raise concern*. |
| Manoj approves | – | **Vijay** is tagged: support incentive data for 21 Sep – 20 Oct is approved, with the tables and CSV. |

Every scheduled message says the real time the next step happens (e.g. *"that's
about 4:30 PM real time today"*). The bot also logs the timeline when it starts.

## 1. Test config (`config/workflow.test.json`) - already filled in

| Role | Who | Setting |
|---|---|---|
| Support channel + flag review | `#support-test` | `collection_channel`, `review_channel` |
| Final approval + HR | `#support-approval-test` | `approval_channel` (`hr_channel` = same) |
| Reviewer | Gnanadesigan | `U0C2TN3B562` |
| Final approver (test) | Manoj | `U0BP446DWBD` |
| HR (test) | Vijay | `U0C2TN3CC06` |

The bot refuses to start while any `REPLACE-…` value is left.

## 2. Slack app (one-time)

Create the app from `manifest.yaml` (see README → Setup), install it, then
`/invite @ops-agent` into **both** test channels. Members of channel 1: you and
the two teammates. Members of channel 2: you, Manoj and Vijay.

## 3. Start the test

```bash
cd slack-agent
pip install -r requirements.txt
set -a; source .env; set +a                  # SLACK_BOT_TOKEN, SLACK_APP_TOKEN, ANTHROPIC_API_KEY
WORKFLOW_CONFIG_PATH=config/workflow.test.json python app.py
```

Keep it running for the whole test, on a laptop that won't sleep or on a
server. If it restarts, the pretend clock carries on where it was. **To run the
test again from the start**, stop the bot and delete `test_support_allowance.db`.

## 4. What to try (fake data)

Ask the two teammates (A and B) to do these in channel 1 during the first hour:

| # | Who | Message to the bot | Expected |
|---|---|---|---|
| 1 | A | `@ops-agent night shift 3 and 4 Oct, day shift 11 Oct, on 11th also did the DB failover` | A table with 3 rows, *Recorded*, no amounts |
| 2 | B | `@ops-agent day shift 6 Oct, night shift 12 Oct` | Table, *Recorded* |
| 3 | A | `@ops-agent night shift 18, 19 and 20 Oct` | Recorded (inside the period, submitted in advance) |
| 4 | B | `@ops-agent day shift 22 Oct` | **Flagged**: after the period. Accept/Reject appears for Gnanadesigan |
| 5 | B | `@ops-agent day shift 15 Sep` | **Flagged**: before the period |
| 6 | B | `@ops-agent night shift 3 Oct` | **Flagged overlap** with A's night shift. A is told in their thread, and *both* rows appear for review |
| 7 | B | `@ops-agent on 4 Oct I took a night call (no shift)` | Recorded, no flag (extra tasks may overlap) |
| 8 | A | `@ops-agent night shift 3 Oct` again | "already submitted" |
| 9 | A | `@ops-agent remove my 4 Oct night shift` | Updated table |
| 10 | A | `@ops-agent show my details` / `when does the window close?` | Own table / deadline |
| 11 | Gnanadesigan | Click **Accept** / **Reject** on the flagged rows | Row updates in place; the member is told in their thread |
| 12 | A | after the 90-min mark: `@ops-agent day shift 10 Oct` | *"Window is closed… next window opens 17 November"*, nothing recorded |
| 13 | Manoj | Click **Raise concern**, pick a row, write a concern | The interactive table appears in the thread for Gnanadesigan |
| 14 | Gnanadesigan | ⋮ **Edit** / **Remove** a row, **Add entry**, then **Respond & send for approval** | Table updates in place; Manoj gets the updated tables + your response |
| 15 | B / Vijay | Click Approve / Accept | Private "only X can do this" |
| 16 | Manoj | **Approve** | Vijay tagged with the 21 Sep – 20 Oct data |
| 17 | Gnanadesigan | `@ops-agent compare with last month and show the trend` | Comparison tables + explanation (September will be empty in the test) |
| 18 | A | the same comparison question | Only A's own counts, no amounts |

Check the amounts in the approval table by hand against the rates. For example,
a day shift on 2 Oct (Gandhi Jayanti, weekday holiday) = ₹1,000; a night shift
on a Saturday = ₹500; +₹500 per extra task.

## 5. Going live

1. Fill in `config/workflow.json` (production): real channels, `reviewer`
   (Gnanadesigan, already set), `approver` (Poornodhaya, already set), the HR group or HR
   people, and your festival holidays in `config/allowance_policy.json`.
2. Invite the bot to the production channels.
3. Start **without** `WORKFLOW_CONFIG_PATH`: `python app.py`. It uses
   `config/workflow.json`, the real clock and `support_allowance.db`. The test
   database is not used.
