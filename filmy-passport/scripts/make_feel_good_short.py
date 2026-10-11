"""Top 5 Feel-Good English Movies - cinematic YouTube Short (no voice). v3

Per movie: big poster rendered as a real print (3D tilt with perspective,
moving specular shine, shape-matched shadow), giant rank numeral, themed
motion, frosted-glass info panel with typewriter description,
film grain + vignette. Original upbeat synthesized music.

Usage: python3 make_short.py [preview [t1 t2 ...]]
"""
import math
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "filmy_passport_feel_good_part1_HQ.mp4")
CHANNEL = "@FilmyPassport"  # change to your handle

W, H, FPS = 1080, 1920, 30
INTRO, PER, OUTRO = 4.0, 9.0, 5.2
DURATION = INTRO + 5 * PER + OUTRO   # design timeline
# real (faster) timeline: animations are designed on the timeline above and
# played back faster by mapping real time -> design time
R_INTRO, R_PER, R_OUTRO = 3.0, 6.4, 4.0
R_DURATION = R_INTRO + 5 * R_PER + R_OUTRO


def design_t(rt):
    if rt < R_INTRO:
        return rt * INTRO / R_INTRO
    rt -= R_INTRO
    if rt < 5 * R_PER:
        i, r = divmod(rt, R_PER)
        return INTRO + i * PER + r * PER / R_PER
    return INTRO + 5 * PER + (rt - 5 * R_PER) * OUTRO / R_OUTRO

FD = "/usr/share/fonts/opentype/inter/"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
INK, SOFT = (52, 32, 28), (105, 76, 68)


def font(n, s):
    return ImageFont.truetype(FD + n + ".otf", s)


# rank, file, title, year, cast, genres, imdb, description, particles, motif, accent
MOVIES = [
    (5, "made_of_honor", "Made of Honor", 2008, "Patrick Dempsey · Michelle Monaghan",
     ["Rom-Com", "Wedding"], 5.8,
     "A charming serial dater finally realises he loves his best friend — right when she asks him to be her maid of honor.",
     ["💐", "🎊", "💍"], "fall", (226, 92, 132)),
    (4, "plus_one", "Plus One", 2019, "Maya Erskine · Jack Quaid",
     ["Rom-Com", "Friendship"], 6.6,
     "Two single best friends agree to be each other's date for every wedding in one chaotic summer. What could go wrong?",
     ["🥂", "🍾", "✨"], "rise", (222, 160, 10)),
    (3, "the_vow", "The Vow", 2012, "Rachel McAdams · Channing Tatum",
     ["Romance", "True Story"], 6.8,
     "After an accident erases her memory, a devoted husband sets out to make his wife fall in love with him all over again.",
     ["💗", "💞", "🤍"], "heart", (214, 104, 104)),
    (2, "love_rosie", "Love, Rosie", 2014, "Lily Collins · Sam Claflin",
     ["Rom-Com", "Best Friends"], 7.1,
     "Best friends since childhood, Rosie and Alex keep missing their moment — for twelve whole years.",
     ["💌", "🎈", "✉️"], "rise", (150, 92, 200)),
    (1, "about_time", "About Time", 2013, "Domhnall Gleeson · Rachel McAdams",
     ["Romance", "Fantasy"], 7.8,
     "A young man discovers he can travel back in time — and slowly learns that the ordinary days matter most.",
     ["⏳", "✨", "🕰️"], "clock", (204, 64, 64)),
]


# ------------------------------------------------------------------ utils
def clamp(t):
    return min(max(t, 0.0), 1.0)


def ease_out(t):
    return 1 - (1 - clamp(t)) ** 3


def ease_io(t):
    t = clamp(t)
    return 3 * t * t - 2 * t ** 3


def back_out(t):
    t = clamp(t)
    c = 1.6
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def lerp(a, b, t):
    return a + (b - a) * t


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((90, 90), ch, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)


def fade(layer, a):
    if a >= 0.999:
        return layer
    out = layer.copy()
    out.putalpha(layer.getchannel("A").point(lambda v: int(v * max(a, 0))))
    return out


