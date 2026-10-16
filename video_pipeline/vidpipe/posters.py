"""Puts film posters from one folder into the right story folders (stories/guess-movie-NN/poster.jpg).

File names only need to contain the film's name, in English or Tamil, spelled any common way:
"Imaikka Nodigal HD poster.jpg", "maayavan_2017.webp" and "இமைக்கா நொடிகள்.png" all work."""

import json
import re
import shutil
from difflib import SequenceMatcher
from pathlib import Path

from .util import log

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".avif", ".bmp", ".heic"}
NOISE = {"poster", "posters", "movie", "film", "tamil", "hd", "official", "first", "look", "fl", "download", "copy",
         "image", "img", "final", "new", "wallpaper", "the", "4k", "1080p", "720p", "full", "photo", "pic"}
SOUNDS = [("th", "t"), ("dh", "d"), ("zh", "l"), ("sh", "s"), ("kh", "k"), ("ph", "p"), ("bh", "b"), ("w", "v"),
          ("ee", "i"), ("oo", "u"), ("ch", "c")]


def normalise(text: str) -> str:
    """Lower case, no years, no "poster"/"HD"-style words, common Tamil-in-English spelling variants folded."""
    text = re.sub(r"(19|20)\d\d", " ", text.lower())
    words = [w for w in re.split(r"[^0-9a-z஀-௿]+", text) if w and w not in NOISE]
    s = "".join(words)
    for a, b in SOUNDS:
        s = s.replace(a, b)
    return re.sub(r"(.)\1+", r"\1", s)  # aa -> a, kk -> k


def score(file_name: str, name: str) -> float:
    f, n = normalise(file_name), normalise(name)
    if not f or not n:
        return 0.0
    if len(n) >= 3 and n in f:
        return 1.0 + len(n) / 100  # the longer the name found, the surer the match (Maayavan beats Maya)
    return SequenceMatcher(None, f, n).ratio()


def match(file_name: str, films: list) -> tuple:
    """(best folder, its score, runner-up score)."""
    ranked = sorted(((max(score(file_name, n) for n in film["names"]), film["folder"]) for film in films), reverse=True)
    best, second = ranked[0], ranked[1] if len(ranked) > 1 else (0.0, "")
    return best[1], best[0], second[0]


def place_posters(src: Path, stories: Path) -> dict:
    films = json.loads((stories / "guess_movies.json").read_text())
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in IMAGE_SUFFIXES and not p.name.startswith("."))
    chosen, unsure = {}, []
    for f in files:
        folder, best, second = match(f.stem, films)
        # An exact name inside the file name is enough as long as it's the longest one found; fuzzy matches need a
        # clear lead over the next film.
        if best < 0.72 or best - second < (0.001 if best >= 1.0 else 0.05):
            unsure.append(f.name)
        elif folder not in chosen or best > chosen[folder][1]:
            if folder in chosen:
                unsure.append(chosen[folder][0].name)
            chosen[folder] = (f, best)
        else:
            unsure.append(f.name)
    placed = []
    for folder, (f, _) in sorted(chosen.items()):
        dest_dir = stories / folder
        try:
            from PIL import Image
            with Image.open(f) as img:
                img.convert("RGB").save(dest_dir / "poster.jpg", quality=92)
        except Exception:  # a format Pillow can't read (e.g. HEIC): copy it if the video tools can use it
            if f.suffix.lower() not in {".jpg", ".jpeg", ".png", ".webp"}:
                unsure.append(f"{f.name} (save it as .jpg)")
                continue
            shutil.copyfile(f, dest_dir / f"poster{f.suffix.lower()}")
        for old in dest_dir.glob("poster.*"):  # only one poster per film
            if old.name not in ("poster.jpg", f"poster{f.suffix.lower()}") or (
                    old.name != "poster.jpg" and (dest_dir / "poster.jpg").exists()):
                old.unlink()
        placed.append((f.name, folder))
    have = {p.parent.name for p in stories.glob("guess-movie-*/poster.*")}
    missing = [film["folder"] for film in films if film["folder"] not in have]
    return {"placed": placed, "unsure": unsure, "missing": missing}


def report(result: dict, films_path: Path) -> None:
    names = {f["folder"]: f["names"][0] for f in json.loads(films_path.read_text())}
    for name, folder in result["placed"]:
        log(f"  {name}  ->  stories/{folder}/  ({names[folder]})")
    for name in result["unsure"]:
        log(f"  ?? {name}: couldn't tell which film; rename it to the film's name and run again")
    if result["missing"]:
        log("Still no poster for: " + ", ".join(f"{f} ({names[f]})" for f in result["missing"]))
    else:
        log("Every film has its poster.")
