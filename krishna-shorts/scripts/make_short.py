"""Assemble a 60 s vertical Short from story.json + images/clips + ElevenLabs voice.

Episode folder:
    story.json        scenes (narration + image prompt + motion)
    voice.mp3         from make_voice.py
    alignment.json    from make_voice.py
    images/scene01.png|jpg|mp4 ...   one per scene; an .mp4 (image-to-video clip) wins
                                     over a still. Missing ones get a labelled placeholder.
    music.mp3         optional background score (auto-ducked under the voice)

Each scene is on screen exactly while its narration is spoken. Stills get a slow
Ken Burns move; captions are word-by-word with the spoken word highlighted.

Usage:
    python3 scripts/make_short.py episodes/01-govardhan        # -> <episode>/short.mp4
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap

W, H, FPS = 1080, 1920, 30
LEAD = 0.4          # silence before the first word
TAIL = 1.6          # hold after the last word
XFADE = 0.5         # crossfade between scenes
ZOOM = 0.12         # Ken Burns strength
CAPTION_FONT = os.environ.get("CAPTION_FONT", "Inter")
TITLE_SECS = 2.8


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n{r.stderr[-3000:]}")


def media_duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout
    return float(out.strip())


# ---------- timings ----------

def words_with_times(alignment):
    """Group ElevenLabs character timings into words: [(word, start, end, char_index)]."""
    chars = alignment["characters"]
    st = alignment["character_start_times_seconds"]
    en = alignment["character_end_times_seconds"]
    words, cur = [], None
    for i, c in enumerate(chars):
        if c.isspace():
            if cur:
                words.append(cur)
                cur = None
            continue
        if cur is None:
            cur = [c, st[i], en[i], i]
        else:
            cur[0] += c
            cur[2] = en[i]
    if cur:
        words.append(cur)
    return [tuple(w) for w in words]


def scene_bounds(story, alignment, total):
    """Scene i runs from its first spoken character to the next scene's first character."""
    st = alignment["character_start_times_seconds"]
    starts, pos = [], 0
    for s in story["scenes"]:
        starts.append(st[min(pos, len(st) - 1)] + LEAD)
        pos += len(s["narration"].strip()) + 1   # +1 for the joining space
    starts[0] = 0.0
    return [(starts[i], starts[i + 1] if i + 1 < len(starts) else total)
            for i in range(len(starts))]


# ---------- visuals ----------

def find_media(ep, i):
    for ext in ("mp4", "mov", "webm", "png", "jpg", "jpeg", "webp"):
        p = os.path.join(ep, "images", f"scene{i:02d}.{ext}")
        if os.path.exists(p):
            return p
    return None


def placeholder(path, i, prompt):
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(H):  # dusk-blue to saffron gradient
        t = y / H
        d.line([(0, y), (W, y)], fill=(int(20 + 200 * t), int(30 + 100 * t), int(90 - 40 * t)))
    try:
        big = ImageFont.truetype("DejaVuSans-Bold.ttf", 120)
        small = ImageFont.truetype("DejaVuSans.ttf", 40)
    except OSError:
        big = small = ImageFont.load_default()
    d.text((80, 300), f"SCENE {i}", font=big, fill="white")
    d.multiline_text((80, 520), "\n".join(textwrap.wrap(prompt, 38)[:18]), font=small,
                     fill=(255, 255, 255), spacing=14)
    img.save(path)


def motion_filter(motion, frames):
    n = max(frames - 1, 1)
    cx, cy = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    z_in, z_out, z_hold = f"1+{ZOOM}*on/{n}", f"{1 + ZOOM}-{ZOOM}*on/{n}", f"{1 + ZOOM}"
    m = {
        "zoom_in": (z_in, cx, cy),
        "zoom_out": (z_out, cx, cy),
        "pan_left": (z_hold, f"(iw-iw/zoom)*(1-on/{n})", cy),
        "pan_right": (z_hold, f"(iw-iw/zoom)*on/{n}", cy),
        "pan_up": (z_hold, cx, f"(ih-ih/zoom)*(1-on/{n})"),
        "pan_down": (z_hold, cx, f"(ih-ih/zoom)*on/{n}"),
    }.get(motion, (z_in, cx, cy))
    return f"zoompan=z='{m[0]}':x='{m[1]}':y='{m[2]}':d={frames}:s={W}x{H}:fps={FPS}"


