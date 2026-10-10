"""Runs the stages in order. Every stage caches its output in the run folder, so a failed or
interrupted run picks up where it stopped (and you only pay for missing pieces)."""

import copy
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from pydantic import ValidationError

from .config import resolve
from .images import generate_images
from .render import check_output, render_main, render_shorts
from .review import write_review, write_shorts_review
from .script import (MANUAL_REPLY, dummy_script, dummy_shorts, generate_script, is_shorts, load_any,
                     parse_manual_reply, write_manual_prompt)
from .stock import credit_lines, fetch_thumbnail_photo, fetch_visuals, used_ids
from .thumbnail import make_thumbnails
from .util import check_ffmpeg_features, log, read_json, require_binary, slugify, write_json
from .voice import narrate_scenes

# Downstream outputs to delete when a stage is redone.
# (Shorts mode keeps each Short's working files in a short_N/ folder, hence the short_*/ patterns.)
REDO = {
    "script": ["script.json", "claude_reply.txt", "PROMPT_FOR_CLAUDE.txt", "metadata.json", "audio", "images",
               "work", "video.mp4", "short_*", "thumbnail_*.jpg"],
    "voice": ["audio", "work", "video.mp4", "short_*.mp4", "short_*/audio", "short_*/work", "short_*/video.mp4"],
    "images": ["images", "work", "video.mp4", "short_*.mp4", "thumbnail_*.jpg", "short_*/images", "short_*/work",
               "short_*/video.mp4"],
    "video": ["work", "video.mp4", "short_*.mp4", "short_*/work", "short_*/video.mp4"],
}


class ManualStepNeeded(Exception):
    """Raised (not an error) when the free manual-script mode is waiting for you."""


def _uses_paid_services(cfg: dict) -> bool:
    return cfg["voice"]["provider"] == "elevenlabs" or cfg["images"]["provider"] == "openai"


def _clear(run_dir: Path, patterns: list) -> None:
    for pattern in patterns:
        for p in run_dir.glob(pattern):
            shutil.rmtree(p) if p.is_dir() else p.unlink()


def _confirm_spend(scenes: list, cfg: dict, assume_yes: bool) -> None:
    chars = sum(len(s.narration) for s in scenes)
    words = sum(len(s.narration.split()) for s in scenes)
    log(f"Script ready: {len(scenes)} scenes, {words} words (~{words / 150:.1f} min of narration), "
        f"{chars} characters.")
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

    script, regenerated = _script_stage(run_dir, topic, angle, cfg, dry_run)
    if is_shorts(cfg):
        return _make_shorts(run_dir, topic, script, cfg, dry_run, assume_yes, regenerated)
    return _make_long(run_dir, topic, script, cfg, dry_run, assume_yes, regenerated)


def _script_stage(run_dir: Path, topic: str, angle: str, cfg: dict, dry_run: bool):
    """Returns (script, regenerated). Raises ManualStepNeeded while waiting for a pasted reply."""
    script_path = run_dir / "script.json"
    if script_path.exists():
        try:
            return load_any(read_json(script_path), cfg), False
        except ValidationError as e:
            fmt = "Shorts" if is_shorts(cfg) else "long-video"
            raise RuntimeError(f"{run_dir.name} was made in the other format, not the {fmt} format set in "
                               "config.yaml. Re-run with --redo script to rewrite it, or pick another topic.") from e
    if dry_run:
        script = dummy_shorts(topic, angle, cfg) if is_shorts(cfg) else dummy_script(topic, angle, cfg)
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
    return script, True


def _visuals(scenes: list, timing: list, img_dir: Path, cfg: dict, dry_run: bool, exclude=frozenset()) -> list:
    img_dir.mkdir(parents=True, exist_ok=True)
    if cfg["images"]["provider"] == "stock" and not dry_run:
        return fetch_visuals(scenes, [t["duration"] for t in timing], img_dir, cfg, exclude)
    # scenes_per_image > 1 reuses each picture for that many consecutive scenes (each still gets its
    # own camera move), dividing generation time; pictures that already exist are always kept.
    k = max(1, int(cfg["images"].get("scenes_per_image", 1)))
    manifest_path = img_dir / "prompts.json"
    manifest = read_json(manifest_path, {}) or {}
    own = [img_dir / f"scene_{i:03d}.png" for i in range(len(scenes))]
    for i, p in enumerate(own):
        # A picture made for a different description is stale (e.g. the script was rewritten).
        # Pictures from before this manifest existed are trusted as-is.
        if p.exists() and manifest.get(p.name, scenes[i].visual) != scenes[i].visual:
            log(f"  {p.name}: scene description changed, regenerating")
            p.unlink()
            p.with_name(p.stem + ".depth.png").unlink(missing_ok=True)
    paths = [p if p.exists() else own[i - i % k] for i, p in enumerate(own)]
    missing = sorted({p for p in paths if not p.exists()})
    generate_images([(scenes[int(p.stem[6:])].visual, p) for p in missing], cfg, dry_run)
    for p in set(paths):
        manifest.setdefault(p.name, scenes[int(p.stem[6:])].visual)
        if p in missing:
            manifest[p.name] = scenes[int(p.stem[6:])].visual
    write_json(manifest_path, manifest)
    # A real video clip saved as scene_NNN.mp4 (e.g. made with an image-to-video app) wins.
    return [img_dir / f"scene_{i:03d}.mp4" if (img_dir / f"scene_{i:03d}.mp4").exists() else p
            for i, p in enumerate(paths)]


