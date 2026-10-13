#!/usr/bin/env python3
"""Turn a still devotional image + a song into an animated, audio-reactive music video.

Effects: cinematic camera path (push-ins / pans across the scene), breathing clouds,
pulsing divine light beam and god-rays, glowing third-eye aura, flickering lamps,
drifting mist, rising embers and golden sparkles, beat-synced glow, title cards.

Usage: python3 make_video.py IMAGE AUDIO OUTPUT.mp4 [--fps 30] [--workers 4] [--preview SECONDS]
"""
import argparse
import os
import subprocess
import sys
import tempfile
from multiprocessing import Pool

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_W, OUT_H = 1920, 1080
SRC_W, SRC_H = 1672, 941  # coordinates below are authored in source-image pixels
BASE_SCALE = 1.75          # work at an upscaled base so zoomed shots stay sharp

# Scene landmarks (source pixels)
THIRD_EYE = (765, 118)
FACE = (745, 210)
BEAM_X = 912
BEAM_BOTTOM = 395
PEAK = (918, 395)

# Camera keyframes: (time s, centre x, centre y, zoom) in source pixels; zoom 1 = full frame
CAMERA = [
    (0.0, 836, 470, 1.05),
    (12.0, 850, 470, 1.13),
    (28.0, 765, 235, 1.60),   # rise to the face
    (44.0, 820, 260, 1.45),
    (58.0, 905, 390, 1.55),   # the burning peak / beam
    (74.0, 900, 630, 1.60),   # temple gopurams
    (90.0, 560, 760, 1.55),   # devotees and lamps
    (106.0, 1390, 650, 1.55),  # Nandi
    (120.0, 900, 420, 1.25),
    (134.0, 765, 240, 1.45),  # back to the face
    (999.0, 836, 470, 1.05),  # final pull-back (time is clamped to song end)
]

FONT_TITLE = "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf"
FONT_SUB = "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf"


