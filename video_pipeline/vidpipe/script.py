"""Stage 1: research + script + metadata, as one structured Claude call."""

import json
import re
from pathlib import Path

import anthropic
from pydantic import BaseModel, ValidationError

from .util import log


class Scene(BaseModel):
    narration: str
    visual: str
    search_query: str


class Chapter(BaseModel):
    title: str
    start_scene: int


class ShortClip(BaseModel):
    hook_title: str
    start_scene: int
    end_scene: int


class FactClaim(BaseModel):
    claim: str
    source: str


class ShortVideo(BaseModel):
    title: str
    hook_text: str
    description: str
    hashtags: list[str]
    scenes: list[Scene]
    fact_check: list[FactClaim]


class ShortsPack(BaseModel):
    shorts: list[ShortVideo]


class VideoScript(BaseModel):
    titles: list[str]
    description: str
    tags: list[str]
    thumbnail_texts: list[str]
    thumbnail_visual: str
    thumbnail_search_query: str
    scenes: list[Scene]
    chapters: list[Chapter]
    shorts: list[ShortClip]
    fact_check: list[FactClaim]


SYSTEM_PROMPT = """You write scripts for "{name}", a faceless YouTube documentary channel about {niche}.
Audience: {audience}. Voice: {tone}. Language: {language}.

The channel only survives if every video is accurate, original and genuinely worth watching, so:
- Use only well-documented facts. If a detail is disputed or uncertain, say so in the narration or leave it out. Never invent quotes, names, numbers or dates.
- Give the video a clear point of view: why it happened, what it reveals, why it still matters.
- Write for the ear: short sentences, concrete images, no lists read aloud, no filler, no "in this video" or "don't forget to subscribe".

Structure:
- Hook (first two scenes): open on the most dramatic or surprising moment, then pose the question the video answers.
- Context, then three or four acts that each end on a small open question, then the payoff and a one-line closing thought.

Output fields:
- scenes: the full narration split into scenes of about {words_per_scene} words (one or two sentences). Each scene's `visual` is an image-generation prompt for a single still image that illustrates that moment: subject, setting, era, camera angle, mood. Describe the image only; no art-style words (style is added later), and no text, captions, logos or real living people's faces in the image. Each scene's `search_query` is 2 to 4 plain keywords for finding matching stock footage on Pexels or Pixabay (e.g. "suspension bridge wind", "factory workers 1950s", "stock market screen"): generic, visual and likely to exist as stock, never a specific event name.
- titles: three title options under 60 characters, curiosity-driven but truthful.
- description: two or three sentences summarising the video for the YouTube description (no hashtags, no links, no timestamps).
- tags: 8 to 12 search tags.
- thumbnail_texts: three options of 2 to 4 punchy words each.
- thumbnail_visual: an image prompt for a striking thumbnail background (same rules as scene visuals).
- thumbnail_search_query: 2 to 4 stock-photo keywords for the same thumbnail background.
- chapters: 4 to 7 chapters; the first must have start_scene 0; start_scene values are increasing 0-based scene indexes.
- shorts: {num_shorts} self-contained moments for 30 to 55 second vertical Shorts, as inclusive 0-based scene ranges that make sense without the rest of the video, each with a hook_title under 60 characters.
- fact_check: every specific factual claim in the narration (names, dates, numbers, causes) with the source a human should check it against."""


