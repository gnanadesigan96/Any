"""Renders the picture: Ken Burns stills, video clips, title cards and the final cut."""
import subprocess
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from . import fonts

MOOD_TINT = {
    "calm": ((10, 38, 48), (24, 92, 96)), "night": ((6, 10, 32), (28, 34, 86)),
    "sad": ((18, 22, 34), (60, 68, 92)), "tension": ((26, 6, 8), (96, 24, 22)),
    "storm": ((12, 10, 22), (62, 54, 84)), "divine": ((40, 22, 4), (170, 112, 30)),
    "celebration": ((48, 16, 6), (196, 92, 24)),
}
GOLD, CREAM = (255, 211, 110), (247, 235, 211)


# ------------------------------------------------------------------ text ---
def font(name, size):
    return ImageFont.truetype(fonts.path(name), int(size), layout_engine=ImageFont.Layout.RAQM)


def wrap(text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if fnt.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_font(name, text, size, max_w):
    f = font(name, size)
    while f.getlength(text) > max_w and size > 20:
        size *= 0.93
        f = font(name, size)
    return f


def glow_text(img, xy, text, fnt, fill, glow=(255, 140, 20), radius=18, anchor="mm", stroke=0):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, text, font=fnt, fill=glow + (255,), anchor=anchor, stroke_width=max(stroke, 4))
    layer = layer.filter(ImageFilter.GaussianBlur(radius))
    img.alpha_composite(layer)
    img.alpha_composite(layer)
    d = ImageDraw.Draw(img)
    d.text(xy, text, font=fnt, fill=fill + (255,), anchor=anchor,
           stroke_width=stroke, stroke_fill=(30, 12, 0, 255))


# ----------------------------------------------------------- backgrounds ---
def gradient(size, top, bottom, glow=None, seed=0, stars=False):
    w, h = size
    y = np.linspace(0, 1, h)[:, None, None]
    arr = np.array(top)[None, None, :] * (1 - y) + np.array(bottom)[None, None, :] * y
    arr = np.repeat(arr, w, axis=1)
    if glow:
        yy, xx = np.mgrid[0:h, 0:w]
        r = np.sqrt(((xx - w / 2) / (0.45 * w)) ** 2 + ((yy - h * 0.45) / (0.45 * h)) ** 2)
        arr += np.array(glow)[None, None, :] * np.exp(-r ** 2 * 2.2)[:, :, None]
    if stars:
        rng = np.random.default_rng(seed)
        for _ in range(int(w * h / 9000)):
            x, yv = rng.integers(0, w), rng.integers(0, int(h * 0.7))
            arr[yv, x] += rng.uniform(60, 200)
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB").convert("RGBA")


def cover(img, size):
    return ImageOps.fit(img.convert("RGB"), size, Image.LANCZOS, centering=(0.5, 0.45)).convert("RGBA")


def ornament(img, cy, width, scale):
    d = ImageDraw.Draw(img)
    cx = img.width / 2
    half = width / 2
    lw = max(2, int(3 * scale))
    d.line([(cx - half, cy), (cx - 26 * scale, cy)], fill=GOLD + (220,), width=lw)
    d.line([(cx + 26 * scale, cy), (cx + half, cy)], fill=GOLD + (220,), width=lw)
    r = 12 * scale
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=GOLD + (255,))


def card_image(sc, ep, size):
    w, h = size
    s = h / 1080
    if sc.image:
        bg = cover(Image.open(sc.image), size).filter(ImageFilter.GaussianBlur(8 * s))
        bg = Image.blend(bg, Image.new("RGBA", size, (0, 0, 0, 255)), 0.55)
    else:
        bg = gradient(size, (8, 10, 34), (44, 16, 64), glow=(150, 90, 20), seed=hash(sc.key) % 99, stars=True)
    title = sc.card.get("title", "")
    sub = sc.card.get("subtitle", "")
    lines = sc.card.get("lines", []) or []
    y = h * (0.40 if not lines else 0.30)
    if title:
        f = fit_font("NotoSerifTamil-Bold.ttf", title, 128 * s, w * 0.84)
        glow_text(bg, (w / 2, y), title, f, GOLD, radius=int(22 * s))
        ornament(bg, y - 120 * s, w * 0.42, s)
        ornament(bg, y + 105 * s, w * 0.42, s)
    if sub:
        f = fit_font("NotoSansTamil-Medium.ttf", sub, 54 * s, w * 0.86)
        glow_text(bg, (w / 2, y + 190 * s), sub, f, CREAM, glow=(0, 0, 0), radius=int(10 * s))
    yy = y + (300 if sub else 200) * s
    for line in lines:
        f = fit_font("NotoSansTamil-Bold.ttf", line, 58 * s, w * 0.86)
        glow_text(bg, (w / 2, yy), line, f, CREAM, glow=(200, 90, 10), radius=int(12 * s))
        yy += 92 * s
    return bg.convert("RGB")


