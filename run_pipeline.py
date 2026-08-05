#!/usr/bin/env python3
"""
End-to-end SaaS consumption pipeline.

For each provider sheet (Snowflake, Databricks, Elastic, Datadog, Splunk) in the
customer's workbook:

  1. Figure out which (year, month) folders are already uploaded to S3 for that
     provider, and skip straight past them - only new months get processed.
  2. Split the sheet into one raw CSV per new month (dates -> DD/MM/YY, cost -> plain
     number).
  3. Run process_saas_data_local.py on that CSV to produce the *_output.csv.
  4. Upload the output file to s3://<bucket>/<Provider>/<Year>/<Month>/.

Safe to re-run on the same or an updated workbook at any time: it always re-derives
"what's new" from what's already in S3, so it never re-processes or re-uploads a month
that's already there.

Examples:
    python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket my-saas-billing-bucket
    python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --no-upload
"""
from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path

from saas_pipeline.config import PROVIDER_SHEETS
from saas_pipeline.split_monthly import read_provider_sheet, write_month_csv
from saas_pipeline import s3_sync

logging.basicConfig(level="INFO", format="%(asctime)s|%(levelname)-8s|%(message)s")
logger = logging.getLogger(__name__)

THIS_DIR = Path(__file__).resolve().parent
PROCESS_SCRIPT = THIS_DIR / "process_saas_data_local.py"


def run_process_script(csv_path: Path) -> Path:
    logger.info("Running %s on %s", PROCESS_SCRIPT.name, csv_path)
    subprocess.run([sys.executable, str(PROCESS_SCRIPT), str(csv_path)], check=True)
    return csv_path.with_name(f"{csv_path.stem}_output{csv_path.suffix}")


def _plan_months(provider, available, s3_client, bucket, no_upload, force_all_months):
    """Decide which (year, month) pairs to process for this provider, and a
    human-readable description of the latest month already uploaded."""
    if no_upload:
        return sorted(available), "n/a (--no-upload)"

    latest = s3_sync.get_latest_uploaded_month(s3_client, bucket, provider)
    latest_desc = f"{latest[0]}-{latest[1]:02d}" if latest else "none uploaded yet"
    to_process = sorted(available) if force_all_months else s3_sync.months_to_process(available, latest)
    return to_process, latest_desc


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workbook", required=True, help="Path to the customer's consumption workbook (.xlsx)")
    parser.add_argument("--output-dir", default="data/monthly_csv", help="Local working directory for split/processed CSVs")
    parser.add_argument("--bucket", default=None, help="S3 bucket to upload output files to")
    parser.add_argument("--providers", nargs="+", default=PROVIDER_SHEETS, help="Subset of provider sheets to process")
    parser.add_argument("--no-upload", action="store_true", help="Skip the S3 step; only split + process locally")
    parser.add_argument(
        "--force-all-months",
        action="store_true",
        help="Ignore what's already in S3 and (re)process every month present in the workbook",
    )
    args = parser.parse_args()

    if not args.no_upload and not args.bucket:
        parser.error("--bucket is required unless --no-upload is set")

    workbook_path = Path(args.workbook).expanduser()
    output_dir = Path(args.output_dir).expanduser()

    s3_client = None
    if not args.no_upload:
        import boto3

        s3_client = boto3.client("s3")

    for provider in args.providers:
        headers, date_col_indices, cost_col_idx, months = read_provider_sheet(workbook_path, provider)
        available = sorted(months.keys())
        if not available:
            logger.info("[%s] no rows with a usable usage_start_date; skipping", provider)
            continue

        to_process, latest_desc = _plan_months(
            provider, available, s3_client, args.bucket, args.no_upload, args.force_all_months
        )

        if not to_process:
            logger.info("[%s] already up to date (latest uploaded: %s); nothing to do", provider, latest_desc)
            continue

        logger.info(
            "[%s] latest uploaded: %s | workbook has: %s | will process: %s",
            provider,
            latest_desc,
            [f"{y}-{m:02d}" for y, m in available],
            [f"{y}-{m:02d}" for y, m in to_process],
        )

        for year, month in to_process:
            rows = months[(year, month)]
            csv_path = write_month_csv(
                headers, date_col_indices, cost_col_idx, rows, provider, year, month, output_dir
            )
            output_path = run_process_script(csv_path)

            if s3_client is not None:
                s3_sync.upload_output_file(s3_client, args.bucket, provider, year, month, output_path)

    logger.info("Pipeline run complete.")


if __name__ == "__main__":
    main()
