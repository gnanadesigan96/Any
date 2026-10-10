import base64
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from vidpipe import bank, images, script as script_mod, stock, voice  # noqa: E402
from vidpipe.pipeline import ManualStepNeeded  # noqa: E402
from vidpipe.render import render_scene_clip  # noqa: E402
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
        thumbnail_search_query="q",
        scenes=[Scene(narration=f"Scene {i} words here.", visual=f"v{i}", search_query=f"q{i}")
                for i in range(n_scenes)],
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


# ---- free providers ---------------------------------------------------------------------

def test_distribute_words_fills_sentence_span():
    words = voice.distribute_words("Hello there, big world.", 1.0, 3.0)
    assert [w[0] for w in words] == ["Hello", "there,", "big", "world."]
    assert words[0][1] == 1.0 and abs(words[-1][2] - 3.0) < 1e-6
    assert all(a[2] <= b[1] + 1e-6 for a, b in zip(words, words[1:]))
    assert voice.split_sentences("One. Two? Three!") == ["One.", "Two?", "Three!"]


def test_manual_script_flow(cfg, tmp_path):
    cfg["script"]["provider"] = "manual"
    with pytest.raises(ManualStepNeeded):
        make_video("Manual Topic", "", cfg)
    run_dir = Path(cfg["runs_dir"]) / "manual-topic"
    prompt = (run_dir / "PROMPT_FOR_CLAUDE.txt").read_text()
    assert "search_query" in prompt and "Manual Topic" in prompt

    # A pasted reply with chat chatter and code fences around the JSON is accepted.
    good = _script(4).model_dump()
    reply = "Here you go!\n```json\n" + json.dumps(good) + "\n```\nLet me know if..."
    parsed = script_mod.parse_manual_reply(reply, cfg)
    assert len(parsed.scenes) == 4

    with pytest.raises(RuntimeError, match="missing or has wrong fields"):
        script_mod.parse_manual_reply('{"titles": ["x"]}', cfg)
    with pytest.raises(RuntimeError, match="No JSON"):
        script_mod.parse_manual_reply("sorry, no", cfg)


def test_old_script_json_still_loads():
    data = _script(2).model_dump()
    del data["thumbnail_search_query"]
    for sc in data["scenes"]:
        del sc["search_query"]
    loaded = script_mod.load_script_dict(data)
    assert loaded.scenes[0].search_query == "v0"


def test_pick_file_prefers_smallest_big_enough():
    files = [{"url": "a", "width": 3840, "height": 2160}, {"url": "b", "width": 1920, "height": 1080},
             {"url": "c", "width": 1280, "height": 720}, {"url": "d", "width": 1080, "height": 1920}]
    assert stock.pick_file(files, 1920, 1080)["url"] == "b"
    assert stock.pick_file(files[2:], 1920, 1080)["url"] == "c"
    # Vertical frame: the portrait file fills 1080x1920 without upscaling.
    assert stock.pick_file(files, 1080, 1920)["url"] == "d"


def test_fetch_visuals_with_mocked_pexels(tmp_path, cfg, monkeypatch):
    clip = tmp_path / "clip.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=640x360:rate=25",
                    "-t", "2", "-pix_fmt", "yuv420p", str(clip)], check=True)
    calls = []

    def fake_get(url, headers=None, params=None, timeout=None, stream=False):
        calls.append((url, params))
        if stream:
            return _Download(clip.read_bytes())
        q = params["query"]
        if "videos" in url and q == "bridge wind storm":
            return _Json({"videos": [{"id": 1, "url": "p1", "user": {"name": "Ann"}, "duration": 20,
                                      "video_files": [{"file_type": "video/mp4", "link": "v1", "width": 1920, "height": 1080}]}]})
        if "videos" in url:
            return _Json({"videos": []})
        if q == "nothing here at":
            return _Json({"photos": []})
        return _Json({"photos": [{"id": 9, "url": "p9", "photographer": "Bo", "src": {"large2x": "i9"}}]})

    monkeypatch.setenv("PEXELS_API_KEY", "k")
    monkeypatch.delenv("PIXABAY_API_KEY", raising=False)
    monkeypatch.setattr(stock.requests, "get", fake_get)
    scenes = [Scene(narration="a", visual="v", search_query="bridge wind storm"),
              Scene(narration="b", visual="v", search_query="old photo"),
              Scene(narration="c", visual="v", search_query="nothing here at all")]
    img_dir = tmp_path / "img"
    img_dir.mkdir()
    paths = stock.fetch_visuals(scenes, [5, 5, 5], img_dir, cfg)
    assert [p.suffix for p in paths] == [".mp4", ".jpg", ".jpg"]
    # Scene 3 had no fresh match (photo 9 already used) -> previous visual reused.
    assert paths[2].read_bytes() == paths[1].read_bytes()
    assert stock.credit_lines(img_dir) == ["Ann (Pexels)", "Bo (Pexels)"]
    # Second call downloads nothing.
    n = len(calls)
    stock.fetch_visuals(scenes, [5, 5, 5], img_dir, cfg)
    assert len(calls) == n


