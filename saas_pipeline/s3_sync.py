"""Check which months are already uploaded per provider in S3, and upload new ones.

Bucket layout: s3://<bucket>/<Provider>/<Year>/<Month (2-digit)>/<file>
e.g. s3://<bucket>/Databricks/2026/04/DatabricksApr_output.csv
"""
from __future__ import annotations

import logging
from pathlib import Path

from saas_pipeline.config import PIPELINE_START_MONTH

logger = logging.getLogger(__name__)

DEFAULT_WINDOW_MONTHS = 12


def month_exists(s3_client, bucket: str, provider: str, year: int, month: int) -> bool:
    """Return True if a file has already been uploaded under this provider's
    year/month folder in S3."""
    prefix = f"{provider}/{year}/{month:02d}/"
    response = s3_client.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    return bool(response.get("Contents"))


def months_to_process(
    s3_client,
    bucket: str,
    provider: str,
    available_months: list[tuple[int, int]],
    window_size: int = DEFAULT_WINDOW_MONTHS,
    floor: tuple[int, int] | None = PIPELINE_START_MONTH,
) -> list[tuple[int, int]]:
    """Check the most recent `window_size` eligible months present in the
    workbook and return whichever ones don't already have a file in S3,
    oldest first.

    This is a per-month gap check, not a moving cutoff: a month older than the
    newest one but still missing (e.g. February was skipped while January and
    March both uploaded fine) gets backfilled too. Months older than the
    window are left alone even if they're missing, and months before `floor`
    (default: PIPELINE_START_MONTH) are never considered at all, however wide
    the window is.
    """
    eligible = [m for m in available_months if floor is None or m >= floor]
    window = sorted(eligible)[-window_size:]
    return [month for month in window if not month_exists(s3_client, bucket, provider, *month)]


def upload_output_file(s3_client, bucket: str, provider: str, year: int, month: int, local_path: Path) -> str:
    key = f"{provider}/{year}/{month:02d}/{local_path.name}"
    logger.info("Uploading %s -> s3://%s/%s", local_path, bucket, key)
    s3_client.upload_file(str(local_path), bucket, key)
    return key
