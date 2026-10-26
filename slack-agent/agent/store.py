"""SQLite storage for monthly cycles and the support entries people submit.

Entry `review` values:
    NULL      inside the cycle's period - payable
    pending   outside the period, waiting for the reviewer
    accepted  outside the period, accepted by the reviewer - payable
    rejected  outside the period, rejected by the reviewer
    removed   taken out by the reviewer while addressing a concern
"""

import json
import sqlite3
from datetime import datetime, timezone

_CYCLE_FIELDS = {
    "status", "reminder_sent_at", "closing_reminder_sent_at", "closed_at",
    "approval_channel", "approval_ts", "decided_by", "decided_at",
    "concern_text", "concern_by", "concern_entry_ids", "concern_channel", "concern_ts",
}
_ENTRY_FIELDS = {"support_date", "shift", "extra_task", "review", "reviewed_by", "flag_reason"}
_GONE = ("rejected", "removed")
PAYABLE_SQL = "(review IS NULL OR review = 'accepted')"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path):
        self.path = str(path)
        with self._db() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS cycles (
                    cycle_id TEXT PRIMARY KEY,            -- 'YYYY-MM'
                    status TEXT NOT NULL DEFAULT 'open',  -- open | reviewing | pending_approval | concern | approved | empty
                    reminder_sent_at TEXT,
                    closing_reminder_sent_at TEXT,
                    closed_at TEXT,
                    approval_channel TEXT,
                    approval_ts TEXT,
                    decided_by TEXT,
                    decided_at TEXT,
                    concern_text TEXT,
                    concern_by TEXT,
                    concern_entry_ids TEXT,
                    concern_channel TEXT,
                    concern_ts TEXT
                );
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    person_id TEXT NOT NULL,
                    person_name TEXT NOT NULL,
                    support_date TEXT NOT NULL,
                    shift TEXT NOT NULL,                 -- day | night | none (extra task only)
                    extra_task TEXT,
                    review TEXT,
                    reviewed_by TEXT,
                    flag_reason TEXT,
                    thread_channel TEXT,
                    thread_ts TEXT,
                    submitted_by TEXT,
                    submitted_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS entries_person_date ON entries (person_id, support_date, shift);
                """
            )

    def _db(self):
        db = sqlite3.connect(self.path, timeout=30)
        db.row_factory = sqlite3.Row
        return db

    # -- cycles ---------------------------------------------------------------

    def cycle(self, cycle_id: str):
        with self._db() as db:
            row = db.execute("SELECT * FROM cycles WHERE cycle_id = ?", (cycle_id,)).fetchone()
        if not row:
            return None
        c = dict(row)
        c["concern_entry_ids"] = json.loads(c["concern_entry_ids"] or "[]")
        return c

    def ensure_cycle(self, cycle_id: str) -> dict:
        with self._db() as db:
            db.execute("INSERT OR IGNORE INTO cycles (cycle_id) VALUES (?)", (cycle_id,))
        return self.cycle(cycle_id)

    @staticmethod
    def _cycle_values(fields):
        bad = set(fields) - _CYCLE_FIELDS
        if bad:
            raise ValueError(f"unknown cycle fields: {bad}")
        return {k: json.dumps(v) if k == "concern_entry_ids" else v for k, v in fields.items()}

    def update_cycle(self, cycle_id: str, **fields):
        fields = self._cycle_values(fields)
        self.ensure_cycle(cycle_id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        with self._db() as db:
            db.execute(f"UPDATE cycles SET {sets} WHERE cycle_id = ?", [*fields.values(), cycle_id])

    def transition(self, cycle_id: str, from_statuses, to_status: str, **fields) -> bool:
        """Atomically move a cycle between statuses; False if it wasn't in `from_statuses` (e.g. a double click)."""
        fields = self._cycle_values(fields)
        from_statuses = list(from_statuses)
        sets = ", ".join(["status = ?", *(f"{k} = ?" for k in fields)])
        marks = ",".join("?" * len(from_statuses))
        with self._db() as db:
            cur = db.execute(
                f"UPDATE cycles SET {sets} WHERE cycle_id = ? AND status IN ({marks})",
                [to_status, *fields.values(), cycle_id, *from_statuses],
            )
        return cur.rowcount == 1

    # -- entries --------------------------------------------------------------

    def duplicate_of(self, person_id, support_date, shift, exclude_id=None):
        """Cycle ID where this person already claimed this date + shift, if any (rejected/removed don't count)."""
        with self._db() as db:
            row = db.execute(
                f"""SELECT cycle_id FROM entries WHERE person_id = ? AND support_date = ? AND shift = ?
                    AND (review IS NULL OR review NOT IN {_GONE}) AND id IS NOT ?""",
                (person_id, support_date, shift, exclude_id),
            ).fetchone()
        return row["cycle_id"] if row else None

    def overlaps(self, support_date, shift, person_id, exclude_id=None) -> list:
        """Other people's live entries for the same date and the same day/night shift (extra-task-only never overlaps)."""
        if shift not in ("day", "night"):
            return []
        with self._db() as db:
            return [dict(r) for r in db.execute(
                f"""SELECT * FROM entries WHERE support_date = ? AND shift = ? AND person_id != ?
                    AND (review IS NULL OR review NOT IN {_GONE}) AND id IS NOT ?""",
                (support_date, shift, person_id, exclude_id)).fetchall()]

    def add_entries(self, cycle_id, person_id, person_name, entries, submitted_by, thread=(None, None)):
        """Insert entries; returns (added, duplicates). `added` items gain an `id`."""
        added, duplicates = [], []
        for e in entries:
            existing = self.duplicate_of(person_id, e["date"], e["shift"])
            if existing:
                duplicates.append({**e, "already_in_cycle": existing})
                continue
            with self._db() as db:
                cur = db.execute(
                    """INSERT INTO entries (cycle_id, person_id, person_name, support_date, shift, extra_task,
                                            review, reviewed_by, flag_reason, thread_channel, thread_ts, submitted_by, submitted_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cycle_id, person_id, person_name, e["date"], e["shift"], e.get("extra_task") or None,
                     e.get("review"), e.get("reviewed_by"), e.get("flag_reason"), thread[0], thread[1], submitted_by, _now()),
                )
            added.append({**e, "id": cur.lastrowid})
        return added, duplicates

    def entry(self, entry_id: int):
        with self._db() as db:
            row = db.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None

    def update_entry(self, entry_id: int, **fields):
        bad = set(fields) - _ENTRY_FIELDS
        if bad:
            raise ValueError(f"unknown entry fields: {bad}")
        sets = ", ".join(f"{k} = ?" for k in fields)
        with self._db() as db:
            db.execute(f"UPDATE entries SET {sets} WHERE id = ?", [*fields.values(), entry_id])

    def set_review_if_pending(self, entry_id: int, review: str, reviewed_by: str) -> bool:
        with self._db() as db:
            cur = db.execute("UPDATE entries SET review = ?, reviewed_by = ? WHERE id = ? AND review = 'pending'",
                             (review, reviewed_by, entry_id))
        return cur.rowcount == 1

    def remove_entries(self, cycle_id, person_id, dates, shift=None) -> int:
        """A person withdrawing their own entries while the window is open."""
        marks = ",".join("?" * len(dates))
        sql = f"DELETE FROM entries WHERE cycle_id = ? AND person_id = ? AND support_date IN ({marks})"
        args = [cycle_id, person_id, *dates]
        if shift:
            sql += " AND shift = ?"
            args.append(shift)
        with self._db() as db:
            return db.execute(sql, args).rowcount

    def entries(self, cycle_id, person_id=None, payable_only=False, ids=None) -> list:
        """Entries of a cycle (rejected/removed excluded unless `ids` asks for them explicitly)."""
        sql, args = "SELECT * FROM entries WHERE cycle_id = ?", [cycle_id]
        if ids is not None:
            sql += f" AND id IN ({','.join('?' * len(ids)) or 'NULL'})"
            args += list(ids)
        else:
            sql += f" AND (review IS NULL OR review NOT IN {_GONE})"
        if payable_only:
            sql += f" AND {PAYABLE_SQL}"
        if person_id:
            sql += " AND person_id = ?"
            args.append(person_id)
        sql += " ORDER BY lower(person_name), support_date, shift"
        with self._db() as db:
            return [dict(r) for r in db.execute(sql, args).fetchall()]

    def pending_reviews(self, cycle_id) -> list:
        with self._db() as db:
            return [dict(r) for r in db.execute(
                "SELECT * FROM entries WHERE cycle_id = ? AND review = 'pending' ORDER BY lower(person_name), support_date",
                (cycle_id,)).fetchall()]
