import json
import sys
from datetime import date, datetime, time
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent import blocks as B  # noqa: E402
from agent import slack_actions, workflow  # noqa: E402
from agent.config import Policy, Workflow  # noqa: E402
from agent.context import RequestContext, current_request  # noqa: E402
from agent.report import final_report  # noqa: E402
from agent.store import Store  # noqa: E402
from agent.tools import support_allowance as tools  # noqa: E402

IST = ZoneInfo("Asia/Kolkata")
POLICY = Policy.load()  # the real config/allowance_policy.json
ME, BOSS, PRIYA, ARUN, UDAY = "UGNANA", "UBOSS", "UPRIYA", "UARUN", "UUDAY"


def ist(y, m, d, hh=0, mm=0, ss=0):
    return datetime(y, m, d, hh, mm, ss, tzinfo=IST)


class FakeSlack:
    def __init__(self):
        self.posts, self.updates, self.files, self.ephemeral, self.views = [], [], [], [], []

    def chat_postMessage(self, **kw):
        self.posts.append(kw)
        return {"channel": kw["channel"], "ts": f"{len(self.posts)}.000"}

    def chat_update(self, **kw):
        self.updates.append(kw)

    def chat_postEphemeral(self, **kw):
        self.ephemeral.append(kw)

    def views_open(self, **kw):
        self.views.append(kw["view"])

    def users_info(self, user):
        return {"user": {"real_name": {PRIYA: "Priya Kumar", ARUN: "Arun", ME: "Gnanadesigan", BOSS: "Poornodhaya"}.get(user, user)}}

    def texts(self, channel=None):
        return [p["text"] for p in self.posts if channel is None or p["channel"] == channel]

    def with_blocks(self, channel=None):
        return [p for p in self.posts if p.get("blocks") and (channel is None or p["channel"] == channel)]


