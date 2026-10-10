"""Stage 4: assemble scenes into the long-form video and the vertical Shorts with ffmpeg."""

import random
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image

from .captions import group_words, write_ass
from .config import resolve
from .util import find_font_file, find_silences, log, media_duration, run_ffmpeg

MOTIONS = ["zoom_in", "pan_right", "zoom_out", "pan_left"]
VIDEO_SUFFIXES = {".mp4", ".mov", ".webm", ".m4v"}


def build_timeline(timing: list, fps: int) -> list:
    """Snap scene boundaries to whole frames so audio and video never drift apart.

    Returns [{start, frames}] where start is in seconds (frame-aligned).
    """
    boundaries, t = [0], 0.0
    for info in timing:
        t += info["duration"]
        boundaries.append(max(round(t * fps), boundaries[-1] + 1))
    return [{"start": boundaries[i] / fps, "frames": boundaries[i + 1] - boundaries[i]}
            for i in range(len(timing))]


def _zoompan(motion: str, frames: int, zoom: float, out_w: int, out_h: int, fps: int) -> str:
    n = max(frames - 1, 1)
    center_x, center_y = "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    if motion == "zoom_in":
        z, x, y = f"1+{zoom}*on/{n}", center_x, center_y
    elif motion == "zoom_out":
        z, x, y = f"1+{zoom}-{zoom}*on/{n}", center_x, center_y
    elif motion == "pan_right":
        z, x, y = f"1+{zoom}", f"(iw-iw/zoom)*on/{n}", center_y
    else:  # pan_left
        z, x, y = f"1+{zoom}", f"(iw-iw/zoom)*(1-on/{n})", center_y
    return f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={out_w}x{out_h}:fps={fps}"


def _media_size(path: Path):
    if path.suffix.lower() in VIDEO_SUFFIXES:
        out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                              "stream=width,height", "-of", "csv=p=0", str(path)],
                             capture_output=True, text=True, check=True)
        w, h = out.stdout.strip().split("\n")[0].split(",")[:2]
        return int(w), int(h)
    with Image.open(path) as im:
        return im.width, im.height


def _render_video_clip(src: Path, frames: int, out: Path, cfg: dict, vertical: bool, enc: list) -> None:
    """Stock video: fill the frame, conform the frame rate, loop if the clip is too short."""
    fps = cfg["video"]["fps"]
    if not vertical:
        w, h = cfg["video"]["width"], cfg["video"]["height"]
        vf = (f"fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
              "setsar=1,format=yuv420p")
        run_ffmpeg(["-stream_loop", "-1", "-i", src, "-vf", vf, *enc])
        return
    w, h = cfg["shorts"]["width"], cfg["shorts"]["height"]
    sw, sh = _media_size(src)
    fg_h = int(w * sh / sw) // 2 * 2
    fc = (f"[0:v]fps={fps},split[a][b];"
          f"[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},boxblur=24:4,eq=brightness=-0.12[bg];"
          f"[b]scale={w}:{fg_h},setsar=1[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2-{int(h * 0.04)},format=yuv420p")
    run_ffmpeg(["-stream_loop", "-1", "-i", src, "-filter_complex", fc, *enc])


