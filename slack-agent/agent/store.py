"""SQLite storage for monthly cycles and the support entries people submit."""

import sqlite3
from datetime import datetime, timezone

_CYCLE_FIELDS = {
    "status", "reminder_sent_at", "closing_reminder_sent_at", "closed_at",
    "approval_channel", "approval_ts", "decided_by", "decided_at",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Store:
    def __init__(self, path):
        self.path = str(path)
        with self._db() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS cycles (
                    cycle_id TEXT PRIMARY KEY,          -- 'YYYY-MM'
                    status TEXT NOT NULL DEFAULT 'open',  -- open | pending_approval | rejected | approved | empty
                    reminder_sent_at TEXT,
                    closing_reminder_sent_at TEXT,
                    closed_at TEXT,
                    approval_channel TEXT,
                    approval_ts TEXT,
                    decided_by TEXT,
                    decided_at TEXT
                );
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cycle_id TEXT NOT NULL,
                    person_id TEXT NOT NULL,
                    person_name TEXT NOT NULL,
                    support_date TEXT NOT NULL,
                    shift TEXT NOT NULL,               -- day | night | none (extra task only)
                    extra_task TEXT,
                    submitted_by TEXT,
                    submitted_at TEXT NOT NULL,
                    UNIQUE (person_id, support_date, shift)
                );
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
        return dict(row) if row else None

    def ensure_cycle(self, cycle_id: str) -> dict:
        with self._db() as db:
            db.execute("INSERT OR IGNORE INTO cycles (cycle_id) VALUES (?)", (cycle_id,))
        return self.cycle(cycle_id)

    def update_cycle(self, cycle_id: str, **fields):
        bad = set(fields) - _CYCLE_FIELDS
        if bad:
            raise ValueError(f"unknown cycle fields: {bad}")
        self.ensure_cycle(cycle_id)
        sets = ", ".join(f"{k} = ?" for k in fields)
        with self._db() as db:
            db.execute(f"UPDATE cycles SET {sets} WHERE cycle_id = ?", [*fields.values(), cycle_id])

    def transition(self, cycle_id: str, from_statuses, to_status: str, **fields) -> bool:
        """Atomically move a cycle between statuses; False if it wasn't in `from_statuses` (e.g. a double click)."""
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

    def add_entries(self, cycle_id, person_id, person_name, entries, submitted_by):
        """Insert entries; returns (added, duplicates). A person/date/shift can only ever be claimed once."""
        added, duplicates = [], []
        with self._db() as db:
            for e in entries:
                existing = db.execute(
                    "SELECT cycle_id FROM entries WHERE person_id = ? AND support_date = ? AND shift = ?",
                    (person_id, e["date"], e["shift"]),
                ).fetchone()
                if existing:
                    duplicates.append({**e, "already_in_cycle": existing["cycle_id"]})
                    continue
                db.execute(
                    """INSERT INTO entries (cycle_id, person_id, person_name, support_date, shift, extra_task, submitted_by, submitted_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cycle_id, person_id, person_name, e["date"], e["shift"], e.get("extra_task") or None, submitted_by, _now()),
                )
                added.append(e)
        return added, duplicates

    def remove_entries(self, cycle_id, person_id, dates, shift=None) -> int:
        marks = ",".join("?" * len(dates))
        sql = f"DELETE FROM entries WHERE cycle_id = ? AND person_id = ? AND support_date IN ({marks})"
        args = [cycle_id, person_id, *dates]
        if shift:
            sql += " AND shift = ?"
            args.append(shift)
        with self._db() as db:
            return db.execute(sql, args).rowcount

    def entries(self, cycle_id, person_id=None) -> list:
        sql = "SELECT * FROM entries WHERE cycle_id = ?"
        args = [cycle_id]
        if person_id:
            sql += " AND person_id = ?"
            args.append(person_id)
        sql += " ORDER BY lower(person_name), support_date, shift"
        with self._db() as db:
            return [dict(r) for r in db.execute(sql, args).fetchall()]
