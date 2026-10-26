"""Slack Block Kit builders: clickable review rows, approval buttons, the concern table and modals."""

import json
from datetime import date

from .config import Policy, Workflow, cycle_label
from .report import STATUS_LABEL, day_type_label, money, shift_label

# Button / menu action IDs
REVIEW_ACCEPT = "review_accept"
REVIEW_REJECT = "review_reject"
REVIEW_ALL = "review_all"
APPROVE = "allowance_approve"
RAISE_CONCERN = "allowance_concern"
CONCERN_ROW = "concern_row"
CONCERN_ADD = "concern_add"
CONCERN_RESPOND = "concern_respond"

# Modal callback IDs
CONCERN_MODAL = "concern_modal"
EDIT_MODAL = "edit_entry_modal"
ADD_MODAL = "add_entry_modal"
RESPOND_MODAL = "respond_modal"

ROWS_PER_MESSAGE = 20  # Slack allows 50 blocks per message; review rows use 2 each


def _text(t, kind="mrkdwn"):
    return {"type": kind, "text": t}


def _plain(t):
    return {"type": "plain_text", "text": t[:75], "emoji": True}


def _button(text, action_id, value, style=None, confirm=None):
    b = {"type": "button", "text": _plain(text), "action_id": action_id, "value": str(value)}
    if style:
        b["style"] = style
    if confirm:
        b["confirm"] = {"title": _plain(confirm[0]), "text": _text(confirm[1]),
                        "confirm": _plain(confirm[2]), "deny": _plain("Cancel")}
    return b


def entry_line(e, policy: Policy, with_amount: bool) -> str:
    d = date.fromisoformat(e["support_date"])
    parts = [f"*{e['person_name']}*", d.strftime("%a %d %b %Y"), shift_label(e["shift"]), day_type_label(policy, d)]
    if with_amount:
        a = policy.amount(d, e["shift"], bool(e.get("extra_task")))
        parts.append(money(a["total"], policy.currency))
    line = " · ".join(parts)
    if e.get("extra_task"):
        line += f"\n_Extra task: {e['extra_task']}_"
    return line


def entry_option(e, policy: Policy):
    d = date.fromisoformat(e["support_date"])
    return {"text": _plain(f"{e['person_name']} · {d:%d %b} · {shift_label(e['shift'])}"), "value": str(e["id"])}


def row_ids(message_blocks) -> list:
    """Entry IDs embedded (as block_id "row:<id>") in a message we posted earlier."""
    return [int(b["block_id"].split(":", 1)[1]) for b in message_blocks or [] if str(b.get("block_id", "")).startswith("row:")]


# -- out-of-period review (sent to the reviewer) ------------------------------

def review_blocks(cid, entries, cfg: Workflow, policy: Policy):
    blocks = [{"type": "section", "text": _text(
        f"<@{cfg.reviewer}> these *{cycle_label(cid)}* support entries need your decision - they are outside the "
        f"allocation period (*{cfg.period_text(cid)}*) or overlap with someone else's shift. Accept or reject each one:")}]
    pending = []
    for e in entries:
        blocks.append({"type": "section", "block_id": f"row:{e['id']}",
                       "text": _text(f"{entry_line(e, policy, with_amount=False)}\n:warning: {e.get('flag_reason') or 'needs review'}")})
        if e.get("review") == "pending":
            pending.append(e["id"])
            blocks.append({"type": "actions", "block_id": f"act:{e['id']}", "elements": [
                _button("Accept", REVIEW_ACCEPT, e["id"], "primary"),
                _button("Reject", REVIEW_REJECT, e["id"], "danger"),
            ]})
        else:
            icon = ":white_check_mark:" if e.get("review") == "accepted" else ":x:"
            who = f" by <@{e['reviewed_by']}>" if e.get("reviewed_by") else ""
            blocks.append({"type": "context", "elements": [_text(f"{icon} {STATUS_LABEL[e.get('review')]}{who}")]})
    if len(pending) > 1:
        blocks.append({"type": "actions", "elements": [
            _button("Accept all", REVIEW_ALL, json.dumps({"d": "accepted", "ids": pending})),
            _button("Reject all", REVIEW_ALL, json.dumps({"d": "rejected", "ids": pending}), "danger",
                    ("Reject all?", f"Reject all {len(pending)} entries?", "Reject all")),
        ]})
    return blocks


# -- final approval (sent to the approver) ------------------------------------

def approval_blocks(cid, report, cfg: Workflow, cycle: dict, response: str = None):
    text = (f"<@{cfg.approver}> please review the support allowance for *{cycle_label(cid)}* "
            f"(period {cfg.period_text(cid)}): {report['people']} people, {report['entries']} entries, "
            f"total *{report['grand_total_text']}*. Tables and CSV are above.")
    blocks = [{"type": "section", "text": _text(text)}]
    if response:
        blocks.append({"type": "section", "text": _text(
            f"*Your concern:* {cycle.get('concern_text', '')[:1200]}\n*Response from <@{cfg.reviewer}>:* {response[:1200]}")})
    blocks.append({"type": "actions", "elements": [
        _button("Approve", APPROVE, cid, "primary",
                ("Approve?", f"Approve {cycle_label(cid)} for {report['grand_total_text']} and notify HR?", "Approve")),
        _button("Raise concern", RAISE_CONCERN, cid, "danger"),
    ]})
    return text, blocks


