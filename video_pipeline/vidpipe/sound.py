"""Generated score for story Shorts: a dark drone bed, a whoosh on every cut, a deep boom on the
hook and on the cliffhanger, and a rising tension sound into it. Synthesised here, so it is free
and royalty-free, and it is timed to the actual scene cuts of each video."""

import wave
from pathlib import Path

import numpy as np

SR = 44100


def _smooth(x: np.ndarray, width: int) -> np.ndarray:
    """Moving-average low-pass (cheap and good enough for noise textures)."""
    c = np.cumsum(np.concatenate([[0.0], x]))
    out = (c[width:] - c[:-width]) / width
    return np.concatenate([out, np.full(width - 1, out[-1] if len(out) else 0.0)])


def _boom(rng) -> np.ndarray:
    t = np.arange(int(1.6 * SR)) / SR
    freq = 36 + 80 * np.exp(-t * 5)
    phase = 2 * np.pi * np.cumsum(freq) / SR
    body = np.sin(phase) * np.exp(-t * 2.4)
    hit = _smooth(rng.standard_normal(len(t)), 30) * np.exp(-t * 18) * 0.8
    return body + hit


def _whoosh(rng) -> np.ndarray:
    n = int(0.5 * SR)
    t = np.arange(n) / n
    env = np.sin(np.pi * np.clip(t / 0.75, 0, 1)) ** 2 * (t < 0.75) + (t >= 0.75) * np.exp(-(t - 0.75) * 30)
    noise = rng.standard_normal(n)
    airy = noise - _smooth(noise, 12)  # remove the lows: an airy swish rather than a rumble
    return airy * env * 0.6


def _riser(seconds: float, rng) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ramp = (t / seconds) ** 2
    freq = 180 + 520 * ramp
    tone = np.sin(2 * np.pi * np.cumsum(freq) / SR) * 0.25
    noise = (rng.standard_normal(n) - _smooth(rng.standard_normal(n), 6)) * 0.15
    return (tone + noise) * ramp


def build_score(path: Path, duration: float, cut_times: list, climax_time: float, seed: int = 0) -> Path:
    """Writes a mono 44.1 kHz WAV `duration` seconds long."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    drone = (0.22 * np.sin(2 * np.pi * 55.0 * t) + 0.14 * np.sin(2 * np.pi * 55.35 * t)
             + 0.09 * np.sin(2 * np.pi * 82.41 * t + 0.6 * np.sin(2 * np.pi * 0.07 * t))
             + 0.05 * np.sin(2 * np.pi * 110.2 * t))
    drone *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.11 * t + 1.3)
    rumble = _smooth(rng.standard_normal(n), 400) * 3.0
    score = drone + rumble * 0.25
    score *= np.clip(t / 0.6, 0, 1)  # quick swell in, under the opening boom

    def place(sound: np.ndarray, at: float, gain: float) -> None:
        start = int(at * SR)
        if start >= n:
            return
        seg = sound[: n - start]
        score[start:start + len(seg)] += seg * gain

    place(_boom(rng), 0.0, 0.9)
    for cut in cut_times:
        if 0.5 < cut < duration - 0.3:
            place(_whoosh(rng), max(cut - 0.35, 0), 0.5)
    if climax_time > 3.5:
        riser = _riser(3.0, rng)
        place(riser, climax_time - 3.0, 0.9)
        place(_boom(rng), climax_time, 1.0)
    fade = int(min(0.4, duration / 4) * SR)
    score[-fade:] *= np.linspace(1, 0, fade)
    score /= max(np.abs(score).max(), 1e-6) / 0.9
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((score * 32767).astype(np.int16).tobytes())
    return path
