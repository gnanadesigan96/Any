#!/usr/bin/env python3
"""Kannan Kathaigal production pipeline: make a whole Short by script.

    python kk.py status                  # what exists, what's missing
    python kk.py all --yes               # run every step below in order
    python kk.py voices [--auto]         # create the KK_ voices in ElevenLabs if missing
    python kk.py refs   [--takes 2]      # character + background reference pictures (Gemini API)
    python kk.py frames [--takes 2]      # first frame of every shot (Gemini API, uses refs)
    python kk.py clips  --yes            # video clips (Veo via Gemini API, costs money; asks for --yes)
    python kk.py lines                   # all voice lines (ElevenLabs TTS)
    python kk.py revoice                 # lip-sync method A: Veo speech -> isolate -> character voice
    python kk.py sfx                     # sound effects + ambience (ElevenLabs)
    python kk.py music                   # music cues (ElevenLabs Music)
    python kk.py assemble                # final MP4 + SRT with ffmpeg (works at any stage: missing
                                         #   clips become still frames or placeholder cards = animatic)
    python kk.py choose frames S03 2     # promote take 2 of a refs/frames/clips item to the main one
    python kk.py link KK_Kannan <id> [--pitch 3]   # use a Voice Library voice (optionally pitched up)
    python kk.py pitch KK_Kannan 3       # change only the pitch of a linked voice

Common options: --episode short01, --only S03,S08a (ids), --force (redo even if the file exists).
Keys come from environment variables: ELEVENLABS_API_KEY, GEMINI_API_KEY.
Any output can also be made by hand and dropped into work/<episode>/<folder>/ with the same name.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from clients import ApiError, ElevenLabs, Gemini  # noqa: E402

NEG_SHORT = ("photorealistic live action, anime, flat 2D cartoon, distorted or melting faces, extra fingers, extra limbs, "
             "changing costume, changing skin colour, modern objects, text, subtitles, captions, watermark, logo")
REF_HINT = "Use the attached reference images for the characters' exact faces, skin colour, hair, costumes and jewellery, and for the room. "


# ---------------------------------------------------------------- helpers
def log(*a):
    print(*a, flush=True)


class Ctx:
    def __init__(self, args):
        self.args = args
        self.m = json.load(open(os.path.join(HERE, "episodes", f"{args.episode}.json"), encoding="utf-8"))
        self.work = os.path.join(os.environ.get("KK_WORK_ROOT", os.path.join(HERE, "work")), args.episode)
        for d in ("refs", "frames", "clips", "voice", "revoice", "sfx", "music", "out"):
            os.makedirs(os.path.join(self.work, d), exist_ok=True)
        self.only = set(args.only.split(",")) if getattr(args, "only", None) else None
        self._el = self._gm = None

    def p(self, folder, name, ext):
        return os.path.join(self.work, folder, f"{name}.{ext}")

    def want(self, ident, path):
        if self.only and ident not in self.only:
            return False
        return self.args.force or not os.path.exists(path)

    @property
    def el(self):
        if not self._el:
            key = os.environ.get("ELEVENLABS_API_KEY")
            if not key:
                sys.exit("ELEVENLABS_API_KEY is not set.")
            self._el = ElevenLabs(key)
        return self._el

    @property
    def gm(self):
        if not self._gm:
            key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
            if not key:
                sys.exit("GEMINI_API_KEY is not set.")
            self._gm = Gemini(key)
        return self._gm


def write(path, data):
    with open(path, "wb") as f:
        f.write(data)


def take_path(path, n):
    root, ext = os.path.splitext(path)
    return path if n == 1 else f"{root}__t{n}{ext}"


def run(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"command failed: {' '.join(cmd[:6])} ...\n{r.stderr[-2000:]}")
    return r.stderr if quiet else r.stdout


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def has_audio(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index",
                          "-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip()
    return bool(out)


def pitch_shift(path, semitones):
    """Raise pitch in place (asetrate shifts pitch and formants together: younger, brighter voice)."""
    if not semitones:
        return
    r = 2 ** (semitones / 12.0)
    tmp = path + ".tmp" + os.path.splitext(path)[1]
    run(["ffmpeg", "-y", "-hide_banner", "-i", path, "-af",
         f"asetrate=44100*{r:.5f},aresample=44100,atempo={1 / r:.5f}", tmp])
    os.replace(tmp, path)


def speech_regions(path, noise_db=-32, min_sil=0.25):
    """[(start, end)] of non-silent regions, via ffmpeg silencedetect."""
    err = run(["ffmpeg", "-hide_banner", "-i", path, "-af", f"silencedetect=noise={noise_db}dB:d={min_sil}",
               "-f", "null", "-"])
    total = duration(path)
    sil, cur = [], None
    for line in err.splitlines():
        m = re.search(r"silence_start: ([\d.]+)", line)
        if m:
            cur = float(m.group(1))
        m = re.search(r"silence_end: ([\d.]+)", line)
        if m and cur is not None:
            sil.append((cur, float(m.group(1))))
            cur = None
    if cur is not None:
        sil.append((cur, total))
    regions, t = [], 0.0
    for s, e in sil:
        if s - t > 0.08:
            regions.append((t, s))
        t = e
    if total - t > 0.08:
        regions.append((t, total))
    return regions


def group_regions(regions, n):
    """Merge speech regions into n groups by cutting at the n-1 biggest gaps."""
    if n <= 1 or len(regions) <= 1:
        return [(regions[0][0], regions[-1][1])] if regions else []
    gaps = sorted(range(1, len(regions)), key=lambda i: regions[i][0] - regions[i - 1][1], reverse=True)[:n - 1]
    cuts = sorted(gaps)
    groups, start = [], 0
    for c in cuts + [len(regions)]:
        groups.append((regions[start][0], regions[c - 1][1]))
        start = c
    return groups


# ---------------------------------------------------------------- steps
def step_voices(ctx):
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "tools"))
    import create_elevenlabs_voices as cv
    needed = sorted({ln["voice"] for s in ctx.m["shots"] for ln in s["lines"]})
    existing = {v["name"] for v in ctx.el.get_json("/v1/voices").get("voices", [])} | set(ctx.el.linked())
    missing = [n for n in needed if n not in existing]
    if not missing:
        log("voices: all present:", ", ".join(needed))
        return
    specs = {v["name"]: v for v in cv.load_json(cv.VOICES_FILE, [])}
    kids = [n for n in missing if specs[n].get("child")]
    for name in [n for n in missing if not specs[n].get("child")]:
        v = specs[name]
        log(f"voices: designing {name} ({v['character']})")
        try:
            previews = cv.make_previews(ctx.el.key, v)
        except Exception as e:  # keep going with the other voices
            log(f"   {name}: could not design ({e})")
            continue
        paths = cv.write_previews(v, previews)
        if ctx.args.auto:
            vid = cv.save_voice(ctx.el.key, v, previews[0]["generated_voice_id"])
            cv.register(v, vid)
            log(f"   saved preview 1 as {name} ({vid})")
        else:
            log("   previews:", ", ".join(paths))
    if not ctx.args.auto and len(kids) < len(missing):
        log("\nListen, then save your picks, e.g.:\n  python3 ../tools/create_elevenlabs_voices.py save KK_Yashoda=2 KK_Narrator=1\n"
            "or rerun with --auto to keep preview 1 of each.")
    if kids:
        log("\nChild voices can't be made with Voice Design (ElevenLabs blocks designing children's voices).\n"
            "Pick them from the Voice Library instead (see pipeline/README.md, 'Child voices'), then link each one:")
        for n in kids:
            log(f"  python3 kk.py link {n} <voice_id>      # {specs[n]['character']}")


def step_pitch(ctx):
    name, semis = ctx.args.target[0], float(ctx.args.target[1])
    path = os.path.join(HERE, "voice_map.json")
    data = json.load(open(path)) if os.path.exists(path) else {}
    cur = data.get(name)
    if not cur:
        sys.exit(f"{name} isn't linked yet (run boys.py auto / use, or kk.py link).")
    vid = cur["id"] if isinstance(cur, dict) else cur
    data[name] = {"id": vid, "pitch": semis} if semis else vid
    json.dump(data, open(path, "w"), indent=2)
    log(f"{name}: pitch set to {semis:+g} semitones. Regenerate its lines: python3 kk.py lines --only <line ids> --force "
        "(or delete work/short01/voice/ and run lines again)")


def step_link(ctx):
    name, vid = ctx.args.target
    path = os.path.join(HERE, "voice_map.json")
    data = json.load(open(path)) if os.path.exists(path) else {}
    data[name] = {"id": vid, "pitch": ctx.args.pitch} if ctx.args.pitch else vid
    json.dump(data, open(path, "w"), indent=2)
    log(f"linked {name} -> {vid}" + (f" (+{ctx.args.pitch:g} semitones)" if ctx.args.pitch else "") +
        "  (saved in voice_map.json). Re-run 'lines' with --force --only for this voice's lines to apply it.")


def _gen_image(ctx, ident, path, prompt, refs, aspect):
    for n in range(1, ctx.args.takes + 1):
        out = take_path(path, n)
        try:
            write(out, ctx.gm.image(prompt, refs, aspect))
            log(f"   {ident}: {os.path.relpath(out, ctx.work)}")
        except (ApiError, RuntimeError) as e:
            log(f"   {ident}: FAILED take {n}: {e}")


def step_refs(ctx):
    refs = ctx.m["refs"]
    order = [k for k, v in refs.items() if "from" not in v] + [k for k, v in refs.items() if "from" in v]
    for name in order:
        spec, path = refs[name], ctx.p("refs", name, "png")
        if not ctx.want(name, path):
            continue
        src = [ctx.p("refs", spec["from"], "png")] if spec.get("from") else []
        src = [s for s in src if os.path.exists(s)]
        if spec.get("from") and not src:
            log(f"   {name}: skipped (needs {spec['from']} first)")
            continue
        aspect = "9:16" if name.endswith("_full") else ("1:1" if name.endswith("_front") else "16:9")
        _gen_image(ctx, name, path, spec["prompt"], src, aspect)


def step_frames(ctx):
    for s in ctx.m["shots"]:
        path = ctx.p("frames", s["id"], "png")
        if not ctx.want(s["id"], path):
            continue
        refs = [ctx.p("refs", r, "png") for r in s["refs"]]
        missing = [os.path.basename(r) for r in refs if not os.path.exists(r)]
        if missing:
            log(f"   {s['id']}: note, missing refs {missing}; generating without them")
        refs = [r for r in refs if os.path.exists(r)]
        _gen_image(ctx, s["id"], path, (REF_HINT if refs else "") + s["frame_prompt"], refs, ctx.m["aspect"])


def step_clips(ctx):
    todo = [s for s in ctx.m["shots"] if ctx.want(s["id"], ctx.p("clips", s["id"], "mp4"))]
    secs = sum(s["veo_seconds"] for s in todo) * ctx.args.takes
    if not todo:
        log("clips: nothing to do")
        return
    log(f"clips: {len(todo)} clip(s), {secs} s of video with model {ctx.gm.video_model}. "
        "This is billed on your Gemini API account (roughly $0.15-0.40 per second; check Google's pricing page).")
    if not ctx.args.yes:
        log("Re-run with --yes to generate.")
        return
    for s in todo:
        frame = ctx.p("frames", s["id"], "png")
        if not os.path.exists(frame):
            log(f"   {s['id']}: skipped (no first frame yet)")
            continue
        for n in range(1, ctx.args.takes + 1):
            out = take_path(ctx.p("clips", s["id"], "mp4"), n)
            log(f"   {s['id']}: rendering take {n} ({s['veo_seconds']} s)...")
            try:
                write(out, ctx.gm.video(s["video_prompt"], frame, ctx.m["aspect"], s["veo_seconds"], NEG_SHORT, log=log))
                log(f"   {s['id']}: {os.path.relpath(out, ctx.work)}")
            except (ApiError, RuntimeError, TimeoutError) as e:
                log(f"   {s['id']}: FAILED: {e}\n      Tip: make this shot by hand in Flow and save it as clips/{s['id']}.mp4")


def step_lines(ctx):
    for s in ctx.m["shots"]:
        for ln in s["lines"]:
            path = ctx.p("voice", ln["id"], "mp3")
            if ctx.only and ln["id"] not in ctx.only and s["id"] not in ctx.only:
                continue
            if os.path.exists(path) and not ctx.args.force:
                continue
            for n in range(1, ctx.args.takes + 1):
                out = take_path(path, n)
                try:
                    write(out, ctx.el.tts(ln["voice"], ln["text"]))
                    pitch_shift(out, ctx.el.pitch(ln["voice"]))
                    log(f"   {ln['id']}: {os.path.relpath(out, ctx.work)} ({duration(out):.1f} s)")
                except (ApiError, KeyError) as e:
                    log(f"   {ln['id']}: FAILED: {e}")


def step_revoice(ctx):
    """For shots with a clip: isolate Veo's speech. Method A: convert it to the character voices.
    Method B: just record where speech starts, so the TTS lines can be aligned to the mouths."""
    info_path = os.path.join(ctx.work, "revoice", "revoice.json")
    info = json.load(open(info_path)) if os.path.exists(info_path) else {}
    for s in ctx.m["shots"]:
        clip = ctx.p("clips", s["id"], "mp4")
        if s["method"] not in ("A", "B") or not s["lines"] or not os.path.exists(clip):
            continue
        if ctx.only and s["id"] not in ctx.only:
            continue
        if s["id"] in info and not ctx.args.force:
            continue
        if not has_audio(clip):
            log(f"   {s['id']}: clip has no audio; will use TTS lines")
            continue
        raw = ctx.p("revoice", s["id"] + "_raw", "wav")
        iso = ctx.p("revoice", s["id"] + "_iso", "mp3")
        run(["ffmpeg", "-y", "-hide_banner", "-i", clip, "-t", str(s["dur"]), "-vn", "-ac", "1", "-ar", "44100", raw])
        try:
            write(iso, ctx.el.isolate(raw))
        except ApiError as e:
            log(f"   {s['id']}: isolation failed ({e}); using raw audio")
            shutil.copy(raw, iso)
        groups = group_regions(speech_regions(iso), len(s["lines"]))
        entry = {"onsets": [g[0] for g in groups], "lines": {}}
        if s["method"] == "A" and len(groups) == len(s["lines"]):
            for ln, (g0, g1) in zip(s["lines"], groups):
                seg = ctx.p("revoice", ln["id"] + "_seg", "wav")
                run(["ffmpeg", "-y", "-hide_banner", "-i", iso, "-ss", f"{max(0, g0 - 0.05):.3f}",
                     "-to", f"{g1 + 0.1:.3f}", "-ac", "1", "-ar", "44100", seg])
                try:
                    out = ctx.p("revoice", ln["id"] + "_A", "mp3")
                    write(out, ctx.el.voice_change(ln["voice"], seg))
                    pitch_shift(out, ctx.el.pitch(ln["voice"]))
                    entry["lines"][ln["id"]] = {"file": os.path.basename(out), "offset": round(max(0, g0 - 0.05), 3)}
                    log(f"   {ln['id']}: re-voiced at +{g0:.2f} s in {s['id']}")
                except (ApiError, KeyError) as e:
                    log(f"   {ln['id']}: voice change failed ({e}); TTS line will be used")
        elif s["method"] == "A":
            log(f"   {s['id']}: found {len(groups)} speech part(s) for {len(s['lines'])} line(s); "
                "falling back to aligned TTS lines (method B)")
        info[s["id"]] = entry
        json.dump(info, open(info_path, "w"), indent=2)


def step_sfx(ctx):
    for name, spec in ctx.m["sfx_library"].items():
        path = ctx.p("sfx", name, "mp3")
        if ctx.want(name, path):
            try:
                write(path, ctx.el.sound_effect(spec["prompt"], spec["seconds"]))
                log(f"   {name}: ok")
            except ApiError as e:
                log(f"   {name}: FAILED: {e}")


def step_music(ctx):
    for name, spec in ctx.m["music_library"].items():
        path = ctx.p("music", name, "mp3")
        if ctx.want(name, path):
            try:
                write(path, ctx.el.music(spec["prompt"], spec["seconds"]))
                log(f"   {name}: ok ({duration(path):.0f} s)")
            except ApiError as e:
                log(f"   {name}: FAILED: {e}\n      Tip: make it in Gemini's music tool and save it as music/{name}.mp3")


def step_choose(ctx):
    kind, ident, n = ctx.args.target
    ext = {"refs": "png", "frames": "png", "clips": "mp4", "voice": "mp3"}[kind]
    main = ctx.p(kind, ident, ext)
    alt = take_path(main, int(n))
    if not os.path.exists(alt):
        sys.exit(f"No such take: {alt}")
    if os.path.exists(main):
        os.replace(main, take_path(main, 99))
    os.replace(alt, main)
    if os.path.exists(take_path(main, 99)):
        os.replace(take_path(main, 99), alt)
    log(f"{kind}/{ident}: take {n} is now the main file (old main kept as take {n})")
    if kind == "clips":
        info_path = os.path.join(ctx.work, "revoice", "revoice.json")
        if os.path.exists(info_path):
            info = json.load(open(info_path))
            info.pop(ident, None)
            json.dump(info, open(info_path, "w"), indent=2)
            log("  (re-run 'revoice' for this shot)")


def step_status(ctx):
    rows = []
    for name in ctx.m["refs"]:
        rows.append(("ref", name, os.path.exists(ctx.p("refs", name, "png"))))
    for s in ctx.m["shots"]:
        rows.append(("frame", s["id"], os.path.exists(ctx.p("frames", s["id"], "png"))))
        rows.append(("clip", s["id"], os.path.exists(ctx.p("clips", s["id"], "mp4"))))
        for ln in s["lines"]:
            rows.append(("line", ln["id"], os.path.exists(ctx.p("voice", ln["id"], "mp3"))))
    for name in ctx.m["sfx_library"]:
        rows.append(("sfx", name, os.path.exists(ctx.p("sfx", name, "mp3"))))
    for name in ctx.m["music_library"]:
        rows.append(("music", name, os.path.exists(ctx.p("music", name, "mp3"))))
    kinds = {}
    for k, name, ok in rows:
        kinds.setdefault(k, [0, 0, []])
        kinds[k][0] += ok
        kinds[k][1] += 1
        if not ok:
            kinds[k][2].append(name)
    for k, (ok, total, miss) in kinds.items():
        log(f"{k:<6} {ok:>3}/{total:<3} " + ("done" if not miss else "missing: " + ", ".join(miss[:12]) + (" ..." if len(miss) > 12 else "")))
    log(f"work folder: {ctx.work}")


# ---------------------------------------------------------------- assembly
def _ass_time(t):
    t = max(0, t)
    h, rem = divmod(t, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def _srt_time(t):
    ms = int(round(max(0, t) * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_subs(ctx, cues):
    m, W, H = ctx.m, ctx.m["width"], ctx.m["height"]
    font = os.environ.get("KK_FONT", "Noto Sans Tamil")
    title_font = os.environ.get("KK_TITLE_FONT", "Mukta Malar ExtraBold")
    fs, mv = int(H * 0.034), int(H * 0.33)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,{font},{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,70,70,{mv},1
Style: Kannan,{font},{fs},&H0066D9FF,&H0066D9FF,&H00000000,&H64000000,-1,0,0,0,100,100,0,0,1,4,2,2,70,70,{mv},1
Style: Narr,{font},{fs},&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,2,2,70,70,{mv},1
Style: Title,{title_font},{int(H * 0.055)},&H0037AFD4,&H0037AFD4,&H00101010,&H96000000,-1,0,0,0,100,100,0,0,1,5,3,8,40,40,{int(H * 0.2)},1
Style: End,{font},{int(H * 0.036)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev, srt = [], []
    for i, (t0, t1, speaker, text) in enumerate(cues, 1):
        style = {"kannan": "Kannan", "narrator": "Narr"}.get(speaker, "Sub")
        ev.append(f"Dialogue: 0,{_ass_time(t0)},{_ass_time(t1)},{style},,0,0,0,,{text}")
        srt.append(f"{i}\n{_srt_time(t0)} --> {_srt_time(t1)}\n{text}\n")
    for t in m.get("titles", []):
        ev.append(f"Dialogue: 1,{_ass_time(t['start'])},{_ass_time(t['end'])},Title,,0,0,0,,"
                  f"{{\\fad(250,300)}}{t['text']}\\N{{\\fs{int(H * 0.04)}}}{t['sub']}")
    ec = m.get("end_card")
    if ec:
        ev.append(f"Dialogue: 1,{_ass_time(ec['start'])},{_ass_time(ec['end'])},End,,0,0,0,,"
                  "{\\fad(300,300)}" + "\\N\\N".join(ec["lines"]))
    ass = os.path.join(ctx.work, "out", f"{m['id']}.ass")
    with open(ass, "w", encoding="utf-8") as f:
        f.write(head + "\n".join(ev) + "\n")
    with open(os.path.join(ctx.work, "out", f"{m['id']}.srt"), "w", encoding="utf-8") as f:
        f.write("\n".join(srt))
    return ass


def split_long(cues, limit=46):
    """Split long subtitle cues at a '...' or ',' near the middle into two timed cues."""
    out = []
    for t0, t1, spk, text in cues:
        if len(text) <= limit:
            out.append([t0, t1, spk, text])
            continue
        cands = [m.end() for m in re.finditer(r"(\.\.\.|[,?!])\s+", text)]
        if not cands:
            out.append([t0, t1, spk, text])
            continue
        cut = min(cands, key=lambda i: abs(i - len(text) / 2))
        a, b = text[:cut].strip(), text[cut:].strip()
        mid = t0 + (t1 - t0) * len(a) / max(1, len(a) + len(b))
        out += [[t0, mid, spk, a], [mid, t1, spk, b]]
    return out


def step_assemble(ctx):
    m = ctx.m
    W, H, fps, total = m["width"], m["height"], m["fps"], m["length"]
    info_path = os.path.join(ctx.work, "revoice", "revoice.json")
    revoice = json.load(open(info_path)) if os.path.exists(info_path) else {}
    inputs, vf, a_dial, a_mus, a_fx = [], [], [], [], []
    stage = {"clip": 0, "frame": 0, "card": 0}

    def add_input(args):
        inputs.extend(args)
        return sum(1 for x in inputs if x == "-i") - 1

    # ---- video
    for i, s in enumerate(m["shots"]):
        clip, frame = ctx.p("clips", s["id"], "mp4"), ctx.p("frames", s["id"], "png")
        if os.path.exists(clip):
            k = add_input(["-i", clip])
            stage["clip"] += 1
            src = f"[{k}:v]"
            if s.get("keep_clip_audio_db") is not None and has_audio(clip):
                a_fx.append((f"[{k}:a]", 0, s["dur"], s["start"], s["keep_clip_audio_db"], 0, 0))
        elif os.path.exists(frame):
            k = add_input(["-loop", "1", "-framerate", str(fps), "-t", str(s["dur"]), "-i", frame])
            stage["frame"] += 1
            src = f"[{k}:v]"
        else:
            k = add_input(["-f", "lavfi", "-t", str(s["dur"]), "-i", f"color=c=0x1d1a24:s={W}x{H}:r={fps}"])
            stage["card"] += 1
            src = f"[{k}:v]"
            label = s["id"].replace(":", "")
            vf.append(f"{src}drawtext=text='{label}':fontsize={int(H * 0.06)}:fontcolor=white@0.5:"
                      f"x=(w-tw)/2:y=(h-th)/2[card{i}]")
            src = f"[card{i}]"
        vf.append(f"{src}scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={fps},"
                  f"setsar=1,trim=0:{s['dur']},setpts=PTS-STARTPTS[v{i}]")
    last_end = max(s["start"] + s["dur"] for s in m["shots"])
    tail = max(0.1, total - last_end)
    k = add_input(["-f", "lavfi", "-t", f"{tail:.3f}", "-i", f"color=c=black:s={W}x{H}:r={fps}"])
    vf.append(f"[{k}:v]setsar=1,fps={fps}[vend]")
    n = len(m["shots"])
    vf.append("".join(f"[v{i}]" for i in range(n)) + f"[vend]concat=n={n + 1}:v=1:a=0[vcat]")

    # ---- dialogue placement + subtitle cues
    cues = []
    for s in m["shots"]:
        rv = revoice.get(s["id"], {})
        onsets = rv.get("onsets", [])
        for j, ln in enumerate(s["lines"]):
            at, path = ln["at"], ctx.p("voice", ln["id"], "mp3")
            done = rv.get("lines", {}).get(ln["id"])
            if s["method"] == "A" and done:
                path = os.path.join(ctx.work, "revoice", done["file"])
                at = s["start"] + done["offset"]
            elif s["method"] in ("A", "B") and len(onsets) == len(s["lines"]) and abs(s["start"] + onsets[j] - at) < 1.5:
                at = s["start"] + onsets[j]
            d = duration(path) if os.path.exists(path) else max(1.2, len(ln["subtitle"]) / 11)
            if os.path.exists(path):
                k = add_input(["-i", path])
                a_dial.append((f"[{k}:a]", 0, d, at, -1.0, 0, 0))
            cues.append([at, at + d + 0.15, ln["speaker"], ln["subtitle"]])
    cues = split_long(cues)
    cues.sort()
    for a, b in zip(cues, cues[1:]):
        a[1] = max(a[0] + 0.7, min(a[1], b[0] - 0.05))

    # ---- ambience, sfx, music
    for amb in m["ambience"]:
        path = ctx.p("sfx", amb["sfx"], "mp3")
        if os.path.exists(path):
            k = add_input(["-stream_loop", "-1", "-i", path])
            a_fx.append((f"[{k}:a]", 0, amb["end"] - amb["start"], amb["start"], amb["db"], 0.4, 0.4))
    for fx in m["sfx"]:
        path = ctx.p("sfx", fx["sfx"], "mp3")
        if os.path.exists(path):
            k = add_input(["-i", path])
            a_fx.append((f"[{k}:a]", 0, duration(path), fx["at"], fx["db"], 0, 0.05))
    for cue in m["music"]:
        path = ctx.p("music", cue["track"], "mp3")
        if os.path.exists(path):
            k = add_input(["-stream_loop", "-1", "-i", path])
            a_mus.append((f"[{k}:a]", cue.get("offset", 0), cue["end"] - cue["start"], cue["start"], cue["db"],
                          cue.get("fade_in", 0), cue.get("fade_out", 0)))

    af, idx = [], [0]

    def chain(ev):
        src, off, dur, start, db, fin, fout = ev
        idx[0] += 1
        lab = f"[a{idx[0]}]"
        f = (f"{src}atrim={off:.3f}:{off + dur:.3f},asetpts=PTS-STARTPTS,"
             f"aformat=sample_rates=48000:channel_layouts=stereo,volume={db}dB")
        if fin:
            f += f",afade=t=in:d={fin}"
        if fout:
            f += f",afade=t=out:st={max(0, dur - fout):.3f}:d={fout}"
        f += f",adelay={int(start * 1000)}:all=1{lab}"
        af.append(f)
        return lab

    def bus(events, name):
        labs = [chain(e) for e in events]
        if not labs:
            k = add_input(["-f", "lavfi", "-t", str(total), "-i", "anullsrc=r=48000:cl=stereo"])
            af.append(f"[{k}:a]anull[{name}]")
        elif len(labs) == 1:
            af.append(f"{labs[0]}anull[{name}]")
        else:
            af.append(f"{''.join(labs)}amix=inputs={len(labs)}:normalize=0:duration=longest[{name}]")

    bus(a_dial, "dial")
    bus(a_mus, "mus")
    bus(a_fx, "fx")
    af.append("[dial]asplit=2[dmix][dkey]")
    af.append("[mus][dkey]sidechaincompress=threshold=0.02:ratio=6:attack=15:release=350[musd]")
    af.append(f"[dmix][musd][fx]amix=inputs=3:normalize=0:duration=longest,apad=whole_dur={total},"
              f"atrim=0:{total},loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")

    ass = build_subs(ctx, cues)
    fontsdir = os.path.join(HERE, "fonts")
    sub = f"ass='{ass}':shaping=complex" + (f":fontsdir='{fontsdir}'" if os.path.isdir(fontsdir) else "")
    grade = "eq=saturation=1.06:contrast=1.03,noise=alls=3:allf=t+u," if not ctx.args.no_grade else ""
    vf.append(f"[vcat]{grade}{sub},format=yuv420p[vout]")

    graph = os.path.join(ctx.work, "out", "graph.txt")
    with open(graph, "w", encoding="utf-8") as f:
        f.write(";\n".join(vf + af))
    ver = 1
    while os.path.exists(os.path.join(ctx.work, "out", f"{m['id']}_v{ver}.mp4")):
        ver += 1
    out = os.path.join(ctx.work, "out", f"{m['id']}_v{ver}.mp4")
    log(f"assemble: {stage['clip']} clips, {stage['frame']} still frames, {stage['card']} placeholder cards; "
        f"{len(a_dial)} voice files, {len(a_fx)} sfx/ambience, {len(a_mus)} music cues")
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"] + inputs + [
        "-filter_complex", open(graph, encoding="utf-8").read(), "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(fps),
        "-c:a", "aac", "-b:a", "192k", "-t", str(total), "-movflags", "+faststart", out]
    run(cmd)
    log(f"assemble: wrote {os.path.relpath(out, HERE)} ({duration(out):.1f} s) and {m['id']}.srt")
    return out


# ---------------------------------------------------------------- main
STEPS = {"status": step_status, "voices": step_voices, "refs": step_refs, "frames": step_frames,
         "clips": step_clips, "lines": step_lines, "revoice": step_revoice, "sfx": step_sfx,
         "music": step_music, "assemble": step_assemble, "choose": step_choose, "link": step_link, "pitch": step_pitch}
ALL = ["voices", "lines", "sfx", "music", "refs", "frames", "clips", "revoice", "assemble"]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("step", choices=list(STEPS) + ["all"])
    ap.add_argument("target", nargs="*", help="choose: <refs|frames|clips|voice> <id> <take>; link: <KK_Name> <voice_id>")
    ap.add_argument("--episode", default="short01")
    ap.add_argument("--only", help="comma-separated ids (shot ids, line ids, ref names...)")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--takes", type=int, default=1)
    ap.add_argument("--yes", action="store_true", help="allow paid video generation")
    ap.add_argument("--auto", action="store_true", help="voices: keep preview 1 without asking")
    ap.add_argument("--no-grade", action="store_true")
    ap.add_argument("--pitch", type=float, default=0, help="link: raise this voice by N semitones (e.g. 3 for a boy)")
    args = ap.parse_args(argv)
    ctx = Ctx(args)
    if args.step == "choose" and len(args.target) != 3:
        sys.exit("usage: kk.py choose <refs|frames|clips|voice> <id> <take>")
    if args.step == "pitch" and len(args.target) != 2:
        sys.exit("usage: kk.py pitch <KK_Name> <semitones>")
    if args.step == "link" and len(args.target) != 2:
        sys.exit("usage: kk.py link <KK_Name> <voice_id>")
    for step in (ALL if args.step == "all" else [args.step]):
        log(f"== {step} ==")
        STEPS[step](ctx)


if __name__ == "__main__":
    main()