def render_scene_clip(image: Path, frames: int, motion: str, out: Path, cfg: dict,
                      vertical: bool = False, index: int = 0, text: str = "") -> None:
    v = cfg["video"]
    fps, zoom = v["fps"], v["zoom"]
    enc = ["-c:v", "libx264", "-preset", v["preset"], "-crf", v["crf"], "-pix_fmt", "yuv420p",
           "-frames:v", frames, "-an", out]
    if image.suffix.lower() in VIDEO_SUFFIXES:
        _render_video_clip(image, frames, out, cfg, vertical, enc)
        return
    if v.get("animation") == "parallax" and not vertical:
        from .animate import render_parallax_clip
        render_parallax_clip(image, frames, index, out, cfg, text)
        return
    if not vertical:
        w, h = v["width"], v["height"]
        # Upscale 2x before zoompan: zoompan rounds to whole pixels, so this keeps motion smooth.
        vf = (f"scale={2 * w}:{2 * h}:force_original_aspect_ratio=increase,crop={2 * w}:{2 * h},"
              + _zoompan(motion, frames, zoom, w, h, fps) + ",format=yuv420p")
        run_ffmpeg(["-i", image, "-vf", vf, *enc])
        return

    # Vertical: blurred full-bleed background + the whole landscape image, moving, in the middle.
    s = cfg["shorts"]
    w, h = s["width"], s["height"]
    iw, ih = _media_size(image)
    fg_h = int(w * ih / iw) // 2 * 2
    fc = (f"[0:v]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"boxblur=24:4,eq=brightness=-0.12,fps={fps}[bg];"
          f"[1:v]scale={2 * w}:{2 * fg_h},"
          + _zoompan(motion, frames, zoom * 0.6, w, fg_h, fps) + "[fg];"
          f"[bg][fg]overlay=(W-w)/2:(H-h)/2-{int(h * 0.04)}:shortest=1,format=yuv420p")
    run_ffmpeg(["-loop", "1", "-framerate", fps, "-i", image, "-i", image,
                "-filter_complex", fc, *enc])


def _scene_wav(mp3: Path, frames: int, fps: int, out: Path) -> None:
    """Decode and pad/trim to exactly the scene's frame-aligned length."""
    run_ffmpeg(["-i", mp3, "-af", f"apad,atrim=0:{frames / fps:.6f}", "-ar", 44100, "-ac", 1, out])


def _concat(paths: list, list_file: Path, out: Path, copy: bool = True) -> None:
    list_file.write_text("".join(f"file '{p.resolve()}'\n" for p in paths))
    args = ["-f", "concat", "-safe", "0", "-i", list_file]
    run_ffmpeg(args + (["-c", "copy"] if copy else []) + [out])


def _pick_music(cfg: dict, seed: str):
    music_dir = resolve(cfg["video"]["music_dir"])
    tracks = sorted(p for p in music_dir.glob("*") if p.suffix.lower() in {".mp3", ".wav", ".m4a", ".ogg"})
    return random.Random(seed).choice(tracks) if tracks else None


def _final_mix(work_dir: Path, video: str, narration: str, ass: str, out: Path, cfg: dict,
               music, duration: float) -> None:
    """Burn captions, mix music under the voice, normalise loudness. Runs inside work_dir so
    the subtitles filter never needs path escaping."""
    v = cfg["video"]
    args = ["-i", video, "-i", narration]
    vf = f"[0:v]subtitles=filename={ass}:fontsdir={Path(find_font_file(v['caption_font'])).parent}[v]" \
        if ass else "[0:v]null[v]"
    loud = f"loudnorm=I={v['loudness_lufs']}:TP=-1.5:LRA=11"
    if music:
        args += ["-stream_loop", "-1", "-i", music]
        fade_start = max(duration - 3, 0)
        af = (f"[2:a]aformat=sample_rates=44100:channel_layouts=mono,volume={v['music_volume']},"
              f"afade=t=in:d=2,afade=t=out:st={fade_start:.2f}:d=3[m];"
              f"[1:a][m]amix=inputs=2:duration=first:normalize=0,{loud}[a]")
    else:
        af = f"[1:a]{loud}[a]"
    run_ffmpeg([*args, "-filter_complex", f"{vf};{af}", "-map", "[v]", "-map", "[a]",
                "-c:v", "libx264", "-preset", v["preset"], "-crf", v["crf"], "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-ar", 44100, "-t", f"{duration:.3f}",
                "-movflags", "+faststart", out], cwd=work_dir)


def _absolute_words(timing: list, timeline: list, scene_ids, offset: float, fps: int) -> list:
    """Scene-relative word times -> times on the assembled video, clamped to each scene."""
    words = []
    for i in scene_ids:
        base = timeline[i]["start"] - offset
        limit = base + timeline[i]["frames"] / fps
        words += [[w, min(base + s, limit), min(base + e, limit)] for w, s, e in timing[i]["words"]]
    return words