# ---------------------------------------------------------------- audio analysis
def analyse_audio(path, fps, duration):
    sr = 22050
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"],
        check=True, capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    n = int(duration * fps)
    hop = sr / fps
    win = 2048
    freqs = np.fft.rfftfreq(win, 1 / sr)
    bass_band = (freqs > 30) & (freqs < 180)
    hi_band = (freqs > 2000) & (freqs < 8000)
    window = np.hanning(win).astype(np.float32)
    rms, bass, hi = np.zeros(n), np.zeros(n), np.zeros(n)
    for i in range(n):
        c = int(i * hop)
        seg = x[max(0, c - win // 2): c + win // 2]
        if len(seg) < win:
            seg = np.pad(seg, (0, win - len(seg)))
        spec = np.abs(np.fft.rfft(seg * window))
        rms[i] = np.sqrt(np.mean(seg ** 2))
        bass[i] = spec[bass_band].mean()
        hi[i] = spec[hi_band].mean()

    def norm(v):
        lo, top = np.percentile(v, 5), np.percentile(v, 98)
        return np.clip((v - lo) / (top - lo + 1e-9), 0, 1)

    def envelope(v, attack, release):
        out = np.zeros_like(v)
        for i in range(1, len(v)):
            k = attack if v[i] > out[i - 1] else release
            out[i] = out[i - 1] + k * (v[i] - out[i - 1])
        return out

    rms, bass, hi = norm(rms), norm(bass), norm(hi)
    onset = np.clip(np.diff(bass, prepend=bass[0]), 0, None)
    onset = norm(onset) * (onset > np.percentile(onset, 90))
    return {
        "level": envelope(rms, 0.5, 0.06),
        "slow": envelope(rms, 0.03, 0.01),
        "bass": envelope(bass, 0.7, 0.12),
        "hi": envelope(hi, 0.6, 0.15),
        "kick": envelope(onset, 1.0, 0.15),
    }


# ---------------------------------------------------------------- camera
def catmull(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return 0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)


def camera_at(t, duration):
    keys = [list(k) for k in CAMERA]
    keys[-1][0] = duration
    keys = [k for k in keys if k[0] <= duration]
    ts = [k[0] for k in keys]
    i = max(0, min(np.searchsorted(ts, t, side="right") - 1, len(keys) - 2))
    u = (t - ts[i]) / max(ts[i + 1] - ts[i], 1e-6)
    u = u * u * (3 - 2 * u)  # ease in/out between keys
    k = lambda j: keys[max(0, min(j, len(keys) - 1))]
    cx = catmull(k(i - 1)[1], k(i)[1], k(i + 1)[1], k(i + 2)[1], u)
    cy = catmull(k(i - 1)[2], k(i)[2], k(i + 1)[2], k(i + 2)[2], u)
    lz = catmull(*(np.log(k(j)[3]) for j in (i - 1, i, i + 1, i + 2)), u)
    # gentle hand-held drift
    cx += 6 * np.sin(t * 0.37) + 3 * np.sin(t * 1.1)
    cy += 4 * np.sin(t * 0.29 + 1) + 2 * np.sin(t * 0.9)
    return cx, cy, float(np.exp(lz))


# ---------------------------------------------------------------- static layers
def fbm_noise(h, w, seed, octaves=5):
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        gh, gw = 3 * 2 ** o, int(3 * 2 ** o * w / h)
        g = rng.random((gh, gw)).astype(np.float32)
        g = np.concatenate([g, g[:, :1]], axis=1)  # wrap horizontally for tiling
        layer = cv2.resize(g, (w + w // gw, h), interpolation=cv2.INTER_CUBIC)[:, :w]
        acc += amp * layer
        total += amp
        amp *= 0.5
    acc /= total
    acc = (acc - acc.min()) / (acc.max() - acc.min())
    return acc


def build_layers(image_path):
    src = cv2.imread(image_path, cv2.IMREAD_COLOR)[:, :, ::-1]
    src = cv2.resize(src, (SRC_W, SRC_H), interpolation=cv2.INTER_AREA)
    bw, bh = int(SRC_W * BASE_SCALE), int(SRC_H * BASE_SCALE)
    base = cv2.resize(src, (bw, bh), interpolation=cv2.INTER_LANCZOS4).astype(np.float32) / 255
    # light sharpen to counter upscale softness
    base = np.clip(base * 1.35 - cv2.GaussianBlur(base, (0, 0), 2.0) * 0.35, 0, 1)

    lum = base @ np.array([0.299, 0.587, 0.114], np.float32)
    yy, xx = np.mgrid[0:bh, 0:bw].astype(np.float32) / BASE_SCALE  # source coords

    # bloom of the brightest areas
    bright = np.clip((lum - 0.62) / 0.38, 0, 1)[..., None] * base
    glow = cv2.GaussianBlur(bright, (0, 0), 18) * 0.9 + cv2.GaussianBlur(bright, (0, 0), 60) * 0.7

    # lamps: small, very bright, warm points in the lower part of the frame
    warm = (base[..., 0] > 0.75) & (base[..., 0] > base[..., 2] * 1.25) & (lum > 0.6)
    lamp_mask = (warm & (yy > 470)).astype(np.float32)
    lamp_mask = cv2.GaussianBlur(lamp_mask, (0, 0), 6)
    lamp_glow = cv2.GaussianBlur(lamp_mask, (0, 0), 14)[..., None] * np.array([1.0, 0.62, 0.22], np.float32)
    lamp_glow /= lamp_glow.max() + 1e-6

    # where clouds may "breathe": the sky, but not Shiva's face/trident or the hill
    sky = np.clip((520 - yy) / 120, 0, 1)
    face = np.exp(-(((xx - 700) / 300) ** 2 + ((yy - 220) / 260) ** 2) * 2.2)
    trident = np.exp(-((xx - 450) / 70) ** 2) * (yy < 420)
    cloud_mask = np.clip(sky - face * 1.6 - trident, 0, 1).astype(np.float32)
    cloud_mask = cv2.GaussianBlur(cloud_mask, (0, 0), 20)

    # mist bands (valley fog and foreground haze)
    band = np.exp(-((yy - 575) / 45) ** 2) * 0.9 + np.clip((yy - 760) / 180, 0, 1) * 0.55
    band *= 1 - 0.5 * np.exp(-((xx - 905) / 120) ** 2)  # keep main gopuram clear
    mist_mask = band.astype(np.float32)

    noise = fbm_noise(512, 1024, seed=7)
    noise2 = fbm_noise(512, 1024, seed=11)
    return {
        "base": base, "glow": glow.astype(np.float32), "lamp_glow": lamp_glow.astype(np.float32),
        "lamp_mask": lamp_mask, "cloud_mask": cloud_mask, "mist_mask": mist_mask,
        "noise": noise, "noise2": noise2,
    }


def text_layer(lines, w=OUT_W, h=OUT_H):
    """lines: list of (text, font_path, size, y). Returns float RGBA with golden glow."""
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for text, font, size, y in lines:
        f = ImageFont.truetype(font, size)
        tw = d.textlength(text, font=f)
        d.text(((w - tw) / 2, y), text, font=f, fill=(255, 226, 160, 255))
    alpha = np.array(img)[..., 3].astype(np.float32) / 255
    halo = np.array(img.filter(ImageFilter.GaussianBlur(14)))[..., 3].astype(np.float32) / 255
    rgb = np.array(img)[..., :3].astype(np.float32) / 255
    scrim = np.array(img.filter(ImageFilter.GaussianBlur(40)))[..., 3].astype(np.float32) / 255
    scrim = np.clip(scrim * 4, 0, 1)
    return rgb, alpha, halo, scrim


# ---------------------------------------------------------------- particles
class Particles:
    def __init__(self, n, seed, duration):
        rng = np.random.default_rng(seed)
        self.n = n
        self.x0 = rng.uniform(0, SRC_W, n)
        self.y0 = rng.uniform(SRC_H * 0.35, SRC_H * 1.1, n)
        self.speed = rng.uniform(8, 30, n)
        self.phase = rng.uniform(0, 2 * np.pi, n)
        self.sway = rng.uniform(4, 18, n)
        self.size = rng.uniform(0.8, 2.6, n)
        self.life = rng.uniform(5, 12, n)
        self.offset = rng.uniform(0, 12, n)
        self.hue = rng.uniform(0, 1, n)

    def at(self, t):
        age = (t + self.offset) % self.life
        cycle = np.floor((t + self.offset) / self.life)
        jitter = (np.sin(cycle * 12.9898 + self.phase * 78.233) * 43758.5453) % 1
        x = (self.x0 + jitter * 300) % SRC_W + self.sway * np.sin(t * 0.8 + self.phase)
        y = self.y0 - self.speed * age
        fade = np.sin(np.pi * age / self.life) ** 1.5
        return x, y, fade


# ---------------------------------------------------------------- frame renderer
G = {}


def init_worker(image_path, audio_feats, duration, fps):
    G["L"] = build_layers(image_path)
    G["A"] = audio_feats
    G["dur"] = duration
    G["fps"] = fps
    G["embers"] = Particles(260, 1, duration)
    G["sparks"] = Particles(140, 2, duration)
    G["title"] = text_layer([
        ("Jothi Darisanam", FONT_TITLE, 120, 760),
        ("Om Namah Shivaya", FONT_SUB, 54, 905)])
    G["end"] = text_layer([("Om Namah Shivaya", FONT_TITLE, 100, 820)])
    u = np.linspace(-1, 1, OUT_W, dtype=np.float32)
    v = np.linspace(-1, 1, OUT_H, dtype=np.float32)
    U, V = np.meshgrid(u, v)
    G["vignette"] = np.clip(1 - 0.38 * (U ** 2 * 0.8 + V ** 2) ** 1.2, 0, 1)[..., None].astype(np.float32)
    G["gx"], G["gy"] = np.meshgrid(np.arange(OUT_W, dtype=np.float32), np.arange(OUT_H, dtype=np.float32))


def render_frame(i):
    L, A, fps, dur = G["L"], G["A"], G["fps"], G["dur"]
    t = i / fps
    lvl, slow, bass, hi, kick = (A[k][min(i, len(A[k]) - 1)] for k in ("level", "slow", "bass", "hi", "kick"))

    cx, cy, z = camera_at(t, dur)
    z *= 1 + 0.012 * kick  # punch-in on strong beats
    cw = SRC_W / z
    ch = cw * OUT_H / OUT_W
    cx = np.clip(cx, cw / 2 + 4, SRC_W - cw / 2 - 4)
    cy = np.clip(cy, ch / 2 + 4, SRC_H - ch / 2 - 4)
    x0, y0 = cx - cw / 2, cy - ch / 2

    # source-space coordinates of every output pixel
    sx = (x0 + G["gx"] * (cw / OUT_W)).astype(np.float32)
    sy = (y0 + G["gy"] * (ch / OUT_H)).astype(np.float32)
    bx, by = sx * BASE_SCALE, sy * BASE_SCALE

    cm = cv2.remap(L["cloud_mask"], bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    dx = (np.sin(sy * 0.021 + t * 0.55) * 3.0 + np.sin(sx * 0.013 - t * 0.31) * 2.0) * cm
    dy = (np.cos(sx * 0.017 + t * 0.43) * 2.0) * cm
    mx = ((sx + dx + 14 * np.sin(t * 0.09) * cm) * BASE_SCALE).astype(np.float32)  # slow cloud sway
    my = ((sy + dy) * BASE_SCALE).astype(np.float32)
    img = cv2.remap(L["base"], mx, my, cv2.INTER_CUBIC, borderMode=cv2.BORDER_REFLECT)
    glow = cv2.remap(L["glow"], bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    img += glow * (0.06 + 0.22 * lvl + 0.14 * kick)

    # god rays from the burning peak
    ang = np.arctan2(sy - PEAK[1], sx - PEAK[0])
    dist = np.hypot(sx - PEAK[0], sy - PEAK[1])
    rays = (0.5 + 0.5 * np.sin(ang * 22 + t * 0.25)) ** 6 * (0.5 + 0.5 * np.sin(ang * 9 - t * 0.17)) ** 2
    rays *= np.exp(-dist / 520) * (sy < PEAK[1] + 60)
    img += rays[..., None] * np.array([1.0, 0.75, 0.38], np.float32) * (0.10 + 0.22 * bass)

    # the pillar of light
    beam_w = 7 + 5 * bass
    flick = 0.85 + 0.15 * np.sin(t * 11 + sy * 0.03)
    beam = np.exp(-((sx - BEAM_X) / beam_w) ** 2) * flick + 0.35 * np.exp(-((sx - BEAM_X) / (beam_w * 5)) ** 2)
    beam *= np.clip((BEAM_BOTTOM + 10 - sy) / 60, 0, 1) * (0.55 + 0.45 * np.clip(1 - sy / BEAM_BOTTOM, 0, 1))
    img += beam[..., None] * np.array([1.0, 0.86, 0.55], np.float32) * (0.25 + 0.55 * bass)

    # third-eye / face aura
    r2 = ((sx - THIRD_EYE[0]) / 14) ** 2 + ((sy - THIRD_EYE[1]) / 14) ** 2
    fr2 = ((sx - FACE[0]) / 260) ** 2 + ((sy - FACE[1]) / 230) ** 2
    pulse = 0.5 + 0.5 * np.sin(t * 2 * np.pi / 6.0)
    img += (np.exp(-r2)[..., None] * np.array([1.0, 0.7, 0.35], np.float32) * (0.35 + 0.6 * lvl)
            + np.exp(-fr2)[..., None] * np.array([1.0, 0.8, 0.5], np.float32) * (0.04 + 0.08 * pulse + 0.08 * slow))

    # flickering lamps
    lm = cv2.remap(L["lamp_glow"], bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    fl = 0.5 + 0.5 * np.sin(sx * 0.11 + t * 9.0) * np.sin(sy * 0.13 - t * 6.7 + sx * 0.02)
    img += lm * (0.25 + 0.55 * fl[..., None] + 0.35 * hi)

    # drifting mist (two scrolling noise fields)
    mm = cv2.remap(L["mist_mask"], bx, by, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    n1 = cv2.remap(L["noise"], ((sx * 0.6 + t * 9) % 1024).astype(np.float32),
                   ((sy * 0.5) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    n2 = cv2.remap(L["noise2"], ((sx * 0.35 - t * 5) % 1024).astype(np.float32),
                   ((sy * 0.4 + 100) % 512).astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    mist = np.clip((n1 * 0.6 + n2 * 0.6 - 0.45) * 1.6, 0, 1) * mm * 0.42
    img = img * (1 - mist[..., None]) + mist[..., None] * np.array([1.0, 0.9, 0.78], np.float32)

    # embers + sparkles (screen space)
    part = np.zeros((OUT_H, OUT_W, 3), np.float32)
    scale = OUT_W / cw
    for P, col, bright in ((G["embers"], (1.0, 0.55, 0.15), 1.0), (G["sparks"], (1.0, 0.9, 0.6), 0.9)):
        px, py, fade = P.at(t)
        qx, qy = (px - x0) * scale, (py - y0) * scale
        tw = 0.6 + 0.4 * np.sin(t * 7 + P.phase * 5)
        for j in range(P.n):
            if fade[j] < 0.02 or not (-10 < qx[j] < OUT_W + 10 and -10 < qy[j] < OUT_H + 10):
                continue
            a = fade[j] * tw[j] * bright * (0.6 + 0.6 * lvl)
            cv2.circle(part, (int(qx[j]), int(qy[j])), max(1, int(P.size[j] * scale * 0.6)),
                       (col[0] * a, col[1] * a, col[2] * a), -1, cv2.LINE_AA)
    img += cv2.GaussianBlur(part, (0, 0), 3) * 2.2 + part * 0.8

    # grade: warm filmic curve, vignette, gentle beat exposure
    img *= 1.0 + 0.05 * kick
    knee = 0.8  # soft highlight roll-off, midtones untouched
    img = np.where(img > knee, knee + (1 - knee) * (1 - np.exp(-(img - knee) / (1 - knee))), img)
    img = np.clip(img, 0, 1) ** 1.06  # a touch more contrast
    img *= G["vignette"]

    # title & end cards
    def card(layer, t_in, t_out, fade=1.5):
        nonlocal img
        if not (t_in <= t <= t_out):
            return
        a = min(1, (t - t_in) / fade, (t_out - t) / fade)
        rgb, alpha, halo, scrim = layer
        img = img * (1 - 0.55 * a * scrim[..., None])  # darken behind the text
        img += halo[..., None] * a * 0.25 * np.array([1, 0.6, 0.2], np.float32)
        img = img * (1 - a * alpha[..., None]) + rgb * a * alpha[..., None]

    card(G["title"], 2.5, 10.0)
    card(G["end"], dur - 9.0, dur - 2.0)

    # fade from / to black
    img *= min(1.0, t / 2.5, max(0.0, (dur - t) / 3.0))
    return (np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)


def render_chunk(args):
    start, end, path, fps = args
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OUT_W}x{OUT_H}",
         "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19",
         "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(start, end):
        enc.stdin.write(render_frame(i).tobytes())
        if (i - start) % 150 == 0:
            print(f"  [{os.getpid()}] frame {i}/{end}", flush=True)
    enc.stdin.close()
    enc.wait()
    return path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("image")
    ap.add_argument("audio")
    ap.add_argument("output")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--workers", type=int, default=os.cpu_count() or 4)
    ap.add_argument("--preview", type=float, default=0, help="render only N seconds")
    ap.add_argument("--start", type=float, default=0, help="preview start time")
    a = ap.parse_args()

    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                "-of", "csv=p=0", a.audio], capture_output=True, text=True).stdout)
    print(f"audio {dur:.2f}s, analysing...")
    feats = analyse_audio(a.audio, a.fps, dur)
    total = int(dur * a.fps)
    first = int(a.start * a.fps)
    last = min(total, first + int(a.preview * a.fps)) if a.preview else total

    tmp = tempfile.mkdtemp(prefix="vid_", dir=os.path.dirname(os.path.abspath(a.output)))
    n_chunks = a.workers * 3
    bounds = np.linspace(first, last, n_chunks + 1).astype(int)
    jobs = [(int(bounds[k]), int(bounds[k + 1]), os.path.join(tmp, f"c{k:03d}.mp4"), a.fps)
            for k in range(n_chunks) if bounds[k + 1] > bounds[k]]
    with Pool(a.workers, initializer=init_worker, initargs=(a.image, feats, dur, a.fps)) as pool:
        parts = pool.map(render_chunk, jobs, chunksize=1)

    lst = os.path.join(tmp, "list.txt")
    with open(lst, "w") as f:
        f.writelines(f"file '{p}'\n" for p in parts)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst,
                    "-ss", str(a.start), "-t", str((last - first) / a.fps), "-i", a.audio,
                    "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", a.output], check=True)
    for p in parts:
        os.remove(p)
    os.remove(lst)
    os.rmdir(tmp)
    print("done:", a.output)


if __name__ == "__main__":
    sys.exit(main())