CFG = Workflow(
    tz=IST, collection_channel="CSUPPORT", approval_channel="CAPPROVAL", hr_channel="CAPPROVAL",
    reviewer=ME, approver=BOSS, hr_group="SHR", hr_users=(), period_start_day=21, period_end_day=20,
    reminder=(17, time(10, 0)), closing_reminder=(19, time(10, 0)), close=(19, time(23, 59)),
    analytics_users=(UDAY,),
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


def as_user(user_id, fn, channel="CSUPPORT", **kwargs):
    ctx = RequestContext(user_id, FakeSlack().users_info(user_id)["user"]["real_name"], channel, f"t-{user_id}")
    token = current_request.set(ctx)
    try:
        return json.loads(fn.call(kwargs)), ctx.attachments
    finally:
        current_request.reset(token)


def action_ids(blocks):
    ids = set()
    for b in blocks:
        for el in b.get("elements", []):
            if el.get("action_id"):
                ids.add(el["action_id"])
        if b.get("accessory"):
            ids.add(b["accessory"]["action_id"])
    return ids


# -- rates and periods --------------------------------------------------------

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


def test_period_is_21st_to_20th(wf):
    assert CFG.period("2026-10") == (date(2026, 9, 21), date(2026, 10, 20))
    assert CFG.period("2026-01") == (date(2025, 12, 21), date(2026, 1, 20))
    assert wf.flag_reason("2026-10", date(2026, 9, 20)).startswith("before")
    assert wf.flag_reason("2026-10", date(2026, 9, 21)) is None
    assert wf.flag_reason("2026-10", date(2026, 10, 20)) is None
    assert wf.flag_reason("2026-10", date(2026, 10, 21)).startswith("after")


def test_configs_require_ids_and_restrict_channels():
    import dataclasses
    prod = Workflow.load()
    assert prod.reviewer == "U0C2TN3B562" and prod.period_text("2026-10") == "21 Sep 2026 - 20 Oct 2026"
    assert any(p.startswith("approver") for p in prod.problems())   # Poornodhaya's member ID still to fill in
    test = Workflow.load(Path(__file__).resolve().parent.parent / "config" / "workflow.test.json")
    assert (test.reviewer, test.approver, test.hr_users) == ("U0C2TN3B562", "U0BP446DWBD", ("U0C2TN3CC06",))
    assert test.analytics_users == ("U0BP446DWBD",)   # Manoj stands in for Uday in the test
    assert test.problems() == [] and test.allowed_channels == {"C0CCS25TRPU", "C0CCLUWT7JR"}
    assert (test.collection_channel, test.review_target, test.approval_channel, test.hr_channel) == (
        "C0CCS25TRPU", "C0CCS25TRPU", "C0CCLUWT7JR", "C0CCLUWT7JR")
    filled = dataclasses.replace(test, collection_channel="C0SUPPORT1", review_channel="C0SUPPORT1",
                                 approval_channel="C0APPROVE1", hr_channel="C0APPROVE1")
    assert filled.problems() == []
    assert filled.allowed_channels == {"C0SUPPORT1", "C0APPROVE1"}
    assert dataclasses.replace(filled, approver="manoj@corestack.io").problems()        # e-mails rejected
    assert dataclasses.replace(filled, approval_channel="#support-approval-test").problems()  # names rejected
    assert dataclasses.replace(filled, review_channel=None).review_target == "C0SUPPORT1"


def test_submission_cycle_rolls_over_after_19th_eod(wf):
    assert wf.submission_cycle(ist(2026, 10, 19, 23, 59, 59)) == "2026-10"
    assert wf.submission_cycle(ist(2026, 10, 20, 0, 0)) == "2026-11"


def test_final_report_marks_accepted_out_of_period():
    entries = [
        {"person_id": PRIYA, "person_name": "Priya Kumar", "support_date": "2026-10-01", "shift": "night", "extra_task": None, "review": None},
        {"person_id": PRIYA, "person_name": "Priya Kumar", "support_date": "2026-09-12", "shift": "day", "extra_task": "DB failover", "review": "accepted",
         "flag_reason": "before the period (21 Sep 2026 - 20 Oct 2026)"},
    ]
    r = final_report(entries, POLICY)
    assert r["grand_total"] == 1000 + 1500
    assert "Accepted: before the period" in r["detail"] and "Accepted by reviewer: before the period" in r["csv"]


# -- the whole month ----------------------------------------------------------

def test_full_month_with_review_concern_and_approval(wf):
    slack = wf.client
    wf.tick(ist(2026, 10, 17, 10, 0))
    assert "21 Sep 2026 - 20 Oct 2026" in slack.posts[0]["text"]

    # Priya submits: one date before the period gets flagged; the 20th (in period) is fine even though it's tomorrow+.
    out, attached = as_user(PRIYA, tools.submit_support_details, entries=[
        {"date": "2026-10-03", "shift": "night"},
        {"date": "2026-10-02", "shift": "day", "extra_task": "Patched prod cluster"},
        {"date": "2026-09-15", "shift": "night"},
        {"date": "2026-10-20", "shift": "day"},
    ])
    assert out["added"] == 4 and len(out["flagged_for_reviewer"]) == 1
    table = "\n".join(attached)
    assert "Awaiting review" in table and "₹" not in table

    review_msg = slack.with_blocks("CSUPPORT")[-1]
    assert action_ids(review_msg["blocks"]) == {B.REVIEW_ACCEPT, B.REVIEW_REJECT}
    flagged_id = B.row_ids(review_msg["blocks"])[0]

    as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])

    # Window closes; a flagged entry is still open, so the final table waits.
    wf.clock.dt = ist(2026, 10, 20, 0, 0)
    wf.tick(wf.clock.dt)
    assert wf.store.cycle("2026-10")["status"] == "reviewing"
    assert not slack.with_blocks("CAPPROVAL")
    assert "still need your decision" in slack.texts("CSUPPORT")[-2]

    # Only the reviewer can decide; deciding the last one releases the final table to the boss.
    assert wf.review(flagged_id, "accepted", PRIYA) == "not_authorised"
    assert wf.review(flagged_id, "accepted", ME) == "accepted"
    assert wf.review(flagged_id, "rejected", ME) == "already_decided"
    assert any("accepted* your night shift" in t for t in slack.texts("CSUPPORT"))
    assert wf.store.cycle("2026-10")["status"] == "pending_approval"
    approval = slack.with_blocks("CAPPROVAL")[-1]
    assert f"<@{BOSS}>" in approval["text"] and action_ids(approval["blocks"]) == {B.APPROVE, B.RAISE_CONCERN}
    # night Sat 500 + day holiday 1000 + extra 500 + night weekday (15 Sep, accepted) 1000 + day Tue 20 Oct 500 + Arun 500
    assert "total *₹4,000*" in approval["text"]

    # Boss raises a concern about Arun's entry -> interactive table for me in the thread.
    arun_id = wf.store.entries("2026-10", ARUN)[0]["id"]
    assert wf.raise_concern("2026-10", ME, "?") == "not_authorised"
    assert wf.raise_concern("2026-10", BOSS, "Arun was on leave on 5 Oct", [arun_id]) == "concern"
    concern = slack.posts[-1]
    assert concern["thread_ts"] == wf.store.cycle("2026-10")["approval_ts"] and concern["reply_broadcast"]
    assert f"<@{ME}>" in concern["text"] and B.CONCERN_ROW in action_ids(concern["blocks"])
    assert B.row_ids(concern["blocks"]) == [arun_id]

    # I fix it in the same table: Arun actually worked the 6th, night shift; I also add a missed entry.
    assert wf.edit_entry(arun_id, ME, "2026-10-06", "night", None) is None
    assert "Tue 06 Oct 2026 · Night" in json.dumps(slack.updates[-1]["blocks"], ensure_ascii=False)
    assert wf.add_entry("2026-10", ME, PRIYA, "2026-10-03", "night", None).startswith("Already claimed")
    assert wf.add_entry("2026-10", ME, ARUN, "2026-10-07", "day", "Cert rotation") is None
    assert len(B.row_ids(slack.updates[-1]["blocks"])) == 2

    assert wf.respond_to_concern("2026-10", BOSS, "x") == "not_authorised"
    assert wf.respond_to_concern("2026-10", ME, "Corrected Arun's dates as per roster") == "pending_approval"
    reapproval = slack.with_blocks("CAPPROVAL")[-1]
    assert "Corrected Arun's dates" in json.dumps(reapproval["blocks"]) and B.APPROVE in action_ids(reapproval["blocks"])

    # Final approval -> HR tagged once.
    assert wf.approve("2026-10", ME) == "not_authorised"
    assert wf.approve("2026-10", BOSS) == "approved"
    assert wf.approve("2026-10", BOSS) == "approved"
    hr = [t for t in slack.texts("CAPPROVAL") if "<!subteam^SHR>" in t]
    assert len(hr) == 1 and f"approved by <@{BOSS}>" in hr[0]

    # Approved month is locked.
    assert "approved" in wf.add_entry("2026-10", ME, ARUN, "2026-10-08", "day", None)


