"""Usage: python stories/clean_posters.py <originals dir> <out dir>

Removes extra wording (logos, dates, taglines, credits) from the posters, keeping the artwork and the film's own
title, and rebuilds the bottom band with just the film's name."""
import sys, glob, time
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont

SRC, OUT = Path(sys.argv[1]), Path(sys.argv[2])
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
# (x0, y0, x1, y1, mode): "s" = remove only the letters inside the box, "f" = fill the whole box (solid logos/badges)
BOXES = {
 "01": [(395,55,830,115,"s"),(245,195,960,275,"s"),(515,385,705,435,"s"),(370,625,810,665,"s")],
 "02": [(0,0,215,80,"s"),(270,5,830,60,"s"),(5,90,125,210,"f"),(870,10,1185,225,"f"),(285,1055,835,1125,"s"),
        (370,1125,710,1255,"s"),(790,1485,855,1545,"f"),(955,1385,1115,1545,"f"),(370,1530,750,1600,"s")],
 "03": [(370,385,1110,435,"s"),(100,430,1140,478,"s")],
 "04": [],
 "05": [(0,0,160,190,"s"),(980,55,1200,190,"s"),(495,1130,735,1240,"s")],
 "06": [(0,15,190,180,"s"),(1145,15,1200,165,"s"),(155,210,435,360,"s"),(990,190,1200,470,"f"),(495,1510,725,1595,"s")],
 "07": [(0,1235,415,1475,"f")],
 "08": [(40,40,345,190,"s"),(710,40,1150,140,"s")],
 "09": [(0,5,290,180,"f"),(1025,35,1200,165,"s"),(975,235,1200,425,"s"),(0,795,315,995,"s"),(315,1515,960,1600,"s")],
 "10": [(475,20,725,260,"s")],
 "11": [(130,180,260,280,"x"),(850,165,1085,285,"s"),(640,425,840,475,"s"),
        (530,1090,712,1378,"g"),(110,1395,1090,1600,"s")],
 "12": [(35,5,315,105,"s"),(815,5,1175,105,"s"),(845,1140,1135,1370,"s"),(380,1435,520,1490,"s"),(345,1410,535,1445,"s")],
 "13": [], "14": [(395,1295,845,1350,"s")], "15": [], "16": [],
 "17": [(20,50,185,165,"f"),(0,175,295,260,"s"),(1025,45,1200,115,"s"),(925,1520,1165,1585,"s")],
}
TITLES = {"01": "Raatchasi", "02": "Imaikkaa Nodigal", "03": "Maanagaram", "04": "Thegidi",
          "05": "Onaayum Aattukkuttiyum", "06": "Maayavan", "07": "Aaranya Kaandam", "08": "Dhuruvangal Pathinaaru",
          "09": "Pizza 2: Villa", "10": "Sathuranga Vettai", "11": "Mundasupatti", "12": "Maya",
          "13": "Demonte Colony", "14": "Aruvi", "15": "Meyaadha Maan", "16": "Taramani", "17": "Yuddham Sei"}
BAND_TOP = 1590

def blank_badge(im, x0, y0, x1, y1):
    """Turns a text badge into a plain gold plaque: each row gets the median of its own gold pixels."""
    roi = im[y0:y1, x0:x1]
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    gold = (hsv[..., 0] > 12) & (hsv[..., 0] < 35) & (hsv[..., 1] > 90) & (hsv[..., 2] > 110)
    rows = np.full((y1 - y0, 3), np.nan)
    for i in range(y1 - y0):
        if gold[i].sum() > 8:
            rows[i] = np.median(roi[i][gold[i]], 0)
    for c in range(3):
        v = rows[:, c]; ok = ~np.isnan(v)
        rows[:, c] = np.interp(np.arange(len(v)), np.flatnonzero(ok), v[ok])
    rows = cv2.GaussianBlur(rows[:, None, :].astype(np.float32), (1, 0), 9)[:, 0]
    fill = np.repeat(rows[:, None, :], x1 - x0, 1)
    fill += np.random.default_rng(1).normal(0, 4, fill.shape)
    im[y0:y1, x0:x1] = np.clip(fill, 0, 255).astype(np.uint8)
    return im


