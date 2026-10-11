"""Filmy Passport - logo (800x800), banner (2560x1440) and video watermark (300x300)."""
import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"

NAVY = (28, 32, 74)
NAVY2 = (44, 40, 110)
CORAL = (226, 88, 104)
SAFFRON = (255, 170, 60)
GOLD = (246, 200, 110)
CREAM = (255, 244, 232)


def font(n, s):
    return ImageFont.truetype(FD + n + ".otf", s)


def grad(w, h, c1, c2, diagonal=True):
    y, x = np.mgrid[0:h, 0:w]
    t = ((x / w + y / h) / 2) if diagonal else (y / h)
    t = t[..., None]
    arr = np.array(c1) * (1 - t) + np.array(c2) * t
    return Image.fromarray(arr.astype(np.uint8), "RGB").convert("RGBA")


def spaced(d, cx, y, txt, f, fill, sp, anchor_mid=True):
    ws = [d.textlength(c, font=f) for c in txt]
    x = cx - (sum(ws) + sp * (len(txt) - 1)) / 2
    for c, w in zip(txt, ws):
        d.text((x, y), c, font=f, fill=fill, anchor="lm" if anchor_mid else "la")
        x += w + sp


def shadow_of(img, blur, op, offset=(0, 12)):
    a = img.getchannel("A").point(lambda v: int(v * op))
    sh = Image.new("RGBA", img.size, (20, 10, 30, 0))
    sh.putalpha(a)
    pad = blur * 3
    out = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    out.alpha_composite(sh, (pad + offset[0], pad + offset[1]))
    return out.filter(ImageFilter.GaussianBlur(blur)), pad


def emblem(size, line=GOLD):
    """Globe made of meridians/parallels with a play button in the middle."""
    S = size * 4  # supersample
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c, r, w = S / 2, S * 0.46, max(4, int(S * 0.028))
    d.ellipse((c - r, c - r, c + r, c + r), outline=line, width=w)
    for k in (0.38, 0.75):  # meridians
        d.ellipse((c - r * k, c - r, c + r * k, c + r), outline=line, width=w)
    for yy in (-0.5, 0.5):  # parallels
        hw = r * math.sqrt(1 - yy ** 2)
        d.line((c - hw, c + yy * r, c + hw, c + yy * r), fill=line, width=w)
    d.line((c - r, c, c + r, c), fill=line, width=w)
    # play badge
    pr = r * 0.42
    d.ellipse((c - pr, c - pr, c + pr, c + pr), fill=CORAL, outline=line, width=w)
    tri = [(c - pr * 0.32, c - pr * 0.48), (c - pr * 0.32, c + pr * 0.48), (c + pr * 0.55, c)]
    d.polygon(tri, fill=CREAM)
    return im.resize((size, size), Image.LANCZOS)


def passport(w, h):
    """Navy passport booklet with gold FILMY / emblem / PASSPORT."""
    S = 3
    im = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rad = int(w * S * 0.09)
    cover = grad(w * S, h * S, NAVY2, NAVY)
    m = Image.new("L", (w * S, h * S), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w * S - 1, h * S - 1), rad, fill=255)
    im.paste(cover, (0, 0), m)
    # spine shading + gold inner border
    d.rounded_rectangle((0, 0, int(w * S * 0.07), h * S - 1), rad, fill=(18, 20, 52, 255))
    inset = int(w * S * 0.07)
    d.rounded_rectangle((inset + 10 * S, 12 * S, w * S - 12 * S, h * S - 12 * S), int(rad * 0.6),
                        outline=GOLD + (170,), width=2 * S)
    cx = (inset + w * S) / 2
    f1 = font("InterDisplay-Black", int(h * S * 0.115))
    spaced(d, cx, h * S * 0.17, "FILMY", f1, GOLD, int(w * S * 0.02))
    e = emblem(int(w * S * 0.62))
    im.alpha_composite(e, (int(cx - e.width / 2), int(h * S * 0.50 - e.height / 2)))
    f2 = font("InterDisplay-Bold", int(h * S * 0.075))
    spaced(d, cx, h * S * 0.84, "PASSPORT", f2, GOLD, int(w * S * 0.012))
    return im.resize((w, h), Image.LANCZOS)