class _Json:
    status_code = 200

    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


class _Download:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass

    def raise_for_status(self):
        pass

    def iter_content(self, n):
        yield self.data


@pytest.mark.parametrize("vertical", [False, True])
def test_render_scene_from_stock_video(tmp_path, cfg, vertical):
    clip = tmp_path / "in.mp4"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "lavfi", "-i", "testsrc=size=1280x720:rate=25",
                    "-t", "1", "-pix_fmt", "yuv420p", str(clip)], check=True)
    out = tmp_path / "out.mp4"
    render_scene_clip(clip, 60, "zoom_in", out, cfg, vertical=vertical)  # 2.5s from a 1s clip: loops
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames", "-show_entries",
                            "stream=width,height,nb_read_frames", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True).stdout.strip()
    assert probe == ("360,640,60" if vertical else "640,360,60")


@pytest.mark.skipif(not (ROOT / "models" / "kokoro-v1.0.onnx").exists()
                    and not (ROOT / "models" / "kokoro-v1.0.int8.onnx").exists(),
                    reason="Kokoro model not downloaded")
def test_kokoro_real_synthesis(tmp_path, cfg):
    if not (ROOT / "models" / "kokoro-v1.0.onnx").exists():
        cfg["voice"]["kokoro"]["model_file"] = "kokoro-v1.0.int8.onnx"
    out = tmp_path / "k.mp3"
    words = voice.KokoroVoice(cfg).synthesize("The bridge twisted. Then it fell.", "", "", out)
    assert [w[0] for w in words] == ["The", "bridge", "twisted.", "Then", "it", "fell."]
    assert media_duration(out) > words[-1][2]


def test_next_resumes_unfinished_manual_run(cfg, monkeypatch):
    cfg["script"]["provider"] = "manual"
    first = bank.unused(cfg, "Engineering Disasters")[0]
    with pytest.raises(ManualStepNeeded):
        make_video(first["title"], first["angle"], cfg)
    # The waiting run is offered again instead of a new topic...
    assert [r["title"] for r in bank.unfinished(cfg, "Engineering Disasters")] == [first["title"]]
    # ...and it no longer counts as unused.
    assert bank.unused(cfg, "Engineering Disasters")[0]["title"] != first["title"]


# ---- Shorts format ------------------------------------------------------------------------

def test_shorts_dry_run_end_to_end(cfg):
    cfg["format"] = "shorts"
    cfg["shorts"].update(width=360, height=640, per_topic=2)
    run_dir = make_video("Shorts Topic", "", cfg, dry_run=True)
    outs = sorted(run_dir.glob("short_*.mp4"))
    assert [o.name for o in outs] == ["short_1.mp4", "short_2.mp4"]
    for o in outs:
        probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries",
                                "stream=width,height", "-of", "csv=p=0", str(o)], capture_output=True, text=True)
        assert probe.stdout.strip() == "360,640"
    meta = json.loads((run_dir / "metadata.json").read_text())
    assert meta["format"] == "shorts" and len(meta["shorts"]) == 2
    assert "#dryrun" in meta["shorts"][0]["description"]
    assert not (run_dir / "video.mp4").exists()
    assert "Short 2:" in (run_dir / "REVIEW.md").read_text()
    # Re-running reuses everything.
    mtime = outs[0].stat().st_mtime
    make_video("Shorts Topic", "", cfg, dry_run=True)
    assert outs[0].stat().st_mtime == mtime
    # The same folder in the other format gives a clear message, not a crash.
    cfg["format"] = "long"
    with pytest.raises(RuntimeError, match="other format"):
        make_video("Shorts Topic", "", cfg, dry_run=True)