def test_rejected_entry_is_not_paid_and_can_be_claimed_again(wf):
    out, _ = as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-09-01", "shift": "day"},
                                                                   {"date": "2026-10-01", "shift": "day"}])
    flagged = wf.store.pending_reviews("2026-10")[0]
    as_user(ME, tools.review_flagged_entries, decision="rejected")
    assert wf.store.entry(flagged["id"])["review"] == "rejected"
    assert [e["support_date"] for e in wf.store.entries("2026-10", payable_only=True)] == ["2026-10-01"]
    assert wf.store.duplicate_of(PRIYA, "2026-09-01", "day") is None


def test_members_only_see_their_own_and_no_money(wf):
    as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])
    assert "error" in as_user(PRIYA, tools.show_support_details, person_slack_id=ARUN)[0]
    out, attached = as_user(BOSS, tools.show_support_details, channel="CAPPROVAL")
    assert out["total"] == "₹500" and any("Arun" in a for a in attached)
    # The same request in the team channel shows everyone's details but no money.
    out, attached = as_user(BOSS, tools.show_support_details)
    assert "₹" not in "\n".join(attached) and any("Arun" in a for a in attached) and out["amounts_hidden"]
    assert "error" in as_user(PRIYA, tools.close_window_now)[0]
    assert "error" in as_user(PRIYA, tools.remove_support_details, dates=["2026-10-05"], person_slack_id=ARUN)[0]


