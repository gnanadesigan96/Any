"""Loads config.yaml (channel/style/provider settings) and .env (API keys)."""

import copy
import os
from pathlib import Path

import yaml

PIPELINE_ROOT = Path(__file__).resolve().parent.parent

DEFAULTS = {
    "channel": {
        "name": "My Channel",
        "niche": "Engineering Disasters",
        "audience": "curious adults who enjoy documentaries",
        "tone": "calm, gripping documentary narrator; short sentences; no hype",
        "language": "English",
    },
    "script": {
        "provider": "api",  # api (Claude API, paid) | manual (paste into the free Claude.ai chat)
        "model": "claude-opus-5-5",
        "effort": "high",
        "target_words": 1500,
        "words_per_scene": 28,
        "max_scenes": 90,
        "num_shorts": 3,
    },
    "voice": {
        "provider": "elevenlabs",
        "voice_id": "",
        "model_id": "eleven_multilingual_v2",
        "stability": 0.45,
        "similarity_boost": 0.8,
        "style": 0.15,
        "workers": 3,
        "kokoro": {
            "voice": "am_michael",
            "speed": 1.0,
            "lang": "en-us",
            "model_dir": "models",
            "model_file": "kokoro-v1.0.onnx",
        },
    },
    "images": {
        "provider": "openai",
        "model": "gpt-image-1",
        "size": "1536x1024",
        "quality": "medium",
        "style": "detailed digital illustration, cinematic documentary look, muted colours, "
                 "soft dramatic lighting, no text, no logos, no watermarks",
        "workers": 4,
        "stock": {
            "sources": ["pexels", "pixabay"],
            "prefer_video": True,
        },
    },
    "video": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "crf": 20,
        "preset": "veryfast",
        "zoom": 0.12,
        "captions": True,
        "caption_font": "Inter",
        "caption_font_file": "",
        "caption_max_words": 5,
        "music_dir": "assets/music",
        "music_volume": 0.10,
        "loudness_lufs": -14,
    },
    "shorts": {
        "enabled": True,
        "width": 1080,
        "height": 1920,
    },
    "thumbnail": {
        "font_file": "",
    },
    "upload": {
        "client_secrets": "client_secret.json",
        "token_file": "youtube_token.json",
        "category_id": "27",  # Education
        "made_for_kids": False,
        "contains_synthetic_media": True,
        "default_language": "en",
    },
    "runs_dir": "runs",
    "topic_bank": "topics/topic_bank.csv",
}


def _deep_merge(base, override):
    out = copy.deepcopy(base)
    for key, value in (override or {}).items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _deep_merge(out[key], value)
        else:
            out[key] = value
    return out


def load_dotenv(path: Path) -> None:
    """Minimal .env reader: KEY=VALUE lines; existing environment variables win."""
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def load_config(path=None, overrides=None) -> dict:
    load_dotenv(PIPELINE_ROOT / ".env")
    cfg_path = Path(path) if path else PIPELINE_ROOT / "config.yaml"
    user_cfg = {}
    if cfg_path.exists():
        user_cfg = yaml.safe_load(cfg_path.read_text()) or {}
    cfg = _deep_merge(DEFAULTS, user_cfg)
    return _deep_merge(cfg, overrides or {})


def resolve(path_str: str) -> Path:
    """Resolve a config path relative to the pipeline folder."""
    p = Path(path_str)
    return p if p.is_absolute() else PIPELINE_ROOT / p
