"""Tools for calculating and allocating on-call / support allowances."""

import json
import os

from anthropic import beta_tool

from ..allowance import Ledger, Policy, calculate
from ..context import current_request

_ledger = None


def _get_ledger() -> Ledger:
    global _ledger
    if _ledger is None:
        _ledger = Ledger(os.environ.get("ALLOWANCE_DB_PATH", "allowance_ledger.db"))
    return _ledger


def _approvers() -> set:
    return {u.strip() for u in os.environ.get("ALLOWANCE_APPROVERS", "").split(",") if u.strip()}


@beta_tool
def get_allowance_policy() -> str:
    """Show the current support allowance policy: currency, day rates for weekday / weekend / holiday, half-day factor and the configured holiday list."""
    p = Policy.load()
    return json.dumps({
        "currency": p.currency,
        "rates": p.rates,
        "half_day_factor": p.half_day_factor,
        "weekend_days": sorted(p.weekend_days),
        "holidays": p.holidays,
    })


@beta_tool
def calculate_support_allowance(person: str, support_dates: list[str], half_days: list[str] | None = None) -> str:
    """Preview the allowance for a person's support days WITHOUT saving anything. Use this when someone asks "how much" or before allocating.

    Args:
        person: Full name of the person who was on support, e.g. "Priya Kumar".
        support_dates: Every date they were on support, as YYYY-MM-DD strings. Expand ranges into individual dates first.
        half_days: Optional subset of support_dates that were only half days.
    """
    try:
        result = calculate(person, support_dates, half_days or [])
    except ValueError as e:
        return json.dumps({"error": str(e)})
    result["already_recorded"] = _get_ledger().already_recorded(person, [d["date"] for d in result["days"]])
    return json.dumps(result)


@beta_tool
def allocate_support_allowance(person: str, support_dates: list[str], half_days: list[str] | None = None) -> str:
    """Calculate AND record (allocate) the allowance for a person's support days in the ledger. Only call this when the user asked to allocate / record / approve the payment. Fails if any of the days were already allocated for that person.

    Args:
        person: Full name of the person who was on support, e.g. "Priya Kumar".
        support_dates: Every date they were on support, as YYYY-MM-DD strings. Expand ranges into individual dates first.
        half_days: Optional subset of support_dates that were only half days.
    """
    req = current_request.get(None)
    approvers = _approvers()
    if approvers and (req is None or req.user_id not in approvers):
        return json.dumps({
            "error": "Not authorised: only configured allowance approvers can allocate. "
                     "You can still preview the amount with calculate_support_allowance."
        })
    try:
        result = calculate(person, support_dates, half_days or [])
        _get_ledger().record(result, recorded_by=req.user_name if req else None)
    except ValueError as e:
        return json.dumps({"error": str(e)})
    result["status"] = "allocated"
    return json.dumps(result)


@beta_tool
def get_allowance_summary(person: str = "", month: str = "") -> str:
    """Report allowances already allocated, totalled per person. Leave a filter empty to include everyone / all months.

    Args:
        person: Optional person name to filter by.
        month: Optional month to filter by, as YYYY-MM (e.g. "2026-10").
    """
    return json.dumps(_get_ledger().summary(person, month))


TOOLS = [get_allowance_policy, calculate_support_allowance, allocate_support_allowance, get_allowance_summary]
