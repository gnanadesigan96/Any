"""Stage 5: three 1280x720 thumbnail variants (same background, different text)."""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from .util import find_font_file

SIZE = (1280, 720)
ACCENTS = [(255, 215, 0), (255, 255, 255), (255, 90, 60)]


def _cover(img: Image.Image, size) -> Image.Image:
    w, h = size
    scale = max(w / img.width, h / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((left, top, left + w, top + h))


def _fit_font(draw, lines, font_file, max_w, max_h):
    for size in range(150, 40, -6):
        font = ImageFont.truetype(font_file, size)
        boxes = [draw.textbbox((0, 0), line, font=font, stroke_width=size // 12) for line in lines]
        width = max(b[2] - b[0] for b in boxes)
        height = sum(b[3] - b[1] for b in boxes) + (len(lines) - 1) * size * 0.15
        if width <= max_w and height <= max_h:
            return font
    return ImageFont.truetype(font_file, 40)


def make_thumbnails(background: Path, texts: list, out_dir: Path, cfg: dict) -> list:
    font_file = cfg["thumbnail"].get("font_file") or find_font_file("Inter", "black") \
        or find_font_file()
    with Image.open(background) as src:
        base = _cover(src.convert("RGB"), SIZE)
    # Darken the left side so text stays readable on any image.
    shade = Image.new("L", SIZE)
    sd = ImageDraw.Draw(shade)
    for x in range(SIZE[0]):
        sd.line([(x, 0), (x, SIZE[1])], fill=int(190 * max(0.0, 1 - x / (SIZE[0] * 0.75))))
    base = Image.composite(Image.new("RGB", SIZE, (0, 0, 0)), base, shade.filter(ImageFilter.GaussianBlur(8)))

    outputs = []
    for k, text in enumerate(texts[:3]):
        img = base.copy()
        draw = ImageDraw.Draw(img)
        lines = textwrap.wrap(text.upper(), 12)[:3] or [""]
        font = _fit_font(draw, lines, font_file, SIZE[0] * 0.58, SIZE[1] * 0.7)
        stroke = max(4, font.size // 12)
        line_h = font.size * 1.12
        y = (SIZE[1] - line_h * len(lines)) / 2
        for j, line in enumerate(lines):
            fill = ACCENTS[k % len(ACCENTS)] if j == len(lines) - 1 else (255, 255, 255)
            draw.text((60, y), line, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0))
            y += line_h
        out = out_dir / f"thumbnail_{k + 1}.jpg"
        img.save(out, quality=92)
        outputs.append(out)
    return outputs
