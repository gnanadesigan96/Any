"""The monthly support-allowance cycle.

    17th  reminder posted in the collection channel (team submits details)
    19th  "last day" reminder; window closes at end of day (IST)
    close final tables posted in the approval channel, approver tagged with Approve / Reject buttons
    ok    HR tagged: details updated and approved

`tick()` is called every minute by a background thread. All progress is stored
in SQLite, so a restart (or the bot being down at the exact minute) just
catches up on the next tick instead of skipping or repeating a step.
"""

import logging
import threading
from datetime import datetime, timezone

from .config import Policy, Workflow, cycle_id_for, cycle_label, next_cycle_id, prev_cycle_id
from .report import code_blocks, final_report
from .store import Store

log = logging.getLogger(__name__)

APPROVE_ACTION = "allowance_approve"
REJECT_ACTION = "allowance_reject"

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

    # -- time helpers ---------------------------------------------------------

    def now(self) -> datetime:
        return datetime.now(self.cfg.tz)

    def submission_cycle(self, now: datetime = None) -> str:
        """The cycle a submission made right now belongs to: this month's until its window closes, then next month's."""
        now = now or self.now()
        cid = cycle_id_for(now)
        if now >= self.cfg.close_at(cid):
            cid = next_cycle_id(cid)
        while (c := self.store.cycle(cid)) and c["status"] != "open":  # closed early by an admin
            cid = next_cycle_id(cid)
        return cid

    # -- scheduler ------------------------------------------------------------

    def start(self, interval_seconds: int = 60):
        def loop():
            while True:
                try:
                    self.tick()
                except Exception:
                    log.exception("support workflow tick failed")
                stop.wait(interval_seconds)

        stop = threading.Event()
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

    # -- steps ----------------------------------------------------------------

    def _deadline_text(self, cid) -> str:
        last_minute = self.cfg.at(cid, self.cfg.close)
        return f"{last_minute:%d %B, %I:%M %p} {last_minute.tzname()}"

    def post_reminder(self, cid):
        self.store.update_cycle(cid, reminder_sent_at=_utc_now())
        self.client.chat_postMessage(
            channel=self.cfg.collection_channel,
            text=(
                f"<!channel> :wave: Time to submit your *support details for {cycle_label(cid)}*.\n"
                f"Mention me in this channel with the dates you were on support, for example:\n"
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
        if not self.store.transition(cid, ["open"], "pending_approval", closed_at=_utc_now()):
            return self.store.cycle(cid)["status"]
        self.client.chat_postMessage(
            channel=self.cfg.collection_channel,
            text=f":lock: The support details window for {cycle_label(cid)} is closed and has been sent for approval. "
                 f"Anything new will go into next month's cycle.",
        )
        self.post_for_approval(cid)
        return "pending_approval"

    def _post_report(self, channel, cid, report, title):
        self.client.chat_postMessage(
            channel=channel,
            text=f"*{title}*\n{report['people']} people · {report['entries']} entries · total *{report['grand_total_text']}*\n\n*Summary*",
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

    def post_for_approval(self, cid):
        report = final_report(self.store.entries(cid), Policy.load())
        channel = self.cfg.approval_channel
        self._post_report(channel, cid, report, f"Support allowance - {cycle_label(cid)}")
        text = (f"{self.cfg.approver_mention()} please review the support allowance for *{cycle_label(cid)}* "
                f"(total *{report['grand_total_text']}*) and approve.")
        resp = self.client.chat_postMessage(
            channel=channel,
            text=text,
            blocks=[
                {"type": "section", "text": {"type": "mrkdwn", "text": text}},
                {"type": "actions", "elements": [
                    {"type": "button", "action_id": APPROVE_ACTION, "value": cid, "style": "primary",
                     "text": {"type": "plain_text", "text": "Approve"},
                     "confirm": {"title": {"type": "plain_text", "text": "Approve?"},
                                 "text": {"type": "plain_text", "text": f"Approve {cycle_label(cid)} for {report['grand_total_text']} and notify HR?"},
                                 "confirm": {"type": "plain_text", "text": "Approve"},
                                 "deny": {"type": "plain_text", "text": "Cancel"}}},
                    {"type": "button", "action_id": REJECT_ACTION, "value": cid, "style": "danger",
                     "text": {"type": "plain_text", "text": "Needs changes"}},
                ]},
            ],
        )
        self.store.update_cycle(cid, approval_channel=resp["channel"], approval_ts=resp["ts"])

    def _close_buttons(self, cid, outcome):
        c = self.store.cycle(cid)
        if not c.get("approval_ts"):
            return
        try:
            self.client.chat_update(
                channel=c["approval_channel"], ts=c["approval_ts"], text=outcome,
                blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": outcome}}],
            )
        except Exception:
            log.exception("could not update the approval message")

    def approve(self, cid, user_id) -> str:
        if user_id not in self.cfg.approvers:
            return "not_authorised"
        if not self.store.transition(cid, ["pending_approval"], "approved", decided_by=user_id, decided_at=_utc_now()):
            return (self.store.cycle(cid) or {}).get("status", "unknown")
        report = final_report(self.store.entries(cid), Policy.load())
        when = self.now().strftime("%d %b %Y %I:%M %p")
        self._close_buttons(cid, f":white_check_mark: *{cycle_label(cid)}* support allowance approved by <@{user_id}> on {when}.")
        if self.cfg.hr_channel != self.cfg.approval_channel:
            self._post_report(self.cfg.hr_channel, cid, report, f"Support allowance - {cycle_label(cid)} (approved)")
        self.client.chat_postMessage(
            channel=self.cfg.hr_channel,
            text=(f"{self.cfg.hr_mention()} The support allowance details for *{cycle_label(cid)}* are updated "
                  f"and approved by <@{user_id}>. {report['people']} people, total *{report['grand_total_text']}*. "
                  f"The tables and CSV are above."),
        )
        return "approved"

    def reject(self, cid, user_id) -> str:
        if user_id not in self.cfg.approvers:
            return "not_authorised"
        if not self.store.transition(cid, ["pending_approval"], "rejected", decided_by=user_id, decided_at=_utc_now()):
            return (self.store.cycle(cid) or {}).get("status", "unknown")
        c = self.store.cycle(cid)
        self._close_buttons(cid, f":warning: *{cycle_label(cid)}* sent back for changes by <@{user_id}>.")
        self.client.chat_postMessage(
            channel=c["approval_channel"], thread_ts=c["approval_ts"],
            text=(f"<@{user_id}> tell me in this thread what to change (e.g. _remove Priya's night shift on 3 Oct_ "
                  f"or _add a day shift for Arun on 12 Oct_), then say _send it for approval again_."),
        )
        return "rejected"

    def resubmit(self, cid) -> str:
        if not self.store.transition(cid, ["rejected", "pending_approval"], "pending_approval"):
            return (self.store.cycle(cid) or {}).get("status", "unknown")
        self._close_buttons(cid, f"_{cycle_label(cid)}: superseded by an updated version below._")
        self.post_for_approval(cid)
        return "pending_approval"
