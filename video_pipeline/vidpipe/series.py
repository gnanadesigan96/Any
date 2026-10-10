"""Story series: one story (a movie, book or legend) retold as N consecutive ~40-second Shorts,
with a fixed art style and fixed character designs so every part looks like the same world.

Steps (each cached in the run folder, so the command can be re-run until it finishes):
  1. outline   - Claude writes the art style, the character designs and an N-part outline
  2. parts     - Claude writes the full parts in batches (5 per request by default)
  3. render    - voice, illustrated images, captions and music for every part
"""

import copy
import json
import math
from pathlib import Path

from pydantic import BaseModel, ValidationError

from .config import resolve
from .script import FactClaim, Scene, ShortsPack, ShortVideo, call_claude, extract_json
from .util import log, read_json, slugify, write_json


class Character(BaseModel):
    name: str
    look: str


class EpisodeOutline(BaseModel):
    part: int
    title: str
    summary: str
    cliffhanger: str


class SeriesBible(BaseModel):
    series_title: str
    art_style: str
    characters: list[Character]
    episodes: list[EpisodeOutline]


class StoryScene(BaseModel):
    narration: str
    visual: str
    characters: list[str]


class Episode(BaseModel):
    part: int
    title: str
    hook_text: str
    description: str
    hashtags: list[str]
    scenes: list[StoryScene]


class EpisodeBatch(BaseModel):
    episodes: list[Episode]


COMMON_RULES = """Rules for retelling:
- Tell it in your own words. Never quote more than a few words of the original dialogue or text.
- Characters are original illustrated designs. Never describe, name or imitate the actors from any film adaptation.
- Keep it suitable for a general YouTube audience: imply violence rather than describing gore."""


def _outline_prompt(story: str, notes: str, cfg: dict) -> str:
    sr, ch = cfg["series"], cfg["channel"]
    style_hint = sr["style_hint"] or "pick a striking non-photorealistic illustration style that suits the story"
    return f"""You are adapting a story into a {sr['parts']}-part YouTube Shorts series for the channel "{ch['name']}".
Each part is a vertical Short of about 40 seconds (about {sr['target_words']} words of narration). Watched in order,
the parts tell the whole story from beginning to end; each part ends on a cliffhanger that makes people watch the next.

{COMMON_RULES}

Story: {story}
{('Notes from the creator: ' + notes) if notes else ''}
Visual style preference: {style_hint}

Write the series plan:
- series_title: the series name as viewers will see it (under 40 characters).
- art_style: ONE sentence describing a consistent illustration style used for every image (medium, line work,
  colour palette, lighting, mood), e.g. "moody graphic-novel illustration, bold ink lines, muted teal and amber palette,
  dramatic rim lighting". Not photorealistic.
- characters: every recurring character, each with a fixed visual description (`look`) of 25 to 40 words: age, build,
  face, hair, clothing and colours. These exact descriptions are pasted into every image prompt, so make each one
  distinctive and keep clothing consistent.
- episodes: exactly {sr['parts']} entries in story order, part 1 to {sr['parts']}, covering the WHOLE story with even
  pacing (don't rush the ending). Each has: part, title (under 50 characters), summary (2 to 3 sentences of exactly what
  happens in that part) and cliffhanger (the moment or question that part ends on; for the final part, the ending).

Reply with ONLY a JSON object (no other text) in exactly this shape:
{json.dumps({"series_title": "...", "art_style": "...",
             "characters": [{"name": "...", "look": "..."}],
             "episodes": [{"part": 1, "title": "...", "summary": "...", "cliffhanger": "..."}]}, indent=2)}
"""


