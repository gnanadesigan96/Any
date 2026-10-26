"""Chat tools for the monthly support-allowance workflow.

Team members submit / fix / view their own support days (no amounts shown).
Approvers can also see amounts, edit anyone's entries, close the window early,
approve, and re-send for approval.
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


def _is_approver(user_id: str) -> bool:
    return user_id in get_instance().cfg.approvers


def _name_for(user_id: str) -> str:
    try:
        u = get_instance().client.users_info(user=user_id)["user"]
        return u.get("real_name") or u.get("name") or user_id
    except Exception:
        return user_id


def _resolve(person_slack_id: str, cycle: str):
    """Work out (person_id, person_name, cycle_id) for a request, enforcing who may touch what."""
    req = current_request.get()
    wf = get_instance()
    person_slack_id = (person_slack_id or "").strip().strip("<@>")
    person_id = person_slack_id or req.user_id
    person_name = req.user_name if person_id == req.user_id else _name_for(person_id)
    if cycle:
        if not _is_approver(req.user_id):
            raise PermissionError("Only approvers can change a specific month; your details go into the open window.")
        c = wf.store.ensure_cycle(cycle)
        if c["status"] == "approved":
            raise PermissionError(f"{cycle_label(cycle)} is already approved and locked.")
        return person_id, person_name, cycle
    return person_id, person_name, wf.submission_cycle()


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
        "window_closes": f"{closes:%d %B %Y, %I:%M %p} {closes.tzname()}",
        "note": "This month's window has already closed, so these were added to next month's cycle." if late else None,
    }


@beta_tool
def submit_support_details(entries: list[SupportEntry], person_slack_id: str = "", cycle: str = "") -> str:
    """Record support days someone was on duty. Call this whenever a person shares their support details. A table of what was recorded is posted automatically below your reply - don't repeat it or mention amounts.

    Args:
        entries: One item per date and shift. `date` is YYYY-MM-DD; `shift` is "day" or "night" ("none" only for an extra task done on a day without a support shift); `extra_task` briefly describes any additional task performed that day, otherwise omit it. Expand ranges like "3-5 Oct" into separate dates.
        person_slack_id: Slack user ID (e.g. U0123ABC) when submitting on behalf of someone else. Leave empty for the person asking.
        cycle: Approvers only - a YYYY-MM month to edit after its window closed. Leave empty normally.
    """
    try:
        person_id, person_name, cid = _resolve(person_slack_id, cycle)
    except PermissionError as e:
        return _err(str(e))
    wf = get_instance()
    today = wf.now().date()
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
        elif d > today:
            problems.append(f"{d} is in the future - submit it after the shift")
        else:
            clean.append({"date": d.isoformat(), "shift": shift, "extra_task": extra})
    wf.store.ensure_cycle(cid)
    added, duplicates = wf.store.add_entries(cid, person_id, person_name, clean, current_request.get().user_name)
    _attach_person_table(person_id, person_name, cid)
    return json.dumps({
        "person": person_name,
        "added": len(added),
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
        person_slack_id: Slack user ID when fixing someone else's details. Leave empty for the person asking.
        cycle: Approvers only - YYYY-MM month to edit after its window closed.
    """
    try:
        person_id, person_name, cid = _resolve(person_slack_id, cycle)
    except PermissionError as e:
        return _err(str(e))
    req = current_request.get()
    if person_id != req.user_id and not _is_approver(req.user_id):
        return _err("You can only remove your own support details.")
    removed = get_instance().store.remove_entries(cid, person_id, dates, shift or None)
    _attach_person_table(person_id, person_name, cid)
    return json.dumps({"person": person_name, "removed": removed, "cycle": cycle_label(cid)})


@beta_tool
def show_support_details(person_slack_id: str = "", cycle: str = "") -> str:
    """Show recorded support details. Team members see their own (no amounts). Approvers can see anyone's, or - with no person - the full report with amounts for a month. The table is posted automatically.

    Args:
        person_slack_id: Slack user ID of the person to show. Empty = the person asking (or everyone, for approvers asking about a month).
        cycle: YYYY-MM month. Empty = the currently open window.
    """
    req = current_request.get()
    wf = get_instance()
    cid = cycle or wf.submission_cycle()
    approver = _is_approver(req.user_id)
    pid = (person_slack_id or "").strip().strip("<@>")
    if approver and not pid:
        entries = wf.store.entries(cid)
        if not entries:
            return json.dumps({"cycle": cycle_label(cid), "entries": 0})
        report = final_report(entries, Policy.load())
        req.attachments.append(f"*Support allowance - {cycle_label(cid)}* · {report['people']} people · total *{report['grand_total_text']}*")
        req.attachments.extend(code_blocks(report["summary"]))
        req.attachments.extend(code_blocks(report["detail"]))
        return json.dumps({"cycle": cycle_label(cid), "status": (wf.store.cycle(cid) or {}).get("status", "open"),
                           "people": report["people"], "entries": report["entries"], "total": report["grand_total_text"]})
    if pid and pid != req.user_id and not approver:
        return _err("You can only view your own support details.")
    person_id = pid or req.user_id
    _attach_person_table(person_id, req.user_name if person_id == req.user_id else _name_for(person_id), cid)
    return json.dumps({"cycle": cycle_label(cid), "shown_for": person_id})


@beta_tool
def support_window_status() -> str:
    """Which month is currently collecting support details, when the window closes, and the status of last month's approval."""
    wf = get_instance()
    cid = wf.submission_cycle()
    this_month = cycle_id_for(wf.now())
    info = _window_info(cid)
    info["months"] = {
        cycle_label(m): (wf.store.cycle(m) or {}).get("status", "open")
        for m in sorted({this_month, cid})
    }
    return json.dumps(info)


def _approver_only():
    req = current_request.get()
    return None if _is_approver(req.user_id) else _err("Only the configured approver can do this.")


@beta_tool
def close_window_now(cycle: str = "") -> str:
    """Approvers only: close a month's submission window immediately and post the final tables for approval.

    Args:
        cycle: YYYY-MM. Empty = the currently open window.
    """
    if denied := _approver_only():
        return denied
    wf = get_instance()
    cid = cycle or wf.submission_cycle()
    return json.dumps({"cycle": cycle_label(cid), "status": wf.close_cycle(cid)})


@beta_tool
def approve_support_allowance(cycle: str) -> str:
    """Approvers only: approve a month's support allowance (same as pressing Approve) and notify HR.

    Args:
        cycle: YYYY-MM month to approve.
    """
    if denied := _approver_only():
        return denied
    return json.dumps({"cycle": cycle_label(cycle), "status": get_instance().approve(cycle, current_request.get().user_id)})


@beta_tool
def resend_for_approval(cycle: str) -> str:
    """Approvers only: after corrections, re-post the updated tables for approval.

    Args:
        cycle: YYYY-MM month to re-send.
    """
    if denied := _approver_only():
        return denied
    return json.dumps({"cycle": cycle_label(cycle), "status": get_instance().resubmit(cycle)})


TOOLS = [
    submit_support_details, remove_support_details, show_support_details, support_window_status,
    close_window_now, approve_support_allowance, resend_for_approval,
]
