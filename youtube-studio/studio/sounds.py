"""Original background music and sound effects, synthesised from scratch.

Nothing here is sampled from a recording, so none of it can trigger a
YouTube Content ID claim. To use a better track instead, drop a file with the
same name into assets/music/ (for a mood) or assets/sfx/ (for an effect),
e.g. assets/music/divine.mp3 - it is used automatically instead.

Moods (background music beds, each a seamless loop):
    calm, night, sad, tension, storm, divine, celebration
Sound effects:
    one-shots : temple_bell, puja_bell, conch, thunder, chains, gate_open,
                gate_close, whoosh, shimmer, sword, impact
    ambiences : rain, river, wind, crickets, heartbeat   (loop under scenes)
"""
import numpy as np

from .dsp import (SR, bp, coloured, fade, fft_filter, hp, loopify, lp, nsamp, normalize,
                  pan, place, reverb, set_rms, stereo, stft_filter, t_axis, white)

SYNTH_VERSION = 3
SA = 138.59  # tonic (Sa) = C#3, a common pitch for devotional music

SCALES = {
    "mohanam": [0, 2, 4, 7, 9],          # peaceful, pastoral
    "hamsadhwani": [0, 2, 4, 7, 11],     # bright, auspicious
    "shivaranjani": [0, 2, 3, 7, 9],     # longing, sorrow
    "revati": [0, 1, 5, 7, 10],          # mystic, dark
    "kalyani": [0, 2, 4, 6, 7, 9, 11],   # majestic
}

MOODS = ["calm", "night", "sad", "tension", "storm", "divine", "celebration"]
AMBIENCES = ["rain", "river", "wind", "crickets", "heartbeat"]
ONE_SHOTS = ["temple_bell", "puja_bell", "conch", "thunder", "chains", "gate_open",
             "gate_close", "whoosh", "shimmer", "sword", "impact"]
SFX = ONE_SHOTS + AMBIENCES


def semis(f, s):
    return f * 2 ** (s / 12)


# ============================================================ instruments ==
def tanpura_pluck(f0, dur=6.0, rng=None):
    """One tanpura string: rich harmonics with the moving 'jawari' buzz."""
    rng = rng or np.random.default_rng(0)
    t = t_axis(dur)
    out = np.zeros_like(t)
    centre = 2.0 + 13.0 * (1 - np.exp(-t / 1.6))
    for n in range(1, 32):
        fn = n * f0 * (1 + 0.00015 * n * n)
        if fn > 9000:
            break
        bump = np.exp(-((n - centre) / 2.6) ** 2)
        amp = (1 / n ** 0.85) * np.exp(-t * (0.32 + 0.045 * n)) * (0.3 + bump)
        out += amp * np.sin(2 * np.pi * fn * t + rng.uniform(0, 2 * np.pi))
    out *= 1 - np.exp(-t / 0.004)
    return fade(out, 0, 0.3)


def tanpura(length, sa=SA, cycle=4.6, seed=1):
    rng = np.random.default_rng(seed)
    strings = [(sa * 0.75, -0.35), (sa, 0.15), (sa, 0.3), (sa / 2, -0.1)]
    plucks = [(tanpura_pluck(f, 6.0, rng), p) for f, p in strings]
    out = np.zeros((nsamp(length), 2))
    t = -cycle
    while t < length:
        for k, (snd, p) in enumerate(plucks):
            place(out, pan(snd, p), t + k * cycle / 4 + rng.uniform(-0.03, 0.03),
                  rng.uniform(0.85, 1.0))
        t += cycle
    return out


