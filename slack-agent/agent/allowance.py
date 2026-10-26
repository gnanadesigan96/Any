"""Support allowance rules and ledger.

Pure calculation lives in `calculate()` so it can be tested without Slack or
Claude. Recorded allocations go to a small SQLite ledger so the same day can't
be paid twice and totals can be reported per person / month.
"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path

DEFAULT_POLICY_PATH = Path(__file__).resolve().parent.parent / "config" / "allowance_policy.json"

_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass(frozen=True)
class Policy:
    currency: str
    rates: dict
    half_day_factor: float
    weekend_days: frozenset
    holidays: dict

    @classmethod
    def load(cls, path=DEFAULT_POLICY_PATH):
        raw = json.loads(Path(path).read_text())
        missing = {"weekday", "weekend", "holiday"} - set(raw["rates"])
        if missing:
            raise ValueError(f"allowance policy is missing rates for: {sorted(missing)}")
        return cls(
            currency=raw["currency"],
            rates={k: float(v) for k, v in raw["rates"].items()},
            half_day_factor=float(raw.get("half_day_factor", 0.5)),
            weekend_days=frozenset(raw.get("weekend_days", ["Saturday", "Sunday"])),
            holidays=dict(raw.get("holidays", {})),
        )

    def day_type(self, d: date):
        """Return (category, note) for a date; holidays win over weekends."""
        iso = d.isoformat()
        if iso in self.holidays:
            return "holiday", self.holidays[iso]
        if _WEEKDAY_NAMES[d.weekday()] in self.weekend_days:
            return "weekend", _WEEKDAY_NAMES[d.weekday()]
        return "weekday", _WEEKDAY_NAMES[d.weekday()]


def parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        raise ValueError(f"'{value}' is not a valid date - use YYYY-MM-DD") from None


def calculate(person: str, support_dates, half_days=(), policy: Policy = None) -> dict:
    """Work out the allowance for one person's support days.

    `half_days` must be a subset of `support_dates`; those days are paid at
    `half_day_factor` of the normal rate.
    """
    policy = policy or Policy.load()
    if not person.strip():
        raise ValueError("person is required")
    days = sorted({parse_date(d) for d in support_dates})
    if not days:
        raise ValueError("at least one support date is required")
    halves = {parse_date(d) for d in half_days}
    stray = halves - set(days)
    if stray:
        raise ValueError(
            "half_days must also appear in support_dates: "
            + ", ".join(d.isoformat() for d in sorted(stray))
        )

    lines = []
    subtotals = {"weekday": 0.0, "weekend": 0.0, "holiday": 0.0}
    for d in days:
        category, note = policy.day_type(d)
        factor = policy.half_day_factor if d in halves else 1.0
        amount = round(policy.rates[category] * factor, 2)
        subtotals[category] += amount
        lines.append({
            "date": d.isoformat(),
            "day_type": category,
            "note": note,
            "half_day": d in halves,
            "rate": policy.rates[category],
            "amount": amount,
        })

    return {
        "person": person.strip(),
        "currency": policy.currency,
        "days": lines,
        "day_count": len(lines),
        "subtotals": {k: round(v, 2) for k, v in subtotals.items() if v},
        "total": round(sum(subtotals.values()), 2),
    }


class Ledger:
    """SQLite record of allowances that have actually been allocated."""

    def __init__(self, path):
        self.path = str(path)
        with self._connect() as db:
            db.execute(
                """CREATE TABLE IF NOT EXISTS allocations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person TEXT NOT NULL,
                    person_key TEXT NOT NULL,
                    support_date TEXT NOT NULL,
                    day_type TEXT NOT NULL,
                    half_day INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,
                    recorded_by TEXT,
                    recorded_at TEXT NOT NULL,
                    UNIQUE (person_key, support_date)
                )"""
            )

    def _connect(self):
        return sqlite3.connect(self.path)

    @staticmethod
    def _key(person: str) -> str:
        return " ".join(person.lower().split())

    def already_recorded(self, person: str, dates) -> list:
        dates = list(dates)
        if not dates:
            return []
        marks = ",".join("?" * len(dates))
        with self._connect() as db:
            rows = db.execute(
                f"SELECT support_date FROM allocations WHERE person_key = ? AND support_date IN ({marks})",
                [self._key(person), *dates],
            ).fetchall()
        return sorted(r[0] for r in rows)

    def record(self, result: dict, recorded_by: str = None) -> None:
        """Persist a `calculate()` result; refuses if any day is already paid."""
        dupes = self.already_recorded(result["person"], [d["date"] for d in result["days"]])
        if dupes:
            raise ValueError(f"{result['person']} already has allowance recorded for: {', '.join(dupes)}")
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as db:
            db.executemany(
                """INSERT INTO allocations
                   (person, person_key, support_date, day_type, half_day, amount, currency, recorded_by, recorded_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    (result["person"], self._key(result["person"]), d["date"], d["day_type"],
                     int(d["half_day"]), d["amount"], result["currency"], recorded_by, now)
                    for d in result["days"]
                ],
            )

    def summary(self, person: str = "", month: str = "") -> dict:
        """Totals per person, optionally filtered by person and/or YYYY-MM month."""
        where, args = [], []
        if person:
            where.append("person_key = ?")
            args.append(self._key(person))
        if month:
            where.append("substr(support_date, 1, 7) = ?")
            args.append(month)
        clause = f"WHERE {' AND '.join(where)}" if where else ""
        with self._connect() as db:
            rows = db.execute(
                f"""SELECT person, currency, COUNT(*), SUM(amount), GROUP_CONCAT(support_date, ', ')
                    FROM (SELECT * FROM allocations {clause} ORDER BY support_date)
                    GROUP BY person_key, currency ORDER BY person""",
                args,
            ).fetchall()
        people = [
            {"person": p, "currency": c, "day_count": n, "total": round(t, 2), "dates": ds}
            for p, c, n, t, ds in rows
        ]
        return {"filters": {"person": person or None, "month": month or None}, "people": people}