LOOK = "eq=saturation=1.12:contrast=1.04,vignette=PI/5,format=yuv420p"


def render_scene(src, dur, motion, out):
    frames = round(dur * FPS)
    cover = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
    if src.lower().endswith((".mp4", ".mov", ".webm")):
        # animated clip: loop if shorter than the scene, gently retime if much shorter
        clip = media_duration(src)
        speed = max(0.6, min(1.0, clip / dur)) if clip < dur else 1.0
        vf = f"{cover},setpts=PTS/{speed},fps={FPS},{LOOK}"
        cmd = ["ffmpeg", "-y", "-stream_loop", "-1", "-i", src, "-an", "-t", f"{dur:.3f}"]
    else:
        # still: upscale 2x first so the zoom is smooth, not jittery
        vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,"
              f"crop={W * 2}:{H * 2},{motion_filter(motion, frames)},{LOOK}")
        cmd = ["ffmpeg", "-y", "-loop", "1", "-i", src, "-frames:v", str(frames)]
    run(cmd + ["-vf", vf, "-r", str(FPS), "-c:v", "libx264", "-preset", "medium",
               "-crf", "16", "-pix_fmt", "yuv420p", out])


# ---------- captions ----------

def ass_time(t):
    t = max(t, 0)
    return f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:05.2f}"


def esc(s):
    return s.replace("\\", "\\\\").replace("{", "(").replace("}", ")")


def build_ass(story, words, total, path):
    hi = "&H0033CCFF&"  # saffron-gold (ASS colours are &HBBGGRR)
    font = story.get("caption_font", CAPTION_FONT)
    lines = [
        "[Script Info]", "ScriptType: v4.00+", f"PlayResX: {W}", f"PlayResY: {H}",
        "WrapStyle: 0", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, "
        "BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, "
        "BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        # captions sit above the Shorts UI (bottom ~350 px is covered by title/buttons)
        f"Style: Cap,{font},84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,"
        "1,7,3,2,110,170,560,1",
        f"Style: Title,{font},78,&H00FFFFFF,&H00FFFFFF,&H00301040,&H96000000,1,0,0,0,100,100,0,0,"
        "1,6,2,8,90,90,230,1",
        "", "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    title = story.get("on_screen_title", story.get("title", ""))
    if title:
        lines.append(f"Dialogue: 1,{ass_time(0)},{ass_time(TITLE_SECS)},Title,,0,0,0,,"
                     f"{{\\fad(250,400)}}{esc(title)}")

    # chunks of up to 3 words, broken early at punctuation
    chunks, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) == 3 or w[0][-1] in ".,!?;:'\"—":
            chunks.append(cur)
            cur = []
    if cur:
        chunks.append(cur)
    for ci, ch in enumerate(chunks):
        chunk_end = (chunks[ci + 1][0][1] if ci + 1 < len(chunks) else ch[-1][2] + 0.6) + LEAD
        for wi, w in enumerate(ch):
            start = w[1] + LEAD
            end = (ch[wi + 1][1] + LEAD) if wi + 1 < len(ch) else chunk_end
            text = " ".join((f"{{\\c{hi}}}{esc(x[0])}{{\\c&H00FFFFFF&}}" if j == wi
                             else esc(x[0])) for j, x in enumerate(ch))
            pop = "{\\fscx108\\fscy108\\t(0,90,\\fscx100\\fscy100)}" if wi == 0 else ""
            lines.append(f"Dialogue: 0,{ass_time(start)},{ass_time(end)},Cap,,0,0,0,,{pop}{text}")

    outro = story.get("outro_text")
    if outro:
        lines.append(f"Dialogue: 1,{ass_time(total - TAIL)},{ass_time(total)},Title,,0,0,0,,"
                     f"{{\\fad(300,0)}}{esc(outro)}")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------- main ----------