def melody(rng, scale, sa, bpm, length, register=1, density=0.7, long_notes=False):
    """Phrase-based melody that wanders the raga and rests on Sa / Pa."""
    beat = 60.0 / bpm
    sc = SCALES[scale]
    pitches = [semis(sa, s + 12 * o) for o in range(register, register + 2) for s in sc]
    pitches.append(semis(sa, 12 * (register + 2)))
    homes = [i for i, f in enumerate(pitches) if any(
        abs(np.log2(f / semis(sa, 12 * o + k))) < 1e-3 for o in range(4) for k in (0, 7))]
    idx = homes[len(homes) // 2]
    notes, t = [], rng.uniform(0.5, 2.0) * beat
    durs = [1, 1.5, 2, 3] if long_notes else [0.5, 0.5, 1, 1, 1.5, 2]
    while t < length - 2 * beat:
        for i in range(int(rng.integers(3, 8))):
            step = rng.choice([-2, -1, -1, 0, 1, 1, 2])
            idx = int(np.clip(idx + step, 0, len(pitches) - 1))
            d = rng.choice(durs) * beat
            if i == 0 and rng.random() < 0.3:
                d *= 2
            gamaka = d >= 1.5 * beat and rng.random() < 0.35
            notes.append((t, d * 0.97, pitches[idx], gamaka))
            t += d
            if t > length - 2 * beat:
                break
        idx = min(homes, key=lambda h: abs(h - idx))
        d = rng.choice([2, 3, 4]) * beat
        notes.append((t, d, pitches[idx], rng.random() < 0.5))
        t += d + rng.choice([1, 2, 3, 4]) * beat / max(density, 0.2)
    return [n for n in notes if n[0] < length]


def flute(notes, length, rng, breath=0.05, vib_depth=0.006):
    """Bansuri-like line with glides, vibrato and Carnatic-style gamaka."""
    CR = 1000
    nC = int(length * CR) + 2
    logf = np.full(nC, np.nan)
    amp = np.zeros(nC)
    vib = np.zeros(nC)
    gam = np.zeros(nC)
    for st, du, fr, gk in notes:
        a, b = int(st * CR), min(nC, int((st + du) * CR))
        if b <= a:
            continue
        logf[a:b] = np.log(fr)
        n = b - a
        tt = np.arange(n) / CR
        env = np.minimum(1, tt / 0.07) * (0.85 + 0.15 * np.exp(-tt / 0.4))
        rel = int(0.14 * CR)
        env = np.concatenate([env, env[-1] * np.linspace(1, 0, rel)])
        e = min(nC, a + len(env))
        amp[a:e] = np.maximum(amp[a:e], env[:e - a])
        vib[a:b] = np.clip((tt - 0.25) / 0.35, 0, 1)
        if gk:
            up = np.log(2 ** (1.6 / 12))
            gam[a:b] = up * (0.5 - 0.5 * np.cos(2 * np.pi * 3.4 * tt)) * np.clip((tt - 0.15) / 0.2, 0, 1)
    # forward-fill pitch through rests, then glide
    first = np.nanmean(logf) if np.any(~np.isnan(logf)) else np.log(440)
    last = first
    alpha = 1 - np.exp(-1 / (0.04 * CR))
    sm = np.empty(nC)
    cur = first
    for i in range(nC):
        if not np.isnan(logf[i]):
            last = logf[i]
        cur += alpha * (last - cur)
        sm[i] = cur
    tc = np.arange(nC) / CR
    sm += gam + vib * vib_depth * np.sin(2 * np.pi * 5.2 * tc + rng.uniform(0, 6))
    sm += np.cumsum(rng.standard_normal(nC)) * 2e-5
    ta = t_axis(length)
    f = np.exp(np.interp(ta, tc, sm))
    a = np.interp(ta, tc, amp)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.22 * np.sin(2 * ph + 0.4) + 0.07 * np.sin(3 * ph + 1.1) + 0.025 * np.sin(4 * ph)
    br = fft_filter(white(len(ta), rng), bp(1500, 4500, 2)) * 0.25
    return (tone + br * breath / 0.05 * 0.12) * a


def formant_gain(f, vowel="a"):
    table = {"a": [(800, 110, 1.0), (1150, 120, 0.5), (2900, 200, 0.25)],
             "o": [(450, 80, 1.0), (800, 100, 0.45), (2830, 200, 0.1)],
             "u": [(325, 70, 1.0), (700, 90, 0.25), (2530, 200, 0.05)]}
    g = np.zeros_like(np.asarray(f, dtype=float))
    for fc, bw, a in table[vowel]:
        g += a / (1 + ((f - fc) / bw) ** 2)
    return g + 0.02


def choir(chord, length, rng, vowel="a", attack=2.5):
    """Soft 'aah' choir pad built from formant-shaped harmonics."""
    t = t_axis(length)
    out = np.zeros((len(t), 2))
    for f0 in chord:
        for v in range(3):
            det = 2 ** (rng.uniform(-7, 7) / 1200)
            vib = 1 + 0.004 * np.sin(2 * np.pi * rng.uniform(4.5, 5.5) * t + rng.uniform(0, 6))
            ph = 2 * np.pi * np.cumsum(f0 * det * vib) / SR
            voice = np.zeros_like(t)
            for n in range(1, 40):
                if n * f0 > 6000:
                    break
                voice += formant_gain(n * f0, vowel) / n ** 0.3 * np.sin(n * ph)
            out += pan(voice, rng.uniform(-0.6, 0.6))
    env = np.minimum(1, t / attack) * (0.8 + 0.2 * np.sin(2 * np.pi * t / 9.0))
    return out * env[:, None]


def strings(chord, length, rng, attack=3.0, tremolo=0.0, cutoff=2500):
    """Warm string ensemble pad (detuned additive saws)."""
    t = t_axis(length)
    out = np.zeros((len(t), 2))
    for f0 in chord:
        for v in range(4):
            det = 2 ** (rng.uniform(-9, 9) / 1200)
            ph0 = rng.uniform(0, 2 * np.pi)
            voice = np.zeros_like(t)
            for n in range(1, 30):
                fn = n * f0 * det
                if fn > 8000:
                    break
                voice += (1 / n) / np.sqrt(1 + (fn / cutoff) ** 4) * np.sin(2 * np.pi * fn * t + n * ph0)
            out += pan(voice, rng.uniform(-0.7, 0.7))
    env = np.minimum(1, t / attack)
    if tremolo:
        env = env * (0.65 + 0.35 * np.sin(2 * np.pi * tremolo * t) ** 2)
    return out * env[:, None]


# --------------------------------------------------------- percussion ------
def drum_low(rng, f_hi=120, f_lo=62, decay=0.35):
    t = t_axis(decay * 3)
    f = f_lo + (f_hi - f_lo) * np.exp(-t / 0.04)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    click = fft_filter(white(len(t), rng), bp(800, 4000)) * np.exp(-t / 0.004) * 0.3
    return fade(body + click, 0, 0.05)


def drum_ring(rng, f0=420, decay=0.28):
    t = t_axis(decay * 4)
    out = np.zeros_like(t)
    for n, a in zip([1, 2, 3, 4, 5], [1, 0.5, 0.35, 0.2, 0.1]):
        out += a * np.sin(2 * np.pi * f0 * n * (1 + 0.012 * np.exp(-t / 0.03)) * t) * np.exp(-t / (decay / n ** 0.4))
    out += fft_filter(white(len(t), rng), hp(2000)) * np.exp(-t / 0.003) * 0.4
    return fade(out, 0, 0.05)


def drum_tick(rng):
    t = t_axis(0.2)
    n = fft_filter(white(len(t), rng), bp(900, 3500)) * np.exp(-t / 0.025)
    return n + 0.5 * np.sin(2 * np.pi * 300 * t) * np.exp(-t / 0.03)


def manjira(rng, decay=0.9):
    t = t_axis(decay * 2.5)
    out = np.zeros_like(t)
    for f in [3150, 3980, 5240, 6630, 8010]:
        f *= rng.uniform(0.99, 1.01)
        out += np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / (decay * rng.uniform(0.6, 1.0)))
    out += fft_filter(white(len(t), rng), hp(4000)) * np.exp(-t / 0.01) * 2
    return fade(out * 0.3, 0, 0.1)


