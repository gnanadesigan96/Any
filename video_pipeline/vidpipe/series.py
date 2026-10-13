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
    language: str = ""  # narration language; empty means the config's series.language


class StoryScene(BaseModel):
    narration: str
    visual: str
    characters: list[str]
    subtitle: str = ""  # on-screen caption in another language than the narration (e.g. English under Tamil)
    kind: str = ""      # "countdown" (silent, blurred poster), "reveal" (the poster), "outro" (end screen); last only
    seconds: float = 0.0  # countdown length; for reveal / outro, the least time the scene is held on screen


class Episode(BaseModel):
    part: int
    title: str
    hook_text: str
    description: str
    hashtags: list[str]
    scenes: list[StoryScene]
    hook_sub: str = ""  # optional second line under the opening title card, e.g. "60 விநாடியில் முழுக் கதை"
    reveal_text: str = ""  # shown over the poster in the reveal scene, e.g. "பதில்: <film>"
    end_text: str = ""  # optional end card instead of "Part N+1 →" / "The End", e.g. a quiz question
    end_sub: str = ""
    hook_note: str = ""  # a third line on the opening card; makes it a panel card with the title in English
    outro: dict = {}  # the closing screen of an "outro" scene: title, sub, button, handle, thanks, thanks_sub


class EpisodeBatch(BaseModel):
    episodes: list[Episode]


COMMON_RULES = """Rules for retelling:
- Tell it in your own words. Never quote more than a few words of the original dialogue or text.
- Characters are original illustrated designs. Never describe, name or imitate the actors from any film adaptation.
- Keep it suitable for a general YouTube audience: imply violence rather than describing gore."""


# On-screen words of the end cards, per narration language.
UI_TEXT = {
    "english": {"part": "Part {n} →", "next": "Next: {title}", "end": "The End", "follow": "Follow for the next story",
                "tag": "PART {n}", "of": "Part {n} of {total}."},
    "tamil": {"part": "பாகம் {n} →", "next": "அடுத்து: {title}", "end": "முடிவு",
              "follow": "அடுத்த கதைக்குக் காத்திருங்கள்", "tag": "பாகம் {n}", "of": "பாகம் {n} / {total}."},
}


def language_of(cfg: dict, bible: "SeriesBible" = None) -> str:
    return ((bible.language if bible else "") or cfg["series"].get("language") or "English").strip()


def series_settings(cfg: dict, language: str = "") -> dict:
    """cfg["series"] with the narration language's overrides (length in words, scene size, speaking rate)."""
    sr = dict(cfg["series"])
    sr["words_per_second"] = 2.8
    sr.update(cfg["series"].get("languages", {}).get((language or language_of(cfg)).lower(), {}))
    return sr


# How people actually talk, per language: the narration should sound like everyday speech, not writing.
SLANG = {
    "tamil": ("Write plain everyday spoken Tamil, the way an ordinary person tells a story to family or friends "
              "today: spoken verb forms (பண்ணிடுறான், போயிடுறா, கேக்கல, சொல்றாரு), simple common words, and only the "
              "English words everyone already uses in Tamil, written in Tamil script (ஸ்கூல், போலீஸ், கேஸ், பார்ட்டி, "
              "ட்விஸ்ட்). No forced slang or catchphrases (no ப்ரோ, மச்சான், செம்ம, வேற லெவல், மாஸ்) and no written or "
              "literary Tamil (இலக்கு, தயாரிப்பாளர், திருப்பம், அசாத்திய). "),
}


def _language_rules(language: str) -> str:
    if language.lower() == "english":
        return ""
    return (f"\nLanguage: write every `narration`, `title`, `hook_text` and `description` in {language}: "
            f"natural, everyday spoken {language} as people talk today (gripping, simple words, with the English words "
            f"everyone already uses; never formal, bookish or old-fashioned, and no forced slang). {SLANG.get(language.lower(), '')}"
            f"Keep character and place names as they are commonly said in {language}. "
            "Write `visual`, `art_style`, character `look`, `summary` and `cliffhanger` in English (they are only used to "
            "draw the pictures and plan the story). Hashtags: a mix of English and " + language + ".")


