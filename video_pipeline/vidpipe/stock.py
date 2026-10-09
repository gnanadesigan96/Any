"""Free visuals: stock video clips and photos from Pexels and Pixabay (free API keys,
free for commercial use). Credits are recorded so they can go in the description."""

import os
import shutil
from pathlib import Path

import requests
from PIL import Image, ImageDraw

from .util import log, read_json, write_json

VIDEO_EXT, PHOTO_EXT = ".mp4", ".jpg"


class Pexels:
    name = "Pexels"

    def __init__(self, key: str):
        self.headers = {"Authorization": key}

    def videos(self, query: str) -> list:
        r = requests.get("https://api.pexels.com/videos/search", headers=self.headers, timeout=30,
                         params={"query": query, "orientation": "landscape", "per_page": 15})
        r.raise_for_status()
        out = []
        for v in r.json().get("videos", []):
            files = [{"url": f["link"], "width": f.get("width") or 0, "height": f.get("height") or 0}
                     for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and f.get("link")]
            if files:
                out.append({"id": f"pexels-v{v['id']}", "page": v.get("url", ""), "author": v.get("user", {}).get("name", ""),
                            "duration": v.get("duration") or 0, "files": files})
        return out

    def photos(self, query: str) -> list:
        r = requests.get("https://api.pexels.com/v1/search", headers=self.headers, timeout=30,
                         params={"query": query, "orientation": "landscape", "per_page": 15})
        r.raise_for_status()
        return [{"id": f"pexels-p{p['id']}", "page": p.get("url", ""), "author": p.get("photographer", ""),
                 "url": p["src"].get("large2x") or p["src"]["original"]}
                for p in r.json().get("photos", []) if p.get("src")]


class Pixabay:
    name = "Pixabay"

    def __init__(self, key: str):
        self.key = key

    def _get(self, url: str, query: str, extra: dict) -> list:
        r = requests.get(url, timeout=30, params={"key": self.key, "q": query[:100], "safesearch": "true",
                                                  "per_page": 20, **extra})
        r.raise_for_status()
        return r.json().get("hits", [])

    def videos(self, query: str) -> list:
        out = []
        for h in self._get("https://pixabay.com/api/videos/", query, {}):
            files = [{"url": f["url"], "width": f.get("width") or 0, "height": f.get("height") or 0}
                     for f in (h.get("videos") or {}).values() if f.get("url")]
            if files:
                out.append({"id": f"pixabay-v{h['id']}", "page": h.get("pageURL", ""), "author": h.get("user", ""),
                            "duration": h.get("duration") or 0, "files": files})
        return out

    def photos(self, query: str) -> list:
        return [{"id": f"pixabay-p{h['id']}", "page": h.get("pageURL", ""), "author": h.get("user", ""),
                 "url": h["largeImageURL"]}
                for h in self._get("https://pixabay.com/api/", query,
                                   {"image_type": "photo", "orientation": "horizontal"})
                if h.get("largeImageURL")]


def make_sources(cfg: dict) -> list:
    sources = []
    for name in cfg["images"]["stock"]["sources"]:
        if name == "pexels" and os.environ.get("PEXELS_API_KEY"):
            sources.append(Pexels(os.environ["PEXELS_API_KEY"]))
        elif name == "pixabay" and os.environ.get("PIXABAY_API_KEY"):
            sources.append(Pixabay(os.environ["PIXABAY_API_KEY"]))
    if not sources:
        raise RuntimeError("Stock visuals need PEXELS_API_KEY and/or PIXABAY_API_KEY in .env (both are free)")
    return sources


def pick_file(files: list, target_width: int) -> dict:
    """Smallest landscape file that is at least target_width wide, else the widest one."""
    landscape = [f for f in files if f["width"] >= f["height"]] or files
    big_enough = [f for f in landscape if f["width"] >= target_width]
    return min(big_enough, key=lambda f: f["width"]) if big_enough else max(landscape, key=lambda f: f["width"])


def _download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.replace(dest)