def wrap(d, txt, f, mw):
    lines, cur = [], ""
    for w in txt.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= mw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def spaced(d, cx, y, txt, f, fill, sp):
    ws = [d.textlength(c, font=f) for c in txt]
    x = cx - (sum(ws) + sp * (len(txt) - 1)) / 2
    for c, w in zip(txt, ws):
        d.text((x, y), c, font=f, fill=fill)
        x += w + sp


def soft_shadow(w, h, r, blur=30, op=90):
    p = blur * 3
    s = Image.new("RGBA", (w + 2 * p, h + 2 * p), (0, 0, 0, 0))
    ImageDraw.Draw(s).rounded_rectangle((p, p, p + w, p + h), r, fill=(40, 20, 20, op))
    return s.filter(ImageFilter.GaussianBlur(blur)), p


def coeffs(dst, src):
    A, B = [], []
    for (x, y), (u, v) in zip(dst, src):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); B.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); B.append(v)
    return np.linalg.solve(np.array(A, float), np.array(B, float)).tolist()


def project(img, ax, ay, scale=1.0, f=2200):
    """Render img as a flat card rotated by ax (pitch) / ay (yaw), with perspective."""
    w, h = img.size
    ws, hs = w * scale, h * scale
    cw, ch = int(ws * 1.25) + 2, int(hs * 1.25) + 2
    dst = []
    for x, y in [(-ws / 2, -hs / 2), (ws / 2, -hs / 2), (ws / 2, hs / 2), (-ws / 2, hs / 2)]:
        x1, z1 = x * math.cos(ay), x * math.sin(ay)
        y2, z2 = y * math.cos(ax) - z1 * math.sin(ax), y * math.sin(ax) + z1 * math.cos(ax)
        k = f / (f + z2)
        dst.append((cw / 2 + x1 * k, ch / 2 + y2 * k))
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    return img.transform((cw, ch), Image.PERSPECTIVE, coeffs(dst, src), Image.BICUBIC)


