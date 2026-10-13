#!/usr/bin/env python3
"""Mythology video studio - turns an episode folder into a finished YouTube video.

  python make.py check  episodes/ep01_kannan_pirandhan     what's ready / missing
  python make.py text   episodes/ep01_kannan_pirandhan     narration text for ElevenLabs
  python make.py voice  episodes/ep01_kannan_pirandhan     ElevenLabs API, one file per scene
  python make.py split  episodes/ep01_kannan_pirandhan full.mp3   cut one long recording
  python make.py render episodes/ep01_kannan_pirandhan [--preview]
  python make.py short  episodes/ep01_kannan_pirandhan --from 15 --to 18
  python make.py thumb  episodes/ep01_kannan_pirandhan
  python make.py sounds                                    build + preview all music/SFX
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from studio import episode as episode_mod  # noqa: E402


def cmd_check(args):
    ep = episode_mod.load(args.episode)
    from studio import library
    print(f"\n{ep.cfg.get('title', ep.slug)}\n")
    print(f"{'scene':6} {'start':>6} {'secs':>5}  {'voice':9} {'visual':28} {'music':12} sfx / ambience")
    missing_img, missing_voice = [], []
    for sc in ep.scenes:
        voice = "-" if not sc.text else ("estimate" if sc.estimated else "ok")
        if sc.text and sc.estimated:
            missing_voice.append(sc.key)
        if sc.visual_source == "PLACEHOLDER":
            missing_img.append(sc.key)
        fx = ", ".join([s.name for s in sc.sfx] + [f"~{a}" for a in sc.ambience])
        print(f"{sc.key:6} {sc.start:6.1f} {sc.duration:5.1f}  {voice:9} {sc.visual_source[:28]:28} "
              f"{sc.music:12} {fx}")
    mins, secs = divmod(int(round(ep.total)), 60)
    print(f"\nTotal length: {mins}:{secs:02d}" + ("  (estimated - narration not recorded yet)" if missing_voice else ""))
    if missing_img:
        print(f"Images still needed ({len(missing_img)}): {', '.join(missing_img)}")
    if missing_voice:
        print(f"Narration still needed ({len(missing_voice)} scenes)")
    moods = sorted({sc.music for sc in ep.scenes})
    print("Music: " + "; ".join(f"{m} = {library.source_of('music', m)}" for m in moods))


def cmd_text(args):
    from studio import voice
    ep = episode_mod.load(args.episode)
    n = voice.export_text(ep)
    episode_mod.write_prompts(ep)
    print(f"Wrote narration_full.txt, narration_by_scene.txt ({n} characters) and IMAGE_PROMPTS.md.")


def cmd_voice(args):
    from studio import voice
    ep = episode_mod.load(args.episode)
    voice.elevenlabs(ep, only=set(args.scenes.split(",")) if args.scenes else None, force=args.force)


def cmd_split(args):
    from studio import voice
    ep = episode_mod.load(args.episode)
    voice.split(ep, Path(args.file).resolve())


def cmd_render(args):
    from studio import fonts, mixer, subs, video
    from studio.dsp import write_wav
    t0 = time.time()
    fonts.ensure()
    ep = episode_mod.load(args.episode)
    ep.build.mkdir(exist_ok=True)
    preview = args.preview
    size = (1280, 720) if preview else (1920, 1080)
    fps = int(ep.cfg["fps"])
    crf_seg, crf_out = (26, 28) if preview else (17, 20)
    est = [sc.key for sc in ep.scenes if sc.text and sc.estimated]
    if est:
        print(f"Note: {len(est)} scenes have no narration yet - timing is estimated and they will be silent.")
    print("1/4 soundtrack ...")
    audio = ep.build / "soundtrack.wav"
    write_wav(audio, mixer.build(ep))
    print("2/4 subtitles ...")
    ass = ep.build / f"{ep.slug}.ass"
    srt = ep.build / f"{ep.slug}.srt"
    n = subs.write(ep, ass, srt)
    print(f"    {n} subtitle lines")
    print("3/4 scenes (Ken Burns + clips) ...")
    workers = args.workers or max(1, (os.cpu_count() or 2) - 1)
    segs = video.render_segments(ep, size, fps, crf_seg, workers)
    print("4/4 final cut ...")
    out = ep.build / f"{ep.slug}{'_preview' if preview else ''}.mp4"
    burn = ep.cfg["burn_subtitles"] and not args.no_subs
    video.assemble(ep, segs, audio, ass if burn else None, out, fps, crf_out,
                   preset="veryfast" if preview else "medium")
    timeline = [{"scene": sc.key, "start": round(sc.start, 3), "duration": round(sc.duration, 3)}
                for sc in ep.scenes]
    (ep.build / "timeline.json").write_text(json.dumps(timeline, indent=1))
    mb = out.stat().st_size / 1e6
    m, s = divmod(int(round(ep.total)), 60)
    print(f"\nDone in {time.time() - t0:.0f}s -> {out}  ({m}:{s:02d}, {mb:.1f} MB)")
    print(f"Subtitles for YouTube upload: {srt}")


def cmd_short(args):
    from studio import fonts, video
    fonts.ensure()
    ep = episode_mod.load(args.episode)
    src = ep.build / f"{ep.slug}.mp4"
    if not src.exists():
        src = ep.build / f"{ep.slug}_preview.mp4"
    if not src.exists():
        raise SystemExit("Render the episode first.")
    keys = {sc.key: sc for sc in ep.scenes}
    a, b = keys[f"{int(args.start):02d}"], keys[f"{int(args.end):02d}"]
    start, end = a.start, b.start + b.duration
    if end - start > 180:
        print("Warning: Shorts must be 3 minutes or less.")
    title = args.title or ep.cfg.get("short_title") or ep.cfg.get("title", "")
    out = ep.build / f"{ep.slug}_short_{args.start}-{args.end}.mp4"
    video.make_short(src, start, end, title.replace("\\n", "\n"), out)
    print(f"Short ({end - start:.0f}s) -> {out}")


def cmd_thumb(args):
    from studio import fonts, video
    fonts.ensure()
    ep = episode_mod.load(args.episode)
    title = args.title or ep.cfg.get("thumbnail_text") or ep.cfg.get("title", "")
    ep.build.mkdir(exist_ok=True)
    out = video.thumbnail(ep, ep.build / "thumbnail.jpg", title.replace("\\n", "\n"))
    print(f"Thumbnail -> {out}")


def cmd_sounds(args):
    from studio import library
    print("Building music beds and sound effects ...")
    library.build_all()
    out = library.ROOT / "assets" / "_generated" / "sound_preview.wav"
    order = library.demo_reel(out)
    print(f"Preview reel -> {out}\nOrder: " + " | ".join(order))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in [("check", cmd_check), ("text", cmd_text), ("voice", cmd_voice), ("split", cmd_split),
                     ("render", cmd_render), ("short", cmd_short), ("thumb", cmd_thumb)]:
        p = sub.add_parser(name)
        p.add_argument("episode")
        p.set_defaults(fn=fn)
        if name == "voice":
            p.add_argument("--scenes", help="comma list, e.g. 03,04")
            p.add_argument("--force", action="store_true", help="re-generate existing files")
        if name == "split":
            p.add_argument("file", help="one long narration mp3/wav")
        if name == "render":
            p.add_argument("--preview", action="store_true", help="fast 720p draft")
            p.add_argument("--no-subs", action="store_true", help="don't burn subtitles in")
            p.add_argument("--workers", type=int)
        if name == "short":
            p.add_argument("--from", dest="start", required=True, help="first scene number")
            p.add_argument("--to", dest="end", required=True, help="last scene number")
            p.add_argument("--title")
        if name == "thumb":
            p.add_argument("--title")
    p = sub.add_parser("sounds")
    p.set_defaults(fn=cmd_sounds)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