def drum_pattern(length, bpm, pattern, rng, sounds, swing=0.0, accent_every=None):
    """pattern: string of tokens, one per 1/4 beat. '.' = rest."""
    step = 60.0 / bpm / 4
    out = np.zeros((nsamp(length), 2))
    i, t = 0, 0.0
    while t < length:
        tok = pattern[i % len(pattern)]
        if tok != ".":
            snd, p, g = sounds[tok]
            jitter = rng.uniform(-0.006, 0.006) + (swing * step if i % 2 else 0)
            gain = g * rng.uniform(0.8, 1.0) * (1.25 if accent_every and i % accent_every == 0 else 1)
            place(out, pan(snd, p), t + jitter, gain)
        i += 1
        t += step
    return out


def _layer(*sounds):
    out = np.zeros(max(len(s) for s in sounds))
    for s in sounds:
        out[:len(s)] += s
    return out


# =============================================================== beds ======
def _mix(parts, target=0.1):
    total = None
    for x, level in parts:
        x = set_rms(stereo(x), level)
        total = x if total is None else total + x
    return set_rms(total, target)


def make_bed(mood, length=40.0, seed=0):
    """Return a seamless stereo music loop for a mood."""
    X = 4.0
    L = length + X
    rng = np.random.default_rng(1000 + MOODS.index(mood) * 17 + seed)
    sa = SA
    if mood == "calm":
        mel = melody(rng, "mohanam", sa, 72, L, register=1, density=0.6)
        parts = [(tanpura(L, sa), 0.05), (flute(mel, L, rng), 0.06),
                 (strings([sa, sa * 1.5, sa * 2], L, rng, attack=4), 0.022),
                 (_shimmer_layer(L, rng, every=11, scale="mohanam"), 0.012)]
        bed = reverb(_mix(parts), decay=3.2, mix=0.32)
    elif mood == "night":
        mel = melody(rng, "revati", sa, 54, L, register=1, density=0.35, long_notes=True)
        parts = [(tanpura(L, sa, cycle=5.4), 0.045), (flute(mel, L, rng, vib_depth=0.004), 0.045),
                 (choir([sa, sa * 1.5], L, rng, vowel="u", attack=5), 0.03),
                 (_shimmer_layer(L, rng, every=14, scale="revati"), 0.012)]
        bed = reverb(_mix(parts), decay=4.0, mix=0.4)
    elif mood == "sad":
        mel = melody(rng, "shivaranjani", sa, 56, L, register=1, density=0.45, long_notes=True)
        parts = [(tanpura(L, sa, cycle=5.0), 0.045), (flute(mel, L, rng), 0.06),
                 (strings([sa, semis(sa, 3), sa * 1.5, sa * 2], L, rng, attack=5, cutoff=1800), 0.035)]
        bed = reverb(_mix(parts), decay=3.5, mix=0.35)
    elif mood == "tension":
        low = sa / 2
        sounds = {"T": (drum_low(rng, 95, 48, 0.5), 0.0, 1.0), "t": (drum_low(rng, 80, 45, 0.3), 0.0, 0.6)}
        drums = drum_pattern(L, 64, "T..t............", rng, sounds)
        mel = melody(rng, "revati", sa / 2, 50, L, register=1, density=0.3, long_notes=True)
        parts = [(strings([low, low * 1.5, semis(low, 13)], L, rng, attack=4, cutoff=900), 0.05),
                 (strings([sa * 2, semis(sa * 2, 1)], L, rng, attack=6, tremolo=6.0, cutoff=3000), 0.012),
                 (drums, 0.05), (flute(mel, L, rng, vib_depth=0.003), 0.025)]
        bed = reverb(_mix(parts), decay=3.0, mix=0.3)
    elif mood == "storm":
        low = sa / 2
        sounds = {"T": (drum_low(rng, 110, 55, 0.4), 0.0, 1.0),
                  "t": (drum_low(rng, 140, 80, 0.2), 0.2, 0.55),
                  "n": (drum_ring(rng, 300, 0.2), -0.2, 0.45),
                  "k": (drum_tick(rng), 0.3, 0.35),
                  "B": (_impact(rng, 2.0), 0.0, 1.5)}
        drums = drum_pattern(L, 124, "B.t.T.k.n.t.T.k.T.t.T.k.n.k.T.t.", rng, sounds, accent_every=8)
        parts = [(choir([low * 2, semis(low * 2, 3), low * 3], L, rng, vowel="a", attack=2), 0.035),
                 (strings([low, low * 1.5], L, rng, attack=2, tremolo=7.5, cutoff=1500), 0.04),
                 (drums, 0.075)]
        bed = reverb(_mix(parts, 0.12), decay=2.6, mix=0.28)
    elif mood == "divine":
        mel = melody(rng, "hamsadhwani", sa, 64, L, register=1, density=0.45, long_notes=True)
        parts = [(tanpura(L, sa), 0.04),
                 (choir([sa * 2, semis(sa * 2, 4), sa * 3, sa * 4], L, rng, vowel="a", attack=4), 0.045),
                 (strings([sa, sa * 1.5, sa * 2, semis(sa * 2, 4)], L, rng, attack=5), 0.03),
                 (flute(mel, L, rng), 0.04),
                 (_shimmer_layer(L, rng, every=5, scale="hamsadhwani"), 0.025),
                 (_bell_layer(L, rng, every=9), 0.02)]
        bed = reverb(_mix(parts), decay=4.5, mix=0.42)
    elif mood == "celebration":
        sounds = {"T": (drum_low(rng, 120, 65, 0.3), -0.1, 1.0),
                  "D": (_layer(drum_low(rng, 130, 70, 0.35), drum_ring(rng, 440, 0.35) * 0.6), 0.0, 1.0),
                  "n": (drum_ring(rng, 440, 0.25), 0.2, 0.7),
                  "k": (drum_tick(rng), 0.25, 0.5)}
        drums = drum_pattern(L, 100, "D.k.n.k.T.n.k.n.D.k.n.T.k.n.T.n.", rng, sounds, swing=0.08)
        cym = drum_pattern(L, 100, "M...m...m...m...", rng,
                           {"M": (manjira(rng), 0.4, 1.0), "m": (manjira(rng, 0.6), 0.4, 0.6)})
        mel = melody(rng, "mohanam", sa, 100, L, register=1, density=1.0)
        parts = [(tanpura(L, sa, cycle=3.6), 0.035), (flute(mel, L, rng), 0.065),
                 (drums, 0.06), (cym, 0.018)]
        bed = reverb(_mix(parts), decay=2.2, mix=0.25)
    else:
        raise ValueError(f"unknown mood {mood!r}; choose from {MOODS}")
    return set_rms(loopify(bed, length, X), 0.1)


