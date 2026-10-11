"""Filmy Passport - minimal international-style logo options (800x800)."""
import math
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/opentype/inter/"
INKBG = (14, 16, 30)
CREAM = (246, 239, 228)
CORAL = (232, 72, 85)
GOLD = (232, 182, 92)
SS = 4  # supersampling
N = 800


def font(n, s):
    return ImageFont.truetype(FD + n + ".otf", s)


def canvas(bg=INKBG):
    return Image.new("RGB", (N * SS, N * SS), bg)


def done(im, name):
    im = im.resize((N, N), Image.LANCZOS)
    im.save(os.path.join(HERE, name))
    return im


def rounded_triangle(d, cx, cy, r, fill, rot=0.0, round_px=0):
    """Play triangle centred (by centroid) at cx,cy with circumradius r."""
    pts = [(cx + r * math.cos(rot + k * 2 * math.pi / 3), cy + r * math.sin(rot + k * 2 * math.pi / 3)) for k in range(3)]
    d.polygon(pts, fill=fill)
    if round_px:
        d.line(pts + [pts[0]], fill=fill, width=round_px, joint="curve")


# ---------------------------------------------------------------- A: FP monogram
def option_a():
    im = canvas()
    d = ImageDraw.Draw(im)
    k = SS
    s = 78 * k                       # stroke
    top, bot = 200 * k, 600 * k
    ox = 175 * k
    # F
    d.rectangle((ox, top, ox + s, bot), fill=CREAM)
    d.rectangle((ox, top, ox + 205 * k, top + s), fill=CREAM)
    d.rectangle((ox, top + 165 * k, ox + 170 * k, top + 165 * k + s), fill=CREAM)
    # P
    px = ox + 255 * k
    bowl_h = 290 * k
    R = bowl_h / 2
    d.rectangle((px, top, px + s, bot), fill=CREAM)
    d.rectangle((px, top, px + 95 * k, top + bowl_h), fill=CREAM)
    d.pieslice((px + 95 * k - R, top, px + 95 * k + R, top + bowl_h), -90, 90, fill=CREAM)
    # counter (hole) + play triangle inside it
    ri = R - s
    d.rectangle((px + s, top + s, px + 95 * k, top + bowl_h - s), fill=INKBG)
    d.pieslice((px + 95 * k - ri, top + s, px + 95 * k + ri, top + bowl_h - s), -90, 90, fill=INKBG)
    cx, cy = px + s + 34 * k, top + R
    rounded_triangle(d, cx, cy, 36 * k, CORAL, 0, 6 * k)
    return done(im, "logo_option_A_monogram.png")


# ---------------------------------------------------------------- B: globe + play
def option_b():
    im = canvas()
    d = ImageDraw.Draw(im)
    k = SS
    c = N * k / 2
    R = 255 * k
    w = 26 * k
    d.ellipse((c - R, c - R, c + R, c + R), outline=CREAM, width=w)
    for f in (0.42,):
        d.ellipse((c - R * f, c - R, c + R * f, c + R), outline=CREAM, width=w)
    hw = R * math.sqrt(1 - 0.5 ** 2) - w * 0.6
    for yy in (-0.5, 0.5):
        d.line((c - hw, c + yy * R, c + hw, c + yy * R), fill=CREAM, width=w)
    # play badge with knockout ring
    pr = 118 * k
    d.ellipse((c - pr - 22 * k, c - pr - 22 * k, c + pr + 22 * k, c + pr + 22 * k), fill=INKBG)
    d.ellipse((c - pr, c - pr, c + pr, c + pr), fill=CORAL)
    rounded_triangle(d, c + 10 * k, c, 62 * k, CREAM, 0, 10 * k)
    return done(im, "logo_option_B_globe.png")


# ---------------------------------------------------------------- C: stamp seal
def option_c():
    im = canvas()
    d = ImageDraw.Draw(im)
    k = SS
    c = N * k / 2
    R1, R2 = 330 * k, 228 * k
    d.ellipse((c - R1, c - R1, c + R1, c + R1), outline=GOLD, width=12 * k)
    d.ellipse((c - R2, c - R2, c + R2, c + R2), outline=GOLD, width=6 * k)
    f = font("InterDisplay-Bold", 50 * k)
    rr = (R1 + R2) / 2

    def arc(txt, centre_deg, top):
        sp = 1.22
        widths = [d.textlength(ch, font=f) * sp for ch in txt]
        span = sum(widths) / rr
        ang = math.radians(centre_deg) + (-span / 2 if top else span / 2)
        for ch, cw in zip(txt, widths):
            a = ang + (cw / 2 / rr) * (1 if top else -1)
            g = Image.new("RGBA", (90 * k, 90 * k), (0, 0, 0, 0))
            ImageDraw.Draw(g).text((45 * k, 45 * k), ch, font=f, fill=GOLD, anchor="mm")
            rot = -(math.degrees(a) + 90) if top else -(math.degrees(a) - 90)
            g = g.rotate(rot, resample=Image.BICUBIC)
            x, y = c + rr * math.cos(a), c + rr * math.sin(a)
            im.paste(g, (int(x - g.width / 2), int(y - g.height / 2)), g)
            ang += (cw / rr) * (1 if top else -1)

    arc("FILMY PASSPORT", -90, True)
    arc("WORLD CINEMA", 90, False)
    for deg in (180, 0):
        x, y = c + rr * math.cos(math.radians(deg)), c + rr * math.sin(math.radians(deg))
        d.ellipse((x - 10 * k, y - 10 * k, x + 10 * k, y + 10 * k), fill=GOLD)
    # centre: play triangle
    rounded_triangle(d, c + 14 * k, c, 120 * k, CORAL, 0, 16 * k)
    return done(im, "logo_option_C_stamp.png")


def sheet(opts):
    W, H = 1800, 860
    P = Image.new("RGB", (W, H), (246, 245, 242))
    d = ImageDraw.Draw(P)
    labels = ["A · Monogram", "B · Globe", "C · Stamp seal"]
    for i, im in enumerate(opts):
        x0 = 60 + i * 590
        m = Image.new("L", (440, 440), 0)
        ImageDraw.Draw(m).ellipse((0, 0, 439, 439), fill=255)
        P.paste(im.resize((440, 440), Image.LANCZOS), (x0 + 15, 40), m)
        d.text((x0 + 235, 520), labels[i], font=font("InterDisplay-Bold", 40), fill=(20, 20, 20), anchor="mm")
        x = x0 + 60
        for s in (98, 64, 40):
            mm = Image.new("L", (s, s), 0)
            ImageDraw.Draw(mm).ellipse((0, 0, s - 1, s - 1), fill=255)
            P.paste(im.resize((s, s), Image.LANCZOS), (x, 600 + (98 - s) // 2), mm)
            x += s + 40
        d.text((x0 + 235, 760), "as seen next to video titles", font=font("Inter-Medium", 24), fill=(120, 120, 120), anchor="mm")
    P.save(os.path.join(HERE, "logo_options.png"))


if __name__ == "__main__":
    sheet([option_a(), option_b(), option_c()])
    print("done")
