"""Downloads the free (SIL Open Font License) Tamil fonts from Google Fonts on first use."""
import re
import urllib.request
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parent.parent / "fonts"

# file name -> (Google Fonts family, weight)
FONTS = {
    "NotoSansTamil-Bold.ttf": ("Noto Sans Tamil", 700),
    "NotoSansTamil-Medium.ttf": ("Noto Sans Tamil", 500),
    "NotoSerifTamil-Bold.ttf": ("Noto Serif Tamil", 700),
    "Catamaran-ExtraBold.ttf": ("Catamaran", 800),
    "Catamaran-SemiBold.ttf": ("Catamaran", 600),
}


def _fetch(family, weight, dest):
    css_url = f"https://fonts.googleapis.com/css2?family={family.replace(' ', '+')}:wght@{weight}"
    req = urllib.request.Request(css_url, headers={"User-Agent": "Mozilla/4.0"})  # old UA => .ttf links
    css = urllib.request.urlopen(req, timeout=30).read().decode()
    urls = re.findall(r"url\((https://[^)]+\.ttf)\)", css)
    if not urls:
        raise RuntimeError(f"no ttf found for {family} {weight}")
    # Tamil families list several unicode-range subsets; the largest file holds the Tamil glyphs
    best = max((urllib.request.urlopen(u, timeout=60).read() for u in set(urls)), key=len)
    dest.write_bytes(best)


def ensure():
    FONT_DIR.mkdir(exist_ok=True)
    for name, (family, weight) in FONTS.items():
        p = FONT_DIR / name
        if not p.exists():
            print(f"  downloading font {family} {weight} ...")
            _fetch(family, weight, p)
    return FONT_DIR


def path(name):
    ensure()
    return str(FONT_DIR / name)