def _outline_prompt(story: str, notes: str, cfg: dict) -> str:
    sr, ch = series_settings(cfg), cfg["channel"]
    style_hint = sr["style_hint"] or "pick a striking non-photorealistic illustration style that suits the story"
    seconds = round(sr["target_words"] / sr["words_per_second"])
    acts = ("Structure the parts as acts: part 1 sets up the world and ends on the moment everything goes wrong; the "
            "middle part(s) escalate with a major twist; the final part delivers the climax and a haunting resolution. "
            if sr["parts"] <= 5 else "")
    return f"""You are adapting a story into a {sr['parts']}-part YouTube Shorts series for the channel "{ch['name']}".
Each part is a vertical Short of about {seconds} seconds (about {sr['target_words']} words of narration). Watched in
order, the parts tell the whole story from beginning to end; each part ends on a cliffhanger that makes people
desperate to watch the next. {acts}

{COMMON_RULES}{_language_rules(language_of(cfg))}

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
    language = language_of(cfg, bible)
    sr = series_settings(cfg, language)
    plan = bible.model_dump()
    return f"""You are writing parts {first} to {last} of the {len(bible.episodes)}-part YouTube Shorts series
"{bible.series_title}". Here is the series plan (characters and the outline of every part):

{json.dumps(plan, indent=2, ensure_ascii=False)}

{COMMON_RULES}{_language_rules(language)}

Write parts {first} to {last} in full, following the outline exactly. Viewers swipe away within 2 seconds unless
something grabs them, so every part must be built for retention:
- Narration of about {sr['target_words']} words (about {round(sr['target_words'] / sr['words_per_second'])} seconds spoken), fast and vivid,
  written for the ear: short punchy sentences, no filler, no slow scene-setting.
- The FIRST sentence is the hook: drop the viewer into the most shocking, strange or dangerous moment of this part, or a
  question they must know the answer to. Never open with "Last time", a recap or background.
- Weave any needed context in after the hook, in a few words, so the part makes sense on its own.
- Keep an open question alive the whole way through, and escalate: each line should raise the stakes.
- Re-hook every 15 to 20 seconds with a turn, a reveal or a new question ("Then he saw the boxes."), so nobody
  swipes away halfway through.
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
        write_json(bible_path, {**_dummy_bible(story, sr["parts"]).model_dump(), "language": language_of(cfg)})
    if bible_path.exists():
        bible = SeriesBible.model_validate(read_json(bible_path))
    else:
        bible = _load_or_write(run_dir, 1, "outline", _outline_prompt(story, notes, cfg), SeriesBible, cfg)
        bible.episodes = sorted(bible.episodes, key=lambda e: e.part)
        if not bible.episodes:
            raise RuntimeError("The outline has no episodes; ask Claude to redo it")
        bible.language = bible.language or language_of(cfg)
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
    # Framing first: the image model weighs the start of the prompt most, and the 2.5D camera moves crop the edges.
    text = (f"{scene.visual.strip().rstrip('.')}. Framing: every person's whole head and face inside the frame with "
            "clear space above the head, main subject in the centre of the frame, sharp natural faces")
    if cast:
        text += ". " + " ".join(f"{c.name}: {c.look.strip().rstrip('.')}." for c in cast)
    return text


def ui_text(cfg: dict, bible: SeriesBible, episodes: list) -> dict:
    """On-screen words: English when English subtitles are shown, otherwise the narration's language."""
    if has_subtitles(episodes):
        return UI_TEXT["english"]
    return UI_TEXT.get(language_of(cfg, bible).lower(), UI_TEXT["english"])


def to_pack(bible: SeriesBible, episodes: list, ui: dict = None) -> ShortsPack:
    """Express the series as a ShortsPack so the Shorts renderer, review and upload code apply."""
    total = len(episodes)
    ui = ui or UI_TEXT["english"]
    shorts = []
    for e in episodes:
        hashtags = ["#" + h.strip().lstrip("#").replace(" ", "") for h in e.hashtags if h.strip("# ")][:5]
        shorts.append(ShortVideo(
            title=(f"{e.title} | {bible.series_title} {ui['tag'].format(n=e.part).title()}" if total > 1
                   else f"{e.title} | {bible.series_title}")[:100],
            # A small part tag (none for a one-part story); the story's name is never shown on screen.
            hook_text=ui["tag"].format(n=e.part) if total > 1 else "",
            description=e.description.strip() + (f"\n\n{ui['of'].format(n=e.part, total=total)}" if total > 1 else ""),
            hashtags=hashtags,
            scenes=[Scene(narration=s.narration, visual=s.visual if s.kind else image_prompt(s, bible), search_query="",
                          kind=s.kind, seconds=s.seconds) for s in e.scenes],
            fact_check=[FactClaim(claim="(story retelling - no factual claims)", source="n/a")],
        ))
    return ShortsPack(shorts=shorts)


