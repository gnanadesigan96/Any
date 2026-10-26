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
ME, BOSS, PRIYA, ARUN = "UGNANA", "UBOSS", "UPRIYA", "UARUN"


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

    def files_upload_v2(self, **kw):
        self.files.append(kw)

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


def as_user(user_id, fn, **kwargs):
    ctx = RequestContext(user_id, FakeSlack().users_info(user_id)["user"]["real_name"], "CSUPPORT", f"t-{user_id}")
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


def test_bundled_config_loads_and_resolves_emails():
    cfg = Workflow.load().resolve_emails(lambda email: {"gnanadesigan@corestack.io": ME,
                                                        "poornodhaya.reddy@corestack.io": BOSS}[email])
    assert (cfg.reviewer, cfg.approver) == (ME, BOSS)
    assert cfg.period_text("2026-10") == "21 Sep 2026 - 20 Oct 2026"


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

    review_msg = slack.with_blocks(ME)[-1]
    assert action_ids(review_msg["blocks"]) == {B.REVIEW_ACCEPT, B.REVIEW_REJECT}
    flagged_id = B.row_ids(review_msg["blocks"])[0]

    as_user(ARUN, tools.submit_support_details, entries=[{"date": "2026-10-05", "shift": "day"}])

    # Window closes; a flagged entry is still open, so the final table waits.
    wf.tick(ist(2026, 10, 20, 0, 0))
    assert wf.store.cycle("2026-10")["status"] == "reviewing"
    assert not slack.with_blocks("CAPPROVAL")
    assert "still need your decision" in slack.texts(ME)[-2]

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
    out, attached = as_user(BOSS, tools.show_support_details)
    assert out["total"] == "₹500" and any("Arun" in a for a in attached)
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
    msg = slack.with_blocks(ME)[-1]
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
    review_msg = slack.with_blocks(ME)[-1]
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