def test_quiet_month_without_reminder_is_not_announced(wf):
    wf.tick(ist(2026, 10, 25, 12))
    assert wf.client.posts == []


# -- button and modal handlers -------------------------------------------------

class FakeApp:
    def __init__(self):
        self.handlers = {}

    def action(self, action_id):
        return lambda fn: self.handlers.setdefault(action_id, fn)

    def view(self, callback_id):
        return lambda fn: self.handlers.setdefault(callback_id, fn)


class Ack:
    def __init__(self):
        self.calls = []

    def __call__(self, **kw):
        self.calls.append(kw)


def test_buttons_and_modals(wf):
    app = FakeApp()
    slack_actions.register(app)
    h, slack = app.handlers, wf.client

    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-09-01", "shift": "night"},
                                                          {"date": "2026-10-01", "shift": "day"}])
    msg = slack.with_blocks("CSUPPORT")[-1]
    flagged_id = B.row_ids(msg["blocks"])[0]

    def click(user, action, value=None, **extra):
        body = {"user": {"id": user}, "channel": {"id": msg["channel"]}, "trigger_id": "trig",
                "message": {"ts": msg_ts, "blocks": msg["blocks"]}, "actions": [{"value": value, **extra}]}
        h[action](ack=Ack(), body=body, client=slack)

    msg_ts = "x.1"
    click(PRIYA, B.REVIEW_ACCEPT, str(flagged_id))
    assert "Only" in slack.ephemeral[-1]["text"] and wf.store.entry(flagged_id)["review"] == "pending"
    click(ME, B.REVIEW_ACCEPT, str(flagged_id))
    assert wf.store.entry(flagged_id)["review"] == "accepted"
    assert "Accepted" in json.dumps(slack.updates[-1]["blocks"], ensure_ascii=False) and B.REVIEW_ACCEPT not in action_ids(slack.updates[-1]["blocks"])

    wf.close_cycle("2026-10")
    click(PRIYA, B.RAISE_CONCERN, "2026-10")
    assert not slack.views
    click(BOSS, B.RAISE_CONCERN, "2026-10")
    assert slack.views[-1]["callback_id"] == B.CONCERN_MODAL

    view = {"private_metadata": json.dumps({"cid": "2026-10"}), "state": {"values": {
        "entries": {"v": {"selected_options": []}}, "concern": {"v": {"value": "Why the September night shift?"}}}}}
    h[B.CONCERN_MODAL](ack=Ack(), body={"user": {"id": BOSS}}, view=view)
    assert wf.store.cycle("2026-10")["status"] == "concern"

    # Edit via the row menu -> modal -> a duplicate is reported inline on the form.
    click(ME, B.CONCERN_ROW, selected_option={"value": f"edit:{flagged_id}"})
    assert slack.views[-1]["callback_id"] == B.EDIT_MODAL
    edit_view = {"private_metadata": slack.views[-1]["private_metadata"], "state": {"values": {
        "date": {"v": {"selected_date": "2026-10-01"}}, "shift": {"v": {"selected_option": {"value": "day"}}},
        "extra": {"v": {"value": None}}}}}
    ack = Ack()
    h[B.EDIT_MODAL](ack=ack, body={"user": {"id": ME}}, view=edit_view)
    assert ack.calls[-1]["response_action"] == "errors"

    click(ME, B.CONCERN_ROW, selected_option={"value": f"remove:{flagged_id}"})
    assert wf.store.entry(flagged_id)["review"] == "removed"
    restore = [b for b in slack.updates[-1]["blocks"] if b.get("block_id") == f"row:{flagged_id}"][0]["accessory"]
    assert restore["type"] == "button" and restore["value"] == f"restore:{flagged_id}"
    click(ME, B.CONCERN_ROW, f"restore:{flagged_id}")
    assert wf.store.entry(flagged_id)["review"] == "accepted"
    click(ME, B.CONCERN_ROW, selected_option={"value": f"remove:{flagged_id}"})
    click(ME, B.CONCERN_RESPOND, "2026-10")
    assert slack.views[-1]["callback_id"] == B.RESPOND_MODAL
    h[B.RESPOND_MODAL](ack=Ack(), body={"user": {"id": ME}}, view={
        "private_metadata": json.dumps({"cid": "2026-10"}), "state": {"values": {"response": {"v": {"value": "Removed it"}}}}})
    assert wf.store.cycle("2026-10")["status"] == "pending_approval"
    assert "total *₹500*" in slack.with_blocks("CAPPROVAL")[-1]["text"]

    click(BOSS, B.APPROVE, "2026-10")
    assert wf.store.cycle("2026-10")["status"] == "approved"