def overlays_for(bible: SeriesBible, episodes: list, cfg: dict) -> list:
    if not cfg["series"].get("hook_card", True):
        return [{} for _ in episodes]
    subtitled = has_subtitles(episodes)  # on-screen text in English, whatever language is spoken
    ui = ui_text(cfg, bible, episodes)
    out = []
    for i, e in enumerate(episodes):
        if i + 1 < len(episodes):
            nxt = episodes[i + 1]
            end = {"end_text": ui["part"].format(n=nxt.part), "end_sub": ui["next"].format(title=nxt.title)}
        else:
            end = {"end_text": ui["end"], "end_sub": ui["follow"]}
        if e.end_text:
            end = {"end_text": e.end_text, "end_sub": e.end_sub}
        out.append({"hook": e.hook_text, **({"hook_sub": e.hook_sub} if e.hook_sub else {}),
                    **({"hook_note": e.hook_note} if e.hook_note else {}), **({"outro": e.outro} if e.outro else {}), **end})
        if any(sc.kind for sc in e.scenes):  # countdown / poster reveal at the end
            out[-1].update(kinds=[sc.kind for sc in e.scenes], reveal_text=e.reveal_text)
        if subtitled:
            out[-1]["subtitles"] = [sc.subtitle for sc in e.scenes]
    return out


def has_subtitles(episodes: list) -> bool:
    return any(sc.subtitle.strip() for e in episodes for sc in e.scenes)


def series_config(cfg: dict, bible: SeriesBible, episodes: list = ()) -> dict:
    scfg = copy.deepcopy(cfg)
    scfg["images"]["provider"] = cfg["series"]["images_provider"]  # illustrations, not stock footage
    scfg["shorts"].update(voice_speed=cfg["series"]["voice_speed"], sentence_pause=cfg["series"]["sentence_pause"])
    scfg["video"]["animation"] = cfg["series"]["animation"]
    scfg["video"]["title_style"] = cfg["series"].get("title_style", "tag")
    scfg["voice"]["tempo"] = cfg["series"].get("voice_tempo", 1.0)
    scfg["shorts"]["part_seconds"] = cfg["series"].get("part_seconds", 0)
    scfg["images"]["scenes_per_image"] = cfg["series"]["scenes_per_image"]
    scfg["video"]["score"] = cfg["series"].get("score", True)
    scfg["video"]["parallax"] = {**scfg["video"].get("parallax", {}), **cfg["series"].get("motion", {})}
    scfg["images"]["style"] = f"{bible.art_style.strip().rstrip('.')}, vertical 9:16 composition, no text, no lettering"
    language = language_of(cfg, bible)
    provider = cfg["series"].get("voice_provider", "auto")
    if provider == "elevenlabs":  # expressive storyteller voice in any language (paid)
        scfg["voice"]["provider"] = "elevenlabs"
        if cfg["series"].get("voice_id"):
            scfg["voice"]["voice_id"] = cfg["series"]["voice_id"]
    elif provider == "gemini":  # expressive Google voice in any language (free tier)
        scfg["voice"]["provider"] = "gemini"
        if cfg["series"].get("gemini_voice"):
            scfg["voice"]["gemini"] = {**scfg["voice"]["gemini"], "voice": cfg["series"]["gemini_voice"]}
    if language.lower() != "english":  # Kokoro speaks English only: use the free Edge voice for this language
        lang = series_settings(cfg, language)
        if provider not in ("elevenlabs", "gemini"):
            edge = scfg["voice"]["edge"]
            scfg["voice"]["provider"] = "edge"
            scfg["voice"]["edge"] = {**edge, "voice": cfg["series"].get("edge_voice") or lang.get("voice", edge["voice"]),
                                     "rate": cfg["series"].get("voice_rate") or lang.get("rate", edge["rate"]),
                                     "pitch": cfg["series"].get("voice_pitch") or lang.get("pitch", edge["pitch"])}
        if lang.get("font") and not has_subtitles(episodes):
            scfg["video"]["caption_font"] = lang["font"]
        if lang.get("caption_max_words") and not has_subtitles(episodes):
            scfg["shorts"]["caption_max_words"] = lang["caption_max_words"]
    return scfg


