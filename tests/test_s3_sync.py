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


def test_month_exists_false_when_nothing_uploaded(s3_client):
    assert s3_sync.month_exists(s3_client, BUCKET, "Databricks", 2026, 4) is False


def test_month_exists_true_when_a_file_is_there(s3_client):
    _put(s3_client, "Databricks/2026/04/DatabricksApr_output.csv")
    assert s3_sync.month_exists(s3_client, BUCKET, "Databricks", 2026, 4) is True


def test_month_exists_ignores_other_providers_and_months(s3_client):
    _put(s3_client, "Databricks/2026/04/DatabricksApr_output.csv")
    assert s3_sync.month_exists(s3_client, BUCKET, "Databricks", 2026, 5) is False
    assert s3_sync.month_exists(s3_client, BUCKET, "Snowflake", 2026, 4) is False


def test_months_to_process_none_uploaded_processes_whole_window(s3_client):
    available = [(2026, 1), (2026, 2), (2026, 3)]
    assert s3_sync.months_to_process(s3_client, BUCKET, "Databricks", available) == available


def test_months_to_process_skips_months_already_present(s3_client):
    for key in [
        "Databricks/2026/01/DatabricksJan_output.csv",
        "Databricks/2026/02/DatabricksFeb_output.csv",
    ]:
        _put(s3_client, key)
    available = [(2026, 1), (2026, 2), (2026, 3), (2026, 4)]

    assert s3_sync.months_to_process(s3_client, BUCKET, "Databricks", available) == [(2026, 3), (2026, 4)]


def test_months_to_process_backfills_an_older_gap_not_just_the_newest_month(s3_client):
    # January and March both uploaded fine, February was somehow skipped.
    for key in [
        "Databricks/2026/01/DatabricksJan_output.csv",
        "Databricks/2026/03/DatabricksMar_output.csv",
        "Databricks/2026/04/DatabricksApr_output.csv",
    ]:
        _put(s3_client, key)
    available = [(2026, 1), (2026, 2), (2026, 3), (2026, 4)]

    assert s3_sync.months_to_process(s3_client, BUCKET, "Databricks", available) == [(2026, 2)]


def test_months_to_process_ignores_gaps_older_than_the_window(s3_client):
    available = [(2025, 1), (2025, 2), (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5)]
    # Only the single oldest month (2025-01) falls outside a trailing window of 6
    # out of these 7 available months - it's missing from S3 too, but should
    # never be flagged since it's outside the window. floor=None isolates the
    # window-slicing behavior from the separate PIPELINE_START_MONTH floor.
    to_process = s3_sync.months_to_process(s3_client, BUCKET, "Databricks", available, window_size=6, floor=None)

    assert (2025, 1) not in to_process
    assert to_process == [(2025, 2), (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5)]


def test_months_to_process_never_goes_before_pipeline_start_month(s3_client):
    # Even with a wide window that would otherwise reach back into 2025, the
    # default floor (PIPELINE_START_MONTH = 2026-01) excludes anything earlier.
    available = [(2025, 6), (2025, 12), (2026, 1), (2026, 2), (2026, 3)]

    to_process = s3_sync.months_to_process(s3_client, BUCKET, "Databricks", available, window_size=24)

    assert (2025, 6) not in to_process
    assert (2025, 12) not in to_process
    assert to_process == [(2026, 1), (2026, 2), (2026, 3)]


def test_months_to_process_up_to_date_returns_empty(s3_client):
    available = [(2026, 1), (2026, 2), (2026, 3)]
    for key in [
        "Databricks/2026/01/x.csv",
        "Databricks/2026/02/x.csv",
        "Databricks/2026/03/x.csv",
    ]:
        _put(s3_client, key)

    assert s3_sync.months_to_process(s3_client, BUCKET, "Databricks", available) == []


def test_upload_output_file_uses_provider_year_month_key(tmp_path, s3_client):
    local_file = tmp_path / "DatabricksApr_output.csv"
    local_file.write_text("a,b\n1,2\n")

    key = s3_sync.upload_output_file(s3_client, BUCKET, "Databricks", 2026, 4, local_file)

    assert key == "Databricks/2026/04/DatabricksApr_output.csv"
    obj = s3_client.get_object(Bucket=BUCKET, Key=key)
    assert obj["Body"].read() == b"a,b\n1,2\n"
