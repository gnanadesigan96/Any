"""Chat tools for the monthly support-allowance workflow.

Team members submit / fix / view their own support days (no amounts shown).
The reviewer decides out-of-period entries and fixes entries after a concern;
the approver gives the final approval or raises a concern. Everything here can
also be done with the buttons the bot posts - these tools let people just ask.
"""

import json
from datetime import date
from typing import Literal, TypedDict

from anthropic import beta_tool

from .. import analytics
from ..config import Policy, cycle_id_for, cycle_label, prev_cycle_id
from ..context import current_request
from ..report import code_blocks, final_report, submission_table, team_table
from ..workflow import get_instance


class SupportEntry(TypedDict, total=False):
    date: str
    shift: Literal["day", "night", "none"]
    extra_task: str


def _err(msg: str) -> str:
    return json.dumps({"error": msg})


def _uid(raw: str) -> str:
    return (raw or "").strip().strip("<@>")


def _money_visible(req, wf) -> bool:
    """Amounts are shown only to the reviewer/approver, and only in the approval (or HR) channel -
    replies in the support channel are visible to the whole team."""
    return req.user_id in wf.cfg.admins and req.channel_id in {wf.cfg.approval_channel, wf.cfg.hr_channel}


def _attach_person_table(person_id, person_name, cid):
    entries = get_instance().store.entries(cid, person_id)
    req = current_request.get()
    if not entries:
        req.attachments.append(f"_{person_name} has no support details recorded for {cycle_label(cid)}._")
        return
    req.attachments.append(f"*Support details - {person_name} - {cycle_label(cid)}* ({len(entries)} entries)")
    req.attachments.extend(code_blocks(submission_table(entries, Policy.load())))


def _window_info(cid):
    wf = get_instance()
    closes = wf.cfg.at(cid, wf.cfg.close)
    late = cid != cycle_id_for(wf.now())
    return {
        "cycle": cycle_label(cid),
        "allocation_period": wf.cfg.period_text(cid),
        "window_closes": f"{closes:%d %B %Y, %I:%M %p} {closes.tzname()}",
        "note": "This month's window has already closed, so these were added to next month's cycle." if late else None,
    }


def _parse(entries):
    clean, problems = [], []
    for e in entries:
        try:
            d = date.fromisoformat(str(e.get("date", "")).strip())
        except ValueError:
            problems.append(f"'{e.get('date')}' is not a valid date")
            continue
        shift = e.get("shift")
        extra = (e.get("extra_task") or "").strip()
        if shift not in ("day", "night", "none"):
            problems.append(f"{d}: shift must be day or night")
        elif shift == "none" and not extra:
            problems.append(f"{d}: no shift and no extra task - nothing to record")
        else:
            clean.append({"date": d.isoformat(), "shift": shift, "extra_task": extra})
    return clean, problems


