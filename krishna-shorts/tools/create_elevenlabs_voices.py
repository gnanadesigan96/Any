#!/usr/bin/env python3
"""Create the Kannan Kathaigal character voices in ElevenLabs (Voice Design API).

Needs only Python 3.8+ (no extra packages) and an ElevenLabs API key with
permission to use Voice Design and create voices.

Easiest (interactive, on your own computer):
    python create_elevenlabs_voices.py
  For each character it makes 3 voice previews, saves them as MP3s, opens the
  folder, and asks which one to keep (1/2/3), or r = try again, s = skip.

Two-step (no prompts; useful when someone else runs it for you):
    python create_elevenlabs_voices.py preview [KK_Kannan KK_Yashoda ...]
    python create_elevenlabs_voices.py preview KK_Narrator:all          # every narrator style
    python create_elevenlabs_voices.py preview KK_Narrator:female       # only the female styles (or :male)
    python create_elevenlabs_voices.py preview KK_Narrator:cinematic+paati
        -> writes voice_previews/<name>_1.mp3 .. _3.mp3 and previews.json
    python create_elevenlabs_voices.py save KK_Kannan=2 KK_Yashoda=1 ...
        -> creates the chosen voices and writes voice_register.json

Other:
    python create_elevenlabs_voices.py list      # show your KK_ voices
    python create_elevenlabs_voices.py check     # validate voices.json, no API calls

The API key is read from the ELEVENLABS_API_KEY environment variable. In
interactive mode, if it isn't set, you're asked for it (input is hidden and
never saved).
"""
import base64
import getpass
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.elevenlabs.io"
VOICES_FILE = os.path.join(HERE, "voices.json")
PREVIEW_DIR = os.path.join(HERE, "voice_previews")
PREVIEWS_FILE = os.path.join(PREVIEW_DIR, "previews.json")
REGISTER_FILE = os.path.join(HERE, "voice_register.json")
DESIGN_MODELS = ["eleven_ttv_v3", "eleven_multilingual_ttv_v2"]


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class ApiError(Exception):
    def __init__(self, status, body):
        super().__init__(f"HTTP {status}: {body[:400]}")
        self.status = status


