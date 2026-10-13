"""Narrate an episode with ElevenLabs and save word timings.

Reads  <episode>/story.json
Writes <episode>/voice.mp3       narration
       <episode>/alignment.json  per-character start/end times (drives scene cuts + captions)

Usage:
    export ELEVENLABS_API_KEY=...            # elevenlabs.io -> Profile -> API keys
    export ELEVENLABS_VOICE_ID=...           # or put "voice_id" in story.json
    python3 scripts/make_voice.py episodes/01-govardhan
    python3 scripts/make_voice.py episodes/01-govardhan --fake   # no API call: silent
                                                                 # audio + estimated timings
"""
import base64
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

API = "https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_192"
DEFAULT_MODEL = "eleven_multilingual_v2"  # handles English, Hindi, Tamil, Telugu, ...


def narration_text(story):
    return " ".join(s["narration"].strip() for s in story["scenes"])


def call_elevenlabs(story, text):
    key = os.environ.get("ELEVENLABS_API_KEY")
    voice = story.get("voice_id") or os.environ.get("ELEVENLABS_VOICE_ID")
    if not key or not voice:
        sys.exit("Set ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID (or story.json voice_id).")
    settings = {"stability": 0.45, "similarity_boost": 0.8, "style": 0.35,
                "use_speaker_boost": True, "speed": 1.0}
    settings.update(story.get("voice_settings", {}))
    body = json.dumps({
        "text": text,
        "model_id": story.get("model_id", DEFAULT_MODEL),
        "voice_settings": settings,
    }).encode()
    req = urllib.request.Request(API.format(voice=voice), data=body, method="POST", headers={
        "xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs error {e.code}: {e.read().decode(errors='replace')}")
    return base64.b64decode(data["audio_base64"]), data["alignment"]


def fake_voice(text, mp3_path, chars_per_sec=15.0):
    """Evenly spaced timings + silent audio, for testing the edit without spending credits."""
    starts = [i / chars_per_sec for i in range(len(text))]
    ends = [t + 1 / chars_per_sec for t in starts]
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
                    "anullsrc=r=44100:cl=mono", "-t", f"{ends[-1]:.3f}", "-c:a", "libmp3lame",
                    "-b:a", "128k", mp3_path], check=True)
    return {"characters": list(text), "character_start_times_seconds": starts,
            "character_end_times_seconds": ends}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        sys.exit(__doc__)
    ep = args[0]
    with open(os.path.join(ep, "story.json"), encoding="utf-8") as f:
        story = json.load(f)
    text = narration_text(story)
    mp3 = os.path.join(ep, "voice.mp3")
    words = len(text.split())
    print(f"{words} words (~{words / 2.5:.0f} s at a normal storytelling pace)")

    if "--fake" in sys.argv:
        alignment = fake_voice(text, mp3)
    else:
        audio, alignment = call_elevenlabs(story, text)
        with open(mp3, "wb") as f:
            f.write(audio)
    with open(os.path.join(ep, "alignment.json"), "w", encoding="utf-8") as f:
        json.dump(alignment, f, ensure_ascii=False)

    dur = alignment["character_end_times_seconds"][-1]
    print(f"wrote {mp3}  ({dur:.1f} s of speech)")
    if dur > 57:
        print("WARNING: narration is over ~57 s; trim the story or raise voice_settings.speed "
              "(max 1.2) to keep the Short under 60 s.")


if __name__ == "__main__":
    main()