@beta_tool
def submit_support_details(entries: list[SupportEntry], person_slack_id: str = "", cycle: str = "") -> str:
    """Record support days someone was on duty. Call this whenever a person shares their support details. A table of what was recorded is posted automatically below your reply - don't repeat it or mention amounts. Entries outside the allocation period, or whose day/night shift overlaps someone else's on the same date, are kept but flagged for the reviewer to accept or reject.

    Args:
        entries: One item per date and shift. `date` is YYYY-MM-DD; `shift` is "day" or "night" ("none" only for an extra task done on a day without a support shift); `extra_task` briefly describes any additional task performed that day, otherwise omit it. Expand ranges like "3-5 Oct" into separate dates.
        person_slack_id: Slack user ID (e.g. U0123ABC) when submitting on behalf of someone else. Leave empty for the person asking.
        cycle: Reviewer only - a YYYY-MM month to add entries to after its window closed (e.g. while fixing a concern). Leave empty normally.
    """
    req = current_request.get()
    wf = get_instance()
    person_id = _uid(person_slack_id) or req.user_id
    person_name = req.user_name if person_id == req.user_id else wf.user_name(person_id)
    clean, problems = _parse(entries)

    if cycle:  # reviewer adding to a closed month - same rules as the "Add entry" button
        if err := wf.check_reviewer_edit(cycle, req.user_id):
            return _err(err)
        added = 0
        for e in clean:
            if err := wf.add_entry(cycle, req.user_id, person_id, e["date"], e["shift"], e["extra_task"]):
                problems.append(f"{e['date']} {e['shift']}: {err}")
            else:
                added += 1
        _attach_person_table(person_id, person_name, cycle)
        return json.dumps({"person": person_name, "added": added, "problems": problems, "cycle": cycle_label(cycle)})

    if wf.cfg.outside_window == "reject":
        window = wf.window_state()
        if not window["open"]:
            return json.dumps({
                "window_closed": True,
                "message": f"The support details window is closed. The next window opens on "
                           f"{window['next_opens']:%d %B %Y} for {cycle_label(window['next_cycle'])} "
                           f"(support dates {wf.cfg.period_text(window['next_cycle'])}). "
                           f"For anything urgent, contact <@{wf.cfg.reviewer}>.",
                "nothing_recorded": True,
            })
        cid = window["cycle"]
    else:
        cid = wf.submission_cycle()
    wf.store.ensure_cycle(cid)
    added, duplicates = [], []
    for e in clean:  # one at a time so overlaps within the same message are caught too
        reason, _ = wf.entry_flags(cid, person_id, e["date"], e["shift"])
        if reason:
            e.update(review="pending", flag_reason=reason)
        a, d = wf.store.add_entries(cid, person_id, person_name, [e], req.user_name, thread=(req.channel_id, req.thread_ts))
        added += a
        duplicates += d
    flagged = [e for e in added if e.get("review") == "pending"]
    to_review = wf.flag_overlap_partners([{**e, "person_id": person_id, "person_name": person_name} for e in added])
    to_review.setdefault(cid, [])[:0] = [e["id"] for e in flagged]
    for review_cid, ids in to_review.items():
        if ids:
            wf.notify_reviewer(review_cid, ids)
    _attach_person_table(person_id, person_name, cid)
    return json.dumps({
        "person": person_name,
        "added": len(added),
        "flagged_for_reviewer": [f"{e['date']} ({e['flag_reason']})" for e in flagged],
        "reviewer": f"<@{wf.cfg.reviewer}>",
        "already_submitted": [f"{d['date']} {d['shift']} (in {cycle_label(d['already_in_cycle'])})" for d in duplicates],
        "problems": problems,
        **_window_info(cid),
    })


@beta_tool
def remove_support_details(dates: list[str], shift: str = "", person_slack_id: str = "", cycle: str = "") -> str:
    """Remove wrongly submitted support days (e.g. "remove my 3 Oct night shift"). The updated table is posted automatically.

    Args:
        dates: Dates to remove, YYYY-MM-DD.
        shift: "day" or "night" to remove only that shift; empty removes every entry on those dates.
        person_slack_id: Slack user ID when the reviewer fixes someone else's details. Leave empty for the person asking.
        cycle: Reviewer only - YYYY-MM month to edit after its window closed.
    """
    req = current_request.get()
    wf = get_instance()
    person_id = _uid(person_slack_id) or req.user_id
    person_name = req.user_name if person_id == req.user_id else wf.user_name(person_id)
    if cycle or person_id != req.user_id:
        cid = cycle or wf.submission_cycle()
        if err := wf.check_reviewer_edit(cid, req.user_id):
            return _err(err if req.user_id == wf.cfg.reviewer else "You can only remove your own support details.")
        targets = [e for e in wf.store.entries(cid, person_id)
                   if e["support_date"] in dates and (not shift or e["shift"] == shift)]
        for e in targets:
            wf.set_row_removed(e["id"], req.user_id, removed=True)
        removed = len(targets)
    else:
        cid = wf.submission_cycle()
        removed = wf.store.remove_entries(cid, person_id, dates, shift or None)
    _attach_person_table(person_id, person_name, cid)
    return json.dumps({"person": person_name, "removed": removed, "cycle": cycle_label(cid)})


