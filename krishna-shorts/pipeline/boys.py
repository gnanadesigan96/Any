#!/usr/bin/env python3
"""Find, test and link the four boys' voices (Kannan, Subala, Shridama, Balarama) automatically.

    python3 boys.py auto            # search the Voice Library, pick 4 different voices, add them to your
                                    # account, make Tamil test lines (normal + pitched up), link them
    python3 boys.py search          # only list + download previews of the best candidates (adds nothing)

ElevenLabs can't design children's voices, so this uses published Voice Library voices (adult performers)
and, where a voice doesn't already sound like a child, raises its pitch a little (a standard animation
technique). Results and test audio go to work/boys/. Change any pick later with:
    python3 kk.py link KK_Kannan <voice_id> --pitch 3
"""
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from clients import ApiError, ElevenLabs  # noqa: E402
import kk  # noqa: E402

OUT = os.path.join(os.environ.get("KK_WORK_ROOT", os.path.join(HERE, "work")), "boys")

KID = ["kid", "kids", "child", "children", "boy", "cartoon", "animated", "animation", "cute", "high-pitched",
       "high pitched", "childlike", "child-like", "little", "baby", "teen", "youthful", "squeaky"]
AVOID = ["sad", "heartbroken", "deep", "old", "elderly", "news", "corporate", "customer", "support", "narrator",
         "documentary", "audiobook", "meditation", "villain", "seductive", "asmr", "podcast", "announcer"]
ROLES = {  # character: (words that suit him, Tamil test line)
    "KK_Kannan": (["sweet", "playful", "cute", "cheeky", "mischievous", "bright", "giggl", "innocent", "happy"],
                  "[exaggerated innocence] அம்மா, நான் ஒண்ணுமே பண்ணலையே! [giggles]"),
    "KK_Subala": (["soft", "shy", "nervous", "timid", "gentle", "thin", "whisper", "anxious", "worried"],
                  "[terrified whisper] டேய்... கொலுசு சத்தம்... அம்மா!"),
    "KK_Shridama": (["playful", "exaggerated", "energetic", "loud", "fun", "funny", "comic", "cheerful", "goofy"],
                    "[straining] சீக்கிரம் கண்ணா... தோள் வலிக்குது! [laughs]"),
    "KK_Balarama": (["confident", "strong", "firm", "bold", "clear", "brave", "assertive", "energetic"],
                    "[breathless] அம்மா! கண்ணன் மண்ணு தின்னான்! நானே பார்த்தேன்!"),
}
ORDER = ["KK_Kannan", "KK_Subala", "KK_Shridama", "KK_Balarama"]


def text_of(v):
    return " ".join(str(v.get(k) or "") for k in ("name", "description", "descriptive", "use_case", "category")).lower()


def is_kid(v):
    return any(w in text_of(v) for w in ("kid", "child", "boy", "cartoon", "childlike", "child-like", "baby"))


def is_tamil(v):
    langs = json.dumps(v.get("verified_languages") or []).lower() + " " + str(v.get("language") or "").lower()
    return "ta" in re.findall(r"[a-z]+", langs) or "tamil" in langs


def base_score(v):
    t = text_of(v)
    s = 3 * sum(w in t for w in KID) - 4 * sum(w in t for w in AVOID)
    if "characters" in t or "animation" in t:
        s += 4
    if v.get("age") == "young":
        s += 2
    if is_tamil(v):
        s += 10
    gender = str(v.get("gender") or "").lower()
    name_desc = text_of(v)
    if gender == "female" or any(w in name_desc for w in (" girl", "female", "woman", "lady", "princess")):
        s -= 40  # the four characters are boys
    if v.get("rate") not in (None, 0, 0.0, 1, 1.0):
        s -= 6  # custom-priced voice: avoid surprise costs
    return s


def search(el):
    found = {}
    queries = [dict(language="ta", use_cases="characters_animation"), dict(language="ta", gender="male", age="young")]
    queries += [dict(language="ta", search=w) for w in ("kid", "child", "boy", "cartoon", "playful", "cute")]
    queries += [dict(search=w, use_cases="characters_animation") for w in ("kid", "child", "little boy", "cartoon boy")]
    for q in queries:
        try:
            for v in el.shared_voices(page_size=100, **q):
                found.setdefault(v["voice_id"], v)
        except ApiError as e:
            print(f"   search {q} failed: {e}")
    ranked = sorted(found.values(), key=base_score, reverse=True)
    print(f"Found {len(found)} candidate voices.")
    return ranked


def pick(ranked):
    chosen, used = {}, set()
    for role in ORDER:
        words = ROLES[role][0]
        best = max((v for v in ranked[:60] if v["voice_id"] not in used and base_score(v) > 0),
                   key=lambda v: base_score(v) + 3 * sum(w in text_of(v) for w in words), default=None)
        if best:
            chosen[role] = best
            used.add(best["voice_id"])
    return chosen