def test_shorts_manual_prompt_and_reply(cfg):
    cfg["format"] = "shorts"
    cfg["script"]["provider"] = "manual"
    with pytest.raises(ManualStepNeeded):
        make_video("Manual Shorts", "", cfg)
    prompt = (Path(cfg["runs_dir"]) / "manual-shorts" / "PROMPT_FOR_CLAUDE.txt").read_text()
    assert "3 separate Shorts" in prompt and "hook_text" in prompt
    reply = {"shorts": [{"title": "T", "hook_text": "H", "description": "D", "hashtags": ["bridges", "#wind power"],
                         "scenes": [{"narration": "A line.", "visual": "v", "search_query": "q"}],
                         "fact_check": []}]}
    pack = script_mod.parse_manual_reply(json.dumps(reply), cfg)
    assert pack.shorts[0].hashtags == ["#bridges", "#windpower"]


def test_shorts_config_is_vertical_and_brisk(cfg):
    from vidpipe.pipeline import shorts_config
    v = shorts_config(cfg)
    assert (v["video"]["width"], v["video"]["height"]) == (cfg["shorts"]["width"], cfg["shorts"]["height"])
    assert v["voice"]["kokoro"]["scene_pause"] < cfg["voice"]["kokoro"]["scene_pause"]
    assert cfg["video"]["width"] == 640  # original config untouched


# ---- story series -------------------------------------------------------------------------

def test_series_manual_steps(cfg):
    from vidpipe import series
    cfg["script"]["provider"] = "manual"
    cfg["series"].update(parts=6, per_batch=5)
    run_dir = Path(cfg["runs_dir"]) / "series-x"
    run_dir.mkdir(parents=True)

    with pytest.raises(series.SeriesStepNeeded, match="step 1"):
        series.write_series(run_dir, "Dracula", "", cfg, dry_run=False)
    assert "exactly 6 entries" in (run_dir / "PROMPT_1_outline.txt").read_text()
    outline = {"series_title": "Dracula", "art_style": "ink comic",
               "characters": [{"name": "Jonathan", "look": "young clerk in a brown suit"}],
               "episodes": [{"part": p, "title": f"T{p}", "summary": "s", "cliffhanger": "c"} for p in range(1, 7)]}
    (run_dir / "reply_1_outline.txt").write_text("Sure!\n```json\n" + json.dumps(outline) + "\n```")

    with pytest.raises(series.SeriesStepNeeded, match="step 2"):
        series.write_series(run_dir, "Dracula", "", cfg, dry_run=False)
    assert "parts 1 to 5" in (run_dir / "PROMPT_2_parts_01-05.txt").read_text()

    def batch(parts):
        return json.dumps({"episodes": [{"part": p, "title": "t", "hook_text": "h", "description": "d",
                                         "hashtags": ["dracula"], "scenes": [
                                             {"narration": "A line.", "visual": "castle at night",
                                              "characters": ["Jonathan"]}]} for p in parts]})

    (run_dir / "reply_2_parts_01-05.txt").write_text(batch([1, 2, 3]))  # wrong parts -> clear error
    with pytest.raises(RuntimeError, match="Expected parts 1-5"):
        series.write_series(run_dir, "Dracula", "", cfg, dry_run=False)
    (run_dir / "reply_2_parts_01-05.txt").write_text(batch(range(1, 6)))
    with pytest.raises(series.SeriesStepNeeded, match="step 3"):
        series.write_series(run_dir, "Dracula", "", cfg, dry_run=False)
    (run_dir / "reply_3_parts_06-06.txt").write_text(batch([6]))
    bible, episodes = series.write_series(run_dir, "Dracula", "", cfg, dry_run=False)
    assert [e.part for e in episodes] == list(range(1, 7))

    pack = series.to_pack(bible, episodes)
    assert pack.shorts[5].hook_text == "Dracula · Part 6/6"
    assert "young clerk in a brown suit" in pack.shorts[0].scenes[0].visual
    assert pack.shorts[0].hashtags == ["#dracula"]