def text_mask(img, x0, y0, x1, y1, mode):
    m = np.zeros(img.shape[:2], np.uint8)
    if mode == "g":
        return m
    if mode in "fx":
        m[y0:y1, x0:x1] = 255
        return m
    roi = cv2.cvtColor(img[y0:y1, x0:x1], cv2.COLOR_BGR2GRAY).astype(np.int16)
    k = max(31, (min(y1 - y0, x1 - x0) // 2) | 1)
    bg = cv2.medianBlur(img[y0:y1, x0:x1], min(k, 255) if min(k, 255) % 2 else min(k, 255) - 1)
    bg = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY).astype(np.int16)
    letters = (np.abs(roi - bg) > 28).astype(np.uint8) * 255
    letters = cv2.dilate(letters, np.ones((7, 7), np.uint8))
    m[y0:y1, x0:x1] = letters
    return m


def clean(path):
    n = path.name[:2]
    img = cv2.imread(str(path))
    mask = np.zeros(img.shape[:2], np.uint8)
    for b in BOXES[n]:
        mask |= text_mask(img, *b)
    for b in BOXES[n]:
        if b[4] == "g":
            blank_badge(img, *b[:4])
    xm = np.zeros_like(mask)
    for b in BOXES[n]:
        if b[4] == "x":
            xm |= text_mask(img, *b)
    mask &= ~xm
    if xm.any():  # big solid badges: exemplar-based fill copies real texture instead of smearing
        out = np.zeros_like(img)
        cv2.xphoto.inpaint(img, 255 - xm, out, cv2.xphoto.INPAINT_FSR_FAST)
        img = out
    if mask.any():
        img = cv2.inpaint(img, mask, 9, cv2.INPAINT_TELEA)
        # Smooth the filled patches a little so they blend with the surrounding grain.
        soft = cv2.GaussianBlur(img, (0, 0), 2.2)
        m3 = cv2.GaussianBlur(mask, (0, 0), 3)[..., None] / 255.0
        img = (img * (1 - m3) + soft * m3).astype(np.uint8)
    # Bottom band: fade into solid black (hides the credits that showed through), then just the title.
    h, w = img.shape[:2]
    a = np.zeros((h, 1), np.float32)
    fade = 70
    a[BAND_TOP - fade:BAND_TOP, 0] = np.linspace(0, 1, fade)
    a[BAND_TOP:, 0] = 1
    band = np.array([12, 10, 10], np.float32)
    img = (img * (1 - a[..., None]) + band * a[..., None]).astype(np.uint8)
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    d = ImageDraw.Draw(pil)
    title = TITLES[n]
    size = 96
    font = ImageFont.truetype(FONT, size)
    lines = [title]
    if d.textlength(title, font=font) > w - 120:  # long names: two lines, or smaller
        words = title.split()
        mid = len(words) // 2 or 1
        lines = [" ".join(words[:mid]), " ".join(words[mid:])] if len(words) > 1 else [title]
        size = 84
        font = ImageFont.truetype(FONT, size)
        while max(d.textlength(l, font=font) for l in lines) > w - 120:
            size -= 4
            font = ImageFont.truetype(FONT, size)
    total = len(lines) * size * 1.15
    y = BAND_TOP + (h - BAND_TOP - total) / 2
    for line in lines:
        tw = d.textlength(line, font=font)
        d.text(((w - tw) / 2, y), line, font=font, fill=(255, 255, 255))
        y += size * 1.15
    pil.save(OUT / path.name, quality=93)


t = time.time()
for f in sorted(SRC.glob("*.jpg")):
    clean(f)
print("done", round(time.time() - t, 1), "s")