def make_series(story: str, notes: str, cfg: dict, dry_run: bool = False, redo: str = "",
                assume_yes: bool = False, first_n: int = 0, script_dir: str = "") -> Path:
    from .pipeline import REDO, _clear, _make_shorts
    from .util import check_ffmpeg_features, require_binary

    require_binary("ffmpeg")
    require_binary("ffprobe")
    check_ffmpeg_features(cfg["video"]["captions"])
    language = language_of(cfg)
    if script_dir and (resolve(script_dir) / "bible.json").exists():
        language = (read_json(resolve(script_dir) / "bible.json", {}) or {}).get("language") or language
    suffix = "" if language.lower() == "english" else "-" + slugify(language)
    run_dir = resolve(cfg["runs_dir"]) / ("series-" + slugify(story) + suffix + ("-dryrun" if dry_run else ""))
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
        for old in run_dir.glob("parts_*.json"):  # parts files from an older version of the script
            if not (src / old.name).exists():
                log(f"Script updated: removed {old.name}")
                old.unlink()

    bible, episodes = write_series(run_dir, story, notes, cfg, dry_run)
    if any(sc.kind for e in episodes for sc in e.scenes):  # needs the film's poster: check before spending anything
        _copy_poster(resolve(script_dir) if script_dir else None, run_dir, dry_run)
    regenerated = not (run_dir / "metadata.json").exists()
    result = _make_shorts(run_dir, bible.series_title, to_pack(bible, episodes, ui_text(cfg, bible, episodes)), series_config(cfg, bible, episodes),
                          dry_run, assume_yes, regenerated, prefix="part", limit=first_n,
                          overlays=overlays_for(bible, episodes, cfg))
    write_shot_list(run_dir, bible, episodes, first_n or len(episodes))
    _remove_extra_parts(run_dir, len(episodes))
    return result


def _remove_extra_parts(run_dir: Path, parts: int) -> None:
    """When a series is rewritten with fewer parts, delete the leftover videos so they can't be uploaded by
    mistake. Their pictures were already saved to library/ and are reused wherever the same shot appears."""
    import shutil
    for path in run_dir.glob("part_*"):
        num = path.name[5:].split(".")[0]
        if num.isdigit() and int(num) > parts:
            shutil.rmtree(path) if path.is_dir() else path.unlink()


# ---- real motion for key scenes (free image-to-video apps) ---------------------------------

def key_scenes(episode: Episode) -> list:
    """The hook, the most crowded scene in each half, and the cliffhanger: where motion matters most."""
    n = len(episode.scenes)
    if n <= 4:
        return list(range(n))

    def busiest(lo, hi):
        return max(range(lo, hi), key=lambda i: (len(episode.scenes[i].characters), -abs(i - (lo + hi) // 2)))

    picks = {0, n - 2, busiest(1, n // 2)}
    if n >= 12:
        picks.add(busiest(n // 2, n - 2))
    return sorted(picks)


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


POSTER_NAMES = [f"poster{ext}" for ext in (".jpg", ".jpeg", ".png", ".webp")]


def find_poster(run_dir: Path):
    return next((run_dir / n for n in POSTER_NAMES if (run_dir / n).exists()), None)


def _copy_poster(src: Path, run_dir: Path, dry_run: bool) -> Path:
    """The story folder's poster.jpg/.png/... is used for the countdown and the reveal."""
    for name in POSTER_NAMES:
        f = src / name if src else None
        if f and f.exists():
            for old in POSTER_NAMES:
                if old != name:
                    (run_dir / old).unlink(missing_ok=True)
            dest = run_dir / name
            if not dest.exists() or dest.read_bytes() != f.read_bytes():
                dest.write_bytes(f.read_bytes())
            return dest
    if find_poster(run_dir):
        return find_poster(run_dir)
    if dry_run:  # a stand-in poster so dry runs work without one
        from PIL import Image, ImageDraw
        img = Image.new("RGB", (1000, 1500), (40, 30, 60))
        ImageDraw.Draw(img).rectangle([80, 80, 920, 1420], outline=(230, 200, 80), width=12)
        img.save(run_dir / "poster.jpg")
        return run_dir / "poster.jpg"
    where = src / "poster.jpg" if src else run_dir / "poster.jpg"
    raise RuntimeError(f"This video ends with the film's poster: save it as {where} (or .png / .webp) and run again.")
