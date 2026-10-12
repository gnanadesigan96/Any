"""Filmy Passport - cover/thumbnail for 'Feel-Good Movies - Part 1'.

Outputs a vertical Shorts cover (1080x1920) and a 16:9 thumbnail (1280x720).
"""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
PART = int(os.environ.get("PART", "1"))
OUT_DIR = os.environ.get("OUT_DIR", os.path.dirname(os.path.abspath(__file__)))
POSTERS = os.path.join(HERE, "..", "english", "posters")
ORDER = ["made_of_honor", "plus_one", "the_vow", "love_rosie", "about_time"]
FD = "/usr/share/fonts/opentype/inter/"
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
INK = (14, 16, 30)
CREAM = (250, 242, 230)
CORAL = (236, 78, 92)

# one colour theme per part so every cover looks different (cycles after 8)
THEMES = [(236, 78, 92), (20, 165, 160), (140, 90, 220), (245, 125, 40),
          (60, 120, 235), (30, 170, 100), (220, 60, 150), (225, 175, 40)]
ACCENT = THEMES[(PART - 1) % len(THEMES)]
ACCENT_DARK = tuple(int(c * 0.6) for c in ACCENT)
ACCENT_GLOW = tuple(int(c * 0.85) for c in ACCENT)
SAFFRON = (255, 176, 64)
GOLD = (232, 182, 92)


def font(n, s):
    return ImageFont.truetype(FD + n + ".otf", s)


def emoji(ch, size):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (180, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((90, 90), ch, font=f, embedded_color=True, anchor="mm")
    im = im.crop(im.getbbox())
    r = size / max(im.size)
    return im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)


def card(key, w, h):
    src = Image.open(os.path.join(POSTERS, key + ".jpg")).convert("RGB")
    sc = max(w / src.width, h / src.height)
    p = src.resize((int(src.width * sc), int(src.height * sc)), Image.LANCZOS).filter(ImageFilter.UnsharpMask(2, 80, 2))
    ox, oy = (p.width - w) // 2, (p.height - h) // 2
    p = p.crop((ox, oy, ox + w, oy + h)).convert("RGBA")
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), int(w * 0.045), fill=255)
    edge = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(edge).rounded_rectangle((1, 1, w - 2, h - 2), int(w * 0.045), outline=(255, 255, 255, 150), width=3)
    p.alpha_composite(edge)
    p.putalpha(m)
    return p


def card_back(label, w, h, hero=False):
    """Face-down mystery card: navy back, gold frame, rank number (or '?')."""
    S = 2
    W2, H2 = w * S, h * S
    r = int(W2 * 0.06)
    im = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    y, x = np.mgrid[0:H2, 0:W2]
    t = ((x / W2 + y / H2) / 2)[..., None]
    top, bot = (np.array((46, 40, 108)), np.array((22, 22, 54))) if not hero else (np.array(ACCENT), np.array(ACCENT_DARK))
    body = Image.fromarray((top * (1 - t) + bot * t).astype(np.uint8)).convert("RGBA")
    m = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, W2 - 1, H2 - 1), r, fill=255)
    im.paste(body, (0, 0), m)
    d = ImageDraw.Draw(im)
    gold = CREAM if hero else GOLD
    ins = int(W2 * 0.06)
    d.rounded_rectangle((ins, ins, W2 - ins, H2 - ins), int(r * 0.6), outline=gold + (200,), width=3 * S)
    # subtle diagonal pattern
    pat = Image.new("RGBA", (W2, H2), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pat)
    for k in range(-H2, W2, 26 * S):
        pd.line((k, 0, k + H2, H2), fill=(255, 255, 255, 14), width=2 * S)
    pm = Image.new("L", (W2, H2), 0)
    ImageDraw.Draw(pm).rounded_rectangle((ins + 8 * S, ins + 8 * S, W2 - ins - 8 * S, H2 - ins - 8 * S), int(r * 0.5), fill=255)
    im.paste(pat, (0, 0), Image.composite(pat.getchannel("A"), Image.new("L", (W2, H2), 0), pm))
    cx, cy = W2 / 2, H2 * 0.47
    cr = W2 * 0.3
    d.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=gold + (230,), width=4 * S)
    f = font("InterDisplay-Black", int(cr * (1.45 if label == "?" else 1.25)))
    d.text((cx, cy + (6 * S if label == "?" else 0)), label, font=f, fill=gold, anchor="mm")
    d.text((cx, H2 * 0.86), "FILMY PASSPORT", font=font("Inter-Bold", int(W2 * 0.055)), fill=gold + (200,), anchor="mm")
    return im.resize((w, h), Image.LANCZOS)


def drop_shadow(img, blur=26, op=0.6, off=(0, 22)):
    pad = blur * 3
    sh = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    a = Image.new("RGBA", img.size, (0, 0, 0, 0))
    a.putalpha(img.getchannel("A").point(lambda v: int(v * op)))
    sh.alpha_composite(a, (pad + off[0], pad + off[1]))
    return sh.filter(ImageFilter.GaussianBlur(blur)), pad


