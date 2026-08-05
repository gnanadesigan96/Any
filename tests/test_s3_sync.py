from pathlib import Path

import boto3
import pytest
from moto import mock_aws

from saas_pipeline import s3_sync


BUCKET = "test-saas-billing"


@pytest.fixture
def s3_client():
    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        client.create_bucket(Bucket=BUCKET)
        yield client


def _put(client, key):
    client.put_object(Bucket=BUCKET, Key=key, Body=b"data")


def test_no_uploads_yet_returns_none(s3_client):
    assert s3_sync.get_latest_uploaded_month(s3_client, BUCKET, "Databricks") is None


def test_finds_latest_month_within_latest_year(s3_client):
    for key in [
        "Databricks/2026/01/DatabricksJan_output.csv",
        "Databricks/2026/02/DatabricksFeb_output.csv",
        "Databricks/2026/03/DatabricksMar_output.csv",
    ]:
        _put(s3_client, key)

    assert s3_sync.get_latest_uploaded_month(s3_client, BUCKET, "Databricks") == (2026, 3)


def test_ignores_other_providers(s3_client):
    _put(s3_client, "Databricks/2026/05/DatabricksMay_output.csv")
    _put(s3_client, "Snowflake/2026/01/SnowflakeJan_output.csv")

    assert s3_sync.get_latest_uploaded_month(s3_client, BUCKET, "Databricks") == (2026, 5)
    assert s3_sync.get_latest_uploaded_month(s3_client, BUCKET, "Snowflake") == (2026, 1)


def test_picks_latest_year_not_just_latest_month_number(s3_client):
    # 2027-01 is chronologically newer than 2026-12 even though "01" < "12" alphabetically
    _put(s3_client, "Databricks/2026/12/DatabricksDec_output.csv")
    _put(s3_client, "Databricks/2027/01/DatabricksJan_output.csv")

    assert s3_sync.get_latest_uploaded_month(s3_client, BUCKET, "Databricks") == (2027, 1)


def test_months_to_process_none_uploaded_yet():
    available = [(2026, 1), (2026, 2), (2026, 3)]
    assert s3_sync.months_to_process(available, None) == available


def test_months_to_process_skips_already_uploaded():
    available = [(2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6)]
    assert s3_sync.months_to_process(available, (2026, 3)) == [(2026, 4), (2026, 5), (2026, 6)]


def test_months_to_process_up_to_date_returns_empty():
    available = [(2026, 1), (2026, 2), (2026, 3)]
    assert s3_sync.months_to_process(available, (2026, 3)) == []


def test_upload_output_file_uses_provider_year_month_key(tmp_path, s3_client):
    local_file = tmp_path / "DatabricksApr_output.csv"
    local_file.write_text("a,b\n1,2\n")

    key = s3_sync.upload_output_file(s3_client, BUCKET, "Databricks", 2026, 4, local_file)

    assert key == "Databricks/2026/04/DatabricksApr_output.csv"
    obj = s3_client.get_object(Bucket=BUCKET, Key=key)
    assert obj["Body"].read() == b"a,b\n1,2\n"
