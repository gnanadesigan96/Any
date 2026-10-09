import base64
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vidpipe import bank, images, script as script_mod, voice  # noqa: E402
from vidpipe.captions import group_words, write_ass  # noqa: E402
from vidpipe.config import load_config  # noqa: E402
from vidpipe.pipeline import make_video  # noqa: E402
from vidpipe.render import build_timeline  # noqa: E402
from vidpipe.review import chapter_times  # noqa: E402
from vidpipe.script import Chapter, Scene, ShortClip, VideoScript, validate_script  # noqa: E402
from vidpipe.util import fmt_timestamp, media_duration  # noqa: E402


@pytest.fixture
def cfg(tmp_path):
    return load_config(overrides={
        "runs_dir": str(tmp_path / "runs"),
        "video": {"width": 640, "height": 360, "fps": 24, "music_dir": str(tmp_path / "no_music")},
        "shorts": {"width": 360, "height": 640},
        "images": {"size": "768x512"},
    })


def _script(n_scenes=6, **kw):
    base = dict(
        titles=["T"], description="D", tags=["a"], thumbnail_texts=["X"], thumbnail_visual="v",
        scenes=[Scene(narration=f"Scene {i} words here.", visual=f"v{i}") for i in range(n_scenes)],
        chapters=[Chapter(title="A", start_scene=0)], shorts=[], fact_check=[],
    )
    base.update(kw)
    return VideoScript(**base)


# ---- pure helpers -----------------------------------------------------------------------

def test_alignment_to_words_groups_characters():
    alignment = {
        "characters": list("Hi there."),
        "character_start_times_seconds": [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8],
        "character_end_times_seconds": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    }
    assert voice.alignment_to_words(alignment) == [["Hi", 0.0, 0.2], ["there.", 0.3, 0.9]]


def test_group_words_breaks_on_punctuation_and_length():
    words = [[w, i * 0.3, i * 0.3 + 0.25] for i, w in enumerate(
        "One two three. Four five six seven eight nine ten".split())]
    phrases = group_words(words, max_words=4)
    assert [p[0] for p in phrases] == ["One two three.", "Four five six seven", "eight nine ten"]
    # Each caption is held until the next one starts, never overlapping it.
    for a, b in zip(phrases, phrases[1:]):
        assert a[2] <= b[1] + 1e-9


def test_build_timeline_is_frame_aligned_without_drift():
    timing = [{"duration": 1.013}] * 100
    tl = build_timeline(timing, 30)
    assert all(t["frames"] >= 1 for t in tl)
    total = tl[-1]["start"] + tl[-1]["frames"] / 30
    assert abs(total - 101.3) < 1 / 30


def test_chapters_follow_youtube_rules():
    s = _script(10, chapters=[Chapter(title="Intro", start_scene=0), Chapter(title="Too soon", start_scene=1),
                              Chapter(title="Act 1", start_scene=3), Chapter(title="Act 2", start_scene=6)])
    tl = build_timeline([{"duration": 6.0}] * 10, 30)
    marks = chapter_times(s, tl, 30)
    assert [m[0] for m in marks] == ["Intro", "Act 1", "Act 2"]
    assert marks[0][1] == 0
    assert fmt_timestamp(marks[1][1]) == "0:18"
    # Fewer than three usable chapters -> no chapters at all.
    assert chapter_times(_script(3), build_timeline([{"duration": 6.0}] * 3, 30), 30) == []


def test_validate_script_clamps_bad_model_output(cfg):
    s = _script(5, chapters=[Chapter(title="B", start_scene=2), Chapter(title="Bad", start_scene=99)],
                shorts=[ShortClip(hook_title="ok", start_scene=1, end_scene=3),
                        ShortClip(hook_title="bad", start_scene=3, end_scene=9)])
    out = validate_script(s, cfg)
    assert [c.start_scene for c in out.chapters] == [0, 2]
    assert [sc.hook_title for sc in out.shorts] == ["ok"]


def test_write_ass_escapes_override_braces(tmp_path):
    path = tmp_path / "c.ass"
    write_ass([["a {\\b1} b", 0.0, 1.0]], path, 640, 360, "Inter", vertical=False)
    text = path.read_text()
    assert "{\\b1}" not in text and "Dialogue: 0,0:00:00.00,0:00:01.00,Cap" in text


# ---- providers (HTTP mocked; no keys or credits needed) --------------------------------

def _tiny_mp3(path):
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=mono",
                    "-t", "1", "-c:a", "libmp3lame", str(path)], check=True)
    return path.read_bytes()


