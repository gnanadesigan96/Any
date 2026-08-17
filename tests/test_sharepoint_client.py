from unittest.mock import MagicMock, patch

import pytest

from saas_pipeline import sharepoint_client


def _mock_response(json_data=None, content=b"", raise_for_status=None):
    resp = MagicMock()
    resp.json.return_value = json_data or {}
    resp.content = content
    resp.raise_for_status = raise_for_status or (lambda: None)
    return resp


@patch("saas_pipeline.sharepoint_client.requests.post")
def test_get_graph_token_posts_client_credentials(mock_post):
    mock_post.return_value = _mock_response({"access_token": "tok-123"})

    token = sharepoint_client.get_graph_token("tenant-1", "client-1", "secret-1")

    assert token == "tok-123"
    called_url, kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    assert called_url == "https://login.microsoftonline.com/tenant-1/oauth2/v2.0/token"
    assert kwargs["data"]["grant_type"] == "client_credentials"
    assert kwargs["data"]["scope"] == "https://graph.microsoft.com/.default"


@patch("saas_pipeline.sharepoint_client.requests.get")
def test_get_site_id_builds_correct_url(mock_get):
    mock_get.return_value = _mock_response({"id": "site-abc"})

    site_id = sharepoint_client.get_site_id("tok", "contoso.sharepoint.com", "sites/Billing")

    assert site_id == "site-abc"
    called_url = mock_get.call_args[0][0]
    assert called_url == "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/Billing"


@patch("saas_pipeline.sharepoint_client.requests.get")
def test_find_latest_matching_file_picks_most_recently_modified(mock_get):
    mock_get.return_value = _mock_response({
        "value": [
            {"name": "2026 Consumption Costs (old).xlsx", "file": {}, "lastModifiedDateTime": "2026-05-01T00:00:00Z"},
            {"name": "2026 Consumption Costs.xlsx", "file": {}, "lastModifiedDateTime": "2026-07-01T00:00:00Z"},
            {"name": "notes.txt", "file": {}, "lastModifiedDateTime": "2026-08-01T00:00:00Z"},
            {"name": "SomeFolder", "folder": {}, "lastModifiedDateTime": "2026-08-02T00:00:00Z"},
        ]
    })

    item = sharepoint_client.find_latest_matching_file("tok", "site-abc", "Shared Documents", "Consumption Costs")

    assert item["name"] == "2026 Consumption Costs.xlsx"


@patch("saas_pipeline.sharepoint_client.requests.get")
def test_find_latest_matching_file_raises_when_nothing_matches(mock_get):
    mock_get.return_value = _mock_response({"value": [{"name": "unrelated.xlsx", "file": {}, "lastModifiedDateTime": "2026-01-01T00:00:00Z"}]})

    with pytest.raises(FileNotFoundError):
        sharepoint_client.find_latest_matching_file("tok", "site-abc", "Shared Documents", "Consumption Costs")


@patch("saas_pipeline.sharepoint_client.requests.get")
def test_download_drive_item_writes_content_without_auth_header(mock_get, tmp_path):
    mock_get.return_value = _mock_response(content=b"workbook-bytes")
    item = {
        "name": "file.xlsx",
        "lastModifiedDateTime": "2026-07-01T00:00:00Z",
        "@microsoft.graph.downloadUrl": "https://presigned.example/file.xlsx",
    }
    dest = tmp_path / "file.xlsx"

    result = sharepoint_client.download_drive_item(item, dest)

    assert result == dest
    assert dest.read_bytes() == b"workbook-bytes"
    called_url, kwargs = mock_get.call_args[0][0], mock_get.call_args[1]
    assert called_url == "https://presigned.example/file.xlsx"
    assert "headers" not in kwargs