def background(W, H, glow_xy, glow_r):
    y, x = np.mgrid[0:H, 0:W]
    t = (y / H)[..., None]
    base = np.array((26, 22, 52)) * (1 - t) + np.array(INK) * t
    gx, gy = glow_xy
    dist = np.sqrt(((x - gx) / glow_r[0]) ** 2 + ((y - gy) / glow_r[1]) ** 2)[..., None]
    g = np.clip(1 - dist, 0, 1) ** 2
    base = base * (1 - g * 0.85) + np.array(ACCENT_GLOW) * g * 0.85
    im = Image.fromarray(base.astype(np.uint8)).convert("RGBA")
    # faint rays
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    for i in range(20):
        a = i * math.tau / 20
        d.polygon([(gx, gy), (gx + 3000 * math.cos(a - 0.04), gy + 3000 * math.sin(a - 0.04)),
                   (gx + 3000 * math.cos(a + 0.04), gy + 3000 * math.sin(a + 0.04))], fill=(255, 210, 180, 14))
    im.alpha_composite(ov.filter(ImageFilter.GaussianBlur(6)))
    return im


def fan(base, centre, cw, ch, spread, tilt, lift):
    """Five posters fanned like playing cards, #1 (About Time) on top in the middle."""
    order = [0, 4, 1, 3, 2]  # draw outer first; middle slot gets the best-rated
    slots = {0: -2, 1: -1, 2: 0, 3: 1, 4: 2}
    keys = ["4", "2", "?", "3", "5"]  # left -> right; the #1 stays a mystery
    for i in [0, 4, 1, 3, 2]:
        k = slots[i]
        scale = 1.0 if k == 0 else (0.9 if abs(k) == 1 else 0.8)
        c = card_back(keys[i], int(cw * scale), int(ch * scale), hero=(k == 0)).rotate(-k * tilt, expand=True, resample=Image.BICUBIC)
        x = centre[0] + k * spread
        y = centre[1] + abs(k) * lift
        sh, pad = drop_shadow(c)
        base.alpha_composite(sh, (int(x - c.width / 2) - pad, int(y - c.height / 2) - pad))
        base.alpha_composite(c, (int(x - c.width / 2), int(y - c.height / 2)))


def spaced(d, cx, y, txt, f, fill, sp):
    ws = [d.textlength(c, font=f) for c in txt]
    x = cx - (sum(ws) + sp * (len(txt) - 1)) / 2
    for c, w in zip(txt, ws):
        d.text((x, y), c, font=f, fill=fill)
        x += w + sp


def text_shadow(base, xy, txt, f, fill, anchor="ma", blur=12):
    lay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).text((xy[0], xy[1] + 8), txt, font=f, fill=(0, 0, 0, 170), anchor=anchor)
    base.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))
    ImageDraw.Draw(base).text(xy, txt, font=f, fill=fill, anchor=anchor)


def pill(base, cx, cy, txt, f, fill, fg, padx=46, h=None):
    d = ImageDraw.Draw(base)
    w = d.textlength(txt, font=f) + padx * 2
    h = h or int(f.size * 1.6)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h // 2, fill=fill)
    d.text((cx, cy), txt, font=f, fill=fg, anchor="mm")


def vertical():
    W, H = 1080, 1920
    im = background(W, H, (W / 2, 1180), (900, 760))
    d = ImageDraw.Draw(im)
    spaced(d, W / 2, 150, "FILMY PASSPORT", font("Inter-Bold", 36), GOLD, 10)
    text_shadow(im, (W / 2, 230), "FEEL-GOOD", font("InterDisplay-Black", 164), CREAM)
    text_shadow(im, (W / 2, 405), "MOVIES", font("InterDisplay-Black", 222), ACCENT)
    pill(im, W / 2, 735, f"PART {PART}", font("InterDisplay-Black", 82), SAFFRON, INK, padx=60, h=132)
    fan(im, (W / 2, 1190), 420, 622, 180, 9, 46)
    heart = emoji("💖", 96)
    im.alpha_composite(heart, (int(W / 2 + 250), 905))
    text_shadow(im, (W / 2, 1590), "5 English movies that make you", font("InterDisplay-Bold", 54), CREAM)
    text_shadow(im, (W / 2, 1668), "believe in love again", font("InterDisplay-BoldItalic", 62), SAFFRON)
    out = os.path.join(OUT_DIR, f"thumbnail_feel_good_part{PART}_vertical.png")
    im.convert("RGB").save(out)
    return out


def landscape():
    W, H = 1280, 720
    im = background(W, H, (900, 380), (620, 480))
    fan(im, (985, 395), 240, 355, 108, 9, 24)
    d = ImageDraw.Draw(im)
    x0 = 70
    d.text((x0 + 4, 92), "FILMY PASSPORT", font=font("Inter-Bold", 26), fill=GOLD)
    text_shadow(im, (x0, 140), "FEEL-GOOD", font("InterDisplay-Black", 118), CREAM, anchor="la")
    text_shadow(im, (x0, 262), "MOVIES", font("InterDisplay-Black", 150), ACCENT, anchor="la")
    f = font("InterDisplay-Black", 40)
    w = d.textlength(f"PART {PART}", font=f) + 64
    d.rounded_rectangle((x0 + 4, 448, x0 + 4 + w, 512), 32, fill=SAFFRON)
    d.text((x0 + 4 + w / 2, 480), f"PART {PART}", font=f, fill=INK, anchor="mm")
    text_shadow(im, (x0 + 4, 548), "5 English movies that make you", font("InterDisplay-Bold", 38), CREAM, anchor="la", blur=8)
    text_shadow(im, (x0 + 4, 598), "believe in love again", font("InterDisplay-BoldItalic", 40), SAFFRON, anchor="la", blur=8)
    out = os.path.join(OUT_DIR, f"thumbnail_feel_good_part{PART}_16x9.png")
    im.convert("RGB").save(out)
    return out


if __name__ == "__main__":
    print(vertical())
    print(landscape())