def placeholder_image(sc, size):
    w, h = size
    s = h / 1080
    top, bottom = MOOD_TINT.get(sc.music, MOOD_TINT["calm"])
    img = gradient(size, top, bottom, glow=(40, 40, 40))
    d = ImageDraw.Draw(img)
    big = font("Catamaran-ExtraBold.ttf", 120 * s)
    d.text((w / 2, h * 0.24), f"காட்சி {sc.key}", font=big, fill=GOLD, anchor="mm")
    small = font("Catamaran-SemiBold.ttf", 40 * s)
    tag = "AI VIDEO CLIP: clips/" if sc.video_clip else "IMAGE: images/"
    d.text((w / 2, h * 0.36), f"PLACEHOLDER · add {tag}{sc.key}.jpg" if not sc.video_clip
           else f"PLACEHOLDER · add {tag}{sc.key}.mp4 (or images/{sc.key}.jpg)",
           font=small, fill=CREAM, anchor="mm")
    if sc.prompt:
        pf = font("Catamaran-SemiBold.ttf", 30 * s)
        yy = h * 0.46
        for line in wrap(sc.prompt, pf, w * 0.8)[:8]:
            d.text((w / 2, yy), line, font=pf, fill=(225, 225, 225), anchor="mm")
            yy += 42 * s
    return img.convert("RGB")


# -------------------------------------------------------------- segments ---
def _ease(p):
    return 0.5 - 0.5 * np.cos(np.pi * p)


def _window(motion, p, K):
    if motion == "zoom_out":
        return K - (K - 1) * p, 0.5, 0.5
    if motion == "pan_left":
        return K, 1 - p, 0.5
    if motion == "pan_right":
        return K, p, 0.5
    if motion == "pan_up":
        return K, 0.5, 1 - p
    if motion == "pan_down":
        return K, 0.5, p
    if motion == "zoom_in_top":
        return 1 + (K - 1) * p, 0.5, 0.2
    if motion == "static":
        return 1 + (K - 1) * 0.15, 0.5, 0.5
    return 1 + (K - 1) * p, 0.5, 0.5  # zoom_in


def _encode_args(out, w, h, fps, crf):
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-r", str(fps), str(out)]


def render_still(job):
    src, out, seconds, motion, zoom, w, h, fps, crf = job
    K = 1 + zoom
    img = Image.open(src).convert("RGB")
    SW, SH = img.size
    frames = max(1, int(round(seconds * fps)))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(fps), "-i", "-"] + _encode_args(out, w, h, fps, crf)
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(frames):
        p = _ease(i / max(1, frames - 1))
        z, fx, fy = _window(motion, p, K)
        ww, wh = SW / z, SH / z
        x0, y0 = (SW - ww) * fx, (SH - wh) * fy
        a, e = ww / w, wh / h
        frame = img.transform((w, h), Image.AFFINE, (a, 0, x0 + 0.5 * a - 0.5, 0, e, y0 + 0.5 * e - 0.5),
                              resample=Image.BICUBIC)
        proc.stdin.write(frame.tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg failed for {out}")
    return out


def render_clip(job):
    src, out, seconds, w, h, fps, crf = job
    vf = f"scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},fps={fps},format=yuv420p"
    cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", str(src), "-t", f"{seconds:.3f}",
           "-vf", vf, "-an"] + _encode_args(out, w, h, fps, crf)
    subprocess.run(cmd, check=True)
    return out


def prepare_stills(ep, size, zoom):
    """Create the high-res source picture for every non-clip segment."""
    w, h = size
    stills = ep.build / "stills"
    stills.mkdir(parents=True, exist_ok=True)
    out = {}
    for sc in ep.scenes:
        if sc.kind == "scene" and sc.clip:
            continue
        K = 1 + (sc.zoom if sc.zoom is not None else zoom)
        big = (int(w * K), int(h * K))
        if sc.kind == "card":
            img = card_image(sc, ep, big)
        elif sc.image:
            img = cover(Image.open(sc.image), big).convert("RGB")
        else:
            img = placeholder_image(sc, big)
        p = stills / f"{sc.key}.png"
        img.save(p)
        out[sc.key] = p
    return out


