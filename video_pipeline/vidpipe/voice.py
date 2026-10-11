"""Stage 2: narration audio per scene, with word-level timestamps for captions."""

import base64
import json
import os
import re
import shutil
import threading
import wave
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

from .config import resolve
from .util import find_silences, log, media_duration, read_json, run_ffmpeg, write_json

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


ELEVEN_API = "https://api.elevenlabs.io"


def eleven_get(path: str, key: str, **params) -> dict:
    resp = requests.get(ELEVEN_API + path, params=params, headers={"xi-api-key": key}, timeout=60)
    if resp.status_code != 200:
        raise RuntimeError(f"ElevenLabs error {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def eleven_my_voices(key: str) -> list:
    """The voices in your ElevenLabs account (premade ones plus any you added from the Voice Library)."""
    return eleven_get("/v1/voices", key).get("voices", [])


def eleven_library_voices(key: str, language: str, limit: int = 30, gender: str = "") -> list:
    """Voices other people shared in the Voice Library for a language (ISO code, e.g. "ta")."""
    params = {"language": language, "page_size": limit, **({"gender": gender} if gender else {})}
    return eleven_get("/v1/shared-voices", key, **params).get("voices", [])


def _gender(v: dict) -> str:
    return str(v.get("gender") or (v.get("labels") or {}).get("gender") or "").lower()


class ElevenLabsVoice:
    def __init__(self, cfg: dict):
        self.v = dict(cfg["voice"])
        self.key = os.environ.get("ELEVENLABS_API_KEY", "")
        if not self.key:
            raise RuntimeError("Set ELEVENLABS_API_KEY in .env")
        if not self.v.get("voice_id"):
            raise RuntimeError("Choose a voice: --voice <name or ID> (see `python make_video.py voices --provider "
                               "elevenlabs`), or set voice.voice_id in config.yaml")
        if not re.fullmatch(r"[A-Za-z0-9]{20}", self.v["voice_id"]):  # a name: look up its ID in the account
            voices = eleven_my_voices(self.key)
            match = [x for x in voices if x.get("name", "").lower().startswith(self.v["voice_id"].lower())]
            if not match:
                names = ", ".join(x.get("name", "") for x in voices)
                raise RuntimeError(f"No ElevenLabs voice called '{self.v['voice_id']}' in your account. "
                                   f"Your voices: {names}")
            self.v["voice_id"] = match[0]["voice_id"]

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
        return _spread_sentences(text, media_duration(out_mp3) - self.e["scene_pause"])


def _spread_sentences(text: str, spoken: float) -> list:
    """Stand-in word timings when a voice reports none: each sentence gets time in proportion to its length."""
    sentences = split_sentences(text)
    total = sum(len(x) for x in sentences) or 1
    t, end, out = 0.1, max(spoken, 0.2), []
    for sentence in sentences:
        span = (end - 0.1) * len(sentence) / total
        out += distribute_words(sentence, t, t + span)
        t += span
    return out


EDGE_SAMPLE_VOICES = {"tamil": ["ta-IN-ValluvarNeural", "ta-IN-PallaviNeural", "ta-LK-KumarNeural",
                                "ta-LK-SaranyaNeural", "ta-MY-SuryaNeural", "ta-MY-KaniNeural",
                                "ta-SG-AnbuNeural", "ta-SG-VenbaNeural"]}

# Each free voice is previewed in a few deliveries, since pace and depth change how gripping it sounds.
EDGE_STYLES = {"story": {"rate": "+15%", "pitch": "-4Hz"},
               "thriller": {"rate": "+25%", "pitch": "-10Hz"},
               "dramatic": {"rate": "+5%", "pitch": "-14Hz"}}


def preview_edge_voices(cfg: dict, text: str, out_dir: Path, voices: list, styles: dict = None) -> list:
    """Renders each voice in each delivery: styles maps a name to rate/pitch (default EDGE_STYLES)."""
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for v in voices:
        for name, style in (styles or EDGE_STYLES).items():
            edge = {**cfg["voice"]["edge"], **style, "voice": v}
            path = out_dir / f"{v}_{name}.mp3"
            EdgeVoice({**cfg, "voice": {**cfg["voice"], "edge": edge}}).synthesize(text, "", "", path)
            outputs.append(path)
    return outputs


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Gemini's prebuilt voices and the character Google gives each one. All of them speak Tamil.
GEMINI_VOICES = {
    "Zephyr": "bright", "Puck": "upbeat", "Charon": "informative", "Kore": "firm", "Fenrir": "excitable",
    "Leda": "youthful", "Orus": "firm", "Aoede": "breezy", "Callirrhoe": "easy-going", "Autonoe": "bright",
    "Enceladus": "breathy", "Iapetus": "clear", "Umbriel": "easy-going", "Algieba": "smooth", "Despina": "smooth",
    "Erinome": "clear", "Algenib": "gravelly", "Rasalgethi": "informative", "Laomedeia": "upbeat",
    "Achernar": "soft", "Alnilam": "firm", "Schedar": "even", "Gacrux": "mature", "Pulcherrima": "forward",
    "Achird": "friendly", "Zubenelgenubi": "casual", "Vindemiatrix": "gentle", "Sadachbia": "lively",
    "Sadaltager": "knowledgeable", "Sulafat": "warm",
}
# The ones that suit a gripping story; `voices --provider gemini --only <names>` previews any of the 30.
GEMINI_STORY_VOICES = ["Charon", "Fenrir", "Algenib", "Enceladus", "Gacrux", "Orus", "Alnilam", "Iapetus",
                       "Kore", "Sulafat", "Achernar", "Puck"]


class GeminiVoice:
    """Google Gemini text-to-speech: expressive voices steered by a plain-language style instruction
    ("tell it like a gripping thriller"). Free tier with a key from aistudio.google.com (rate-limited)."""

    def __init__(self, cfg: dict):
        self.g = cfg["voice"]["gemini"]
        self.key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
        if not self.key:
            raise RuntimeError("Set GEMINI_API_KEY in .env (free key from https://aistudio.google.com/apikey)")

    def _request(self, text: str) -> bytes:
        import time

        style = self.g.get("style", "").strip()
        body = {
            "contents": [{"parts": [{"text": f"{style}: {text}" if style else text}]}],
            "generationConfig": {
                "responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": self.g["voice"]}}},
            },
        }
        err = ""
        for attempt in range(6):
            wait = min(10 * 2 ** attempt, 60)
            try:
                resp = requests.post(GEMINI_URL.format(model=self.g["model"]), json=body, timeout=180,
                                     headers={"x-goog-api-key": self.key, "Content-Type": "application/json"})
            except requests.RequestException as e:
                resp, err = None, f"network error: {e}"
            if resp is not None and resp.status_code == 200:
                try:
                    part = resp.json()["candidates"][0]["content"]["parts"][0]
                    return base64.b64decode(part["inlineData"]["data"])
                except (KeyError, IndexError, ValueError):
                    err = f"no audio in the reply: {resp.text[:300]}"
            elif resp is not None:
                info = gemini_error(resp)
                err = f"Gemini error {resp.status_code}: {info['message']}"
                if info["hopeless"]:
                    raise RuntimeError(err + "\n" + info["hint"])
                if resp.status_code not in (429, 500, 502, 503, 504):
                    break
                wait = min(info["retry_after"] or wait, 90)
            if attempt < 5:
                log(f"  {err[:120]}...")
                log(f"  retrying in {wait:.0f}s...")
                time.sleep(wait)
        raise RuntimeError(err)

    def synthesize(self, text: str, prev_text: str, next_text: str, out_mp3: Path) -> list:
        return self.synthesize_many([text], [out_mp3])[0]

    def synthesize_many(self, texts: list, out_mp3s: list) -> list:
        """Voices several scenes in ONE request (the free tier allows only ~10 a day), then cuts the audio
        into scenes at the pauses between them. Returns each scene's word timings."""
        wav_path = out_mp3s[0].with_name(out_mp3s[0].stem + ".all.wav")
        with wave.open(str(wav_path), "wb") as w:  # Gemini sends raw 16-bit mono PCM at 24 kHz
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(24000)
            w.writeframes(self._request("\n\n".join(t.strip() for t in texts)))
        cuts = scene_cuts(texts, media_duration(wav_path), find_silences(wav_path, 0.2, -35))
        out = []
        for text, mp3, start, end in zip(texts, out_mp3s, cuts, cuts[1:]):
            run_ffmpeg(["-i", wav_path, "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-af",
                        f"apad=pad_dur={self.g['scene_pause']}", "-c:a", "libmp3lame", "-q:a", "2", mp3])
            # Gemini doesn't report word timings: spread the words over each sentence.
            out.append(_spread_sentences(text, media_duration(mp3) - self.g["scene_pause"]))
        wav_path.unlink()
        return out