@beta_tool
def show_support_details(person_slack_id: str = "", cycle: str = "") -> str:
    """Show recorded support details. Team members see their own (no amounts). The reviewer and approver can see anyone's, or - with no person - the full report with amounts for a month. The table is posted automatically.

    Args:
        person_slack_id: Slack user ID of the person to show. Empty = the person asking (or everyone, for the reviewer/approver).
        cycle: YYYY-MM month. Empty = the currently open window.
    """
    req = current_request.get()
    wf = get_instance()
    cid = cycle or wf.submission_cycle()
    admin = req.user_id in wf.cfg.admins
    pid = _uid(person_slack_id)
    if admin and not pid:
        entries = wf.store.entries(cid, payable_only=True)
        pending = wf.store.pending_reviews(cid)
        status = (wf.store.cycle(cid) or {}).get("status", "open")
        if not _money_visible(req, wf):
            everyone = wf.store.entries(cid)
            req.attachments.append(f"*Support details - {cycle_label(cid)}* ({wf.cfg.period_text(cid)}) · "
                                   f"{len({e['person_id'] for e in everyone})} people · {len(everyone)} entries")
            if everyone:
                req.attachments.extend(code_blocks(team_table(everyone, Policy.load())))
            return json.dumps({"cycle": cycle_label(cid), "status": status, "entries": len(everyone),
                               "awaiting_review": len(pending),
                               "amounts_hidden": "Amounts are only shown in the approval channel, since this channel is "
                                                 "visible to the team."})
        if not entries:
            return json.dumps({"cycle": cycle_label(cid), "status": status, "entries": 0, "awaiting_review": len(pending)})
        report = final_report(entries, Policy.load())
        req.attachments.append(f"*Support allowance - {cycle_label(cid)}* ({wf.cfg.period_text(cid)}) · "
                               f"{report['people']} people · total *{report['grand_total_text']}*")
        req.attachments.extend(code_blocks(report["summary"]))
        req.attachments.extend(code_blocks(report["detail"]))
        return json.dumps({"cycle": cycle_label(cid), "status": status, "people": report["people"],
                           "entries": report["entries"], "total": report["grand_total_text"],
                           "awaiting_review": len(pending)})
    if pid and pid != req.user_id and not admin:
        return _err("You can only view your own support details.")
    person_id = pid or req.user_id
    _attach_person_table(person_id, req.user_name if person_id == req.user_id else wf.user_name(person_id), cid)
    return json.dumps({"cycle": cycle_label(cid), "shown_for": person_id})


@beta_tool
def support_window_status() -> str:
    """Which month is collecting support details, its allocation period, when the window closes, and where each month is in the approval process."""
    wf = get_instance()
    cid = wf.submission_cycle()
    this_month = cycle_id_for(wf.now())
    info = _window_info(cid)
    info["months"] = {
        cycle_label(m): {"status": (wf.store.cycle(m) or {}).get("status", "open"),
                         "awaiting_review": len(wf.store.pending_reviews(m))}
        for m in sorted({this_month, cid})
    }
    info["reviewer"] = f"<@{wf.cfg.reviewer}>"
    info["approver"] = f"<@{wf.cfg.approver}>"
    return json.dumps(info)


@beta_tool
def review_flagged_entries(decision: Literal["accepted", "rejected"], person_slack_id: str = "", cycle: str = "") -> str:
    """Reviewer only: accept or reject flagged entries - outside the allocation period or overlapping another person's shift (same as the Accept / Reject buttons).

    Args:
        decision: "accepted" or "rejected".
        person_slack_id: Only this person's flagged entries. Empty = all flagged entries of the month.
        cycle: YYYY-MM. Empty = the currently open window.
    """
    req = current_request.get()
    wf = get_instance()
    if req.user_id != wf.cfg.reviewer:
        return _err("Only the reviewer can accept or reject flagged entries.")
    cid = cycle or wf.submission_cycle()
    pid = _uid(person_slack_id)
    targets = [e for e in wf.store.pending_reviews(cid) if not pid or e["person_id"] == pid]
    for e in targets:
        wf.review(e["id"], decision, req.user_id)
    return json.dumps({"cycle": cycle_label(cid), decision: [f"{e['person_name']} {e['support_date']} {e['shift']}" for e in targets],
                       "status": (wf.store.cycle(cid) or {}).get("status", "open")})


@beta_tool
def close_window_now(cycle: str = "") -> str:
    """Reviewer or approver only: close a month's submission window immediately and move it on to review / final approval.

    Args:
        cycle: YYYY-MM. Empty = the currently open window.
    """
    req = current_request.get()
    wf = get_instance()
    if req.user_id not in wf.cfg.admins:
        return _err("Only the reviewer or approver can close the window early.")
    cid = cycle or wf.submission_cycle()
    return json.dumps({"cycle": cycle_label(cid), "status": wf.close_cycle(cid)})


@beta_tool
def approve_support_allowance(cycle: str) -> str:
    """Approver only: give the final approval for a month (same as pressing Approve). HR is then tagged.

    Args:
        cycle: YYYY-MM month to approve.
    """
    return json.dumps({"cycle": cycle_label(cycle), "status": get_instance().approve(cycle, current_request.get().user_id)})


@beta_tool
def raise_concern_on_allowance(cycle: str, concern: str) -> str:
    """Approver only: send the month back to the reviewer with a concern (same as pressing Raise concern).

    Args:
        cycle: YYYY-MM month.
        concern: What the approver is unhappy about.
    """
    return json.dumps({"cycle": cycle_label(cycle),
                       "status": get_instance().raise_concern(cycle, current_request.get().user_id, concern)})


