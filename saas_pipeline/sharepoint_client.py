"""Microsoft Graph client for finding and downloading the latest consumption
workbook dropped into a SharePoint document library.

Uses the OAuth2 client-credentials flow (app-only auth) - the calling app
registration needs the Graph *application* permission Sites.Selected (scoped to
just the target site) or Sites.Read.All, with admin consent granted.
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