def _shimmer_layer(length, rng, every=8.0, scale="mohanam"):
    out = np.zeros((nsamp(length), 2))
    t = rng.uniform(1, every)
    while t < length:
        place(out, _shimmer(rng, scale, 1.6, 10), t)
        t += every * rng.uniform(0.7, 1.3)
    return out


def _bell_layer(length, rng, every=8.0):
    out = np.zeros((nsamp(length), 2))
    t = rng.uniform(2, every)
    while t < length:
        place(out, pan(_bell(rng, rng.choice([SA * 8, SA * 6, SA * 9]), 3.0), rng.uniform(-0.5, 0.5)), t, 0.6)
        t += every * rng.uniform(0.8, 1.2)
    return out


# ======================================================= sound effects =====
def _bell(rng, f=620.0, dur=5.0):
    t = t_axis(dur)
    out = np.zeros_like(t)
    partials = [(0.5, 0.5, 1.0), (1.0, 1.0, 0.8), (1.19, 0.5, 0.6), (1.5, 0.45, 0.5), (2.0, 0.6, 0.4),
                (2.51, 0.35, 0.3), (2.66, 0.3, 0.25), (3.01, 0.25, 0.2), (4.16, 0.15, 0.12), (5.43, 0.08, 0.08)]
    for ratio, amp, dec in partials:
        for beat in (0.0, rng.uniform(0.4, 1.6)):
            out += amp * np.sin(2 * np.pi * (f * ratio + beat) * t + rng.uniform(0, 6)) * np.exp(-t / (dur * dec * 0.45))
    out += fft_filter(white(len(t), rng), hp(2500)) * np.exp(-t / 0.004) * 1.5
    return fade(normalize(out, 0.9), 0, 0.2)