# -- period edges and overlaps --------------------------------------------------

def test_18th_to_20th_can_be_submitted_in_advance_but_21st_is_flagged(wf):
    wf.clock.dt = ist(2026, 10, 17, 11)
    out, _ = as_user(PRIYA, tools.submit_support_details, entries=[
        {"date": d, "shift": "day"} for d in ("2026-10-18", "2026-10-19", "2026-10-20", "2026-10-21")])
    assert out["added"] == 4
    assert out["flagged_for_reviewer"] == ["2026-10-21 (after the period (21 Sep 2026 - 20 Oct 2026))"]


def test_same_shift_same_day_by_two_people_flags_both(wf):
    slack = wf.client
    out, _ = as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-03", "shift": "night"}])
    assert out["flagged_for_reviewer"] == []
    priya_id = wf.store.entries("2026-10", PRIYA)[0]["id"]

    out, _ = as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-03", "shift": "night"}])
    assert out["flagged_for_reviewer"] == ["2026-10-03 (overlaps with Priya Kumar's night shift)"]
    arun_id = wf.store.entries("2026-10", ARUN)[0]["id"]

    # Priya's earlier entry is pulled into review too, and she's told in her thread.
    assert wf.store.entry(priya_id)["review"] == "pending"
    assert "overlaps with Arun's night shift" == wf.store.entry(priya_id)["flag_reason"]
    assert any("Arun also claimed the night shift" in t for t in slack.texts("CSUPPORT"))
    review_msg = slack.with_blocks("CSUPPORT")[-1]
    assert sorted(B.row_ids(review_msg["blocks"])) == sorted([priya_id, arun_id])

    # Reviewer keeps Priya's, rejects Arun's.
    assert wf.review(priya_id, "accepted", ME) == "accepted"
    assert wf.review(arun_id, "rejected", ME) == "rejected"
    assert [e["person_id"] for e in wf.store.entries("2026-10", payable_only=True)] == [PRIYA]


def test_extra_tasks_and_different_shifts_may_overlap(wf):
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-03", "shift": "night"}])
    out, _ = as_user(ARUN, tools.submit_support_details, entries=[
        {"date": "2026-10-03", "shift": "day"},
        {"date": "2026-10-04", "shift": "none", "extra_task": "Night call for P1 incident"},
    ])
    as_user(PRIYA, tools.submit_support_details, entries=[
        {"date": "2026-10-04", "shift": "none", "extra_task": "Same night call"}])
    assert out["flagged_for_reviewer"] == []
    assert wf.store.pending_reviews("2026-10") == []


def test_overlap_within_one_message_for_two_people_and_reviewer_edits_blocked(wf):
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}], person_slack_id=ARUN)
    assert len(wf.store.pending_reviews("2026-10")) == 2
    # The reviewer can't create a new overlap by hand.
    as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-06", "shift": "night"}])
    wf.store.update_cycle("2026-10", status="concern")
    err = wf.add_entry("2026-10", ME, PRIYA, "2026-10-06", "night", None)
    assert "overlaps with Arun's night shift" in err


# -- comparisons and trends -------------------------------------------------------

def _seed_two_months(wf):
    wf.clock.dt = ist(2026, 9, 18, 12)
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-09-05", "shift": "night"},   # Sat 500
                                                          {"date": "2026-09-08", "shift": "day"}])    # Tue 500
    as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-09-09", "shift": "night"}])   # Wed 1000
    wf.close_cycle("2026-09")
    wf.approve("2026-09", BOSS)
    wf.clock.dt = ist(2026, 10, 18, 12)
    as_user(PRIYA, tools.submit_support_details, entries=[
        {"date": "2026-10-02", "shift": "day", "extra_task": "Prod patch"},                            # holiday 1000 + 500
        {"date": "2026-10-03", "shift": "night"}, {"date": "2026-10-06", "shift": "night"}])           # 500 + 1000
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-07", "shift": "day"}],
            person_slack_id="UNEW")                                                                    # 500
    wf.close_cycle("2026-10")