@beta_tool
def respond_to_concern(cycle: str, response: str) -> str:
    """Reviewer only: after fixing entries, answer the approver's concern and re-send the updated tables for final approval.

    Args:
        cycle: YYYY-MM month.
        response: The reviewer's answer to the concern.
    """
    return json.dumps({"cycle": cycle_label(cycle),
                       "status": get_instance().respond_to_concern(cycle, current_request.get().user_id, response)})


def _latest_finished_cycle(wf) -> str:
    cycles = wf.store.cycles_with_entries()
    finished = [c for c in cycles if (wf.store.cycle(c) or {}).get("status", "open") != "open"]
    return (finished or cycles or [wf.submission_cycle()])[-1]


@beta_tool
def compare_support_months(later_month: str = "", earlier_month: str = "", trend_months: int = 0, person_slack_id: str = "") -> str:
    """Compare support allowance between months and show trends: totals, people, day/night/weekend/holiday shifts, extra tasks, flagged entries and a per-person breakdown of who went up or down. Use it for "compare with last month", "what's the trend", "how did October go", etc. Only specific people have access; for anyone else this returns no_access. When allowed, the tables AND your reply are shown only to the person who asked ("only visible to you" in the thread; the channel sees a short note), so explain the story in the numbers fully: biggest changes, who drove them, holidays/weekends, new or missing people, anything unusual.

    Args:
        later_month: YYYY-MM of the month to look at. Empty = the most recent month whose window has closed.
        earlier_month: YYYY-MM to compare against. Empty = the month before later_month.
        trend_months: Also show a trend over this many months ending at later_month (3-12). 0 = just the two-month comparison.
        person_slack_id: Only this person's numbers. Empty = the whole team.
    """
    req = current_request.get()
    wf = get_instance()
    if req.user_id not in wf.cfg.analytics_users:
        return json.dumps({"no_access": True,
                           "message": "Sorry, you don't have access to support allowance comparisons and trends."})
    req.private_reply["user"] = req.user_id   # everything below is sent to them privately
    pid = _uid(person_slack_id) or None
    later = later_month or _latest_finished_cycle(wf)
    earlier = earlier_month or prev_cycle_id(later)
    policy = Policy.load()
    a = analytics.cycle_stats(wf.store, policy, earlier, pid)
    b = analytics.cycle_stats(wf.store, policy, later, pid)
    cmp = analytics.compare(a, b, policy.currency, with_money=True)  # private to an authorised person

    who = f" - {wf.user_name(pid)}" if pid else ""
    req.attachments.append(f"*Support allowance: {a['label']} vs {b['label']}{who}*\n"
                           f"Periods: {wf.cfg.period_text(earlier)} vs {wf.cfg.period_text(later)}")
    req.attachments.extend(code_blocks(cmp["summary_table"]))
    if cmp["person_table"] and not pid:  # team view
        req.attachments.append(f"*Per person* ({cmp['columns_note']})")
        req.attachments.extend(code_blocks(cmp["person_table"]))

    series = []
    if trend_months and trend_months >= 3:
        cids = [later]
        for _ in range(min(int(trend_months), 12) - 1):
            cids.insert(0, prev_cycle_id(cids[0]))
        series = [analytics.cycle_stats(wf.store, policy, c, pid) for c in cids]
        req.attachments.append(f"*Trend - last {len(cids)} months{who}*")
        req.attachments.extend(code_blocks(analytics.trend_table(series, policy.currency, with_money=True)))

    def holidays_in(cid):
        first, last = wf.cfg.period(cid)
        return [f"{d} {n}" for d, n in sorted(policy.holidays.items()) if first.isoformat() <= d <= last.isoformat()]

    def slim(st):
        out = {k: v for k, v in st.items() if k != "by_person"}
        out["holidays_in_period"] = holidays_in(st["cycle"])
        return out

    people = cmp["people"][:15]
    notes = []
    if b["status"] in ("open", "reviewing"):
        notes.append(f"{b['label']} is still {b['status']} - its numbers may change.")
    if b["flags"]["pending"]:
        notes.append(f"{b['flags']['pending']} entries in {b['label']} are still awaiting review and are not counted.")
    return json.dumps({
        "earlier": slim(a), "later": slim(b),
        "biggest_person_changes": people,
        "trend": [slim(t) for t in series],
        "delivered_privately": True,
        "notes": notes,
    })


TOOLS = [
    submit_support_details, remove_support_details, show_support_details, support_window_status,
    review_flagged_entries, close_window_now, approve_support_allowance, raise_concern_on_allowance, respond_to_concern,
    compare_support_months,
]
