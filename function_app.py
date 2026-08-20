"""Azure Functions: two independent entry points that both feed the same
pipeline, since the customer may submit the workbook either way.

- ProcessSaasConsumption (HTTP trigger): pulls the latest workbook from
  SharePoint, for use with the Power Automate flow.
- PollS3ForNewWorkbook (Timer trigger): on a schedule, pulls the latest
  workbook from a raw-upload location in S3, for when the customer drops the
  file directly into S3 instead of SharePoint.

Both then split the workbook into per-provider/per-month CSVs, run
process_saas_data_local.py on whatever isn't already in S3, and upload the
results - that shared logic lives in run_pipeline_for_workbook() below.

All config comes from environment variables (Function App "Environment
variables" / Application Settings - see local.settings.json.example for the
full list). Secrets (SHAREPOINT_CLIENT_SECRET, AWS keys) are meant to be Key
Vault references there, not plain values - see README.md.

Safe to call repeatedly / run on every schedule tick: for each provider it
checks the most recent 12 months present in the workbook against S3
individually, and only backfills whichever ones are actually missing - an
older gap gets filled just like the newest month would, and anything already
uploaded is left untouched.
"""
from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path

import azure.functions as func
import boto3

from process_saas_data_local import process_saas_data_local
from saas_pipeline import s3_sync
from saas_pipeline.config import PIPELINE_START_MONTH, PROVIDER_SHEETS
from saas_pipeline.sharepoint_client import (
    download_drive_item,
    find_latest_matching_file,
    get_graph_token,
    get_site_id,
    parse_site_url,
)
from saas_pipeline.split_monthly import read_provider_sheet, write_month_csv

app = func.FunctionApp()

REQUIRED_ENV_VARS = [
    "SHAREPOINT_TENANT_ID",
    "SHAREPOINT_CLIENT_ID",
    "SHAREPOINT_CLIENT_SECRET",
    "SHAREPOINT_SITE_URL",
    "SHAREPOINT_FOLDER_PATH",
    "S3_BUCKET",
]

S3_POLL_REQUIRED_ENV_VARS = [
    "S3_INPUT_BUCKET",
    "S3_BUCKET",
]


def _plan_months(provider: str, available: list, s3_client, bucket: str, s3_prefix: str, force_all_months: bool):
    if force_all_months:
        return sorted(m for m in available if m >= PIPELINE_START_MONTH)
    return s3_sync.months_to_process(s3_client, bucket, provider, available, prefix=s3_prefix)


def run_pipeline_for_workbook(
    workbook_path: Path, providers: list, bucket: str, s3_prefix: str, force_all_months: bool
) -> dict:
    """Split + process + upload every new month for each provider. Returns a
    per-provider summary suitable for logging/returning as the HTTP response."""
    s3_client = boto3.client("s3")
    summary = {}

    with tempfile.TemporaryDirectory() as tmp:
        monthly_csv_dir = Path(tmp) / "monthly_csv"

        for provider in providers:
            try:
                headers, date_col_indices, cost_col_idx, months = read_provider_sheet(workbook_path, provider)
            except ValueError as exc:
                logging.warning("[%s] %s", provider, exc)
                summary[provider] = {"error": str(exc)}
                continue

            available = sorted(months.keys())
            if not available:
                summary[provider] = {"processed": [], "note": "no rows with a usable usage_start_date"}
                continue

            eligible = [m for m in available if m >= PIPELINE_START_MONTH]
            window = sorted(eligible)[-s3_sync.DEFAULT_WINDOW_MONTHS:]
            to_process = _plan_months(provider, available, s3_client, bucket, s3_prefix, force_all_months)
            processed = []

            for year, month in to_process:
                rows = months[(year, month)]
                csv_path = write_month_csv(
                    headers, date_col_indices, cost_col_idx, rows, provider, year, month, monthly_csv_dir
                )
                output_path = Path(process_saas_data_local(str(csv_path)))
                s3_sync.upload_output_file(s3_client, bucket, provider, year, month, output_path, prefix=s3_prefix)
                processed.append(f"{year}-{month:02d}")

            summary[provider] = {
                "checked_window": [f"{y}-{m:02d}" for y, m in window],
                "already_in_s3": [f"{y}-{m:02d}" for y, m in window if (y, m) not in to_process],
                "processed": processed,
            }

    return summary


