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
            "sentence_pause": 0.22,  # silence between sentences (seconds)
            "scene_pause": 0.25,     # silence after each scene
            "clause_pause": 0.06,    # Kokoro's pause at commas/dashes
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
        "local": {                # images.provider: local (free, Apple Silicon Macs only)
            "model": "z-image-turbo",
            "quantize": 4,        # 4-bit keeps memory use low enough for a 16 GB Mac
            "steps": 9,
            "width": 720,         # vertical 9:16; upscaled to 1080x1920 when rendering
            "height": 1280,
            "seed": 42,           # a fixed seed keeps the look more consistent across images
        },
    },
    "series": {
        "parts": 20,
        "per_batch": 5,           # parts written per Claude.ai prompt (keeps each reply short enough)
        "target_words": 100,      # ~40 seconds of narration per part
        "words_per_scene": 12,
        "style_hint": "",         # e.g. "anime", "graphic novel", "watercolour storybook"
        "images_provider": "local",  # local (free, Apple Silicon) or openai (paid)
        "animation": "parallax",  # 2.5D animated illustrations for story series
        "voice_speed": 0.95,      # storytelling pace: a little slower and more dramatic than fact Shorts
        "sentence_pause": 0.2,
    },
    "video": {
        "width": 1920,
        "height": 1080,
        "fps": 30,
        "crf": 20,
        "preset": "veryfast",
        "zoom": 0.12,
        # Still images: "kenburns" = slow zoom/pan; "parallax" = 2.5D depth animation + weather/light effects
        "animation": "kenburns",
        "parallax": {"strength": 1.0},
        "effects": True,          # parallax only: fog, rain, snow, embers, flicker, lightning from scene text
        "captions": True,
        "caption_font": "Inter",
        "caption_font_file": "",
        "caption_max_words": 5,
        "music_dir": "assets/music",
        "music_volume": 0.10,
        "loudness_lufs": -14,
    },
    # "long": one long video (plus clips cut from it). "shorts": several standalone Shorts per topic.
    "format": "long",
    "shorts": {
        "enabled": True,          # long format only: also cut Shorts out of the long video
        "width": 1080,
        "height": 1920,
        "per_topic": 3,           # shorts format: how many Shorts to write per topic
        "target_words": 115,      # ~40-50 seconds each
        "words_per_scene": 10,    # new visual every ~3-4 seconds
        "max_scenes": 20,
        "caption_max_words": 3,
        "voice_speed": 1.08,      # Kokoro speed for Shorts (slightly brisker)
        "sentence_pause": 0.12,
        "scene_pause": 0.06,
        "clause_pause": 0.04,
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
