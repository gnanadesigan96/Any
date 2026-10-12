"""Writes stories/guess-movie-NN/ (bible.json + parts_01-01.json) and stories/GUESS_MOVIE_ANSWERS.md.

Add a movie to MOVIES and run:  python stories/make_guess_movies.py stories
Each video from #02 on opens with the previous answer (SPOKEN) and lists it in its description."""
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
CTA = "இந்தப் படம் எது? பதிலை கமெண்ட்ல சொல்லுங்க. பிடிச்சிருந்தா லைக் பண்ணுங்க, சப்ஸ்க்ரைப் பண்ணுங்க!"
VILLAGE = ("photorealistic cinematic film still, rural Tamil Nadu, warm golden colour grade with dusty earth tones, natural "
           "light, shallow depth of field, 35mm film grain, high detail, natural skin texture, realistic expressions")
NIGHT = ("photorealistic cinematic action film still, Tamil Nadu at night, high-contrast teal and orange colour grade, "
         "headlights and sodium street lamps, haze, 35mm anamorphic lens, film grain, high detail, realistic expressions")
CITY = ("photorealistic cinematic film still, Chennai, rich vibrant colour grade, soft natural light, shallow depth of "
        "field, 35mm film grain, high detail, natural skin texture, realistic expressions")
SCIFI = ("photorealistic cinematic science-fiction film still, Chennai, cool blue and chrome colour grade with warm "
         "highlights, glowing lab lights, 35mm anamorphic lens, film grain, high detail, realistic expressions")
GRITTY = ("photorealistic cinematic drama film still, rural Tamil Nadu, muted desaturated earth tones, harsh natural light "
          "and deep shadows, 35mm film grain, high detail, natural skin texture, realistic expressions")

THRILLER = ("photorealistic cinematic crime thriller film still, Bengaluru at night, cold steel-blue and amber colour "
            "grade, rain and wet neon reflections, deep shadows, 35mm anamorphic lens, film grain, high detail, natural "
            "skin texture, realistic expressions")

# Keep them hard: no names until the last line, never a word from the title, the best clue in the description.
# Each film: spoken = how the next video says the answer aloud; written = how its description writes it.
MOVIES = [
 dict(n=1, answer="Imaikkaa Nodigal (இமைக்கா நொடிகள், 2018)", spoken="இமைக்கா நொடிகள்", written="இமைக்கா நொடிகள்",
  title_words=["இமைக்க", "நொடிகள்"], style=THRILLER,
  clues=["க்ரைம் த்ரில்லர், பெங்களூருல நடக்குற கதை", "கதாநாயகி பேரு அஞ்சலி",
         "ஒரு பிரபல ஹிந்திப் பட இயக்குநர், வில்லனா நடிச்ச தமிழ் படம்"],
  chars={"Officer": "Tamil woman in her mid-thirties, sharp intense eyes, black hair tied in a tight low ponytail, dark formal trouser suit, ID card on a lanyard, holstered pistol, composed fearless expression",
         "Doctor": "Tamil man in his late twenties, short wavy black hair, light stubble, white doctor's coat over a grey t-shirt, stethoscope around his neck",
         "Killer": "tall man in a long black hooded raincoat and a plain black face mask, only cold staring eyes visible"},
  scenes=[
   ("அஞ்சு வருஷம் முன்னாடி செத்துட்டான்னு சொன்ன ஒரு தொடர் கொலைகாரன்... மறுபடியும் வந்துட்டான்!",
    "a dark rain-soaked city street at night, the killer standing motionless under a flickering streetlight", ["Killer"]),
   ("பெங்களூருல, பணக்கார வீட்டுப் பிள்ளைகளைக் கடத்துறான். பணம் கேக்குறான். பணம் கொடுத்தாலும்... அவங்க உயிரோட திரும்ப வர்றதில்ல.",
    "a missing-person poster of a young man on a wet wall at night, police tape and flashing police lights behind it", []),
   ("அவனைப் பிடிக்க வர்றாங்க, ஒரு துணிச்சலான சிபிஐ அதிகாரி.",
    "the officer stepping out of a car into the rain at a night crime scene, officers making way for her", ["Officer"]),
   ("அஞ்சு வருஷம் முன்னாடி அதே வழக்கை விசாரிச்சவங்க இவங்கதான். இந்த முறை, அவன் அவங்களுக்கே நேரடியா சவால் விடுறான்.",
    "the officer alone in a dark office at night, studying a wall of photographs and red string, a phone glowing on the desk", ["Officer"]),
   ("அப்போ, ஒரு இளம் டாக்டரோட காதலியைக் கடத்துறான். அவளைத் தண்ணியில மூழ்கடிப்பேன்னு நேரலையில மிரட்டுறான்.",
    "a laptop screen in a dark room showing a live video of a frightened young woman tied to a chair as water rises around her", ["Doctor"]),
   ("அவளைக் காப்பாத்த, அந்த டாக்டர் கொலைகாரன் சொல்றதையெல்லாம் செய்யுறான். கடைசியில, கொலைகாரனே அவன்தான்னு போலீஸ் நம்புற மாதிரி மாட்டி விடப்படுறான்!",
    "the doctor running through a crowded night market in the rain clutching a heavy bag, police torches sweeping behind him", ["Doctor"]),
   ("அந்த டாக்டர் வேற யாரும் இல்ல... அந்த அதிகாரியோட சொந்தத் தம்பி! அப்போ இந்தக் கொலைகாரன் உண்மையில யாரு? திருப்பம் மேல திருப்பம்!",
    "the officer aiming her pistol across a dark parking garage at the hooded killer, her younger brother the doctor kneeling between them", ["Officer", "Killer"]),
   ("க்ளூ: அந்த அதிகாரியோட பேரு அஞ்சலி. " + CTA,
    "the officer's face half lit by a red emergency light, rain on the window behind her", ["Officer"]),
  ]),
]