SHORTS_PROMPT = """You write YouTube Shorts for "{name}", a faceless channel about {niche}.
Audience: {audience}. Voice: {tone}. Language: {language}.

The channel only survives if every Short is accurate, original and genuinely worth watching, so:
- Use only well-documented facts. If a detail is disputed or uncertain, leave it out. Never invent quotes, names, numbers or dates.
- Write for the ear: short, punchy sentences; concrete images; no filler.

From the topic, write {count} separate Shorts. Each one covers a DIFFERENT surprising angle of the topic and must make complete sense on its own (viewers won't have seen the others).

Each Short:
- About {words} words of narration (roughly 40 to 50 seconds spoken).
- The first sentence is the hook: a surprising fact, claim or question that stops the scroll within 2 seconds. No greetings, no "did you know", no "in this video", no "let's dive in".
- Builds quickly to one satisfying payoff. The last line should land hard, ideally echoing the opening so the Short loops well.
- No calls to action (no "like and subscribe", no "follow for more").

Fields for each Short:
- title: under 60 characters, curiosity-driven but truthful (do not add #Shorts).
- hook_text: 2 to 5 words shown on screen during the Short (e.g. "The bridge that danced").
- description: one or two sentences (no hashtags, no links).
- hashtags: 3 to 5 relevant hashtags, each starting with # and without spaces.
- scenes: the narration split into scenes of about {words_per_scene} words (one short sentence each), so the picture changes every 3 to 4 seconds. Each scene's `visual` describes a single image for that moment (subject, setting, era, mood; no text, logos or real living people's faces). Each scene's `search_query` is 2 to 4 plain keywords for finding matching stock video on Pexels or Pixabay (e.g. "suspension bridge wind", "storm clouds timelapse"): generic, visual and likely to exist as stock footage, never a specific event name.
- fact_check: every specific factual claim (names, dates, numbers, causes) with the source a human should check it against."""


def is_shorts(cfg: dict) -> bool:
    return cfg.get("format") == "shorts"


def script_model(cfg: dict):
    return ShortsPack if is_shorts(cfg) else VideoScript


def _user_prompt(topic: str, angle: str, cfg: dict) -> str:
    if is_shorts(cfg):
        lines = [f"Topic: {topic}"]
        if angle:
            lines.append(f"Background angle: {angle}")
        return "\n".join(lines)
    s = cfg["script"]
    lines = [f"Topic: {topic}"]
    if angle:
        lines.append(f"Angle / hook to build around: {angle}")
    lines.append(f"Target length: about {s['target_words']} words of narration "
                 f"(roughly {s['target_words'] // 150} minutes).")
    return "\n".join(lines)


def _system_prompt(cfg: dict) -> str:
    s, ch = cfg["script"], cfg["channel"]
    if is_shorts(cfg):
        sh = cfg["shorts"]
        return SHORTS_PROMPT.format(
            name=ch["name"], niche=ch["niche"], audience=ch["audience"], tone=ch["tone"],
            language=ch["language"], count=sh["per_topic"], words=sh["target_words"],
            words_per_scene=sh["words_per_scene"],
        )
    return SYSTEM_PROMPT.format(
        name=ch["name"], niche=ch["niche"], audience=ch["audience"], tone=ch["tone"],
        language=ch["language"], words_per_scene=s["words_per_scene"],
        num_shorts=s["num_shorts"],
    )


def generate_script(topic: str, angle: str, cfg: dict):
    s = cfg["script"]
    system = _system_prompt(cfg)
    client = anthropic.Anthropic(timeout=900.0)
    log(f"Writing script with {s['model']} (effort={s['effort']})...")
    try:
        response = client.beta.messages.parse(
            model=s["model"],
            max_tokens=32000,
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
            output_config={"effort": s["effort"]},
            system=system,
            messages=[{"role": "user", "content": _user_prompt(topic, angle, cfg)}],
            output_format=script_model(cfg),
        )
    except anthropic.AuthenticationError as e:
        raise RuntimeError("Claude API authentication failed - set ANTHROPIC_API_KEY in .env") from e
    except anthropic.RateLimitError as e:
        raise RuntimeError("Claude API rate limit hit - wait a minute and re-run (finished stages are kept)") from e
    except anthropic.APIStatusError as e:
        raise RuntimeError(f"Claude API error {e.status_code}: {e.message}") from e
    except anthropic.APIConnectionError as e:
        raise RuntimeError("Could not reach the Claude API - check your network") from e

    if response.stop_reason == "refusal":
        category = response.stop_details.category if response.stop_details else None
        raise RuntimeError(f"Claude declined this topic (category: {category}); pick another topic")
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Script was cut off at max_tokens; lower script.target_words and retry")
    script = response.parsed_output
    if script is None:
        raise RuntimeError("Claude returned no parsable script; re-run the script stage")
    return finalize(script, cfg)


