"""Detect the latest month already uploaded per provider in S3, and upload new output files.

Bucket layout: s3://<bucket>/<Provider>/<Year>/<Month (2-digit)>/<file>
e.g. s3://<bucket>/Databricks/2026/04/DatabricksApr_output.csv
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_latest_uploaded_month(s3_client, bucket: str, provider: str) -> tuple[int, int] | None:
    """Return (year, month) of the most recently uploaded month folder for this
    provider, or None if nothing has been uploaded yet."""
    provider_prefix = f"{provider}/"
    year_resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=provider_prefix, Delimiter="/")
    years = []
    for entry in year_resp.get("CommonPrefixes", []):
        part = entry["Prefix"][len(provider_prefix):].strip("/")
        if part.isdigit():
            years.append(int(part))
    if not years:
        return None
    latest_year = max(years)

    year_prefix = f"{provider_prefix}{latest_year}/"
    month_resp = s3_client.list_objects_v2(Bucket=bucket, Prefix=year_prefix, Delimiter="/")
    months = []
    for entry in month_resp.get("CommonPrefixes", []):
        part = entry["Prefix"][len(year_prefix):].strip("/")
        if part.isdigit():
            months.append(int(part))
    if not months:
        return None

    return latest_year, max(months)


def months_to_process(
    available_months: list[tuple[int, int]], latest_uploaded: tuple[int, int] | None
) -> list[tuple[int, int]]:
    """Given the (year, month) pairs present in the workbook and the latest one
    already uploaded, return the new ones to process, oldest first."""
    if latest_uploaded is None:
        return sorted(available_months)
    return sorted(m for m in available_months if m > latest_uploaded)


def upload_output_file(s3_client, bucket: str, provider: str, year: int, month: int, local_path: Path) -> str:
    key = f"{provider}/{year}/{month:02d}/{local_path.name}"
    logger.info("Uploading %s -> s3://%s/%s", local_path, bucket, key)
    s3_client.upload_file(str(local_path), bucket, key)
    return key
