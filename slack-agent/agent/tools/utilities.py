"""General-purpose helpers the agent can use for any request."""

import json
from datetime import date, timedelta

from anthropic import beta_tool


@beta_tool
def expand_date_range(start: str, end: str, weekdays_only: bool = False) -> str:
    """List every date between two dates (inclusive), with the weekday name. Use it to turn "1st to 7th Oct" into exact dates.

    Args:
        start: First date, YYYY-MM-DD.
        end: Last date, YYYY-MM-DD.
        weekdays_only: If true, skip Saturdays and Sundays.
    """
    try:
        first, last = date.fromisoformat(start), date.fromisoformat(end)
    except ValueError:
        return json.dumps({"error": "dates must be YYYY-MM-DD"})
    if last < first:
        return json.dumps({"error": "end is before start"})
    if (last - first).days > 366:
        return json.dumps({"error": "range is longer than a year"})
    days = []
    d = first
    while d <= last:
        if not (weekdays_only and d.weekday() >= 5):
            days.append({"date": d.isoformat(), "weekday": d.strftime("%A")})
        d += timedelta(days=1)
    return json.dumps({"count": len(days), "dates": days})


TOOLS = [expand_date_range]