def _parts_prompt(bible: SeriesBible, first: int, last: int, cfg: dict) -> str:
    sr = cfg["series"]
    plan = bible.model_dump()
    return f"""You are writing parts {first} to {last} of the {len(bible.episodes)}-part YouTube Shorts series
"{bible.series_title}". Here is the series plan (characters and the outline of every part):

{json.dumps(plan, indent=2, ensure_ascii=False)}

{COMMON_RULES}

Write parts {first} to {last} in full, following the outline exactly. Viewers swipe away within 2 seconds unless
something grabs them, so every part must be built for retention:
- Narration of about {sr['target_words']} words (about 35 seconds spoken), present tense, fast and vivid, written for the
  ear: short punchy sentences, no filler, no slow scene-setting.
- The FIRST sentence is the hook: drop the viewer into the most shocking, strange or dangerous moment of this part, or a
  question they must know the answer to. Never open with "Last time", a recap or background.
- Weave any needed context in after the hook, in a few words, so the part makes sense on its own.
- Keep an open question alive the whole way through, and escalate: each line should raise the stakes.
- End on the part's cliffhanger, then ONE short teaser line that names what is coming in the next part without
  revealing it (e.g. "And in Part 4, he finds out where the Count sleeps."). The final part ends the story with a
  satisfying, haunting close instead.
- scenes: the narration split into scenes of about {sr['words_per_scene']} words each (one sentence), so the picture
  changes every 3 to 5 seconds. For each scene: `narration`; `visual` = what the image shows (shot type, action,
  setting, lighting; no style words, no text in the image); `characters` = the names (exactly as in the plan) of
  characters visible in the image, or an empty list.
- title: under 50 characters, a curiosity gap (e.g. "The Man With No Reflection").
  hook_text: 2 to 5 punchy words shown huge on screen in the first 2 seconds (e.g. "HE HAS NO REFLECTION").
  description: one sentence.
  hashtags: 3 to 5, each starting with #.

Reply with ONLY a JSON object (no other text) in exactly this shape:
{json.dumps({"episodes": [{"part": first, "title": "...", "hook_text": "...", "description": "...",
                           "hashtags": ["#..."],
                           "scenes": [{"narration": "...", "visual": "...", "characters": ["..."]}]}]}, indent=2)}
"""


def _batches(parts: int, per_batch: int) -> list:
    return [(a, min(a + per_batch - 1, parts)) for a in range(1, parts + 1, per_batch)]


class SeriesStepNeeded(Exception):
    """Not an error: the free manual mode is waiting for a pasted Claude.ai reply."""


def _manual_step(run_dir: Path, n: int, name: str, prompt: str) -> str:
    prompt_file = run_dir / f"PROMPT_{n}_{name}.txt"
    reply_file = run_dir / f"reply_{n}_{name}.txt"
    if not prompt_file.exists():
        prompt_file.write_text(prompt, encoding="utf-8")
    if not reply_file.exists():
        reply_file.touch()
    text = reply_file.read_text(encoding="utf-8")
    if not text.strip():
        raise SeriesStepNeeded(
            f"Free script step {n}:\n"
            f"  1. Open {prompt_file} and copy all of it\n"
            "  2. Paste it into a NEW chat at claude.ai and send\n"
            f"  3. Paste Claude's whole reply into {reply_file} and save\n"
            "  4. Run the same command again")
    return text


def _load_or_write(run_dir: Path, n: int, name: str, prompt: str, model_cls, cfg: dict):
    if cfg["script"]["provider"] == "manual":
        text = _manual_step(run_dir, n, name, prompt)
        try:
            return model_cls.model_validate(extract_json(text, f"reply_{n}_{name}.txt"))
        except ValidationError as e:
            raise RuntimeError(f"reply_{n}_{name}.txt is missing or has wrong fields:\n{e}\n"
                               "Ask Claude to fix those fields and resend the full JSON, then re-run") from e
    return call_claude("You write story scripts for YouTube Shorts series.", prompt, model_cls, cfg)


def write_series(run_dir: Path, story: str, notes: str, cfg: dict, dry_run: bool) -> tuple:
    """Returns (bible, episodes) once every step is done; raises SeriesStepNeeded while waiting."""
    sr = cfg["series"]
    bible_path = run_dir / "bible.json"
    if dry_run and not bible_path.exists():
        write_json(bible_path, _dummy_bible(story, sr["parts"]).model_dump())
    if bible_path.exists():
        bible = SeriesBible.model_validate(read_json(bible_path))
    else:
        bible = _load_or_write(run_dir, 1, "outline", _outline_prompt(story, notes, cfg), SeriesBible, cfg)
        bible.episodes = sorted(bible.episodes, key=lambda e: e.part)
        if not bible.episodes:
            raise RuntimeError("The outline has no episodes; ask Claude to redo it")
        write_json(bible_path, bible.model_dump())
        log(f"Outline saved: '{bible.series_title}', {len(bible.episodes)} parts, "
            f"{len(bible.characters)} characters")

    parts = len(bible.episodes)
    episodes = {}
    for n, (first, last) in enumerate(_batches(parts, sr["per_batch"]), start=2):
        path = run_dir / f"parts_{first:02d}-{last:02d}.json"
        if dry_run and not path.exists():
            write_json(path, _dummy_batch(bible, first, last).model_dump())
        if path.exists():
            batch = EpisodeBatch.model_validate(read_json(path))
        else:
            batch = _load_or_write(run_dir, n, f"parts_{first:02d}-{last:02d}",
                                   _parts_prompt(bible, first, last, cfg), EpisodeBatch, cfg)
            got = sorted(e.part for e in batch.episodes)
            if got != list(range(first, last + 1)):
                raise RuntimeError(f"Expected parts {first}-{last} but the reply has parts {got}. "
                                   f"Ask Claude to send exactly parts {first} to {last}, then re-run")
            write_json(path, batch.model_dump())
        for e in batch.episodes:
            episodes[e.part] = e
    return bible, [episodes[p] for p in sorted(episodes)]