def finalize(script, cfg: dict):
    return validate_shorts(script, cfg) if is_shorts(cfg) else validate_script(script, cfg)


def validate_shorts(pack: ShortsPack, cfg: dict) -> ShortsPack:
    max_scenes = cfg["shorts"]["max_scenes"]
    kept = []
    for short in pack.shorts:
        if not short.scenes:
            continue
        short.scenes = short.scenes[:max_scenes]
        short.hashtags = ["#" + h.strip().lstrip("#").replace(" ", "") for h in short.hashtags if h.strip("# ")][:5]
        kept.append(short)
    if not kept:
        raise RuntimeError("The script has no Shorts with scenes")
    pack.shorts = kept[: cfg["shorts"]["per_topic"]]
    return pack


def validate_script(script: VideoScript, cfg: dict) -> VideoScript:
    """Clamp model output into a shape the renderer can rely on."""
    n = len(script.scenes)
    if n == 0:
        raise RuntimeError("Script has no scenes")
    max_scenes = cfg["script"]["max_scenes"]
    if n > max_scenes:
        log(f"Script has {n} scenes; keeping the first {max_scenes} (raise script.max_scenes to keep all)")
        script.scenes = script.scenes[:max_scenes]
        n = max_scenes

    chapters, last = [], -1
    for c in script.chapters:
        if last < c.start_scene < n:
            chapters.append(c)
            last = c.start_scene
    if not chapters or chapters[0].start_scene != 0:
        chapters.insert(0, Chapter(title="Introduction", start_scene=0))
    script.chapters = chapters

    script.shorts = [
        sc for sc in script.shorts
        if 0 <= sc.start_scene <= sc.end_scene < n
    ]
    if not script.titles:
        script.titles = ["Untitled"]
    if not script.thumbnail_texts:
        script.thumbnail_texts = [script.titles[0]]
    return script


def dummy_script(topic: str, angle: str, cfg: dict) -> VideoScript:
    """Offline stand-in used by --dry-run so the rest of the pipeline can be tested free."""
    beats = [
        f"This is a dry-run narration for {topic}.",
        "In a real run, Claude writes this scene from careful research.",
        "Each scene gets its own illustration and a slow camera move.",
        "Captions follow the voice word by word, timed from the audio.",
        "Chapters, thumbnails and Shorts are generated automatically.",
        "Nothing is uploaded until you review the video and approve it.",
    ]
    scenes = [Scene(narration=b, visual=f"Illustration {i + 1} for {topic}", search_query="city skyline")
              for i, b in enumerate(beats)]
    return validate_script(VideoScript(
        titles=[f"{topic} (dry run)"[:60]],
        description=f"Dry-run description for {topic}. {angle}".strip(),
        tags=["dry run", "test"],
        thumbnail_texts=["DRY RUN", "TEST ONLY", "NOT REAL"],
        thumbnail_visual=f"Thumbnail background for {topic}",
        thumbnail_search_query="dramatic sky",
        scenes=scenes,
        chapters=[Chapter(title="Start", start_scene=0), Chapter(title="How it works", start_scene=2),
                  Chapter(title="Review", start_scene=4)],
        shorts=[ShortClip(hook_title="Dry-run Short", start_scene=1, end_scene=3)],
        fact_check=[FactClaim(claim="(dry run - no claims)", source="n/a")],
    ), cfg)


# ---- manual mode: free, via the Claude.ai chat app -------------------------------------

MANUAL_PROMPT = "PROMPT_FOR_CLAUDE.txt"
MANUAL_REPLY = "claude_reply.txt"