def test_series_dry_run_partial_then_full(cfg):
    from vidpipe.series import make_series
    cfg["series"].update(parts=3)
    cfg["shorts"].update(width=360, height=640)
    run_dir = make_series("Test Story", "", cfg, dry_run=True, first_n=1)
    assert [p.name for p in sorted(run_dir.glob("part_*.mp4"))] == ["part_01.mp4"]
    assert not (run_dir / "metadata.json").exists()
    make_series("Test Story", "", cfg, dry_run=True)
    assert len(list(run_dir.glob("part_*.mp4"))) == 3
    meta = json.loads((run_dir / "metadata.json").read_text())
    assert meta["format"] == "shorts" and meta["shorts"][2]["file"] == "part_03.mp4"


def test_local_images_uses_mflux_once(tmp_path, cfg, monkeypatch):
    import types
    created, calls = [], []

    class FakeImage:
        def save(self, path, overwrite=False):
            Path(path).write_bytes(b"PNG")

    import threading

    class FakeZImage:
        def __init__(self, quantize=None):
            created.append(quantize)
            self.thread = threading.get_ident()

        def generate_image(self, **kw):
            # Like MLX: the model only works on the thread that loaded it.
            assert threading.get_ident() == self.thread, "There is no Stream(cpu, 0) in current thread."
            calls.append(kw)
            return FakeImage()

    mod = types.ModuleType("mflux.models.z_image.variants.z_image")
    mod.ZImage = FakeZImage
    for name in ["mflux", "mflux.models", "mflux.models.z_image", "mflux.models.z_image.variants"]:
        monkeypatch.setitem(sys.modules, name, types.ModuleType(name))
    monkeypatch.setitem(sys.modules, "mflux.models.z_image.variants.z_image", mod)
    monkeypatch.setattr(images, "_PROVIDERS", {})
    cfg["images"]["provider"] = "local"
    images.generate_images([("a castle", tmp_path / "a.png"), ("a ship", tmp_path / "b.png")], cfg, False)
    images.generate_images([("a wolf", tmp_path / "c.png")], cfg, False)
    assert created == [4]  # model loaded once, 4-bit
    assert [c["width"] for c in calls] == [720] * 3 and calls[0]["num_inference_steps"] == 9
    assert "Style:" in calls[0]["prompt"]


def test_dracula_script_dir_is_valid_and_used(cfg):
    from vidpipe.series import make_series, write_series
    cfg["shorts"].update(width=360, height=640)
    run_dir = make_series("Dracula", "", cfg, dry_run=True, first_n=1, script_dir="stories/dracula")
    bible, episodes = write_series(run_dir, "Dracula", "", cfg, dry_run=True)
    assert bible.series_title == "Dracula" and len(episodes) == 3
    assert [e.part for e in episodes] == [1, 2, 3]
    names = {c.name for c in bible.characters}
    assert all(set(s.characters) <= names for e in episodes for s in e.scenes)
    assert (run_dir / "part_01.mp4").exists()


def test_rewritten_series_drops_old_parts(cfg):
    from vidpipe.series import make_series
    cfg["shorts"].update(width=360, height=640)
    run_dir = make_series("Dracula", "", cfg, dry_run=True, first_n=1, script_dir="stories/dracula")
    # Leftovers from the earlier 20-part version of the script.
    (run_dir / "parts_16-20.json").write_text("{}")
    (run_dir / "part_07" / "images").mkdir(parents=True)
    (run_dir / "part_07.mp4").write_bytes(b"old")
    make_series("Dracula", "", cfg, dry_run=True, first_n=1, script_dir="stories/dracula")
    assert not (run_dir / "parts_16-20.json").exists()
    assert not (run_dir / "part_07").exists() and not (run_dir / "part_07.mp4").exists()
    assert (run_dir / "part_01.mp4").exists()


# ---- 2.5D animation -----------------------------------------------------------------------

def test_effects_picked_from_scene_text():
    from vidpipe.animate import effects_for
    assert effects_for("A ship in a raging storm") == ["rain", "lightning"]
    assert effects_for("Van Helsing by a campfire in the snow") == ["snow", "embers"]
    assert effects_for("Mina writing by candlelight") == ["flicker"]
    assert effects_for("A quiet sunny garden") == []