# ------------------------------------------------------------------ assets
PW, PH = 800, 1184          # poster print size (hero)
HERO_C = (W // 2, 875)      # hero centre
SMALL_S = 0.78              # scale when the info panel is up
SMALL_C = (W // 2, 185 + int(PH * SMALL_S) // 2)
PANEL = (70, 1135, W - 70, 1580)

# specular sheet: soft diagonal highlight we slide across the print
_sx = np.linspace(-1, 1, PW * 2)[None, :]
_sy = np.linspace(-1, 1, PH * 2)[:, None]
_band = np.exp(-((_sx * 0.9 + _sy * 0.45) * 3.2) ** 2)
SPEC = Image.fromarray((_band * 120).astype(np.uint8), "L")


def load_assets(m):
    key = m[1]
    src = Image.open(os.path.join(HERE, "posters", key + ".jpg")).convert("RGB")
    s = max(W / src.width, H / src.height) * 1.15
    bg = src.resize((int(src.width * s), int(src.height * s)), Image.BICUBIC)
    bg = bg.filter(ImageFilter.GaussianBlur(50))
    bg = Image.blend(bg, Image.new("RGB", bg.size, (255, 244, 236)), 0.5).convert("RGBA")
    sc = max(PW / src.width, PH / src.height)
    p = src.resize((int(src.width * sc), int(src.height * sc)), Image.LANCZOS)
    p = p.filter(ImageFilter.UnsharpMask(2.5, 90, 2))
    ox, oy = (p.width - PW) // 2, (p.height - PH) // 2
    p = p.crop((ox, oy, ox + PW, oy + PH)).convert("RGBA")
    mask = Image.new("L", (PW, PH), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, PW - 1, PH - 1), 18, fill=255)
    # thin glossy edge, like a laminated print
    edge = Image.new("RGBA", (PW, PH), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle((1, 1, PW - 2, PH - 2), 18, outline=(255, 255, 255, 120), width=3)
    p.alpha_composite(edge)
    p.putalpha(mask)
    # giant numeral
    num = Image.new("RGBA", (360, 380), (0, 0, 0, 0))
    nd = ImageDraw.Draw(num)
    nf = font("InterDisplay-Black", 330)
    nd.text((180, 190), str(m[0]), font=nf, fill=(255, 255, 255), anchor="mm",
            stroke_width=12, stroke_fill=m[-1])
    nsh = Image.new("RGBA", num.size, (0, 0, 0, 0))
    ImageDraw.Draw(nsh).text((186, 200), str(m[0]), font=nf, fill=(40, 20, 20, 120), anchor="mm",
                             stroke_width=12, stroke_fill=(40, 20, 20, 120))
    nsh = nsh.filter(ImageFilter.GaussianBlur(10))
    nsh.alpha_composite(num)
    return dict(bg=bg, card=p, mask=mask, num=nsh, sprites=[emoji(e, 90) for e in m[8]])


ASSETS = [load_assets(m) for m in MOVIES]

rng = np.random.default_rng(3)
PARTS = [dict(x=rng.uniform(40, W - 40), y=rng.uniform(0, H), sp=rng.uniform(80, 160),
              sw=rng.uniform(20, 60), ph=rng.uniform(0, 6.3), sc=rng.uniform(0.4, 1.0),
              k=int(rng.integers(0, 3)), rot=rng.uniform(-40, 40)) for _ in range(14)]
# grain + vignette (applied on the final RGB frame)
GRAIN = [rng.normal(0, 2.5, (H // 2, W // 2, 1)).repeat(2, 0).repeat(2, 1).astype(np.int16) for _ in range(6)]
_vy = np.linspace(-1, 1, H)[:, None]
_vx = np.linspace(-1, 1, W)[None, :]
VIGN = (1 - 0.22 * np.clip((_vx ** 2 * 0.9 + _vy ** 2 * 0.6) - 0.15, 0, 1))[:, :, None].astype(np.float32)


# ------------------------------------------------------------------ pieces
def draw_particles(fr, m, A, lt, a):
    for pt in PARTS:
        spr = A["sprites"][pt["k"]]
        s = int(spr.width * pt["sc"])
        if s < 3:
            continue
        im = spr.resize((s, int(spr.height * pt["sc"])))
        if m[9] == "fall":
            y = (pt["y"] + pt["sp"] * lt) % (H + 200) - 100
            im = im.rotate(pt["rot"] + lt * 40, expand=True)
        else:
            y = (pt["y"] - pt["sp"] * lt) % (H + 200) - 100
        if pt["sc"] < 0.55:  # far away -> out of focus
            im = im.filter(ImageFilter.GaussianBlur(3))
        x = pt["x"] + pt["sw"] * math.sin(lt * 1.3 + pt["ph"])
        fr.alpha_composite(fade(im, 0.8 * a), (int(x - im.width / 2), int(y - im.height / 2)))


def draw_motif(fr, m, lt, a, c):
    motif, accent = m[9], m[-1]
    cx, cy = c
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if motif == "clock":
        R = 520
        d.ellipse((cx - R, cy - R, cx + R, cy + R), outline=(255, 255, 255, 150), width=6)
        for i in range(12):
            an = i * math.pi / 6
            r1 = R - (44 if i % 3 == 0 else 24)
            d.line((cx + r1 * math.sin(an), cy - r1 * math.cos(an),
                    cx + (R - 8) * math.sin(an), cy - (R - 8) * math.cos(an)),
                   fill=(255, 255, 255, 170), width=8 if i % 3 == 0 else 4)
        for L, sp, wd in [(R * 0.55, 1.2, 14), (R * 0.88, 7.5, 8)]:
            an = lt * sp
            d.line((cx, cy, cx + L * math.sin(an), cy - L * math.cos(an)), fill=(255, 255, 255, 190), width=wd)
    elif motif == "heart":
        beat = (math.sin(lt * 7) * 0.5 + 0.5) ** 4
        for i in range(3):
            r = 450 + i * 70 + beat * 40
            d.ellipse((cx - r, cy - r * 1.2, cx + r, cy + r * 1.2), outline=accent + (int(90 - i * 25),), width=10)
    else:
        for i in range(16):
            an = i * math.pi / 8 + lt * 0.25
            d.polygon([(cx, cy), (cx + 1400 * math.cos(an - 0.07), cy + 1400 * math.sin(an - 0.07)),
                       (cx + 1400 * math.cos(an + 0.07), cy + 1400 * math.sin(an + 0.07))],
                      fill=(255, 255, 255, 40))
    fr.alpha_composite(fade(lay.filter(ImageFilter.GaussianBlur(2)), a))


def poster_state(lt):
    """Return (centre, scale, pitch, yaw, alpha) of the print at local time lt."""
    t_in = ease_out(lt / 1.2)
    shrink = ease_io((lt - 3.6) / 0.8)
    t_out = ease_io((lt - (PER - 0.5)) / 0.5)
    cx = lerp(HERO_C[0], SMALL_C[0], shrink)
    cy = lerp(HERO_C[1], SMALL_C[1], shrink) + (1 - t_in) * 700 - t_out * 80
    sc = lerp(0.72, 1.0, t_in) * lerp(1.0 + 0.03 * clamp(lt / 3.6), SMALL_S, shrink)
    ax = (1 - t_in) * math.radians(58) + math.radians(4) * math.cos(lt * 0.8) * t_in - t_out * math.radians(25)
    ay = (1 - t_in) * math.radians(-18) + math.radians(7) * math.sin(lt * 0.95) * t_in
    return (cx, cy), sc, ax, ay, clamp(lt / 0.4) * (1 - t_out)


def draw_poster(fr, A, lt):
    (cx, cy), sc, ax, ay, a = poster_state(lt)
    card = A["card"].copy()
    # specular highlight follows the tilt, plus a slow drift
    ox = int(PW / 2 - ay * 900 + 120 * math.sin(lt * 0.6))
    oy = int(PH / 2 + ax * 900)
    ox, oy = max(0, min(PW, ox)), max(0, min(PH, oy))
    spec = ImageChops.multiply(SPEC.crop((ox, oy, ox + PW, oy + PH)), A["mask"])
    hl = Image.new("RGBA", (PW, PH), (255, 255, 255, 0))
    hl.putalpha(spec)
    card.alpha_composite(hl)
    proj = project(card, ax, ay, sc)
    # shadow matched to the projected shape, offset by tilt
    al = proj.getchannel("A").resize((proj.width // 8, proj.height // 8))
    al = al.filter(ImageFilter.GaussianBlur(5)).resize(proj.size, Image.BILINEAR)
    sh = Image.new("RGBA", proj.size, (35, 15, 15, 0))
    sh.putalpha(al.point(lambda v: int(v * 0.55 * a)))
    px, py = int(cx - proj.width / 2), int(cy - proj.height / 2)
    fr.alpha_composite(sh, (px + int(-ay * 160), py + 40 + int(ax * 60)))
    fr.alpha_composite(fade(proj, a), (px, py))
    # numeral pinned to the print's top-left corner
    p = back_out((lt - 0.6) / 0.6)
    if p > 0:
        n = A["num"]
        k = max(0.05, p) * (0.95 if sc > 0.9 else 0.8)
        nim = n.resize((int(n.width * k), int(n.height * k)), Image.BICUBIC)
        left, top = cx - PW * sc / 2, cy - PH * sc / 2
        fr.alpha_composite(fade(nim, a), (int(left - nim.width * 0.42), int(top - nim.height * 0.30)))


def frosted(fr, box, a):
    x0, y0, x1, y1 = box
    region = fr.crop(box).filter(ImageFilter.GaussianBlur(22))
    region = Image.blend(region, Image.new("RGBA", region.size, (255, 255, 255, 255)), 0.55)
    m = Image.new("L", region.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, region.width - 1, region.height - 1), 40, fill=int(255 * a))
    fr.paste(region, (x0, y0), m)
    edge = Image.new("RGBA", region.size, (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle((1, 1, region.width - 2, region.height - 2), 40,
                                           outline=(255, 255, 255, int(200 * a)), width=3)
    fr.alpha_composite(edge, (x0, y0))


def draw_info(fr, m, lt):
    rank, key, title, year, cast, genres, _imdb, desc, _, _, accent = m
    t0 = 4.0
    pin = ease_out((lt - t0) / 0.6)
    a_out = 1 - ease_io((lt - (PER - 0.5)) / 0.5)
    if pin <= 0:
        return
    dy = int((1 - pin) * 420)
    x0, y0, x1, y1 = PANEL
    frosted(fr, (x0, y0 + dy, x1, y1 + dy), pin * a_out)
    lay = Image.new("RGBA", (W, y1 - y0), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    tf = font("InterDisplay-Black", 92 if len(title) < 12 else 84)
    words = title.split()
    widths = [d.textlength(w_, font=tf) for w_ in words]
    gap = d.textlength(" ", font=tf)
    x = (W - sum(widths) - gap * (len(words) - 1)) / 2
    for i, (w_, ww) in enumerate(zip(words, widths)):
        p = ease_out((lt - t0 - 0.3 - i * 0.12) / 0.5)
        if p > 0:
            wl = Image.new("RGBA", (int(ww) + 20, 130), (0, 0, 0, 0))
            ImageDraw.Draw(wl).text((0, 0), w_, font=tf, fill=INK)
            lay.alpha_composite(fade(wl, p), (int(x), int(26 + 40 * (1 - p))))
        x += ww + gap
    p = ease_out((lt - t0 - 0.6) / 0.5)
    if p > 0:
        cl = Image.new("RGBA", (W, 50), (0, 0, 0, 0))
        ImageDraw.Draw(cl).text((W / 2, 0), f"{year}  ·  {cast}", font=font("Inter-SemiBold", 31), fill=SOFT, anchor="ma")
        lay.alpha_composite(fade(cl, p), (0, 138))
    cf = font("Inter-Bold", 29)
    cw = [d.textlength(g, font=cf) + 46 for g in genres]
    x = (W - sum(cw) - 16 * (len(cw) - 1)) / 2
    for i, (g, w_) in enumerate(zip(genres, cw)):
        p = back_out((lt - t0 - 0.8 - i * 0.1) / 0.45)
        if p > 0:
            chp = Image.new("RGBA", (int(w_) + 4, 56), (0, 0, 0, 0))
            cd = ImageDraw.Draw(chp)
            cd.rounded_rectangle((0, 0, w_, 52), 26, fill=accent + (255,))
            cd.text((w_ / 2, 26), g, font=cf, fill="white", anchor="mm")
            s = max(0.05, p)
            chp = chp.resize((max(1, int(chp.width * s)), max(1, int(chp.height * s))))
            lay.alpha_composite(fade(chp, clamp(p)), (int(x + w_ / 2 - chp.width / 2), int(192 + 26 - chp.height / 2)))
        x += w_ + 16
    df = font("Inter-Medium", 34)
    lines = wrap(d, desc, df, x1 - x0 - 110)
    n = int(len(desc) * clamp((lt - t0 - 1.0) / 1.8))
    shown, y = 0, 272
    for ln in lines:
        take = max(0, min(len(ln), n - shown))
        d.text((x0 + 55, y), ln[:take], font=df, fill=INK)
        shown += len(ln) + 1
        y += 47
    fr.alpha_composite(fade(lay, pin * a_out), (0, y0 + dy))


def draw_header(fr, idx, a):
    lay = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    spaced(d, W / 2, 62, "FEEL-GOOD MOVIES — PART 1", font("Inter-Bold", 32), INK, 5)
    for i in range(5):
        x0 = W / 2 - 2 * 70 + i * 70
        col = INK if i <= idx else (255, 255, 255, 170)
        d.rounded_rectangle((x0 - 26, 120, x0 + 26, 128), 4, fill=col)
    fr.alpha_composite(fade(lay, a))


def light_leak(fr, p, accent):
    if p <= 0 or p >= 1:
        return
    lay = Image.new("RGBA", (W // 4, H // 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    x = -200 + p * (W // 4 + 400)
    col = tuple(int(c * 0.4 + 255 * 0.6) for c in accent)
    s = int(255 * math.sin(p * math.pi))
    d.ellipse((x - 220, -100, x + 220, H // 4 + 100), fill=col + (s,))
    d.ellipse((x - 90, 80, x + 90, H // 4 - 80), fill=(255, 250, 240, s))
    fr.alpha_composite(lay.filter(ImageFilter.GaussianBlur(40)).resize((W, H), Image.BILINEAR))


# ------------------------------------------------------------------ intro / outro
_g = np.linspace(0, 1, H)[:, None, None]
BASE_BG = Image.fromarray(((np.array([255, 246, 236]) * (1 - _g) + np.array([255, 208, 196]) * _g)
                           .repeat(W, 1)).astype(np.uint8)).convert("RGBA")
THUMBS = [A["card"].resize((300, 444), Image.LANCZOS) for A in ASSETS]
HEART = emoji("💖", 120)
POINT = emoji("👇", 100)
POPCORN = emoji("🍿", 110)
TSH, _ = soft_shadow(300, 444, 18, blur=18, op=90)


def draw_fan(fr, t, y, alpha):
    n = len(THUMBS)
    for i, th in enumerate(THUMBS):
        p = back_out((t - 0.15 * i) / 0.7)
        if p <= 0:
            continue
        k = i - (n - 1) / 2
        ang = -k * 11 * p
        x = W / 2 + k * 165 * p
        yy = y + abs(k) * 34 * p + (1 - clamp(p)) * 300
        im = th.rotate(ang, expand=True, resample=Image.BICUBIC)
        sh = TSH.rotate(ang, expand=True)
        fr.alpha_composite(fade(sh, alpha * clamp(p)), (int(x - sh.width / 2), int(yy - sh.height / 2 + 16)))
        fr.alpha_composite(fade(im, alpha * clamp(p)), (int(x - im.width / 2), int(yy - im.height / 2)))


def text_line(fr, t, start, y, txt, f, col, a=1.0):
    p = ease_out((t - start) / 0.6)
    if p <= 0:
        return
    lay = Image.new("RGBA", (W, 170), (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((W / 2, 0), txt, font=f, fill=col, anchor="ma")
    fr.alpha_composite(fade(lay, p * a), (0, int(y + 40 * (1 - p))))


def draw_intro(fr, t):
    a = 1 - ease_io((t - (INTRO - 0.5)) / 0.5)
    text_line(fr, t, 0.1, 300, "Bad day?", font("InterDisplay-SemiBoldItalic", 70), SOFT, a)
    text_line(fr, t, 0.4, 410, "5 movies that will make", font("InterDisplay-Bold", 68), INK, a)
    text_line(fr, t, 0.6, 500, "you believe in love", font("InterDisplay-Black", 92), (214, 84, 104), a)
    text_line(fr, t, 0.8, 610, "again", font("InterDisplay-Black", 92), (214, 84, 104), a)
    draw_fan(fr, t - 1.0, 1130, a)
    p = back_out((t - 2.2) / 0.5)
    if p > 0:
        hb = HEART.resize((max(1, int(120 * p)), max(1, int(120 * p))))
        fr.alpha_composite(fade(hb, a), (int(W / 2 - hb.width / 2), int(1500 - hb.height / 2)))


def draw_outro(fr, t):
    fr.alpha_composite(fade(POPCORN, ease_out(t / 0.5)), (int(W / 2 - POPCORN.width / 2), 280))
    text_line(fr, t, 0.2, 430, "Which one made", font("InterDisplay-Bold", 78), INK)
    text_line(fr, t, 0.4, 530, "you smile?", font("InterDisplay-Black", 108), (214, 84, 104))
    text_line(fr, t, 0.9, 680, "Tell us in the comments", font("Inter-Medium", 46), SOFT)
    p = ease_out((t - 1.2) / 0.5)
    if p > 0:
        fr.alpha_composite(fade(POINT, p), (int(W / 2 - POINT.width / 2), int(760 + 12 * math.sin(t * 5))))
    if t > 1.2:
        draw_fan(fr, t - 1.2, 1130, 1.0)
    p = ease_out((t - 2.4) / 0.6)
    if p > 0:
        lay = Image.new("RGBA", (W, 260), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        d.rounded_rectangle((200, 10, W - 200, 120), 55, fill=(214, 84, 104))
        d.text((W / 2, 65), f"Follow {CHANNEL}", font=font("InterDisplay-Bold", 50), fill="white", anchor="mm")
        d.text((W / 2, 170), "Save this for your next movie night", font=font("Inter-SemiBold", 36), fill=SOFT, anchor="ma")
        fr.alpha_composite(fade(lay, p), (0, int(1440 + 30 * (1 - p))))


# ------------------------------------------------------------------ music
def make_music(path, dur, sr=44100):
    """Original upbeat, soft-beat pop: 112 bpm, G-D-Em-C, marimba hook."""
    n = int(dur * sr)
    L = np.zeros(n)
    R = np.zeros(n)
    beat = 60 / 118
    bar = 4 * beat
    note = lambda m_: 440 * 2 ** ((m_ - 69) / 12)
    noise = np.random.default_rng(1).standard_normal(int(0.3 * sr))

    def add(sig, start, vol, pan=0.0):
        s = int(start * sr)
        if s >= n:
            return
        sig = sig[: n - s]
        L[s:s + len(sig)] += sig * vol * (1 - max(pan, 0))
        R[s:s + len(sig)] += sig * vol * (1 + min(pan, 0))

    def env(length, decay, attack=0.004):
        tt = np.arange(int(length * sr)) / sr
        return tt, np.exp(-tt * decay) * np.minimum(1, tt / attack)

    tt, e = env(0.35, 14)
    KICK = np.sin(2 * np.pi * (48 * tt + 70 * (1 - np.exp(-tt * 30)) / 30)) * e
    c = noise[: int(0.18 * sr)]
    c = np.diff(c, prepend=0)
    CLAP = c * np.exp(-np.arange(len(c)) / sr * 28)
    h = np.diff(np.diff(noise[: int(0.06 * sr)], prepend=0), prepend=0)
    HAT = h * np.exp(-np.arange(len(h)) / sr * 70)
    SHAKER = h * np.exp(-np.arange(len(h)) / sr * 40) * np.minimum(1, np.arange(len(h)) / (0.015 * sr))

    def pluck(m_, length=0.35, decay=9):
        tt, e = env(length, decay)
        f = note(m_)
        return e * (np.sin(2 * np.pi * f * tt) + 0.45 * np.sin(4 * np.pi * f * tt) + 0.2 * np.sin(6 * np.pi * f * tt))

    def marimba(m_):
        tt, e = env(0.6, 7)
        f = note(m_)
        return e * (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * 4 * f * tt) * np.exp(-tt * 25))

    def bass(m_, length):
        tt, e = env(length, 5, 0.01)
        f = note(m_)
        return e * (np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt))

    # G, D, Em, C  (root, triad)
    prog = [(43, [67, 71, 74]), (38, [66, 69, 74]), (40, [67, 71, 76]), (36, [64, 67, 72])]
    hook = [(0, 79), (0.5, 76), (1, 74), (1.5, 76), (2.5, 79), (3, 81),
            (4, 78), (4.5, 76), (5, 74), (6, 74), (6.5, 76), (7, 78)]
    nbars = int(dur / bar) + 1
    for b in range(nbars):
        t0 = b * bar
        root, triad = prog[b % 4]
        intro = b < 2
        for k in range(8):  # offbeat ukulele-ish chord stabs + 8th hats
            tk = t0 + k * beat / 2
            if k % 2 == 1:
                for j, m_ in enumerate(triad):
                    add(pluck(m_, 0.28, 12), tk + j * 0.008, 0.05, pan=-0.3 + 0.3 * j)
            add(HAT, tk, 0.05 if k % 2 else 0.03, pan=0.35)
            add(SHAKER, tk + beat / 4, 0.025, pan=-0.35)
        if not intro:
            for k in range(4):
                add(KICK, t0 + k * beat, 0.38)
            add(KICK, t0 + 2.5 * beat, 0.22)
            add(CLAP, t0 + beat, 0.11)
            add(CLAP, t0 + 3 * beat, 0.11)
            for pos, ln in [(0, 0.6), (1.5, 0.3), (2, 0.6), (3.5, 0.3)]:  # bouncy bass
                add(bass(root + (12 if pos == 1.5 else 0), ln * beat * 2), t0 + pos * beat, 0.24)
            if b % 8 < 4 or b >= 4:  # marimba hook over 2 bars
                for pos, m_ in hook:
                    if (b % 2) * 4 <= pos < (b % 2) * 4 + 4:
                        add(marimba(m_), t0 + (pos - (b % 2) * 4) * beat, 0.09, pan=0.15)
        else:
            add(bass(root, bar), t0, 0.14)
    st = np.stack([L, R], 1)
    st[: int(0.5 * sr)] *= np.linspace(0, 1, int(0.5 * sr))[:, None]
    st[-int(2.5 * sr):] *= np.linspace(1, 0, int(2.5 * sr))[:, None]
    st = np.tanh(st / np.max(np.abs(st)) * 1.2) * 0.62  # gentle glue, not loud
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(sr)
        wf.writeframes((st * 32767).astype(np.int16).tobytes())


# ------------------------------------------------------------------ render
def compose(t):
    if t < INTRO:
        fr = BASE_BG.copy()
        draw_intro(fr, t)
        return fr
    lt_all = t - INTRO
    idx = int(lt_all // PER)
    if idx >= 5:
        fr = BASE_BG.copy()
        ot = lt_all - 5 * PER
        draw_outro(fr, ot)
        light_leak(fr, ot / 0.7, MOVIES[4][-1])
        return fr
    lt = lt_all - idx * PER
    m, A = MOVIES[idx], ASSETS[idx]
    bg = A["bg"]
    z = 1 + 0.06 * lt / PER
    bw, bh = int(W * z), int(H * z)
    cx, cy = (bg.width - bw) // 2, (bg.height - bh) // 2
    fr = bg.crop((cx, cy, cx + bw, cy + bh)).resize((W, H), Image.BILINEAR)
    c, *_ = poster_state(lt)
    draw_motif(fr, m, lt, ease_out((lt - 0.3) / 0.8), c)
    draw_particles(fr, m, A, lt, ease_out((lt - 0.4) / 0.8))
    draw_header(fr, idx, 1)
    draw_poster(fr, A, lt)
    draw_info(fr, m, lt)
    a = ease_out(lt / 0.35) * (1 - ease_io((lt - (PER - 0.3)) / 0.3))
    if a < 1:
        fr.alpha_composite(Image.new("RGBA", (W, H), (255, 246, 236, int(255 * (1 - a)))))
    light_leak(fr, (lt - (PER - 0.6)) / 1.2, m[-1])
    if lt < 0.6:
        prev = MOVIES[idx - 1][-1] if idx else (214, 84, 104)
        light_leak(fr, (lt + 0.6) / 1.2, prev)
    return fr


def render(t, fi=0):
    arr = np.asarray(compose(t).convert("RGB"), dtype=np.float32)
    arr = arr * VIGN + GRAIN[fi % len(GRAIN)]
    return np.clip(arr, 0, 255).astype(np.uint8)


def main():
    wav = os.path.join(HERE, "music.wav")
    make_music(wav, R_DURATION)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
           "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-tune", "film", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = int(R_DURATION * FPS)
    for fi in range(total):
        proc.stdin.write(render(design_t(fi / FPS), fi).tobytes())
        if fi % 200 == 0:
            print(f"frame {fi}/{total}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("wrote", OUT)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "preview":
        ts = [float(x) for x in sys.argv[2:]] or [2.8, INTRO + 0.6, INTRO + 2.5, INTRO + 7.5,
                                                  INTRO + PER * 2 + 7.5, INTRO + PER * 4 + 3, DURATION - 1.5]
        for x in ts:
            Image.fromarray(render(x)).save(os.path.join(HERE, f"preview_{x:.1f}.png"))
        print("ok")
    elif len(sys.argv) > 1 and sys.argv[1] == "music":
        make_music(os.path.join(HERE, "music.wav"), R_DURATION)
        print("music ok")
    else:
        main()
