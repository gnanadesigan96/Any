"""Small shared helpers: ffmpeg/ffprobe wrappers, slugs, JSON state, logging."""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def log(msg: str) -> None:
    print(f"[vidpipe] {msg}", file=sys.stderr, flush=True)


def slugify(text: str, max_len: int = 60) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return slug[:max_len].rstrip("-") or "video"


def require_binary(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"'{name}' is not installed or not on PATH")


def check_ffmpeg_features(need_captions: bool) -> None:
    """Fail early (before any paid work) if this ffmpeg build lacks what the renderer uses."""
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"], capture_output=True, text=True).stdout
    missing = [f for f in (["subtitles"] if need_captions else []) + ["zoompan", "loudnorm"]
               if f" {f} " not in out]
    encoders = subprocess.run(["ffmpeg", "-hide_banner", "-encoders"], capture_output=True, text=True).stdout
    missing += [e for e in ("libx264", "libmp3lame") if e not in encoders]
    if missing:
        raise RuntimeError(
            f"Your ffmpeg is missing: {', '.join(missing)}. On a Mac, install the full build:\n"
            "  brew uninstall ffmpeg && brew install ffmpeg-full\n"
            "  export PATH=\"/opt/homebrew/opt/ffmpeg-full/bin:$PATH\"   (also add this line to ~/.zprofile)\n"
            "Or set video.captions: false in config.yaml to skip burned-in captions.")


def run_ffmpeg(args: list, cwd=None) -> None:
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, args)]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {' '.join(cmd)}\n{result.stderr.strip()}")


def media_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def read_json(path: Path, default=None):
    return json.loads(path.read_text()) if path.exists() else default


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    tmp.replace(path)


def fmt_timestamp(seconds: float) -> str:
    """YouTube chapter format: M:SS or H:MM:SS."""
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def find_font_file(family: str = "Inter", style: str = "bold") -> str:
    """Locate a font file via fontconfig; falls back to DejaVu Sans Bold."""
    try:
        out = subprocess.run(["fc-match", "-f", "%{file}", f"{family}:{style}"],
                             capture_output=True, text=True, check=True)
        if out.stdout.strip():
            return out.stdout.strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        pass
    return "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
