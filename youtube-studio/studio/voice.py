"""Narration: ElevenLabs text-to-speech per scene, or split one long recording."""
import json
import os
import re
import ssl
import subprocess
import urllib.error
import urllib.request

import numpy as np

from .dsp import SR, read_audio, write_wav

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}?output_format=mp3_44100_128"


def _ssl_ctx():
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return ssl.create_default_context(cafile=ca) if ca and os.path.exists(ca) else ssl.create_default_context()


def elevenlabs(ep, only=None, force=False):
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        raise SystemExit(
            "ELEVENLABS_API_KEY is not set.\n"
            "  Add it as a secret/environment variable (never paste it into a chat or commit it), "
            "or make the audio in the ElevenLabs website and use `make.py split` instead.")
    vcfg = ep.cfg.get("voice") or {}
    voice = vcfg.get("voice_id", "")
    if not voice or voice.startswith("PASTE"):
        raise SystemExit("Set voice.voice_id in episode.yaml (ElevenLabs > Voices > your voice > copy ID).")
    narr_dir = ep.folder / "narration"
    narr_dir.mkdir(exist_ok=True)
    spoken = [sc for sc in ep.scenes if sc.text]
    for i, sc in enumerate(spoken):
        if only and sc.key not in only:
            continue
        out = narr_dir / f"{sc.key}.mp3"
        if out.exists() and not force:
            print(f"  {sc.key}: exists, skipping")
            continue
        body = {
            "text": sc.text,
            "model_id": vcfg.get("model_id", "eleven_multilingual_v2"),
            "voice_settings": {
                "stability": vcfg.get("stability", 0.45),
                "similarity_boost": vcfg.get("similarity_boost", 0.8),
                "style": vcfg.get("style", 0.3),
                "use_speaker_boost": True,
                "speed": vcfg.get("speed", 0.95),
            },
        }
        if vcfg.get("language_code"):
            body["language_code"] = vcfg["language_code"]
        # neighbouring text keeps intonation continuous across scene files
        if i > 0:
            body["previous_text"] = spoken[i - 1].text
        if i + 1 < len(spoken):
            body["next_text"] = spoken[i + 1].text
        req = urllib.request.Request(API.format(voice=voice), data=json.dumps(body).encode(),
                                     headers={"xi-api-key": key, "Content-Type": "application/json",
                                              "Accept": "audio/mpeg"})
        try:
            audio = urllib.request.urlopen(req, timeout=180, context=_ssl_ctx()).read()
        except urllib.error.HTTPError as e:
            raise SystemExit(f"ElevenLabs error for scene {sc.key}: {e.code} {e.read()[:400]!r}")
        out.write_bytes(audio)
        print(f"  {sc.key}: {len(sc.text)} chars -> {out.name}")


def _silences(path, noise_db=-35, min_len=0.45):
    proc = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(path), "-af",
                           f"silencedetect=noise={noise_db}dB:d={min_len}", "-f", "null", "-"],
                          capture_output=True, text=True)
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", proc.stderr)]
    return list(zip(starts, ends))


def split(ep, full_path):
    """Cut one long narration file into per-scene files at the pauses between scenes.

    Pauses are matched to where each scene *should* start (by text length),
    so it still works if the voice paused in other places too.
    """
    spoken = [sc for sc in ep.scenes if sc.text]
    audio = read_audio(full_path, 1)
    total = len(audio) / SR
    sil = [s for s in _silences(full_path) if s[0] > 0.3 and s[1] < total - 0.3]
    need = len(spoken) - 1
    if len(sil) < need:
        raise SystemExit(f"Found only {len(sil)} pauses but need {need}. Re-generate with a pause "
                         f"between scenes (narration_full.txt has break tags for this).")
    chars = np.array([len(sc.text) for sc in spoken], dtype=float)
    expected = np.cumsum(chars)[:-1] / chars.sum() * total
    mids = np.array([(a + b) / 2 for a, b in sil])
    widths = np.array([b - a for a, b in sil])
    # dynamic programming: choose `need` pauses in order, close to the expected boundaries,
    # preferring longer pauses
    M = len(mids)
    INF = 1e18
    cost = np.full((need, M), INF)
    back = np.zeros((need, M), dtype=int)
    pen = lambda k, j: (mids[j] - expected[k]) ** 2 - 4.0 * widths[j]
    for j in range(M):
        cost[0, j] = pen(0, j)
    for k in range(1, need):
        best, arg = INF, -1
        for j in range(M):
            if j - 1 >= 0 and cost[k - 1, j - 1] < best:
                best, arg = cost[k - 1, j - 1], j - 1
            if arg >= 0:
                cost[k, j] = best + pen(k, j)
                back[k, j] = arg
    j = int(np.argmin(cost[need - 1]))
    picks = [j]
    for k in range(need - 1, 0, -1):
        j = back[k, j]
        picks.append(j)
    picks = picks[::-1]
    cuts = [0.0] + [float(mids[p]) for p in picks] + [total]
    narr_dir = ep.folder / "narration"
    narr_dir.mkdir(exist_ok=True)
    for i, sc in enumerate(spoken):
        a, b = int(cuts[i] * SR), int(cuts[i + 1] * SR)
        seg = _trim(audio[a:b])
        write_wav(narr_dir / f"{sc.key}.wav", seg)
        print(f"  {sc.key}: {cuts[i]:7.2f}s -> {cuts[i + 1]:7.2f}s  ({len(seg) / SR:5.1f}s)  {sc.text[:40]}...")


def _trim(x, thresh=0.01, pad=0.08):
    idx = np.flatnonzero(np.abs(x) > thresh)
    if not len(idx):
        return x
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(x), idx[-1] + int(pad * SR))
    return x[a:b]


def export_text(ep):
    """Write narration_full.txt (with pause tags) for pasting into the ElevenLabs website."""
    spoken = [sc for sc in ep.scenes if sc.text]
    tagged = "\n<break time=\"1.5s\" />\n".join(sc.text for sc in spoken)
    (ep.folder / "narration_full.txt").write_text(tagged + "\n", encoding="utf-8")
    plain = "\n\n".join(f"[{sc.key}] {sc.text}" for sc in spoken)
    (ep.folder / "narration_by_scene.txt").write_text(plain + "\n", encoding="utf-8")
    return sum(len(sc.text) for sc in spoken)