def call(key, method, path, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={
        "xi-api-key": key, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise ApiError(e.code, e.read().decode("utf-8", "replace"))


def call_first(key, attempts):
    """Try (method, path, body) attempts in order; skip ones the API doesn't know (404/405/422)."""
    last = None
    for method, path, body in attempts:
        try:
            return call(key, method, path, body)
        except ApiError as e:
            last = e
            if e.status not in (400, 404, 405, 422):
                raise
    raise last


def make_previews(key, voice):
    """Return a list of {generated_voice_id, mp3_bytes}."""
    attempts = [("POST", "/v1/text-to-voice/design?output_format=mp3_44100_128",
                 {"voice_description": voice["description"], "text": voice["text"],
                  "model_id": m, "auto_generate_text": False}) for m in DESIGN_MODELS]
    attempts.append(("POST", "/v1/text-to-voice/create-previews?output_format=mp3_44100_128",
                     {"voice_description": voice["description"], "text": voice["text"]}))
    res = call_first(key, attempts)
    out = []
    for p in res.get("previews", []):
        out.append({"generated_voice_id": p["generated_voice_id"],
                    "mp3": base64.b64decode(p["audio_base_64"])})
    if not out:
        raise RuntimeError(f"No previews returned: {str(res)[:300]}")
    return out


def save_voice(key, voice, generated_voice_id):
    body = {"voice_name": voice["name"], "voice_description": voice["description"],
            "generated_voice_id": generated_voice_id,
            "labels": {"series": "Kannan Kathaigal", "language": "Tamil"}}
    res = call_first(key, [("POST", "/v1/text-to-voice", body),
                           ("POST", "/v1/text-to-voice/create-voice-from-preview", body)])
    return res["voice_id"]


def write_previews(voice, previews):
    """Save previews as <name>_<n>.mp3. Variant rounds keep numbering on (e.g. _1.._15) so one 'save' picks any."""
    os.makedirs(PREVIEW_DIR, exist_ok=True)
    store = load_json(PREVIEWS_FILE, {})
    ids = store.get(voice["name"], []) if voice.get("variant") else []
    descs = store.get("_desc_" + voice["name"], []) if voice.get("variant") else []
    paths = []
    for p in previews:
        ids.append(p["generated_voice_id"])
        descs.append(voice["description"])
        path = os.path.join(PREVIEW_DIR, f"{voice['name']}_{len(ids)}.mp3")
        with open(path, "wb") as f:
            f.write(p["mp3"])
        paths.append(path)
    store[voice["name"]] = ids
    store["_desc_" + voice["name"]] = descs
    save_json(PREVIEWS_FILE, store)
    return paths


def register(voice, voice_id):
    reg = load_json(REGISTER_FILE, {})
    reg[voice["name"]] = {"voice_id": voice_id, "character": voice["character"],
                          "description": voice["description"]}
    save_json(REGISTER_FILE, reg)


def open_folder(path):
    try:
        if sys.platform.startswith("win"):
            os.startfile(path)  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.run(["open", path], check=False)
        else:
            subprocess.run(["xdg-open", path], check=False, stderr=subprocess.DEVNULL)
    except Exception:
        pass


def get_key(interactive):
    key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
    if not key and interactive:
        key = getpass.getpass("ElevenLabs API key (hidden): ").strip()
    if not key:
        sys.exit("Set the ELEVENLABS_API_KEY environment variable first.")
    return key


def select(voices, names):
    if not names:
        return voices
    by = {v["name"]: v for v in voices}
    missing = [n for n in names if n not in by]
    if missing:
        sys.exit(f"Unknown voice name(s): {', '.join(missing)}. Known: {', '.join(by)}")
    return [by[n] for n in names]


def cmd_check(voices):
    ok = True
    for v in voices:
        problems = []
        if not 100 <= len(v["text"]) <= 1000:
            problems.append(f"text length {len(v['text'])} (needs 100-1000)")
        if not 20 <= len(v["description"]) <= 1000:
            problems.append(f"description length {len(v['description'])} (needs 20-1000)")
        print(f"{v['name']:<12} {'OK' if not problems else 'PROBLEM: ' + '; '.join(problems)}")
        ok = ok and not problems
    return 0 if ok else 1


def expand_variants(voices, args):
    """'KK_Narrator:cinematic' or 'KK_Narrator:all' -> copies of the voice using variant descriptions."""
    out = []
    by = {v["name"]: v for v in voices}
    for a in args:
        name, _, var = a.partition(":")
        if name not in by:
            sys.exit(f"Unknown voice {name}")
        v = by[name]
        if not var:
            out.append(v)
            continue
        variants = v.get("variants", {})
        groups = {"all": list(variants),
                  "female": [k for k in variants if k.startswith("female_")],
                  "male": [k for k in variants if not k.startswith("female_")]}
        names = groups.get(var) or var.split("+")
        for vn in names:
            if vn not in variants:
                sys.exit(f"{name} has no variant '{vn}'. Available: {', '.join(variants) or 'none'}")
            out.append(dict(v, description=variants[vn], variant=vn))
    return out


def cmd_preview(key, voices):
    store = load_json(PREVIEWS_FILE, {})
    for name in {v["name"] for v in voices if v.get("variant")}:
        store.pop(name, None)  # fresh numbering for a variant round
        save_json(PREVIEWS_FILE, store)
    for v in voices:
        if v.get("child"):
            print(f"\n{v['name']}: skipped (child voice; pick one from the Voice Library and link it, see pipeline/README.md)")
            continue
        print(f"\n{v['name']}  ({v['character']}): designing 3 previews...")
        try:
            paths = write_previews(v, make_previews(key, v))
            for p in paths:
                print("   ", os.path.relpath(p), f"  [{v['variant']}]" if v.get("variant") else "")
        except Exception as e:  # keep going with the other characters
            print(f"    FAILED: {e}")
    print(f"\nListen to the files in {os.path.relpath(PREVIEW_DIR)}, then run e.g.:\n"
          f"    python {os.path.basename(__file__)} save KK_Kannan=2 KK_Yashoda=1")


def cmd_save(key, voices, picks):
    store = load_json(PREVIEWS_FILE, {})
    by = {v["name"]: v for v in voices}
    for pick in picks:
        name, _, num = pick.partition("=")
        if name not in by or not num.isdigit():
            print(f"Skipping '{pick}': use NAME=number, e.g. KK_Kannan=2")
            continue
        ids = store.get(name, [])
        n = int(num)
        if not 1 <= n <= len(ids):
            print(f"Skipping {name}: no preview #{n} (run 'preview' first)")
            continue
        descs = store.get("_desc_" + name, [])
        spec = dict(by[name], description=descs[n - 1]) if len(descs) >= n else by[name]
        try:
            vid = save_voice(key, spec, ids[n - 1])
            register(spec, vid)
            print(f"Created {name}  voice_id={vid}")
        except Exception as e:
            print(f"FAILED {name}: {e}  (previews expire after a while; if so, run 'preview' again)")
    print(f"\nVoice register: {os.path.relpath(REGISTER_FILE)}")


def cmd_interactive(key, voices):
    existing = {v.get("name") for v in call(key, "GET", "/v1/voices").get("voices", [])}
    for v in voices:
        if v.get("child"):
            print(f"\n{v['name']}: skipped (child voice; pick one from the Voice Library, see pipeline/README.md)")
            continue
        if v["name"] in existing:
            print(f"\n{v['name']} already exists in your ElevenLabs account; skipping.")
            continue
        while True:
            print(f"\n=== {v['name']}: {v['character']} ===\nDesigning 3 previews (about 20-40 s)...")
            try:
                previews = make_previews(key, v)
            except Exception as e:
                print(f"Could not design this voice: {e}")
                if input("r = try again, s = skip: ").strip().lower() == "r":
                    continue
                break
            write_previews(v, previews)
            open_folder(PREVIEW_DIR)
            print(f"Listen to {v['name']}_1.mp3 .. _{len(previews)}.mp3 in {PREVIEW_DIR}")
            ans = input(f"Keep which one? 1-{len(previews)}, r = new previews, s = skip: ").strip().lower()
            if ans == "s":
                break
            if ans.isdigit() and 1 <= int(ans) <= len(previews):
                vid = save_voice(key, v, previews[int(ans) - 1]["generated_voice_id"])
                register(v, vid)
                print(f"Saved {v['name']} (voice_id {vid})")
                break
            print("New previews coming. Tip: edit the description in voices.json to steer the voice.")
    print(f"\nDone. Voice IDs are in {REGISTER_FILE}")


def cmd_list(key):
    for v in call(key, "GET", "/v1/voices").get("voices", []):
        if v.get("name", "").startswith("KK_"):
            print(f"{v['name']:<12} {v['voice_id']}")


def main():
    args = sys.argv[1:]
    voices = load_json(VOICES_FILE, [])
    cmd = args[0] if args else "interactive"
    if cmd == "check":
        sys.exit(cmd_check(voices))
    if cmd_check(voices) != 0:
        sys.exit("Fix voices.json first.")
    if cmd == "preview":
        sel = expand_variants(voices, args[1:]) if any(":" in a for a in args[1:]) else select(voices, args[1:])
        cmd_preview(get_key(False), sel)
    elif cmd == "save":
        cmd_save(get_key(False), voices, args[1:])
    elif cmd == "list":
        cmd_list(get_key(False))
    elif cmd == "interactive":
        cmd_interactive(get_key(True), voices)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
