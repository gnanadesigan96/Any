#!/usr/bin/env python3
"""Faceless YouTube video pipeline.

  python make_video.py make "How the Tacoma Narrows Bridge Tore Itself Apart"
  python make_video.py next --niche "Engineering Disasters"
  python make_video.py topics --niche "Engineering Disasters" --limit 20
  python make_video.py series "Dracula by Bram Stoker" --parts 3 --style "graphic novel"
  python make_video.py upload runs/<run-folder> [--shorts] [--publish-at 2026-11-01T14:30:00Z]

Add --dry-run to make/next to test everything offline (placeholder images, silent voice).
"""

import argparse
import os
import random
import sys
from pathlib import Path

# macOS prints a harmless "MallocStackLogging" line for every subprocess when these are inherited.
for _var in ("MallocStackLogging", "MallocStackLoggingNoCompact"):
    os.environ.pop(_var, None)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vidpipe import bank  # noqa: E402
from vidpipe.config import load_config  # noqa: E402
from vidpipe.pipeline import REDO, ManualStepNeeded, make_video  # noqa: E402
from vidpipe.series import SeriesStepNeeded, make_series  # noqa: E402

TAMIL_SAMPLE = "ப்ரோ, அவன் கண்ணாடிய பாக்குறான். பின்னாடி ஒருத்தன் நிக்குறான். ஆனா கண்ணாடில… யாருமே இல்ல! என்ன ப்ரோ நடக்குது இங்க?!"
from vidpipe.upload import upload_run  # noqa: E402


