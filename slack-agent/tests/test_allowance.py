import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import workflow  # noqa: E402
from agent.config import Policy, Workflow  # noqa: E402
from agent.context import RequestContext, current_request  # noqa: E402
from agent.report import final_report  # noqa: E402
from agent.store import Store  # noqa: E402
from agent.tools import support_allowance as tools  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")
POLICY = Policy.load()  # the real config/allowance_policy.json


def ist(y, m, d, hh=0, mm=0, ss=0):
    return datetime(y, m, d, hh, mm, ss, tzinfo=IST)


class FakeSlack:
    def __init__(self):
        self.posts, self.updates, self.files, self.ephemeral = [], [], [], []

    def chat_postMessage(self, **kw):
        self.posts.append(kw)
        return {"channel": kw["channel"], "ts": f"{len(self.posts)}.000"}

    def chat_update(self, **kw):
        self.updates.append(kw)

    def files_upload_v2(self, **kw):
        self.files.append(kw)

    def users_info(self, user):
        return {"user": {"real_name": {"UPRIYA": "Priya Kumar", "UARUN": "Arun"}.get(user, user)}}

    def texts(self, channel=None):
        return [p["text"] for p in self.posts if channel is None or p["channel"] == channel]


CFG = Workflow(
    tz=IST, collection_channel="CSUPPORT", approval_channel="CAPPROVAL", hr_channel="CAPPROVAL",
    approvers=frozenset({"UBOSS"}), hr_group="SHR", hr_users=(),
    reminder=(17, time(10, 0)), closing_reminder=(19, time(10, 0)), close=(19, time(23, 59)),
)


class Clock:
    def __init__(self, dt):
        self.dt = dt


@pytest.fixture
def wf(tmp_path):
    slack = FakeSlack()
    w = workflow.SupportWorkflow(slack, Store(tmp_path / "s.db"), CFG, "UBOT")
    clock = Clock(ist(2026, 10, 18, 12))
    w.now = lambda: clock.dt
    w.clock = clock
    workflow.set_instance(w)
    yield w
    workflow.set_instance(None)


def as_user(user_id, name, fn, **kwargs):
    ctx = RequestContext(user_id, name, "CSUPPORT")
    token = current_request.set(ctx)
    try:
        return json.loads(fn.call(kwargs)), ctx.attachments
    finally:
        current_request.reset(token)


# -- rates --------------------------------------------------------------------

@pytest.mark.parametrize("day,shift,extra,expected,day_type", [
    ("2026-10-01", "day", False, 500, "weekday"),     # Thu
    ("2026-10-03", "day", False, 1000, "weekend"),    # Sat
    ("2026-10-02", "day", False, 1000, "holiday"),    # Gandhi Jayanti, Fri
    ("2026-10-01", "night", False, 1000, "weekday"),
    ("2026-10-03", "night", False, 500, "weekend"),
    ("2026-08-15", "day", False, 1000, "weekend"),    # holiday on a Saturday counts as weekend
    ("2026-10-01", "day", True, 1000, "weekday"),     # +500 extra task
    ("2026-10-01", "none", True, 500, "weekday"),     # extra task only
])
def test_rates(day, shift, extra, expected, day_type):
    a = POLICY.amount(date.fromisoformat(day), shift, extra)
    assert (a["total"], a["day_type"]) == (expected, day_type)


def test_final_report_totals():
    entries = [
        {"person_id": "UPRIYA", "person_name": "Priya Kumar", "support_date": "2026-10-01", "shift": "night", "extra_task": None},
        {"person_id": "UPRIYA", "person_name": "Priya Kumar", "support_date": "2026-10-03", "shift": "day", "extra_task": "DB failover"},
        {"person_id": "UARUN", "person_name": "Arun", "support_date": "2026-10-02", "shift": "day", "extra_task": None},
    ]
    r = final_report(entries, POLICY)
    assert r["grand_total"] == 1000 + 1500 + 1000
    assert "Priya Kumar | 1          | 1            | 1           | ₹2,500" in r["summary"]
    assert "DB failover" in r["csv"]


# -- window timing ------------------------------------------------------------

def test_submission_cycle_rolls_over_after_19th_eod(wf):
    assert wf.submission_cycle(ist(2026, 10, 19, 23, 59, 59)) == "2026-10"
    assert wf.submission_cycle(ist(2026, 10, 20, 0, 0)) == "2026-11"
    assert wf.submission_cycle(ist(2026, 12, 25)) == "2027-01"


# -- full month ---------------------------------------------------------------

