"""Stage 7 (manual): upload an approved run to YouTube as private, optionally scheduled."""

from pathlib import Path

from .config import resolve
from .util import log, read_json, write_json

SCOPES = ["https://www.googleapis.com/auth/youtube.upload",
          "https://www.googleapis.com/auth/youtube"]


def _youtube(cfg: dict):
    # Imported lazily so the rest of the pipeline works without the Google libraries.
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    u = cfg["upload"]
    token_path, secrets_path = resolve(u["token_file"]), resolve(u["client_secrets"])
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not secrets_path.exists():
                raise RuntimeError(f"Missing {secrets_path} - see README 'YouTube upload setup'")
            flow = InstalledAppFlow.from_client_secrets_file(str(secrets_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("youtube", "v3", credentials=creds)


def _insert(youtube, path: Path, title: str, description: str, tags: list, cfg: dict,
            publish_at: str) -> str:
    from googleapiclient.http import MediaFileUpload

    u = cfg["upload"]
    status = {
        "privacyStatus": "private",
        "selfDeclaredMadeForKids": u["made_for_kids"],
        "containsSyntheticMedia": u["contains_synthetic_media"],
    }
    if publish_at:
        status["publishAt"] = publish_at  # goes public automatically at this time
    body = {
        "snippet": {"title": title[:100], "description": description[:5000], "tags": tags,
                    "categoryId": u["category_id"], "defaultLanguage": u["default_language"],
                    "defaultAudioLanguage": u["default_language"]},
        "status": status,
    }
    request = youtube.videos().insert(
        part="snippet,status", body=body,
        media_body=MediaFileUpload(str(path), chunksize=8 * 1024 * 1024, resumable=True),
    )
    response = None
    while response is None:
        progress, response = request.next_chunk()
        if progress:
            log(f"  {path.name}: {int(progress.progress() * 100)}%")
    return response["id"]


def upload_run(run_dir: Path, cfg: dict, include_shorts: bool, publish_at: str) -> None:
    from googleapiclient.http import MediaFileUpload

    meta_path = run_dir / "metadata.json"
    meta = read_json(meta_path)
    if not meta:
        raise RuntimeError(f"No metadata.json in {run_dir}; run the pipeline first")
    if meta.get("dry_run"):
        raise RuntimeError("This is a dry-run video (placeholder images, silent audio); it can't be uploaded")
    if meta.get("approved") is not True:
        raise RuntimeError("Not approved yet: review REVIEW.md, then set \"approved\": true in metadata.json")

    youtube = _youtube(cfg)
    if meta.get("youtube_video_id"):
        log(f"Main video already uploaded: https://youtu.be/{meta['youtube_video_id']}")
    else:
        log("Uploading main video (private)...")
        vid = _insert(youtube, run_dir / "video.mp4", meta["title"], meta["description"],
                      meta.get("tags", []), cfg, publish_at)
        meta["youtube_video_id"] = vid
        write_json(meta_path, meta)
        if meta.get("thumbnail"):
            try:
                youtube.thumbnails().set(
                    videoId=vid, media_body=MediaFileUpload(str(run_dir / meta["thumbnail"]))).execute()
            except Exception as e:  # custom thumbnails need a phone-verified channel
                log(f"Thumbnail upload failed ({e}); set it manually in YouTube Studio")
        log(f"Uploaded: https://youtu.be/{vid} (private)")

    if include_shorts:
        for short in meta.get("shorts", []):
            if short.get("youtube_video_id"):
                continue
            log(f"Uploading {short['file']} (private)...")
            short["youtube_video_id"] = _insert(
                youtube, run_dir / short["file"], short["title"],
                short.get("description", "") + (f"\n\nFull video: https://youtu.be/{meta['youtube_video_id']}"),
                meta.get("tags", []), cfg, publish_at)
            write_json(meta_path, meta)
            log(f"Uploaded: https://youtu.be/{short['youtube_video_id']} (private)")