def stamp(txt, sub, col, size=260, rot=0):
    S = size * 2
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    d.ellipse((8, 8, S - 8, S - 8), outline=col, width=10)
    d.ellipse((34, 34, S - 34, S - 34), outline=col, width=4)
    for i in range(36):  # dotted ring
        a = i * math.tau / 36
        x, y = c + (S / 2 - 21) * math.cos(a), c + (S / 2 - 21) * math.sin(a)
        d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=col)
    f = font("InterDisplay-Black", int(S * 0.15) if len(txt) < 8 else int(S * 0.12))
    d.text((c, c - S * 0.05), txt, font=f, fill=col, anchor="mm")
    d.text((c, c + S * 0.14), sub, font=font("Inter-Bold", int(S * 0.075)), fill=col, anchor="mm")
    d.line((S * 0.22, c + S * 0.05, S * 0.78, c + S * 0.05), fill=col, width=4)
    im = im.resize((size, size), Image.LANCZOS)
    # worn-ink texture
    noise = (np.random.default_rng(len(txt)).random((size, size)) > 0.18).astype(np.uint8) * 255
    a = np.minimum(np.array(im.getchannel("A")), noise)
    im.putalpha(Image.fromarray(a))
    return im.rotate(rot, expand=True, resample=Image.BICUBIC)


# ------------------------------------------------------------------ logo
def make_logo():
    N = 800
    bg = grad(N, N, SAFFRON, CORAL)
    # soft sunburst
    ov = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    c = N / 2
    for i in range(18):
        a = i * math.tau / 18
        d.polygon([(c, c), (c + 900 * math.cos(a - 0.06), c + 900 * math.sin(a - 0.06)),
                   (c + 900 * math.cos(a + 0.06), c + 900 * math.sin(a + 0.06))], fill=(255, 255, 255, 60))
    bg.alpha_composite(ov.filter(ImageFilter.GaussianBlur(1)))
    pp = passport(400, 540).rotate(-8, expand=True, resample=Image.BICUBIC)
    sh, pad = shadow_of(pp, 18, 0.45, (10, 18))
    bg.alpha_composite(sh, (int(c - pp.width / 2) - pad, int(c - pp.height / 2) - pad))
    bg.alpha_composite(pp, (int(c - pp.width / 2), int(c - pp.height / 2)))
    out = bg.convert("RGB")
    out.save(os.path.join(HERE, "filmy_passport_logo.png"))
    # preview as YouTube shows it (circle)
    m = Image.new("L", (N, N), 0)
    ImageDraw.Draw(m).ellipse((0, 0, N, N), fill=255)
    circ = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    circ.paste(out, (0, 0), m)
    return circ