def scene_cuts(texts: list, total: float, silences: list) -> list:
    """Where to cut audio of several scenes read back to back: at the pause nearest to where each scene should end
    (judged by its share of the characters), or at that estimate when no pause is close. Returns len(texts)+1 times."""
    lengths = [len(t.strip()) or 1 for t in texts]
    gaps = [(s + d / 2, d) for s, d in silences if 0 < s and s + d < total]
    cuts, done = [0.0], 0
    for n in lengths[:-1]:
        done += n
        guess = total * done / sum(lengths)
        reach = total * min(n, lengths[len(cuts)]) / sum(lengths) * 0.5  # never stray into a neighbouring scene
        near = [(abs(mid - guess) - 0.2 * d, mid) for mid, d in gaps if abs(mid - guess) <= reach and mid > cuts[-1]]
        cuts.append(round(min(near)[1] if near else max(guess, cuts[-1] + 0.1), 3))
    return cuts + [round(total, 3)]


def gemini_error(resp) -> dict:
    """Reads a Gemini error reply: its message, how long Google asks us to wait, and whether retrying is pointless
    (the daily free quota is used up, or the free tier gives this model no quota at all)."""
    try:
        e = resp.json().get("error", {})
    except ValueError:
        e = {}
    message = (e.get("message") or resp.text or "").strip().replace("\n", " ")
    retry_after, quota_ids = 0.0, []
    for d in e.get("details") or []:
        if str(d.get("retryDelay", "")).endswith("s"):
            try:
                retry_after = float(d["retryDelay"][:-1]) + 1
            except ValueError:
                pass
        quota_ids += [v.get("quotaId", "") for v in d.get("violations") or []]
    daily = any("PerDay" in q for q in quota_ids)
    no_quota = bool(re.search(r"limit:\s*0\b", message))
    if no_quota:
        hint = ("Your Google key has no free quota for this voice model. Turn on billing for the key's project at "
                "aistudio.google.com, or set voice.gemini.model in config.yaml to another TTS model.")
    elif daily:
        hint = "The free daily Gemini voice quota is used up. Try again tomorrow, or turn on billing at aistudio.google.com."
    elif resp.status_code in (401, 403):
        hint = "Check GEMINI_API_KEY in .env (create one at aistudio.google.com/apikey)."
    elif resp.status_code == 404:
        hint = "Google doesn't recognise voice.gemini.model; set it to a current TTS model in config.yaml."
    else:
        hint = ""
    return {"message": message[:400], "retry_after": retry_after,
            "hopeless": no_quota or daily or resp.status_code in (400, 401, 403, 404), "hint": hint}


