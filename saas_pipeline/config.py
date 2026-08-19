"""Shared constants for the SaaS consumption pipeline."""

PROVIDER_SHEETS = ["Snowflake", "Databricks", "Elastic", "Datadog", "Splunk"]

MONTH_ABBR = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

# Columns that need reformatting when a monthly CSV is split out of the workbook.
DATE_COLUMNS = ["usage_start_date", "usage_end_date"]
COST_COLUMN = "cost"

# Which date column determines which month a row belongs to.
MONTH_KEY_COLUMN = "usage_start_date"

# The S3 gap-check never looks earlier than this (year, month), even if the
# workbook someday contains older data and the trailing window would
# otherwise reach past it.
PIPELINE_START_MONTH = (2026, 1)