def download(url, path):
    try:
        with urllib.request.urlopen(url, timeout=60) as r, open(path, "wb") as f:
            f.write(r.read())
        return True
    except Exception:
        return False


def cmd_search(el):
    os.makedirs(os.path.join(OUT, "previews"), exist_ok=True)
    ranked = search(el)
    lines = ["# Boy voice candidates (best first)\n", "| # | Name | Description | voice_id | preview |", "|---|---|---|---|---|"]
    for i, v in enumerate(ranked[:15], 1):
        prev = os.path.join(OUT, "previews", f"{i:02d}_{re.sub(r'[^A-Za-z0-9]+', '_', v['name'])[:30]}.mp3")
        ok = v.get("preview_url") and download(v["preview_url"], prev)
        desc = (v.get("description") or "").replace("|", "/").replace("\n", " ")[:90]
        lines.append(f"| {i} | {v['name']} | {desc} | `{v['voice_id']}` | {os.path.basename(prev) if ok else '-'} |")
        print(f"{i:>2}. {v['name']}  ({v['voice_id']})  {v.get('gender') or '?'}, "
              f"{'Tamil' if is_tamil(v) else 'not Tamil-verified'}, score {base_score(v)}")
    with open(os.path.join(OUT, "candidates.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\nPreviews and list: {OUT}")
    return ranked


def cmd_auto(el):
    os.makedirs(os.path.join(OUT, "tests"), exist_ok=True)
    ranked = cmd_search(el)
    chosen = pick(ranked)
    if len(chosen) < 4:
        sys.exit("Not enough candidates found. Try again later, or pick voices by hand (see README).")
    mine = {v["name"]: v["voice_id"] for v in el.get_json("/v1/voices").get("voices", [])}
    path = os.path.join(HERE, "voice_map.json")
    vmap = json.load(open(path)) if os.path.exists(path) else {}
    report = ["# Boys' voices picked automatically\n",
              "Listen to the files in `tests/`. `_p0` = the voice as published, `_p3` = 3 semitones higher (younger).\n",
              "| Character | Voice (Voice Library) | Why | Linked as | Change with |", "|---|---|---|---|---|"]
    print("\n=== Picks ===")
    for role in ORDER:
        v = chosen[role]
        new_name = f"{role} ({v['name'][:40]})"
        for old_name, old_id in list(mine.items()):
            if old_name.startswith(f"{role} (") and old_name != new_name:
                try:
                    el.delete_voice(old_id)  # an earlier pick this script added; free the slot
                    print(f"   removed earlier pick '{old_name}' from your voices")
                except ApiError as e:
                    print(f"   could not remove '{old_name}': {e}")
        vid = mine.get(new_name)
        if not vid:
            try:
                vid = el.add_shared(v["public_owner_id"], v["voice_id"], new_name)
            except ApiError as e:
                print(f"{role}: could not add '{v['name']}' to your voices ({e})")
                continue
        el._voices = None
        pitch = 0 if is_kid(v) else 3
        vmap[role] = {"id": vid, "pitch": pitch} if pitch else vid
        line = ROLES[role][1]
        for p in (0, 3):
            out = os.path.join(OUT, "tests", f"{role}_p{p}.mp3")
            try:
                with open(out, "wb") as f:
                    f.write(_tts_by_id(el, vid, line))
                kk.pitch_shift(out, p)
            except ApiError as e:
                print(f"   test line failed for {role}: {e}")
        why = "child-like description" if is_kid(v) else "playful young voice, pitched up 3 semitones"
        print(f"{role:<12} → {v['name']}  [{why}]")
        report.append(f"| {role} | **{v['name']}**: {(v.get('description') or '')[:80]} | {why} | `{vid}`"
                      f"{' +' + str(pitch) + ' st' if pitch else ''} | `python3 kk.py link {role} <voice_id> --pitch N` |")
    json.dump(vmap, open(path, "w"), indent=2)
    with open(os.path.join(OUT, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report) + "\n")
    print(f"\nLinked in voice_map.json. Test lines: {os.path.join(OUT, 'tests')}  Report: {os.path.join(OUT, 'report.md')}")
    print("Next: python3 kk.py lines")


def _tts_by_id(el, vid, text):
    """TTS for a voice id (the voice may not be mapped yet)."""
    saved = el.voice_id
    el.voice_id = lambda name: vid
    try:
        return el.tts("_", text)
    finally:
        el.voice_id = saved


def main():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("ELEVENLABS_API_KEY is not set.")
    el = ElevenLabs(key)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "auto"
    {"auto": cmd_auto, "search": cmd_search}.get(cmd, lambda _: sys.exit(__doc__))(el)


if __name__ == "__main__":
    main()
