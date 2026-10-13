"""Loads episode.yaml, finds each scene's files and works out the timeline."""
from dataclasses import dataclass, field
from pathlib import Path

import yaml

IMAGE_EXT = (".jpg", ".jpeg", ".png", ".webp")
CLIP_EXT = (".mp4", ".mov", ".webm", ".mkv")
NARR_EXT = (".mp3", ".wav", ".m4a")

DEFAULTS = {
    "fps": 30,
    "transition_seconds": 0.6,
    "narration_lead": 0.35,       # silence before a scene's narration starts
    "narration_tail": 0.6,        # silence after it ends
    "preview_chars_per_second": 15.0,  # used to estimate timing before the voice exists
    "music_level": 0.35,          # music volume when nobody is speaking (0-1)
    "music_duck_level": 0.14,     # music volume under the narration
    "ambience_level": 0.30,
    "burn_subtitles": True,
    "zoom": 0.12,
}


@dataclass
class Sfx:
    name: str
    at: float = 0.0
    volume: float = 0.8


@dataclass
class Scene:
    key: str                  # "01", "02" ... or "intro" / "outro"
    text: str = ""
    kind: str = "scene"       # scene | card
    motion: str = "zoom_in"
    zoom: float | None = None
    music: str = "calm"
    ambience: list = field(default_factory=list)
    sfx: list = field(default_factory=list)
    min_seconds: float = 0.0
    hold: float = 0.0
    transition: str = "fade"
    prompt: str = ""
    video_clip: bool = False  # script recommends an AI video clip here
    card: dict = field(default_factory=dict)
    # resolved
    image: Path | None = None
    clip: Path | None = None
    narration: Path | None = None
    narration_seconds: float = 0.0
    estimated: bool = False
    start: float = 0.0
    duration: float = 0.0

    @property
    def visual_source(self):
        if self.kind == "card":
            return "card" if not self.image else f"card on {self.image.name}"
        if self.clip:
            return f"clip {self.clip.name}"
        if self.image:
            return f"image {self.image.name}"
        return "PLACEHOLDER"


@dataclass
class Episode:
    folder: Path
    cfg: dict
    scenes: list

    @property
    def build(self):
        return self.folder / "build"

    @property
    def slug(self):
        return self.cfg.get("slug") or self.folder.name

    @property
    def total(self):
        last = self.scenes[-1]
        return last.start + last.duration


def _find(folder, stem, exts):
    for ext in exts:
        for cand in (folder / f"{stem}{ext}", folder / f"{stem}{ext.upper()}"):
            if cand.exists():
                return cand
    return None


def _sfx_list(raw):
    out = []
    for item in raw or []:
        if isinstance(item, str):
            out.append(Sfx(item))
        else:
            out.append(Sfx(item["name"], float(item.get("at", 0)), float(item.get("volume", 0.8))))
    return out


def _scene(key, raw, kind="scene"):
    return Scene(
        key=key,
        text=(raw.get("text") or "").strip(),
        kind=kind,
        motion=raw.get("motion", "zoom_in"),
        zoom=raw.get("zoom"),
        music=raw.get("music", "calm"),
        ambience=list(raw.get("ambience") or []),
        sfx=_sfx_list(raw.get("sfx")),
        min_seconds=float(raw.get("min_seconds", 5.0 if kind == "card" else 0)),
        hold=float(raw.get("hold", 0)),
        transition=raw.get("transition", "fade"),
        prompt=(raw.get("image_prompt") or "").strip(),
        video_clip=bool(raw.get("video_clip", False)),
        card={k: raw[k] for k in ("title", "subtitle", "lines") if k in raw},
    )


