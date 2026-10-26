"""The monthly support-allowance cycle.

    17th     reminder posted in the collection channel (team submits details)
    19th     "last day" reminder; window closes at end of day (IST)
    flags    dates outside the period (21st last month .. 20th this month) go to the
             reviewer with Accept / Reject buttons; the final table waits for them
    close    final tables posted in the approval channel, approver tagged with
             Approve / Raise concern buttons
    concern  the concern comes back to the reviewer as an editable table; the
             reviewer fixes rows and presses "Respond & send for approval"
    ok       HR tagged: details updated and approved

Cycle status: open -> [reviewing] -> pending_approval <-> concern -> approved   (or "empty")

`tick()` runs every minute in a background thread. All progress is stored in
SQLite, so a restart (or being down at the exact minute) just catches up on the
next tick instead of skipping or repeating a step.
"""

import logging
import threading
from datetime import date, datetime, timezone

from . import blocks as B
from .config import Policy, Workflow, cycle_id_for, cycle_label, next_cycle_id, prev_cycle_id
from .report import code_blocks, final_report, shift_label
from .store import Store

log = logging.getLogger(__name__)

EDITABLE_STATUSES = ("open", "reviewing", "concern")

_instance = None


def set_instance(wf):
    global _instance
    _instance = wf


def get_instance() -> "SupportWorkflow":
    if _instance is None:
        raise RuntimeError("support workflow is not running")
    return _instance


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class SupportWorkflow:
    def __init__(self, client, store: Store, cfg: Workflow, bot_user_id: str = ""):
        self.client = client
        self.store = store
        self.cfg = cfg
        self.bot_mention = f"<@{bot_user_id}>" if bot_user_id else "@me"
        self._names = {}

    # -- helpers --------------------------------------------------------------

    def now(self) -> datetime:
        return datetime.now(self.cfg.tz)

    def user_name(self, user_id: str) -> str:
        if user_id not in self._names:
            try:
                u = self.client.users_info(user=user_id)["user"]
                self._names[user_id] = u.get("real_name") or u.get("name") or user_id
            except Exception:
                return user_id
        return self._names[user_id]

    def submission_cycle(self, now: datetime = None) -> str:
        """The cycle a submission made right now belongs to: this month's until its window closes, then next month's."""
        now = now or self.now()
        cid = cycle_id_for(now)
        if now >= self.cfg.close_at(cid):
            cid = next_cycle_id(cid)
        while (c := self.store.cycle(cid)) and c["status"] != "open":  # closed early
            cid = next_cycle_id(cid)
        return cid

    def flag_reason(self, cid: str, d: date):
        """Why a date needs the reviewer's decision, or None if it's inside the cycle's period."""
        first, last = self.cfg.period(cid)
        if d < first:
            return f"before the period ({self.cfg.period_text(cid)})"
        if d > last:
            return f"after the period ({self.cfg.period_text(cid)})"
        return None

    def _post_thread_note(self, entry, text):
        if entry.get("thread_channel"):
            try:
                self.client.chat_postMessage(channel=entry["thread_channel"], thread_ts=entry["thread_ts"], text=text)
            except Exception:
                log.exception("could not notify submitter")

    # -- scheduler ------------------------------------------------------------

    def start(self, interval_seconds: int = 60):
        stop = threading.Event()

        def loop():
            while True:
                try:
                    self.tick()
                except Exception:
                    log.exception("support workflow tick failed")
                stop.wait(interval_seconds)

        threading.Thread(target=loop, name="support-workflow", daemon=True).start()

    def tick(self, now: datetime = None):
        now = now or self.now()
        this_month = cycle_id_for(now)
        for cid in (prev_cycle_id(this_month), this_month):
            close_at = self.cfg.close_at(cid)
            c = self.store.cycle(cid) or {}
            if cid == this_month and now < close_at:
                if not c.get("reminder_sent_at") and now >= self.cfg.at(cid, self.cfg.reminder):
                    self.post_reminder(cid)
                    if self.cfg.closing_reminder and now >= self.cfg.at(cid, self.cfg.closing_reminder):
                        # Started late (bot was down): one reminder is enough, don't post two back to back.
                        self.store.update_cycle(cid, closing_reminder_sent_at=_utc_now())
                elif (self.cfg.closing_reminder and not c.get("closing_reminder_sent_at")
                      and now >= self.cfg.at(cid, self.cfg.closing_reminder)):
                    self.post_closing_reminder(cid)
            if now >= close_at and c.get("status") == "open" and (c.get("reminder_sent_at") or self.store.entries(cid)):
                self.close_cycle(cid)

    # -- reminders and closing ------------------------------------------------

    def _deadline_text(self, cid) -> str:
        last_minute = self.cfg.at(cid, self.cfg.close)
        return f"{last_minute:%d %B, %I:%M %p} {last_minute.tzname()}"

    def post_reminder(self, cid):
        self.store.update_cycle(cid, reminder_sent_at=_utc_now())
        self.client.chat_postMessage(
            channel=self.cfg.collection_channel,
            text=(
                f"<!channel> :wave: Time to submit your *support details for {cycle_label(cid)}* "
                f"(support dates *{self.cfg.period_text(cid)}*).\n"
                f"Mention me in this channel with the dates and shifts, for example:\n"
                f"> {self.bot_mention} Night shift 3, 4 Oct; day shift 11 Oct, on 11th also did the DB failover\n"
                f"I'll reply with a table of what I recorded so you can check it.\n"
                f"*Window closes: {self._deadline_text(cid)}.*"
            ),
        )

    def post_closing_reminder(self, cid):
        self.store.update_cycle(cid, closing_reminder_sent_at=_utc_now())
        self.client.chat_postMessage(
            channel=self.cfg.collection_channel,
            text=f"<!channel> :hourglass_flowing_sand: Last day to submit support details for {cycle_label(cid)} - "
                 f"the window closes *{self._deadline_text(cid)}*.",
        )

    def close_cycle(self, cid) -> str:
        self.store.ensure_cycle(cid)
        if not self.store.entries(cid):
            if self.store.transition(cid, ["open"], "empty", closed_at=_utc_now()):
                self.client.chat_postMessage(
                    channel=self.cfg.approval_channel,
                    text=f"No support details were submitted for {cycle_label(cid)} - nothing to approve.",
                )
            return "empty"
        pending = self.store.pending_reviews(cid)
        to_status = "reviewing" if pending else "pending_approval"
        if not self.store.transition(cid, ["open"], to_status, closed_at=_utc_now()):
            return self.store.cycle(cid)["status"]
        self.client.chat_postMessage(
            channel=self.cfg.collection_channel,
            text=f":lock: The support details window for {cycle_label(cid)} is closed and has been sent for approval. "
                 f"Anything new will go into next month's cycle.",
        )
        if pending:
            self.client.chat_postMessage(
                channel=self.cfg.reviewer,
                text=f"The {cycle_label(cid)} window is closed. *{len(pending)} flagged "
                     f"entr{'y' if len(pending) == 1 else 'ies'}* still need your decision before the final table goes "
                     f"to <@{self.cfg.approver}>:",
            )
            self.notify_reviewer(cid, [e["id"] for e in pending])
        else:
            self.post_for_approval(cid)
        return to_status

    # -- out-of-period review -------------------------------------------------

    def notify_reviewer(self, cid, entry_ids):
        policy = Policy.load()
        for i in range(0, len(entry_ids), B.ROWS_PER_MESSAGE):
            chunk = self.store.entries(cid, ids=entry_ids[i:i + B.ROWS_PER_MESSAGE])
            names = ", ".join(sorted({e["person_name"] for e in chunk}))
            self.client.chat_postMessage(
                channel=self.cfg.reviewer,
                text=f"Support dates outside the {cycle_label(cid)} period need your review ({names}).",
                blocks=B.review_blocks(cid, chunk, self.cfg, policy),
            )

    def review(self, entry_id: int, decision: str, user_id: str) -> str:
        """Reviewer accepts/rejects one flagged entry. Returns accepted | rejected | not_authorised | already_decided."""
        if user_id != self.cfg.reviewer:
            return "not_authorised"
        if not self.store.set_review_if_pending(entry_id, decision, user_id):
            return "already_decided"
        e = self.store.entry(entry_id)
        self._post_thread_note(e, (
            f"<@{e['person_id']}> <@{user_id}> *{decision}* your {shift_label(e['shift']).lower()} shift entry for "
            f"{date.fromisoformat(e['support_date']):%d %b %Y} ({e['flag_reason']})."))
        self._release_if_reviewed(e["cycle_id"])
        return decision

    def refresh_review_message(self, channel, ts, entry_ids):
        entries = [e for e in (self.store.entry(i) for i in entry_ids) if e]
        if entries:
            self.client.chat_update(channel=channel, ts=ts, text="Support dates outside the period",
                                    blocks=B.review_blocks(entries[0]["cycle_id"], entries, self.cfg, Policy.load()))

    def _release_if_reviewed(self, cid):
        if self.store.pending_reviews(cid):
            return
        if self.store.transition(cid, ["reviewing"], "pending_approval"):
            self.client.chat_postMessage(channel=self.cfg.reviewer,
                                         text=f"All flagged entries for {cycle_label(cid)} are decided - "
                                              f"sending the final table to <@{self.cfg.approver}>.")
            self.post_for_approval(cid)

    # -- final approval -------------------------------------------------------

    def _post_report(self, channel, cid, report, title):
        self.client.chat_postMessage(
            channel=channel,
            text=f"*{title}*\nPeriod {self.cfg.period_text(cid)} · {report['people']} people · "
                 f"{report['entries']} entries · total *{report['grand_total_text']}*\n\n*Summary*",
        )
        for block in code_blocks(report["summary"]):
            self.client.chat_postMessage(channel=channel, text=block)
        self.client.chat_postMessage(channel=channel, text="*Details*")
        for block in code_blocks(report["detail"]):
            self.client.chat_postMessage(channel=channel, text=block)
        try:
            self.client.files_upload_v2(
                channel=channel, content=report["csv"],
                filename=f"support-allowance-{cid}.csv", title=f"Support allowance {cycle_label(cid)} (CSV)",
            )
        except Exception:
            log.exception("CSV upload failed (does the app have the files:write scope?)")

    def post_for_approval(self, cid, response: str = None):
        report = final_report(self.store.entries(cid, payable_only=True), Policy.load())
        channel = self.cfg.approval_channel
        title = f"Support allowance - {cycle_label(cid)}" + (" (updated)" if response else "")
        self._post_report(channel, cid, report, title)
        text, blocks = B.approval_blocks(cid, report, self.cfg, self.store.cycle(cid), response)
        resp = self.client.chat_postMessage(channel=channel, text=text, blocks=blocks)
        self.store.update_cycle(cid, approval_channel=resp["channel"], approval_ts=resp["ts"])

    def _replace_message(self, channel, ts, text):
        if not ts:
            return
        try:
            self.client.chat_update(channel=channel, ts=ts, text=text,
                                    blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": text}}])
        except Exception:
            log.exception("could not update message")

    def approve(self, cid, user_id) -> str:
        if user_id != self.cfg.approver:
            return "not_authorised"
        if not self.store.transition(cid, ["pending_approval"], "approved", decided_by=user_id, decided_at=_utc_now()):
            return (self.store.cycle(cid) or {}).get("status", "unknown")
        c = self.store.cycle(cid)
        report = final_report(self.store.entries(cid, payable_only=True), Policy.load())
        when = self.now().strftime("%d %b %Y %I:%M %p")
        self._replace_message(c["approval_channel"], c["approval_ts"],
                              f":white_check_mark: *{cycle_label(cid)}* support allowance "
                              f"({report['grand_total_text']}) approved by <@{user_id}> on {when}.")
        if self.cfg.hr_channel != self.cfg.approval_channel:
            self._post_report(self.cfg.hr_channel, cid, report, f"Support allowance - {cycle_label(cid)} (approved)")
        self.client.chat_postMessage(
            channel=self.cfg.hr_channel,
            text=(f"{self.cfg.hr_mention()} The support allowance details for *{cycle_label(cid)}* "
                  f"(period {self.cfg.period_text(cid)}) are updated and approved by <@{user_id}>. "
                  f"{report['people']} people, total *{report['grand_total_text']}*. The tables and CSV are above."),
        )
        return "approved"

    # -- concerns -------------------------------------------------------------

    def raise_concern(self, cid, user_id, text, entry_ids=None) -> str:
        if user_id != self.cfg.approver:
            return "not_authorised"
        ids = [int(i) for i in entry_ids or []] or [e["id"] for e in self.store.entries(cid)]
        if not self.store.transition(cid, ["pending_approval"], "concern", concern_text=text, concern_by=user_id,
                                     concern_entry_ids=ids):
            return (self.store.cycle(cid) or {}).get("status", "unknown")
        c = self.store.cycle(cid)
        self._replace_message(c["approval_channel"], c["approval_ts"],
                              f":warning: <@{user_id}> raised a concern on *{cycle_label(cid)}* - "
                              f"<@{self.cfg.reviewer}> is addressing it in the thread.")
        resp = self.client.chat_postMessage(
            channel=c["approval_channel"], thread_ts=c["approval_ts"], reply_broadcast=True,
            text=f"<@{self.cfg.reviewer}> concern from <@{user_id}> on {cycle_label(cid)}: {text}",
            blocks=self._concern_blocks(cid),
        )
        self.store.update_cycle(cid, concern_channel=resp["channel"], concern_ts=resp["ts"])
        return "concern"

    def _concern_blocks(self, cid, closed_note=None):
        c = self.store.cycle(cid)
        entries = self.store.entries(cid, ids=c["concern_entry_ids"])
        return B.concern_blocks(cid, c, entries, self.cfg, Policy.load(), closed_note)

    def refresh_concern(self, cid):
        c = self.store.cycle(cid)
        if c and c["status"] == "concern" and c.get("concern_ts"):
            self.client.chat_update(channel=c["concern_channel"], ts=c["concern_ts"],
                                    text=f"Concern on {cycle_label(cid)}", blocks=self._concern_blocks(cid))

    def check_reviewer_edit(self, cid, user_id):
        """Error message if `user_id` may not edit this cycle's entries right now, else None."""
        if user_id != self.cfg.reviewer:
            return "Only the reviewer can change entries here."
        status = (self.store.cycle(cid) or {}).get("status", "open")
        if status not in EDITABLE_STATUSES:
            return f"{cycle_label(cid)} is {status.replace('_', ' ')} - it can't be edited now."
        return None

    def _validate(self, cid, person_id, d: str, shift, extra, exclude_id=None):
        """(flag_reason, error) for a reviewer-made entry."""
        if shift == "none" and not extra:
            return None, "Pick a shift or describe the extra task."
        if dup := self.store.duplicate_of(person_id, d, shift, exclude_id):
            return None, f"Already claimed for this date and shift in {cycle_label(dup)}."
        return self.flag_reason(cid, date.fromisoformat(d)), None

    def set_row_removed(self, entry_id, user_id, removed: bool) -> str:
        e = self.store.entry(entry_id)
        if err := self.check_reviewer_edit(e["cycle_id"], user_id):
            return err
        if not removed:
            # Restoring: make sure nobody re-claimed the same day meanwhile.
            if dup := self.store.duplicate_of(e["person_id"], e["support_date"], e["shift"], entry_id):
                return f"Can't restore - already claimed in {cycle_label(dup)}."
        review = "removed" if removed else ("accepted" if e.get("flag_reason") else None)
        self.store.update_entry(entry_id, review=review, reviewed_by=user_id)
        self.refresh_concern(e["cycle_id"])
        return None

    def edit_entry(self, entry_id, user_id, support_date, shift, extra_task) -> str:
        """Returns an error message, or None when saved."""
        e = self.store.entry(entry_id)
        if err := self.check_reviewer_edit(e["cycle_id"], user_id):
            return err
        reason, err = self._validate(e["cycle_id"], e["person_id"], support_date, shift, extra_task, entry_id)
        if err:
            return err
        self.store.update_entry(entry_id, support_date=support_date, shift=shift, extra_task=extra_task or None,
                                review="accepted" if reason else None, reviewed_by=user_id, flag_reason=reason)
        self.refresh_concern(e["cycle_id"])
        return None

    def add_entry(self, cid, user_id, person_id, support_date, shift, extra_task) -> str:
        if err := self.check_reviewer_edit(cid, user_id):
            return err
        reason, err = self._validate(cid, person_id, support_date, shift, extra_task)
        if err:
            return err
        added, _ = self.store.add_entries(
            cid, person_id, self.user_name(person_id),
            [{"date": support_date, "shift": shift, "extra_task": extra_task,
              "review": "accepted" if reason else None, "reviewed_by": user_id if reason else None, "flag_reason": reason}],
            self.user_name(user_id))
        c = self.store.cycle(cid)
        if c["status"] == "concern":
            self.store.update_cycle(cid, concern_entry_ids=c["concern_entry_ids"] + [added[0]["id"]])
            self.refresh_concern(cid)
        return None

    def respond_to_concern(self, cid, user_id, response) -> str:
        if user_id != self.cfg.reviewer:
            return "not_authorised"
        if not self.store.transition(cid, ["concern"], "pending_approval"):
            return (self.store.cycle(cid) or {}).get("status", "unknown")
        c = self.store.cycle(cid)
        self.client.chat_update(
            channel=c["concern_channel"], ts=c["concern_ts"], text=f"Concern on {cycle_label(cid)} addressed",
            blocks=self._concern_blocks(cid, closed_note=f":speech_balloon: <@{user_id}> responded: {response}"))
        self.post_for_approval(cid, response=response)
        return "pending_approval"
