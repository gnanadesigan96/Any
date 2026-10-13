"""Builds the full soundtrack: narration + ducked music + ambiences + effects."""
import numpy as np

from . import library
from .dsp import SR, fade, nsamp, place, read_audio, soft_limit, stereo, tile


def _segments(scenes, attr):
    """Merge consecutive scenes that share the same value of attr."""
    segs = []
    for sc in scenes:
        val = getattr(sc, attr)
        if segs and segs[-1][2] == val:
            segs[-1][1] = sc.start + sc.duration
        else:
            segs.append([sc.start, sc.start + sc.duration, val])
    return segs


def _smooth(x, attack, release, rate):
    """One-pole envelope follower at control rate."""
    a_up = 1 - np.exp(-1 / (attack * rate))
    a_dn = 1 - np.exp(-1 / (release * rate))
    out = np.empty_like(x)
    cur = x[0]
    for i, v in enumerate(x):
        cur += (a_up if v > cur else a_dn) * (v - cur)
        out[i] = cur
    return out


def build(ep):
    total = ep.total
    n = nsamp(total) + SR
    lead = float(ep.cfg["narration_lead"])

    # ---- narration --------------------------------------------------------
    voice = np.zeros((n, 2))
    for sc in ep.scenes:
        if sc.narration:
            place(voice, stereo(read_audio(sc.narration, 1)), sc.start + lead)

    # ---- music bed with crossfades between moods -------------------------
    music = np.zeros((n, 2))
    X = 2.0
    for start, end, mood in _segments(ep.scenes, "music"):
        if not mood or mood == "none":
            continue
        s0 = max(0.0, start - X / 2)
        e0 = min(total, end + X / 2)
        loop = library.music(mood)
        off = nsamp(s0) % len(loop)  # keep the loop's own clock so re-entries feel continuous
        seg = tile(np.roll(loop, -off, axis=0), nsamp(e0 - s0))
        seg = fade(seg, X if s0 > 0 else 1.0, X if e0 < total else 3.0)
        place(music, seg, s0)

    # ---- duck music under the voice --------------------------------------
    rate = 200  # control points per second
    hop = SR // rate
    m = len(voice) // hop
    env = np.sqrt(np.mean(voice[: m * hop, 0].reshape(m, hop) ** 2, axis=1))
    active = (env > 0.01).astype(float)
    # hold the duck through short pauses between words
    hold = int(0.35 * rate)
    if hold:
        active = np.convolve(active, np.ones(hold), mode="same") > 0
    lo, hi = float(ep.cfg["music_duck_level"]), float(ep.cfg["music_level"])
    gain_c = _smooth(np.where(active, lo, hi).astype(float), attack=0.12, release=0.7, rate=rate)
    gain = np.interp(np.arange(n), np.arange(m) * hop + hop / 2, gain_c)
    music *= gain[:, None]  # beds are normalised to rms 0.1 (-20 dBFS)

    # ---- ambiences (rain, river ...) -------------------------------------
    amb = np.zeros((n, 2))
    names = sorted({a for sc in ep.scenes for a in sc.ambience})
    for name in names:
        loop = library.sfx(name)
        spans = []
        for sc in ep.scenes:
            if name in sc.ambience:
                if spans and abs(spans[-1][1] - sc.start) < 1e-6:
                    spans[-1][1] = sc.start + sc.duration
                else:
                    spans.append([sc.start, sc.start + sc.duration])
        for s, e in spans:
            seg = tile(loop, nsamp(e - s + 1.0))
            place(amb, fade(seg, 1.2, 2.0), max(0.0, s - 0.5))
    amb *= float(ep.cfg["ambience_level"])  # ambience loops are rms 0.12

    # ---- one-shot effects -------------------------------------------------
    fx = np.zeros((n, 2))
    for sc in ep.scenes:
        for s in sc.sfx:
            snd = library.sfx(s.name)
            if s.name in library.sounds.AMBIENCES:
                snd = fade(snd[: 6 * SR], 0.3, 1.5)
            at = s.at if s.at >= 0 else max(0.0, sc.duration + s.at)  # negative = from scene end
            place(fx, snd, sc.start + at, s.volume)

    mix = voice * 1.0 + music + amb + fx * 0.7
    mix = mix[: nsamp(total)]
    mix = fade(mix, 0.05, 1.5)
    return soft_limit(mix * 0.9)
