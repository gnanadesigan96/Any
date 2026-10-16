"""The quiz ending, drawn frame by frame: the countdown, the reveal and the end screen.

- countdown: the poster blurred beyond recognition, a glowing ring that runs down over the five seconds, a pulse
  on every second, turning from gold to red at the end.
- reveal: a flash, the poster snapping from blurred to sharp with a small zoom punch, a burst of gold sparkles, and
  a gold banner sliding down for the answer.
- outro: a glass card over the dimmed poster: the channel badge, a SUBSCRIBE button that pops in, gets tapped and
  turns into SUBSCRIBED with a ringing bell.

Only shapes and pictures are drawn here; every word is drawn by the captions (libass shapes Tamil correctly), at the
positions in LAYOUT, so text and shapes line up."""

import subprocess
from pathlib import Path

import numpy as np

# Fractions of the frame (x of the width, y and sizes of the height unless noted). captions.py uses the same values.
LAYOUT = {
    "ring_y": 0.46, "ring_r": 0.255,          # countdown ring centre and radius (radius: fraction of the width)
    "count_label_y": 0.215,                   # the line above the ring
    "banner_y": 0.085, "banner_w": 0.86, "banner_h": 0.082,   # reveal: the answer banner (w: of the width)
    "reveal_poster_y": 0.55, "reveal_poster_h": 0.72,
    "card_y": 0.455, "card_w": 0.88, "card_h": 0.56,          # outro card (w: of the width)
    "badge_y": 0.255, "badge_r": 0.085,                       # channel badge (r: of the width)
    "name_y": 0.345, "title_y": 0.405, "sub_y": 0.445,
    "button_y": 0.53, "button_w": 0.62, "button_h": 0.074,
    "thanks_y": 0.625, "thanks_sub_y": 0.665,
}
# The clue card: a pill with the heading, then each clue (its rows of text are drawn by the captions).
LAYOUT.update(clue_card_y=0.45, clue_card_h=0.44, clue_pill_y=0.285, clue_y=(0.37, 0.53), clue_row=0.042)
# Outro timings (seconds from the start of the end screen).
BUTTON_IN, TAP, THANKS_IN = 0.55, 1.75, 2.35
REVEAL_FLASH, REVEAL_SHARP, BANNER_IN = 0.14, 0.45, 0.3

GOLD = np.array([40, 200, 255], np.float32)    # BGR
ORANGE = np.array([30, 140, 255], np.float32)
RED = np.array([60, 60, 235], np.float32)
YT_RED = np.array([23, 33, 230], np.float32)
GREY = np.array([70, 70, 70], np.float32)
WHITE = np.array([255, 255, 255], np.float32)


