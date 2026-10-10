"""Free 2.5D animation for still illustrations.

A small depth model (Depth Anything V2 Small, Apache-2.0, runs on the CPU) estimates what is near
and far in each image. The camera then moves through the scene with near things moving more than
far things (parallax), which reads as animation rather than a flat zoom. Atmospheric effects
(fog, rain, snow, embers, flickering light, lightning) are chosen from each scene's description
and drawn on top, frame by frame.
"""

import re
import subprocess
import threading
from pathlib import Path

import numpy as np

from .config import resolve
from .util import log

DEPTH_URL = ("https://github.com/fabio-sim/Depth-Anything-ONNX/releases/download/v2.0.0/"
             "depth_anything_v2_vits.onnx")
DEPTH_FILE = "depth_anything_v2_vits.onnx"
MOTIONS = ["push_in", "pan_right", "pull_out", "pan_left", "drift_up"]

EFFECT_WORDS = [
    ("rain", r"\b(rain|raining|downpour|storm|stormy|drizzle)\b"),
    ("lightning", r"\b(lightning|thunder|storm)\b"),
    ("snow", r"\b(snow|snowy|blizzard|snowfall|frost)\b"),
    ("fog", r"\b(fog|foggy|mist|misty|haze|smoke)\b"),
    ("embers", r"\b(fire|campfire|embers?|flames?|burning|torch)\b"),
    ("flicker", r"\b(candle|candles|candlelit|candlelight|lamp|lamplight|lantern|firelight|fire|campfire|torch)\b"),
]


def effects_for(text: str, limit: int = 2) -> list:
    """Pick up to `limit` atmospheric effects from a scene's description and narration."""
    text = text.lower()
    found = [name for name, pattern in EFFECT_WORDS if re.search(pattern, text)]
    return found[:limit]


# ---- depth --------------------------------------------------------------------------------