def render_segments(ep, size, fps, crf, workers):
    w, h = size
    X = float(ep.cfg["transition_seconds"])
    zoom = float(ep.cfg["zoom"])
    stills = prepare_stills(ep, size, zoom)
    seg_dir = ep.build / "segments"
    seg_dir.mkdir(parents=True, exist_ok=True)
    jobs_still, jobs_clip, segs = [], [], []
    last = len(ep.scenes) - 1
    for i, sc in enumerate(ep.scenes):
        length = sc.duration + (X / 2 if i > 0 else 0) + (X / 2 if i < last else 0)
        out = seg_dir / f"{i:02d}_{sc.key}.mp4"
        segs.append(out)
        if sc.kind == "scene" and sc.clip:
            jobs_clip.append((sc.clip, out, length, w, h, fps, crf))
        else:
            z = sc.zoom if sc.zoom is not None else zoom
            motion = sc.motion if sc.kind == "scene" else "zoom_in"
            jobs_still.append((stills[sc.key], out, length, motion, z if sc.kind == "scene" else 0.05,
                               w, h, fps, crf))
    with ProcessPoolExecutor(max_workers=workers) as pool:
        list(pool.map(render_still, jobs_still))
        list(pool.map(render_clip, jobs_clip))
    return segs


def assemble(ep, segs, audio_wav, ass_file, out, fps, crf, preset="medium"):
    X = float(ep.cfg["transition_seconds"])
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for s in segs:
        cmd += ["-i", str(s)]
    cmd += ["-i", str(audio_wav)]
    parts = [f"[{i}:v]settb=AVTB,fps={fps},format=yuv420p[v{i}]" for i in range(len(segs))]
    prev = "v0"
    for i in range(1, len(segs)):
        sc = ep.scenes[i]
        offset = sc.start - X / 2
        tr = sc.transition if sc.transition else "fade"
        parts.append(f"[{prev}][v{i}]xfade=transition={tr}:duration={X}:offset={offset:.3f}[x{i}]")
        prev = f"x{i}"
    if ass_file:
        # complex shaping is required for Tamil vowel signs (libass "auto" picks simple here)
        parts.append(f"[{prev}]ass={Path(ass_file).name}:fontsdir={fonts.FONT_DIR}:shaping=complex[vout]")
    else:
        parts.append(f"[{prev}]null[vout]")
    parts.append(f"[{len(segs)}:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000[aout]")
    cmd += ["-filter_complex", ";".join(parts), "-map", "[vout]", "-map", "[aout]",
            "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{ep.total:.3f}", str(out)]
    subprocess.run(cmd, check=True, cwd=Path(ass_file).parent if ass_file else None)
    return out


# -------------------------------------------------------------- extras -----
def thumbnail(ep, out, title, size=(1280, 720)):
    w, h = size
    src = None
    for key in ("thumbnail",) + tuple(sc.key for sc in ep.scenes):
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            p = ep.folder / "images" / f"{key}{ext}"
            if p.exists():
                src = p
                break
        if src:
            break
    img = cover(Image.open(src), size) if src else gradient(size, (8, 10, 34), (44, 16, 64), glow=(150, 90, 20))
    shade = gradient(size, (0, 0, 0), (0, 0, 0))
    mask = Image.fromarray((np.linspace(0, 200, h)[:, None] * np.ones((1, w))).astype(np.uint8), "L")
    img.paste(shade, (0, 0), mask)
    lines = title.split("\n")
    s = h / 720
    y = h - 60 * s - (len(lines) - 1) * 110 * s
    for line in lines:
        f = fit_font("Catamaran-ExtraBold.ttf", line, 120 * s, w * 0.92)
        glow_text(img, (w / 2, y), line, f, GOLD, glow=(220, 60, 0), radius=int(16 * s), anchor="ms",
                  stroke=int(6 * s))
        y += 115 * s
    img.convert("RGB").save(out, quality=92)
    return out


def make_short(src_video, start, end, title, out, fps=30):
    """Vertical 9:16 cut: blurred fill behind the 16:9 frame, title on top."""
    w, h = 1080, 1920
    title_png = Path(out).with_suffix(".title.png")
    img = Image.new("RGBA", (w, 420), (0, 0, 0, 0))
    y = 150
    for line in title.split("\n"):
        f = fit_font("Catamaran-ExtraBold.ttf", line, 96, w * 0.9)
        glow_text(img, (w / 2, y), line, f, GOLD, glow=(220, 60, 0), radius=14, stroke=5)
        y += 115
    img.save(title_png)
    dur = end - start
    fc = (f"[0:v]split[a][b];[a]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
          f"boxblur=30:3,eq=brightness=-0.12[bg];[b]scale={w}:-2[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[m];"
          f"[m][1:v]overlay=0:0,fps={fps},format=yuv420p[v];"
          f"[0:a]afade=t=in:d=0.3,afade=t=out:st={max(0, dur - 1.2):.2f}:d=1.2[a]")
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", str(src_video),
           "-i", str(title_png), "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k",
           "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    title_png.unlink(missing_ok=True)
    return out