def _shimmer(rng, scale="hamsadhwani", dur=2.0, count=18):
    out = np.zeros((nsamp(dur + 2.0), 2))
    sc = SCALES[scale]
    pitches = [semis(SA * 16, s + 12 * o) for o in range(2) for s in sc]
    for i in range(count):
        f = pitches[min(len(pitches) - 1, int(i / count * len(pitches) + rng.integers(0, 2)))]
        t = t_axis(1.5)
        ping = np.sin(2 * np.pi * f * t) * np.exp(-t / rng.uniform(0.2, 0.6)) * (1 - np.exp(-t / 0.002))
        place(out, pan(ping, rng.uniform(-0.8, 0.8)), i / count * dur + rng.uniform(0, 0.05), rng.uniform(0.4, 1))
    return reverb(out, decay=2.5, mix=0.5, bright=9000)


def _impact(rng, dur=2.5):
    t = t_axis(dur)
    f = 42 + 50 * np.exp(-t / 0.06)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.6)
    crack = fft_filter(white(len(t), rng), lp(2500)) * np.exp(-t / 0.05) * 0.6
    rumble = fft_filter(white(len(t), rng), lp(180)) * np.exp(-t / 0.8) * 2
    return fade(normalize(body + crack + rumble), 0, 0.3)


def _creak(rng, dur=1.6, rate=(40, 130)):
    """Stick-slip impulse train through a resonant wooden/iron body."""
    n = nsamp(dur)
    t = np.arange(n) / SR
    r = rate[0] + (rate[1] - rate[0]) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.4 + rng.uniform(0, 0.4)) * t + 1))
    r *= 1 + 0.25 * np.cumsum(rng.standard_normal(n)) / np.sqrt(n)
    ph = np.cumsum(np.maximum(r, 5) / SR)
    imp = np.zeros(n)
    imp[np.flatnonzero(np.diff(np.floor(ph)) > 0)] = 1.0
    imp *= rng.uniform(0.5, 1.0, n)
    tb = t_axis(0.06)
    body = sum(np.sin(2 * np.pi * f * tb) * np.exp(-tb / d) for f, d in
               [(240, 0.03), (530, 0.02), (910, 0.015), (1450, 0.01), (2300, 0.006)])
    from .dsp import convolve
    out = convolve(imp, body)[:n]
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.5
    return normalize(out * env, 0.7)


