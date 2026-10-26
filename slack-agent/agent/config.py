"""Allowance rates and workflow settings, loaded from config/*.json."""

import json
import os
from dataclasses import dataclass, replace
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"

SHIFTS = ("day", "night", "none")
_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass(frozen=True)
class Policy:
    currency: str
    rates: dict          # {"day": {"weekday": .., "weekend": .., "holiday": ..}, "night": {...}}
    extra_task: float
    weekend_days: frozenset
    holidays: dict       # {"YYYY-MM-DD": "name"}

    @classmethod
    def load(cls, path=None):
        raw = json.loads(Path(path or os.environ.get("ALLOWANCE_POLICY_PATH", CONFIG_DIR / "allowance_policy.json")).read_text())
        for shift in ("day", "night"):
            missing = {"weekday", "weekend", "holiday"} - set(raw["rates"].get(shift, {}))
            if missing:
                raise ValueError(f"allowance policy is missing {shift}-shift rates for: {sorted(missing)}")
        return cls(
            currency=raw["currency"],
            rates={s: {k: float(v) for k, v in r.items()} for s, r in raw["rates"].items()},
            extra_task=float(raw.get("extra_task", 0)),
            weekend_days=frozenset(raw.get("weekend_days", ["Saturday", "Sunday"])),
            holidays=dict(raw.get("holidays", {})),
        )

    def day_type(self, d: date) -> str:
        """weekend / holiday / weekday. A holiday only counts when it falls on a weekday."""
        if _WEEKDAY_NAMES[d.weekday()] in self.weekend_days:
            return "weekend"
        if d.isoformat() in self.holidays:
            return "holiday"
        return "weekday"

    def amount(self, d: date, shift: str, has_extra_task: bool) -> dict:
        day_type = self.day_type(d)
        shift_amount = self.rates[shift][day_type] if shift in self.rates else 0.0
        extra = self.extra_task if has_extra_task else 0.0
        return {"day_type": day_type, "shift_amount": shift_amount, "extra_amount": extra, "total": shift_amount + extra}


@dataclass(frozen=True)
class Workflow:
    tz: ZoneInfo
    collection_channel: str
    approval_channel: str
    hr_channel: str
    reviewer: str            # handles flagged (out-of-period) entries and answers concerns
    approver: str            # gives the final approval
    hr_group: str
    hr_users: tuple
    period_start_day: int    # cycle "2026-10" covers 21 Sep (start, previous month) ..
    period_end_day: int      # .. 20 Oct (end, this month)
    reminder: tuple          # (day, time)
    closing_reminder: tuple  # (day, time) or None
    close: tuple             # (day, time)

    @classmethod
    def load(cls, path=None):
        raw = json.loads(Path(path or os.environ.get("WORKFLOW_CONFIG_PATH", CONFIG_DIR / "workflow.json")).read_text())
        sched = raw["schedule"]

        def slot(key):
            if not sched.get(key):
                return None
            return int(sched[key]["day"]), time.fromisoformat(sched[key]["time"])

        return cls(
            tz=ZoneInfo(raw.get("timezone", "Asia/Kolkata")),
            collection_channel=raw["collection_channel"],
            approval_channel=raw["approval_channel"],
            hr_channel=raw.get("hr_channel") or raw["approval_channel"],
            reviewer=raw["reviewer"],
            approver=raw["approver"],
            hr_group=raw.get("hr_group") or "",
            hr_users=tuple(raw.get("hr_users", [])),
            period_start_day=int(raw.get("period", {}).get("start_day", 21)),
            period_end_day=int(raw.get("period", {}).get("end_day", 20)),
            reminder=slot("reminder"),
            closing_reminder=slot("closing_reminder"),
            close=slot("close"),
        )

    def resolve_emails(self, lookup) -> "Workflow":
        """Swap any e-mail addresses (reviewer, approver, hr_users) for Slack user IDs using `lookup(email) -> id`."""
        conv = lambda v: lookup(v) if "@" in v else v  # noqa: E731
        return replace(self, reviewer=conv(self.reviewer), approver=conv(self.approver),
                       hr_users=tuple(conv(u) for u in self.hr_users))

    @property
    def admins(self) -> frozenset:
        """People who may see amounts and edit anyone's entries."""
        return frozenset({self.reviewer, self.approver})

    def period(self, cycle_id: str):
        """(first_day, last_day) of support dates paid in this cycle, e.g. 21 Sep .. 20 Oct."""
        year, month = map(int, cycle_id.split("-"))
        py, pm = map(int, prev_cycle_id(cycle_id).split("-"))
        return date(py, pm, self.period_start_day), date(year, month, self.period_end_day)

    def period_text(self, cycle_id: str) -> str:
        first, last = self.period(cycle_id)
        return f"{first:%d %b %Y} - {last:%d %b %Y}"

    def at(self, cycle_id: str, slot: tuple) -> datetime:
        """The moment a schedule slot happens in a given cycle month ("YYYY-MM")."""
        year, month = map(int, cycle_id.split("-"))
        day, t = slot
        return datetime(year, month, day, t.hour, t.minute, tzinfo=self.tz)

    def close_at(self, cycle_id: str) -> datetime:
        """The window closes at the END of the configured minute, so "23:59" means midnight."""
        return self.at(cycle_id, self.close) + timedelta(minutes=1)

    def hr_mention(self) -> str:
        parts = [f"<!subteam^{self.hr_group}>"] if self.hr_group else []
        parts += [f"<@{u}>" for u in self.hr_users]
        return " ".join(parts) or "HR team"



def cycle_id_for(dt: datetime) -> str:
    return f"{dt.year:04d}-{dt.month:02d}"


def next_cycle_id(cycle_id: str) -> str:
    y, m = map(int, cycle_id.split("-"))
    return f"{y + (m == 12):04d}-{m % 12 + 1:02d}"


def prev_cycle_id(cycle_id: str) -> str:
    y, m = map(int, cycle_id.split("-"))
    return f"{y - (m == 1):04d}-{(m - 2) % 12 + 1:02d}"


def cycle_label(cycle_id: str) -> str:
    return datetime.strptime(cycle_id, "%Y-%m").strftime("%B %Y")