def _join_signed_values(argv: list) -> list:
    """argparse reads "-6Hz" in `--voice-pitch -6Hz` as an option; pass it as `--voice-pitch=-6Hz` instead."""
    out, i = [], 0
    while i < len(argv):
        if argv[i] in ("--voice-rate", "--voice-pitch") and i + 1 < len(argv):
            out.append(f"{argv[i]}={argv[i + 1]}")
            i += 2
        else:
            out.append(argv[i])
            i += 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", help="path to config.yaml (default: ./config.yaml)")
    sub = parser.add_subparsers(dest="command", required=True)

    def add_make_flags(p):
        p.add_argument("--dry-run", action="store_true", help="no API calls: placeholder images and silent audio")
        p.add_argument("--redo", choices=sorted(REDO), help="throw away this stage's output (and everything after it)")
        p.add_argument("--yes", "-y", action="store_true", help="don't ask before spending API credits")

    p_make = sub.add_parser("make", help="make a video for a topic")
    p_make.add_argument("topic")
    p_make.add_argument("--angle", default="", help="optional hook/angle to build the script around")
    add_make_flags(p_make)

    p_next = sub.add_parser("next", help="make a video for the next unused topic in the topic bank")
    p_next.add_argument("--niche", required=True)
    p_next.add_argument("--subcategory", default="")
    p_next.add_argument("--random", action="store_true", help="pick a random unused topic instead of the first")
    add_make_flags(p_next)

    p_topics = sub.add_parser("topics", help="list unused topics from the topic bank")
    p_topics.add_argument("--niche", default="")
    p_topics.add_argument("--subcategory", default="")
    p_topics.add_argument("--limit", type=int, default=25)

    p_series = sub.add_parser("series", help="retell one story as a numbered series of Shorts")
    p_series.add_argument("story", help='e.g. "Dracula by Bram Stoker" or a movie title')
    p_series.add_argument("--parts", type=int, help="number of parts (default from config: 3)")
    p_series.add_argument("--style", default="", help='visual style hint, e.g. "anime", "watercolour storybook"')
    p_series.add_argument("--notes", default="", help="anything Claude should know (focus, tone, ending)")
    p_series.add_argument("--first", type=int, default=0, help="only render the first N parts this run")
    p_series.add_argument("--language", default="", help='narration language, e.g. "Tamil" (default: English)')
    p_series.add_argument("--voice", default="",
                          help="Edge voice for non-English narration, e.g. ta-IN-PallaviNeural (with "
                               "--voice-provider gemini: a Gemini voice such as Charon; elevenlabs: a voice ID)")
    p_series.add_argument("--voice-rate", default="", help='speak faster/slower (non-English voices), e.g. +20%% or -5%%')
    p_series.add_argument("--voice-pitch", default="", help='deeper/higher (non-English voices), e.g. -6Hz or +2Hz')
    p_series.add_argument("--voice-provider", choices=["auto", "edge", "gemini", "elevenlabs"], default="",
                          help="gemini: expressive storyteller voice, free tier (GEMINI_API_KEY); "
                               "elevenlabs: most expressive (paid, ELEVENLABS_API_KEY)")
    p_series.add_argument("--voice-style", default="",
                          help='how a Gemini voice should tell it, e.g. "Whisper it like a ghost story, slow and tense"')
    p_series.add_argument("--script-dir", default="", help="use a ready-made script, e.g. stories/dracula")
    p_series.add_argument("--scenes-per-image", type=int, default=0,
                          help="reuse each picture for N scenes (2 halves image-generation time)")
    add_make_flags(p_series)

    p_voices = sub.add_parser("voices", help="preview the free Kokoro voices (writes one mp3 per voice)")
    p_voices.add_argument("--say", default="In 1940, a brand new bridge began to twist in the wind. "
                                            "Within hours, it was gone.")
    p_voices.add_argument("--only", nargs="*", default=[], help="e.g. am_michael bm_george")
    p_voices.add_argument("--language", default="", help='e.g. "Tamil": preview the free Tamil voices instead')
    p_voices.add_argument("--provider", choices=["edge", "gemini"], default="edge",
                          help="gemini: preview Google's expressive voices (needs GEMINI_API_KEY)")
    p_voices.add_argument("--style", default="", help="Gemini only: how to tell it (default from config)")

    p_up = sub.add_parser("upload", help="upload an approved run to YouTube (private)")
    p_up.add_argument("run_dir")
    p_up.add_argument("--shorts", action="store_true", help="also upload the Shorts")
    p_up.add_argument("--publish-at", default="", help="ISO 8601 UTC time to go public, e.g. 2026-11-01T14:30:00Z")

    args = parser.parse_args(_join_signed_values(sys.argv[1:]))
    cfg = load_config(args.config)

    try:
        if args.command == "make":
            make_video(args.topic, args.angle, cfg, args.dry_run, args.redo or "", args.yes)
        elif args.command == "next":
            pending = [] if args.dry_run else bank.unfinished(cfg, args.niche)
            if pending:
                row = pending[0]
                print(f"Resuming unfinished video: {row['title']}")
            else:
                rows = bank.unused(cfg, args.niche, args.subcategory)
                if not rows:
                    print("No unused topics left for that niche/subcategory.")
                    return 1
                row = random.choice(rows) if args.random else rows[0]
                print(f"Topic: {row['title']}\nAngle: {row['angle']}")
            make_video(row["title"], row["angle"], cfg, args.dry_run, args.redo or "", args.yes)
        elif args.command == "series":
            if args.parts:
                cfg["series"]["parts"] = args.parts
            if args.style:
                cfg["series"]["style_hint"] = args.style
            if args.language:
                cfg["series"]["language"] = args.language
            if args.voice_provider:
                cfg["series"]["voice_provider"] = args.voice_provider
            if args.voice:
                key = {"elevenlabs": "voice_id", "gemini": "gemini_voice"}.get(cfg["series"].get("voice_provider"),
                                                                                  "edge_voice")
                cfg["series"][key] = args.voice
            if args.voice_style:
                cfg["voice"]["gemini"]["style"] = args.voice_style
            if args.voice_rate:
                cfg["series"]["voice_rate"] = args.voice_rate if args.voice_rate[0] in "+-" else "+" + args.voice_rate
            if args.voice_pitch:
                cfg["series"]["voice_pitch"] = args.voice_pitch if args.voice_pitch[0] in "+-" else "+" + args.voice_pitch
            if args.scenes_per_image:
                cfg["series"]["scenes_per_image"] = args.scenes_per_image
            make_series(args.story, args.notes, cfg, args.dry_run, args.redo or "", args.yes, args.first,
                        args.script_dir)
        elif args.command == "topics":
            if not args.niche:
                print("Niches:\n  " + "\n  ".join(bank.niches(cfg)))
                return 0
            rows = bank.unused(cfg, args.niche, args.subcategory)
            for row in rows[: args.limit]:
                print(f"[{row['subcategory']}] {row['title']}\n    {row['angle']}")
            print(f"\n{len(rows)} unused topics in '{args.niche}'.")
        elif args.command == "voices":
            from vidpipe.config import resolve
            from vidpipe.voice import (EDGE_SAMPLE_VOICES, GEMINI_STORY_VOICES, preview_edge_voices,
                                       preview_gemini_voices, preview_voices)
            out_dir = resolve("voice_samples")
            lang = args.language.lower()
            if args.provider == "gemini":
                say = args.say if "--say" in sys.argv else TAMIL_SAMPLE if lang in ("", "tamil") else args.say
                if args.style:
                    cfg["voice"]["gemini"]["style"] = args.style
                for path in preview_gemini_voices(cfg, say, out_dir, args.only or GEMINI_STORY_VOICES):
                    print(path)
                print("Listen, then add --voice-provider gemini --voice <Name> to the series command.")
            elif lang and lang != "english":
                if lang not in EDGE_SAMPLE_VOICES and not args.only:
                    raise RuntimeError(f"No sample voices listed for {args.language}; pass them with --only")
                say = args.say if "--say" in sys.argv else TAMIL_SAMPLE
                for path in preview_edge_voices(cfg, say, out_dir, args.only or EDGE_SAMPLE_VOICES[lang]):
                    print(path)
                print("Each voice is in 3 deliveries: story (+15%, -4Hz), thriller (+25%, -10Hz), dramatic "
                      "(+5%, -14Hz).\nPick one, e.g. --voice ta-IN-ValluvarNeural --voice-rate +25% --voice-pitch -10Hz")
            else:
                for path in preview_voices(cfg, args.say, out_dir, args.only):
                    print(path)
                print("Listen, then set voice.kokoro.voice in config.yaml to the one you like.")
        elif args.command == "upload":
            upload_run(Path(args.run_dir).resolve(), cfg, args.shorts, args.publish_at)
    except (ManualStepNeeded, SeriesStepNeeded) as e:
        print(e)
        return 0
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