def _ask(user, fn, channel="CAPPROVAL", **kw):
    ctx = RequestContext(user, user, channel, "t-1")
    token = current_request.set(ctx)
    try:
        return json.loads(fn.call(kw)), ctx
    finally:
        current_request.reset(token)


def test_comparison_for_uday_is_complete_and_private(wf):
    _seed_two_months(wf)
    out, ctx = _ask(UDAY, tools.compare_support_months)
    assert ctx.private_reply == {"user": UDAY} and out["delivered_privately"]
    assert (out["earlier"]["label"], out["later"]["label"]) == ("September 2026", "October 2026")
    assert (out["earlier"]["total"], out["later"]["total"]) == (2000, 3500)
    assert out["later"]["holiday_shifts"] == 1 and out["later"]["extra_tasks"] == 1
    assert "2026-10-02 Gandhi Jayanti" in out["later"]["holidays_in_period"]
    assert out["biggest_person_changes"][0]["name"] == "Priya Kumar"   # +2000
    text = "\n".join(ctx.attachments)
    assert "₹2,000" in text and "₹3,500" in text and "+₹1,500 (+75%)" in text
    assert "Arun" in text and "not in October" in text and "UNEW" in text and "new" in text
    assert "₹1,000 → ₹3,000" in text and "+0%" not in text


@pytest.mark.parametrize("who,channel", [(BOSS, "CAPPROVAL"), (ME, "CAPPROVAL"), (ME, "CSUPPORT"), (PRIYA, "CSUPPORT")])
def test_comparison_denied_for_everyone_else(wf, who, channel):
    _seed_two_months(wf)
    out, ctx = _ask(who, tools.compare_support_months, channel=channel)
    assert out["no_access"] and "don't have access" in out["message"]
    assert ctx.attachments == [] and ctx.private_reply == {}


def test_trend_over_several_months(wf):
    _seed_two_months(wf)
    out, ctx = _ask(UDAY, tools.compare_support_months, channel="CSUPPORT", trend_months=4)
    assert [t["label"] for t in out["trend"]] == ["July 2026", "August 2026", "September 2026", "October 2026"]
    assert "Trend - last 4 months" in "\n".join(ctx.attachments)


def test_private_delivery_is_only_visible_to_requester():
    from agent.delivery import deliver
    slack = FakeSlack()
    ctx = RequestContext(UDAY, "Uday", "CAPPROVAL", "t-9", private_reply={"user": UDAY})
    deliver(slack, ctx, "CAPPROVAL", "t-9", ["Here is the story", "```table ₹3,500```", ""])
    assert [(e["user"], e["channel"], e["thread_ts"], e["text"]) for e in slack.ephemeral] == [
        (UDAY, "CAPPROVAL", "t-9", "Here is the story"), (UDAY, "CAPPROVAL", "t-9", "```table ₹3,500```")]
    assert len(slack.posts) == 1 and "privately" in slack.posts[0]["text"] and slack.posts[0]["thread_ts"] == "t-9"
    assert "₹" not in slack.posts[0]["text"] and "table" not in slack.posts[0]["text"]
    assert not [p for p in slack.posts if p["channel"].startswith("U")]   # never a DM


def test_normal_replies_stay_in_thread():
    from agent.delivery import deliver
    slack = FakeSlack()
    deliver(slack, RequestContext(PRIYA, "Priya", "CSUPPORT", "t-1"), "CSUPPORT", "t-1", ["ok", "```t```"])
    assert [(p["channel"], p["thread_ts"]) for p in slack.posts] == [("CSUPPORT", "t-1")] * 2


# -- test mode: pretend clock and closed window -----------------------------------

from datetime import timedelta  # noqa: E402

from agent.config import PretendClock  # noqa: E402


