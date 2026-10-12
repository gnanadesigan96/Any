"""Writes stories/guess-movie-NN/ (bible.json + parts_01-01.json) and stories/GUESS_MOVIE_ANSWERS.md.

Add a movie to MOVIES and run:  python stories/make_guess_movies.py stories

Format: a title card ("கதையைக் கேளுங்க! / படத்தைக் கண்டுபிடிங்க") over the first picture, the story with no
character names and no word from the title, then one spoken call to action (comment the answer, the clue is in
the description, subscribe to the channel) and a channel end card. Answers are posted in the comments, not in the
next video. The description has two clues: the main character's name and one easy clue."""
import json, sys
from pathlib import Path
out = Path(sys.argv[1])
CHANNEL = "Guessinema"            # shown on the end card and in descriptions
CHANNEL_SPOKEN = "கெஸ்ஸினிமா"      # how the narrator says it
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
 dict(n=2, tease='செத்துப்போன கொலைகாரன் திரும்ப வந்தா?', answer="Imaikkaa Nodigal (இமைக்கா நொடிகள், 2018)", spoken="இமைக்கா நொடிகள்", written="இமைக்கா நொடிகள்",
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
 dict(n=3, tease='ஒரு சின்ன தவறு... பல பேரோட வாழ்க்கை!', answer="Maanagaram (மாநகரம், 2017)", spoken="மாநகரம்", written="மாநகரம்", title_words=["மாநகர"],
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
 dict(n=4, tease='அவன் பின்தொடர்ந்த எல்லாரும் சாகுறாங்க!', answer="Thegidi (தெகிடி, 2014)", spoken="தெகிடி", written="தெகிடி", title_words=["தெகிடி"],
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

NOIR = ("photorealistic cinematic neo-noir film still, Chennai at night, moody teal and amber colour grade, wet streets, "
        "deep shadows, 35mm anamorphic lens, film grain, high detail, natural skin texture, realistic expressions")
HORROR = ("photorealistic cinematic horror film still, dim decaying interiors, cold blue-green colour grade with sickly "
          "yellow lamp light, deep shadows, mist, 35mm film grain, high detail, realistic expressions")
WARM = ("photorealistic cinematic drama film still, Chennai, warm natural colour grade, soft window light, shallow depth "
        "of field, 35mm film grain, high detail, natural skin texture, realistic expressions")
RETRO = ("photorealistic cinematic film still, a Tamil Nadu village in the early 1980s, warm faded film colours, dusty "
         "sunlight, vintage details, 35mm film grain, high detail, realistic expressions")
NEW13 = [
 dict(n=5, tease='குண்டடிபட்ட குற்றவாளிக்கு ஆபரேஷன் பண்ண மாணவன்', answer="Onaayum Aattukkuttiyum (ஓநாயும் ஆட்டுக்குட்டியும், 2013)", spoken="ஓநாயும் ஆட்டுக்குட்டியும்",
  written="ஓநாயும் ஆட்டுக்குட்டியும்", title_words=["ஓநாய்", "ஆட்டுக்குட்டி"], style=NOIR,
  clues=["ஹீரோ பேரு சந்துரு", "மிஷ்கின் இயக்கி, நடிச்ச படம்; இதுல பாட்டே கிடையாது"],
  chars={"Student": "Tamil man in his early twenties, thin, short black hair, clean-shaven, frightened earnest eyes, plain shirt and trousers",
         "Fugitive": "Tamil man in his forties, long unkempt black hair, thick beard, black clothes, a bandaged shoulder, calm unreadable face"},
  scenes=[
   ("ராத்திரி நேரம். ரோட்டோரத்துல, குண்டடிபட்ட ஒருத்தன் ரத்த வெள்ளத்துல கிடக்குறான். யாருமே கண்டுக்கல.",
    "an empty Chennai road at night, a wounded man lying by the roadside under a streetlight, cars passing by", ["Fugitive"]),
   ("ஒரு மருத்துவ மாணவன் அவனைப் பார்க்கிறான். எங்கயும் உதவி கிடைக்கல. தன் வீட்டுக்கே தூக்கிட்டுப் போய், தானே ஆபரேஷன் பண்றான்.",
    "the student operating on the wounded man on a kitchen table at night under a single bulb, sweat on his face", ["Student", "Fugitive"]),
   ("விடிஞ்சதும் தெரியுது... அவன் போலீசுக்குத் தப்பிச்சு ஓடின ஒரு பயங்கரமான குற்றவாளி!",
    "the student staring at a television news report in shock at dawn, the fugitive's empty bloodstained bed behind him", ["Student"]),
   ("உதவி பண்ணதுக்காக, அந்த மாணவனோட குடும்பத்தையே போலீஸ் பிடிச்சுட்டுப் போகுது.",
    "police officers leading a frightened family out of a small house at night, the student pleading with them", ["Student"]),
   ("போலீஸ் அவன் கையில ஒரு துப்பாக்கியைக் கொடுக்குது. அந்தக் குற்றவாளியைக் கொன்னாதான், குடும்பம் வெளிய வரும்!",
    "a police officer pressing a pistol into the trembling hands of the student in a dark interrogation room", ["Student"]),
   ("ஆனா அந்த ராத்திரி, அவன் கூடவே சுத்தும்போது... அந்தக் குற்றவாளியோட இன்னொரு முகம் தெரியுது. அவன் யாரையோ காப்பாத்தப் போராடுறான்.",
    "the fugitive and the student walking through a dark empty railway yard at night, the fugitive looking back with sad eyes", ["Fugitive", "Student"]),
   ("யாரு கெட்டவன்? யாரு நல்லவன்? ஒரே இரவுல நடக்குற ஒரு உணர்ச்சிப் போராட்டம்!",
    "a candlelit old cemetery at night, the fugitive standing among the graves, the student watching from a distance", ["Fugitive"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the student alone on a misty road at dawn, holding a pistol at his side, exhausted", ["Student"]),
  ]),
 dict(n=6, tease='உடம்பு மாறி சாகாம வாழுற விஞ்ஞானி!', answer="Maayavan (மாயவன், 2017)", spoken="மாயவன்", written="மாயவன்", title_words=["மாய"],
  style=("photorealistic cinematic science-fiction thriller film still, Chennai, cool blue and steel colour grade, "
         "glowing lab screens, rain at night, 35mm anamorphic lens, film grain, high detail, realistic expressions"),
  clues=["ஹீரோ பேரு குமரன்", "சந்தீப் கிஷன் போலீஸா நடிச்ச சயின்ஸ் ஃபிக்ஷன் த்ரில்லர்"],
  chars={"Cop": "Tamil man about thirty, short black hair, trimmed beard, intense tired eyes, khaki police inspector uniform",
         "Doctor": "Tamil woman in her late twenties, hair tied back, calm kind eyes, white coat over a simple kurta"},
  scenes=[
   ("ஒரு திருடனைத் துரத்திட்டுப் போற ஒரு போலீஸ் இன்ஸ்பெக்டர். அங்க ஒருத்தன், தன் மனைவியையே கொலை பண்றதைப் பார்க்கிறான்.",
    "the cop bursting through the door of a dark apartment at night, a shadowy figure inside, rain on the window", ["Cop"]),
   ("சண்டையில, அந்தக் கொலைகாரன் செத்துப்போறான். இன்ஸ்பெக்டருக்கு பலத்த காயம்.",
    "the injured cop slumped against a wall in a corridor, bandaged arm, flashing police lights outside", ["Cop"]),
   ("அந்த அதிர்ச்சியில இருந்து மீள, ஒரு மனநல மருத்துவர்கிட்ட சிகிச்சை எடுக்கிறான்.",
    "the cop sitting across from the doctor in a quiet therapy room, rain streaking the window", ["Cop", "Doctor"]),
   ("திரும்ப வேலைக்கு வந்தா, அதே மாதிரி இன்னொரு கொலை! ஆனா இந்த முறை கொலைகாரன் வேற ஆளு.",
    "the cop at a night crime scene under police tape, staring at an evidence board with two different suspects' photos", ["Cop"]),
   ("ஒவ்வொரு கொலைகாரனும், கொலைக்கு முன்னாடி திடீர்னு வேற ஆளா மாறிட்டான்னு குடும்பத்தார் சொல்றாங்க.",
    "a worried family sitting in a police station describing someone, the cop listening intently", ["Cop"]),
   ("உண்மை அதிர்ச்சியானது. ஒரு விஞ்ஞானி, தன் நினைவுகளை ஒரு உடம்புல இருந்து இன்னொரு உடம்புக்கு மாத்தி... சாகாம வாழ்ந்துட்டு இருக்கான்!",
    "a secret laboratory at night with a brain scan glowing on screens and a man lying under a metal headset", []),
   ("அவனைக் கொன்னா, அவன் அடுத்த உடம்புக்குத் தாவிடுவான். அப்போ அவனை எப்படித் தடுக்கிறது?",
    "the cop standing in a dark basement looking at a locked steel door, a single bulb swinging overhead", ["Cop"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the cop's face reflected in a cracked mirror, two different reflections looking back", ["Cop"]),
  ]),
 dict(n=7, tease='ஒரு சரக்கு, ரெண்டு கும்பல், ஒரு பொண்ணு', answer="Aaranya Kaandam (ஆரண்ய காண்டம், 2010)", spoken="ஆரண்ய காண்டம்", written="ஆரண்ய காண்டம்",
  title_words=["ஆரண்ய", "காண்டம்"], style=NOIR,
  clues=["முக்கிய கதாபாத்திரம் பேரு சுப்பு", "தேசிய விருது வாங்கின, தமிழோட முதல் நியோ-நாய்ர் படம்னு சொல்லப்படுற படம்"],
  chars={"Don": "Tamil man in his sixties, heavy build, grey hair, thick grey moustache, gold chains, loud silk shirt",
         "Woman": "young Tamil woman in her early twenties, long black hair, kohl-lined eyes, sad defiant expression, simple cotton saree",
         "Boy": "Tamil boy about ten, sharp clever eyes, faded shirt and shorts"},
  scenes=[
   ("ஒரு வயசான தாதா. அவனோட வீட்டுல, ஒரு இளம் பொண்ணு அடிமை மாதிரி சிக்கியிருக்கா.",
    "the don sitting on a carved chair in a dim old house, the young woman standing silently by a barred window", ["Don", "Woman"]),
   ("அவனோட வலது கை, ஒரு எதிரி கும்பலோட போதைப்பொருள் சரக்கைப் பத்தி ஒரு டீல் கொண்டு வர்றான். தாதா வேண்டாம்னு சொல்றான். அவன் தனியா முடிக்கக் கிளம்புறான்.",
    "a tough henchman leaning forward and talking to the don across a table full of cigarette smoke", ["Don"]),
   ("ஆனா, டீல் முடிஞ்சதும் அவனைக் கொல்லச் சொல்லி, தாதா ரகசியமா ஆள் அனுப்புறான்.",
    "the don whispering an order to a thin killer in a dark corridor, a knife glinting", ["Don"]),
   ("அவன் தப்பிச்சு ஓடுறான். சரக்கு அவன்கிட்டதான் இருக்குன்னு நினைச்சு, ரெண்டு கும்பலும் அவனைத் துரத்துது.",
    "a wounded man running through narrow lanes at night, two gangs with weapons chasing from different directions", []),
   ("ஆனா அந்தச் சரக்கு, சேவல் சண்டை நடத்துற ஒரு அப்பாவும் அவனோட சின்னப் பையனும் கையில மாட்டிக்குது!",
    "a poor father holding a fighting rooster and his young son staring at a bag of white packets in their hut", ["Boy"]),
   ("இதுக்கு நடுவுல, தாதா வீட்டுல அந்தப் பொண்ணுக்கும், ஒரு எடுபிடிப் பையனுக்கும் காதல்.",
    "the young woman and a shy young servant exchanging a secret glance in a dim kitchen", ["Woman"]),
   ("எல்லாரும் எல்லாரையும் ஏமாத்துற ஒரு ஆட்டம். கடைசியில ஜெயிக்கிறது யாரு? நீங்க நினைக்கவே மாட்டீங்க!",
    "the young woman standing alone in the empty courtyard at dusk, a faint knowing smile", ["Woman"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "a bag of money lying on a dusty road at sunset, footprints leading away", []),
  ]),
 dict(n=8, tease='ஒரு மழை இரவு, ஒரு விபத்து, பல கதைகள்', answer="Dhuruvangal Pathinaaru (துருவங்கள் பதினாறு, 2016)", spoken="துருவங்கள் பதினாறு",
  written="துருவங்கள் பதினாறு", title_words=["துருவ", "பதினாறு"],
  style=("photorealistic cinematic crime thriller film still, Coimbatore on a rainy night, cold blue-grey colour grade, "
         "heavy rain, headlights, 35mm anamorphic lens, film grain, high detail, realistic expressions"),
  clues=["போலீஸ் அதிகாரி பேரு தீபக்", "ரகுமான் நடிச்ச, இருபத்திரெண்டு வயசு இயக்குநரோட முதல் படம்"],
  chars={"Officer": "Tamil man in his fifties, salt-and-pepper beard, calm sharp eyes, grey cardigan, walking with a wooden cane",
         "Listener": "Tamil man in his twenties, short hair, quiet watchful eyes, dark jacket"},
  scenes=[
   ("ஒரு காலை இழந்த, ஓய்வுபெற்ற போலீஸ் அதிகாரி. போலீஸ் ஆகணும்னு வந்த ஒரு இளைஞன்கிட்ட, தன்னோட பழைய வழக்கைச் சொல்ல ஆரம்பிக்கிறாரு.",
    "the officer sitting in a dim living room with a cane beside his chair, the listener seated across from him", ["Officer", "Listener"]),
   ("அஞ்சு வருஷம் முன்னாடி, கோயம்புத்தூர்ல மழை பெய்யுற ஒரு ராத்திரி.",
    "a dark city street in pouring rain at night, a lone streetlight, empty road", []),
   ("மூணு நண்பர்கள் போன கார், ஒருத்தன் மேல மோதுது. பயத்துல, அந்த உடலை வீட்டுக்குள்ளேயே ஒளிச்சு வைக்கிறாங்க.",
    "three panicked young men dragging something wrapped in a sheet into a house at night in the rain, a dented car behind them", []),
   ("அதே ராத்திரி, ஒரு பார்க் பக்கத்துல ஒரு உடல். இன்னொரு இளைஞன் தற்கொலை பண்ணிக்கிட்டதா தகவல்.",
    "police torches lighting up a wet park at night, a covered shape on the ground, nothing graphic", []),
   ("ஒவ்வொரு தடயமும், ஒவ்வொருத்தர் சொல்ற கதையும் வேற வேற. ஒரே சம்பவம், பல பார்வைகள்!",
    "the younger version of the officer standing before a board covered in photos and maps connected with string", ["Officer"]),
   ("விசாரணையில நடந்த ஒரு விபத்துல, அவர் தன்னோட காலை இழந்தாரு.",
    "a police jeep crashed on its side on a rainy road at night, headlights still on", []),
   ("இப்போ, கதையைக் கேட்டுட்டு இருக்கிற அந்த இளைஞன் யாரு? கடைசி நிமிஷம் வரை யாராலயும் யூகிக்க முடியாது!",
    "close-up of the listener's face half in shadow, an unreadable expression", ["Listener"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the officer alone at a rain-streaked window, looking out into the night", ["Officer"]),
  ]),
 dict(n=9, tease='எதிர்காலத்தை முன்னாடியே வரைஞ்ச அப்பா!', answer="Pizza 2: Villa (பீட்சா 2: வில்லா, 2013)", spoken="வில்லா", written="பீட்சா 2: வில்லா",
  title_words=["பீட்சா", "வில்லா"], style=HORROR,
  clues=["ஹீரோ பேரு ஜெபின்", "அசோக் செல்வன் நடிச்ச, பாண்டிச்சேரியில நடக்குற திகில் படம்"],
  chars={"Writer": "Tamil man in his late twenties, short wavy hair, light beard, thoughtful eyes, casual linen shirt",
         "Girlfriend": "Tamil woman in her mid-twenties, shoulder-length hair, bright eyes, paint-stained hands, cotton kurti"},
  scenes=[
   ("எழுத்தாளனாகப் போராடுற ஒரு இளைஞன். இறந்துபோன அவனோட அப்பா, ஒரு பழைய பங்களாவை விட்டுட்டுப் போயிருக்காருன்னு திடீர்னு தெரியுது.",
    "the writer holding an old brass key and a property document, looking surprised in a small rented room", ["Writer"]),
   ("கடற்கரை நகரத்துல இருக்கிற அந்தப் பங்களாவுக்கு, தன் காதலியோட போறான்.",
    "the writer and his girlfriend standing at the gate of an old colonial bungalow overgrown with vines near the sea", ["Writer", "Girlfriend"]),
   ("அங்க, அப்பா வரைஞ்ச மர்மமான ஓவியங்கள்.",
    "a dusty room full of strange dark oil paintings covered with white sheets, one sheet slipping off", []),
   ("அந்த ஓவியங்கள்ல இருக்கிறது... அவனோட வாழ்க்கையில நடந்த சம்பவங்கள்! அம்மாவோட விபத்து கூட.",
    "the writer staring in horror at a painting of a car crash on a rainy road", ["Writer"]),
   ("அப்போ, இனிமே நடக்கப்போறதையும் அப்பா முன்னாடியே வரைஞ்சிருக்காரா?",
    "the girlfriend lifting a lantern toward a wall of paintings in a dark secret room, shadows everywhere", ["Girlfriend"]),
   ("ஒரு ஓவியத்துல... அவன் தன் காதலியையே கொல்ற மாதிரி!",
    "the writer holding a painting with trembling hands, his face pale, the painting turned away from us", ["Writer"]),
   ("விதியை மாத்த முடியுமா? அவன் எடுக்கிற முடிவு, உங்களை உறைய வைக்கும்!",
    "the old bungalow at night with orange firelight glowing in its windows", []),
   ("கதை புரிஞ்சுதா? " + CTA,
    "an empty easel in a dark room with a single candle burning", []),
  ]),
 dict(n=10, tease='ஊரையே ஏமாத்துற ஒரு பக்கா ஏமாத்துக்காரன்', answer="Sathuranga Vettai (சதுரங்க வேட்டை, 2014)", spoken="சதுரங்க வேட்டை", written="சதுரங்க வேட்டை",
  title_words=["சதுரங்க", "வேட்டை"], style=WARM,
  clues=["ஹீரோ பேரு காந்தி பாபு", "இயக்குநர் ஹெச். வினோத்தோட முதல் படம்"],
  chars={"Conman": "Tamil man in his early thirties, slick combed hair, thin moustache, sly confident smile, crisp white shirt, gold watch",
         "Wife": "young Tamil woman, long braid, innocent gentle eyes, simple cotton saree"},
  scenes=[
   ("ஒரு பக்கா ஏமாத்துக்காரன். பேச்சாலயே எல்லாரையும் மயக்கிடுவான்.",
    "the conman smiling charmingly at a crowd of eager people in a rented hall, holding up a glossy brochure", ["Conman"]),
   ("சாதாரண பாம்பை, கோடிக்கணக்கான மதிப்புள்ள அபூர்வ பாம்புன்னு விக்கிறான். சங்கிலித் தொடர் திட்டம் போட்டு, ஊரையே ஏமாத்துறான்.",
    "the conman showing a snake in a glass box to two wide-eyed rich buyers in a dim room", ["Conman"]),
   ("அவன்கிட்ட வேலைக்கு வந்த ஒரு ஏழைப் பொண்ணு, அவனையே காதலிக்கிறா. ஆனா மோசடி வெளிய வந்ததும், அவளைத் தனியா விட்டுட்டு ஓடிடுறான்.",
    "the young woman standing alone in an empty office as angry people storm in, papers flying", ["Wife"]),
   ("அவனால ஏமாந்த ஒருத்தர், ஒரு கும்பலை அனுப்பி அவனைக் கடத்துறாரு.",
    "the conman being bundled into a van by rough men on a dusty road at night", ["Conman"]),
   ("தப்பிச்சு வந்து, அந்தப் பொண்ணையே கல்யாணம் பண்ணிக்கிறான். நல்லவனா வாழ நினைக்கிறான்.",
    "a simple temple wedding, the conman tying the thali around the young woman's neck, both smiling", ["Conman", "Wife"]),
   ("ஆனா அந்தக் கும்பல் மறுபடியும் அவனைப் பிடிக்குது. ஒரே ஒரு பெரிய மோசடி பண்ணணும். இல்லன்னா, அவனும் அவன் மனைவியும் சாவாங்க!",
    "the conman tied to a chair in a warehouse, a gang leader holding up a photo of his wife", ["Conman"]),
   ("கடைசி வேலை: ஒரு பெரிய பணக்காரனை ஏமாத்தி, நூறு கோடி! ஆனா அதுக்கப்புறம் நடக்கிறது...",
    "stacks of cash on a table in a dark room, the conman staring at them, sweat on his face", ["Conman"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the conman digging in the dirt at night under torchlight, men standing over him", ["Conman"]),
  ]),
 dict(n=11, tease='போட்டோ எடுத்தா செத்துடுவாங்களாம்!', answer="Mundasupatti (முண்டாசுப்பட்டி, 2014)", spoken="முண்டாசுப்பட்டி", written="முண்டாசுப்பட்டி",
  title_words=["முண்டாசு"], style=RETRO,
  clues=["ஹீரோ பேரு கோபி", "விஷ்ணு விஷால் நடிச்ச, 1982-ல நடக்குற கிராமத்துக் காமெடி"],
  chars={"Photographer": "Tamil man in his late twenties, 1980s side-parted hair, thick moustache, bell-bottom trousers, an old box camera on a strap",
         "Assistant": "Tamil man in his twenties, thin, curly hair, cheerful face, loose 1980s shirt, carrying a tripod"},
  scenes=[
   ("எண்பதுகள்ல ஒரு கிராமம். அந்த ஊர் மக்களுக்கு ஒரு வினோதமான நம்பிக்கை.",
    "a sleepy early-1980s Tamil village with thatched houses, villagers in turbans gathered under a banyan tree", []),
   ("போட்டோ எடுத்தா... ஆயுசு குறைஞ்சு செத்துப்போயிடுவாங்க!",
    "terrified villagers covering their faces and running from an old camera on a tripod in the village square", []),
   ("டவுன்ல ஸ்டுடியோ வச்சிருக்கிற ஒரு போட்டோகிராபரும் அவனோட உதவியாளும், அந்த ஊருக்குக் கூப்பிடப்படுறாங்க.",
    "the photographer and his assistant riding into the village on a bicycle loaded with camera gear, villagers staring", ["Photographer", "Assistant"]),
   ("ஊர்ப் பெரியவரை போட்டோ எடுக்கணும். ஆனா ஏதோ ஒரு குழப்பத்தால, ரெண்டு பேரும் அந்த ஊர்லயே மாட்டிக்கிறாங்க.",
    "the photographer and assistant standing nervously before a stern village council under a tree", ["Photographer", "Assistant"]),
   ("அங்க, ஊர்த் தலைவரோட பொண்ணு மேல போட்டோகிராபருக்குக் காதல்.",
    "a pretty village girl in a half-saree drawing water at a well, the photographer staring at her, smitten", ["Photographer"]),
   ("ஆனா அவளுக்கு ஏற்கனவே வேற ஒருத்தரோட கல்யாணம் பேசி முடிச்சிருக்காங்க!",
    "a village engagement ceremony with plates of fruit and flowers, the photographer watching sadly from behind a pillar", ["Photographer"]),
   ("சினிமா ஹீரோ ஆகணும்னு கனவு காணுற ஒருத்தர், ஒரு கேமரா, ஒரு காதல்... சிரிப்புக்குப் பஞ்சமே இல்ல!",
    "a funny villager striking a dramatic film-hero pose in front of the camera while the assistant laughs", ["Assistant"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "an old black-and-white photograph of a village group, everyone looking scared of the camera", []),
  ]),
 dict(n=12, tease='தியேட்டர்ல தனியா பேய்ப் படம் பார்த்தா பரிசு!', answer="Maya (மாயா, 2015)", spoken="மாயா", written="மாயா", title_words=["மாய"], style=HORROR,
  clues=["ஹீரோயின் பேரு அப்சரா", "நயன்தாராவோட 50-வது படம்"],
  chars={"Mother": "Tamil woman in her early thirties, long black hair, tired but strong eyes, simple cotton saree, a small daughter's hand in hers"},
  scenes=[
   ("கடன்ல மூழ்கியிருக்கிற ஒரு அம்மா. தனியா தன் குழந்தையை வளர்க்கிறா. சின்னச் சின்ன விளம்பரங்கள்ல நடிச்சு பொழைக்கிறா.",
    "the mother counting a few rupee notes at a small kitchen table at night, her little daughter asleep nearby", ["Mother"]),
   ("ஒரு பேய்ப் படத்தோட விளம்பரப் போட்டி: தியேட்டர்ல தனியா உட்கார்ந்து அந்தப் படத்தைப் பார்த்தா, பரிசுப் பணம்!",
    "a dark horror film poster on a wall with a blank space for a title, a tiny cash-prize sticker in the corner", []),
   ("பணத்துக்காக, அவ அந்தச் சவாலை ஏத்துக்கிறா.",
    "the mother sitting alone in a huge empty dark cinema hall, lit only by the flickering screen", ["Mother"]),
   ("இன்னொரு பக்கம், ஒரு ஓவியன், ஒரு காட்டைப் பத்தின பேய்க் கதையை வரையறான்.",
    "an illustrator drawing a dark forest with an old asylum building at his desk at night", []),
   ("அந்தக் காட்டுல ஒரு மனநல மருத்துவமனை. கணவனுக்கு விஷம் வச்சதா குற்றம் சாட்டப்பட்ட ஒரு கர்ப்பிணிப் பெண், அங்க அடைக்கப்பட்டா.",
    "a pregnant woman in a white gown behind the bars of an old asylum deep in a misty forest", []),
   ("இருட்டான தியேட்டர்ல தனியா அவ. திரையில ஓடுற கதைக்கும், அவளோட வாழ்க்கைக்கும் ஏதோ ஒரு தொடர்பு இருக்கு...",
    "the mother gripping the cinema seat in terror, a ghostly pale hand appearing on the seat beside her", ["Mother"]),
   ("அந்தக் கர்ப்பிணிப் பெண் யாரு? அவ குழந்தைக்கு என்ன ஆச்சு? பதில் தெரிஞ்சா உறைஞ்சு போயிடுவீங்க!",
    "an old diary lying open on a cinema seat under a single beam of projector light", []),
   ("கதை புரிஞ்சுதா? " + CTA,
    "a misty forest at night with an old abandoned asylum in the distance", []),
  ]),
 dict(n=13, tease='பாழடைஞ்ச பங்களாவுல இருந்து எடுத்த நகை', answer="Demonte Colony (டிமான்ட்டி காலனி, 2015)", spoken="டிமான்ட்டி காலனி", written="டிமான்ட்டி காலனி",
  title_words=["டிமான்ட்டி", "டிமாண்டி", "காலனி"], style=HORROR,
  clues=["ஹீரோ பேரு சீனு", "அருள்நிதி நடிச்ச பேய்ப் படம்; 2024-ல இதோட ரெண்டாம் பாகம் வந்துச்சு"],
  chars={"Friend": "Tamil man in his late twenties, short hair, stubble, nervous eyes, plain t-shirt and jeans"},
  scenes=[
   ("மழை பெய்யுற ஒரு ராத்திரி. நாலு நண்பர்கள் நல்லா குடிச்சுட்டு, ஒருத்தருக்கொருத்தர் சவால் விடுறாங்க.",
    "four young men laughing and drinking in a small room on a rainy night, empty bottles on the floor", ["Friend"]),
   ("சென்னையில, பல வருஷமா யாருமே போகாத ஒரு பாழடைஞ்ச பங்களா. அங்க பேய் இருக்குன்னு ஊரே சொல்லுது.",
    "a huge abandoned colonial mansion behind rusted gates on a stormy night, lightning flashing", []),
   ("தைரியத்தைக் காட்ட, நாலு பேரும் உள்ள போறாங்க.",
    "four young men with phone torches stepping into the dark dusty hall of the mansion", ["Friend"]),
   ("அந்த பங்களாவுக்கு ஒரு பயங்கரமான பழைய கதை இருக்கு...",
    "an old portrait of a stern European man hanging crooked on a cobwebbed wall", []),
   ("அங்க இருந்து, ஒருத்தன் ஒரு பழைய நகையை யாருக்கும் தெரியாம எடுத்துட்டு வந்துடுறான்.",
    "a hand slipping an old ornate necklace into a pocket in the dark", []),
   ("அன்னைக்கு ராத்திரி, அவங்க அறைக்குள்ளேயே மாட்டிக்கிறாங்க. கதவு திறக்கல. விளக்கு அணையுது...",
    "the friend pulling desperately at a locked door in a dark room, the bulb flickering out", ["Friend"]),
   ("ஏதோ ஒண்ணு... அவங்களைத் தேடி வந்துட்டு இருக்கு!",
    "a dark doorway with a faint shadowy figure standing in it, mist on the floor", []),
   ("கதை புரிஞ்சுதா? " + CTA,
    "an old necklace lying on a wet floor in a beam of torchlight", []),
  ]),
 dict(n=14, tease='ஒரு டிவி ஸ்டுடியோவையே பிடிச்ச பொண்ணு!', answer="Aruvi (அருவி, 2017)", spoken="அருவி", written="அருவி", title_words=["அருவி"], style=WARM,
  clues=["அவளோட தோழி பேரு எமிலி", "புதுமுகம் அதிதி பாலன் நடிச்ச படம்"],
  chars={"Heroine": "young Tamil woman in her early twenties, short cropped hair, intense fearless eyes, plain kurta and jeans",
         "Emily": "Tamil trans woman in her late twenties, long hair, warm caring smile, colourful saree"},
  scenes=[
   ("போலீஸ் ஒரு இளம் பெண்ணைத் தீவிரவாதியா சந்தேகப்பட்டு விசாரிக்குது. அவ யாரு? அவளோட கடந்த காலம் என்ன?",
    "the heroine sitting calmly in a bare police interrogation room, officers watching through glass", ["Heroine"]),
   ("பாசமா வளர்ந்த ஒரு நடுத்தரக் குடும்பத்துப் பொண்ணு. ஆனா ஒரு நாள், குடும்பமே அவளை வீட்டை விட்டுத் துரத்துது.",
    "the heroine standing outside her family's front door with a small bag, the door closing on her", ["Heroine"]),
   ("தனியா நிக்கிற அவளுக்கு, ஒரு திருநங்கைத் தோழி மட்டும்தான் துணை.",
    "the heroine and Emily sharing a simple meal in a tiny hostel room, laughing", ["Heroine", "Emily"]),
   ("அவளுக்கு எச்ஐவி தொற்று. பல ஆண்கள் அவளை ஏமாத்தி, கொடுமைப்படுத்தியிருக்காங்க.",
    "the heroine sitting alone on a hospital bench holding a medical report, eyes empty", ["Heroine"]),
   ("நியாயம் கேட்டு, ஒரு பிரபல டிவி நிகழ்ச்சிக்குப் போறா.",
    "a bright television studio set with an audience and cameras, the heroine walking onto the stage", ["Heroine"]),
   ("அங்க அவளுக்கு அவமானம். அடுத்த நொடி, அவ கையில துப்பாக்கி! மொத்த ஸ்டுடியோவையும் பிணைக்கைதியா பிடிக்கிறா.",
    "the heroine holding a pistol in a TV studio as frightened crew members raise their hands", ["Heroine"]),
   ("கடைசியில, அவளோட கதை இந்தச் சமூகத்தையே கேள்வி கேக்குது.",
    "the heroine sitting on a quiet green hilltop at sunrise, smiling softly", ["Heroine"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "a camera flash capturing the heroine's smiling face", ["Heroine"]),
  ]),
 dict(n=15, tease='ஒருதலைக் காதல், ஒரு தற்கொலை நாடகம்', answer="Meyaadha Maan (மேயாத மான், 2017)", spoken="மேயாத மான்", written="மேயாத மான்", title_words=["மேயாத"],
  style=("photorealistic cinematic film still, North Chennai, vibrant warm colour grade, festival lights and street life, "
         "35mm film grain, high detail, natural skin texture, realistic expressions"),
  clues=["ஹீரோ பேரு முரளி", "வைபவ், பிரியா பவானி சங்கர் நடிச்ச வட சென்னைக் காதல் படம்"],
  chars={"Singer": "Tamil man in his late twenties, curly hair, light beard, cheerful lovelorn eyes, colourful printed shirt",
         "Girl": "Tamil woman in her mid-twenties, long hair, gentle smile, elegant pastel churidar"},
  scenes=[
   ("வட சென்னையில, மெல்லிசைக் கச்சேரியில பாடுற ஒரு இளைஞன்.",
    "the singer singing into a microphone on a small stage with a light-music band at a street festival at night", ["Singer"]),
   ("பல வருஷமா, ஒரு பொண்ணை ஒருதலையா காதலிக்கிறான்.",
    "the singer watching the girl from across a college corridor, holding his notebook to his chest", ["Singer", "Girl"]),
   ("அவளுக்கு நிச்சயதார்த்தம்னு தெரிஞ்சதும், நண்பர்களுக்கு போன் பண்ணி, தற்கொலை பண்ணிக்கப் போறேன்னு சொல்றான்!",
    "the singer on a rooftop at night with a phone to his ear, tearful and dramatic", ["Singer"]),
   ("அவனைக் காப்பாத்த, நண்பர்கள் ஒரு திட்டம் போடுறாங்க. அந்தப் பொண்ணையே அவனைத் திட்டிப் பேச வைக்கிறாங்க.",
    "two friends whispering a plan to the hesitant girl outside a tea shop", ["Girl"]),
   ("கோபத்துல, அவன் தற்கொலை எண்ணத்தையே விட்டுடுறான்.",
    "the singer storming down the stairs angrily while his friends grin with relief", ["Singer"]),
   ("ஆனா விதி விடல. மறுபடியும் ரெண்டு பேரும் நெருங்கி வர்றாங்க.",
    "the singer and the girl laughing together at a wedding reception under string lights", ["Singer", "Girl"]),
   ("பணக்காரக் குடும்பம், ஒரு சாதாரணப் பாடகன், அப்பாவோட கோபம்... இந்தக் காதல் ஜெயிக்குமா?",
    "a stern wealthy father glaring at the singer at a family function, the girl caught between them", ["Singer", "Girl"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the singer alone on a beach at sunset holding a microphone, waves behind him", ["Singer"]),
  ]),
 dict(n=16, tease='மழை, ஒரு பஸ் ஸ்டாப், ரெண்டு உடைஞ்ச இதயங்கள்', answer="Taramani (தரமணி, 2017)", spoken="தரமணி", written="தரமணி", title_words=["தரமணி"], style=WARM,
  clues=["ஹீரோ பேரு பிரபுநாத்", "ஆண்ட்ரியா நடிச்ச, இயக்குநர் ராமோட படம்"],
  chars={"Woman": "Anglo-Indian woman in her early thirties, wavy shoulder-length hair, confident sharp eyes, office blazer over a blouse",
         "Man": "Tamil man in his late twenties, rugged unkempt hair, thick beard, brooding eyes, crumpled shirt"},
  scenes=[
   ("சென்னையில, ஒரு பெரிய கம்பெனியில வேலை பார்க்கிற ஒரு ஆங்கிலோ இந்தியப் பொண்ணு. தனியா ஒரு மகனை வளர்க்கிறா.",
    "the woman in a glass office tower at dusk, looking at a photo of her young son on her desk", ["Woman"]),
   ("மழை பெய்யுற ஒரு சாயங்காலம். பாழடைஞ்ச ஒரு பஸ் ஸ்டாப்ல, ஒரு முரட்டு இளைஞனோட ஒதுங்கி நிக்கிறா.",
    "the woman and the man sheltering from heavy rain under a broken bus stop, standing apart awkwardly", ["Woman", "Man"]),
   ("அவன் ஒரு காதல் தோல்வி. அவனோட காதலி, வெளிநாட்டுல சந்திச்ச இன்னொருத்தனுக்காக அவனை விட்டுப் போயிட்டா.",
    "the man sitting alone on a staircase at night staring at an old photo of a smiling young woman", ["Man"]),
   ("ரெண்டு உடைஞ்ச இதயங்கள். மெல்ல மெல்ல நெருங்கி, ஒண்ணா வாழ ஆரம்பிக்கிறாங்க.",
    "the woman, the man and a small boy laughing together at a kitchen table in a cosy flat", ["Woman", "Man"]),
   ("ஆனா அவனோட சந்தேகம் வளருது. அவ போனை நோண்டுறான். அவ மேல நம்பிக்கையே இல்ல.",
    "the man secretly scrolling through the woman's phone in a dark room while she sleeps", ["Man"]),
   ("சுதந்திரமா வாழ நினைக்கிற ஒரு பொண்ணு. அவளைப் புரிஞ்சுக்க முடியாத ஒரு ஆண்.",
    "the woman standing alone on a balcony at night, city lights behind her, arms crossed", ["Woman"]),
   ("இந்தக் கதை, ஆண்கள் கண்டிப்பா பார்க்க வேண்டிய ஒரு கண்ணாடி!",
    "a cracked mirror reflecting the man's troubled face", ["Man"]),
   ("கதை புரிஞ்சுதா? " + CTA,
    "an empty rain-soaked bus stop at night under a flickering streetlight", []),
  ]),
 dict(n=17, tease='அட்டைப் பெட்டியில வெட்டப்பட்ட கைகள்!', answer="Yuddham Sei (யுத்தம் செய், 2011)", spoken="யுத்தம் செய்", written="யுத்தம் செய்",
  title_words=["யுத்தம்", "போர்"], style=NOIR,
  clues=["போலீஸ் அதிகாரி பேரு ஜே.கே.", "சேரன் நடிச்ச, மிஷ்கின் இயக்கின படம்"],
  chars={"Officer": "Tamil man in his forties, short hair, neat moustache, grieving tired eyes, dark shirt with sleeves rolled up"},
  scenes=[
   ("சென்னையில, அட்டைப் பெட்டிகள்ல... வெட்டப்பட்ட மனுஷக் கைகள்!",
    "a plain cardboard box left on a busy Chennai footpath at dawn, police tape around it, nothing graphic shown", []),
   ("இந்த வழக்கு, ஒரு சிபிசிஐடி அதிகாரிகிட்ட வருது. காணாமப் போன தன் தங்கையை நினைச்சு, தினமும் உடைஞ்சு போயிருக்கிறவர்.",
    "the officer sitting alone in a dim room holding a framed photo of a young woman", ["Officer"]),
   ("அவருக்குத் துணையா, ஒரு பெண் சப்-இன்ஸ்பெக்டரும் ஒரு டாக்டரும்.",
    "the officer with a young woman sub-inspector and an older doctor examining files in a cramped office", ["Officer"]),
   ("விசாரணை, காணாமப் போன இன்னொரு இளம் பொண்ணுகிட்ட போய் நிக்குது.",
    "a missing-person poster of a young woman on a wet wall at night, the officer looking at it", ["Officer"]),
   ("ஒவ்வொரு தடயமும், பெரிய அதிகாரம் உள்ள மனுஷங்களை நோக்கிப் போகுது. மேல இருந்து அழுத்தம்.",
    "powerful men in white shirts in a smoky room, a senior police officer warning the officer in a corridor", ["Officer"]),
   ("இந்தக் கைகளை வெட்டுறது யாரு? ஏன்? இது சாதாரண கொலை இல்ல... கணக்கு போட்ட பழிவாங்கல்!",
    "a shadowy figure carefully sealing a cardboard box with tape in a dark room", []),
   ("நீதி கிடைக்காதவங்க, தங்களுக்கான நீதியைத் தாங்களே தேடினா என்ன ஆகும்?",
    "an airplane taking off into a grey dawn sky", []),
   ("கதை புரிஞ்சுதா? " + CTA,
    "the officer standing alone on a rooftop at night, looking over the city", ["Officer"]),
  ]),
]
MOVIES += NEW13

answers = ["# Guess the movie: answers (never upload this file)", ""]
for m in MOVIES:
    if m.get("published"):  # leave a posted video's files exactly as they were
        answers += [f"- **#{m['n']:02d}:** {m['answer']}"]
        continue
    d = out / f"guess-movie-{m['n']:02d}"
    d.mkdir(parents=True, exist_ok=True)
    bible = {"series_title": CHANNEL, "language": "Tamil", "art_style": m["style"],
             "characters": [{"name": k, "look": v} for k, v in m["chars"].items()],
             "episodes": [{"part": 1, "title": f"இந்தப் படம் எது? #{m['n']:02d}",
                           "summary": f"A guess-the-movie Short retelling {m['answer']} in about a minute without naming it.",
                           "cliffhanger": "Viewers guess the film in the comments."}]}
    c1, c2 = m["clues"]
    # YouTube title: the story hook first (what makes people tap), then the quiz and number; the channel name is
    # added after it ("... | Guessinema").
    ep = {"part": 1, "title": f"{m['tease']} 🤔 இந்தப் படம் எது? #{m['n']:02d}",
          "hook_text": "கதையைக் கேளுங்க!", "hook_sub": "படத்தைக் கண்டுபிடிங்க",
          "description": (f"{m['tease']}\nஒரு முழுப் படத்தோட கதை, ஒரு நிமிஷத்துல! படத்தோட பேரு என்ன? 🤔\n\n"
                          f"🔍 க்ளூ 1: {c1}\n🔍 க்ளூ 2: {c2}\n\n"
                          f"👇 பதிலை கமெண்ட்ல சொல்லுங்க! சரியான பதில் பின் பண்ணின கமெண்ட்ல வரும்.\n"
                          f"🎬 இது மாதிரி இன்னும் நிறைய படங்களுக்கு {CHANNEL} சேனலை சப்ஸ்க்ரைப் பண்ணுங்க."),
          "hashtags": ["#GuessTheMovie", "#படம்எது", "#Guessinema", "#TamilMovie", "#TamilShorts", "#Shorts"],
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

# Copy-paste sheet for uploading: the same title and description the pipeline uses, plus the comments to pin.
sheet = ["# Guess the movie: YouTube titles and descriptions", "",
         "Copy each block when uploading `runs/series-guess-movie-NN-tamil/part_01.mp4`. Pin the first comment when you",
         "upload; post the answer comment later (e.g. the next day) and pin it instead. This file contains the answers:",
         "keep the repository private.", ""]
for m in MOVIES:
    if m.get("published"):
        continue
    ep = json.loads((out / f"guess-movie-{m['n']:02d}" / "parts_01-01.json").read_text())["episodes"][0]
    title = f"{ep['title']} | {CHANNEL}"
    sheet += [f"## #{m['n']:02d}", "", "**Title** (" + str(len(title)) + " characters)", "```", title, "```", "",
              "**Description**", "```", ep["description"], "", " ".join(ep["hashtags"]), "```", "",
              "**Tags**", "```", ", ".join(h.lstrip("#") for h in ep["hashtags"]) + ", tamil movie quiz, guess the tamil movie", "```", "",
              "**Pinned comment (on upload)**", "```", "இந்தப் படம் எது? 🤔 உங்க பதிலை கீழ கமெண்ட் பண்ணுங்க! 👇", "```", "",
              "**Answer comment (later)**", "```", f"✅ சரியான பதில்: {m['written']}! சரியா சொன்னவங்களுக்கு வாழ்த்துக்கள் 🎉", "```", ""]
(out / "GUESS_MOVIE_UPLOADS.md").write_text("\n".join(sheet) + "\n")
