"""Generated score for story Shorts: a dark drone bed, a deep boom on the hook and on the
cliffhanger, and a rising tension sound into it (optionally a whoosh on every cut). Synthesised here, so it is free
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


def _tick(rng, last: bool = False) -> np.ndarray:
    """A wooden clock tick: a short knock (two damped body modes) with a click of noise on top."""
    t = np.arange(int(0.12 * SR)) / SR
    f = 1250 if last else 950
    knock = (np.sin(2 * np.pi * f * t) * 0.7 + np.sin(2 * np.pi * f * 2.7 * t) * 0.25) * np.exp(-t * 55)
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.5
    return knock + click - _smooth(click, 8)


def _chime(rng) -> np.ndarray:
    """A bright sparkle for the reveal: a few high bell partials, slightly detuned, ringing out."""
    t = np.arange(int(1.6 * SR)) / SR
    out = np.zeros_like(t)
    for k, f in enumerate((1568, 2093, 2637, 3136, 4186)):
        start = int(k * 0.045 * SR)
        tt = t[: len(t) - start]
        out[start:] += np.sin(2 * np.pi * f * (1 + rng.uniform(-0.002, 0.002)) * tt) * np.exp(-tt * (3 + k)) * 0.25
    return out


def _pop() -> np.ndarray:  # the button popping in
    t = np.arange(int(0.12 * SR)) / SR
    return np.sin(2 * np.pi * (300 + 900 * t / 0.12) * t) * np.exp(-t * 35) * 0.8


def _click(rng) -> np.ndarray:  # the tap
    t = np.arange(int(0.05 * SR)) / SR
    n = rng.standard_normal(len(t))
    return (n - _smooth(n, 4)) * np.exp(-t * 180) * 0.9


def _ding() -> np.ndarray:  # subscribed
    t = np.arange(int(0.9 * SR)) / SR
    return (np.sin(2 * np.pi * 1760 * t) + 0.5 * np.sin(2 * np.pi * 2640 * t)) * np.exp(-t * 6) * 0.45


def _riser(seconds: float, rng) -> np.ndarray:
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ramp = (t / seconds) ** 2
    freq = 180 + 520 * ramp
    tone = np.sin(2 * np.pi * np.cumsum(freq) / SR) * 0.25
    noise = (rng.standard_normal(n) - _smooth(rng.standard_normal(n), 6)) * 0.15
    return (tone + noise) * ramp


def build_score(path: Path, duration: float, cut_times: list, climax_time: float, seed: int = 0,
                whoosh: bool = False, riser: bool = False, ticks: list = (), bed: bool = True,
                events: list = ()) -> Path:
    """Writes a mono 44.1 kHz WAV `duration` seconds long. bed=False leaves out the drone under the voice (quiz
    videos: just the ticks and the hits, so nothing hisses or hums behind the narration)."""
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    t = np.arange(n) / SR
    drone = (0.22 * np.sin(2 * np.pi * 55.0 * t) + 0.14 * np.sin(2 * np.pi * 55.35 * t)
             + 0.09 * np.sin(2 * np.pi * 82.41 * t + 0.6 * np.sin(2 * np.pi * 0.07 * t))
             + 0.05 * np.sin(2 * np.pi * 110.2 * t))
    drone *= 0.65 + 0.35 * np.sin(2 * np.pi * 0.11 * t + 1.3)
    # No noise layer: filtered noise under the voice is heard as static once the mix is loudness-normalised.
    score = drone if bed else np.zeros(n)
    score *= np.clip(t / 0.6, 0, 1)  # quick swell in, under the opening boom

    def place(sound: np.ndarray, at: float, gain: float) -> None:
        start = int(at * SR)
        if start >= n:
            return
        seg = sound[: n - start]
        score[start:start + len(seg)] += seg * gain

    place(_boom(rng), 0.0, 0.9)
    for cut in (cut_times if whoosh else []):
        if 0.5 < cut < duration - 0.3:
            place(_whoosh(rng), max(cut - 0.35, 0), 0.5)
    for k, at in enumerate(ticks):  # a clock tick each second of a countdown, the last one higher
        place(_tick(rng, last=k == len(ticks) - 1), at, 0.75)
    for kind, at in events:  # the quiz ending: (kind, start time)
        if kind == "reveal":
            place(_whoosh(rng), max(at - 0.38, 0), 0.9)
            place(_chime(rng), at + 0.02, 0.8)
        elif kind == "outro":
            from .finale import BUTTON_IN, TAP
            place(_pop(), at + BUTTON_IN, 0.6)
            place(_click(rng), at + TAP, 0.8)
            place(_ding(), at + TAP + 0.06, 0.6)
    if climax_time > 3.5:
        if riser:  # a rising whoosh into the last scene (off by default: it sounds like a whoosh at the end)
            place(_riser(3.0, rng), climax_time - 3.0, 0.9)
        place(_boom(rng), climax_time, 1.0)
    fade = int(min(0.4, duration / 4) * SR)
    score[-fade:] *= np.linspace(1, 0, fade)
    score /= max(np.abs(score).max(), 1e-6) / 0.9
    if not bed:  # no drone to fill the silences: keep the hits clean, below the voice
        score *= 0.7
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((score * 32767).astype(np.int16).tobytes())
    return path
