"""Allowance rates and workflow settings, loaded from config/*.json."""

import json
import os
import re
from dataclasses import dataclass
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
    review_channel: str = None        # where flagged entries go; None = DM the reviewer
    outside_window: str = "reject"    # "reject" (tell them the window is closed) or "next_cycle"
    test_timeline: tuple = None       # ((minutes_after_start, pretend_datetime), ...) - test mode only

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
            review_channel=raw.get("review_channel") or None,
            outside_window=raw.get("submissions_outside_window", "reject"),
            test_timeline=_test_timeline(raw, ZoneInfo(raw.get("timezone", "Asia/Kolkata"))),
        )

    def problems(self) -> list:
        """Config values that are missing or not Slack IDs.

        The app deliberately has no permission to list channels or look people up by
        e-mail (so it can't see beyond the channels it's invited to) - hence IDs only.
        """
        out = []
        for name in ("collection_channel", "approval_channel", "hr_channel", "review_channel"):
            v = getattr(self, name)
            if v and not re.fullmatch(r"[CG][A-Z0-9]{6,}", v):
                out.append(f"{name} = {v!r} (needs a channel ID like C0123ABCD)")
        people = {"reviewer": self.reviewer, "approver": self.approver,
                  **{f"hr_users[{i}]": u for i, u in enumerate(self.hr_users)}}
        for name, v in people.items():
            if not re.fullmatch(r"[UW][A-Z0-9]{6,}", v or ""):
                out.append(f"{name} = {v!r} (needs a member ID like U0123ABCD)")
        if self.hr_group and not re.fullmatch(r"S[A-Z0-9]{6,}", self.hr_group):
            out.append(f"hr_group = {self.hr_group!r} (needs a user-group ID like S0123ABCD, or leave it empty)")
        return out

    @property
    def review_target(self) -> str:
        """Channel where flagged entries are posted for the reviewer."""
        return self.review_channel or self.collection_channel

    @property
    def allowed_channels(self) -> frozenset:
        """The only channels the bot listens to; anything else is ignored."""
        return frozenset(c for c in (self.collection_channel, self.review_channel, self.approval_channel, self.hr_channel) if c)

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



def _test_timeline(raw, tz):
    tm = raw.get("test_mode") or {}
    if not tm.get("enabled"):
        return None
    points = tuple(sorted(
        (float(p["after_minutes"]), datetime.fromisoformat(p["pretend"]).replace(tzinfo=tz)) for p in tm["timeline"]))
    if len(points) < 2 or points[0][0] != 0:
        raise ValueError("test_mode.timeline needs at least two points, the first at after_minutes 0")
    return points


class PretendClock:
    """Test mode: real minutes since the bot first started map onto pretend dates.

    Between two timeline points pretend time moves proportionally; after the last
    point it moves at normal speed.
    """

    def __init__(self, timeline, started_real: datetime):
        self.timeline = timeline
        self.started = started_real

    def at_real(self, real: datetime) -> datetime:
        minutes = (real - self.started).total_seconds() / 60
        pts = self.timeline
        for (m0, p0), (m1, p1) in zip(pts, pts[1:]):
            if minutes <= m1:
                frac = max(minutes, m0) - m0
                return p0 + (p1 - p0) * (frac / (m1 - m0))
        return pts[-1][1] + timedelta(minutes=minutes - pts[-1][0])

    def real_for(self, pretend: datetime) -> datetime:
        """When (real time) the pretend clock reaches `pretend`."""
        pts = self.timeline
        for (m0, p0), (m1, p1) in zip(pts, pts[1:]):
            if pretend <= p1:
                frac = max((pretend - p0) / (p1 - p0), 0)
                return self.started + timedelta(minutes=m0 + (m1 - m0) * frac)
        return self.started + timedelta(minutes=pts[-1][0]) + (pretend - pts[-1][1])


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