def image_prompt(scene: StoryScene, bible: SeriesBible) -> str:
    looks = {c.name.lower(): c for c in bible.characters}
    # At most 3 designs: the image model reads only the first few hundred words of a prompt.
    cast = [looks[n.lower()] for n in scene.characters if n.lower() in looks][:3]
    text = scene.visual.strip().rstrip(".")
    if cast:
        text += ". " + " ".join(f"{c.name}: {c.look.strip().rstrip('.')}." for c in cast)
    return text


def to_pack(bible: SeriesBible, episodes: list) -> ShortsPack:
    """Express the series as a ShortsPack so the Shorts renderer, review and upload code apply."""
    total = len(episodes)
    shorts = []
    for e in episodes:
        hashtags = ["#" + h.strip().lstrip("#").replace(" ", "") for h in e.hashtags if h.strip("# ")][:5]
        shorts.append(ShortVideo(
            title=f"{e.title} | {bible.series_title} Part {e.part}"[:100],
            hook_text=f"{bible.series_title} · Part {e.part}/{total}",
            description=f"{e.description.strip()}\n\nPart {e.part} of {total} of {bible.series_title}.",
            hashtags=hashtags,
            scenes=[Scene(narration=s.narration, visual=image_prompt(s, bible), search_query="") for s in e.scenes],
            fact_check=[FactClaim(claim="(story retelling - no factual claims)", source="n/a")],
        ))
    return ShortsPack(shorts=shorts)


def overlays_for(bible: SeriesBible, episodes: list, cfg: dict) -> list:
    if not cfg["series"].get("hook_card", True):
        return [{} for _ in episodes]
    out = []
    for i, e in enumerate(episodes):
        if i + 1 < len(episodes):
            nxt = episodes[i + 1]
            end = {"end_text": f"Part {nxt.part} →", "end_sub": f"Next: {nxt.title}"}
        else:
            end = {"end_text": "The End", "end_sub": "Follow for the next story"}
        out.append({"hook": e.hook_text, **end})
    return out


def series_config(cfg: dict, bible: SeriesBible) -> dict:
    scfg = copy.deepcopy(cfg)
    scfg["images"]["provider"] = cfg["series"]["images_provider"]  # illustrations, not stock footage
    scfg["shorts"].update(voice_speed=cfg["series"]["voice_speed"], sentence_pause=cfg["series"]["sentence_pause"])
    scfg["video"]["animation"] = cfg["series"]["animation"]
    scfg["images"]["scenes_per_image"] = cfg["series"]["scenes_per_image"]
    scfg["video"]["score"] = cfg["series"].get("score", True)
    scfg["video"]["parallax"] = {**scfg["video"].get("parallax", {}), **cfg["series"].get("motion", {})}
    scfg["images"]["style"] = f"{bible.art_style.strip().rstrip('.')}, vertical 9:16 composition, no text, no lettering"
    return scfg


