"""Azure Function (HTTP trigger): pulls the latest consumption workbook from
SharePoint, splits it into per-provider/per-month CSVs, runs
process_saas_data_local.py on whatever isn't already in S3, and uploads the
results.

All config comes from environment variables (Function App "Environment
variables" / Application Settings - see local.settings.json.example for the
full list). Secrets (SHAREPOINT_CLIENT_SECRET, AWS keys) are meant to be Key
Vault references there, not plain values - see README.md.

Safe to call repeatedly / on every SharePoint file-drop notification: for each
provider it checks the most recent 12 months present in the workbook against
S3 individually, and only backfills whichever ones are actually missing - an
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