def _queries(query: str) -> list:
    words = query.split()
    out = [query]
    if len(words) > 2:
        out.append(" ".join(words[:2]))
    return out


def blank_card(dest: Path, size=(1920, 1080)) -> None:
    """Last resort when nothing matches: a dark gradient (the captions carry the scene)."""
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(size[1]):
        shade = int(18 + 22 * (1 - abs(y / size[1] - 0.5) * 2))
        draw.line([(0, y), (size[0], y)], fill=(shade, shade, shade + 6))
    img.save(dest, quality=92)


def existing_asset(img_dir: Path, stem: str):
    for ext in (VIDEO_EXT, PHOTO_EXT, ".png"):
        if (img_dir / f"{stem}{ext}").exists():
            return img_dir / f"{stem}{ext}"
    return None


def fetch_visuals(scenes: list, durations: list, img_dir: Path, cfg: dict) -> list:
    """Returns one asset path per scene (.mp4 clip or .jpg photo), downloading what's missing."""
    st = cfg["images"]["stock"]
    width = cfg["video"]["width"]
    credits_path = img_dir / "credits.json"
    credits = read_json(credits_path, {}) or {}
    used = {c["id"] for c in credits.values() if c.get("id")}
    paths = [existing_asset(img_dir, f"scene_{i:03d}") for i in range(len(scenes))]
    todo = [i for i, p in enumerate(paths) if p is None]
    if not todo:
        return paths
    sources = make_sources(cfg)
    log(f"Finding stock footage for {len(todo)} scenes ({', '.join(s.name for s in sources)})...")

    for i in todo:
        stem = img_dir / f"scene_{i:03d}"
        found = None
        for query in _queries(scenes[i].search_query):
            for source in sources:
                try:
                    if st["prefer_video"]:
                        clips = [c for c in source.videos(query) if c["id"] not in used]
                        long_enough = [c for c in clips if c["duration"] >= durations[i]]
                        if long_enough or clips:
                            c = (long_enough or clips)[0]
                            dest = stem.with_suffix(VIDEO_EXT)
                            _download(pick_file(c["files"], width)["url"], dest)
                            found = (dest, c, source.name)
                            break
                    photos = [p for p in source.photos(query) if p["id"] not in used]
                    if photos:
                        dest = stem.with_suffix(PHOTO_EXT)
                        _download(photos[0]["url"], dest)
                        found = (dest, photos[0], source.name)
                        break
                except requests.RequestException as e:
                    log(f"  {source.name} search failed for '{query}': {e}")
            if found:
                break
        if found:
            dest, item, source_name = found
            used.add(item["id"])
            credits[str(i)] = {"id": item["id"], "source": source_name, "author": item["author"], "page": item["page"]}
            paths[i] = dest
        elif i > 0 and paths[i - 1] is not None:
            log(f"  No stock match for scene {i} ('{scenes[i].search_query}'); reusing the previous visual")
            paths[i] = stem.with_suffix(paths[i - 1].suffix)
            shutil.copyfile(paths[i - 1], paths[i])
        else:
            log(f"  No stock match for scene {i} ('{scenes[i].search_query}'); using a plain card")
            paths[i] = stem.with_suffix(PHOTO_EXT)
            blank_card(paths[i], (cfg["video"]["width"], cfg["video"]["height"]))
        write_json(credits_path, credits)
    return paths


def fetch_thumbnail_photo(query: str, dest: Path, cfg: dict) -> None:
    if dest.exists():
        return
    for q in _queries(query):
        for source in make_sources(cfg):
            try:
                photos = source.photos(q)
            except requests.RequestException:
                continue
            if photos:
                _download(photos[0]["url"], dest)
                return
    blank_card(dest)


def credit_lines(img_dir: Path) -> list:
    credits = read_json(img_dir / "credits.json", {}) or {}
    seen, lines = set(), []
    for c in credits.values():
        key = (c["source"], c["author"])
        if key not in seen and c["author"]:
            seen.add(key)
            lines.append(f"{c['author']} ({c['source']})")
    return lines