class _Depth:
    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        import onnxruntime as ort
        path = resolve("models") / DEPTH_FILE
        if not path.exists():
            from .voice import _download
            _download(DEPTH_URL, path)
        self.session = ort.InferenceSession(str(path), providers=["CPUExecutionProvider"])
        self.input = self.session.get_inputs()[0].name

    @classmethod
    def get(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def __call__(self, rgb: np.ndarray) -> np.ndarray:
        import cv2
        x = cv2.resize(rgb, (518, 518), interpolation=cv2.INTER_CUBIC).astype(np.float32) / 255.0
        x = (x - [0.485, 0.456, 0.406]) / [0.229, 0.224, 0.225]
        x = x.transpose(2, 0, 1)[None].astype(np.float32)
        with self._lock:
            out = self.session.run(None, {self.input: x})[0][0]
        return out


def depth_map(image_path: Path, rgb: np.ndarray) -> np.ndarray:
    """Relative depth in [0, 1] (1 = nearest), cached next to the image as a 16-bit PNG."""
    import cv2
    cache = image_path.with_name(image_path.stem + ".depth.png")
    if cache.exists():
        d = cv2.imread(str(cache), cv2.IMREAD_UNCHANGED).astype(np.float32) / 65535.0
        if d.shape[:2] == rgb.shape[:2]:
            return d
    raw = _Depth.get()(rgb)
    raw = cv2.resize(raw, (rgb.shape[1], rgb.shape[0]), interpolation=cv2.INTER_CUBIC)
    lo, hi = np.percentile(raw, 2), np.percentile(raw, 98)
    d = np.clip((raw - lo) / max(hi - lo, 1e-6), 0, 1)
    # Grow near regions slightly and smooth, so object edges don't tear when they move.
    d = cv2.dilate(d, np.ones((9, 9), np.uint8))
    d = cv2.GaussianBlur(d, (0, 0), sigmaX=max(rgb.shape[1] / 300, 1.5))
    cv2.imwrite(str(cache), (d * 65535).astype(np.uint16))
    return d


# ---- effects ------------------------------------------------------------------------------

class _Effects:
    def __init__(self, names: list, w: int, h: int, frames: int, seed: int):
        import cv2
        self.names, self.w, self.h, self.frames = names, w, h, frames
        rng = np.random.default_rng(seed)
        self.rng = rng
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        self.vignette = np.clip(1.0 - 0.35 * np.clip(r - 0.55, 0, None) ** 1.5, 0.55, 1.0)[..., None]
        if "fog" in names:
            small = rng.random((h // 64 + 2, (w * 2) // 64 + 2)).astype(np.float32)
            fog = cv2.resize(small, (w * 2, h), interpolation=cv2.INTER_CUBIC)
            self.fog = cv2.GaussianBlur(fog, (0, 0), sigmaX=w / 25)
            self.fog = (self.fog - self.fog.min()) / max(np.ptp(self.fog), 1e-6)
        n = {"rain": 700, "snow": 350, "embers": 90}
        self.particles = {}
        for name in ("rain", "snow", "embers"):
            if name in names:
                self.particles[name] = np.column_stack([rng.random(n[name]) * w, rng.random(n[name]) * h,
                                                        0.5 + rng.random(n[name])])
        self.flashes = set()
        if "lightning" in names:
            for start in rng.choice(max(frames - 6, 1), size=min(2, max(frames // 60, 1)), replace=False):
                self.flashes.update(range(int(start), int(start) + 4))

    def apply(self, img: np.ndarray, i: int) -> np.ndarray:
        import cv2
        out = img.astype(np.float32)
        t = i / max(self.frames - 1, 1)
        if "flicker" in self.names:
            k = 1.0 + 0.05 * np.sin(i * 0.7) + 0.03 * np.sin(i * 2.3) + 0.02 * self.rng.standard_normal()
            out *= np.array([k * 0.97, k, k * 1.05], np.float32)  # BGR: warm the light
        if "fog" in self.names:
            shift = int(t * self.w * 0.5)
            f = self.fog[:, shift:shift + self.w][..., None]
            out = out * (1 - 0.35 * f) + 205 * 0.35 * f
        overlay = np.zeros_like(img)
        h, w = self.h, self.w
        if "rain" in self.particles:
            p = self.particles["rain"]
            p[:, 1] = (p[:, 1] + 55 * p[:, 2]) % h
            p[:, 0] = (p[:, 0] - 8 * p[:, 2]) % w
            for x, y, s in p:
                cv2.line(overlay, (int(x), int(y)), (int(x + 8 * s), int(y - 40 * s)), (190, 190, 200), 1, cv2.LINE_AA)
        if "snow" in self.particles:
            p = self.particles["snow"]
            p[:, 1] = (p[:, 1] + 3.5 * p[:, 2]) % h
            p[:, 0] = (p[:, 0] + 1.5 * np.sin(i * 0.05 + p[:, 2] * 6)) % w
            for x, y, s in p:
                cv2.circle(overlay, (int(x), int(y)), int(2 + 3 * s), (245, 245, 245), -1, cv2.LINE_AA)
        if "embers" in self.particles:
            p = self.particles["embers"]
            p[:, 1] = (p[:, 1] - 4 * p[:, 2]) % h
            p[:, 0] = (p[:, 0] + 2 * np.sin(i * 0.1 + p[:, 2] * 9)) % w
            for x, y, s in p:
                cv2.circle(overlay, (int(x), int(y)), int(2 + 2 * s), (40, 140, 255), -1, cv2.LINE_AA)
        if overlay.any():
            out = out + overlay.astype(np.float32) * 0.8
        if i in self.flashes:
            out = out * 0.45 + 255 * 0.55
        out *= self.vignette
        return np.clip(out, 0, 255).astype(np.uint8)


# ---- camera -------------------------------------------------------------------------------

def _ease(t: float) -> float:
    return t * t * (3 - 2 * t)


def render_parallax_clip(image: Path, frames: int, index: int, out: Path, cfg: dict,
                         text: str = "") -> None:
    """Writes `frames` frames of 2.5D camera motion over `image` to `out` (H.264, no audio)."""
    import cv2
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    a = v.get("parallax", {})
    strength = float(a.get("strength", 1.0))

    bgr = cv2.imread(str(image), cv2.IMREAD_COLOR)
    if bgr is None:
        raise RuntimeError(f"Could not read image {image}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    depth = depth_map(image, rgb)
    # Cover-fit to the output frame with a little margin, so camera moves never reveal an edge.
    margin = 1.12
    scale = max(w / bgr.shape[1], h / bgr.shape[0]) * margin
    size = (int(round(bgr.shape[1] * scale)), int(round(bgr.shape[0] * scale)))
    src = cv2.resize(bgr, size, interpolation=cv2.INTER_CUBIC)
    dep = cv2.resize(depth, size, interpolation=cv2.INTER_LINEAR)
    ox, oy = (size[0] - w) / 2, (size[1] - h) / 2
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = dep[int(oy):int(oy) + h, int(ox):int(ox) + w]
    near = 0.25 + 0.75 * d  # how strongly each pixel follows the camera move
    cx, cy = w / 2, h / 2

    motion = MOTIONS[index % len(MOTIONS)]
    zoom = 0.10 * strength
    pan = 0.045 * w * strength
    effects = _Effects(effects_for(text) if v.get("effects", True) else [], w, h, frames, seed=index)
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-frames:v", str(frames),
           "-c:v", "libx264", "-preset", str(v["preset"]), "-crf", str(v["crf"]), "-pix_fmt", "yuv420p", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for i in range(frames):
            t = _ease(i / max(frames - 1, 1))
            if motion == "push_in":
                s, dx, dy = 1 + zoom * t * near, 0.0, 0.0
            elif motion == "pull_out":
                s, dx, dy = 1 + zoom * (1 - t) * near, 0.0, 0.0
            elif motion == "pan_right":
                s, dx, dy = 1 + 0.03 * near, pan * (t - 0.5) * near, 0.0
            elif motion == "pan_left":
                s, dx, dy = 1 + 0.03 * near, -pan * (t - 0.5) * near, 0.0
            else:  # drift_up
                s, dx, dy = 1 + 0.04 * t * near, 0.0, -0.6 * pan * (t - 0.5) * near
            map_x = (cx + (xx - cx) / s - dx + ox).astype(np.float32)
            map_y = (cy + (yy - cy) / s - dy + oy).astype(np.float32)
            frame = cv2.remap(src, map_x, map_y, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
            proc.stdin.write(effects.apply(frame, i).tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass
    if proc.wait() != 0:
        raise RuntimeError(f"ffmpeg failed while animating {image.name}: {proc.stderr.read().decode()[-500:]}")
    log(f"  animated {image.name} ({motion}{', ' + ', '.join(effects.names) if effects.names else ''})")
