"""Slack button, menu and modal handlers for the support-allowance workflow."""

import json

from . import blocks as B
from .config import Policy
from .workflow import get_instance


def _ephemeral(client, body, text):
    channel = (body.get("channel") or {}).get("id") or body["user"]["id"]
    client.chat_postEphemeral(channel=channel, user=body["user"]["id"], text=text)


def register(app):

    # -- reviewer: accept / reject flagged entries ----------------------------

    def _review(ack, body, client, decisions):
        ack()
        wf = get_instance()
        user = body["user"]["id"]
        results = [wf.review(entry_id, decision, user) for entry_id, decision in decisions]
        if "not_authorised" in results:
            _ephemeral(client, body, f"Only <@{wf.cfg.reviewer}> can accept or reject flagged entries.")
            return
        msg = body["message"]
        wf.refresh_review_message(body["channel"]["id"], msg["ts"], B.row_ids(msg.get("blocks")))

    @app.action(B.REVIEW_ACCEPT)
    def review_accept(ack, body, client):
        _review(ack, body, client, [(int(body["actions"][0]["value"]), "accepted")])

    @app.action(B.REVIEW_REJECT)
    def review_reject(ack, body, client):
        _review(ack, body, client, [(int(body["actions"][0]["value"]), "rejected")])

    @app.action(B.REVIEW_ALL)
    def review_all(ack, body, client):
        v = json.loads(body["actions"][0]["value"])
        _review(ack, body, client, [(int(i), v["d"]) for i in v["ids"]])

    # -- approver: approve / raise concern -----------------------------------

    @app.action(B.APPROVE)
    def approve(ack, body, client):
        ack()
        wf = get_instance()
        result = wf.approve(body["actions"][0]["value"], body["user"]["id"])
        if result == "not_authorised":
            _ephemeral(client, body, f"Only <@{wf.cfg.approver}> can give the final approval.")
        elif result != "approved":
            _ephemeral(client, body, f"Nothing to do - this month is *{result.replace('_', ' ')}*.")

    @app.action(B.RAISE_CONCERN)
    def raise_concern(ack, body, client):
        ack()
        wf = get_instance()
        cid = body["actions"][0]["value"]
        if body["user"]["id"] != wf.cfg.approver:
            _ephemeral(client, body, f"Only <@{wf.cfg.approver}> can raise a concern on the final approval.")
            return
        entries = wf.store.entries(cid, payable_only=True)
        client.views_open(trigger_id=body["trigger_id"], view=B.concern_modal(cid, entries, Policy.load()))

    @app.view(B.CONCERN_MODAL)
    def concern_submitted(ack, body, view):
        ack()
        wf = get_instance()
        v = B.modal_values(view)
        cid = json.loads(view["private_metadata"])["cid"]
        wf.raise_concern(cid, body["user"]["id"], v["concern"], v.get("entries"))

    # -- reviewer: fix rows in the concern table ------------------------------

    @app.action(B.CONCERN_ROW)
    def concern_row(ack, body, client):
        ack()
        wf = get_instance()
        act = body["actions"][0]
        action, entry_id = (act.get("selected_option") or {}).get("value", act.get("value")).split(":")
        entry_id = int(entry_id)
        user = body["user"]["id"]
        if action == "edit":
            e = wf.store.entry(entry_id)
            if err := wf.check_reviewer_edit(e["cycle_id"], user):
                _ephemeral(client, body, err)
                return
            client.views_open(trigger_id=body["trigger_id"], view=B.edit_modal(e, {"id": entry_id}))
            return
        if err := wf.set_row_removed(entry_id, user, removed=(action == "remove")):
            _ephemeral(client, body, err)

    @app.view(B.EDIT_MODAL)
    def edit_submitted(ack, body, view):
        v = B.modal_values(view)
        err = get_instance().edit_entry(json.loads(view["private_metadata"])["id"], body["user"]["id"],
                                        v["date"], v["shift"], v.get("extra"))
        ack(response_action="errors", errors={"date": err}) if err else ack()

    @app.action(B.CONCERN_ADD)
    def concern_add(ack, body, client):
        ack()
        wf = get_instance()
        cid = body["actions"][0]["value"]
        if err := wf.check_reviewer_edit(cid, body["user"]["id"]):
            _ephemeral(client, body, err)
            return
        client.views_open(trigger_id=body["trigger_id"], view=B.add_modal({"cid": cid}))

    @app.view(B.ADD_MODAL)
    def add_submitted(ack, body, view):
        v = B.modal_values(view)
        err = get_instance().add_entry(json.loads(view["private_metadata"])["cid"], body["user"]["id"],
                                       v["person"], v["date"], v["shift"], v.get("extra"))
        ack(response_action="errors", errors={"date": err}) if err else ack()

    @app.action(B.CONCERN_RESPOND)
    def concern_respond(ack, body, client):
        ack()
        wf = get_instance()
        cid = body["actions"][0]["value"]
        if body["user"]["id"] != wf.cfg.reviewer:
            _ephemeral(client, body, f"Only <@{wf.cfg.reviewer}> can respond to this concern.")
            return
        client.views_open(trigger_id=body["trigger_id"], view=B.respond_modal(cid, wf.store.cycle(cid)))

    @app.view(B.RESPOND_MODAL)
    def respond_submitted(ack, body, view):
        ack()
        v = B.modal_values(view)
        get_instance().respond_to_concern(json.loads(view["private_metadata"])["cid"], body["user"]["id"], v["response"])
