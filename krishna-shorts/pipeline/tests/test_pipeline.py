"""Offline end-to-end test: fake ElevenLabs + Gemini that return generated media.
    python -I tests/test_pipeline.py
"""
import os, re, subprocess, sys, tempfile, json
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
tmp = tempfile.mkdtemp(prefix="kk_test_")
os.environ.update(KK_WORK_ROOT=tmp, ELEVENLABS_API_KEY="x", GEMINI_API_KEY="x")
import clients, kk  # noqa: E402


def ff(*args):
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", *args], check=True)


def tone(seconds, freq=300, out=None):
    out = out or tempfile.mktemp(suffix=".mp3", dir=tmp)
    ff("-f", "lavfi", "-i", f"sine=f={freq}:d={seconds}", "-ac", "2", out)
    return open(out, "rb").read()


VOICES = ["KK_Kannan", "KK_Yashoda", "KK_Subala", "KK_Shridama", "KK_Balarama", "KK_Narrator"]
calls = {"vc": 0, "iso": 0}
clients.ElevenLabs.get_json = lambda self, path: {"voices": [{"name": n, "voice_id": "id_" + n} for n in VOICES]}
clients.ElevenLabs.tts = lambda self, v, text, model="eleven_v3": tone(max(0.8, len(text) / 25), 400)
clients.ElevenLabs.sound_effect = lambda self, p, s: tone(s, 900)
clients.ElevenLabs.music = lambda self, p, s: tone(s, 220)
def iso(self, path):
    calls["iso"] += 1
    out = tempfile.mktemp(suffix=".mp3", dir=tmp); ff("-i", path, out); return open(out, "rb").read()
def vc(self, voice, path):
    calls["vc"] += 1
    self.voice_id(voice)
    out = tempfile.mktemp(suffix=".mp3", dir=tmp); ff("-i", path, out); return open(out, "rb").read()
clients.ElevenLabs.isolate = iso
clients.ElevenLabs.voice_change = vc

def image(self, prompt, refs=(), aspect="9:16"):
    size = {"9:16": "360x640", "16:9": "640x360", "1:1": "400x400"}[aspect]
    out = tempfile.mktemp(suffix=".png", dir=tmp)
    ff("-f", "lavfi", "-i", f"color=c=0x8a5a2b:s={size}", "-frames:v", "1", out)
    return open(out, "rb").read()
def video(self, prompt, frame=None, aspect="9:16", seconds=8, negative=None, log=print, **kw):
    n = max(1, len(re.findall(r'says in Tamil|say in Tamil', prompt)))
    expr = f"0.6*sin(2*PI*440*t)*gt(t,0.3)*lt(mod(t-0.3,1.4),0.8)*lt(t,0.3+1.4*{n}-0.5)"
    out = tempfile.mktemp(suffix=".mp4", dir=tmp)
    ff("-f", "lavfi", "-i", f"testsrc2=s=360x640:r=24:d={seconds}", "-f", "lavfi", "-i", f"aevalsrc='{expr}':s=44100:d={seconds}",
       "-shortest", "-c:v", "libx264", "-preset", "ultrafast", "-c:a", "aac", out)
    return open(out, "rb").read()
clients.Gemini.image = image
clients.Gemini.video = video

kk.main(["all", "--yes"])
work = os.path.join(tmp, "short01")
info = json.load(open(os.path.join(work, "revoice", "revoice.json")))
outs = sorted(f for f in os.listdir(os.path.join(work, "out")) if f.endswith(".mp4"))
dur = kk.duration(os.path.join(work, "out", outs[-1]))
print("\nrevoiced shots:", {k: len(v["lines"]) for k, v in info.items()}, "voice changes:", calls["vc"])
print("output:", outs[-1], f"{dur:.1f}s")
timing = json.load(open(os.path.join(work, "out", "timing.json")))
expected = max(t["start"] + t["dur"] for t in timing.values()) + 3.0  # + end card
assert abs(dur - expected) < 0.3, (dur, expected)
ctx = kk.Ctx(kk.argparse.Namespace(episode="short01", only=None, force=False))
_, placed, _, _ = kk.retime(ctx, info)
for a, b in zip(placed, placed[1:]):
    assert b["at"] >= a["at"] + a["dur"], ("overlapping lines", a["line"]["id"], b["line"]["id"])
assert info["S03"]["lines"] and len(info["S03"]["lines"]) == 3, info["S03"]
assert info["S09"]["lines"] and len(info["S09"]["lines"]) == 2
srt = open(os.path.join(work, "out", "short01.srt"), encoding="utf-8").read()
assert srt.count("-->") >= 18, srt.count("-->")
kk.main(["status"])
print("ALL OK  (work dir:", work, ")")
