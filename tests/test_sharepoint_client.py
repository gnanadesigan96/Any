from unittest.mock import MagicMock, patch

import pytest

from saas_pipeline import sharepoint_client


def _mock_response(json_data=None, content=b"", raise_for_status=None, status_code=200):
    resp = MagicMock()
    resp.json.return_value = json_data or {}
    resp.content = content
    resp.status_code = status_code
    resp.raise_for_status = raise_for_status or (lambda: None)
    return resp


def test_parse_site_url_splits_hostname_and_path():
    assert sharepoint_client.parse_site_url("cloudenablersinc.sharepoint.com/sites/SupportTeam") == (
        "cloudenablersinc.sharepoint.com",
        "sites/SupportTeam",
    )


def test_parse_site_url_strips_scheme_and_trailing_slash():
    assert sharepoint_client.parse_site_url("https://contoso.sharepoint.com/sites/Billing/") == (
        "contoso.sharepoint.com",
        "sites/Billing",
    )


def test_parse_site_url_rejects_missing_path():
    with pytest.raises(ValueError):
        sharepoint_client.parse_site_url("contoso.sharepoint.com")


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
def test_find_latest_matching_file_with_no_filter_matches_any_file(mock_get):
    mock_get.return_value = _mock_response({
        "value": [
            {"name": "Consumption.xlsx", "file": {}, "lastModifiedDateTime": "2026-05-01T00:00:00Z"},
            {"name": "Consumption (2).xlsx", "file": {}, "lastModifiedDateTime": "2026-07-01T00:00:00Z"},
            {"name": "SomeFolder", "folder": {}, "lastModifiedDateTime": "2026-08-02T00:00:00Z"},
        ]
    })

    item = sharepoint_client.find_latest_matching_file("tok", "site-abc", "Data")

    assert item["name"] == "Consumption (2).xlsx"


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


@patch("saas_pipeline.sharepoint_client.requests.put")
def test_upload_file_to_sharepoint_uses_simple_upload_for_small_files(mock_put):
    mock_put.return_value = _mock_response({"id": "item-1", "name": "file.xlsx"}, status_code=201)

    result = sharepoint_client.upload_file_to_sharepoint("tok", "site-abc", "Shared Documents", "file.xlsx", b"small content")

    assert result == {"id": "item-1", "name": "file.xlsx"}
    called_url, kwargs = mock_put.call_args[0][0], mock_put.call_args[1]
    assert called_url == "https://graph.microsoft.com/v1.0/sites/site-abc/drive/root:/Shared Documents/file.xlsx:/content"
    assert kwargs["headers"]["Authorization"] == "Bearer tok"
    assert kwargs["data"] == b"small content"


@patch("saas_pipeline.sharepoint_client.requests.put")
@patch("saas_pipeline.sharepoint_client.requests.post")
def test_upload_file_to_sharepoint_uses_chunked_upload_for_large_files(mock_post, mock_put):
    mock_post.return_value = _mock_response({"uploadUrl": "https://upload.example/session"})

    big_content = b"x" * (sharepoint_client.SIMPLE_UPLOAD_MAX_BYTES + 100)
    mock_put.return_value = _mock_response({"id": "item-2", "name": "big.xlsx"}, status_code=201)

    result = sharepoint_client.upload_file_to_sharepoint("tok", "site-abc", "Shared Documents", "big.xlsx", big_content)

    assert result == {"id": "item-2", "name": "big.xlsx"}
    session_url, session_kwargs = mock_post.call_args[0][0], mock_post.call_args[1]
    assert session_url == (
        "https://graph.microsoft.com/v1.0/sites/site-abc/drive/root:/Shared Documents/big.xlsx:/createUploadSession"
    )
    assert session_kwargs["json"] == {"item": {"@microsoft.graph.conflictBehavior": "replace"}}

    # One PUT since the content fits in a single chunk; verify Content-Range covers the whole file.
    put_url, put_kwargs = mock_put.call_args[0][0], mock_put.call_args[1]
    assert put_url == "https://upload.example/session"
    assert put_kwargs["headers"]["Content-Range"] == f"bytes 0-{len(big_content) - 1}/{len(big_content)}"
    assert "Authorization" not in put_kwargs["headers"]


@patch("saas_pipeline.sharepoint_client.requests.put")
@patch("saas_pipeline.sharepoint_client.requests.post")
def test_upload_file_to_sharepoint_chunked_upload_sends_multiple_chunks(mock_post, mock_put):
    mock_post.return_value = _mock_response({"uploadUrl": "https://upload.example/session"})

    total = sharepoint_client.UPLOAD_SESSION_CHUNK_SIZE + 1000
    content = b"y" * total
    # Intermediate chunk: 202 with nextExpectedRanges. Final chunk: 201 with the driveItem.
    mock_put.side_effect = [
        _mock_response({"nextExpectedRanges": ["..."]}, status_code=202),
        _mock_response({"id": "item-3"}, status_code=201),
    ]

    result = sharepoint_client.upload_file_to_sharepoint("tok", "site-abc", "Data", "big.xlsx", content)

    assert result == {"id": "item-3"}
    assert mock_put.call_count == 2
    first_range = mock_put.call_args_list[0][1]["headers"]["Content-Range"]
    second_range = mock_put.call_args_list[1][1]["headers"]["Content-Range"]
    assert first_range == f"bytes 0-{sharepoint_client.UPLOAD_SESSION_CHUNK_SIZE - 1}/{total}"
    assert second_range == f"bytes {sharepoint_client.UPLOAD_SESSION_CHUNK_SIZE}-{total - 1}/{total}"