# ------------------------------------------------------------------ banner
def make_banner(logo_circle):
    BW, BH = 2560, 1440
    bg = grad(BW, BH, (34, 30, 86), (20, 22, 56))
    ov = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # faint globe grid
    gc = (BW / 2, BH / 2)
    for r in range(300, 1600, 130):
        d.ellipse((gc[0] - r * 1.4, gc[1] - r, gc[0] + r * 1.4, gc[1] + r), outline=(255, 255, 255, 16), width=2)
    bg.alpha_composite(ov)
    ov = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # warm glow behind the safe area
    glow = Image.new("RGBA", (BW, BH), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((BW / 2 - 900, BH / 2 - 330, BW / 2 + 900, BH / 2 + 330), fill=CORAL + (90,))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(160)))
    # stamps around the edges (visible on TV / desktop wide)
    stamps = [("HOLLYWOOD", "USA", GOLD, 300, 12, (250, 210)),
              ("SEOUL", "K-DRAMA", (255, 140, 160), 260, -14, (2300, 230)),
              ("PARIS", "CINÉMA", (140, 200, 255), 250, 8, (420, 1210)),
              ("TOKYO", "ANIME", (255, 200, 120), 250, -10, (2150, 1220)),
              ("LONDON", "BRIT FILMS", (180, 230, 190), 230, 18, (900, 1290)),
              ("MUMBAI", "DESI HEART", SAFFRON, 240, -6, (1700, 160))]
    for txt, sub, col, s, rot, (x, y) in stamps:
        st = stamp(txt, sub, col + (255,), s, rot)
        a = st.getchannel("A").point(lambda v: int(v * 0.55))
        st.putalpha(a)
        bg.alpha_composite(st, (int(x - st.width / 2), int(y - st.height / 2)))
    # dotted flight path with plane
    pts = [(BW * t, BH * 0.5 - math.sin(t * math.pi) * 420 + 260) for t in np.linspace(0.05, 0.95, 90)]
    for i, (x, y) in enumerate(pts):
        if i % 2 == 0 and not (880 < x < 2120 and 480 < y < 960):
            d.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(255, 255, 255, 60))
    # film strip along the bottom of the safe area
    fy = 1010
    d.rectangle((0, fy, BW, fy + 70), fill=(12, 12, 30, 200))
    for x in range(10, BW, 60):
        d.rounded_rectangle((x, fy + 10, x + 30, fy + 26), 4, fill=(255, 255, 255, 40))
        d.rounded_rectangle((x, fy + 44, x + 30, fy + 60), 4, fill=(255, 255, 255, 40))
    bg.alpha_composite(ov)

    # ---- safe area content (1546 x 423 centred) ----
    sx0, sy0 = (BW - 1546) // 2, (BH - 423) // 2
    lg = logo_circle.resize((330, 330), Image.LANCZOS)
    ring = Image.new("RGBA", (350, 350), (0, 0, 0, 0))
    ImageDraw.Draw(ring).ellipse((0, 0, 349, 349), fill=CREAM + (255,))
    ring.alpha_composite(lg, (10, 10))
    sh, pad = shadow_of(ring, 22, 0.5)
    lx, ly = sx0 + 40, sy0 + (423 - 350) // 2
    bg.alpha_composite(sh, (lx - pad, ly - pad))
    bg.alpha_composite(ring, (lx, ly))

    tx = lx + 350 + 70
    title = Image.new("RGBA", (1200, 200), (0, 0, 0, 0))
    td = ImageDraw.Draw(title)
    tf = font("InterDisplay-Black", 150)
    td.text((0, 0), "Filmy", font=tf, fill=CREAM)
    td.text((td.textlength("Filmy ", font=tf), 0), "Passport", font=tf, fill=SAFFRON)
    sh, pad = shadow_of(title, 14, 0.5, (0, 8))
    bg.alpha_composite(sh, (tx - pad, sy0 + 40 - pad))
    bg.alpha_composite(title, (tx, sy0 + 40))
    d = ImageDraw.Draw(bg)
    d.text((tx + 6, sy0 + 230), "World cinema, desi style", font=font("InterDisplay-SemiBoldItalic", 64), fill=CREAM)
    chips = ["Reviews", "Top Lists", "Hidden Gems", "New Shorts weekly"]
    x = tx + 6
    cf = font("Inter-Bold", 34)
    for i, ch in enumerate(chips):
        w = d.textlength(ch, font=cf) + 56
        if i < 3:
            d.rounded_rectangle((x, sy0 + 330, x + w, sy0 + 392), 31, fill=CORAL)
        else:
            d.rounded_rectangle((x, sy0 + 330, x + w, sy0 + 392), 31, outline=SAFFRON, width=3)
        d.text((x + w / 2, sy0 + 361), ch, font=cf, fill="white", anchor="mm")
        x += w + 18
    bg.convert("RGB").save(os.path.join(HERE, "filmy_passport_banner.png"))
    return bg


def make_watermark():
    """Small transparent-friendly mark for YouTube 'Video watermark' (min 150x150)."""
    N = 300
    pp = passport(200, 270)
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    sh, pad = shadow_of(pp, 10, 0.4, (4, 8))
    im.alpha_composite(sh, ((N - pp.width) // 2 - pad, (N - pp.height) // 2 - pad))
    im.alpha_composite(pp, ((N - pp.width) // 2, (N - pp.height) // 2))
    im.save(os.path.join(HERE, "filmy_passport_watermark.png"))


def make_preview(logo_circle, banner):
    """How it looks on a channel page: banner (desktop crop) + round logo at small sizes."""
    P = Image.new("RGB", (1600, 760), (250, 248, 246))
    crop = banner.crop((0, 508, 2560, 931)).resize((1600, 264))  # desktop-visible strip
    P.paste(crop.convert("RGB"), (0, 0))
    d = ImageDraw.Draw(P)
    P.paste(logo_circle.resize((160, 160)), (60, 310), logo_circle.resize((160, 160)))
    d.text((250, 330), "Filmy Passport", font=font("InterDisplay-Bold", 56), fill=(20, 20, 20))
    d.text((250, 405), "@FilmyPassport · World cinema, desi style", font=font("Inter-Medium", 30), fill=(96, 96, 96))
    d.text((60, 520), "Small sizes:", font=font("Inter-SemiBold", 28), fill=(96, 96, 96))
    x = 260
    for s in (98, 64, 40, 24):
        P.paste(logo_circle.resize((s, s), Image.LANCZOS), (x, 560), logo_circle.resize((s, s), Image.LANCZOS))
        x += s + 40
    P.save(os.path.join(HERE, "preview_channel.png"))


if __name__ == "__main__":
    circ = make_logo()
    ban = make_banner(circ)
    make_watermark()
    make_preview(circ, ban)
    print("done")
