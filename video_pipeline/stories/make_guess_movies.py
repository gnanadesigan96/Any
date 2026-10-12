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

MOVIES = [
 dict(n=1, answer="Raatchasi (ராட்சசி, 2019)", style=VILLAGE,
  clues=["தமிழ் படம், கதாநாயகியை மையமா வச்ச கதை", "கதாநாயகி பேரு கீதா ராணி", "2019-ல வெளியான படம்"],
  chars={"Headmistress": "Tamil woman in her late thirties, wheatish skin, determined eyes, black hair in a neat low bun, small red bindi, crisp plain maroon cotton saree, simple wristwatch, upright confident posture",
         "SchoolOwner": "Tamil man in his fifties, heavy build, thick black moustache, oiled swept-back hair, white shirt and white veshti, thick gold chain and gold rings, smug expression"},
  scenes=[
   ("ஒரு கிராமத்து அரசுப் பள்ளி. பசங்க சுவரேறி ஓடுறாங்க. வாத்தியார்கள் தூங்குறாங்க. யாருக்கும் கவலையே இல்ல.",
    "a crumbling village government school with cracked walls and faded paint, schoolchildren in uniforms climbing over the compound wall to run away, a teacher dozing in a chair inside a classroom", []),
   ("ஒரு நாள், கீதா ராணின்னு ஒரு புது தலைமை ஆசிரியை வர்றாங்க. முதல் நாளே எல்லாரும் நடுங்கிட்டாங்க.",
    "the headmistress walking through the rusty iron gate of the village school in the morning light, children and teachers stopping to stare at her", ["Headmistress"]),
   ("நேரத்துக்கு வரணும். ஒழுங்கா பாடம் எடுக்கணும். பள்ளி முழுக்க சுத்தமா இருக்கணும். சோம்பேறி வாத்தியார்கள் அவங்களுக்கு ஒரு பட்டப்பேர் வச்சாங்க.",
    "the headmistress in a shabby staff room pointing firmly at the wall clock while embarrassed teachers stand up from their chairs, two of them whispering behind her back", ["Headmistress"]),
   ("படிப்பை நிறுத்தின பிள்ளைகளை, வீடு வீடா போய் மறுபடியும் பள்ளிக்குக் கூட்டிட்டு வர்றாங்க.",
    "the headmistress kneeling outside a small village hut, gently holding the hand of a barefoot girl while the girl's worried mother listens", ["Headmistress"]),
   ("ஊர்ல ஒரு தனியார் பள்ளி முதலாளி. அரசுப் பள்ளி உயர்ந்தா, அவன் வியாபாரம் படுத்துடும். அரசியல்வாதிங்க, அதிகாரிங்க, அடியாட்கள்... எல்லாரும் அவங்களுக்கு எதிரா.",
    "the private school owner standing with arms crossed in front of a shiny new private school building, a few rough men and a politician in white beside him, smirking", ["SchoolOwner"]),
   ("ஆனா அவங்க பயப்படல. அடிக்க வந்தவங்களையே அடிச்சு விரட்டுறாங்க!",
    "dynamic action shot in a dusty school courtyard: the headmistress in her saree blocking a thug's punch and pushing him back, dust flying, children watching from a doorway", ["Headmistress"]),
   ("கடைசியில அந்தப் பள்ளியே மாறிடுது. பசங்க சிரிச்சுட்டே படிக்கிறாங்க. ஊரே அவங்களைக் கொண்டாடுது.",
    "the same village school now freshly painted and clean, happy children in neat uniforms cheering around the smiling headmistress in the courtyard, villagers clapping", ["Headmistress"]),
   ("சோம்பேறிகள் அவங்களுக்கு வச்ச அந்தப் பட்டப்பேர்தான்... இந்தப் படத்தோட பேரு! " + CTA,
    "silhouette of the headmistress standing tall at the school gate against a blazing orange sunset, children's silhouettes behind her", ["Headmistress"]),
  ]),
 dict(n=2, answer="Kaithi (கைதி, 2019)", style=NIGHT,
  clues=["ஆக்ஷன் த்ரில்லர், முழுக் கதையும் ஒரே இரவுல நடக்கும்", "ஹீரோ பேரு டில்லி", "பாட்டே இல்லாத தமிழ் படம்"],
  chars={"Hero": "rugged Tamil man in his late thirties, long untidy black hair, thick black beard, tired intense eyes, faded checked shirt and grey veshti folded at the knee, strong build",
         "Officer": "Tamil police inspector in his forties, short hair, trimmed moustache, khaki uniform torn and dusty, bandaged arm"},
  scenes=[
   ("பத்து வருஷம் ஜெயில்ல இருந்த டில்லி, இன்னைக்குத்தான் வெளியே வர்றான். அவனுக்கு ஒரே ஆசை... இதுவரைக்கும் பார்க்காத தன் பொண்ணைப் பார்க்கணும்.",
    "the hero walking out of a prison gate at dusk holding a small cloth bag, looking at the sky", ["Hero"]),
   ("அதே ராத்திரி, போலீஸ் ஒரு பெரிய போதைப்பொருள் கடத்தலைப் பிடிக்குது.",
    "police officers stacking seized sacks into a dim police station storeroom at night, torch beams, tense faces", ["Officer"]),
   ("கோபமான கடத்தல் கும்பல், ஒரு விருந்துல போலீஸ் அதிகாரிகளுக்கு விஷம் கலந்துடுது. எல்லாரும் மயங்கி விழுறாங்க.",
    "police officers slumped unconscious around tables at a night party, spilled glasses, colourful string lights", []),
   ("அவங்களைக் காப்பாத்த, ராத்திரியோட ராத்திரியா ஆஸ்பத்திரிக்குக் கொண்டு போகணும். லாரி ஓட்ட, ஒரு அதிகாரி டில்லியைக் கூட்டிட்டு வர்றாரு.",
    "an old lorry speeding down a dark highway at night, headlights blazing, the hero at the wheel and the injured officer beside him", ["Hero", "Officer"]),
   ("வழி முழுக்க, கும்பல் கும்பலா அடியாட்கள் லாரியைத் துரத்துறாங்க. இன்னொரு பக்கம், ஒரு வயசான போலீஸ்காரரும் சில பசங்களும் போலீஸ் ஸ்டேஷனைக் காப்பாத்துறாங்க.",
    "a gang of thugs on motorbikes with burning torches chasing the lorry through a forest road at night", []),
   ("ஒரே ராத்திரி. ஒரே லாரி. டில்லி தனி ஆளா எல்லாரையும் அடிச்சு, போலீசைக் காப்பாத்துறான்.",
    "the hero fighting a crowd of thugs alone beside the lorry in the rain at night, sparks and headlights", ["Hero"]),
   ("விடியற்காலையில, அவன் கடைசியா தன் பொண்ணைப் பார்க்கிறான்.",
    "at dawn, the hero kneeling in an orphanage courtyard as a little girl in a school uniform walks shyly toward him, soft golden light", ["Hero"]),
   ("க்ளூ: ஹீரோ பேரு டில்லி. " + CTA,
    "the hero standing beside the old lorry on an empty highway at sunrise, looking into the distance", ["Hero"]),
  ]),
 dict(n=3, answer="Enthiran (எந்திரன், 2010)", style=SCIFI,
  clues=["அறிவியல் புனைகதை (சயின்ஸ் ஃபிக்ஷன்) படம்", "விஞ்ஞானி பேரு வசீகரன், ரோபோ பேரு சிட்டி", "2010-ல வெளியான படம்"],
  chars={"Scientist": "Tamil man in his fifties, neat side-parted black hair, clean-shaven, kind sharp eyes, white lab coat over a blue shirt",
         "Robot": "humanoid robot that looks exactly like a Tamil man in his fifties with neat side-parted black hair, glowing eyes, metallic silver panels showing on its neck and hands, black suit"},
  scenes=[
   ("ஒரு விஞ்ஞானி, பத்து வருஷம் கஷ்டப்பட்டு, தன்னைப் போலவே ஒரு ரோபோவை உருவாக்குறாரு.",
    "the scientist in a high-tech lab at night working on the robot lying on a table, wires and sparks, glowing screens", ["Scientist", "Robot"]),
   ("அந்த ரோபோ ஓடும், சண்டை போடும், ஒரு நொடியில ஆயிரம் புத்தகம் படிக்கும்.",
    "the robot flipping through a book in a blur of pages, holographic text floating around it", ["Robot"]),
   ("ஆனா அதுக்கு மனுஷ உணர்வுகள் இல்ல. விஞ்ஞானி அதுக்கு உணர்வுகளைக் கொடுக்கிறாரு. அதுதான் பெரிய தப்பு!",
    "the scientist connecting a glowing chip to the robot's head, the robot's eyes changing colour for the first time", ["Scientist", "Robot"]),
   ("அந்த ரோபோ, விஞ்ஞானியோட காதலியையே காதலிக்க ஆரம்பிக்குது!",
    "the robot holding a single red rose and gazing at a surprised young Tamil woman in a pale blue salwar in a garden", ["Robot"]),
   ("கோபத்துல விஞ்ஞானி அதை உடைச்சுப் போடுறாரு. ஆனா ஒரு வில்லன் விஞ்ஞானி, அதை எடுத்து ஒரு கொலைகார ரோபோவா மாத்துறான்.",
    "a dark workshop where a sinister old scientist installs a glowing red chip into the broken robot's head", ["Robot"]),
   ("இப்போ அந்த ரோபோ, தன்னைப் போலவே நூத்துக்கணக்கான ரோபோக்களை உருவாக்கி, நகரத்தையே தாக்குது.",
    "an army of identical robots marching through a Chennai street at night, cars overturned, people fleeing", ["Robot"]),
   ("கடைசியில, அதை உருவாக்கின விஞ்ஞானியே அதைத் தடுத்து நிறுத்துறாரு.",
    "the scientist facing the robot alone amid smoke and wreckage, holding a small device", ["Scientist", "Robot"]),
   ("க்ளூ: விஞ்ஞானி பேரு வசீகரன். ரோபோ பேரு சிட்டி. " + CTA,
    "the robot standing alone under a single spotlight in a dark museum hall, a calm expression", ["Robot"]),
  ]),
 dict(n=4, answer="96 (2018)", style=CITY,
  clues=["காதல் படம்", "ஹீரோ ராம், ஹீரோயின் ஜானு", "படத்தோட பேரு ஒரு வருஷம்"],
  chars={"Ram": "Tamil man in his early forties, salt-and-pepper beard, wavy black hair, gentle shy eyes, plain kurta, a camera strap over his shoulder",
         "Janu": "Tamil woman in her late thirties, long black hair, warm expressive eyes, elegant plain yellow cotton saree"},
  scenes=[
   ("ஊர் ஊரா சுத்துற ஒரு போட்டோகிராபர், ராம். ரொம்ப வருஷம் கழிச்சு, தன்னோட பழைய பள்ளிக்கூடத்துக்குப் போறான்.",
    "Ram with a camera standing in the empty corridor of an old school, touching a classroom door, nostalgic afternoon light", ["Ram"]),
   ("இருபது வருஷத்துக்கு மேல கழிச்சு, அவனோட பள்ளித் தோழர்கள் எல்லாரும் ஒண்ணா சந்திக்கிறாங்க.",
    "a joyful school reunion of middle-aged friends hugging and laughing in a decorated hall", ["Ram"]),
   ("அங்க வர்றா ஜானு. அவனோட முதல் காதல்.",
    "Janu entering the reunion hall in a yellow saree, Ram freezing as he sees her across the room", ["Ram", "Janu"]),
   ("பள்ளிக்கூட நாட்கள்ல, ரெண்டு பேருக்கும் ஒருத்தர் மேல ஒருத்தருக்கு காதல். ஆனா ராம் ஒரு வார்த்தை கூட சொல்லல.",
    "a nostalgic flashback: a shy teenage boy and a teenage girl in school uniforms sitting apart on classroom benches, stealing glances", []),
   ("ஒரு சின்ன தவறான புரிதல். அவங்க பிரிஞ்சு போயிட்டாங்க. ஜானுக்கு வேற ஒருத்தரோட கல்யாணம் ஆயிடுச்சு.",
    "a teenage girl in a school uniform waiting alone at a college gate in the rain, holding her books, looking around sadly", []),
   ("இப்போ, ஒரே ஒரு ராத்திரி. பழைய நினைவுகள், சொல்லாத வார்த்தைகள், கண்ணீர்.",
    "Ram and Janu sitting on a terrace at night under string lights, talking quietly, tears in her eyes", ["Ram", "Janu"]),
   ("விடியற்காலையில, ஜானு விமானம் ஏறிப் போயிடுறா. ராம் மறுபடியும் தனியா.",
    "Ram standing alone outside an airport at dawn, watching a plane rise into a pink sky", ["Ram"]),
   ("க்ளூ: ஹீரோ ராம், ஹீரோயின் ஜானு. " + CTA,
    "a close-up of an old school photograph of a class, a faded heart drawn around two faces", []),
  ]),
 dict(n=5, answer="Asuran (அசுரன், 2019)", style=GRITTY,
  clues=["ஆக்ஷன் டிராமா", "ஹீரோ பேரு சிவசாமி", "எழுத்தாளர் பூமணியோட 'வெக்கை' நாவலை அடிப்படையா வச்ச படம்"],
  chars={"Father": "lean Tamil farmer in his late forties, grey stubble, thick moustache, weathered dark skin, calm piercing eyes, faded white vest and veshti, towel over the shoulder",
         "Son": "Tamil teenage boy about sixteen, thin, scared eyes, messy black hair, faded shirt and veshti"},
  scenes=[
   ("ஒரு அமைதியான கிராமத்து விவசாயி, சிவசாமி. எதுக்கும் சண்டைக்குப் போகாதவர்.",
    "the father working calmly in a dry field at sunrise, a bullock behind him", ["Father"]),
   ("ஊர்ல ஒரு பணக்கார நிலச்சுவான்தார், அவரோட நிலத்தைப் பறிக்கப் பார்க்கிறான். அந்தச் சண்டையில, சிவசாமியோட மூத்த பையன் கொல்லப்படுறான்.",
    "a wealthy landlord in white with gold rings standing on a field boundary with his men, a grieving family in the distance", []),
   ("பழிவாங்க, இளைய பையன் அந்தப் பணக்காரனைக் கொன்னுடுறான். இப்போ அவனைக் கொல்ல ஒரு பெரிய கும்பல் தேடுது.",
    "the son running in panic through a village lane at night, holding a sickle, men with torches behind him", ["Son"]),
   ("மகனைக் காப்பாத்த, அப்பாவும் பையனும் காட்டுக்குள்ள ஓடுறாங்க.",
    "the father pulling his son by the hand through a dense dry forest at dawn", ["Father", "Son"]),
   ("அப்போதான் பையனுக்கு அப்பாவோட பழைய கதை தெரியுது. இளமையில, அவர் ஒரு பயங்கரமான வீரன்! தன்னோட மக்களுக்காக அவர் நிறைய ரத்தம் சிந்தியிருக்காரு.",
    "a fierce young version of the father with thick black hair, shirtless, holding a machete, standing defiant in a burning village at night", []),
   ("கடைசியில, மகனைக் காப்பாத்த, அந்த அமைதியான அப்பா மறுபடியும் ஆயுதம் எடுக்கிறாரு.",
    "the father standing alone in a field facing a mob of armed men, gripping a machete, dust rising", ["Father"]),
   ("ஆனா அவர் மகனுக்குச் சொல்ற கடைசி பாடம்... ஆயுதம் இல்ல, படிப்புதான் நம்மளைக் காப்பாத்தும்.",
    "the father with a hand on his son's shoulder at a village bus stop, the son holding school books", ["Father", "Son"]),
   ("க்ளூ: ஹீரோ பேரு சிவசாமி. " + CTA,
    "silhouette of the father walking along a red-earth path at sunset", ["Father"]),
  ]),
 dict(n=6, answer="Papanasam (பாபநாசம், 2015)", style=VILLAGE,
  clues=["குடும்ப த்ரில்லர்", "ஹீரோ பேரு சுயம்புலிங்கம்", "ஒரு மலையாளப் படத்தோட தமிழ் ரீமேக்"],
  chars={"Father": "Tamil man in his fifties, thick moustache, receding hair, kind tired eyes, white shirt and veshti, simple wristwatch"},
  scenes=[
   ("ஒரு சின்ன ஊர்ல, கேபிள் டிவி நடத்துற சுயம்புலிங்கம். சினிமான்னா அவருக்கு உயிர். மனைவி, ரெண்டு பொண்ணுங்க... சந்தோஷமான குடும்பம்.",
    "the father sitting in a small cable TV office in a town, watching an old film on a TV, smiling", ["Father"]),
   ("ஒரு நாள், அவரோட மூத்த பொண்ணைத் தொந்தரவு பண்ண ஒரு பையன் வீட்டுக்கு வர்றான். தற்காப்புக்காக நடந்த சண்டையில, அந்தப் பையன் செத்துப்போறான்.",
    "a dark farmhouse yard at night in the rain, a frightened mother and teenage daughter clutching each other, a fallen shadow on the ground", []),
   ("அந்தப் பையன்... ஒரு பெரிய போலீஸ் அதிகாரியோட மகன்!",
    "a stern senior police officer in uniform staring at a missing-person file in a dim office", []),
   ("குடும்பத்தைக் காப்பாத்த, சுயம்புலிங்கம் ஒரு பெரிய திட்டம் போடுறாரு. தான் பார்த்த சினிமாக்கள்ல இருந்தே யோசனை எடுக்கிறாரு.",
    "the father sitting alone at night in front of a glowing TV, deep in thought, a calendar and bus tickets on the table", ["Father"]),
   ("போலீஸ் குடும்பத்தையே பிடிச்சு அடிச்சு விசாரிக்குது. ஆனா யாருமே உண்மையைச் சொல்லல.",
    "the father, his wife and two daughters sitting in a police interrogation room under a harsh bulb, bruised but silent", ["Father"]),
   ("ஒவ்வொரு கேள்விக்கும், அவங்க ஒரே பதிலைச் சொல்றாங்க. போலீசால எதையும் நிரூபிக்க முடியல.",
    "a frustrated police officer slamming a table while the father sits calmly across from him", ["Father"]),
   ("அந்த உடல் எங்க புதைக்கப்பட்டதுன்னு தெரிஞ்சா... நீங்க அதிர்ச்சி ஆயிடுவீங்க!",
    "the father standing outside a newly built police station at dusk, looking at its foundation, expressionless", ["Father"]),
   ("க்ளூ: ஹீரோ பேரு சுயம்புலிங்கம். " + CTA,
    "the father's face half lit by a flickering TV screen in a dark room", ["Father"]),
  ]),
 dict(n=7, answer="Ghilli (கில்லி, 2004)", style=CITY,
  clues=["ஆக்ஷன் படம், கபடி விளையாட்டு", "ஹீரோ பேரு வேலு", "தெலுங்கு 'ஒக்கடு' படத்தோட தமிழ் ரீமேக்"],
  chars={"Velu": "Tamil young man in his early twenties, athletic build, short spiky black hair, light moustache, confident grin, sleeveless kabaddi jersey and shorts",
         "Heroine": "Tamil young woman about twenty, long braided black hair, frightened big eyes, simple half-saree"},
  scenes=[
   ("சென்னையில, கபடி விளையாட்டுல வெறி பிடிச்ச ஒரு பையன், வேலு. படிப்புல சுமார், கபடியில ராஜா. அவனோட அப்பா ஒரு கண்டிப்பான போலீஸ் அதிகாரி.",
    "Velu raiding in a dusty kabaddi court, leaping over defenders, a cheering crowd", ["Velu"]),
   ("கபடி போட்டிக்காக மதுரைக்குப் போறான். அங்க, ஒரு பெரிய ரவுடி ஒரு பொண்ணைக் கட்டாயக் கல்யாணம் பண்ணப் பார்க்கிறான்.",
    "a menacing rowdy with a thick moustache and gold chains, surrounded by henchmen in a Madurai street, a terrified young woman behind him", ["Heroine"]),
   ("வேலு அந்தப் பொண்ணைக் காப்பாத்தி, சென்னைக்குத் தூக்கிட்டு வந்துடுறான்.",
    "Velu running with the young woman through a crowded Madurai bus stand, henchmen chasing them", ["Velu", "Heroine"]),
   ("அவளை, தன் வீட்டு மாடியிலயே யாருக்கும் தெரியாம ஒளிச்சு வைக்கிறான். கீழ இருக்கிறது... போலீஸ் அப்பா!",
    "the young woman hiding behind a door in a small rooftop room while Velu peeks down the stairs nervously", ["Velu", "Heroine"]),
   ("ரவுடி அவளைத் தேடி சென்னைக்கே வந்துடுறான். ஒரு பக்கம் கபடி ஃபைனல், இன்னொரு பக்கம் உயிர்ப் போராட்டம்.",
    "the rowdy's jeep convoy roaring into a Chennai street at night, headlights glaring", []),
   ("கடைசியில, ரவுடியைத் தோற்கடிச்சு, அந்தப் பொண்ணைக் காப்பாத்துறான் வேலு!",
    "Velu in a dramatic fight with the rowdy on a lighthouse beach at dusk, sand flying", ["Velu"]),
   ("ஒரு சாதாரண கபடி பையன், ஒரு உண்மையான ஹீரோ ஆயிடுறான்.",
    "Velu lifting a kabaddi trophy, his teammates lifting him on their shoulders", ["Velu"]),
   ("க்ளூ: ஹீரோ பேரு வேலு. " + CTA,
    "Velu standing in the centre of an empty kabaddi court at sunset, hands on his knees, grinning", ["Velu"]),
  ]),
 dict(n=8, answer="Soorarai Pottru (சூரரைப் போற்று, 2020)", style=VILLAGE,
  clues=["ஒரு உண்மைக் கதையை அடிப்படையா வச்ச படம்", "ஹீரோ பேரு நெடுமாறன்", "நேரடியா OTT-ல வெளியான படம்"],
  chars={"Maara": "Tamil man in his early thirties, short black hair, thick moustache, fiery determined eyes, pale blue shirt with rolled sleeves",
         "Wife": "Tamil woman in her late twenties, long black hair in a braid, bold confident smile, cotton saree, flour on her hands"},
  scenes=[
   ("ஒரு கிராமத்துப் பையன், நெடுமாறன். விமானப் படையில வேலை பார்க்கிறான்.",
    "Maara in an Indian Air Force uniform standing on an airbase runway beside a fighter jet", ["Maara"]),
   ("ஒரு நாள், சாகக் கிடக்கிற அப்பாவைப் பார்க்க, விமான டிக்கெட் வாங்கக் காசு இல்லாம தவிக்கிறான். அப்பா முகத்தைக் கடைசியா பார்க்கவே முடியல.",
    "Maara at an airport ticket counter begging desperately, counting a few coins and notes in his hand, people staring", ["Maara"]),
   ("அன்னைக்கு ஒரு சபதம் எடுக்கிறான். சாதாரண மக்களும் பறக்கணும். ஒரு ரூபாய்க்கு விமான டிக்கெட்!",
    "Maara standing in a village field at night looking up at a plane's lights crossing the stars, determined", ["Maara"]),
   ("வேலையை விட்டுட்டு, சொந்தமா ஒரு விமான நிறுவனம் தொடங்கப் போராடுறான். ஒரு பெரிய விமான நிறுவன முதலாளி, அவனை எல்லா வழியிலயும் தடுக்கிறான்.",
    "a cold rich businessman in a grey suit in a glass office tower, tearing up a document, Maara standing defiant in front of him", ["Maara"]),
   ("பணம் இல்ல, ஆதரவு இல்ல. ஆனா அவன் மனைவி, தன் சொந்த பேக்கரியில சம்பாதிச்சு அவனுக்குத் துணையா நிக்கிறா.",
    "Maara's wife in a small busy bakery taking out a tray of fresh bread, smiling at Maara who sits tired at a table", ["Wife", "Maara"]),
   ("எத்தனை தடவை விழுந்தாலும், அவன் மறுபடியும் எழுந்து நிக்கிறான்.",
    "Maara standing alone in the rain outside a government office, papers soaked, jaw clenched", ["Maara"]),
   ("கடைசியில, அவனோட முதல் குறைந்த கட்டண விமானம் வானத்துல பறக்குது! கிராமத்து மக்கள் முதல் தடவையா விமானத்துல பறக்கிறாங்க.",
    "a small passenger plane taking off at sunrise while villagers in simple clothes cheer and wave from the edge of the runway", []),
   ("க்ளூ: ஹீரோ பேரு நெடுமாறன். " + CTA,
    "Maara in the cockpit doorway of a plane, smiling with tears in his eyes", ["Maara"]),
  ]),
 dict(n=9, answer="Jai Bhim (ஜெய் பீம், 2021)", style=GRITTY,
  clues=["ஒரு உண்மைச் சம்பவத்தை அடிப்படையா வச்ச நீதிமன்றப் படம்", "வக்கீல் பேரு சந்துரு, அந்தப் பொண்ணு பேரு செங்கேணி", "2021-ல வெளியான படம்"],
  chars={"Wife": "Tamil tribal woman in her late twenties, dark skin, hair tied back, worn cotton saree, tear-stained determined face",
         "Lawyer": "Tamil man in his forties, black lawyer's coat and white bands, short black hair, thick moustache, glasses, calm intense eyes"},
  scenes=[
   ("ஒரு பழங்குடி கிராமம். செங்கேணியும் அவ கணவனும், கூலி வேலை பார்க்கிற ஏழைகள்.",
    "a small tribal hamlet of mud huts at the edge of rice fields, the wife and her husband laughing together outside their hut", ["Wife"]),
   ("ஊர்ல ஒரு வீட்டுல நகை திருட்டு. எந்தச் சாட்சியும் இல்லாம, போலீஸ் அவ கணவனைப் பிடிச்சுட்டுப் போகுது.",
    "policemen dragging a thin tribal man away from his hut while his wife screams and villagers watch helplessly", ["Wife"]),
   ("லாக்கப்ல, அவனை கொடூரமா அடிச்சு சித்ரவதை பண்றாங்க.",
    "a dim police lockup with iron bars, a shadow of a raised baton on the wall, nothing graphic", []),
   ("அடுத்த நாள், அவன் தப்பிச்சு ஓடிட்டான்னு போலீஸ் சொல்லுது. ஆனா அவன் எங்க போனான்னு யாருக்குமே தெரியல.",
    "the wife standing alone in front of a police station, holding a small photo of her husband, officers turning away", ["Wife"]),
   ("நியாயம் கேட்டு, செங்கேணி ஒரு வக்கீலைத் தேடிப் போறா. ஏழைகளுக்காக காசே வாங்காம வாதாடுற வக்கீல்.",
    "the wife sitting across a desk from the lawyer in a cluttered office full of case files, the lawyer listening intently", ["Wife", "Lawyer"]),
   ("அவர் நீதிமன்றத்துல ஒவ்வொரு பொய்யையும் உடைக்கிறாரு. உண்மை வெளிய வருது. போலீஸ் லாக்கப்லேயே அவன் இறந்துட்டான்!",
    "the lawyer arguing passionately in a packed courtroom, pointing at a police officer in the witness box", ["Lawyer"]),
   ("ஒரு ஏழைப் பொண்ணோட போராட்டம், மொத்த அமைப்பையே ஆட வச்சுது.",
    "the wife walking out of the court building into bright sunlight, villagers waiting for her with folded hands", ["Wife"]),
   ("க்ளூ: வக்கீல் பேரு சந்துரு, அந்தப் பொண்ணு பேரு செங்கேணி. " + CTA,
    "the lawyer standing on the court steps, looking up, a determined expression", ["Lawyer"]),
  ]),
 dict(n=10, answer="Anniyan (அந்நியன், 2005)", style=CITY,
  clues=["சைக்கலாஜிக்கல் த்ரில்லர்", "ஹீரோ பேரு அம்பி, இன்னொரு பேரு ரெமோ", "இயக்குநர் ஷங்கர் படம்"],
  chars={"Ambi": "thin Tamil man in his early thirties, neatly combed oiled hair, clean-shaven, innocent nervous eyes, plain half-sleeve shirt tucked into trousers, sacred ash on his forehead"},
  scenes=[
   ("அம்பி, ஒரு அப்பாவி வக்கீல். விதிமுறைன்னா விதிமுறை. சின்ன தப்பைக் கூட அவனால தாங்க முடியாது.",
    "Ambi standing in a busy Chennai street with a rulebook in hand, frowning at people jumping a queue", ["Ambi"]),
   ("ஆனா யாருமே அவன் பேச்சைக் கேக்கல. எல்லாரும் அவனைக் கிண்டல் பண்றாங்க.",
    "a crowd of office workers laughing at Ambi, who looks hurt and alone", ["Ambi"]),
   ("அப்போ ஊர்ல மர்மக் கொலைகள். லஞ்சம் வாங்குறவங்க, ஏமாத்துறவங்க... ஒவ்வொருத்தரும் கொடூரமா தண்டிக்கப்படுறாங்க.",
    "a dark rainy alley at night, police tape, a shadowy figure with long wild hair disappearing into the darkness", []),
   ("கொலைகாரன், கருட புராணத்துல சொல்லியிருக்கிற தண்டனைகளையே கொடுக்கிறான்.",
    "an old palm-leaf manuscript lying open on a table under a candle, ominous shadows on the wall", []),
   ("இன்னொரு பக்கம், அம்பி ஸ்டைலான ரெமோவா மாறி, தான் காதலிக்கிற பொண்ணோட மனசைக் கவர்றான்.",
    "the same man as a stylish fashion model with spiked hair, a leather jacket and sunglasses, posing confidently under neon lights", []),
   ("போலீஸ் கண்டுபிடிக்கிற உண்மை... அதிர்ச்சி! அந்த அப்பாவி, ரெமோ, கொலைகாரன்... மூணு பேருமே ஒரே ஆள்!",
    "Ambi staring into a cracked mirror that shows three different reflections of himself: innocent, stylish and fierce", ["Ambi"]),
   ("சமூகத்தோட அலட்சியம்தான், ஒரு அப்பாவியை அரக்கனா மாத்துச்சு.",
    "Ambi sitting alone on a hospital bed in a white room, looking at his own hands", ["Ambi"]),
   ("க்ளூ: ஹீரோ பேரு அம்பி. இன்னொரு பேரு ரெமோ. " + CTA,
    "Ambi's face split by light and shadow, half calm and half fierce", ["Ambi"]),
  ]),
]

# How each answer is said aloud in the next video (numbers spelled out so the voice reads them right).
SPOKEN = {1: "ராட்சசி", 2: "கைதி", 3: "எந்திரன்", 4: "தொண்ணூத்தி ஆறு", 5: "அசுரன்", 6: "பாபநாசம்", 7: "கில்லி",
          8: "சூரரைப் போற்று", 9: "ஜெய் பீம்", 10: "அந்நியன்"}
WRITTEN = {**SPOKEN, 4: "96"}
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