def _ease_out(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return 1 - (1 - t) ** 3


def _ease_back(t: float) -> float:  # overshoots a little, then settles: a "pop"
    t = min(max(t, 0.0), 1.0)
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def _load(image: Path):
    import cv2
    img = cv2.imread(str(image), cv2.IMREAD_COLOR)
    if img is None:
        raise RuntimeError(f"Can't read the poster {image}")
    return img


def _cover(img, w: int, h: int):
    import cv2
    s = max(w / img.shape[1], h / img.shape[0])
    r = cv2.resize(img, (max(int(img.shape[1] * s + 0.5), w), max(int(img.shape[0] * s + 0.5), h)),
                   interpolation=cv2.INTER_AREA)
    y, x = (r.shape[0] - h) // 2, (r.shape[1] - w) // 2
    return r[y:y + h, x:x + w]


def _fit(img, max_w: int, max_h: int):
    import cv2
    s = min(max_w / img.shape[1], max_h / img.shape[0])
    return cv2.resize(img, (int(img.shape[1] * s), int(img.shape[0] * s)), interpolation=cv2.INTER_AREA)


def _unrecognisable(img):
    """Shrunk to a few dozen pixels and smoothed back up: colours stay, the title and faces don't."""
    import cv2
    h, w = img.shape[:2]
    tiny = cv2.resize(img, (max(w // 56, 5), max(h // 56, 5)), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(cv2.resize(tiny, (w, h), interpolation=cv2.INTER_CUBIC), (0, 0), max(w, h) / 60)


def _paste(base, fg, cx: int, cy: int, shadow: bool = True):
    import cv2
    h, w = fg.shape[:2]
    x0, y0 = cx - w // 2, cy - h // 2
    out = base.copy()
    if shadow:  # a soft drop shadow so the poster sits above the background
        m = np.zeros(base.shape[:2], np.float32)
        m[max(y0 + 18, 0):y0 + h + 18, max(x0, 0):x0 + w] = 1
        m = cv2.GaussianBlur(m, (0, 0), 28)[..., None] * 0.6
        out = (out * (1 - m)).astype(np.uint8)
    ys, xs = slice(max(y0, 0), min(y0 + h, base.shape[0])), slice(max(x0, 0), min(x0 + w, base.shape[1]))
    out[ys, xs] = fg[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    return out


def _zoom(img, scale: float):
    import cv2
    h, w = img.shape[:2]
    m = cv2.getRotationMatrix2D((w / 2, h / 2), 0, scale)
    return cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def _vignette(w: int, h: int, strength: float = 0.55):
    y, x = np.ogrid[:h, :w]
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    return (1 - strength * np.clip(d - 0.35, 0, 1) ** 1.5)[..., None].astype(np.float32)


def _glow(layer, sigma: float):
    """A wide blur, done at a quarter of the size (16x less work; a glow has no fine detail anyway)."""
    import cv2
    h, w = layer.shape[:2]
    small = cv2.resize(layer, (w // 4, h // 4), interpolation=cv2.INTER_AREA)
    out = cv2.resize(cv2.GaussianBlur(small, (0, 0), max(sigma / 4, 0.5)), (w, h), interpolation=cv2.INTER_LINEAR)
    return out.reshape(layer.shape)


def _add(frame, layer, alpha):
    """Composites a BGR layer (an image, or one colour) with its own alpha (h, w, 1, or a number) onto the frame.
    Only the box where the alpha is non-zero is touched (most layers are small: a ring, a button, sparkles)."""
    import cv2
    if np.isscalar(alpha):
        return frame * (1 - alpha) + layer * alpha
    a2 = alpha.reshape(alpha.shape[0], alpha.shape[1])
    x, y, bw, bh = cv2.boundingRect((a2 > 1 / 512).astype(np.uint8))
    if bw == 0 or bh == 0:
        return frame
    ys, xs = slice(y, y + bh), slice(x, x + bw)
    a = alpha[ys, xs]
    lay = layer
    if getattr(layer, "ndim", 1) == 3:  # a full image, or a per-row gradient (h, 1, 3)
        lay = layer[ys, xs] if layer.shape[1] == frame.shape[1] else layer[ys]
    frame[ys, xs] = frame[ys, xs] * (1 - a) + lay * a
    return frame


def _round_rect_mask(w: int, h: int, cx: int, cy: int, bw: int, bh: int, r: int):
    import cv2
    m = np.zeros((h, w), np.uint8)
    x0, y0, x1, y1 = cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2
    r = max(1, min(r, bw // 2, bh // 2))
    cv2.rectangle(m, (x0 + r, y0), (x1 - r, y1), 255, -1, cv2.LINE_AA)
    cv2.rectangle(m, (x0, y0 + r), (x1, y1 - r), 255, -1, cv2.LINE_AA)
    for px, py in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        cv2.circle(m, (px, py), r, 255, -1, cv2.LINE_AA)
    return m.astype(np.float32)[..., None] / 255


class _Writer:
    """Raw frames into ffmpeg (H.264, the same settings as every other clip)."""

    def __init__(self, out: Path, w: int, h: int, cfg: dict):
        v = cfg["video"]
        self.p = subprocess.Popen(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24",
             "-s", f"{w}x{h}", "-r", str(v["fps"]), "-i", "-", "-c:v", "libx264", "-preset", str(v["preset"]),
             "-crf", str(v["crf"]), "-pix_fmt", "yuv420p", "-an", str(out)],
            stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    def write(self, frame):
        self.p.stdin.write(np.clip(frame, 0, 255).astype(np.uint8).tobytes())

    def close(self):
        self.p.stdin.close()
        err = self.p.stderr.read().decode(errors="replace")
        if self.p.wait() != 0:
            raise RuntimeError(f"ffmpeg failed while writing a finale clip: {err.strip()}")


def _backdrops(image: Path, w: int, h: int):
    """The poster three ways, all full-frame: blurred-beyond-recognition, sharp (for the reveal) and dimmed."""
    import cv2
    img = _load(image)
    bg = cv2.GaussianBlur(_cover(img, w, h), (0, 0), 38)
    hidden_bg = (_unrecognisable(_cover(img, w, h)) * 0.62).astype(np.uint8)
    fg_count = _fit(img, int(w * 0.86), int(h * 0.8))
    hidden = _paste(hidden_bg, (_unrecognisable(fg_count) * 0.9).astype(np.uint8), w // 2, int(h * 0.5), shadow=False)
    fg = _fit(img, int(w * 0.86), int(h * LAYOUT["reveal_poster_h"]))
    sharp = _paste((bg * 0.55).astype(np.uint8), fg, w // 2, int(h * LAYOUT["reveal_poster_y"]))
    soft = cv2.GaussianBlur(_paste((bg * 0.5).astype(np.uint8), fg, w // 2, int(h * 0.5), shadow=False), (0, 0), 10)
    dim = (soft * 0.42).astype(np.uint8)
    return hidden, sharp, dim


def render_countdown(image: Path, frames: int, out: Path, cfg: dict) -> None:
    import cv2
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    hidden, _, _ = _backdrops(image, w, h)
    vig = _vignette(w, h, 0.65)
    cx, cy, r = w // 2, int(h * LAYOUT["ring_y"]), int(w * LAYOUT["ring_r"])
    thick = max(8, w // 48)
    total = frames / fps
    writer = _Writer(out, w, h, cfg)
    for n in range(frames):
        t = n / fps
        frame = _zoom(hidden, 1 + 0.035 * t / total).astype(np.float32) * vig
        left = max(0.0, 1 - t / total)
        colour = GOLD if left > 0.45 else (ORANGE if left > 0.22 else RED)
        layer = np.zeros((h, w, 3), np.float32)
        mask = np.zeros((h, w), np.float32)
        # Track ring, then the arc that is left, running down clockwise from the top.
        cv2.circle(mask, (cx, cy), r, 0.22, thick, cv2.LINE_AA)
        arc = np.zeros((h, w), np.float32)
        cv2.ellipse(arc, (cx, cy), (r, r), -90, 0, 360 * left, 1.0, thick, cv2.LINE_AA)
        layer[:] = WHITE
        frame = _add(frame, layer, mask[..., None])
        glow = _glow(arc, thick * 1.4)[..., None]
        frame = _add(frame, colour, np.clip(glow * 1.8, 0, 0.85))
        frame = _add(frame, colour, arc[..., None])
        # Dark disc behind the number.
        disc = np.zeros((h, w), np.float32)
        cv2.circle(disc, (cx, cy), r - thick * 2, 1.0, -1, cv2.LINE_AA)
        frame = frame * (1 - disc[..., None] * 0.35)
        # A pulse ring on every second, growing and fading out.
        k = t - int(t)
        pulse = np.zeros((h, w), np.float32)
        cv2.circle(pulse, (cx, cy), int(r * (1 + 0.35 * _ease_out(k / 0.7))), 1.0, max(3, thick // 3), cv2.LINE_AA)
        frame = _add(frame, colour, pulse[..., None] * max(0.0, 0.7 * (1 - k / 0.7)))
        if left < 0.22:  # the last second: the edges flush red
            frame = frame + (1 - vig) * RED * 0.35 * (0.5 + 0.5 * np.sin(t * 12))
        writer.write(frame)
    writer.close()


def _sparkles(seed: int, w: int, h: int, n: int = 70):
    rng = np.random.default_rng(seed)
    ang = rng.uniform(0, 2 * np.pi, n)
    speed = rng.uniform(0.35, 1.0, n) * w * 1.25
    return [dict(a=a, s=s, size=rng.uniform(0.004, 0.011) * w, life=rng.uniform(0.9, 1.7),
                 c=GOLD if rng.random() < 0.7 else WHITE) for a, s in zip(ang, speed)]


def render_reveal(image: Path, frames: int, out: Path, cfg: dict) -> None:
    import cv2
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    hidden, sharp, _ = _backdrops(image, w, h)
    vig = _vignette(w, h, 0.45)
    sparks = _sparkles(sum(map(ord, image.name)), w, h)
    ox, oy = w // 2, int(h * LAYOUT["reveal_poster_y"])
    bw, bh, by = int(w * LAYOUT["banner_w"]), int(h * LAYOUT["banner_h"]), int(h * LAYOUT["banner_y"])
    writer = _Writer(out, w, h, cfg)
    for n in range(frames):
        t = n / fps
        a = _ease_out(t / REVEAL_SHARP)
        frame = (hidden.astype(np.float32) * (1 - a) + sharp.astype(np.float32) * a)
        frame = _zoom(frame, 1.1 - 0.1 * _ease_out(t / 0.6) + 0.012 * t) * vig
        # Sparkles: burst out from the poster, slow down, fall and fade.
        layer = np.zeros((h, w), np.float32)
        hot = np.zeros((h, w), np.float32)
        for s in sparks:
            if t > s["life"]:
                continue
            d = s["s"] * (1 - np.exp(-3 * t)) / 3
            x = int(ox + np.cos(s["a"]) * d)
            y = int(oy + np.sin(s["a"]) * d + 0.5 * h * 0.35 * t * t)
            fade = 1 - t / s["life"]
            size = max(1, int(s["size"] * (0.6 + 0.4 * fade)))
            cv2.circle(layer if s["c"] is GOLD else hot, (x, y), size, fade, -1, cv2.LINE_AA)
        frame = _add(frame, GOLD, np.clip(_glow(layer, 6)[..., None] * 2.2 + layer[..., None], 0, 1))
        frame = _add(frame, WHITE, np.clip(_glow(hot, 5)[..., None] * 2 + hot[..., None], 0, 1))
        # The gold answer banner slides down from the top.
        k = _ease_back((t - BANNER_IN) / 0.35) if t > BANNER_IN else 0
        if k > 0:
            cy = int(-bh + (by + bh) * k)
            m = _round_rect_mask(w, h, w // 2, cy, bw, bh, bh // 2)
            shadow = _glow(np.roll(m, 10, axis=0), 14)
            frame = frame * (1 - shadow * 0.55)
            grad = np.linspace(1.12, 0.82, h, dtype=np.float32)[:, None, None] * GOLD
            frame = _add(frame, np.clip(grad, 0, 255), m)
        if t < REVEAL_FLASH:  # a white flash at the cut
            frame = _add(frame, WHITE, 0.85 * (1 - t / REVEAL_FLASH))
        writer.write(frame)
    writer.close()


def _bell(mask, cx: int, cy: int, s: int, angle: float) -> None:
    """A small bell, drawn into `mask` (1.0 where it is), tilted by `angle` degrees."""
    import cv2
    pts = np.array([[-0.55, 0.45], [-0.45, -0.1], [-0.3, -0.45], [0, -0.58], [0.3, -0.45], [0.45, -0.1],
                    [0.55, 0.45]], np.float32) * s
    rot = np.deg2rad(angle)
    rm = np.array([[np.cos(rot), -np.sin(rot)], [np.sin(rot), np.cos(rot)]], np.float32)
    pts = (pts @ rm.T + [cx, cy]).astype(np.int32)
    cv2.fillPoly(mask, [pts], 1.0, cv2.LINE_AA)
    base = (np.array([[-0.65, 0.45], [0.65, 0.45]], np.float32) * s) @ rm.T + [cx, cy]
    cv2.line(mask, tuple(map(int, base[0])), tuple(map(int, base[1])), 1.0, max(2, s // 6), cv2.LINE_AA)
    clap = (np.array([0, 0.62], np.float32) * s) @ rm.T + [cx, cy]
    cv2.circle(mask, tuple(map(int, clap)), max(2, s // 7), 1.0, -1, cv2.LINE_AA)


def render_outro(image: Path, frames: int, out: Path, cfg: dict) -> None:
    import cv2
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    _, _, dim = _backdrops(image, w, h)
    vig = _vignette(w, h, 0.5)
    L = LAYOUT
    card = _round_rect_mask(w, h, w // 2, int(h * L["card_y"]), int(w * L["card_w"]), int(h * L["card_h"]), w // 18)
    edge = np.clip(card - _round_rect_mask(w, h, w // 2, int(h * L["card_y"]), int(w * L["card_w"]) - 6,
                                           int(h * L["card_h"]) - 6, w // 18 - 3), 0, 1)
    bx, by, br = w // 2, int(h * L["badge_y"]), int(w * L["badge_r"])
    btn_w, btn_h, btn_y = int(w * L["button_w"]), int(h * L["button_h"]), int(h * L["button_y"])
    total = frames / fps
    writer = _Writer(out, w, h, cfg)
    for n in range(frames):
        t = n / fps
        frame = _zoom(dim, 1.02 + 0.02 * t / total).astype(np.float32) * vig
        k = _ease_out(t / 0.35)
        # Frosted glass card with a thin gold edge.
        frame = frame * (1 - card * 0.5 * k) + card * np.array([18, 14, 12], np.float32) * 0.5 * k
        frame = _add(frame, GOLD, edge * 0.8 * k)
        # Channel badge: a gold ring with a film reel inside, popping in.
        pb = _ease_back(t / 0.45)
        if pb > 0:
            m = np.zeros((h, w), np.float32)
            rr = max(2, int(br * pb))
            cv2.circle(m, (bx, by), rr, 1.0, -1, cv2.LINE_AA)
            frame = _add(frame, GOLD, m[..., None])
            inner = np.zeros((h, w), np.float32)
            cv2.circle(inner, (bx, by), max(1, int(rr * 0.84)), 1.0, -1, cv2.LINE_AA)
            frame = _add(frame, np.array([30, 24, 20], np.float32), inner[..., None])
            reel = np.zeros((h, w), np.float32)
            cv2.circle(reel, (bx, by), max(1, int(rr * 0.55)), 1.0, max(2, rr // 9), cv2.LINE_AA)
            spin = t * 90
            for j in range(5):
                a = np.deg2rad(spin + j * 72)
                cv2.circle(reel, (int(bx + np.cos(a) * rr * 0.3), int(by + np.sin(a) * rr * 0.3)),
                           max(1, int(rr * 0.11)), 1.0, -1, cv2.LINE_AA)
            cv2.circle(reel, (bx, by), max(1, int(rr * 0.08)), 1.0, -1, cv2.LINE_AA)
            frame = _add(frame, GOLD, reel[..., None])
        # SUBSCRIBE button: pops in, is tapped (a ripple), and turns grey with a ringing bell.
        pk = _ease_back((t - BUTTON_IN) / 0.4) if t > BUTTON_IN else 0
        if pk > 0:
            press = 1 - 0.06 * np.exp(-((t - TAP) / 0.08) ** 2)
            bw_, bh_ = int(btn_w * pk * press), int(btn_h * pk * press)
            m = _round_rect_mask(w, h, w // 2, btn_y, max(bw_, 2), max(bh_, 2), max(bh_ // 2, 1))
            colour = YT_RED if t < TAP + 0.05 else GREY
            shadow = _glow(np.roll(m, 8, axis=0), 12)
            frame = frame * (1 - shadow * 0.5)
            frame = _add(frame, colour, m)
            if t >= TAP + 0.05:
                bell = np.zeros((h, w), np.float32)
                swing = 22 * np.sin((t - TAP) * 28) * np.exp(-(t - TAP) * 2.2)
                _bell(bell, w // 2 - int(btn_w * 0.36), btn_y, int(btn_h * 0.32), swing)
                frame = _add(frame, WHITE, bell[..., None])
            if TAP <= t < TAP + 0.6:  # tap ripple
                q = (t - TAP) / 0.6
                rip = np.zeros((h, w), np.float32)
                cv2.circle(rip, (w // 2 + int(btn_w * 0.18), btn_y), int(btn_h * (0.2 + 1.6 * q)), 1.0, -1, cv2.LINE_AA)
                frame = _add(frame, WHITE, rip[..., None] * 0.45 * (1 - q) * m)
        writer.write(frame)
    writer.close()


def render_clue(image: Path, frames: int, out: Path, cfg: dict) -> None:
    """The clue card over the dimmed last story picture: a glass card with a gold edge and a gold heading pill."""
    v = cfg["video"]
    w, h, fps = v["width"], v["height"], v["fps"]
    _, _, dim = _backdrops(image, w, h)
    vig = _vignette(w, h, 0.5)
    L = LAYOUT
    card = _round_rect_mask(w, h, w // 2, int(h * L["clue_card_y"]), int(w * 0.88), int(h * L["clue_card_h"]), w // 18)
    edge = np.clip(card - _round_rect_mask(w, h, w // 2, int(h * L["clue_card_y"]), int(w * 0.88) - 6,
                                           int(h * L["clue_card_h"]) - 6, w // 18 - 3), 0, 1)
    total = frames / fps
    writer = _Writer(out, w, h, cfg)
    for n in range(frames):
        t = n / fps
        frame = _zoom(dim, 1.02 + 0.02 * t / total).astype(np.float32) * vig
        k = _ease_back(t / 0.35)
        frame = frame * (1 - card * 0.55 * min(k, 1)) + card * np.array([18, 14, 12], np.float32) * 0.55 * min(k, 1)
        frame = _add(frame, GOLD, edge * 0.85 * min(k, 1))
        pk = _ease_back((t - 0.1) / 0.35) if t > 0.1 else 0
        if pk > 0:
            pw, ph = int(w * 0.34 * pk), int(h * 0.06 * pk)
            pill = _round_rect_mask(w, h, w // 2, int(h * L["clue_pill_y"]), max(pw, 2), max(ph, 2), max(ph // 2, 1))
            frame = _add(frame, GOLD, pill)
        writer.write(frame)
    writer.close()


def render_finale_clip(kind: str, image: Path, frames: int, out: Path, cfg: dict) -> None:
    {"countdown": render_countdown, "clue_countdown": render_countdown, "clue": render_clue,
     "reveal": render_reveal, "outro": render_outro}[kind](image, frames, out, cfg)