def test_pretend_clock_maps_real_minutes_to_test_dates():
    tl = Workflow.load(Path(__file__).resolve().parent.parent / "config" / "workflow.test.json").test_timeline
    start = ist(2026, 10, 28, 15, 0)
    c = PretendClock(tl, start)
    assert c.at_real(start) == ist(2026, 10, 17, 10, 0)
    assert c.at_real(start + timedelta(minutes=60)) == ist(2026, 10, 19, 10, 0)
    assert c.at_real(start + timedelta(minutes=90)) == ist(2026, 10, 20, 0, 0)
    assert c.at_real(start + timedelta(minutes=100)) == ist(2026, 10, 20, 0, 10)
    assert c.real_for(ist(2026, 10, 20, 0, 0)) == start + timedelta(minutes=90)


def test_simulated_test_run_end_to_end(tmp_path):
    """Drive the real test timeline minute by minute: 17th reminder, 19th reminder, close, then 'window closed'."""
    import dataclasses
    tl = Workflow.load(Path(__file__).resolve().parent.parent / "config" / "workflow.test.json").test_timeline
    cfg = dataclasses.replace(CFG, test_timeline=tl, review_channel="CSUPPORT")
    w = workflow.SupportWorkflow(FakeSlack(), Store(tmp_path / "t.db"), cfg, "UBOT")
    start = datetime.fromisoformat(w.store.meta("test_started_at"))
    real = {"t": start}
    w.now = lambda: w.pretend_clock.at_real(real["t"]).astimezone(IST)
    workflow.set_instance(w)
    slack = w.client
    try:
        w.tick()
        assert "[TEST]" in slack.posts[0]["text"] and "Time to submit" in slack.posts[0]["text"]
        assert "real time today" in slack.posts[0]["text"]

        real["t"] = start + timedelta(minutes=20)        # pretend ~17th evening
        out, _ = as_user(PRIYA, tools.submit_support_details, entries=[
            {"date": "2026-10-03", "shift": "night"}, {"date": "2026-10-22", "shift": "day"}])
        assert out["added"] == 2 and out["flagged_for_reviewer"]
        assert slack.with_blocks("CSUPPORT")  # flagged entry posted for review in the test group, not a DM
        as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-03", "shift": "night"}])

        for minute in range(21, 95):
            real["t"] = start + timedelta(minutes=minute)
            w.tick()
            if minute == 60:
                assert "Last day" in slack.texts("CSUPPORT")[-1]
        assert any("window for October 2026 is closed" in t for t in slack.texts("CSUPPORT"))
        assert w.store.cycle("2026-10")["status"] == "reviewing"  # 3 flags still open

        out, _ = as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-10", "shift": "day"}])
        assert out["window_closed"] and "17 November 2026" in out["message"]

        for e in w.store.pending_reviews("2026-10"):
            w.review(e["id"], "rejected" if e["person_id"] == ARUN or e["support_date"] == "2026-10-22" else "accepted", ME)
        approval = slack.with_blocks("CAPPROVAL")[-1]
        assert f"<@{BOSS}>" in approval["text"] and "₹500" in approval["text"]
        assert w.approve("2026-10", BOSS) == "approved"
        hr = slack.texts("CAPPROVAL")[-1]
        assert "21 Sep 2026 - 20 Oct 2026" in hr and "[TEST]" in hr
    finally:
        workflow.set_instance(None)


def test_submissions_before_the_17th_get_window_closed(wf):
    wf.clock.dt = ist(2026, 10, 16, 18)
    out, _ = as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-10", "shift": "day"}])
    assert out["window_closed"] and "17 October 2026" in out["message"]


# -- permissions guard --------------------------------------------------------------

def test_bot_never_deletes_or_removes_anything():
    """The bot may only read, post and edit its own messages. Fail if any destructive Slack call appears."""
    import re as _re
    root = Path(__file__).resolve().parent.parent
    allowed = {"auth_test", "chat_postMessage", "chat_postEphemeral", "chat_update",
               "conversations_replies", "users_info", "views_open"}
    used = set()
    for f in [root / "app.py", *root.glob("agent/**/*.py")]:
        used |= set(_re.findall(r"client\.([a-z_]+)\(", f.read_text()))
    assert used <= allowed, f"unexpected Slack calls: {used - allowed}"
    assert not [m for m in used if _re.search(r"delete|remove|archive|kick|leave|rename|set_|invite|join", m)]

    manifest = (root / "manifest.yaml").read_text()
    scopes = set(_re.findall(r"^\s+- ([a-z.:_]+)$", manifest.split("settings:")[0], _re.M))
    assert scopes == {"app_mentions:read", "chat:write", "channels:history", "groups:history", "users:read"}


