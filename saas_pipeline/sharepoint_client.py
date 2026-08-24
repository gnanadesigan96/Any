"""Microsoft Graph client for finding, downloading, and uploading files in a
SharePoint document library.

Uses the OAuth2 client-credentials flow (app-only auth) - the calling app
registration needs the Graph *application* permission Sites.Selected (scoped to
just the target site) or Sites.Read.All, with admin consent granted. Writing
(upload_file_to_sharepoint) additionally needs write access - Sites.Selected
granted with the "write" role, or Sites.ReadWrite.All.
"""
from __future__ import annotations

import logging
import re
from pathlib import Path

import requests

logger = logging.getLogger(__name__)

GRAPH_BASE = "https://graph.microsoft.com/v1.0"
REQUEST_TIMEOUT_SECONDS = 30
DOWNLOAD_TIMEOUT_SECONDS = 120
UPLOAD_TIMEOUT_SECONDS = 120

# Graph's "simple upload" (a single PUT) only works below 4 MiB; at or above
# that, an upload session (chunked PUTs) is required instead.
SIMPLE_UPLOAD_MAX_BYTES = 4 * 1024 * 1024
# Upload-session chunk size must be a multiple of 320 KiB.
UPLOAD_SESSION_CHUNK_SIZE = 60 * 320 * 1024  # ~18.75 MiB


def parse_site_url(site_url: str) -> tuple[str, str]:
    """Split a SharePoint site URL/reference into (hostname, site_path).

    Accepts either a bare 'tenant.sharepoint.com/sites/Name' or a full
    'https://tenant.sharepoint.com/sites/Name' - the scheme, if present, is
    stripped before splitting on the first remaining '/'.
    """
    cleaned = re.sub(r"^https?://", "", site_url.strip()).rstrip("/")
    hostname, _, site_path = cleaned.partition("/")
    if not hostname or not site_path:
        raise ValueError(f"Could not split '{site_url}' into hostname/site_path")
    return hostname, site_path


def get_graph_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """Get an app-only access token for Microsoft Graph."""
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    response = requests.post(
        token_url,
        data={
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "https://graph.microsoft.com/.default",
            "grant_type": "client_credentials",
        },
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def get_site_id(token: str, site_hostname: str, site_path: str) -> str:
    """Resolve a SharePoint site's Graph site ID.

    site_hostname: e.g. 'yourtenant.sharepoint.com'
    site_path: e.g. 'sites/YourSiteName'
    """
    url = f"{GRAPH_BASE}/sites/{site_hostname}:/{site_path}"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    return response.json()["id"]


def find_latest_matching_file(token: str, site_id: str, folder_path: str, filename_contains: str = "") -> dict:
    """List files in a SharePoint folder and return the most recently modified one
    whose name contains `filename_contains` (case-insensitive). Leave
    `filename_contains` empty to match any file in the folder - useful when the
    folder is dedicated to just this one workbook."""
    url = f"{GRAPH_BASE}/sites/{site_id}/drive/root:/{folder_path}:/children"
    response = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=REQUEST_TIMEOUT_SECONDS)
    response.raise_for_status()
    items = response.json().get("value", [])

    matches = [
        item for item in items if "file" in item and filename_contains.lower() in item["name"].lower()
    ]
    if not matches:
        raise FileNotFoundError(f"No file containing '{filename_contains}' found in '{folder_path}'")

    matches.sort(key=lambda item: item["lastModifiedDateTime"], reverse=True)
    return matches[0]


def download_drive_item(item: dict, dest_path: Path) -> Path:
    """Download a driveItem's content to dest_path. The '@microsoft.graph.downloadUrl'
    Graph hands back is a pre-signed URL and does not need an Authorization header."""
    download_url = item["@microsoft.graph.downloadUrl"]
    response = requests.get(download_url, timeout=DOWNLOAD_TIMEOUT_SECONDS)
    response.raise_for_status()
    dest_path.write_bytes(response.content)
    logger.info("Downloaded '%s' (modified %s) -> %s", item["name"], item["lastModifiedDateTime"], dest_path)
    return dest_path


def upload_file_to_sharepoint(token: str, site_id: str, folder_path: str, filename: str, content: bytes) -> dict:
    """Upload (or overwrite) a file at folder_path/filename in a SharePoint
    document library. Uses Graph's simple upload for files under 4 MiB and a
    chunked upload session above that, so it stays correct as the workbook
    grows rather than assuming it always stays small."""
    if len(content) < SIMPLE_UPLOAD_MAX_BYTES:
        return _simple_upload(token, site_id, folder_path, filename, content)
    return _chunked_upload(token, site_id, folder_path, filename, content)


def _simple_upload(token: str, site_id: str, folder_path: str, filename: str, content: bytes) -> dict:
    url = f"{GRAPH_BASE}/sites/{site_id}/drive/root:/{folder_path}/{filename}:/content"
    response = requests.put(
        url,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream"},
        data=content,
        timeout=UPLOAD_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    return response.json()


def _chunked_upload(token: str, site_id: str, folder_path: str, filename: str, content: bytes) -> dict:
    session_url = f"{GRAPH_BASE}/sites/{site_id}/drive/root:/{folder_path}/{filename}:/createUploadSession"
    session_response = requests.post(
        session_url,
        headers={"Authorization": f"Bearer {token}"},
        json={"item": {"@microsoft.graph.conflictBehavior": "replace"}},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    session_response.raise_for_status()
    upload_url = session_response.json()["uploadUrl"]

    total = len(content)
    result = {}
    for start in range(0, total, UPLOAD_SESSION_CHUNK_SIZE):
        end = min(start + UPLOAD_SESSION_CHUNK_SIZE, total)
        chunk = content[start:end]
        chunk_response = requests.put(
            upload_url,
            headers={
                "Content-Length": str(len(chunk)),
                "Content-Range": f"bytes {start}-{end - 1}/{total}",
            },
            data=chunk,
            timeout=UPLOAD_TIMEOUT_SECONDS,
        )
        chunk_response.raise_for_status()
        # Intermediate chunks return 202 with nextExpectedRanges; only the
        # final chunk returns 200/201 with the completed driveItem.
        if chunk_response.status_code in (200, 201):
            result = chunk_response.json()
    return result
