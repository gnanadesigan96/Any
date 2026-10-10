"""Stage 3: one still image per scene (plus the thumbnail background)."""

import base64
import os
import textwrap
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont

from .util import find_font_file, log

OPENAI_URL = "https://api.openai.com/v1/images/generations"


class OpenAIImages:
    def __init__(self, cfg: dict):
        self.i = cfg["images"]
        self.key = os.environ.get("OPENAI_API_KEY", "")
        if not self.key:
            raise RuntimeError("Set OPENAI_API_KEY in .env (used for image generation)")

    def generate(self, prompt: str, out_path: Path) -> None:
        resp = requests.post(
            OPENAI_URL,
            headers={"Authorization": f"Bearer {self.key}"},
            json={"model": self.i["model"], "prompt": prompt, "size": self.i["size"],
                  "quality": self.i["quality"], "n": 1},
            timeout=300,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Image API error {resp.status_code}: {resp.text[:300]}")
        out_path.write_bytes(base64.b64decode(resp.json()["data"][0]["b64_json"]))


class PlaceholderImages:
    """Labelled gradient cards; used by --dry-run so no image API is called."""

    PALETTE = [((28, 42, 68), (94, 64, 98)), ((20, 60, 60), (70, 110, 80)),
               ((70, 40, 30), (140, 90, 50)), ((35, 35, 70), (60, 90, 140))]

    def __init__(self, cfg: dict):
        w, h = (int(x) for x in cfg["images"]["size"].split("x"))
        self.size = (w, h)
        self.font = find_font_file()
        self.count = 0

    def generate(self, prompt: str, out_path: Path) -> None:
        top, bottom = self.PALETTE[hash(out_path.name) % len(self.PALETTE)]
        w, h = self.size
        img = Image.new("RGB", self.size)
        draw = ImageDraw.Draw(img)
        for y in range(h):
            t = y / h
            draw.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * t) for a, b in zip(top, bottom)))
        font = ImageFont.truetype(self.font, size=h // 16)
        text = "\n".join(textwrap.wrap(prompt, 32)[:5])
        draw.multiline_text((w / 2, h / 2), text, font=font, fill=(235, 235, 235),
                            anchor="mm", align="center", spacing=12)
        img.save(out_path)


class LocalImages:
    """Free AI images generated on your own Apple Silicon Mac with Z-Image-Turbo (Apache-2.0,
    commercial use allowed) through mflux. The model loads once and is reused for every image."""

    def __init__(self, cfg: dict):
        try:
            from mflux.models.z_image.variants.z_image import ZImage
        except ImportError as e:
            raise RuntimeError("Local images need mflux on an Apple Silicon Mac: pip install mflux") from e
        self.l = cfg["images"]["local"]
        log("Loading the local image model (the first run downloads it once, roughly 20 GB)...")
        self.model = ZImage(quantize=self.l["quantize"])
        self.lock = threading.Lock()

    def generate(self, prompt: str, out_path: Path) -> None:
        with self.lock:  # one image at a time; the GPU is the bottleneck anyway
            started = time.time()
            image = self.model.generate_image(seed=self.l["seed"], prompt=prompt,
                                              num_inference_steps=self.l["steps"],
                                              width=self.l["width"], height=self.l["height"])
            image.save(out_path, overwrite=True)
            log(f"  {out_path.name} ({time.time() - started:.0f}s)")


_PROVIDERS = {}  # reuse heavy providers (the local model) across parts of a run


def make_image_provider(cfg: dict, dry_run: bool):
    if dry_run:
        return PlaceholderImages(cfg)
    provider = cfg["images"]["provider"]
    if provider == "openai":
        return OpenAIImages(cfg)
    if provider == "local":
        key = ("local", tuple(sorted(cfg["images"]["local"].items())))
        if key not in _PROVIDERS:
            _PROVIDERS[key] = LocalImages(cfg)
        return _PROVIDERS[key]
    raise RuntimeError(f"Unknown images.provider '{provider}'")


def styled(prompt: str, cfg: dict) -> str:
    return f"{prompt.strip().rstrip('.')}. Style: {cfg['images']['style']}."


def generate_images(jobs: list, cfg: dict, dry_run: bool) -> None:
    """jobs: [(prompt, out_path)]; existing files are kept so re-runs only fill gaps."""
    todo = [(p, out) for p, out in jobs if not out.exists()]
    if not todo:
        return
    provider = make_image_provider(cfg, dry_run)
    log(f"Generating {len(todo)} images...")
    failures = []

    def work(job):
        prompt, out = job
        try:
            provider.generate(styled(prompt, cfg), out)
        except Exception as e:  # keep going; report all failures together
            failures.append(f"{out.name}: {e}")

    with ThreadPoolExecutor(max_workers=max(1, cfg["images"]["workers"])) as pool:
        list(pool.map(work, todo))
    if failures:
        raise RuntimeError("Some images failed (re-run to retry only these):\n  " + "\n  ".join(failures))