def shorts_config(cfg: dict) -> dict:
    """The config as seen while rendering a Short: vertical frame, short captions, brisk voice."""
    sh = cfg["shorts"]
    vcfg = copy.deepcopy(cfg)
    vcfg["video"].update(width=sh["width"], height=sh["height"], caption_max_words=sh["caption_max_words"])
    vcfg["voice"]["kokoro"].update(speed=sh["voice_speed"], sentence_pause=sh["sentence_pause"],
                                   scene_pause=sh["scene_pause"], clause_pause=sh["clause_pause"])
    vcfg["images"]["size"] = "1024x1536"  # portrait AI images when the paid image provider is used
    if cfg["images"]["provider"] == "local":
        vcfg["images"]["workers"] = 1
    return vcfg


def _fingerprint(short, overlay: dict, paths: list, cfg: dict) -> str:
    """Changes whenever anything that affects the rendered Short changes."""
    v = cfg["video"]
    data = [[s.narration for s in short.scenes], short.hook_text, overlay,
            [f"{p.name}:{p.stat().st_mtime_ns}" for p in paths],
            {k: v.get(k) for k in ("animation", "parallax", "effects", "score", "score_volume", "width",
                                    "height", "fps", "captions", "caption_max_words")},
            cfg["voice"].get("kokoro"), cfg["voice"].get("provider")]
    return hashlib.sha1(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


def _make_shorts(run_dir: Path, topic: str, pack, cfg: dict, dry_run: bool, assume_yes: bool,
                 regenerated: bool, prefix: str = "short", limit: int = 0, overlays: list = None) -> Path:
    """Renders each item of pack.shorts as <prefix>_<k>.mp4. `limit` renders only the first N."""
    if not dry_run:
        _confirm_spend([sc for short in pack.shorts for sc in short.scenes], cfg, assume_yes)
    vcfg = shorts_config(cfg)
    names = [f"{prefix}_{k:02d}" if prefix != "short" else f"short_{k}" for k in range(1, len(pack.shorts) + 1)]
    todo = pack.shorts[:limit] if limit else pack.shorts
    outputs = []
    for k, short in enumerate(todo, start=1):
        sub = run_dir / names[k - 1]
        sub.mkdir(exist_ok=True)
        log(f"{prefix.title()} {k}/{len(pack.shorts)}: {short.title}")
        timing = narrate_scenes(short.scenes, sub, vcfg, dry_run)
        siblings = [run_dir / n / "images" for j, n in enumerate(names, start=1) if j != k]
        paths = _visuals(short.scenes, timing, sub / "images", vcfg, dry_run, used_ids(siblings))
        out = run_dir / f"{names[k - 1]}.mp4"
        overlay = (overlays or [{}] * len(pack.shorts))[k - 1]
        stamp, fp = sub / "fingerprint.txt", _fingerprint(short, overlay, paths, vcfg)
        if stamp.exists() and stamp.read_text() != fp:
            log("  script or settings changed since the last render; re-rendering this one")
            _clear(sub, ["work", "video.mp4"])
            out.unlink(missing_ok=True)
        if not out.exists():
            video = sub / "video.mp4"
            if not video.exists():
                render_main(sub, paths, timing, vcfg, title=short.hook_text,
                            scene_texts=[f"{sc.visual} {sc.narration}" for sc in short.scenes], overlay=overlay)
            shutil.copyfile(video, out)
        stamp.write_text(fp)
        duration = check_output(out, check_silence=not dry_run)
        if duration > 180:
            log(f"  Warning: {out.name} is {duration:.0f}s; YouTube Shorts must be 3 minutes or less")
        outputs.append(out)
    if len(outputs) < len(pack.shorts):
        log(f"Rendered {len(outputs)} of {len(pack.shorts)}. Run the same command without --first to finish.")
        return run_dir
    credits = [credit_lines(run_dir / n / "images") for n in names]
    review = write_shorts_review(run_dir, topic, pack, outputs, credits, dry_run, regenerated)
    log(f"Done: {len(outputs)} Shorts. Review {review} before uploading.")
    return run_dir


def _make_long(run_dir: Path, topic: str, script, cfg: dict, dry_run: bool, assume_yes: bool,
               regenerated: bool) -> Path:
    if not dry_run:
        _confirm_spend(script.scenes, cfg, assume_yes)
    timing = narrate_scenes(script.scenes, run_dir, cfg, dry_run)

    img_dir = run_dir / "images"
    image_paths = _visuals(script.scenes, timing, img_dir, cfg, dry_run)
    if cfg["images"]["provider"] == "stock" and not dry_run:
        thumb_bg = img_dir / "thumbnail_bg.jpg"
        fetch_thumbnail_photo(script.thumbnail_search_query, thumb_bg, cfg)
    else:
        thumb_bg = img_dir / "thumbnail_bg.png"
        generate_images([(script.thumbnail_visual, thumb_bg)], cfg, dry_run)

    video = run_dir / "video.mp4"
    if not video.exists():
        render_main(run_dir, image_paths, timing, cfg)
    check_output(video, check_silence=not dry_run)

    shorts = []
    if cfg["shorts"]["enabled"] and script.shorts:
        shorts = render_shorts(run_dir, image_paths, timing, script.shorts, cfg)

    thumbs = sorted(run_dir.glob("thumbnail_*.jpg")) or make_thumbnails(thumb_bg, script.thumbnail_texts, run_dir, cfg)
    review = write_review(run_dir, topic, script, timing, cfg, thumbs, shorts, dry_run, regenerated)
    log(f"Done. Review {review} before uploading.")
    return run_dir