def test_parallax_clip_renders_exact_frames(tmp_path, cfg, monkeypatch):
    import numpy as np
    from PIL import Image
    from vidpipe import animate
    img = tmp_path / "scene.png"
    Image.new("RGB", (360, 640), (90, 60, 40)).save(img)
    # Stand-in depth model: a vertical gradient (top far, bottom near).
    monkeypatch.setattr(animate._Depth, "get", classmethod(lambda cls: (lambda rgb: np.tile(
        np.linspace(0, 1, 518, dtype=np.float32)[:, None], (1, 518)))))
    cfg["video"].update(width=360, height=640, animation="parallax")
    out = tmp_path / "clip.mp4"
    render_scene_clip(img, 24, "zoom_in", out, cfg, index=2, text="a foggy night in the snow")
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-count_frames", "-show_entries",
                            "stream=width,height,nb_read_frames", "-of", "csv=p=0", str(out)],
                           capture_output=True, text=True).stdout.strip()
    assert probe == "360,640,24"
    assert (tmp_path / "scene.depth.png").exists()  # depth is cached for re-renders


@pytest.mark.skipif(not (ROOT / "models" / "depth_anything_v2_vits.onnx").exists(),
                    reason="depth model not downloaded")
def test_real_depth_model(tmp_path):
    import numpy as np
    from vidpipe.animate import depth_map
    rgb = np.zeros((200, 120, 3), np.uint8)
    rgb[100:, :] = 200  # bright lower half
    d = depth_map(tmp_path / "x.png", rgb)
    assert d.shape == (200, 120) and 0 <= d.min() and d.max() <= 1


def test_scenes_per_image_halves_generation_and_keeps_existing(tmp_path, cfg, monkeypatch):
    from vidpipe import pipeline
    made = []
    monkeypatch.setattr(pipeline, "generate_images",
                        lambda jobs, c, d: [made.append(p.name) or p.write_bytes(b"x") for _, p in jobs])
    cfg["images"]["scenes_per_image"] = 2
    scenes = [Scene(narration=f"n{i}", visual=f"v{i}", search_query="") for i in range(5)]
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    (img_dir / "scene_001.png").write_bytes(b"old")  # made earlier at one-per-scene: keep using it
    paths = pipeline._visuals(scenes, [], img_dir, cfg, dry_run=False)
    assert [p.name for p in paths] == ["scene_000.png", "scene_001.png", "scene_002.png", "scene_002.png",
                                       "scene_004.png"]
    assert made == ["scene_000.png", "scene_002.png", "scene_004.png"]


# ---- retention: hook card, end card, score, cache invalidation -----------------------------

def test_series_overlays_and_shot_list(cfg, tmp_path):
    from vidpipe import series
    bible = series.SeriesBible.model_validate(json.loads((ROOT / "stories/dracula/bible.json").read_text()))
    eps = [e for f in sorted((ROOT / "stories/dracula").glob("parts_*.json"))
           for e in series.EpisodeBatch.model_validate(json.loads(f.read_text())).episodes]
    ov = series.overlays_for(bible, eps, cfg)
    assert ov[0] == {"hook": "HE CAN'T LEAVE", "end_text": "Part 2 →", "end_sub": "Next: The Lady in White"}
    assert ov[-1]["end_text"] == "The End"
    assert all(not e.scenes[0].narration.lower().startswith("last time") for e in eps)
    path = series.write_shot_list(tmp_path, bible, eps, 2)
    text = path.read_text()
    assert "part_01/images/scene_000.png" in text and "## Part 3" not in text


def test_score_is_timed_and_audible(tmp_path):
    import wave
    import numpy as np
    from vidpipe.sound import build_score, SR
    path = build_score(tmp_path / "s.wav", 10.0, [3.0, 6.0], 8.0, seed=1)
    with wave.open(str(path)) as w:
        data = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
    assert abs(len(data) / SR - 10.0) < 0.01
    loud = lambda a, b: np.abs(data[int(a * SR):int(b * SR)]).mean()
    assert loud(0, 0.4) > loud(1.5, 2.0)      # opening boom
    assert loud(8.0, 8.4) > loud(4.5, 5.0)    # cliffhanger boom


