"""Month-over-month comparison and trends for support allowances.

All numbers are computed here from the stored entries (payable ones only for
money and shift counts), so the bot's narrative is always backed by exact data.
"""

from .config import Policy, cycle_label
from .report import money, priced, render_table
from .store import Store

_COUNTS = ("entries", "day_shifts", "night_shifts", "weekday_shifts", "weekend_shifts", "holiday_shifts", "extra_tasks")


def cycle_stats(store: Store, policy: Policy, cid: str, person_id: str = None) -> dict:
    items = priced(store.entries(cid, person_id=person_id, payable_only=True), policy)
    everything = [e for e in store.all_entries(cid) if not person_id or e["person_id"] == person_id]
    shifts = [e for e in items if e["shift"] in ("day", "night")]
    people = {}
    for e in items:
        p = people.setdefault(e["person_id"], {"name": e["person_name"], "shifts": 0, "day": 0, "night": 0,
                                               "weekend": 0, "holiday": 0, "extra": 0, "total": 0.0})
        if e["shift"] in ("day", "night"):
            p["shifts"] += 1
            p[e["shift"]] += 1
            if e["day_type"] in ("weekend", "holiday"):
                p[e["day_type"]] += 1
        p["extra"] += 1 if e.get("extra_task") else 0
        p["total"] += e["total"]
    total = sum(e["total"] for e in items)
    return {
        "cycle": cid,
        "label": cycle_label(cid),
        "status": (store.cycle(cid) or {}).get("status", "open"),
        "people": len(people),
        "entries": len(items),
        "day_shifts": sum(e["shift"] == "day" for e in items),
        "night_shifts": sum(e["shift"] == "night" for e in items),
        "weekday_shifts": sum(e["day_type"] == "weekday" for e in shifts),
        "weekend_shifts": sum(e["day_type"] == "weekend" for e in shifts),
        "holiday_shifts": sum(e["day_type"] == "holiday" for e in shifts),
        "extra_tasks": sum(bool(e.get("extra_task")) for e in items),
        "shift_amount": sum(e["shift_amount"] for e in items),
        "extra_amount": sum(e["extra_amount"] for e in items),
        "total": total,
        "avg_per_person": total / len(people) if people else 0.0,
        "flags": {
            "accepted": sum(e.get("review") == "accepted" for e in everything),
            "rejected": sum(e.get("review") == "rejected" for e in everything),
            "removed": sum(e.get("review") == "removed" for e in everything),
            "pending": sum(e.get("review") == "pending" for e in everything),
        },
        "by_person": people,
    }


def _pct(old, new):
    if not old:
        return None if not new else "new"
    return f"{(new - old) / old * 100:+.0f}%"


def _change(old, new, fmt=str):
    diff = new - old
    if not diff:
        return "no change"
    sign = "+" if diff > 0 else "-"
    pct = _pct(old, new)
    return f"{sign}{fmt(abs(diff))}" + (f" ({pct})" if pct and pct != "new" else "")


def compare(a: dict, b: dict, currency: str, with_money: bool) -> dict:
    """Compare stats of an earlier month `a` with a later month `b`."""
    m = lambda x: money(x, currency)  # noqa: E731
    rows = []
    if with_money:
        rows += [("Total amount", m(a["total"]), m(b["total"]), _change(a["total"], b["total"], m)),
                 ("  shift allowance", m(a["shift_amount"]), m(b["shift_amount"]), _change(a["shift_amount"], b["shift_amount"], m)),
                 ("  extra-task allowance", m(a["extra_amount"]), m(b["extra_amount"]), _change(a["extra_amount"], b["extra_amount"], m))]
    rows.append(("People", a["people"], b["people"], _change(a["people"], b["people"])))
    labels = {"entries": "Entries", "day_shifts": "Day shifts", "night_shifts": "Night shifts",
              "weekday_shifts": "Weekday shifts", "weekend_shifts": "Weekend shifts",
              "holiday_shifts": "Holiday shifts", "extra_tasks": "Extra tasks"}
    rows += [(labels[k], a[k], b[k], _change(a[k], b[k])) for k in _COUNTS]
    if with_money:
        rows.append(("Avg per person", m(a["avg_per_person"]), m(b["avg_per_person"]), _change(a["avg_per_person"], b["avg_per_person"], m)))
    rows.append(("Flagged: accepted/rejected", f"{a['flags']['accepted']}/{a['flags']['rejected']}",
                 f"{b['flags']['accepted']}/{b['flags']['rejected']}", ""))
    summary = render_table(["Metric", a["label"], b["label"], "Change"], rows)

    ids = sorted(set(a["by_person"]) | set(b["by_person"]),
                 key=lambda i: (a["by_person"].get(i) or b["by_person"][i])["name"].lower())
    zero = {"shifts": 0, "night": 0, "weekend": 0, "holiday": 0, "extra": 0, "total": 0.0}
    person_rows, people = [], []
    for i in ids:
        pa, pb = a["by_person"].get(i, zero), b["by_person"].get(i, zero)
        name = (b["by_person"].get(i) or a["by_person"][i])["name"]
        state = "new" if i not in a["by_person"] else ("not in " + b["label"].split()[0] if i not in b["by_person"] else "")
        arrow = lambda k: f"{pa[k]} → {pb[k]}"  # noqa: E731
        row = [name, arrow("shifts"), arrow("night"),
               f"{pa['weekend'] + pa['holiday']} → {pb['weekend'] + pb['holiday']}", arrow("extra")]
        if with_money:
            row += [f"{m(pa['total'])} → {m(pb['total'])}", _change(pa["total"], pb["total"], m)]
        row.append(state)
        person_rows.append(row)
        people.append({"name": name, "before": pa, "after": pb, "change": pb["total"] - pa["total"],
                       "shift_change": pb["shifts"] - pa["shifts"], "status": state or "both months"})
    headers = ["Employee", "Shifts", "Night", "Wknd/Hol", "Extra"]
    if with_money:
        headers += ["Amount", "Change"]
    headers.append("Note")
    people.sort(key=lambda p: -abs(p["change"]))
    return {
        "summary_table": summary,
        "columns_note": f"Per-person columns read {a['label']} → {b['label']}.",
        "person_table": render_table(headers, person_rows) if person_rows else "",
        "people": people,
    }


def trend_table(series: list, currency: str, with_money: bool) -> str:
    rows, prev = [], None
    for s in series:
        status = s["status"].replace("_", " ") if s["entries"] or s["status"] != "open" else "no data"
        row = [s["label"], status, s["people"], s["entries"], s["day_shifts"], s["night_shifts"],
               s["weekend_shifts"] + s["holiday_shifts"], s["extra_tasks"]]
        if with_money:
            row += [money(s["total"], currency), _change(prev["total"], s["total"], lambda x: money(x, currency)) if prev else "-"]
        rows.append(row)
        prev = s
    headers = ["Month", "Status", "People", "Entries", "Day", "Night", "Wknd/Hol", "Extra"]
    if with_money:
        headers += ["Total", "vs prev month"]
    return render_table(headers, rows)
