"""Plain-text tables (Slack code blocks) and CSV for support entries."""

import csv
import io
from datetime import date

from .config import Policy

_SHIFT_LABEL = {"day": "Day", "night": "Night", "none": "-"}


def money(amount: float, currency: str) -> str:
    if currency == "INR":
        return f"₹{amount:,.0f}"
    return f"{currency} {amount:,.2f}"


def render_table(headers, rows) -> str:
    cells = [[str(c) for c in headers]] + [[str(c) for c in r] for r in rows]
    widths = [max(len(r[i]) for r in cells) for i in range(len(headers))]
    line = lambda r: " | ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip()  # noqa: E731
    sep = "-+-".join("-" * w for w in widths)
    return "\n".join([line(cells[0]), sep, *(line(r) for r in cells[1:])])


def code_blocks(text: str, limit: int = 3500) -> list:
    """Split a long table into several ``` blocks so each Slack message stays readable."""
    chunks, current = [], []
    for ln in text.splitlines():
        if current and sum(len(x) + 1 for x in current) + len(ln) > limit:
            chunks.append(current)
            current = []
        current.append(ln)
    if current:
        chunks.append(current)
    return ["```\n" + "\n".join(c) + "\n```" for c in chunks]


def _clip(text, n=40):
    text = (text or "").replace("\n", " ").strip()
    return text if len(text) <= n else text[: n - 1] + "…"


def _day_type_label(policy: Policy, d: date) -> str:
    kind = policy.day_type(d)
    if kind == "holiday":
        return f"Holiday ({policy.holidays[d.isoformat()]})"
    return kind.capitalize()


def priced(entries, policy: Policy) -> list:
    out = []
    for e in entries:
        d = date.fromisoformat(e["support_date"])
        out.append({**e, "date_obj": d, **policy.amount(d, e["shift"], bool(e.get("extra_task")))})
    return out


def submission_table(entries, policy: Policy) -> str:
    """What a person sees after submitting: their details, no amounts."""
    rows = [
        (d.strftime("%d %b %Y"), d.strftime("%a"), _SHIFT_LABEL[e["shift"]], _day_type_label(policy, d), _clip(e.get("extra_task")) or "-")
        for e in entries
        for d in [date.fromisoformat(e["support_date"])]
    ]
    return render_table(["Date", "Day", "Shift", "Day type", "Extra task"], rows)


def final_report(entries, policy: Policy) -> dict:
    """Detailed + per-person summary tables (with amounts) for the approver and HR."""
    items = priced(entries, policy)
    cur = policy.currency
    detail_rows, people = [], {}
    for i, e in enumerate(items, 1):
        d = e["date_obj"]
        detail_rows.append((
            i, e["person_name"], d.strftime("%d %b %Y"), d.strftime("%a"), _SHIFT_LABEL[e["shift"]],
            _day_type_label(policy, d), _clip(e.get("extra_task"), 30) or "-", money(e["total"], cur),
        ))
        p = people.setdefault(e["person_id"], {"name": e["person_name"], "day": 0, "night": 0, "extra": 0, "total": 0.0})
        if e["shift"] in ("day", "night"):
            p[e["shift"]] += 1
        p["extra"] += 1 if e.get("extra_task") else 0
        p["total"] += e["total"]

    summary_rows = [
        (p["name"], p["day"], p["night"], p["extra"], money(p["total"], cur))
        for p in sorted(people.values(), key=lambda p: p["name"].lower())
    ]
    grand = sum(p["total"] for p in people.values())
    summary_rows.append(("TOTAL", sum(p["day"] for p in people.values()), sum(p["night"] for p in people.values()),
                         sum(p["extra"] for p in people.values()), money(grand, cur)))
    return {
        "detail": render_table(["#", "Employee", "Date", "Day", "Shift", "Day type", "Extra task", "Amount"], detail_rows),
        "summary": render_table(["Employee", "Day shifts", "Night shifts", "Extra tasks", "Total"], summary_rows),
        "people": len(people),
        "entries": len(items),
        "grand_total": grand,
        "grand_total_text": money(grand, cur),
        "csv": _csv(items, cur),
    }


def _csv(items, currency) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["Employee", "Slack ID", "Date", "Day", "Shift", "Day type", "Extra task",
                f"Shift amount ({currency})", f"Extra amount ({currency})", f"Total ({currency})"])
    for e in items:
        d = e["date_obj"]
        w.writerow([e["person_name"], e["person_id"], d.isoformat(), d.strftime("%A"), _SHIFT_LABEL[e["shift"]],
                    e["day_type"], e.get("extra_task") or "", e["shift_amount"], e["extra_amount"], e["total"]])
    return buf.getvalue()
