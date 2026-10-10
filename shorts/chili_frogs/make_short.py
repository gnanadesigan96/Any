"""Render a 20s vertical (1080x1920) YouTube Short: "Frogs vs. the Hottest Chili".

Pure procedural 2D animation with Pillow + numpy, audio synthesized with numpy,
muxed with ffmpeg. Usage:  python make_short.py [output.mp4]
"""
import math
import random
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920          # output size
K = 2                      # supersampling factor
FPS = 30
DUR = 20.0
NF = int(FPS * DUR)
WORLD_H = 6000             # tall world: field at bottom, sky above
GROUND = WORLD_H - 300     # feet line (world y)
CAM0 = WORLD_H - H         # camera top at start
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("chili_frogs_short.mp4")
TMP = OUT.with_suffix("")

FONT_PATHS = ["/usr/share/fonts/opentype/inter/Inter-Black.otf",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


# ---------------------------------------------------------------- helpers
def clamp(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def seg(t, a, b):
    """0..1 progress of t across [a, b]."""
    return clamp((t - a) / (b - a))


def ease(u):
    return u * u * (3 - 2 * u)


def ease_in(u):
    return u * u * u


def lerp(a, b, u):
    return a + (b - a) * u


def lerpc(c1, c2, u):
    return tuple(int(lerp(a, b, u)) for a, b in zip(c1, c2))


def darker(c, f=0.6):
    return tuple(int(v * f) for v in c)


class Pen:
    """Draws in logical (1080-wide) coordinates onto a K-scaled canvas with a y offset."""

    def __init__(self, img, oy=0.0, ox=0.0, sc=1.0, piv=(0.0, 0.0)):
        self.d = ImageDraw.Draw(img)
        self.oy, self.ox = oy, ox
        self.sc, self.piv = sc, piv  # optional scale about a pivot (for bigger characters)

    def P(self, x, y):
        x = self.piv[0] + (x - self.piv[0]) * self.sc
        y = self.piv[1] + (y - self.piv[1]) * self.sc
        return ((x - self.ox) * K, (y - self.oy) * K)

    def ell(self, cx, cy, rx, ry, fill, outline=None, w=4):
        x0, y0 = self.P(cx - rx, cy - ry)
        x1, y1 = self.P(cx + rx, cy + ry)
        self.d.ellipse([x0, y0, x1, y1], fill=fill,
                       outline=outline, width=int(w * K * self.sc) if outline else 0)

    def line(self, pts, fill, w):
        self.d.line([self.P(*p) for p in pts], fill=fill, width=int(w * K * self.sc), joint="curve")
        for p in (pts[0], pts[-1]):
            self.ell(p[0], p[1], w / 2, w / 2, fill)

    def poly(self, pts, fill, outline=None, w=3):
        self.d.polygon([self.P(*p) for p in pts], fill=fill,
                       outline=outline, width=int(w * K * self.sc) if outline else 0)

    def arc(self, cx, cy, rx, ry, a0, a1, fill, w):
        x0, y0 = self.P(cx - rx, cy - ry)
        x1, y1 = self.P(cx + rx, cy + ry)
        self.d.arc([x0, y0, x1, y1], a0, a1, fill=fill, width=int(w * K * self.sc))


def chili(pen, x, y, ang, size=1.0, col=(215, 30, 35)):
    """A curved chili pepper; (x, y) is the stem end."""
    pts = []
    L = 70 * size
    for i in range(13):
        u = i / 12
        r = 13 * size * math.sin(math.pi * min(1, u * 1.15)) * (1 - 0.75 * u) + 2
        bend = 18 * size * u * u
        pts.append((u * L, bend, r))
    ca, sa = math.cos(ang), math.sin(ang)

    def rot(px, py):
        return (x + px * ca - py * sa, y + px * sa + py * ca)
    upper = [rot(px, py - r) for px, py, r in pts]
    lower = [rot(px, py + r) for px, py, r in reversed(pts)]
    pen.poly(upper + lower, col, darker(col, 0.55), 2)
    hx, hy = rot(L * 0.25, -5 * size)
    pen.ell(hx, hy, 9 * size, 3 * size, lerpc(col, (255, 255, 255), 0.45))
    sx, sy = rot(-10 * size, -4 * size)
    pen.line([(x, y), (sx, sy)], (60, 130, 40), 6 * size)


# ---------------------------------------------------------------- world background
def build_world():
    rnd = random.Random(7)
    img = Image.new("RGB", (W * K, WORLD_H * K))
    # sky gradient: deep blue high up -> pale near horizon
    top, mid, low = np.array([40, 110, 210]), np.array([80, 160, 240]), np.array([190, 225, 250])
    ys = np.linspace(0, 1, WORLD_H * K)[:, None]
    g = np.where(ys < 0.6, top + (mid - top) * (ys / 0.6), mid + (low - mid) * ((ys - 0.6) / 0.4))
    arr = np.repeat(g[:, None, :], W * K, axis=1).astype(np.uint8)
    img = Image.fromarray(arr.reshape(WORLD_H * K, W * K, 3))
    pen = Pen(img)

    def cloud(cx, cy, s):
        for dx, dy, r in [(-90, 10, 60), (-30, -30, 80), (50, -15, 70), (110, 15, 50), (0, 25, 75)]:
            pen.ell(cx + dx * s, cy + dy * s + 8 * s, r * s, r * s * 0.9, (205, 220, 240))
        for dx, dy, r in [(-90, 10, 60), (-30, -30, 80), (50, -15, 70), (110, 15, 50), (0, 25, 75)]:
            pen.ell(cx + dx * s, cy + dy * s, r * s, r * s * 0.9, (255, 255, 255))

    for _ in range(38):
        cloud(rnd.uniform(-50, W + 50), rnd.uniform(200, WORLD_H - 1500), rnd.uniform(0.7, 1.9))
    # sun with glow
    sx, sy = 860, WORLD_H - 1650
    for r, c in [(230, (235, 240, 235)), (170, (250, 245, 215)), (110, (255, 248, 200)), (80, (255, 252, 230))]:
        pen.ell(sx, sy, r, r, c)
    # distant hills & tree line
    hz = GROUND - 650
    for i, (col, amp, off) in enumerate([((140, 190, 150), 60, 0), ((95, 160, 95), 45, 2.0)]):
        pts = [(x, hz - 40 * (1 - i) + amp * math.sin(x / 170 + off)) for x in range(-20, W + 40, 20)]
        pen.poly(pts + [(W + 40, GROUND + 400), (-20, GROUND + 400)], col)
    for x in range(-40, W + 60, 55):
        r = rnd.uniform(40, 70)
        pen.ell(x, hz + 40 - r * 0.4, r, r * 1.1, (50, 115, 60), (40, 95, 50), 3)
    # field ground
    pen.poly([(-20, hz + 60), (W + 20, hz + 60), (W + 20, WORLD_H), (-20, WORLD_H)], (90, 150, 60))
    # back rows of chili bushes (smaller = farther)
    for row in range(5):
        y = hz + 90 + row * 90
        s = 0.45 + row * 0.12
        for x in np.arange(-30 + (row % 2) * 40, W + 60, 85 * s + 30):
            bush(pen, x + rnd.uniform(-10, 10), y, s, rnd)
    return img


def bush(pen, x, y, s, rnd):
    for _ in range(6):
        dx, dy = rnd.uniform(-55, 55) * s, rnd.uniform(-70, 0) * s
        pen.ell(x + dx, y + dy, 45 * s, 38 * s, lerpc((45, 120, 45), (80, 160, 60), rnd.random()),
                (35, 95, 35), 2)
    for _ in range(5):
        chili(pen, x + rnd.uniform(-55, 50) * s, y + rnd.uniform(-95, -25) * s,
              rnd.uniform(1.2, 1.9), 0.55 * s * 1.6)


def build_foreground():
    """Front bush row (RGBA) drawn over the frogs' feet."""
    rnd = random.Random(11)
    h = 520
    img = Image.new("RGBA", (W * K, h * K), (0, 0, 0, 0))
    pen = Pen(img, oy=GROUND - 330)
    for x in range(-40, W + 80, 110):
        if 140 < x < 940 and rnd.random() < 0.55:
            continue  # leave gaps so the frogs stay visible
        bush(pen, x, GROUND + 120, 1.15, rnd)
    pen.poly([(-20, GROUND + 100), (W + 20, GROUND + 100), (W + 20, GROUND + 200), (-20, GROUND + 200)],
             (70, 130, 50, 255))
    return img, GROUND - 330


# ---------------------------------------------------------------- characters
GREEN, GREEN_BELLY = (125, 175, 95), (205, 220, 160)
YELLOW, YELLOW_BELLY = (225, 185, 75), (245, 225, 160)
HOT, HOT_BELLY = (235, 75, 60), (255, 160, 140)
WHITE, INK = (255, 255, 255), (30, 25, 25)
LIP = (240, 140, 140)


def eye(pen, x, y, r, lid_col, look=(0, 0), squint=0.0, pop=1.0):
    pen.ell(x, y, r * 1.22, r * 1.22, lid_col, darker(lid_col), 4)
    pen.ell(x, y, r * pop, r * pop, WHITE, (90, 90, 90), 3)
    pr = r * 0.38
    pen.ell(x + look[0] * r * 0.35, y + look[1] * r * 0.35, pr, pr, INK)
    pen.ell(x + look[0] * r * 0.35 - pr * 0.35, y + look[1] * r * 0.35 - pr * 0.35, pr * 0.3, pr * 0.3, WHITE)
    if squint > 0:  # angry/smug brow-lid
        pen.poly([(x - r * 1.3, y - r * 1.3), (x + r * 1.3, y - r * 1.3),
                  (x + r * 1.3, y - r * 1.3 + 2 * r * squint * 0.9),
                  (x - r * 1.3, y - r * 1.3 + 2 * r * squint * 0.3)], lid_col)


def mouth(pen, x, y, w, kind, open_=0.0):
    if kind == "smile":
        pen.ell(x, y, w, 18, LIP, darker(LIP), 3)
        pen.arc(x, y - 30, w * 0.95, 40, 20, 160, INK, 5)
    elif kind == "open":
        pen.ell(x, y, w, 22 + 60 * open_, LIP, darker(LIP), 4)
        pen.ell(x, y + 4, w * 0.8, 10 + 50 * open_, (90, 25, 35))
        pen.ell(x, y + 18 + 30 * open_, w * 0.45, 8 + 20 * open_, (230, 100, 110))
    elif kind == "pucker":  # puffed, lips pressed
        pen.ell(x, y, w * 0.55, 26, (250, 120, 120), darker(LIP), 4)
        pen.line([(x - w * 0.4, y), (x + w * 0.4, y)], (120, 40, 40), 4)
    elif kind == "smug":
        pen.ell(x, y, w, 24, LIP, darker(LIP), 4)
        pen.arc(x + 10, y - 12, w * 0.8, 26, 15, 120, INK, 5)


def flame(pen, x, y, length, wid, t, seed):
    rnd = random.Random(int(t * 60) * 31 + seed)
    for col, f in [((255, 90, 20), 1.0), ((255, 160, 30), 0.72), ((255, 235, 120), 0.45), ((255, 255, 230), 0.22)]:
        L = length * f * rnd.uniform(0.85, 1.1)
        w = wid * (0.4 + 0.6 * f)
        pts = [(x - w, y)]
        for i in range(1, 8):
            u = i / 8
            pts.append((x - w * (1 - u) + rnd.uniform(-6, 6) * f, y + L * u))
        pts.append((x + rnd.uniform(-8, 8), y + L))
        for i in range(7, 0, -1):
            u = i / 8
            pts.append((x + w * (1 - u) + rnd.uniform(-6, 6) * f, y + L * u))
        pts.append((x + w, y))
        pen.poly(pts, col)


def fat_frog(pen, x, fy, st):
    red = st.get("red", 0)
    body = lerpc(GREEN, HOT, red)
    belly = lerpc(GREEN_BELLY, HOT_BELLY, red)
    sq = st.get("squash", 0)
    by = fy - 190
    if st.get("flame"):
        for dx in (-70, 70):
            flame(pen, x + dx, fy - 20, st["flame"], 42, st["t"], dx)
    for dx in (-95, 95):
        pen.ell(x + dx, fy - 22, 62, 26, body, darker(body), 4)
    pen.ell(x, by, 172 * (1 + sq), 190 * (1 - sq), body, darker(body), 5)
    pen.ell(x, by + 35, 122 * (1 + sq), 128 * (1 - sq), belly)
    # arms
    if st.get("arm_up"):  # right hand raised (holding chili to mouth)
        u = st["arm_up"]
        hx, hy = lerp(x + 190, x + 70, u), lerp(by + 40, fy - 300, u)
        pen.line([(x - 165, by - 20), (x - 185, by + 70)], body, 48)
        pen.line([(x + 160, by - 20), (hx, hy)], body, 48)
        if st.get("hold"):
            chili(pen, hx - 10, hy - 10, math.radians(200), 1.1)
    elif st.get("laugh"):
        pen.line([(x - 165, by - 20), (x - 120, by + 90)], body, 48)
        pen.line([(x + 165, by - 20), (x + 120, by + 90)], body, 48)
    else:
        for dx in (-1, 1):
            pen.line([(x + dx * 165, by - 20), (x + dx * 190, by + 75)], body, 48)
    # face
    cheek = st.get("cheek", 0)
    if cheek > 0:
        for dx in (-1, 1):
            pen.ell(x + dx * (120 + 30 * cheek), fy - 290, 40 + 55 * cheek, 35 + 45 * cheek,
                    lerpc(body, (250, 95, 80), 0.6), darker(body), 4)
    mouth(pen, x, fy - 290, 115, st.get("mouth", "smile"), st.get("open", 0))
    ey = fy - 370 - 20 * sq
    for dx in (-1, 1):
        eye(pen, x + dx * 78, ey, 52, body, st.get("look", (0, 0)), st.get("squint", 0), st.get("pop", 1))
    # little pink buddy on the head
    bx, bby = x, ey - 75 + st.get("buddy_hop", 0)
    pen.ell(bx, bby, 50, 36, (245, 200, 210), (200, 150, 165), 4)
    for dx in (-1, 1):
        pen.ell(bx + dx * 20, bby - 30, 13, 13, (245, 200, 210), (200, 150, 165), 3)
        pen.ell(bx + dx * 20, bby - 30, 6, 6, INK)
    pen.arc(bx, bby - 4, 14, 8, 20, 160, INK, 3)


def thin_frog(pen, x, fy, st):
    red = st.get("red", 0)
    body = lerpc(YELLOW, HOT, red)
    belly = lerpc(YELLOW_BELLY, HOT_BELLY, red)
    if st.get("flame"):
        for dx in (-30, 30):
            flame(pen, x + dx, fy - 10, st["flame"], 26, st["t"], dx + 5)
    # legs
    for dx in (-1, 1):
        pen.line([(x + dx * 28, fy - 210), (x + dx * 38, fy - 18)], body, 26)
        pen.ell(x + dx * 50, fy - 12, 34, 13, body, darker(body), 3)
    pen.ell(x, fy - 285, 72, 112, body, darker(body), 4)
    pen.ell(x, fy - 265, 48, 80, belly)
    # arms
    sh = fy - 345
    if st.get("crossed"):
        pen.line([(x - 60, sh), (x - 30, sh + 70), (x + 55, sh + 55)], body, 22)
        pen.line([(x + 60, sh), (x + 30, sh + 85), (x - 55, sh + 70)], body, 22)
    else:
        pen.line([(x - 62, sh), (x - 95, fy - 230)], body, 22)
        u = st.get("arm_up", 0)
        hx, hy = lerp(x + 100, x + 35, u), lerp(fy - 240, fy - 420, u)
        if st.get("wave"):
            hy -= 120 + 25 * math.sin(st["t"] * 14)
            hx += 15
        pen.line([(x + 62, sh), (hx, hy)], body, 22)
        if st.get("hold"):
            chili(pen, hx - 5, hy - 5, math.radians(200 + 40 * (1 - u)), 1.0)
    # head
    hy0 = fy - 445
    cheek = st.get("cheek", 0)
    if cheek > 0:
        for dx in (-1, 1):
            pen.ell(x + dx * (70 + 22 * cheek), hy0 + 15, 28 + 45 * cheek, 26 + 38 * cheek,
                    lerpc(body, (250, 95, 80), 0.6), darker(body), 4)
    pen.ell(x, hy0, 92, 62, body, darker(body), 4)
    mouth(pen, x, hy0 + 18, 70, st.get("mouth", "smile"), st.get("open", 0))
    for dx in (-1, 1):
        eye(pen, x + dx * 48, hy0 - 58, 37, body, st.get("look", (0, 0)), st.get("squint", 0), st.get("pop", 1))


def steam(pen, x, y, t, amt, seed):
    if amt <= 0:
        return
    for i in range(6):
        ph = (t * 1.6 + i / 6 + seed) % 1
        r = (14 + 30 * ph) * amt
        pen.ell(x + 40 * math.sin(i * 2.1 + seed) * ph + (i - 2.5) * 12, y - 220 * ph, r, r,
                lerpc((255, 255, 255), (225, 230, 240), ph))


# ---------------------------------------------------------------- timeline
LIFT0, LIFT1 = 10.6, 15.0
FS = 1.45           # character scale
FX, TX = 300, 800   # frog x positions
ALT = 3600


def altitude(t, delay=0.0):
    u = seg(t, LIFT0 + delay, LIFT1)
    a = ALT * (ease_in(u) * 0.35 + ease(u) * 0.65)
    if t > LIFT1:
        a += 30 * math.sin((t - LIFT1) * 2.2 + delay * 5)
    return a


def cam_top(t):
    u = seg(t, LIFT0 + 0.25, LIFT1 + 0.6)
    return CAM0 - (ALT - 250) * ease(u)


def states(t):
    """Return (fat_state, thin_state, shake_amount, caption)."""
    fat = {"t": t, "look": (0.6, 0)}
    thin = {"t": t, "look": (-0.6, 0)}
    blink = (t % 3.1) < 0.12
    if blink:
        fat["pop"] = 0.15
        thin["pop"] = 0.15
    cap = None
    shake = 0.0
    # 0-2.6 intro: thin frog waves a chili
    if t < 2.6:
        thin.update(hold=True, arm_up=0.25, wave=t < 1.6)
        thin["look"] = (0.4, -0.3)
        cap = ("THE HOTTEST", "CHILI CHALLENGE")
    # 2.6-3.6 eat
    elif t < 3.6:
        u = ease(seg(t, 2.6, 3.3))
        thin.update(hold=t < 3.35, arm_up=lerp(0.25, 1, u), mouth="open", open_=0)
        thin["open"] = 0.8 if t < 3.35 else 0.1
        fat["look"] = (0.8, -0.2)
        cap = ("ONE", "BITE...")
    # 3.6-7 heat builds on thin frog
    if 3.6 <= t:
        u = seg(t, 3.7, 6.2)
        thin.update(red=ease(u), cheek=ease(seg(t, 4.3, 6.4)), mouth="pucker",
                    pop=1 + 0.35 * ease(u) if not blink else 0.15)
        thin["look"] = (0, 0)
        shake = 0.0 + 7 * u
        if 3.6 <= t < 7.2:
            cap = ("UH OH...",) if t < 5.4 else ("IT'S", "TOO HOT!!")
    # fat frog laughs 5-7
    if 5.0 <= t < 7.2:
        fat.update(laugh=True, mouth="open", open_=0.5 + 0.4 * abs(math.sin(t * 12)), squint=0.5,
                   buddy_hop=-14 * abs(math.sin(t * 12)))
    # fat frog eats 7.2-8.6 ("hold my chili")
    if 7.2 <= t < 8.6:
        u = ease(seg(t, 7.3, 8.1))
        fat.update(arm_up=u, hold=t < 8.15, mouth="open", open_=0.9 if t < 8.15 else 0.2, squint=0.4)
        cap = ("HOLD MY", "CHILI")
    if t >= 8.6:
        u = seg(t, 8.6, 10.2)
        fat.update(red=ease(u), cheek=ease(seg(t, 8.9, 10.4)), mouth="pucker",
                   pop=1 + 0.4 * ease(u) if not blink else 0.15, look=(0, 0))
        shake = max(shake, 3 + 9 * u)
        if t < 10.6:
            cap = ("BIG", "MISTAKE")
    # sputtering flames, then liftoff
    if t >= 9.8:
        sp = seg(t, 9.8, LIFT0)
        flick = 0.5 + 0.5 * math.sin(t * 40)
        fl = lerp(30 * flick, 160, sp) if t < LIFT0 else 230 + 60 * seg(t, LIFT0, 12)
        fat["flame"] = fl
        thin["flame"] = fl * 0.8
        shake = max(shake, 12 * sp)
    if t >= LIFT0:
        shake = 10 * (1 - seg(t, LIFT0 + 1, LIFT1))
        fat["squash"] = -0.08
        if t < LIFT1:
            cap = ("LIFTOFF!!",)
    # hovering in the sky: smug & cool
    if t >= LIFT1 - 0.4:
        cool = ease(seg(t, LIFT1 - 0.4, LIFT1 + 0.4))
        thin.update(crossed=True, squint=0.6 * cool, mouth="smug", cheek=lerp(1, 0.4, cool), look=(0.5, 0))
        fat.update(squint=0.55 * cool, mouth="smug", cheek=lerp(1, 0.4, cool), look=(-0.5, 0))
        fat["flame"] = thin["flame"] = 200 + 25 * math.sin(t * 9)
        cap = ("WORTH IT?",) if t < 17.4 else ("FOLLOW", "FOR PART 2")
    return fat, thin, shake, cap


# ---------------------------------------------------------------- frame render
_fonts = {}


def font(sz):
    if sz not in _fonts:
        for p in FONT_PATHS:
            if Path(p).exists():
                _fonts[sz] = ImageFont.truetype(p, sz)
                break
        else:
            _fonts[sz] = ImageFont.load_default()
    return _fonts[sz]


_cap_start = {}


def draw_caption(img, cap, t):
    if not cap:
        return
    if cap not in _cap_start or t - _cap_start[cap][1] > 0.1:
        if cap not in _cap_start or _cap_start[cap][1] < t - 0.1:
            _cap_start[cap] = [t, t]
    _cap_start[cap][1] = t
    age = t - _cap_start[cap][0]
    pop = 1 + 0.25 * math.exp(-age * 9) * math.cos(age * 25) if age < 0.6 else 1
    d = ImageDraw.Draw(img)
    y = 300
    for i, line in enumerate(cap):
        sz = int(118 * pop)
        while font(sz).getlength(line) + 20 > W - 100:
            sz -= 4
        f = font(sz)
        fill = (255, 230, 40) if i == len(cap) - 1 and len(cap) > 1 else (255, 255, 255)
        d.text((W / 2, y), line, font=f, fill=fill, anchor="mm", stroke_width=10, stroke_fill=(20, 15, 15))
        y += sz * 1.08


def smoke(pen, t, x0, seed):
    """World-space smoke trail left behind during liftoff."""
    if t < LIFT0 - 0.3:
        return
    ts = LIFT0 - 0.3
    while ts < t:
        age = t - ts
        if age < 1.6:
            rnd = random.Random(int(ts * 100) + seed)
            alt = altitude(ts)
            r = 30 + 45 * age
            c = lerpc((170, 160, 160), (225, 232, 245), clamp(age / 1.2))
            pen.ell(x0 + rnd.uniform(-50, 50) + 20 * age * rnd.choice((-1, 1)),
                    GROUND - alt + 200 + 80 * age, r, r * 0.85, c)
        ts += 1 / 30


def render_frame(world, fg, fg_top, fi):
    t = fi / FPS
    fat, thin, shake, cap = states(t)
    ct = cam_top(t)
    rnd = random.Random(fi)
    sx, sy = rnd.uniform(-shake, shake), rnd.uniform(-shake, shake)
    top = int(round((ct + sy) * K))
    top = max(0, min(top, world.height - H * K))
    frame = world.crop((0, top, W * K, top + H * K))
    pen = Pen(frame, oy=top / K, ox=sx)
    smoke(pen, t, FX, 1)
    smoke(pen, t, TX, 2)
    fx, tx = FX, TX
    fat_y = GROUND - altitude(t)
    thin_y = GROUND - altitude(t, 0.12)
    if t < 10.6 and 5.0 <= t < 7.2:  # laughing bounce
        fat_y -= 10 * abs(math.sin(t * 12))
    if t < 2.6:
        thin_y -= 18 * abs(math.sin(t * 7))
    fat_frog(Pen(frame, oy=top / K, ox=sx, sc=FS, piv=(fx, fat_y)), fx, fat_y, fat)
    thin_frog(Pen(frame, oy=top / K, ox=sx, sc=FS, piv=(tx, thin_y)), tx, thin_y, thin)
    steam(pen, tx, thin_y - 520 * FS, t, FS * seg(t, 4.6, 5.6) * (1 - seg(t, 10.5, 11)), 0.3)
    steam(pen, fx, fat_y - 530 * FS, t, FS * seg(t, 9.2, 10) * (1 - seg(t, 10.5, 11)), 0.7)
    # foreground bushes
    y = int(round((fg_top - top / K) * K))
    if y < H * K:
        frame.paste(fg, (int(-sx * K), y), fg)
    # speed lines during the fast climb
    sp = seg(t, LIFT0 + 0.4, LIFT0 + 1.2) * (1 - seg(t, LIFT1 - 1.2, LIFT1))
    if sp > 0:
        lr = random.Random(fi // 2)
        sd = ImageDraw.Draw(frame)
        for _ in range(int(14 * sp)):
            x = lr.uniform(0, W) * K
            yy = lr.uniform(0, H) * K
            sd.line([(x, yy), (x, yy + lr.uniform(150, 400) * K)], fill=(255, 255, 255), width=3 * K)
    frame = frame.resize((W, H), Image.LANCZOS)
    draw_caption(frame, cap, t)
    return frame


# ---------------------------------------------------------------- audio
SR = 44100


def synth_audio(path):
    n = int(SR * DUR)
    tt = np.arange(n) / SR
    out = np.zeros(n)
    rng = np.random.default_rng(3)

    def env(dur, a=0.005, r=0.15):
        m = int(dur * SR)
        e = np.ones(m)
        ai = max(1, int(a * SR))
        e[:ai] = np.linspace(0, 1, ai)
        e *= np.exp(-np.arange(m) / (r * SR))
        return e

    def add(sig, start):
        i = int(start * SR)
        j = min(n, i + len(sig))
        if i < n:
            out[i:j] += sig[: j - i]

    # bouncy music loop (stops at liftoff, returns in the sky)
    bpm = 128
    beat = 60 / bpm
    notes = [72, 76, 79, 76, 74, 77, 81, 77, 72, 76, 79, 84, 83, 79, 76, 74]
    bass = [48, 48, 53, 53, 55, 55, 48, 48]
    f = lambda m: 440 * 2 ** ((m - 69) / 12)
    b = 0
    while b * beat < DUR:
        st = b * beat
        if not (9.8 <= st < LIFT1):
            m = notes[b % len(notes)]
            d = beat * 0.9
            e = env(d, r=0.12)
            x = np.arange(len(e)) / SR
            add(0.12 * e * (np.sign(np.sin(2 * np.pi * f(m) * x)) * 0.3 + np.sin(2 * np.pi * f(m) * x)), st)
            if b % 2 == 0:
                bm = bass[(b // 2) % len(bass)]
                e = env(beat * 1.8, r=0.3)
                x = np.arange(len(e)) / SR
                add(0.18 * e * np.sin(2 * np.pi * f(bm) * x), st)
            # hi-hat
            add(0.04 * env(0.05, r=0.015) * rng.standard_normal(int(0.05 * SR)), st + beat / 2)
        b += 1

    def crunch(start):
        for k in range(5):
            m = int(0.06 * SR)
            add(0.5 * env(0.06, r=0.02) * rng.standard_normal(m), start + k * 0.07)

    crunch(3.3)
    crunch(8.15)
    # "boing" when cheeks puff
    for st, f0 in [(4.4, 180), (9.0, 120)]:
        d = 0.8
        x = np.arange(int(d * SR)) / SR
        freq = f0 * (1 + 1.5 * x / d) + 30 * np.sin(2 * np.pi * 9 * x)
        add(0.3 * np.exp(-x * 2.5) * np.sin(2 * np.pi * np.cumsum(freq) / SR), st)
    # sizzle while heating
    sizzle = rng.standard_normal(n)
    sizzle = np.diff(np.concatenate([[0], sizzle]))  # high-passed hiss
    hs = np.clip((tt - 4.5) / 2, 0, 1) * (tt < 10.6) + np.clip((tt - 9) / 1.5, 0, 1) * (tt < 10.6)
    out += 0.05 * sizzle * hs
    # sputter pops
    for k in range(10):
        add(0.35 * env(0.04, r=0.01) * rng.standard_normal(int(0.04 * SR)), 9.8 + k * 0.08)
    # rocket roar: low-passed noise, loud at liftoff then steady
    noise = rng.standard_normal(n)
    a = 0.02
    roar = np.zeros(n)
    acc = 0.0
    for i in range(0, n):
        acc += a * (noise[i] - acc)
        roar[i] = acc
    roar /= np.max(np.abs(roar)) + 1e-9
    rv = np.clip((tt - LIFT0) / 0.3, 0, 1) * (1 - 0.6 * np.clip((tt - 12) / 3, 0, 1))
    out += 0.8 * roar * rv
    # rising whoosh
    d = LIFT1 - LIFT0
    x = np.arange(int(d * SR)) / SR
    wf = 200 + 900 * (x / d) ** 2
    add(0.12 * np.sin(2 * np.pi * np.cumsum(wf) / SR) * np.exp(-((x - d * 0.4) ** 2) / 2), LIFT0)
    out = np.tanh(out * 1.3) * 0.85
    pcm = (out * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


# ---------------------------------------------------------------- main
def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wav = TMP.with_suffix(".wav")
    print("synthesizing audio...")
    synth_audio(wav)
    print("building world...")
    world = build_world()
    fg, fg_top = build_foreground()
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium",
           "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
           "-movflags", "+faststart", str(OUT)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(NF):
        proc.stdin.write(render_frame(world, fg, fg_top, fi).tobytes())
        if fi % 60 == 0:
            print(f"frame {fi}/{NF}", flush=True)
    proc.stdin.close()
    proc.wait()
    wav.unlink(missing_ok=True)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
