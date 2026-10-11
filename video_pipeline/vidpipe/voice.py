"""Stage 2: narration audio per scene, with word-level timestamps for captions."""

import base64
import json
import os
import re
import threading
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from .config import resolve
from .util import log, media_duration, read_json, run_ffmpeg, write_json

ELEVEN_URL = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"


def alignment_to_words(alignment: dict) -> list:
    """Collapse ElevenLabs character-level alignment into [word, start, end] triples."""
    chars = alignment.get("characters") or []
    starts = alignment.get("character_start_times_seconds") or []
    ends = alignment.get("character_end_times_seconds") or []
    words, current, w_start, w_end = [], "", None, None
    for ch, st, en in zip(chars, starts, ends):
        if ch.isspace():
            if current:
                words.append([current, w_start, w_end])
            current, w_start = "", None
            continue
        if not current:
            w_start = st
        current += ch
        w_end = en
    if current:
        words.append([current, w_start, w_end])
    return words


def _even_words(text: str, duration: float, lead: float = 0.15) -> list:
    tokens = text.split()
    if not tokens:
        return []
    span = max(duration - lead - 0.2, 0.1) / len(tokens)
    return [[t, round(lead + i * span, 3), round(lead + (i + 1) * span, 3)] for i, t in enumerate(tokens)]


class ElevenLabsVoice:
    def __init__(self, cfg: dict):
        self.v = cfg["voice"]
        self.key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not self.key:
            raise RuntimeError("Set ELEVENLABS_API_KEY in .env")
        if not self.v.get("voice_id"):
            raise RuntimeError("Set voice.voice_id in config.yaml (copy it from your ElevenLabs voice library)")

    def synthesize(self, text: str, prev_text: str, next_text: str, out_mp3: Path) -> list:
        v3 = self.v["model_id"].startswith("eleven_v3")
        stability = self.v["stability"]
        if v3:  # v3 only takes 0 (creative), 0.5 (natural) or 1 (robust)
            stability = min((0.0, 0.5, 1.0), key=lambda x: abs(x - stability))
        body = {
            "text": text,
            "model_id": self.v["model_id"],
            "voice_settings": {
                "stability": stability,
                "similarity_boost": self.v["similarity_boost"],
                "style": self.v["style"],
            },
        }
        if not v3:  # neighbouring text keeps intonation continuous across scenes (v3 doesn't support it)
            body.update(previous_text=prev_text or None, next_text=next_text or None)
        resp = requests.post(
            ELEVEN_URL.format(voice_id=self.v["voice_id"]),
            params={"output_format": "mp3_44100_128"},
            headers={"xi-api-key": self.key, "Content-Type": "application/json"},
            json=body, timeout=180,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"ElevenLabs error {resp.status_code}: {resp.text[:300]}")
        data = resp.json()
        out_mp3.write_bytes(base64.b64decode(data["audio_base64"]))
        alignment = data.get("alignment") or data.get("normalized_alignment") or {}
        words = alignment_to_words(alignment)
        return words or _even_words(text, media_duration(out_mp3))


KOKORO_RELEASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"


def split_sentences(text: str) -> list:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def distribute_words(sentence: str, start: float, end: float) -> list:
    """Spread a sentence's words over [start, end], weighted by length plus a beat after
    commas, as a stand-in for real word timings (Kokoro doesn't report them)."""
    tokens = sentence.split()
    weights = [len(re.sub(r"\W", "", t)) + 2 + (3 if t[-1:] in ",;:" else 0) for t in tokens]
    total, t, out = sum(weights) or 1, start, []
    for tok, w in zip(tokens, weights):
        span = (end - start) * w / total
        out.append([tok, round(t, 3), round(t + span, 3)])
        t += span
    return out


