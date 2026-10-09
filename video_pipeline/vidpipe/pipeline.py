"""Runs the stages in order. Every stage caches its output in the run folder, so a failed or
interrupted run picks up where it stopped (and you only pay for missing pieces)."""

import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from .config import resolve
from .images import generate_images
from .render import check_output, render_main, render_shorts
from .review import write_review
from .script import (MANUAL_REPLY, dummy_script, generate_script, load_script_dict, parse_manual_reply,
                     write_manual_prompt)
from .stock import fetch_thumbnail_photo, fetch_visuals
from .thumbnail import make_thumbnails
from .util import check_ffmpeg_features, log, read_json, require_binary, slugify, write_json
from .voice import narrate_scenes

# Downstream outputs to delete when a stage is redone.
REDO = {
    "script": ["script.json", "claude_reply.txt", "PROMPT_FOR_CLAUDE.txt", "metadata.json", "audio", "images", "work", "video.mp4", "short_*.mp4", "thumbnail_*.jpg"],
    "voice": ["audio", "work", "video.mp4", "short_*.mp4"],
    "images": ["images", "work", "video.mp4", "short_*.mp4", "thumbnail_*.jpg"],
    "video": ["work", "video.mp4", "short_*.mp4"],
}


class ManualStepNeeded(Exception):
    """Raised (not an error) when the free manual-script mode is waiting for you."""


def _uses_paid_services(cfg: dict) -> bool:
    return cfg["voice"]["provider"] == "elevenlabs" or cfg["images"]["provider"] == "openai"


def _clear(run_dir: Path, patterns: list) -> None:
    for pattern in patterns:
        for p in run_dir.glob(pattern):
            shutil.rmtree(p) if p.is_dir() else p.unlink()


def _confirm_spend(script, run_dir: Path, cfg: dict, assume_yes: bool) -> None:
    chars = sum(len(s.narration) for s in script.scenes)
    images = len(script.scenes) + 1
    missing_images = sum(1 for i in range(len(script.scenes)) if not (run_dir / "images" / f"scene_{i:03d}.png").exists())
    words = sum(len(s.narration.split()) for s in script.scenes)
    log(f"Script ready: {len(script.scenes)} scenes, {words} words (~{words / 150:.1f} min). "
        f"Voice: {chars} characters. Images: {images} total, {missing_images} still to generate.")
    if assume_yes or not sys.stdin.isatty() or not _uses_paid_services(cfg):
        return
    if input("Generate voice and images now (uses paid API credits)? [y/N] ").strip().lower() != "y":
        raise SystemExit("Stopped after the script. Read script.json, then re-run the same command to continue.")


def make_video(topic: str, angle: str, cfg: dict, dry_run: bool = False, redo: str = "",
               assume_yes: bool = False) -> Path:
    require_binary("ffmpeg")
    require_binary("ffprobe")
    check_ffmpeg_features(cfg["video"]["captions"])
    run_dir = resolve(cfg["runs_dir"]) / (slugify(topic) + ("-dryrun" if dry_run else ""))
    run_dir.mkdir(parents=True, exist_ok=True)
    if redo:
        _clear(run_dir, REDO[redo])
    if not (run_dir / "run.json").exists():
        write_json(run_dir / "run.json", {"topic": topic, "angle": angle, "dry_run": dry_run,
                                          "created": datetime.now(timezone.utc).isoformat()})
    log(f"Run folder: {run_dir}")

    # 1. Script
    script_path = run_dir / "script.json"
    regenerated = False
    if script_path.exists():
        script = load_script_dict(read_json(script_path))
    else:
        if dry_run:
            script = dummy_script(topic, angle, cfg)
        elif cfg["script"]["provider"] == "manual":
            reply = run_dir / MANUAL_REPLY
            if not reply.exists() or not reply.read_text(encoding="utf-8").strip():
                prompt = write_manual_prompt(topic, angle, run_dir, cfg)
                reply.touch()
                raise ManualStepNeeded(
                    "Free script step:\n"
                    f"  1. Open {prompt} and copy all of it\n"
                    "  2. Paste it into a new chat at claude.ai and send\n"
                    f"  3. Paste Claude's whole reply into {reply} and save\n"
                    "  4. Run the same command again")
            script = parse_manual_reply(reply.read_text(encoding="utf-8"), cfg)
        else:
            script = generate_script(topic, angle, cfg)
        write_json(script_path, script.model_dump())
        regenerated = True
    if not dry_run:
        _confirm_spend(script, run_dir, cfg, assume_yes)

    # 2. Voice
    timing = narrate_scenes(script.scenes, run_dir, cfg, dry_run)

    # 3. Visuals: AI images, or free stock clips/photos (plus a thumbnail background)
    img_dir = run_dir / "images"
    img_dir.mkdir(exist_ok=True)
    if cfg["images"]["provider"] == "stock" and not dry_run:
        image_paths = fetch_visuals(script.scenes, [t["duration"] for t in timing], img_dir, cfg)
        thumb_bg = img_dir / "thumbnail_bg.jpg"
        fetch_thumbnail_photo(script.thumbnail_search_query, thumb_bg, cfg)
    else:
        image_paths = [img_dir / f"scene_{i:03d}.png" for i in range(len(script.scenes))]
        thumb_bg = img_dir / "thumbnail_bg.png"
        generate_images([(s.visual, p) for s, p in zip(script.scenes, image_paths)]
                        + [(script.thumbnail_visual, thumb_bg)], cfg, dry_run)

    # 4. Long-form video
    video = run_dir / "video.mp4"
    if not video.exists():
        render_main(run_dir, image_paths, timing, cfg)
    check_output(video)

    # 5. Shorts
    shorts = []
    if cfg["shorts"]["enabled"] and script.shorts:
        shorts = render_shorts(run_dir, image_paths, timing, script.shorts, cfg)

    # 6. Thumbnails + review package
    thumbs = sorted(run_dir.glob("thumbnail_*.jpg")) or make_thumbnails(thumb_bg, script.thumbnail_texts, run_dir, cfg)
    review = write_review(run_dir, topic, script, timing, cfg, thumbs, shorts, dry_run, regenerated)
    log(f"Done. Review {review} before uploading.")
    return run_dir
