#!/usr/bin/env python3
"""Build pipeline/episodes/short01.json from the episode files.

The manifest is the single source of truth for the pipeline: prompts, refs,
voice lines, timings, sound effects and music cues. Re-run this after editing
the prompt packs or the voice-lines file:
    python make_manifest.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def rd(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def block_after(text, marker):
    i = text.index(marker)
    return re.search(r"```\n(.*?)```", text[i:], re.S).group(1).strip()


pack = rd("GEMINI-PROMPT-PACK.md")
only = rd("GEMINI-ONLY-PROMPT-PACK.md")
lines_md = rd("episodes/ep01-voice-lines-elevenlabs.md")

# ---- character + background reference prompts
CHARS = ["krishna_child", "yashoda", "shridama", "subala", "balarama"]
refs = {}
for key in CHARS:
    sec = pack[pack.index(f"save as `{key}_full.png`") - 200:]
    refs[f"{key}_full"] = {"prompt": block_after(sec, f"`{key}_full.png`")}
    for kind in ("turnaround", "expressions", "front"):
        refs[f"{key}_{kind}"] = {"prompt": block_after(sec, f"`{key}_{kind}.png`"), "from": f"{key}_full"}
refs["bg_mainroom"] = {"prompt": block_after(pack, "→ `bg_mainroom.png`")}

# ---- shots (Short, Part A of the Gemini-only pack)
part_a = only[only.index("## Part A"):only.index("## Part B")]
TIMING = {  # id: (start, edit duration, veo seconds, method)
    "S01": (0.0, 3.0, 4, "A"), "S02": (3.0, 5.0, 6, "C"), "S03": (8.0, 7.0, 8, "A"),
    "S04": (15.0, 6.0, 6, "B"), "S05": (21.0, 5.0, 6, "B"), "S06a": (26.0, 2.0, 4, "none"),
    "S06b": (28.0, 2.0, 4, "B"), "S07": (30.0, 4.0, 4, "none"), "S08a": (34.0, 3.0, 4, "A"),
    "S08b": (37.0, 4.0, 4, "A"), "S09": (41.0, 6.0, 6, "A"), "S10": (47.0, 4.0, 4, "B"),
    "S11a": (51.0, 2.0, 4, "C"), "S11b": (53.0, 4.0, 4, "A"), "S12a": (57.0, 3.0, 4, "C"),
    "S12b": (60.0, 2.0, 4, "none"),
}
shots = []
for m in re.finditer(r"\*\*(Shot (\d+)|(\d+[ab])): ① First frame\*\* · Refs: ([^\n]+)\n```\n(.*?)```\n\n\*\*[^\n]*② Video prompt[^\n]*\*\*\n```\n(.*?)```", part_a, re.S):
    sid = "S%02d" % int(m.group(2)) if m.group(2) else "S%02d%s" % (int(m.group(3)[:-1]), m.group(3)[-1])
    ref_names = [r.split(" (")[0].strip() for r in m.group(4).split(",")] if not m.group(4).startswith("none") else []
    ref_names = [r for r in ref_names if r]
    if sid in ("S03", "S04", "S05", "S07", "S09"):
        ref_names.append("bg_mainroom")
    start, dur, veo, method = TIMING[sid]
    m_video = re.sub(r"\.?\s*\*\*[Cc]heck [^)\n]*", "", m.group(6).strip())
    shots.append({"id": sid, "start": start, "dur": dur, "veo_seconds": veo, "method": method,
                  "refs": ref_names, "frame_prompt": m.group(5).strip(), "video_prompt": m_video,
                  "lines": [], "keep_clip_audio_db": None})
# Key moments that get real AI video (Veo) in the low-cost mode; all other shots use a cinematic camera move
# on the still frame. Speaking close-ups (lip-sync) and the reveal.
HERO = {"S01", "S08a", "S08b", "S09", "S11b", "S12a"}
MOVE = {"S01": "tilt_up", "S02": "push_in_slow", "S03": "push_in", "S04": "tilt_up", "S05": "push_in_slow",
        "S06a": "push_in", "S06b": "push_in", "S07": "shake", "S08a": "push_in", "S08b": "push_in",
        "S09": "push_in_slow", "S10": "pan_left", "S11a": "pan_right", "S11b": "push_in", "S12a": "push_in_slow",
        "S12b": "push_in"}
for sh in shots:
    sh["hero"] = sh["id"] in HERO
    sh["move"] = MOVE.get(sh["id"], "push_in_slow")
by = {s["id"]: s for s in shots}
assert len(shots) == 16, [s["id"] for s in shots]
by["S07"]["keep_clip_audio_db"] = -8  # Veo's own crash sound, under the SFX

# ---- voice lines (Short table) + start times from the subtitle plan
short_tbl = lines_md[lines_md.index("## Short #1"):lines_md.index("## Full Episode 1")]
AT = [0.3, 3.6, 8.8, 11.0, 13.0, 15.6, 18.2, 21.3, 26.6, 28.5, 34.3, 37.6, 41.3, 43.8, 48.3, 51.2, 54.2, 57.8]
SHOT_OF = ["S01", "S02", "S03", "S03", "S03", "S04", "S04", "S05", "S06b", "S06b", "S08a", "S08b",
           "S09", "S09", "S10", "S11a", "S11b", "S12a"]
SPEAKER = {"KK_Kannan": "kannan", "KK_Yashoda": "yashoda", "KK_Subala": "subala", "KK_Shridama": "shridama",
           "KK_Balarama": "balarama", "KK_Narrator": "narrator"}
rows = re.findall(r"^\| (\d+) \| (\d+) \| [^|]+ \| `([^`]+)` \| (.+?) \| `([^`]+)` \|$", short_tbl, re.M)
assert len(rows) == 18, len(rows)
for i, (_, _, voice, text, fname) in enumerate(rows):
    sub = re.sub(r"\[[^\]]*\]\s*", "", text).strip()
    by[SHOT_OF[i]]["lines"].append({"id": fname.rsplit(".", 1)[0], "voice": voice, "speaker": SPEAKER[voice],
                                    "text": text.strip(), "subtitle": sub, "at": AT[i]})

# ---- sound effects, ambience, music
sfx_library = {
    "amb_room": {"prompt": "Inside an ancient Indian village house, quiet morning room tone, birds outside the window, distant cow bells", "seconds": 22},
    "amb_village": {"prompt": "Indian village at sunrise, birds chirping, cow bells, distant river, peaceful", "seconds": 22},
    "anklets_gold": {"prompt": "Small gold anklet bells jingling as a child climbs", "seconds": 2},
    "anklets_silver": {"prompt": "Silver anklets jingling, three slow footsteps on a wooden threshold", "seconds": 2.5},
    "drum_hit": {"prompt": "Single deep dramatic drum hit", "seconds": 1.5},
    "pot_crash": {"prompt": "Clay pot falling and shattering on a mud floor", "seconds": 2},
    "butter_splat": {"prompt": "Soft splat of butter", "seconds": 0.8},
    "monkey": {"prompt": "Langur monkey chattering", "seconds": 2},
    "kids_laugh": {"prompt": "Group of small children laughing", "seconds": 3},
    "bangles": {"prompt": "Glass bangles clinking", "seconds": 1.5},
    "running": {"prompt": "Child running footsteps on a mud floor", "seconds": 2},
    "divine_om": {"prompt": "Low humming om with shimmering temple bells, divine", "seconds": 5},
    "magic_ding": {"prompt": "Quick magical ding", "seconds": 0.8},
    "wood_creak": {"prompt": "Wooden creak and children grunting with effort", "seconds": 2},
}
sfx = [
    {"sfx": "magic_ding", "at": 12.6, "db": -14}, {"sfx": "anklets_gold", "at": 15.4, "db": -14},
    {"sfx": "wood_creak", "at": 17.0, "db": -16}, {"sfx": "kids_laugh", "at": 21.6, "db": -16},
    {"sfx": "butter_splat", "at": 22.4, "db": -12}, {"sfx": "monkey", "at": 23.6, "db": -16},
    {"sfx": "butter_splat", "at": 24.2, "db": -12}, {"sfx": "anklets_silver", "at": 26.0, "db": -8},
    {"sfx": "drum_hit", "at": 28.0, "db": -8}, {"sfx": "pot_crash", "at": 30.8, "db": -8},
    {"sfx": "monkey", "at": 44.6, "db": -14}, {"sfx": "bangles", "at": 47.6, "db": -16},
    {"sfx": "running", "at": 51.0, "db": -14}, {"sfx": "divine_om", "at": 57.0, "db": -12},
]
ambience = [
    {"sfx": "amb_room", "start": 0.0, "end": 3.0, "db": -24},
    {"sfx": "amb_village", "start": 3.0, "end": 8.0, "db": -22},
    {"sfx": "amb_room", "start": 8.0, "end": 57.0, "db": -26},
]
music_library = {
    "T1_title": {"prompt": "Catchy Tamil devotional title theme, instrumental, joyful bansuri flute hook of four notes, mridangam and tabla groove, veena, strings, festive and uplifting, 100 bpm", "seconds": 15},
    "T2_kannan": {"prompt": "Playful mischievous Indian instrumental, cheeky bansuri flute melody with a catchy bouncy hook, pizzicato strings, kanjira and light mridangam, tiptoeing comedic rhythm, 96 bpm, animated family film score", "seconds": 30},
    "T3_yashoda": {"prompt": "Tender warm Indian instrumental, veena melody with soft strings and gentle flute, mother's love, lullaby-like, 68 bpm, emotional cinematic, simple memorable melody", "seconds": 15},
    "T8_divine": {"prompt": "Divine awe-inspiring cinematic instrumental, low choir humming om, temple bells and shimmering chimes, slowly rising strings building to a powerful swell, Indian devotional epic, 60 bpm", "seconds": 15},
    "T9_mystery": {"prompt": "Mysterious ethereal Indian ambient, single temple bell, soft tanpura drone, distant flute note, slow, magical and curious, minimal", "seconds": 15},
}
music = [
    {"track": "T1_title", "start": 3.0, "end": 5.8, "db": -12, "fade_in": 0.1, "fade_out": 0.6},
    {"track": "T2_kannan", "start": 5.2, "end": 26.0, "db": -15, "fade_in": 0.8, "fade_out": 0.05},
    {"track": "T2_kannan", "start": 34.0, "end": 47.0, "db": -24, "fade_in": 0.5, "fade_out": 0.8, "offset": 10.0},
    {"track": "T3_yashoda", "start": 46.6, "end": 51.4, "db": -15, "fade_in": 0.6, "fade_out": 0.6},
    {"track": "T9_mystery", "start": 51.0, "end": 57.2, "db": -18, "fade_in": 0.4, "fade_out": 0.4},
    {"track": "T8_divine", "start": 56.8, "end": 62.0, "db": -12, "fade_in": 0.3, "fade_out": 0.05},
    {"track": "T1_title", "start": 62.2, "end": 65.0, "db": -12, "fade_in": 0.1, "fade_out": 0.8},
]

manifest = {
    "id": "short01", "title": "கண்ணன் கதைகள் #01 | வெண்ணெய் திருடன்",
    "aspect": "9:16", "width": 1080, "height": 1920, "fps": 30, "length": 65.0,
    "refs": refs, "shots": shots, "sfx_library": sfx_library, "sfx": sfx, "ambience": ambience,
    "music_library": music_library, "music": music,
    "titles": [{"text": "கண்ணன் கதைகள் #01", "sub": "வெண்ணெய் திருடன்", "start": 3.5, "end": 5.5}],
    "end_card": {"start": 62.0, "end": 65.0, "lines": ["அடுத்த எபிசோட்:", "வாய்க்குள் ஒரு பிரபஞ்சம்", "Follow பண்ணுங்க"]},
}
out = os.path.join(HERE, "episodes", "short01.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(manifest, f, ensure_ascii=False, indent=2)
print(f"wrote {os.path.relpath(out)}: {len(shots)} shots, {sum(len(s['lines']) for s in shots)} lines, {len(refs)} refs")