# -- nudges -----------------------------------------------------------------------------

def _at(wf, dt):
    wf.clock.dt = dt
    wf.tick(dt)


def _nudges(slack):
    return [p for p in slack.posts if ":alarm_clock:" in p["text"]]


def test_approver_nudged_every_2_hours_at_most_3_times_then_stops(wf):
    slack = wf.client
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])
    wf.clock.dt = ist(2026, 10, 20, 0, 0)
    wf.close_cycle("2026-10")                                   # posted for approval at 00:00
    _at(wf, ist(2026, 10, 20, 1, 59))
    assert _nudges(slack) == []
    _at(wf, ist(2026, 10, 20, 2, 0))
    n = _nudges(slack)
    assert len(n) == 1 and f"<@{BOSS}>" in n[0]["text"] and "2 hours" in n[0]["text"] and "₹500" in n[0]["text"]
    assert n[0]["thread_ts"] == wf.store.cycle("2026-10")["approval_ts"] and n[0]["reply_broadcast"]
    _at(wf, ist(2026, 10, 20, 2, 30))
    assert len(_nudges(slack)) == 1                             # not again until 04:00
    for hh in (4, 6, 8, 10, 12):
        _at(wf, ist(2026, 10, 20, hh, 0))
    assert len(_nudges(slack)) == 3                             # capped at 3
    assert wf.approve("2026-10", BOSS) == "approved"


def test_approval_stops_nudges(wf):
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])
    wf.clock.dt = ist(2026, 10, 20, 0, 0)
    wf.close_cycle("2026-10")
    wf.approve("2026-10", BOSS)
    _at(wf, ist(2026, 10, 20, 5, 0))
    assert _nudges(wf.client) == []


def test_reviewer_nudged_for_flags_and_concerns(wf):
    slack = wf.client
    as_user(PRIYA, tools.submit_support_details, entries=[{"date": "2026-09-01", "shift": "day"}])
    wf.clock.dt = ist(2026, 10, 20, 0, 0)
    assert wf.close_cycle("2026-10") == "reviewing"
    _at(wf, ist(2026, 10, 20, 2, 0))
    n = _nudges(slack)[-1]
    assert n["channel"] == "CSUPPORT" and f"<@{ME}>" in n["text"] and "1 flagged entry" in n["text"]

    # Reviewer decides at 03:00 -> approval posted -> the approver's 2-hour clock starts fresh.
    wf.clock.dt = ist(2026, 10, 20, 3, 0)
    wf.review(wf.store.pending_reviews("2026-10")[0]["id"], "accepted", ME)
    _at(wf, ist(2026, 10, 20, 4, 59))
    assert len(_nudges(slack)) == 1
    _at(wf, ist(2026, 10, 20, 5, 0))
    assert f"<@{BOSS}>" in _nudges(slack)[-1]["text"]

    # Concern raised at 06:00 -> reviewer nudged in the concern thread at 08:00.
    wf.clock.dt = ist(2026, 10, 20, 6, 0)
    wf.raise_concern("2026-10", BOSS, "Check Sep 1")
    _at(wf, ist(2026, 10, 20, 8, 0))
    n = _nudges(slack)[-1]
    assert f"<@{ME}>" in n["text"] and "concern" in n["text"] and n["thread_ts"] == wf.store.cycle("2026-10")["concern_ts"]


def test_test_config_nudges_every_10_minutes():
    cfg = Workflow.load(Path(__file__).resolve().parent.parent / "config" / "workflow.test.json")
    assert (cfg.nudge_every_minutes, cfg.nudge_max) == (10, 3)
    assert (Workflow.load().nudge_every_minutes, Workflow.load().nudge_max) == (120, 3)