def load(folder):
    folder = Path(folder).resolve()
    data = yaml.safe_load((folder / "episode.yaml").read_text(encoding="utf-8"))
    cfg = {**DEFAULTS, **(data.get("settings") or {}), **{k: v for k, v in data.items()
                                                       if k not in ("scenes", "intro", "outro", "settings")}}
    scenes = []
    if data.get("intro"):
        scenes.append(_scene("intro", data["intro"], "card"))
    for i, raw in enumerate(data["scenes"], 1):
        scenes.append(_scene(f"{i:02d}", raw))
    if data.get("outro"):
        scenes.append(_scene("outro", data["outro"], "card"))
    ep = Episode(folder, cfg, scenes)
    resolve(ep)
    return ep


def resolve(ep):
    """Attach files and compute start/duration for every scene."""
    from .dsp import read_audio, SR
    img_dir, clip_dir, narr_dir = ep.folder / "images", ep.folder / "clips", ep.folder / "narration"
    cps = float(ep.cfg["preview_chars_per_second"])
    lead, tail = float(ep.cfg["narration_lead"]), float(ep.cfg["narration_tail"])
    t = 0.0
    for sc in ep.scenes:
        sc.image = _find(img_dir, sc.key, IMAGE_EXT)
        sc.clip = _find(clip_dir, sc.key, CLIP_EXT) if sc.kind == "scene" else None
        sc.narration = _find(narr_dir, sc.key, NARR_EXT) if sc.text else None
        if sc.narration:
            sc.narration_seconds = len(read_audio(sc.narration, 1)) / SR
            sc.estimated = False
        elif sc.text:
            sc.narration_seconds = len(sc.text) / cps
            sc.estimated = True
        dur = lead + sc.narration_seconds + tail if sc.text else 0.0
        sc.duration = max(dur, sc.min_seconds, 2.0) + sc.hold
        sc.start = t
        t += sc.duration


def expand_prompt(ep, prompt):
    """Swap character names (KAMSA, DEVAKI ...) for their full descriptions and add the style."""
    chars = ep.cfg.get("characters") or {}
    for name in sorted(chars, key=len, reverse=True):
        prompt = prompt.replace(name, f"{chars[name].strip()}")
    style = (ep.cfg.get("image_style") or "").strip()
    return f"{prompt.strip()}. Style: {style}" if style else prompt.strip()


def write_prompts(ep):
    lines = [f"# Image & video prompts - {ep.cfg.get('title', ep.slug)}", "",
             "Make one picture per scene and save it in `images/` with the scene number as the name "
             "(`01.jpg`, `02.jpg` ...). Scenes marked VIDEO also look great as a 5-10 s AI video clip "
             "saved in `clips/` (`06.mp4` ...); if there is no clip the picture is used.", "",
             "Tip: generate the main characters first, then attach that picture as a reference in every "
             "later prompt so Krishna, Devaki and Kamsa look the same in every scene.", ""]
    for sc in ep.scenes:
        if sc.kind != "scene":
            continue
        tag = "  **VIDEO**" if sc.video_clip else ""
        lines += [f"## {sc.key}{tag}", "", "```", expand_prompt(ep, sc.prompt), "```", ""]
        if sc.video_clip:
            lines += ["Video clip prompt (Kling / Hailuo / Veo, 5 s, attach the image above):", "", "```",
                      f"Animate this image with slow cinematic camera movement: {sc.prompt.strip()}. "
                      "Natural motion, rain/wind/light effects move gently, faces stay consistent, "
                      "no text, 16:9.", "```", ""]
    thumb = ep.cfg.get("thumbnail_text", "").replace("\n", " ")
    lines += ["## thumbnail", "", "```",
              expand_prompt(ep, "BABY_KRISHNA glowing in a basket held above stormy Yamuna waters, giant "
                                "Adishesha hoods sheltering him, lightning, extremely vivid colours, close-up, "
                                "big empty space at the bottom for title text"), "```", "",
              f"Save it as `images/thumbnail.jpg`, then run `python make.py thumb` to add the title "
              f"({thumb}).", ""]
    (ep.folder / "IMAGE_PROMPTS.md").write_text("\n".join(lines), encoding="utf-8")