EXAMPLE_JSON = {
    "titles": ["...", "...", "..."],
    "description": "...",
    "tags": ["...", "..."],
    "thumbnail_texts": ["...", "...", "..."],
    "thumbnail_visual": "...",
    "thumbnail_search_query": "...",
    "scenes": [{"narration": "...", "visual": "...", "search_query": "..."}],
    "chapters": [{"title": "...", "start_scene": 0}],
    "shorts": [{"hook_title": "...", "start_scene": 0, "end_scene": 4}],
    "fact_check": [{"claim": "...", "source": "..."}],
}


EXAMPLE_SHORTS_JSON = {
    "shorts": [{
        "title": "...",
        "hook_text": "...",
        "description": "...",
        "hashtags": ["#...", "#..."],
        "scenes": [{"narration": "...", "visual": "...", "search_query": "..."}],
        "fact_check": [{"claim": "...", "source": "..."}],
    }],
}


def write_manual_prompt(topic: str, angle: str, run_dir: Path, cfg: dict) -> Path:
    path = run_dir / MANUAL_PROMPT
    example = EXAMPLE_SHORTS_JSON if is_shorts(cfg) else EXAMPLE_JSON
    path.write_text(
        _system_prompt(cfg) + "\n\n" + _user_prompt(topic, angle, cfg) + "\n\n"
        "Reply with ONLY a JSON object (no other text) in exactly this shape, with every field filled in:\n"
        + json.dumps(example, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def parse_manual_reply(text: str, cfg: dict):
    """Accepts the reply as pasted: tolerates ```json fences and text around the JSON."""
    text = re.sub(r"```(?:json)?", "", text)
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise RuntimeError(f"No JSON found in {MANUAL_REPLY}; paste Claude's whole reply into it")
    try:
        data = json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        raise RuntimeError(f"{MANUAL_REPLY} isn't valid JSON ({e}). If the reply was cut off, "
                           "ask Claude to 'continue', paste the rest after it, and re-run") from e
    try:
        return finalize(load_any(data, cfg), cfg)
    except ValidationError as e:
        raise RuntimeError(f"The reply is missing or has wrong fields:\n{e}\n"
                           "Ask Claude to fix those fields and resend the full JSON") from e


def load_script_dict(data: dict) -> VideoScript:
    """Validate a stored/pasted script, filling fields that older versions didn't have."""
    data.setdefault("thumbnail_search_query", data.get("thumbnail_visual", ""))
    for scene in data.get("scenes", []):
        if isinstance(scene, dict):
            scene.setdefault("search_query", " ".join(scene.get("visual", "").split()[:4]))
    return VideoScript.model_validate(data)


def load_any(data: dict, cfg: dict):
    """Load a stored or pasted script in whichever format the config uses."""
    if not is_shorts(cfg):
        return load_script_dict(data)
    for short in data.get("shorts", []) if isinstance(data, dict) else []:
        for scene in short.get("scenes", []) if isinstance(short, dict) else []:
            if isinstance(scene, dict):
                scene.setdefault("search_query", " ".join(scene.get("visual", "").split()[:4]))
    return ShortsPack.model_validate(data)


def dummy_shorts(topic: str, angle: str, cfg: dict) -> ShortsPack:
    """Offline stand-in used by --dry-run in Shorts mode."""
    shorts = []
    for k in range(cfg["shorts"]["per_topic"]):
        beats = [f"Dry-run Short {k + 1} about {topic}.", "This line would be the build-up.",
                 "Here the facts land fast.", "And this is the payoff line."]
        shorts.append(ShortVideo(
            title=f"Dry run {k + 1}: {topic}"[:60], hook_text=f"Dry run {k + 1}",
            description="Dry-run description.", hashtags=["#dryrun", "#test"],
            scenes=[Scene(narration=b, visual=f"Visual {i}", search_query="city skyline") for i, b in enumerate(beats)],
            fact_check=[FactClaim(claim="(dry run - no claims)", source="n/a")],
        ))
    return validate_shorts(ShortsPack(shorts=shorts), cfg)
