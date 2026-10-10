#!/usr/bin/env python3
"""Faceless YouTube video pipeline.

  python make_video.py make "How the Tacoma Narrows Bridge Tore Itself Apart"
  python make_video.py next --niche "Engineering Disasters"
  python make_video.py topics --niche "Engineering Disasters" --limit 20
  python make_video.py series "Dracula by Bram Stoker" --parts 20 --style "graphic novel"
  python make_video.py upload runs/<run-folder> [--shorts] [--publish-at 2026-11-01T14:30:00Z]

Add --dry-run to make/next to test everything offline (placeholder images, silent voice).
"""

import argparse
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from vidpipe import bank  # noqa: E402
from vidpipe.config import load_config  # noqa: E402
from vidpipe.pipeline import REDO, ManualStepNeeded, make_video  # noqa: E402
from vidpipe.series import SeriesStepNeeded, make_series  # noqa: E402
from vidpipe.upload import upload_run  # noqa: E402


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
    p_series.add_argument("--parts", type=int, help="number of parts (default from config: 20)")
    p_series.add_argument("--style", default="", help='visual style hint, e.g. "anime", "watercolour storybook"')
    p_series.add_argument("--notes", default="", help="anything Claude should know (focus, tone, ending)")
    p_series.add_argument("--first", type=int, default=0, help="only render the first N parts this run")
    add_make_flags(p_series)

    p_voices = sub.add_parser("voices", help="preview the free Kokoro voices (writes one mp3 per voice)")
    p_voices.add_argument("--say", default="In 1940, a brand new bridge began to twist in the wind. "
                                            "Within hours, it was gone.")
    p_voices.add_argument("--only", nargs="*", default=[], help="e.g. am_michael bm_george")

    p_up = sub.add_parser("upload", help="upload an approved run to YouTube (private)")
    p_up.add_argument("run_dir")
    p_up.add_argument("--shorts", action="store_true", help="also upload the Shorts")
    p_up.add_argument("--publish-at", default="", help="ISO 8601 UTC time to go public, e.g. 2026-11-01T14:30:00Z")

    args = parser.parse_args()
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
            make_series(args.story, args.notes, cfg, args.dry_run, args.redo or "", args.yes, args.first)
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
            from vidpipe.voice import preview_voices
            out_dir = resolve("voice_samples")
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