# -- concern table (sent to the reviewer, edited in place) --------------------

def concern_blocks(cid, cycle, entries, cfg: Workflow, policy: Policy, closed_note: str = None):
    blocks = [{"type": "section", "text": _text(
        f"<@{cfg.reviewer}> <@{cycle['concern_by']}> raised a concern on *{cycle_label(cid)}*:\n>{cycle['concern_text'][:2000]}\n"
        + ("" if closed_note else "Fix the entries below with the ⋮ menu, then press *Respond & send for approval*."))}]
    for e in entries[:40]:
        gone = e.get("review") in ("rejected", "removed")
        line = entry_line(e, policy, with_amount=True)
        if gone:
            line = f"~{line.splitlines()[0]}~  _{STATUS_LABEL[e['review']]}_"
        block = {"type": "section", "block_id": f"row:{e['id']}", "text": _text(line)}
        if not closed_note and e.get("review") == "removed":
            block["accessory"] = _button("Restore", CONCERN_ROW, f"restore:{e['id']}")
        elif not closed_note and e.get("review") != "rejected":
            block["accessory"] = {"type": "overflow", "action_id": CONCERN_ROW, "options": [
                {"text": _plain("Edit"), "value": f"edit:{e['id']}"},
                {"text": _plain("Remove"), "value": f"remove:{e['id']}"},
            ]}
        blocks.append(block)
    if len(entries) > 40:
        blocks.append({"type": "context", "elements": [_text(f"_Showing 40 of {len(entries)} entries - ask me in chat to change the others._")]})
    if closed_note:
        blocks.append({"type": "context", "elements": [_text(closed_note)]})
    else:
        blocks.append({"type": "actions", "elements": [
            _button("Add entry", CONCERN_ADD, cid),
            _button("Respond & send for approval", CONCERN_RESPOND, cid, "primary"),
        ]})
    return blocks


# -- modals -------------------------------------------------------------------

def _modal(callback_id, title, blocks, meta, submit="Submit"):
    return {"type": "modal", "callback_id": callback_id, "title": _plain(title[:24]),
            "submit": _plain(submit), "close": _plain("Cancel"),
            "private_metadata": json.dumps(meta), "blocks": blocks}


def _shift_select(initial=None):
    opts = [{"text": _plain("Day shift"), "value": "day"}, {"text": _plain("Night shift"), "value": "night"},
            {"text": _plain("No shift (extra task only)"), "value": "none"}]
    el = {"type": "static_select", "action_id": "v", "options": opts}
    if initial:
        el["initial_option"] = next(o for o in opts if o["value"] == initial)
    return {"type": "input", "block_id": "shift", "label": _plain("Shift"), "element": el}


def _date_input(initial=None):
    el = {"type": "datepicker", "action_id": "v"}
    if initial:
        el["initial_date"] = initial
    return {"type": "input", "block_id": "date", "label": _plain("Date"), "element": el}


def _extra_input(initial=None):
    el = {"type": "plain_text_input", "action_id": "v", "placeholder": _plain("Additional task performed (leave empty if none)")}
    if initial:
        el["initial_value"] = initial
    return {"type": "input", "block_id": "extra", "optional": True, "label": _plain("Extra task"), "element": el}


def concern_modal(cid, entries, policy: Policy):
    blocks = []
    if entries:
        blocks.append({"type": "input", "block_id": "entries", "optional": True,
                       "label": _plain("Which entries? (leave empty for the whole month)"),
                       "element": {"type": "multi_static_select", "action_id": "v",
                                   "options": [entry_option(e, policy) for e in entries[:100]]}})
    blocks.append({"type": "input", "block_id": "concern", "label": _plain("Concern"),
                   "element": {"type": "plain_text_input", "action_id": "v", "multiline": True}})
    return _modal(CONCERN_MODAL, "Raise a concern", blocks, {"cid": cid}, "Send to reviewer")


def edit_modal(e, meta):
    return _modal(EDIT_MODAL, "Edit entry", [
        {"type": "section", "text": _text(f"*{e['person_name']}*")},
        _date_input(e["support_date"]), _shift_select(e["shift"]), _extra_input(e.get("extra_task")),
    ], meta, "Save")


def add_modal(meta):
    return _modal(ADD_MODAL, "Add entry", [
        {"type": "input", "block_id": "person", "label": _plain("Person"),
         "element": {"type": "users_select", "action_id": "v"}},
        _date_input(), _shift_select(), _extra_input(),
    ], meta, "Add")


def respond_modal(cid, cycle):
    return _modal(RESPOND_MODAL, "Respond to concern", [
        {"type": "section", "text": _text(f"*Concern:* {(cycle.get('concern_text') or '')[:2500]}")},
        {"type": "input", "block_id": "response", "label": _plain("Your response"),
         "element": {"type": "plain_text_input", "action_id": "v", "multiline": True}},
    ], {"cid": cid}, "Send for approval")


def modal_values(view) -> dict:
    """Flatten a submitted modal's state into {block_id: value}."""
    out = {}
    for block_id, actions in view["state"]["values"].items():
        v = actions["v"]
        out[block_id] = (
            v.get("selected_date") or v.get("selected_user")
            or (v.get("selected_option") or {}).get("value")
            or ([o["value"] for o in v["selected_options"]] if "selected_options" in v else None)
            or (v.get("value") or "").strip() or None
        )
    return out