def _clunk(rng, heavy=1.0):
    t = t_axis(1.5)
    thud = np.sin(2 * np.pi * (60 + 40 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.18)
    ring = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-t / d) for f, d in
               [(310, 0.5), (697, 0.35), (1180, 0.25), (1820, 0.15)]) * 0.3
    knock = fft_filter(white(len(t), rng), bp(300, 3000)) * np.exp(-t / 0.01) * 0.5
    return fade(normalize(thud * heavy + ring + knock), 0, 0.2)


def _clink(rng):
    t = t_axis(0.35)
    out = sum(np.sin(2 * np.pi * rng.uniform(1800, 6800) * t + rng.uniform(0, 6)) * np.exp(-t / rng.uniform(0.04, 0.15))
              for _ in range(5))
    out += fft_filter(white(len(t), rng), hp(3000)) * np.exp(-t / 0.003)
    return out


def make_sfx(name, seed=0):
    """Return a stereo effect. Ambiences come back as seamless 24 s loops."""
    rng = np.random.default_rng(5000 + SFX.index(name) * 31 + seed)
    if name == "temple_bell":
        x = reverb(pan(_bell(rng, 520, 7.0), 0), decay=3.5, mix=0.35, keep_len=False)
    elif name == "puja_bell":
        x = np.zeros((nsamp(4.5), 2))
        for i in range(10):
            place(x, pan(_bell(rng, 1650 * rng.uniform(0.99, 1.01), 1.6), 0.15), i * 0.24, 0.6 + 0.4 * (i % 2))
        x = reverb(x, decay=2.0, mix=0.3)
    elif name == "conch":
        dur = 3.6
        t = t_axis(dur)
        f0 = 311 * (0.86 + 0.14 * (1 - np.exp(-t / 0.18))) * (1 + 0.012 * t / dur)
        f0 *= np.where(t > dur - 0.45, 1 - 0.04 * ((t - (dur - 0.45)) / 0.45), 1)
        f0 *= 1 + 0.004 * np.sin(2 * np.pi * 4.7 * t) + 0.002 * np.sin(2 * np.pi * 7.3 * t)
        ph = 2 * np.pi * np.cumsum(f0) / SR
        tone = np.zeros_like(t)
        for n in range(1, 18):
            g = 1 / (1 + ((n * 311 - 950) / 600) ** 2) + 0.5 / (1 + ((n * 311 - 2300) / 500) ** 2) + 0.35 / n
            tone += g * np.sin(n * ph)
        env = np.minimum(1, t / 0.18) * np.minimum(1, (dur - t) / 0.4) * (0.9 + 0.1 * np.sin(2 * np.pi * 0.7 * t))
        breath = fft_filter(white(len(t), rng), bp(700, 3500)) * 0.05
        x = reverb(pan(normalize((tone + breath) * env), 0), decay=3.0, mix=0.35, keep_len=False)
    elif name == "thunder":
        dur = 7.0
        t = t_axis(dur)
        crack = fft_filter(white(len(t), rng), lp(4000, 1)) * np.exp(-np.maximum(t - 0.05, 0) / 0.12) * (t > 0.05)
        env = np.zeros_like(t)
        for _ in range(7):
            c, w, a = rng.uniform(0.1, 3.5), rng.uniform(0.15, 0.8), rng.uniform(0.4, 1.0)
            env += a * np.exp(-((t - c) / w) ** 2)
        env *= np.exp(-t / 2.5)
        rumble = fft_filter(white(len(t), rng), lp(170, 2)) * env * 5
        roll = fft_filter(white(len(t), rng), bp(150, 700)) * env * 0.8
        x = reverb(stereo(normalize(crack * 0.5 + rumble + roll)), decay=3.5, mix=0.4)
        x[:, 1] = np.roll(x[:, 1], nsamp(0.012))
    elif name == "chains":
        x = np.zeros((nsamp(2.6), 2))
        t = 0.0
        while t < 1.8:
            place(x, pan(_clink(rng), rng.uniform(-0.4, 0.4)), t, rng.uniform(0.3, 1.0))
            t += rng.exponential(0.06)
        for k in range(3):
            place(x, pan(_clunk(rng, 0.6), 0), 1.4 + k * 0.22, 0.5 - k * 0.12)
        x = reverb(x, decay=1.4, mix=0.25)
    elif name in ("gate_open", "gate_close"):
        opening = name == "gate_open"
        x = np.zeros((nsamp(3.4), 2))
        place(x, pan(_creak(rng, 2.0 if opening else 1.2, (35, 120) if opening else (60, 160)), -0.2), 0.0, 0.8)
        place(x, pan(_clunk(rng, 1.4 if not opening else 0.8), 0.1), 2.0 if opening else 1.15, 1.0)
        x = reverb(x, decay=2.2, mix=0.35, bright=3000)
    elif name == "whoosh":
        dur = 1.6
        n = white(nsamp(dur), rng)

        def g(times, freqs):
            p = np.clip(times / dur, 0, 1)[:, None]
            centre = 300 + 3200 * np.sin(np.pi * p) ** 2
            return np.exp(-((np.log(np.maximum(freqs[None, :], 20) / centre)) / 0.5) ** 2)
        y = stft_filter(n, g) * np.sin(np.pi * np.clip(t_axis(dur) / dur, 0, 1)) ** 2
        p = np.linspace(-0.8, 0.8, len(y))
        x = reverb(np.stack([y * np.cos((p + 1) * np.pi / 4), y * np.sin((p + 1) * np.pi / 4)], 1), 1.5, 0.2)
    elif name == "shimmer":
        x = _shimmer(rng, "hamsadhwani", 2.2, 26)
    elif name == "sword":
        t = t_axis(2.0)
        swish = fft_filter(white(len(t), rng), hp(3000)) * np.exp(-((t - 0.12) / 0.07) ** 2) * 0.5
        ring = sum(np.sin(2 * np.pi * f * t * (1 + 0.001 * np.sin(2 * np.pi * 6 * t))) * np.exp(-t / d)
                   for f, d in [(2650, 0.9), (4120, 0.6), (5980, 0.4), (7350, 0.3)]) * (t > 0.1)
        x = reverb(pan(normalize(swish + ring * 0.25), 0.1), decay=2.0, mix=0.3)
    elif name == "impact":
        x = reverb(pan(_impact(rng), 0), decay=3.0, mix=0.3, keep_len=False)
    # ---------------------------------------------------------- ambiences --
    elif name == "rain":
        L = 24.0 + 3
        n = nsamp(L)
        base = stereo(coloured(n, rng, 1.0))
        base[:, 1] = coloured(n, rng, 1.0)
        base = fft_filter(base, bp(350, 9000, 1))
        drops = np.zeros((n, 2))
        drop = fft_filter(white(nsamp(0.01), rng), hp(2500)) * np.exp(-t_axis(0.01) / 0.0015)
        for s in rng.integers(0, n - 500, 9000):
            c = rng.integers(0, 2)
            drops[s:s + len(drop), c] += drop * rng.uniform(0.05, 0.4)
        x = loopify(set_rms(base, 0.1) + set_rms(drops, 0.03), 24.0, 3)
    elif name == "river":
        L = 24.0 + 3
        n = nsamp(L)
        t = t_axis(L)
        flow = np.stack([coloured(n, rng, 1.6), coloured(n, rng, 1.6)], 1)
        flow = fft_filter(flow, bp(60, 2200, 1)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.17 * t))[:, None]
        bub = np.zeros((n, 2))
        for s in rng.integers(0, n - 4000, 700):
            tt = t_axis(rng.uniform(0.02, 0.07))
            f = rng.uniform(250, 900) * (1 + 1.5 * tt / tt[-1])
            blip = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1])
            bub[s:s + len(blip)] += pan(blip, rng.uniform(-0.7, 0.7)) * rng.uniform(0.1, 0.5)
        x = loopify(set_rms(flow, 0.1) + set_rms(bub, 0.025), 24.0, 3)
    elif name == "wind":
        L = 24.0 + 3
        n = white(nsamp(L), rng)
        k = rng.uniform(0, 6, 3)

        def g(times, freqs):
            centre = 520 * np.exp(0.6 * np.sin(2 * np.pi * times / 7.3 + k[0]) + 0.3 * np.sin(2 * np.pi * times / 3.1 + k[1]))[:, None]
            gain = np.exp(-((np.log(np.maximum(freqs[None, :], 20) / centre)) / 0.45) ** 2)
            return gain * (0.6 + 0.4 * np.sin(2 * np.pi * times / 5.2 + k[2]))[:, None]
        y = stft_filter(n, g)
        x = loopify(np.stack([y, np.roll(y, nsamp(0.3))], 1), 24.0, 3)
    elif name == "crickets":
        L = 24.0 + 3
        x = np.zeros((nsamp(L), 2))
        for c in range(4):
            fc = rng.uniform(4200, 5600)
            p = rng.uniform(-0.8, 0.8)
            period = rng.uniform(0.7, 1.3)
            t = rng.uniform(0, period)
            while t < L:
                tt = t_axis(0.12)
                gate = (np.sin(2 * np.pi * 30 * tt) > 0.3).astype(float)
                chirp = np.sin(2 * np.pi * fc * tt) * gate * np.sin(np.pi * tt / 0.12)
                place(x, pan(chirp, p), t, rng.uniform(0.2, 0.5))
                t += period * rng.uniform(0.9, 1.1)
        x = loopify(reverb(x, 1.2, 0.3, bright=9000), 24.0, 3)
    elif name == "heartbeat":
        L = 24.0 + 3
        x = np.zeros((nsamp(L), 2))
        t, beat = 0.0, 60 / 66
        while t < L:
            for off, f, g in ((0.0, 55, 1.0), (0.2, 65, 0.7)):
                tt = t_axis(0.3)
                th = np.sin(2 * np.pi * np.cumsum(f + 25 * np.exp(-tt / 0.02)) / SR) * np.exp(-tt / 0.07)
                place(x, pan(th, 0), t + off, g)
            t += beat
        x = loopify(fft_filter(x, lp(200)), 24.0, 3)
    else:
        raise ValueError(f"unknown sfx {name!r}; choose from {SFX}")
    x = stereo(x)
    if name in AMBIENCES:
        x = set_rms(x, 0.12)
        peak = np.max(np.abs(x))
        return x * (0.8 / peak) if peak > 0.8 else x
    return normalize(x, 0.8)