@app.function_name(name="ProcessSaasConsumption")
@app.route(route="process", methods=["POST"], auth_level=func.AuthLevel.FUNCTION)
def process_saas_consumption(req: func.HttpRequest) -> func.HttpResponse:
    missing = [name for name in REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        message = f"Missing required app settings: {', '.join(missing)}"
        logging.error(message)
        return func.HttpResponse(message, status_code=500)

    force_all_months = (req.params.get("force_all_months") or "").lower() == "true"
    providers_param = req.params.get("providers")
    providers = [p.strip() for p in providers_param.split(",")] if providers_param else PROVIDER_SHEETS

    tenant_id = os.environ["SHAREPOINT_TENANT_ID"]
    client_id = os.environ["SHAREPOINT_CLIENT_ID"]
    client_secret = os.environ["SHAREPOINT_CLIENT_SECRET"]
    site_hostname, site_path = parse_site_url(os.environ["SHAREPOINT_SITE_URL"])
    folder_path = os.environ["SHAREPOINT_FOLDER_PATH"]
    filename_contains = os.environ.get("SHAREPOINT_FILENAME_CONTAINS", "")
    bucket = os.environ["S3_BUCKET"]
    s3_prefix = os.environ.get("S3_PREFIX", "")

    with tempfile.TemporaryDirectory() as tmp:
        try:
            token = get_graph_token(tenant_id, client_id, client_secret)
            site_id = get_site_id(token, site_hostname, site_path)
            latest_item = find_latest_matching_file(token, site_id, folder_path, filename_contains)
            workbook_path = download_drive_item(latest_item, Path(tmp) / latest_item["name"])
        except Exception as exc:
            logging.exception("Failed to fetch workbook from SharePoint")
            return func.HttpResponse(f"SharePoint fetch failed: {exc}", status_code=502)

        try:
            summary = run_pipeline_for_workbook(workbook_path, providers, bucket, s3_prefix, force_all_months)
        except Exception as exc:
            logging.exception("Pipeline run failed")
            return func.HttpResponse(f"Pipeline run failed: {exc}", status_code=500)

    logging.info("Pipeline run summary: %s", summary)
    return func.HttpResponse(body=json.dumps(summary), status_code=200, mimetype="application/json")


@app.function_name(name="PollS3ForNewWorkbook")
@app.timer_trigger(schedule="%S3_POLL_SCHEDULE%", arg_name="timer", run_on_startup=False, use_monitor=True)
def poll_s3_for_new_workbook(timer: func.TimerRequest) -> None:
    """Check a raw-upload location in S3 for the customer's workbook and run
    the pipeline against whatever's most recently modified there. Runs on the
    schedule set by the S3_POLL_SCHEDULE app setting (NCRONTAB, e.g.
    '0 */15 * * * *' for every 15 minutes)."""
    missing = [name for name in S3_POLL_REQUIRED_ENV_VARS if not os.environ.get(name)]
    if missing:
        logging.error("S3 poll skipped - missing required app settings: %s", ", ".join(missing))
        return

    input_bucket = os.environ["S3_INPUT_BUCKET"]
    input_prefix = os.environ.get("S3_INPUT_PREFIX", "")
    input_filename_contains = os.environ.get("S3_INPUT_FILENAME_CONTAINS", "")
    bucket = os.environ["S3_BUCKET"]
    s3_prefix = os.environ.get("S3_PREFIX", "")
    force_all_months = (os.environ.get("S3_POLL_FORCE_ALL_MONTHS") or "").lower() == "true"

    s3_client = boto3.client("s3")

    latest = s3_sync.find_latest_input_file(s3_client, input_bucket, input_prefix, input_filename_contains)
    if latest is None:
        logging.info("No input workbook found under s3://%s/%s", input_bucket, input_prefix)
        return

    with tempfile.TemporaryDirectory() as tmp:
        workbook_path = Path(tmp) / Path(latest["Key"]).name
        try:
            s3_sync.download_input_file(s3_client, input_bucket, latest, workbook_path)
        except Exception:
            logging.exception("Failed to download input workbook from S3")
            return

        try:
            summary = run_pipeline_for_workbook(workbook_path, PROVIDER_SHEETS, bucket, s3_prefix, force_all_months)
        except Exception:
            logging.exception("Pipeline run failed (S3 poll trigger)")
            return

    logging.info("Pipeline run summary (S3 poll trigger): %s", summary)