def preview_eleven_voices(cfg: dict, text: str, out_dir: Path, voices: list, language: str = "ta",
                          gender: str = "") -> list:
    """Reads the sample in your account's voices (or the names/IDs given; each costs about len(text) credits), and
    downloads the free sample clip of each matching voice in the shared Voice Library so you can hear them first."""
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if not key:
        raise RuntimeError("Set ELEVENLABS_API_KEY in .env")
    out_dir.mkdir(parents=True, exist_ok=True)
    gender = gender.lower()
    mine = eleven_my_voices(key)
    outputs = []
    try:
        library = [x for x in eleven_library_voices(key, language, gender=gender) if not gender or _gender(x) == gender]
    except RuntimeError as e:
        library = []
        log(f"(couldn't list Voice Library voices: {e})")
    if library:
        print(f"\nVoice Library voices ({language}{', ' + gender if gender else ''}). Their own sample clips are saved "
              "as library_*.mp3 (free).\nTo use one, add it at elevenlabs.io/app/voice-library, then use its name:")
    for x in library:
        name = x.get("name", "")
        desc = " ".join(str(x.get(k) or "") for k in ("gender", "age", "accent", "use_case")).strip()
        print(f"  {name} [{x.get('voice_id', '')}] {desc}\n    {(x.get('description') or '')[:110]}")
        clip = out_dir / f"library_{re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')[:60]}.mp3"
        if x.get("preview_url") and not clip.exists():
            try:
                r = requests.get(x["preview_url"], timeout=60)
                if r.status_code == 200:
                    clip.write_bytes(r.content)
            except requests.RequestException:
                pass
        if clip.exists():
            outputs.append(clip)
    if voices:
        picked = voices
    else:
        picked = [x["name"] for x in mine if not gender or _gender(x) == gender][:8]
    for n, v in enumerate(picked, start=1):
        engine = ElevenLabsVoice({**cfg, "voice": {**cfg["voice"], "voice_id": v}})
        name = next((x["name"] for x in mine if x["voice_id"] == engine.v["voice_id"]), v)
        path = out_dir / f"eleven_{re.sub(r'[^A-Za-z0-9]+', '_', name).strip('_')}_{engine.v['model_id']}.mp3"
        if path.exists():
            log(f"{n}/{len(picked)} {name}: already made")
        else:
            log(f"{n}/{len(picked)} {name}...")
            engine.synthesize(text, "", "", path)
        outputs.append(path)
    print("\nYour voices: " + ", ".join(f"{x.get('name', '')} ({_gender(x) or '?'})" for x in mine))
    return outputs