def render_main(run_dir: Path, image_paths: list, timing: list, cfg: dict, title: str = "",
                scene_texts: list = None) -> Path:
    v = cfg["video"]
    fps = v["fps"]
    work = run_dir / "work"
    work.mkdir(exist_ok=True)
    timeline = build_timeline(timing, fps)
    final = run_dir / "video.mp4"

    clips = [work / f"clip_{i:03d}.mp4" for i in range(len(timing))]
    wavs = [work / f"scene_{i:03d}.wav" for i in range(len(timing))]

    def work_scene(i):
        if not clips[i].exists():
            text = scene_texts[i] if scene_texts else timing[i].get("text", "")
            render_scene_clip(image_paths[i], timeline[i]["frames"], MOTIONS[i % len(MOTIONS)], clips[i], cfg,
                              index=i, text=text)
        if not wavs[i].exists():
            _scene_wav(run_dir / "audio" / timing[i]["audio"], timeline[i]["frames"], fps, wavs[i])

    log(f"Rendering {len(timing)} scene clips...")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(work_scene, range(len(timing))))

    _concat(clips, work / "clips.txt", work / "video_noaudio.mp4")
    _concat(wavs, work / "wavs.txt", work / "narration.wav", copy=False)
    duration = sum(t["frames"] for t in timeline) / fps

    ass = ""
    if v["captions"]:
        words = _absolute_words(timing, timeline, range(len(timing)), 0.0, fps)
        write_ass(group_words(words, v["caption_max_words"]), work / "captions.ass",
                  v["width"], v["height"], v["caption_font"], vertical=v["height"] > v["width"],
                  title=title, duration=sum(t["frames"] for t in timeline) / fps)
        ass = "captions.ass"
    log("Mixing final video...")
    _final_mix(work, "video_noaudio.mp4", "narration.wav", ass, final.resolve(), cfg,
               _pick_music(cfg, run_dir.name), duration)
    return final


def render_shorts(run_dir: Path, image_paths: list, timing: list, shorts: list, cfg: dict) -> list:
    v, fps = cfg["video"], cfg["video"]["fps"]
    work = run_dir / "work"
    timeline = build_timeline(timing, fps)
    outputs = []
    for k, short in enumerate(shorts):
        out = run_dir / f"short_{k + 1}.mp4"
        outputs.append(out)
        if out.exists():
            continue
        ids = list(range(short.start_scene, short.end_scene + 1))
        log(f"Rendering Short {k + 1} (scenes {ids[0]}-{ids[-1]})...")
        clips = []
        for i in ids:
            clip = work / f"vclip_{i:03d}.mp4"
            if not clip.exists():
                render_scene_clip(image_paths[i], timeline[i]["frames"], MOTIONS[i % len(MOTIONS)],
                                  clip, cfg, vertical=True)
            clips.append(clip)
        tag = f"short{k + 1}"
        _concat(clips, work / f"{tag}_clips.txt", work / f"{tag}_noaudio.mp4")
        _concat([work / f"scene_{i:03d}.wav" for i in ids], work / f"{tag}_wavs.txt",
                 work / f"{tag}_narration.wav", copy=False)
        duration = sum(timeline[i]["frames"] for i in ids) / fps
        words = _absolute_words(timing, timeline, ids, timeline[ids[0]]["start"], fps)
        s = cfg["shorts"]
        write_ass(group_words(words, max(3, v["caption_max_words"] - 2)), work / f"{tag}.ass",
                  s["width"], s["height"], v["caption_font"], vertical=True,
                  title=short.hook_title, duration=duration)
        _final_mix(work, f"{tag}_noaudio.mp4", f"{tag}_narration.wav", f"{tag}.ass", out.resolve(), cfg,
                   _pick_music(cfg, run_dir.name + tag), duration)
        if duration > 180:
            log(f"Warning: Short {k + 1} is {duration:.0f}s; YouTube Shorts must be 3 minutes or less")
    return outputs


def check_output(path: Path, check_silence: bool = True) -> float:
    d = media_duration(path)
    log(f"Wrote {path.name} ({d:.1f}s)")
    for start, length in (find_silences(path) if check_silence else []):
        log(f"  Warning: {length:.1f}s of silence at {int(start // 60)}:{start % 60:04.1f} in {path.name}")
    return d