def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    ep = sys.argv[1].rstrip("/")
    with open(os.path.join(ep, "story.json"), encoding="utf-8") as f:
        story = json.load(f)
    with open(os.path.join(ep, "alignment.json"), encoding="utf-8") as f:
        alignment = json.load(f)
    voice = os.path.join(ep, "voice.mp3")
    total = LEAD + media_duration(voice) + TAIL
    bounds = scene_bounds(story, alignment, total)
    words = words_with_times(alignment)
    tmp = tempfile.mkdtemp(prefix="short_")

    clips = []
    for i, (scene, (a, b)) in enumerate(zip(story["scenes"], bounds), start=1):
        src = find_media(ep, i)
        if not src:
            src = os.path.join(tmp, f"ph{i:02d}.png")
            placeholder(src, i, scene.get("image_prompt", ""))
            print(f"scene {i}: no images/scene{i:02d}.* yet -> placeholder")
        # every clip after the first starts XFADE early, so the crossfade is finished by
        # the time its first word is spoken
        dur = (b - a) + (XFADE if i > 1 else 0)
        out = os.path.join(tmp, f"c{i:02d}.mp4")
        render_scene(src, dur, scene.get("motion", "zoom_in"), out)
        clips.append((out, a))
        print(f"scene {i}: {a:5.2f}-{b:5.2f}s  {os.path.basename(src)}")

    ass = os.path.join(tmp, "captions.ass")
    build_ass(story, words, total, ass)

    cmd = ["ffmpeg", "-y"]
    for c, _ in clips:
        cmd += ["-i", c]
    cmd += ["-i", voice]
    music = os.path.join(ep, "music.mp3")
    has_music = os.path.exists(music)
    if has_music:
        cmd += ["-stream_loop", "-1", "-i", music]

    n = len(clips)
    fc, last = [], "[0:v]"
    for k in range(1, n):
        lbl = f"[x{k}]"
        fc.append(f"{last}[{k}:v]xfade=transition=fade:duration={XFADE}:offset={clips[k][1] - XFADE:.3f}{lbl}")
        last = lbl
    ass_arg = ass.replace("\\", "/").replace(":", "\\:")
    fc.append(f"{last}ass='{ass_arg}',fade=t=out:st={total - 0.6:.3f}:d=0.6[v]")

    v = n  # voice input index
    fc.append(f"[{v}:a]adelay={int(LEAD * 1000)}:all=1,apad,atrim=0:{total:.3f},"
              "aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[vo][sc]")
    if has_music:
        fc.append(f"[{v + 1}:a]atrim=0:{total:.3f},volume=0.22,"
                  "aformat=sample_rates=48000:channel_layouts=stereo[mu]")
        fc.append("[mu][sc]sidechaincompress=threshold=0.03:ratio=8:attack=20:release=400[duck]")
        fc.append("[vo][duck]amix=inputs=2:duration=first:normalize=0[mix]")
    else:
        fc.append("[sc]anullsink")
        fc.append("[vo]anull[mix]")
    fc.append(f"[mix]loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={total - 1.2:.3f}:d=1.2[a]")

    out = os.path.join(ep, "short.mp4")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[v]", "-map", "[a]",
            "-t", f"{total:.3f}", "-r", str(FPS),
            "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", out]
    run(cmd)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n-> {out}  ({total:.1f} s, {W}x{H})")
    if total > 60:
        print("WARNING: longer than 60 s; trim the narration.")


if __name__ == "__main__":
    main()
