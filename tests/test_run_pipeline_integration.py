"""End-to-end test of the split -> process -> upload flow, using a small synthetic
workbook (not customer data) so it's safe to run anywhere."""
import sys
from pathlib import Path

import boto3
import openpyxl
import pytest
from moto import mock_aws

import run_pipeline

BUCKET = "test-saas-billing"
HEADERS = [
    "account_name", "account_number", "payer_account_id", "bill_type", "region",
    "charge_type", "usage_start_date", "usage_end_date", "product", "service",
    "cost", "team", "usage_type", "Line of Business", "Pillar",
]


def _make_workbook(path: Path):
    import datetime

    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for provider in ["Databricks", "Snowflake"]:
        ws = wb.create_sheet(provider)
        ws.append(HEADERS)
        for month in (1, 2, 3, 4):
            ws.append([
                "acct", "acct", "acct", "on-demand", "us", "Usage",
                datetime.datetime(2026, month, 1), datetime.datetime(2026, month, 1),
                "svc", "svc", 100.0 * month, "team-x", "5303", "LoB", "Pillar",
            ])
    wb.save(path)


@pytest.fixture
def workbook(tmp_path):
    path = tmp_path / "Consumption.xlsx"
    _make_workbook(path)
    return path


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield client


def _run(workbook, output_dir, extra_args=()):
    argv = [
        "run_pipeline.py",
        "--workbook", str(workbook),
        "--output-dir", str(output_dir),
        "--bucket", BUCKET,
        *extra_args,
    ]
    old_argv = sys.argv
    sys.argv = argv
    try:
        run_pipeline.main()
    finally:
        sys.argv = old_argv


def test_first_run_uploads_every_month(workbook, s3_client, tmp_path, monkeypatch):
    monkeypatch.setattr(run_pipeline, "run_process_script", lambda csv_path: csv_path)

    _run(workbook, tmp_path / "out", extra_args=["--providers", "Databricks", "Snowflake"])

    keys = {
        obj["Key"] for obj in s3_client.list_objects_v2(Bucket=BUCKET).get("Contents", [])
    }
    assert keys == {
        "databricks/2026/01/DatabricksJan.csv",
        "databricks/2026/02/DatabricksFeb.csv",
        "databricks/2026/03/DatabricksMar.csv",
        "databricks/2026/04/DatabricksApr.csv",
        "snowflake/2026/01/SnowflakeJan.csv",
        "snowflake/2026/02/SnowflakeFeb.csv",
        "snowflake/2026/03/SnowflakeMar.csv",
        "snowflake/2026/04/SnowflakeApr.csv",
    }


def test_second_run_only_uploads_new_months(workbook, s3_client, tmp_path, monkeypatch):
    monkeypatch.setattr(run_pipeline, "run_process_script", lambda csv_path: csv_path)

    # Simulate "we already have everything through Feb" for Databricks only.
    s3_client.put_object(Bucket=BUCKET, Key="databricks/2026/01/DatabricksJan.csv", Body=b"x")
    s3_client.put_object(Bucket=BUCKET, Key="databricks/2026/02/DatabricksFeb.csv", Body=b"x")

    _run(workbook, tmp_path / "out", extra_args=["--providers", "Databricks"])

    keys = {
        obj["Key"] for obj in s3_client.list_objects_v2(Bucket=BUCKET).get("Contents", [])
    }
    assert keys == {
        "databricks/2026/01/DatabricksJan.csv",
        "databricks/2026/02/DatabricksFeb.csv",
        "databricks/2026/03/DatabricksMar.csv",
        "databricks/2026/04/DatabricksApr.csv",
    }
