"""Writes stories/guess-movie-NN/ (bible.json + parts_01-01.json) and stories/GUESS_MOVIE_ANSWERS.md.

Add a movie to MOVIES and run:  python stories/make_guess_movies.py stories

Format: a title card ("கதையைக் கேளுங்க! / படத்தைக் கண்டுபிடிங்க") over the first picture, the story with no
character names and no word from the title, then one spoken call to action (comment the answer, the clue is in
the description, subscribe to the channel) and a channel end card. Answers are posted in the comments, not in the
next video. The description has two clues: the main character's name and one easy clue."""
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
CHANNEL = "FilmSpeaks"            # shown on the end card and in descriptions
CHANNEL_SPOKEN = "ஃபிலிம் ஸ்பீக்ஸ்"  # how the narrator says it
CTA = (f"இந்தப் படம் எது? கமெண்ட்ல சொல்லுங்க. க்ளூ டிஸ்கிரிப்ஷன்ல இருக்கு! "
       f"{CHANNEL_SPOKEN} சேனலை சப்ஸ்க்ரைப் பண்ணுங்க!")
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

# Keep them hard: no character names, never a word from the title. Clues go only in the description.
# Each film: spoken/written = the answer (kept out of the video by a test); clues = [main character's name, easy clue].
MOVIES = [
 # Already made and posted from its own files (stories/guess-movie-01); kept here so #02 can open with its answer.
 dict(n=1, answer="Raatchasi (ராட்சசி, 2019)", spoken="ராட்சசி", written="ராட்சசி", published=True),
 dict(n=2, answer="Imaikkaa Nodigal (இமைக்கா நொடிகள், 2018)", spoken="இமைக்கா நொடிகள்", written="இமைக்கா நொடிகள்",
  title_words=["இமைக்க", "நொடிகள்"], style=THRILLER,
  clues=["கதாநாயகி பேரு அஞ்சலி", "நயன்தாரா சிபிஐ அதிகாரியா நடிச்ச படம்"],
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
   ("கதை புரிஞ்சுதா? " + CTA,
    "the officer's face half lit by a red emergency light, rain on the window behind her", ["Officer"]),
  ]),
 dict(n=3, answer="Maanagaram (மாநகரம், 2017)", spoken="மாநகரம்", written="மாநகரம்", title_words=["மாநகர"],
  style=("photorealistic cinematic crime thriller film still, Chennai at night, gritty teal and sodium-orange colour grade, "
         "busy wet streets, headlights and neon, handheld 35mm look, film grain, high detail, realistic expressions"),
  clues=["முக்கிய கதாபாத்திரம் பேரு பரணி", "லோகேஷ் கனகராஜ் இயக்கின முதல் படம்"],
  chars={"Newcomer": "Tamil man in his late twenties from a small town, neat short black hair, clean-shaven, shy worried eyes, simple checked shirt tucked into trousers, office ID tag",
         "Driver": "Tamil man in his fifties, thin build, grey stubble, kind tired eyes, faded blue shirt, a towel on his shoulder"},
  scenes=[
   ("சென்னைக்கு வந்த சில பேரு. ஒருத்தரை ஒருத்தர் தெரியாது. ஒரு சின்ன தவறால, எல்லாரோட வாழ்க்கையும் சிக்குது.",
    "a crowded Chennai junction at night seen from above, buses, autos and people crossing in every direction, rain on the road", []),
   ("சின்ன ஊர்ல இருந்து வேலைக்கு வந்த ஒரு பையன். இந்த ஊரே பிடிக்கல. வேலையை விட்டுட்டு ஊருக்குப் போகணும்னு நினைக்கிறான்.",
    "the newcomer standing alone on a crowded suburban train platform with a bag, looking lost and homesick", ["Newcomer"]),
   ("ஒரு பார்ல நடந்த சண்டையால, ஒரு ரவுடிக் கும்பல் அவனை வேற ஒருத்தன்னு நினைச்சு, அடிச்சுப் போட்டுடுது.",
    "a dark back alley at night, shadows of a gang standing over a man on the ground, a dropped office ID tag in a puddle, nothing graphic", []),
   ("இன்னொருத்தர், மகனோட சிகிச்சைக்காக சென்னைக்கு வந்த ஒரு ஏழை டாக்சி டிரைவர். அவர் ஓட்டுற டாக்சி, ஒரு பெரிய தாதாவோடது.",
    "the driver behind the wheel of an old yellow-top taxi at night, a worn photo of a small boy tucked on the dashboard", ["Driver"]),
   ("இன்னொரு பக்கம், ஒரு கும்பல் பணத்துக்காக ஒரு ஸ்கூல் பையனைக் கடத்தப் பார்க்குது. ஆனா அதே பேர்ல, அஞ்சு பசங்க!",
    "five schoolboys in identical uniforms standing in a row outside a school gate, a nervous stranger in front of them", []),
   ("தப்பான பையனைத் தூக்கிட்டு வந்துடுறாங்க. அந்தப் பையன்... அதே தாதாவோட மகன்!",
    "a small boy in a school uniform sitting calmly in the back of a van, three bumbling kidnappers staring at each other in panic", []),
   ("ஒரு பை, ஒரு டாக்சி, ஒரு கடத்தல்... எல்லாமே ஒரே இடத்துல வந்து மோதுது!",
    "a lone black bag on the back seat of the taxi under flashing police lights, the driver looking at it in shock", ["Driver"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the newcomer standing on an empty Chennai street at dawn, looking back at the city", ["Newcomer"]),
  ]),
 dict(n=4, answer="Thegidi (தெகிடி, 2014)", spoken="தெகிடி", written="தெகிடி", title_words=["தெகிடி"],
  style=("photorealistic cinematic neo-noir mystery film still, Chennai, dark moody colour grade with deep greens and "
         "golden practical lights, venetian-blind shadows, 35mm film grain, high detail, realistic expressions"),
  clues=["ஹீரோ பேரு வெற்றி", "அசோக் செல்வன் துப்பறிவாளரா நடிச்ச படம்"],
  chars={"Detective": "Tamil man in his mid-twenties, short neat black hair, light stubble, sharp curious eyes, dark jacket over a plain t-shirt, a small notebook in hand",
         "Woman": "Tamil woman in her mid-twenties, long straight black hair, warm gentle smile, pastel cotton kurti, a tote bag"},
  scenes=[
   ("குற்றவியல் படிச்சு முடிச்ச ஒரு இளைஞன். ஒரு தனியார் துப்பறியும் நிறுவனத்துல வேலைக்குச் சேர்றான்.",
    "the detective walking into a small dim private detective office with frosted glass and filing cabinets", ["Detective"]),
   ("அவனோட வேலை, சாதாரண மனுஷங்களை ரகசியமா பின்தொடர்ந்து, அவங்களைப் பத்தி எல்லா தகவலையும் சேகரிக்கிறது.",
    "the detective photographing a stranger from across a busy street with a long-lens camera, hidden behind a tea stall", ["Detective"]),
   ("அவனோட அஞ்சாவது ஆளு, ஒரு அழகான பொண்ணு. அவளைப் பின்தொடர்ந்து... அவளையே காதலிக்க ஆரம்பிக்கிறான்.",
    "the woman laughing at a bus stop in soft evening light, the detective watching her from a distance, smiling despite himself", ["Woman", "Detective"]),
   ("அப்போதான் ஒரு அதிர்ச்சி. அவன் முன்னாடி கண்காணிச்ச ஒவ்வொருத்தரும், ஒருத்தர் பின்னால ஒருத்தரா மர்மமா சாகுறாங்க!",
    "a desk covered in surveillance photos of four strangers, each one crossed out with a red marker, a desk lamp glowing", []),
   ("அடுத்தது... அவன் காதலிக்கிற அந்தப் பொண்ணா?",
    "the woman walking alone down a dark lane at night, unaware of a shadow following her", ["Woman"]),
   ("அவன் சேகரிச்ச தகவல்களை வச்சுதான் இந்தக் கொலைகள் நடக்குதா? அவனுக்கே தெரியாம, அவனையே யாரோ பயன்படுத்துறாங்களா?",
    "the detective in the dark office staring at his own files, venetian-blind shadows across his face, realisation dawning", ["Detective"]),
   ("உண்மையைத் தேடிப் போனா, பின்னாடி ஒரு பெரிய மோசடி... யாருமே எதிர்பார்க்காத ஒரு முகம்!",
    "the detective running up a dark stairwell at night with a torch, a silhouette waiting at the top", ["Detective"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the detective and the woman standing apart on a rainy road at night, looking at each other", ["Detective", "Woman"]),
  ]),
]

answers = ["# Guess the movie: answers (never upload this file)", ""]
for m in MOVIES:
    if m.get("published"):  # leave a posted video's files exactly as they were
        answers += [f"- **#{m['n']:02d}:** {m['answer']}"]
        continue
    d = out / f"guess-movie-{m['n']:02d}"
    d.mkdir(parents=True, exist_ok=True)
    bible = {"series_title": "60 விநாடியில் ஒரு படம்", "language": "Tamil", "art_style": m["style"],
             "characters": [{"name": k, "look": v} for k, v in m["chars"].items()],
             "episodes": [{"part": 1, "title": f"இந்தப் படம் எது? #{m['n']:02d}",
                           "summary": f"A guess-the-movie Short retelling {m['answer']} in about a minute without naming it.",
                           "cliffhanger": "Viewers guess the film in the comments."}]}
    c1, c2 = m["clues"]
    ep = {"part": 1, "title": f"கதையை வச்சு படத்தைக் கண்டுபிடிங்க! #{m['n']:02d}",
          "hook_text": "கதையைக் கேளுங்க!", "hook_sub": "படத்தைக் கண்டுபிடிங்க",
          "description": (f"ஒரு முழுப் படத்தோட கதை, ஒரு நிமிஷத்துல! படத்தோட பேரு என்ன?\n\nக்ளூ 1: {c1}\nக்ளூ 2: {c2}\n\n"
                          f"பதிலை கமெண்ட்ல சொல்லுங்க! {CHANNEL} சேனலை சப்ஸ்க்ரைப் பண்ணுங்க."),
          "hashtags": ["#GuessTheMovie", "#படம்எது", "#TamilMovie", "#TamilShorts", "#Shorts"],
          "end_text": CHANNEL, "end_sub": "சப்ஸ்க்ரைப் பண்ணுங்க!",
          "scenes": [{"narration": n, "visual": v, "characters": c} for n, v, c in m["scenes"]]}
    (d / "bible.json").write_text(json.dumps(bible, ensure_ascii=False, indent=2) + "\n")
    (d / "parts_01-01.json").write_text(json.dumps({"episodes": [ep]}, ensure_ascii=False, indent=2) + "\n")
    stale = d / "parts_01.json"
    stale.unlink(missing_ok=True)
    words = sum(len(s[0].split()) for s in m["scenes"])
    answers += [f"- **#{m['n']:02d}:** {m['answer']}  (clues: {c1}; {c2})"]
    print(f"#{m['n']:02d} {m['answer']}: {len(m['scenes'])} scenes, {words} words")
(out / "GUESS_MOVIE_ANSWERS.md").write_text("\n".join(answers) + "\n")