def preview_gemini_voices(cfg: dict, text: str, out_dir: Path, voices: list) -> list:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []
    for v in voices:
        if v not in GEMINI_VOICES:
            raise RuntimeError(f"Unknown Gemini voice '{v}'. Choose from: {', '.join(GEMINI_VOICES)}")
    for n, v in enumerate(voices, start=1):
        path = out_dir / f"gemini_{v}_{GEMINI_VOICES[v]}.mp3"
        if path.exists():  # made on an earlier try: don't spend free quota on it again
            log(f"{n}/{len(voices)} {v}: already made")
        else:
            log(f"{n}/{len(voices)} {v} ({GEMINI_VOICES[v]})...")
            engine = GeminiVoice({**cfg, "voice": {**cfg["voice"], "gemini": {**cfg["voice"]["gemini"], "voice": v}}})
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
    if provider == "gemini":
        return GeminiVoice(cfg)
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
        [vc["provider"], vc.get("voice_id"), vc.get(vc["provider"]) if vc["provider"] in ("kokoro", "edge", "gemini") else None]
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
        mp3.with_suffix(".voice.mp3").unlink(missing_ok=True)  # the old line's untouched copy is stale now
        words = voice.synthesize(scenes[i].narration, prev_text, next_text, mp3)
        return i, {"text": scenes[i].narration, "audio": mp3.name, "sig": sig,
                   "duration": media_duration(mp3), "words": words}

    todo = [i for i in range(len(scenes)) if not fresh(i)]
    if todo:
        voice = make_voice(cfg, dry_run)
        chars = sum(len(scenes[i].narration) for i in todo)
        log(f"Generating narration for {len(todo)} scenes ({chars} characters)...")
        if hasattr(voice, "synthesize_many") and len(todo) > 1:  # one request for all of them
            mp3s = [audio_dir / f"scene_{i:03d}.mp3" for i in todo]
            for mp3 in mp3s:
                mp3.with_suffix(".voice.mp3").unlink(missing_ok=True)
            for i, mp3, words in zip(todo, mp3s, voice.synthesize_many([scenes[i].narration for i in todo], mp3s)):
                cached[str(i)] = {"text": scenes[i].narration, "audio": mp3.name, "sig": sig,
                                  "duration": media_duration(mp3), "words": words}
            write_json(timing_path, cached)
    with ThreadPoolExecutor(max_workers=max(1, cfg["voice"]["workers"])) as pool:
        for i, info in pool.map(work, range(len(scenes))):
            cached[str(i)] = info
    tempo = float(cfg["voice"].get("tempo", 1.0))
    for i in range(len(scenes)):
        _apply_tempo(audio_dir / f"scene_{i:03d}.mp3", cached[str(i)], tempo)
    write_json(timing_path, cached)
    return [cached[str(i)] for i in range(len(scenes))]


def _apply_tempo(mp3: Path, entry: dict, tempo: float) -> None:
    """Speeds the narration up (or down) without changing the voice's pitch. The voice's own recording is kept as
    scene_NNN.voice.mp3, so a new pace is applied to it again rather than re-recording (no new voice credits)."""
    if abs(entry.get("tempo", 1.0) - tempo) < 1e-6:
        return
    original = mp3.with_suffix(".voice.mp3")
    if not original.exists():
        shutil.copyfile(mp3, original)
        entry["voice_words"] = entry["words"]
    if abs(tempo - 1.0) < 1e-6:
        shutil.copyfile(original, mp3)
    else:
        run_ffmpeg(["-i", original, "-filter:a", f"atempo={tempo}", "-c:a", "libmp3lame", "-q:a", "2", mp3])
    entry["words"] = [[w, round(a / tempo, 3), round(b / tempo, 3)] for w, a, b in entry["voice_words"]]
    entry.update(duration=media_duration(mp3), tempo=tempo)
