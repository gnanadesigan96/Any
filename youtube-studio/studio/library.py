"""Finds (or generates and caches) the music beds and sound effects."""
from pathlib import Path

import numpy as np

from . import sounds
from .dsp import SR, loopify, read_audio, write_wav

ROOT = Path(__file__).resolve().parent.parent
USER_MUSIC = ROOT / "assets" / "music"
USER_SFX = ROOT / "assets" / "sfx"
CACHE = ROOT / "assets" / "_generated" / f"v{sounds.SYNTH_VERSION}"
AUDIO_EXT = (".wav", ".mp3", ".m4a", ".ogg", ".flac", ".aac")

_mem = {}


def _user_file(folder, name):
    for ext in AUDIO_EXT:
        p = folder / f"{name}{ext}"
        if p.exists():
            return p
    return None


def source_of(kind, name):
    folder = USER_MUSIC if kind == "music" else USER_SFX
    p = _user_file(folder, name)
    return f"your file {p.relative_to(ROOT)}" if p else "built-in (synthesised)"


def music(mood):
    key = ("music", mood)
    if key not in _mem:
        user = _user_file(USER_MUSIC, mood)
        if user:
            x = read_audio(user)
            # make an ordinary song loop smoothly by crossfading its end into its start
            _mem[key] = loopify(x, len(x) / SR - 3.0, 3.0) if len(x) > 8 * SR else x
        else:
            if mood not in sounds.MOODS:
                raise ValueError(f"Unknown music mood '{mood}'. Built-in moods: {', '.join(sounds.MOODS)} "
                                 f"(or add assets/music/{mood}.mp3)")
            cached = CACHE / "music" / f"{mood}.wav"
            if not cached.exists():
                cached.parent.mkdir(parents=True, exist_ok=True)
                print(f"  generating music bed '{mood}' ...")
                write_wav(cached, sounds.make_bed(mood))
            _mem[key] = read_audio(cached)
    return _mem[key]


def sfx(name):
    key = ("sfx", name)
    if key not in _mem:
        user = _user_file(USER_SFX, name)
        if user:
            _mem[key] = read_audio(user)
        else:
            if name not in sounds.SFX:
                raise ValueError(f"Unknown sound effect '{name}'. Built-in: {', '.join(sounds.SFX)} "
                                 f"(or add assets/sfx/{name}.mp3)")
            cached = CACHE / "sfx" / f"{name}.wav"
            if not cached.exists():
                cached.parent.mkdir(parents=True, exist_ok=True)
                write_wav(cached, sounds.make_sfx(name))
            _mem[key] = read_audio(cached)
    return _mem[key]


def build_all():
    """Pre-generate everything (used by `make.py sounds`)."""
    for m in sounds.MOODS:
        music(m)
    for s in sounds.SFX:
        sfx(s)


def demo_reel(path):
    """Write one file with every mood and effect back to back, for listening."""
    parts = []
    gap = np.zeros((int(0.8 * SR), 2))
    for m in sounds.MOODS:
        parts += [music(m)[: 15 * SR], gap]
    for s in sounds.SFX:
        x = sfx(s)
        parts += [x[: 6 * SR] if s in sounds.AMBIENCES else x, gap]
    write_wav(path, np.concatenate(parts))
    order = [f"music:{m} (15s)" for m in sounds.MOODS] + [f"sfx:{s}" for s in sounds.SFX]
    return order
