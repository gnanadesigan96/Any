"""Stage 6: metadata.json (what gets uploaded) and REVIEW.md (what a human checks first)."""

from pathlib import Path

from .render import build_timeline
from .stock import credit_lines
from .util import fmt_timestamp, read_json, write_json

MIN_CHAPTER_SECONDS = 10


def chapter_times(script, timeline: list, fps: int) -> list:
    """YouTube only shows chapters if there are 3+, the first is 0:00, and each is 10s+."""
    total = timeline[-1]["start"] + timeline[-1]["frames"] / fps
    marks = []
    for c in script.chapters:
        t = timeline[c.start_scene]["start"]
        if marks and t - marks[-1][1] < MIN_CHAPTER_SECONDS:
            continue
        marks.append([c.title, t])
    if marks and total - marks[-1][1] < MIN_CHAPTER_SECONDS and len(marks) > 1:
        marks.pop()
    if not marks or marks[0][1] != 0:
        marks.insert(0, ["Introduction", 0.0])
    return marks if len(marks) >= 3 else []


def build_description(script, chapters: list, credits: list = ()) -> str:
    parts = [script.description.strip()]
    if chapters:
        parts.append("Chapters:\n" + "\n".join(f"{fmt_timestamp(t)} {title}" for title, t in chapters))
    sources = sorted({f.source.strip() for f in script.fact_check if f.source.strip() and f.source != "n/a"})
    if sources:
        parts.append("Sources:\n" + "\n".join(f"- {s}" for s in sources))
    if credits:
        parts.append("Stock footage: " + ", ".join(credits))
    return "\n\n".join(parts)


def write_review(run_dir: Path, topic: str, script, timing: list, cfg: dict,
                 thumbnails: list, shorts: list, dry_run: bool, regenerate: bool) -> Path:
    fps = cfg["video"]["fps"]
    timeline = build_timeline(timing, fps)
    chapters = chapter_times(script, timeline, fps)
    meta_path = run_dir / "metadata.json"
    metadata = read_json(meta_path)
    # metadata.json is the human's file once it exists (chosen title, approval, upload IDs);
    # only rebuild it when the script itself was regenerated.
    if metadata is None or regenerate:
        metadata = _new_metadata(topic, script, chapters, thumbnails, shorts, dry_run,
                                 credit_lines(run_dir / "images"))
        write_json(meta_path, metadata)
    _write_review_md(run_dir, topic, script, timeline, thumbnails, shorts, metadata)
    return run_dir / "REVIEW.md"


def _new_metadata(topic, script, chapters, thumbnails, shorts, dry_run, credits) -> dict:
    return {
        "approved": False,
        "dry_run": dry_run,
        "topic": topic,
        "title": script.titles[0],
        "title_options": script.titles,
        "description": build_description(script, chapters, credits),
        "tags": script.tags,
        "thumbnail": thumbnails[0].name if thumbnails else None,
        "thumbnail_options": [t.name for t in thumbnails],
        "shorts": [
            {"file": p.name, "title": s.hook_title, "description": script.description.strip()}
            for p, s in zip(shorts, script.shorts)
        ],
        "youtube_video_id": None,
    }


def _write_review_md(run_dir, topic, script, timeline, thumbnails, shorts, metadata) -> None:
    lines = [
        f"# Review: {topic}",
        "",
        "Nothing is uploaded until you finish this checklist and set `\"approved\": true` in "
        "`metadata.json`. Then run `python make_video.py upload " + str(run_dir) + "`.",
        "",
        "## Checklist",
        "- [ ] Watch `video.mp4` all the way through (odd images, mispronounced names, pacing)",
        "- [ ] Check every claim in the fact-check table below against its source",
        "- [ ] Pick a title and thumbnail (edit `title` / `thumbnail` in `metadata.json`)",
        "- [ ] Watch each Short",
        "- [ ] Set `\"approved\": true` in `metadata.json`",
        "",
        "## Title options",
        *[f"{i + 1}. {t}" for i, t in enumerate(script.titles)],
        "",
        "## Thumbnail options",
        *[f"- `{t.name}` - \"{txt}\"" for t, txt in zip(thumbnails, script.thumbnail_texts)],
        "",
        "## Description (as it will be uploaded)",
        "```",
        metadata["description"],
        "```",
        "",
        "## Fact-check",
        "| # | Claim | Check against |",
        "|---|---|---|",
        *[f"| {i + 1} | {f.claim.replace('|', '/')} | {f.source.replace('|', '/')} |"
          for i, f in enumerate(script.fact_check)],
        "",
        "## Shorts",
        *[f"- `{p.name}` - {s.hook_title} (scenes {s.start_scene}-{s.end_scene})"
          for p, s in zip(shorts, script.shorts)],
        "",
        "## Script",
    ]
    for i, (scene, t) in enumerate(zip(script.scenes, timeline)):
        lines.append(f"**[{fmt_timestamp(t['start'])}] Scene {i}** - {scene.narration}  ")
        lines.append(f"_Image: {scene.visual}_")
        lines.append("")
    (run_dir / "REVIEW.md").write_text("\n".join(lines), encoding="utf-8")
