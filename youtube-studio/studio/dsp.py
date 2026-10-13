"""Small numpy-only DSP toolkit used by the sound generators and the mixer."""
import subprocess

import numpy as np

SR = 44100


def t_axis(dur):
    return np.arange(int(round(dur * SR))) / SR


def nsamp(sec):
    return int(round(sec * SR))


# ---------------------------------------------------------------- filters --
def _next_pow2(n):
    return 1 << (int(n) - 1).bit_length()


def fft_filter(x, gain_fn):
    """Zero-phase filter: multiply the spectrum by gain_fn(freqs)."""
    x = np.asarray(x, dtype=np.float64)
    if x.ndim == 2:
        return np.stack([fft_filter(x[:, c], gain_fn) for c in range(x.shape[1])], axis=1)
    n = len(x)
    nfft = _next_pow2(n + 4096)
    spec = np.fft.rfft(x, nfft)
    spec *= gain_fn(np.fft.rfftfreq(nfft, 1 / SR))
    return np.fft.irfft(spec, nfft)[:n]


def lp(fc, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (f / fc) ** (2 * order))


def hp(fc, order=2):
    return lambda f: 1.0 / np.sqrt(1.0 + (fc / np.maximum(f, 1e-3)) ** (2 * order))


def bp(lo, hi, order=2):
    lo_f, hi_f = hp(lo, order), lp(hi, order)
    return lambda f: lo_f(f) * hi_f(f)


def stft_filter(x, gain_fn, n_fft=2048, hop=512):
    """Time-varying filter. gain_fn(times[frames], freqs[bins]) -> (frames, bins)."""
    x = np.asarray(x, dtype=np.float64)
    n = len(x)
    pad = n_fft
    xp = np.concatenate([np.zeros(pad), x, np.zeros(pad + n_fft)])
    win = np.sqrt(np.hanning(n_fft + 1)[:-1])
    n_frames = (len(xp) - n_fft) // hop + 1
    idx = np.arange(n_fft)[None, :] + hop * np.arange(n_frames)[:, None]
    spec = np.fft.rfft(xp[idx] * win, axis=1)
    times = (np.arange(n_frames) * hop + n_fft / 2 - pad) / SR
    freqs = np.fft.rfftfreq(n_fft, 1 / SR)
    spec *= gain_fn(times, freqs)
    frames = np.fft.irfft(spec, n_fft, axis=1) * win
    out = np.zeros(len(xp))
    norm = np.zeros(len(xp))
    w2 = win * win
    for i in range(n_frames):
        s = i * hop
        out[s:s + n_fft] += frames[i]
        norm[s:s + n_fft] += w2
    out /= np.maximum(norm, 1e-6)
    return out[pad:pad + n]


# ------------------------------------------------------------------ noise --
def white(n, rng):
    return rng.standard_normal(n)


def coloured(n, rng, exponent):
    """Noise with power spectrum ~ 1/f^exponent (1 = pink, 2 = brown)."""
    w = rng.standard_normal(n)
    return normalize(fft_filter(w, lambda f: 1.0 / np.maximum(f, 20.0) ** (exponent / 2)), 0.5)


# ----------------------------------------------------------------- shaping --
def normalize(x, peak=0.9):
    m = np.max(np.abs(x)) if len(x) else 0
    return x * (peak / m) if m > 0 else x


def rms(x):
    return float(np.sqrt(np.mean(np.square(x)))) if len(x) else 0.0


def set_rms(x, target):
    r = rms(x)
    return x * (target / r) if r > 0 else x


def fade(x, fin=0.01, fout=0.01):
    x = x.copy()
    a, b = nsamp(fin), nsamp(fout)
    if a:
        ramp = np.sin(np.linspace(0, np.pi / 2, a)) ** 2
        x[:a] *= ramp if x.ndim == 1 else ramp[:, None]
    if b:
        ramp = np.cos(np.linspace(0, np.pi / 2, b)) ** 2
        x[-b:] *= ramp if x.ndim == 1 else ramp[:, None]
    return x


def pan(mono, p=0.0):
    ang = (np.clip(p, -1, 1) + 1) * np.pi / 4
    return np.stack([mono * np.cos(ang), mono * np.sin(ang)], axis=1)


def stereo(x):
    return x if x.ndim == 2 else np.stack([x, x], axis=1)


def place(dst, src, start_sec, gain=1.0):
    s = nsamp(start_sec)
    if s >= len(dst):
        return
    if s < 0:
        src = src[-s:]
        s = 0
    e = min(len(dst), s + len(src))
    if e > s:
        dst[s:e] += gain * src[:e - s]


def loopify(x, length, xfade):
    """Cut x to `length` seconds so it loops seamlessly (needs length+xfade audio)."""
    L, X = nsamp(length), nsamp(xfade)
    x = stereo(x)
    if len(x) < L + X:
        x = np.concatenate([x, np.zeros((L + X - len(x), 2))])
    out = x[:L].copy()
    th = np.linspace(0, np.pi / 2, X)[:, None]
    out[:X] = x[:X] * np.sin(th) + x[L:L + X] * np.cos(th)
    return out


def tile(loop, n):
    """Repeat a seamless loop to n samples."""
    reps = int(np.ceil(n / len(loop))) + 1
    return np.concatenate([loop] * reps)[:n]


def soft_limit(x, ceiling=0.97):
    peak = np.max(np.abs(x)) if len(x) else 0
    if peak <= ceiling:
        return x
    return np.tanh(x / ceiling) * ceiling


# ----------------------------------------------------------------- reverb --
def convolve(x, ir):
    n = len(x) + len(ir) - 1
    nfft = _next_pow2(n)
    return np.fft.irfft(np.fft.rfft(x, nfft) * np.fft.rfft(ir, nfft), nfft)[:n]


def reverb(x, decay=2.5, mix=0.3, pre=0.02, bright=5000, seed=7, keep_len=True):
    """Simple synthetic hall: stereo decorrelated noise impulse response."""
    rng = np.random.default_rng(seed)
    x = stereo(np.asarray(x, dtype=np.float64))
    t = t_axis(decay)
    env = np.exp(-6.9 * t / decay)
    out_ch = []
    for c in range(2):
        ir = rng.standard_normal(len(t)) * env
        ir = fft_filter(ir, lp(bright, 1))
        ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
        ir = np.concatenate([np.zeros(nsamp(pre)), ir])
        wet = convolve(x[:, c], ir)
        dry = np.concatenate([x[:, c], np.zeros(len(wet) - len(x))])
        out_ch.append(dry * (1 - mix) + wet * mix)
    out = np.stack(out_ch, axis=1)
    return out[:len(x)] if keep_len else out


# --------------------------------------------------------------------- io --
def write_wav(path, x):
    import wave
    x = stereo(np.asarray(x, dtype=np.float64))
    data = (np.clip(x, -1, 1) * 32767).astype("<i2")
    with wave.open(str(path), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def read_audio(path, channels=2):
    """Decode any audio file (mp3, wav, m4a ...) with ffmpeg into float samples."""
    cmd = ["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", str(channels),
           "-ar", str(SR), "-"]
    raw = subprocess.run(cmd, check=True, capture_output=True).stdout
    x = np.frombuffer(raw, dtype="<f4").astype(np.float64)
    return x.reshape(-1, channels) if channels > 1 else x
