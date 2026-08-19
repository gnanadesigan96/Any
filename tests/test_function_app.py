import datetime
import json
from pathlib import Path
from unittest.mock import patch

import azure.functions as func
import boto3
import openpyxl
import pytest
from moto import mock_aws

import function_app

BUCKET = "test-saas-billing"
HEADERS = [
    "account_name", "account_number", "payer_account_id", "bill_type", "region",
    "charge_type", "usage_start_date", "usage_end_date", "product", "service",
    "cost", "team", "usage_type", "Line of Business", "Pillar",
]

REQUIRED_ENV = {
    "SHAREPOINT_TENANT_ID": "tenant-1",
    "SHAREPOINT_CLIENT_ID": "client-1",
    "SHAREPOINT_CLIENT_SECRET": "secret-1",
    "SHAREPOINT_SITE_URL": "contoso.sharepoint.com/sites/Billing",
    "SHAREPOINT_FOLDER_PATH": "Shared Documents",
    "S3_BUCKET": BUCKET,
}


def _make_workbook(path: Path):
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    for provider in ["Databricks"]:
        ws = wb.create_sheet(provider)
        ws.append(HEADERS)
        for month in (1, 2, 3, 4):
            ws.append([
                "acct", "acct", "acct", "on-demand", "us", "Usage",
                datetime.datetime(2026, month, 1), datetime.datetime(2026, month, 1),
                "svc", "svc", 100.0 * month, "team-x", "5303", "LoB", "Pillar",
            ])
    wb.save(path)


def _make_request(params=None):
    return func.HttpRequest(method="POST", url="/api/process", params=params or {}, body=b"")


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield client


def test_missing_env_vars_returns_500(monkeypatch):
    for key in function_app.REQUIRED_ENV_VARS:
        monkeypatch.delenv(key, raising=False)

    response = function_app.process_saas_consumption(_make_request())

    assert response.status_code == 500
    assert "SHAREPOINT_TENANT_ID" in response.get_body().decode()


def test_sharepoint_fetch_failure_returns_502(monkeypatch):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    with patch("function_app.get_graph_token", side_effect=RuntimeError("auth failed")):
        response = function_app.process_saas_consumption(_make_request())

    assert response.status_code == 502
    assert "auth failed" in response.get_body().decode()


def test_happy_path_backfills_only_missing_months_in_window(monkeypatch, tmp_path, s3_client):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)

    workbook_path = tmp_path / "2026 Consumption Costs.xlsx"
    _make_workbook(workbook_path)

    # Simulate Jan and Mar already uploaded, but Feb somehow missing - a gap,
    # not just a moving cutoff. Apr isn't uploaded yet either.
    s3_client.put_object(Bucket=BUCKET, Key="Databricks/2026/01/DatabricksJan_output.csv", Body=b"x")
    s3_client.put_object(Bucket=BUCKET, Key="Databricks/2026/03/DatabricksMar_output.csv", Body=b"x")

    fake_item = {
        "name": "2026 Consumption Costs.xlsx",
        "lastModifiedDateTime": "2026-07-01T00:00:00Z",
        "@microsoft.graph.downloadUrl": "https://presigned.example/file.xlsx",
    }

    with patch("function_app.get_graph_token", return_value="tok"), \
         patch("function_app.get_site_id", return_value="site-abc"), \
         patch("function_app.find_latest_matching_file", return_value=fake_item), \
         patch("function_app.download_drive_item", side_effect=lambda item, dest: workbook_path):
        response = function_app.process_saas_consumption(_make_request(params={"providers": "Databricks"}))

    assert response.status_code == 200
    body = json.loads(response.get_body())
    assert body["Databricks"]["checked_window"] == ["2026-01", "2026-02", "2026-03", "2026-04"]
    assert body["Databricks"]["already_in_s3"] == ["2026-01", "2026-03"]
    assert body["Databricks"]["processed"] == ["2026-02", "2026-04"]

    keys = {obj["Key"] for obj in s3_client.list_objects_v2(Bucket=BUCKET).get("Contents", [])}
    assert keys == {
        "Databricks/2026/01/DatabricksJan_output.csv",
        "Databricks/2026/02/DatabricksFeb_output.csv",
        "Databricks/2026/03/DatabricksMar_output.csv",
        "Databricks/2026/04/DatabricksApr_output.csv",
    }


def test_uploads_under_s3_prefix_when_set(monkeypatch, tmp_path, s3_client):
    for key, value in REQUIRED_ENV.items():
        monkeypatch.setenv(key, value)
    monkeypatch.setenv("S3_PREFIX", "saas-upload")

    workbook_path = tmp_path / "2026 Consumption Costs.xlsx"
    _make_workbook(workbook_path)

    # Already uploaded, but under the prefixed path - without S3_PREFIX wired
    # through correctly, the pipeline would fail to see this and reprocess it.
    s3_client.put_object(Bucket=BUCKET, Key="saas-upload/Databricks/2026/01/DatabricksJan_output.csv", Body=b"x")

    fake_item = {
        "name": "2026 Consumption Costs.xlsx",
        "lastModifiedDateTime": "2026-07-01T00:00:00Z",
        "@microsoft.graph.downloadUrl": "https://presigned.example/file.xlsx",
    }

    with patch("function_app.get_graph_token", return_value="tok"), \
         patch("function_app.get_site_id", return_value="site-abc"), \
         patch("function_app.find_latest_matching_file", return_value=fake_item), \
         patch("function_app.download_drive_item", side_effect=lambda item, dest: workbook_path):
        response = function_app.process_saas_consumption(_make_request(params={"providers": "Databricks"}))

    assert response.status_code == 200
    body = json.loads(response.get_body())
    assert body["Databricks"]["already_in_s3"] == ["2026-01"]
    assert body["Databricks"]["processed"] == ["2026-02", "2026-03", "2026-04"]

    keys = {obj["Key"] for obj in s3_client.list_objects_v2(Bucket=BUCKET).get("Contents", [])}
    assert keys == {
        "saas-upload/Databricks/2026/01/DatabricksJan_output.csv",
        "saas-upload/Databricks/2026/02/DatabricksFeb_output.csv",
        "saas-upload/Databricks/2026/03/DatabricksMar_output.csv",
        "saas-upload/Databricks/2026/04/DatabricksApr_output.csv",
    }