def test_full_monthly_flow(wf):
    slack = wf.client

    wf.tick(ist(2026, 10, 17, 9, 59))
    assert slack.posts == []
    wf.tick(ist(2026, 10, 17, 10, 0))
    wf.tick(ist(2026, 10, 17, 10, 1))
    assert len(slack.texts("CSUPPORT")) == 1
    assert "October 2026" in slack.posts[0]["text"] and "19 October, 11:59 PM IST" in slack.posts[0]["text"]

    # Priya submits; she gets a table back with no amounts.
    wf.clock.dt = ist(2026, 10, 18, 15)
    out, attached = as_user("UPRIYA", "Priya Kumar", tools.submit_support_details, entries=[
        {"date": "2026-10-03", "shift": "night"},
        {"date": "2026-10-02", "shift": "day", "extra_task": "Patched prod cluster"},
        {"date": "2026-10-25", "shift": "day"},
    ])
    assert out["added"] == 2 and "future" in out["problems"][0]
    table = "\n".join(attached)
    assert "Night" in table and "Holiday (Gandhi Jayanti)" in table and "Patched prod cluster" in table
    assert "₹" not in table and "1000" not in table

    # Re-submitting the same day is rejected.
    out, _ = as_user("UPRIYA", "Priya Kumar", tools.submit_support_details, entries=[{"date": "2026-10-03", "shift": "night"}])
    assert out["added"] == 0 and out["already_submitted"]

    # A team lead submits for Arun.
    out, _ = as_user("UPRIYA", "Priya Kumar", tools.submit_support_details,
                     entries=[{"date": "2026-10-05", "shift": "day"}], person_slack_id="UARUN")
    assert out["person"] == "Arun"

    wf.tick(ist(2026, 10, 19, 10, 0))
    assert "Last day" in slack.texts("CSUPPORT")[-1]

    # Window closes at 19th EOD IST -> tables + approval request with buttons.
    wf.tick(ist(2026, 10, 19, 23, 59, 30))
    assert not slack.texts("CAPPROVAL")
    wf.tick(ist(2026, 10, 20, 0, 0))
    approval_texts = "\n".join(slack.texts("CAPPROVAL"))
    # Priya: night on Sat 500 + day on holiday 1000 + extra task 500; Arun: weekday day 500
    assert "<@UBOSS>" in approval_texts and "total *₹2,500*" in approval_texts
    assert slack.files and slack.files[0]["filename"] == "support-allowance-2026-10.csv"
    button_post = [p for p in slack.posts if p.get("blocks")][-1]
    assert {e["action_id"] for e in button_post["blocks"][1]["elements"]} == {workflow.APPROVE_ACTION, workflow.REJECT_ACTION}
    assert "closed" in slack.texts("CSUPPORT")[-1]

    # Late submission goes to November.
    wf.clock.dt = ist(2026, 10, 21, 9)
    out, _ = as_user("UARUN", "Arun", tools.submit_support_details, entries=[{"date": "2026-10-20", "shift": "night"}])
    assert out["cycle"] == "November 2026" and out["note"]

    # Only the approver can approve, and only once.
    assert wf.approve("2026-10", "UPRIYA") == "not_authorised"
    assert wf.approve("2026-10", "UBOSS") == "approved"
    assert wf.approve("2026-10", "UBOSS") == "approved"
    hr_posts = [t for t in slack.texts("CAPPROVAL") if "<!subteam^SHR>" in t]
    assert len(hr_posts) == 1 and "approved by <@UBOSS>" in hr_posts[0]
    assert "approved" in slack.updates[-1]["text"]

    # Approved month is locked.
    out, _ = as_user("UBOSS", "Boss", tools.submit_support_details, entries=[{"date": "2026-10-06", "shift": "day"}], cycle="2026-10")
    assert "locked" in out["error"]


def test_send_back_fix_and_resend(wf):
    wf.clock.dt = ist(2026, 10, 18, 12)
    as_user("UARUN", "Arun", tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])
    assert as_user("UARUN", "Arun", tools.close_window_now)[0]["error"]
    assert as_user("UBOSS", "Boss", tools.close_window_now)[0]["status"] == "pending_approval"

    assert wf.reject("2026-10", "UBOSS") == "rejected"
    assert "tell me in this thread" in wf.client.posts[-1]["text"]

    out, _ = as_user("UBOSS", "Boss", tools.submit_support_details,
                     entries=[{"date": "2026-10-06", "shift": "night"}], person_slack_id="UARUN", cycle="2026-10")
    assert out["added"] == 1
    out, _ = as_user("UBOSS", "Boss", tools.remove_support_details, dates=["2026-10-05"], person_slack_id="UARUN", cycle="2026-10")
    assert out["removed"] == 1

    assert as_user("UBOSS", "Boss", tools.resend_for_approval, cycle="2026-10")[0]["status"] == "pending_approval"
    assert "₹1,000" in "\n".join(wf.client.texts("CAPPROVAL")[-6:])
    assert wf.approve("2026-10", "UBOSS") == "approved"


def test_members_only_see_their_own(wf):
    as_user("UARUN", "Arun", tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])
    assert "error" in as_user("UPRIYA", "Priya Kumar", tools.show_support_details, person_slack_id="UARUN")[0]
    out, attached = as_user("UBOSS", "Boss", tools.show_support_details)
    assert out["total"] == "₹500" and any("Arun" in a for a in attached)


def test_quiet_month_without_reminder_is_not_announced(wf):
    # First deploy on 25 Oct: don't post a "nothing submitted" message for September/October retroactively.
    wf.tick(ist(2026, 10, 25, 12))
    assert wf.client.posts == []