def make_series(story: str, notes: str, cfg: dict, dry_run: bool = False, redo: str = "",
                assume_yes: bool = False, first_n: int = 0, script_dir: str = "") -> Path:
    from .pipeline import REDO, _clear, _make_shorts
    from .util import check_ffmpeg_features, require_binary

    require_binary("ffmpeg")
    require_binary("ffprobe")
    check_ffmpeg_features(cfg["video"]["captions"])
    run_dir = resolve(cfg["runs_dir"]) / ("series-" + slugify(story) + ("-dryrun" if dry_run else ""))
    run_dir.mkdir(parents=True, exist_ok=True)
    if redo == "script":
        _clear(run_dir, ["bible.json", "parts_*.json", "PROMPT_*", "reply_*", "part_*", "metadata.json"])
    elif redo:
        _clear(run_dir, [p.replace("short_", "part_") for p in REDO[redo]])
    if not (run_dir / "run.json").exists():
        write_json(run_dir / "run.json", {"topic": story, "notes": notes, "dry_run": dry_run, "series": True})
    log(f"Series folder: {run_dir}")
    if script_dir:  # a ready-made script (bible.json + parts_*.json) skips the Claude steps
        src = resolve(script_dir)
        files = [src / "bible.json", *sorted(src.glob("parts_*.json"))]
        if not files[0].exists():
            raise RuntimeError(f"No bible.json in {src}")
        for f in files:
            dest = run_dir / f.name
            if not dest.exists() or dest.read_bytes() != f.read_bytes():
                if dest.exists():
                    log(f"Script updated: {f.name}")
                dest.write_bytes(f.read_bytes())

    bible, episodes = write_series(run_dir, story, notes, cfg, dry_run)
    regenerated = not (run_dir / "metadata.json").exists()
    result = _make_shorts(run_dir, bible.series_title, to_pack(bible, episodes), series_config(cfg, bible),
                          dry_run, assume_yes, regenerated, prefix="part", limit=first_n,
                          overlays=overlays_for(bible, episodes, cfg))
    write_shot_list(run_dir, bible, episodes, first_n or len(episodes))
    return result


# ---- real motion for key scenes (free image-to-video apps) ---------------------------------

KEY_SHOTS = 3


def key_scenes(episode: Episode) -> list:
    """The hook, the most crowded mid scene, and the cliffhanger: where motion matters most."""
    n = len(episode.scenes)
    if n <= KEY_SHOTS:
        return list(range(n))
    middle = max(range(1, n - 1), key=lambda i: (len(episode.scenes[i].characters), -abs(i - n // 2)))
    return sorted({0, middle, n - 2})


def motion_prompt(scene: StoryScene) -> str:
    return (f"Animate this illustration as a short cinematic movie shot: {scene.visual.strip().rstrip('.')}. "
            "The characters move naturally and react to each other; hair, clothes, smoke and light move; "
            "slow camera push-in. Keep the exact art style, colours and faces. No text, no new characters.")


def write_shot_list(run_dir: Path, bible: SeriesBible, episodes: list, parts: int) -> Path:
    lines = [
        f"# Make {bible.series_title} move like a movie (free)",
        "",
        "Each part is already animated in 2.5D. For real character movement, turn the key shots below into short",
        "video clips with a free image-to-video app (Meta AI, Kling, Hailuo or Google Gemini all have free daily",
        "generations), then re-run the same `series` command. Clips you add are used automatically.",
        "",
        "For each shot:",
        "1. Upload the image file to the app and choose image-to-video, vertical 9:16, about 5 seconds.",
        "2. Paste the motion prompt.",
        "3. Download the video and save it NEXT TO the image with the same name but `.mp4`",
        "   (e.g. `part_01/images/scene_000.png` -> `part_01/images/scene_000.mp4`).",
        "",
    ]
    for e in episodes[:parts]:
        lines += [f"## Part {e.part}: {e.title}", ""]
        for i in key_scenes(e):
            img = f"part_{e.part:02d}/images/scene_{i:03d}.png"
            done = (run_dir / img).with_suffix(".mp4").exists()
            lines += [f"- [{'x' if done else ' '}] `{img}`", f"  > {motion_prompt(e.scenes[i])}", ""]
    path = run_dir / "ANIMATE_ME.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    log(f"Shot list for real animated clips: {path}")
    return path


# ---- dry run ------------------------------------------------------------------------------

def _dummy_bible(story: str, parts: int) -> SeriesBible:
    return SeriesBible(
        series_title=story[:40], art_style="flat graphic illustration, bold shapes, two-tone palette",
        characters=[Character(name="Hero", look="young traveller in a long green coat and red scarf")],
        episodes=[EpisodeOutline(part=p, title=f"Chapter {p}", summary=f"Events of part {p}.",
                                 cliffhanger=f"Cliffhanger {p}") for p in range(1, parts + 1)])


def _dummy_batch(bible: SeriesBible, first: int, last: int) -> EpisodeBatch:
    return EpisodeBatch(episodes=[
        Episode(part=p, title=f"Chapter {p}", hook_text=f"Part {p}", description="Dry-run part.",
                hashtags=["#story"],
                scenes=[StoryScene(narration=f"Part {p}, beat {b}. Something happens here.",
                                   visual=f"Scene {b} of part {p}", characters=["Hero"] if b % 2 else [])
                        for b in range(1, 4)])
        for p in range(first, last + 1)])


def batch_count(parts: int, per_batch: int) -> int:
    return math.ceil(parts / per_batch)
