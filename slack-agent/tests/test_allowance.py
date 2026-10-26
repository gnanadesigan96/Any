import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent.allowance import Ledger, Policy, calculate  # noqa: E402

POLICY = Policy(
    currency="INR",
    rates={"weekday": 1000.0, "weekend": 2000.0, "holiday": 3000.0},
    half_day_factor=0.5,
    weekend_days=frozenset({"Saturday", "Sunday"}),
    holidays={"2026-10-02": "Gandhi Jayanti"},
)


def test_weekday_weekend_holiday_rates():
    # 2026-10-01 Thu, 2026-10-02 Fri (holiday), 2026-10-03 Sat
    r = calculate("Priya", ["2026-10-01", "2026-10-02", "2026-10-03"], policy=POLICY)
    assert [d["day_type"] for d in r["days"]] == ["weekday", "holiday", "weekend"]
    assert r["total"] == 6000
    assert r["subtotals"] == {"weekday": 1000, "weekend": 2000, "holiday": 3000}


def test_half_day_and_dedup_of_input_dates():
    r = calculate("Priya", ["2026-10-03", "2026-10-01", "2026-10-01"], half_days=["2026-10-03"], policy=POLICY)
    assert r["day_count"] == 2
    assert r["days"][0]["date"] == "2026-10-01"
    assert r["total"] == 1000 + 1000


@pytest.mark.parametrize("dates,halves,msg", [
    ([], [], "at least one"),
    (["2026-13-01"], [], "valid date"),
    (["2026-10-01"], ["2026-10-05"], "half_days must also appear"),
])
def test_invalid_input(dates, halves, msg):
    with pytest.raises(ValueError, match=msg):
        calculate("Priya", dates, halves, policy=POLICY)


def test_ledger_blocks_double_payment_and_summarises(tmp_path):
    ledger = Ledger(tmp_path / "l.db")
    ledger.record(calculate("Priya Kumar", ["2026-10-01", "2026-10-03"], policy=POLICY), recorded_by="Lead")
    with pytest.raises(ValueError, match="already has allowance recorded for: 2026-10-03"):
        ledger.record(calculate("priya  kumar", ["2026-10-03", "2026-10-04"], policy=POLICY))
    ledger.record(calculate("Arun", ["2026-11-02"], policy=POLICY))

    oct_only = ledger.summary(month="2026-10")["people"]
    assert oct_only == [{"person": "Priya Kumar", "currency": "INR", "day_count": 2,
                         "total": 3000, "dates": "2026-10-01, 2026-10-03"}]
    assert {p["person"] for p in ledger.summary()["people"]} == {"Priya Kumar", "Arun"}


def test_bundled_policy_loads():
    p = Policy.load()
    assert set(p.rates) >= {"weekday", "weekend", "holiday"}


def test_allocate_tool_respects_approvers(tmp_path, monkeypatch):
    from agent.context import RequestContext, current_request
    from agent.tools import support_allowance as sa

    monkeypatch.setattr(sa, "_ledger", Ledger(tmp_path / "t.db"))
    monkeypatch.setenv("ALLOWANCE_APPROVERS", "UBOSS")

    token = current_request.set(RequestContext("UOTHER", "Someone", "C1"))
    try:
        out = json.loads(sa.allocate_support_allowance.call({"person": "Priya", "support_dates": ["2026-10-01"]}))
        assert "Not authorised" in out["error"]
    finally:
        current_request.reset(token)

    token = current_request.set(RequestContext("UBOSS", "Boss", "C1"))
    try:
        out = json.loads(sa.allocate_support_allowance.call({"person": "Priya", "support_dates": ["2026-10-01"]}))
        assert out["status"] == "allocated"
    finally:
        current_request.reset(token)
