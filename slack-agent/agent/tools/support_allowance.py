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

from ..config import Policy, cycle_id_for, cycle_label
from ..context import current_request
from ..report import code_blocks, final_report, submission_table
from ..workflow import get_instance


class SupportEntry(TypedDict, total=False):
    date: str
    shift: Literal["day", "night", "none"]
    extra_task: str


def _err(msg: str) -> str:
    return json.dumps({"error": msg})


def _uid(raw: str) -> str:
    return (raw or "").strip().strip("<@>")


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


TOOLS = [
    submit_support_details, remove_support_details, show_support_details, support_window_status,
    review_flagged_entries, close_window_now, approve_support_allowance, raise_concern_on_allowance, respond_to_concern,
]