def _download(url: str, dest: Path) -> None:
    log(f"Downloading {dest.name} (one time)...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.replace(dest)


class KokoroVoice:
    """Free, open-source voice that runs on your own computer (Apache-2.0 model)."""

    def __init__(self, cfg: dict):
        try:
            from kokoro_onnx import Kokoro
        except ImportError as e:
            raise RuntimeError("Kokoro isn't installed: pip install kokoro-onnx") from e
        k = cfg["voice"]["kokoro"]
        model_dir = resolve(k["model_dir"])
        model, voices = model_dir / k["model_file"], model_dir / "voices-v1.0.bin"
        for path in (model, voices):
            if not path.exists():
                _download(KOKORO_RELEASE + path.name, path)
        self.k = k
        self.engine = Kokoro(str(model), str(voices))
        if k["voice"] not in self.engine.get_voices():
            raise RuntimeError(f"Unknown Kokoro voice '{k['voice']}'; run `python make_video.py voices`")
        self.lock = threading.Lock()  # one synthesis at a time keeps memory use predictable

    def _speak(self, text: str):
        with self.lock:
            return self.engine.create(text, voice=self.k["voice"], speed=self.k["speed"],
                                      lang=self.k["lang"], clause_pause=self.k["clause_pause"],
                                      sentence_pause=self.k["sentence_pause"])

    def synthesize(self, text: str, prev_text: str, next_text: str, out_mp3: Path) -> list:
        import numpy as np

        pieces, words, t, sr = [], [], 0.0, 24000
        sentences = split_sentences(text)
        for i, sentence in enumerate(sentences):
            audio, sr = self._speak(sentence)
            dur = len(audio) / sr
            words += distribute_words(sentence, t, t + dur)
            pieces.append(audio)
            t += dur
            pause = self.k["sentence_pause"] if i < len(sentences) - 1 else self.k["scene_pause"]
            pieces.append(np.zeros(int(pause * sr), dtype=np.float32))
            t += pause
        samples = np.clip(np.concatenate(pieces) if pieces else np.zeros(sr, dtype=np.float32), -1, 1)
        wav_path = out_mp3.with_suffix(".wav")
        with wave.open(str(wav_path), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(sr)
            w.writeframes((samples * 32767).astype(np.int16).tobytes())
        run_ffmpeg(["-i", wav_path, "-c:a", "libmp3lame", "-q:a", "2", out_mp3])
        wav_path.unlink()
        return words


def preview_voices(cfg: dict, text: str, out_dir: Path, voices: list) -> list:
    """Render the same line in several Kokoro voices so you can pick one by ear."""
    engine = KokoroVoice(cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for v in voices or [v for v in engine.engine.get_voices() if v[:3] in ("am_", "af_", "bm_", "bf_")]:
        engine.k = {**engine.k, "voice": v}
        path = out_dir / f"{v}.mp3"
        engine.synthesize(text, "", "", path)
        outputs.append(path)
    return outputs


class EdgeVoice:
    """Free Microsoft neural voices through the edge-tts package (no key). Covers languages Kokoro can't speak,
    such as Tamil (ta-IN-ValluvarNeural, ta-IN-PallaviNeural). Needs an internet connection."""

    def __init__(self, cfg: dict):
        try:
            import edge_tts
        except ImportError as e:
            raise RuntimeError("The Tamil voice isn't installed: pip install edge-tts") from e
        self.edge_tts = edge_tts
        self.e = cfg["voice"]["edge"]

    def _stream(self, text: str, raw: Path) -> list:
        import asyncio

        words = []

        async def run():
            com = self.edge_tts.Communicate(text, self.e["voice"], rate=self.e["rate"], pitch=self.e["pitch"],
                                            boundary="WordBoundary")
            with open(raw, "wb") as f:
                async for chunk in com.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":  # offsets are in 100-nanosecond units
                        start = chunk["offset"] / 1e7
                        words.append([chunk["text"], round(start, 3), round(start + chunk["duration"] / 1e7, 3)])

        asyncio.run(run())
        return words

    def synthesize(self, text: str, prev_text: str, next_text: str, out_mp3: Path) -> list:
        raw = out_mp3.with_suffix(".raw.mp3")
        for attempt in range(3):
            try:
                words = self._stream(text, raw)
                break
            except Exception as e:  # network hiccups: retry, then explain
                if attempt == 2:
                    raise RuntimeError(f"The Edge voice failed ({e}). Check your internet connection and re-run.") from e
        run_ffmpeg(["-i", raw, "-af", f"apad=pad_dur={self.e['scene_pause']}", "-c:a", "libmp3lame", "-q:a", "2",
                    out_mp3])
        raw.unlink()
        if words:
            return words
        # No word timings for this voice: spread the words over each sentence instead.
        sentences = split_sentences(text)
        total = sum(len(x) for x in sentences) or 1
        t, end, out = 0.1, max(media_duration(out_mp3) - self.e["scene_pause"], 0.2), []
        for sentence in sentences:
            span = (end - 0.1) * len(sentence) / total
            out += distribute_words(sentence, t, t + span)
            t += span
        return out


EDGE_SAMPLE_VOICES = {"tamil": ["ta-IN-ValluvarNeural", "ta-IN-PallaviNeural", "ta-LK-KumarNeural",
                                "ta-LK-SaranyaNeural", "ta-MY-SuryaNeural", "ta-MY-KaniNeural"]}


def preview_edge_voices(cfg: dict, text: str, out_dir: Path, voices: list, settings: dict = None) -> list:
    """settings: rate/pitch overrides, e.g. the language's storytelling pace from series.languages."""
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    edge = {**cfg["voice"]["edge"], **{k: v for k, v in (settings or {}).items() if k in ("rate", "pitch") and v}}
    for v in voices:
        engine = EdgeVoice({**cfg, "voice": {**cfg["voice"], "edge": {**edge, "voice": v}}})
        path = out_dir / f"{v}.mp3"
        engine.synthesize(text, "", "", path)
        outputs.append(path)
    return outputs


class DummyVoice:
    """Silent audio paced at ~2.6 words/second; used by --dry-run."""

    def __init__(self, cfg: dict):
        pass

    def synthesize(self, text: str, prev_text: str, next_text: str, out_mp3: Path) -> list:
        duration = round(len(text.split()) / 2.6 + 0.5, 2)
        run_ffmpeg(["-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono", "-t", duration,
                    "-c:a", "libmp3lame", "-q:a", "6", out_mp3])
        return _even_words(text, duration)


def make_voice(cfg: dict, dry_run: bool):
    if dry_run:
        return DummyVoice(cfg)
    provider = cfg["voice"]["provider"]
    if provider == "elevenlabs":
        return ElevenLabsVoice(cfg)
    if provider == "kokoro":
        return KokoroVoice(cfg)
    if provider == "edge":
        return EdgeVoice(cfg)
    raise RuntimeError(f"Unknown voice.provider '{provider}'")


def narrate_scenes(scenes: list, run_dir: Path, cfg: dict, dry_run: bool) -> list:
    """Returns per-scene timing: [{audio, duration, words}] (word times relative to the scene)."""
    audio_dir = run_dir / "audio"
    audio_dir.mkdir(exist_ok=True)
    timing_path = audio_dir / "timing.json"
    cached = read_json(timing_path, {}) or {}
    voice = None
    # Re-voice a scene when its text OR the voice settings change (speed, pauses, voice).
    vc = cfg["voice"]
    sig = "dry" if dry_run else json.dumps(
        [vc["provider"], vc.get("voice_id"), vc.get(vc["provider"]) if vc["provider"] in ("kokoro", "edge") else None]
        + ([vc.get(k) for k in ("model_id", "stability", "similarity_boost", "style")]
           if vc["provider"] == "elevenlabs" else []),
        sort_keys=True)

    def fresh(i):
        entry = cached.get(str(i), {})
        return ((audio_dir / f"scene_{i:03d}.mp3").exists() and entry.get("text") == scenes[i].narration
                and entry.get("sig", sig) == sig)

    def work(i):
        nonlocal voice
        mp3 = audio_dir / f"scene_{i:03d}.mp3"
        key = str(i)
        if fresh(i):
            return i, cached[key]
        prev_text = scenes[i - 1].narration if i > 0 else ""
        next_text = scenes[i + 1].narration if i + 1 < len(scenes) else ""
        words = voice.synthesize(scenes[i].narration, prev_text, next_text, mp3)
        return i, {"text": scenes[i].narration, "audio": mp3.name, "sig": sig,
                   "duration": media_duration(mp3), "words": words}

    todo = [i for i in range(len(scenes)) if not fresh(i)]
    if todo:
        voice = make_voice(cfg, dry_run)
        chars = sum(len(scenes[i].narration) for i in todo)
        log(f"Generating narration for {len(todo)} scenes ({chars} characters)...")
    with ThreadPoolExecutor(max_workers=max(1, cfg["voice"]["workers"])) as pool:
        for i, info in pool.map(work, range(len(scenes))):
            cached[str(i)] = info
    write_json(timing_path, cached)
    return [cached[str(i)] for i in range(len(scenes))]