def test_elevenlabs_request_and_parse(tmp_path, cfg, monkeypatch):
    mp3 = _tiny_mp3(tmp_path / "ref.mp3")
    seen = {}

    def fake_post(url, params, headers, json, timeout):
        seen.update(url=url, params=params, headers=headers, body=json)
        return SimpleNamespace(status_code=200, json=lambda: {
            "audio_base64": base64.b64encode(mp3).decode(),
            "alignment": {"characters": list("Go now"),
                          "character_start_times_seconds": [0, .1, .2, .3, .4, .5],
                          "character_end_times_seconds": [.1, .2, .3, .4, .5, .6]}})

    monkeypatch.setenv("ELEVENLABS_API_KEY", "k")
    monkeypatch.setattr(voice.requests, "post", fake_post)
    cfg["voice"]["voice_id"] = "VOICE123"
    out = tmp_path / "s.mp3"
    words = voice.ElevenLabsVoice(cfg).synthesize("Go now", "before", "", out)
    assert words == [["Go", 0, .2], ["now", .3, .6]]
    assert seen["url"].endswith("/VOICE123/with-timestamps")
    assert seen["headers"]["xi-api-key"] == "k"
    assert seen["body"]["previous_text"] == "before" and seen["body"]["next_text"] is None
    assert out.read_bytes() == mp3


def test_elevenlabs_requires_key_and_voice(cfg, monkeypatch):
    monkeypatch.delenv("ELEVENLABS_API_KEY", raising=False)
    with pytest.raises(RuntimeError, match="ELEVENLABS_API_KEY"):
        voice.ElevenLabsVoice(cfg)


def test_openai_images_request_and_parse(tmp_path, cfg, monkeypatch):
    seen = {}

    def fake_post(url, headers, json, timeout):
        seen.update(url=url, body=json)
        return SimpleNamespace(status_code=200, json=lambda: {"data": [{"b64_json": base64.b64encode(b"PNG").decode()}]})

    monkeypatch.setenv("OPENAI_API_KEY", "k")
    monkeypatch.setattr(images.requests, "post", fake_post)
    out = tmp_path / "x.png"
    images.OpenAIImages(cfg).generate("a bridge", out)
    assert out.read_bytes() == b"PNG"
    assert seen["body"]["model"] == cfg["images"]["model"] and seen["body"]["size"] == cfg["images"]["size"]


def test_generate_script_calls_claude_with_structured_output(cfg, monkeypatch):
    calls = {}
    good = _script(6, chapters=[Chapter(title="A", start_scene=0), Chapter(title="B", start_scene=3)])

    class FakeMessages:
        def parse(self, **kw):
            calls.update(kw)
            return SimpleNamespace(stop_reason="end_turn", stop_details=None, parsed_output=good)

    class FakeClient:
        def __init__(self, **kw):
            self.beta = SimpleNamespace(messages=FakeMessages())

    monkeypatch.setattr(script_mod.anthropic, "Anthropic", FakeClient)
    out = script_mod.generate_script("Topic", "Angle", cfg)
    assert out.titles == ["T"]
    assert calls["model"] == "claude-opus-5-5"
    assert calls["output_format"] is VideoScript
    assert calls["fallbacks"] == "default" and calls["betas"] == ["server-side-fallback-2026-07-01"]
    assert "Angle / hook" in calls["messages"][0]["content"]


def test_generate_script_surfaces_refusal(cfg, monkeypatch):
    class FakeMessages:
        def parse(self, **kw):
            return SimpleNamespace(stop_reason="refusal", stop_details=SimpleNamespace(category="x"),
                                   parsed_output=None)

    monkeypatch.setattr(script_mod.anthropic, "Anthropic",
                        lambda **kw: SimpleNamespace(beta=SimpleNamespace(messages=FakeMessages())))
    with pytest.raises(RuntimeError, match="declined"):
        script_mod.generate_script("Topic", "", cfg)


# ---- end to end (offline) ---------------------------------------------------------------

def test_dry_run_end_to_end_and_resume(cfg):
    run_dir = make_video("Test Topic", "an angle", cfg, dry_run=True)
    video = run_dir / "video.mp4"
    assert media_duration(video) > 10
    short = run_dir / "short_1.mp4"
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                            "stream=width,height", "-of", "csv=p=0", str(short)], capture_output=True, text=True)
    assert probe.stdout.strip() == "360,640"
    assert len(list(run_dir.glob("thumbnail_*.jpg"))) == 3
    meta = json.loads((run_dir / "metadata.json").read_text())
    assert meta["approved"] is False and meta["dry_run"] is True
    assert "# Review: Test Topic" in (run_dir / "REVIEW.md").read_text()

    # A human edit to metadata.json survives a re-run, and nothing is re-rendered.
    meta["title"] = "My chosen title"
    (run_dir / "metadata.json").write_text(json.dumps(meta))
    mtime = video.stat().st_mtime
    make_video("Test Topic", "an angle", cfg, dry_run=True)
    assert video.stat().st_mtime == mtime
    assert json.loads((run_dir / "metadata.json").read_text())["title"] == "My chosen title"

    # Dry runs never mark a bank topic as used.
    assert bank.used_topics(cfg) == set()