def test_changed_script_rerenders_but_keeps_pictures(cfg):
    from vidpipe import pipeline
    cfg["format"] = "shorts"
    cfg["shorts"].update(width=360, height=640, per_topic=1)
    run_dir = make_video("Rerender Topic", "", cfg, dry_run=True)
    img = run_dir / "short_1" / "images" / "scene_000.png"
    out = run_dir / "short_1.mp4"
    img_mtime, out_mtime = img.stat().st_mtime_ns, out.stat().st_mtime_ns
    # Rewrite one line of narration (same picture descriptions).
    data = json.loads((run_dir / "script.json").read_text())
    data["shorts"][0]["scenes"][1]["narration"] = "A brand new, much more gripping line."
    (run_dir / "script.json").write_text(json.dumps(data))
    make_video("Rerender Topic", "", cfg, dry_run=True)
    assert out.stat().st_mtime_ns != out_mtime          # video rebuilt
    assert img.stat().st_mtime_ns == img_mtime          # picture kept
    # Changing a picture's description regenerates just that picture.
    data["shorts"][0]["scenes"][0]["visual"] = "A completely different scene"
    (run_dir / "script.json").write_text(json.dumps(data))
    make_video("Rerender Topic", "", cfg, dry_run=True)
    assert img.stat().st_mtime_ns != img_mtime


def test_movie_clip_replaces_picture(cfg, tmp_path):
    from vidpipe import pipeline
    scenes = [Scene(narration="n", visual="v", search_query="")]
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    (img_dir / "scene_000.png").write_bytes(b"x")
    (img_dir / "scene_000.mp4").write_bytes(b"clip")
    assert pipeline._visuals(scenes, [], img_dir, cfg, dry_run=True)[0].suffix == ".mp4"


def test_rewritten_script_reuses_pictures_from_library(cfg, tmp_path):
    from vidpipe import pipeline
    old_dir, new_dir, library = tmp_path / "part_01/images", tmp_path / "part_02/images", tmp_path / "library"
    castle = Scene(narration="n", visual="A castle at night", search_query="")
    pipeline._visuals([castle], [], old_dir, cfg, dry_run=True)
    (old_dir / "scene_000.png").write_bytes(b"made on the Mac")
    pipeline.index_library(tmp_path, library)
    # The same shot now sits in another part, at another position: it is copied, not regenerated.
    other = Scene(narration="n", visual="A ship in a storm", search_query="")
    pics = pipeline._visuals([other, castle], [], new_dir, cfg, dry_run=True, library=library)
    assert pics[1].read_bytes() == b"made on the Mac"
    assert pics[0].read_bytes() != b"made on the Mac"


def test_video_from_older_version_without_stamp_is_rebuilt(cfg):
    cfg["format"] = "shorts"
    cfg["shorts"].update(width=360, height=640, per_topic=1)
    run_dir = make_video("Legacy Topic", "", cfg, dry_run=True)
    out = run_dir / "short_1.mp4"
    (run_dir / "short_1" / "fingerprint.txt").unlink()
    before = out.stat().st_mtime_ns
    make_video("Legacy Topic", "", cfg, dry_run=True)
    assert out.stat().st_mtime_ns != before
    after = out.stat().st_mtime_ns
    make_video("Legacy Topic", "", cfg, dry_run=True)  # now stamped: no more rebuilds
    assert out.stat().st_mtime_ns == after


def test_score_has_no_cut_whoosh_by_default(tmp_path):
    import wave
    import numpy as np
    from vidpipe.sound import build_score, SR

    def level_around_cut(**kw):
        path = build_score(tmp_path / "s.wav", 10.0, [5.0], 9.5, seed=1, **kw)
        with wave.open(str(path)) as w:
            data = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(float)
        return np.abs(data[int(4.7 * SR):int(5.0 * SR)]).mean()

    assert level_around_cut(whoosh=True) > 1.5 * level_around_cut()


def test_series_motion_is_livelier(cfg):
    from vidpipe import series
    bible = series.SeriesBible.model_validate(json.loads((ROOT / "stories/dracula/bible.json").read_text()))
    p = series.series_config(cfg, bible)["video"]["parallax"]
    assert p["strength"] >= 2 and p["handheld"] > 0 and p["dust"] is True
