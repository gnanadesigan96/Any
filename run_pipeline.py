#!/usr/bin/env python3
"""
End-to-end SaaS consumption pipeline.

For each provider sheet (Snowflake, Databricks, Elastic, Datadog, Splunk) in the
customer's workbook:

  1. Look at the most recent 12 months present in the workbook, and check each one
     individually against S3 - a month already uploaded is skipped, a missing one
     (even an older gap, not just the newest month) gets backfilled.
  2. Split the sheet into one raw CSV per month being processed (dates -> DD/MM/YY,
     cost -> plain number).
  3. Run process_saas_data_local.py on that CSV to produce the *_output.csv.
  4. Upload the output file to s3://<bucket>/<prefix>/<Provider>/<Year>/<Month>/
     (--s3-prefix is whatever sits between the bucket root and the provider
     folders, e.g. "saas-upload" - leave unset if they sit at the bucket root).

Safe to re-run on the same or an updated workbook at any time: it always re-checks S3
itself, so it never re-processes or re-uploads a month that's already there.

Examples:
    python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --bucket flatiron-saas-upload --s3-prefix saas-upload
    python run_pipeline.py --workbook "2026 Consumption Costs.xlsx" --no-upload
"""
from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from saas_pipeline.config import PIPELINE_START_MONTH, PROVIDER_SHEETS
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


def _plan_months(provider, available, s3_client, bucket, s3_prefix, no_upload, force_all_months):
    """Decide which (year, month) pairs to process for this provider."""
    if no_upload or force_all_months:
        return sorted(m for m in available if m >= PIPELINE_START_MONTH)
    return s3_sync.months_to_process(s3_client, bucket, provider, available, prefix=s3_prefix)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workbook", required=True, help="Path to the customer's consumption workbook (.xlsx)")
    parser.add_argument("--output-dir", default="data/monthly_csv", help="Local working directory for split/processed CSVs")
    parser.add_argument("--bucket", default=None, help="S3 bucket to upload output files to")
    parser.add_argument(
        "--s3-prefix",
        default="",
        help="Path between the bucket root and the provider folders, e.g. 'saas-upload'. "
        "Leave unset if the provider folders sit directly at the bucket root.",
    )
    parser.add_argument("--providers", nargs="+", default=PROVIDER_SHEETS, help="Subset of provider sheets to process")
    parser.add_argument("--no-upload", action="store_true", help="Skip the S3 step; only split + process locally")
    parser.add_argument(
        "--force-all-months",
        action="store_true",
        help="Ignore what's already in S3 and (re)process every month present in the workbook",
    )
    parser.add_argument(
        "--aws-role-arn",
        default=None,
        help="If set, assume this role (via STS, using AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY as the base "
        "identity) for S3 access instead of using those credentials directly.",
    )
    parser.add_argument("--aws-role-session-name", default="saas-pipeline", help="RoleSessionName for --aws-role-arn")
    parser.add_argument("--aws-role-external-id", default=None, help="Optional ExternalId for --aws-role-arn")
    args = parser.parse_args()

    if not args.no_upload and not args.bucket:
        parser.error("--bucket is required unless --no-upload is set")

    workbook_path = Path(args.workbook).expanduser()
    output_dir = Path(args.output_dir).expanduser()

    s3_client = None
    if not args.no_upload:
        if args.aws_role_arn:
            from saas_pipeline.aws_auth import assume_role_s3_client

            s3_client = assume_role_s3_client(
                base_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                base_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
                role_arn=args.aws_role_arn,
                role_session_name=args.aws_role_session_name,
                external_id=args.aws_role_external_id,
                region_name=os.environ.get("AWS_DEFAULT_REGION"),
            )
        else:
            import boto3

            s3_client = boto3.client("s3")

    for provider in args.providers:
        headers, date_col_indices, cost_col_idx, months = read_provider_sheet(workbook_path, provider)
        available = sorted(months.keys())
        if not available:
            logger.info("[%s] no rows with a usable usage_start_date; skipping", provider)
            continue

        to_process = _plan_months(
            provider, available, s3_client, args.bucket, args.s3_prefix, args.no_upload, args.force_all_months
        )

        if not to_process:
            logger.info("[%s] all months in the trailing window are already in S3; nothing to do", provider)
            continue

        logger.info(
            "[%s] workbook has: %s | missing/will process: %s",
            provider,
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
                s3_sync.upload_output_file(
                    s3_client, args.bucket, provider, year, month, output_path, prefix=args.s3_prefix
                )

    logger.info("Pipeline run complete.")


if __name__ == "__main__":
    main()