SPOKEN = {m["n"]: m["spoken"] for m in MOVIES}
WRITTEN = {m["n"]: m["written"] for m in MOVIES}
answers = ["# Guess the movie: answers (never upload this file)", ""]
for m in MOVIES:
    if m["n"] > 1:  # open with the previous video's answer, over this film's first picture
        prev = m["n"] - 1
        first = m["scenes"][0]
        m["scenes"][0] = (f"போன வீடியோவோட பதில்... {SPOKEN[prev]}! சரியா சொன்னவங்களுக்கு வாழ்த்துக்கள். இப்போ அடுத்த படம்! "
                          + first[0], first[1], first[2])
        m["prev_line"] = f"போன வீடியோ #{prev:02d} பதில்: {WRITTEN[prev]}\n\n"

    d = out / f"guess-movie-{m['n']:02d}"
    d.mkdir(parents=True, exist_ok=True)
    bible = {"series_title": "60 விநாடியில் ஒரு படம்", "language": "Tamil", "art_style": m["style"],
             "characters": [{"name": k, "look": v} for k, v in m["chars"].items()],
             "episodes": [{"part": 1, "title": f"இந்தப் படம் எது? #{m['n']:02d}",
                           "summary": f"A guess-the-movie Short retelling {m['answer']} in 60 seconds without naming it.",
                           "cliffhanger": "Viewers guess the film in the comments."}]}
    c1, c2, c3 = m["clues"]
    ep = {"part": 1, "title": f"இந்தப் படம் எது? #{m['n']:02d} கண்டுபிடிங்க!",
          "hook_text": "இந்தப் படம் எது?", "hook_sub": "60 விநாடியில் முழுக் கதை",
          "description": (m.get("prev_line", "") + f"60 விநாடியில ஒரு முழுப் படத்தோட கதை! படத்தோட பேரு என்ன?\n\nக்ளூ 1: {c1}\nக்ளூ 2: {c2}\n"
                          f"க்ளூ 3: {c3}\n\nபதிலை கமெண்ட்ல சொல்லுங்க! பிடிச்சிருந்தா லைக் பண்ணுங்க, சப்ஸ்க்ரைப் பண்ணுங்க!"),
          "hashtags": ["#GuessTheMovie", "#படம்எது", "#TamilMovie", "#TamilShorts", "#Shorts"],
          "end_text": "இந்தப் படம் எது?", "end_sub": "கமெண்ட் • லைக் • சப்ஸ்க்ரைப்",
          "scenes": [{"narration": n, "visual": v, "characters": c} for n, v, c in m["scenes"]]}
    (d / "bible.json").write_text(json.dumps(bible, ensure_ascii=False, indent=2) + "\n")
    (d / "parts_01-01.json").write_text(json.dumps({"episodes": [ep]}, ensure_ascii=False, indent=2) + "\n")
    stale = d / "parts_01.json"
    stale.unlink(missing_ok=True)
    words = sum(len(s[0].split()) for s in m["scenes"])
    answers += [f"- **#{m['n']:02d}:** {m['answer']}  (clues: {c1}; {c2}; {c3})"]
    print(f"#{m['n']:02d} {m['answer']}: {len(m['scenes'])} scenes, {words} words")
(out / "GUESS_MOVIE_ANSWERS.md").write_text("\n".join(answers) + "\n")
