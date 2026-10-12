# Series Bible: கண்ணன் கதைகள் (Kannan Kathaigal)

Everything here is **locked**. Change it only on purpose and update this file when you do, because consistency across 50+ episodes depends on it.

## 1. Visual style (chosen and fixed)

**Style: cinematic stylised 3D, "premium Indian animated feature".** Semi-realistic proportions, expressive large eyes, soft skin shading, painterly golden lighting, rich textiles and real-world materials (clay, brass, wood, silk).

Why this rather than photoreal:
- AI keeps stylised faces **far more consistent** between shots than photoreal faces.
- It avoids the uncanny "AI actor" look and distorted realistic faces.
- Devotional audiences generally accept a reverent animated depiction of deities more readily than a photoreal human playing God.
- Lip-sync tools still work well on this style at close-up distance.

### MASTER STYLE BLOCK (paste at the start of every image and video prompt)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality,
semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed
traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays,
soft atmospheric haze, shallow depth of field, rich saturated but natural colours
(saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga),
vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.
```

### MASTER NEGATIVE BLOCK (paste at the end, or into a negative-prompt field if the tool has one)
```
Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces,
extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery,
changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image,
blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

### Colour and light rules
| Mood | Palette | Light |
|---|---|---|
| Playful / home | Butter-yellow, terracotta, leaf green | Warm morning sun through windows, dust motes |
| Tension / danger | Desaturated teal, smoke grey | Low-key, side light, dark sky |
| Divine / miracle | Deep indigo, gold, white | Golden light from within the character, cosmic particles, soft bloom |

## 2. Characters

**How to build reference sheets (do this once):**
1. Paste MASTER STYLE + the character prompt + `Full-body front view, standing straight, plain light-grey background, even soft lighting, face clearly visible.` + MASTER NEGATIVE into Nano Banana. Generate until one image is right. (Tamil versions of all these prompts: [02b-character-prompts-tamil.md](02b-character-prompts-tamil.md).)
2. Then ask, using that image as the reference: *"Same character, character turnaround sheet: front view, three-quarter view, side profile, full body, on a plain light background."*
3. Then: *"Same character, expression sheet: happy laughing, mischievous grin, innocent wide eyes, sad, surprised."*
4. Save as `refs/krishna_child_front.png`, `refs/krishna_child_turnaround.png` and so on. **Upload the front portrait plus one full-body image as references for every shot that character appears in.**

### 2.1 Child Krishna (கண்ணன்), age ~5: Episodes 1–16
**Identity anchors (must never change):** blue-black (neela megha) skin, large almond-shaped dark eyes with kohl, a black dhrishti dot on the left cheek, a peacock feather in the topknot, a yellow silk dhoti, and a mischievous half-smile.

```
CHARACTER: Child Krishna, 5-year-old Indian boy, deep blue-black skin with soft sheen (colour of a rain cloud),
round cheeks, large almond-shaped dark brown eyes lined with black kohl, small black dhrishti dot on left cheek,
long eyelashes, small button nose, playful mischievous half-smile showing small teeth,
black curly hair tied in a small topknot on top of the head with a single peacock feather tucked in,
a few curls falling on the forehead, small gold crown-band (thin, simple) around the topknot,
bright turmeric-yellow silk dhoti (pitambaram) tied at the waist with a gold sash,
thin gold waist-chain with tiny bells, gold armlets, small gold earrings,
a necklace of tulsi beads and a short garland of small white jasmine and orange marigold,
gold anklets with tiny bells, barefoot, a small bamboo flute tucked into the waist sash.
```

### 2.2 Teen Krishna, age ~16: from Episode 15 onwards (Govardhan / flute / Radha)
Same face structure, now older. Keep the skin, eyes, peacock feather, yellow silk and flute.
```
CHARACTER: Young Krishna, 16 years old, same deep blue-black skin and kohl-lined almond eyes as the child version,
slim athletic build, gentle confident smile, shoulder-length black curly hair partly tied up,
golden crown with a large peacock feather, yellow silk dhoti and a dark blue angavastram over one shoulder,
long vaijayanti garland of forest flowers, gold earrings shaped like makara fish, bamboo flute held in the right hand.
```

### 2.3 Yashoda (யசோதை), age ~28
```
CHARACTER: Yashoda, 28-year-old Indian village mother, warm wheat-brown skin, kind oval face, large expressive eyes,
red kumkum dot on forehead, long black hair in a thick braid decorated with jasmine flowers,
cotton saree in deep red with a mustard-yellow border draped in a simple ancient style, short-sleeved blouse,
glass and gold bangles on both wrists, simple gold necklace, small nose stud, silver anklets (kolusu),
warm maternal expression that easily breaks into laughter.
```

### 2.4 Balarama (பலராமன்), age ~7, Krishna's elder brother
```
CHARACTER: Balarama, 7-year-old Indian boy, fair light skin, sturdy build, confident face, short wavy black hair in a topknot,
deep indigo-blue cotton dhoti, simple gold earrings and armlets, a small white conch-bead necklace.
```

### 2.5 Shridama (ஸ்ரீதாமா), age ~6, cowherd friend, the "strong one"
```
CHARACTER: Shridama, 6-year-old Indian cowherd boy, medium brown skin, chubby and sturdy, round face, big laugh,
short messy hair with a cloth headband in green, short off-white cotton dhoti, a small wooden cowbell on a string around the neck.
```

### 2.6 Subala (சுபலன்), age ~5, cowherd friend, the "worrier"
```
CHARACTER: Subala, 5-year-old Indian cowherd boy, light brown skin, thin and small, big worried eyes, eyebrows often raised,
hair tied in a tiny tuft, short saffron-orange cotton dhoti, a string of red beads on the wrist, carries a small shepherd's stick.
```

### 2.7 Future characters: create refs only when their episode arrives
| Character | Key anchors |
|---|---|
| Baby Krishna (newborn to 1 yr) | same skin and eyes; four-armed divine form only in the birth scene; peacock feather |
| Nanda (நந்தகோபர்) | 35, kind bearded village chief, white dhoti, turban |
| Vasudeva and Devaki | prisoners in Mathura, chains, worn royal clothes |
| Kamsa (கம்சன்) | imposing king, dark red and black armour, heavy gold crown, cruel eyes; never cartoonish |
| Putana (பூதனை) | beautiful disguise that turns into a giant demoness. Keep the transformation scary but **not gory** (family audience) |
| Radha (ராதை) | 15, fair, gentle; deep pink lehenga, jasmine braid |
| Kaliya | five-hooded giant black serpent with gem-crowns |

## 3. Voice casting (ElevenLabs; save each as a named voice and always reuse the same voice ID)

> **Full, detailed voice casting** (age- and gender-matched voices for every character, ElevenLabs Voice Design prompts, child/elderly voice strategy, voice register) is in [04-voices-and-cinematic-flow.md](04-voices-and-cinematic-flow.md). The table below is the short version.

| Character | Voice brief | Settings guide |
|---|---|---|
| Child Krishna | Young, high-pitched, playful, cheeky, giggly; Chennai/neutral Tamil accent | Stability low-mid (~35%) for expressiveness; Style high. If Voice Design won't produce a child voice, use a light, youthful female voice with Tamil accent, or a parent-consented recording of a real child converted with Speech-to-Speech. |
| Yashoda | Warm, affectionate, mother of a naughty child: scolding that melts into laughter | Stability ~50% |
| Balarama | Slightly older boy, bossy and proud big brother | Stability ~45% |
| Shridama | Chubby kid voice, loud, laughs a lot | Stability ~35% |
| Subala | Small, nervous, whiny kid | Stability ~40% |
| Narrator (கதைசொல்லி) | Warm male storyteller like a grandfather telling a bedtime story; slow, smiling, with dramatic pauses | Stability ~60%; keep the same narrator for the whole series, since it is the show's signature |

**Tamil pronunciation rules for every TTS take:** check ழ / ள / ல, ற / ர, ண / ந / ன by ear. If the TTS mispronounces a word, respell it phonetically in Tamil script (for example, write it the way it's spoken) or split it with a hyphen. Never publish a line you haven't listened to in full.

## 4. Series identity
| Element | Spec |
|---|---|
| Series name | **கண்ணன் கதைகள்** (Kannan Kathaigal) |
| Episode title format | `கண்ணன் கதைகள் #01 | வெண்ணெய் திருடன்` |
| Cold open | Every episode opens **on action or a line of dialogue in the first 2 seconds**, with no logo first |
| Title sting | At ~0:03, a 1.5 s overlay: a peacock feather sweeps across the screen with a single flute note, and the series name plus episode number in a gold Tamil display font (e.g. *Mukta Malar ExtraBold* or *Catamaran Black*, free Google Fonts) |
| Subtitles | Tamil, white, bold, 2 lines max, ~18 characters per line, black 4px outline + soft shadow, placed at **62–68% of screen height** (above the YouTube/Instagram UI). Narrator lines in *italic*; Krishna's lines in **light gold (#FFD966)** so viewers instantly know who's speaking. |
| Ending | The last 4 s are always a hook: a cliffhanger frame, then the card `அடுத்த எபிசோட்: <title>` + the flute motif + "Follow பண்ணுங்க 🙏" |
| Music signature | A 4-note flute motif used in every opening and ending (generate once in Suno and reuse) |
| Cover / thumbnail | Close-up of Krishna's face reacting + 2–3 word Tamil title in gold; no clickbait |
| Description footer | "Based on Srimad Bhagavatam, Canto 10, ch. X. Dialogue and some scenes are creative adaptations for storytelling." |

## 5. Tradition vs. adaptation policy
- Every episode file has a **"Source & adaptation"** box that names the traditional source and lists what was invented (dialogue, comic lines, timeline compression, extra characters).
- Never put invented details in the narrator's mouth as fact ("the scriptures say...") unless they actually are.
- Where traditions differ (for example, Radha is not named in the Bhagavatam but is central in Gita Govinda and later tradition), say so in the description.
- Tone: playful is fine, mocking is not. Krishna can be naughty; he is never humiliated, and divine moments are treated with awe.

## 6. Krishna series roadmap
Episode 1 is a **pilot**: it opens on Krishna's personality (the butter thief) rather than the dark prison birth, to hook new viewers. Episodes 3–4 then go back to tell the birth as a flashback ("கண்ணன் எப்படி கோகுலம் வந்தான்?"), and the series runs strictly forward from there.

| # | Title | Incident | Source (Bhagavatam Canto 10) | Ending hook |
|---|---|---|---|---|
| 1 | வெண்ணெய் திருடன் | Butter theft with friends | 10.8.29–31 | "Krishna ate mud!" → "open your mouth" |
| 2 | வாய்க்குள் ஒரு பிரபஞ்சம் | Yashoda sees the universe in his mouth | 10.8.32–45 | "But who is this child really?" |
| 3 | சிறையில் ஒரு இரவு | Birth in Kamsa's prison | 10.3 | The prison gates open by themselves |
| 4 | யமுனையைக் கடந்து | Vasudeva carries the baby across the Yamuna | 10.3–10.4 | Kamsa learns the child escaped |
| 5 | பூதனை | Putana's poisoned milk | 10.6 | "Kamsa sends the next demon" |
| 6 | சூறாவளி அசுரன் | Shakatasura / Trinavarta | 10.7 | — |
| 7 | உரலில் கட்டிய கண்ணன் | Damodara: Yashoda ties him to a mortar | 10.9 | He drags the mortar toward two trees… |
| 8 | இரண்டு மரங்கள் | Yamalarjuna liberation | 10.10 | — |
| 9 | பிருந்தாவனம் | The family moves to Vrindavan | 10.11 | — |
| 10 | கன்றுக்குட்டி அசுரன் | Vatsasura and Bakasura | 10.11 | — |
| 11 | பாம்பு வாய்க்குள் | Aghasura | 10.12 | — |
| 12 | பிரம்மாவின் சோதனை | Brahma steals the calves and boys | 10.13–14 | — |
| 13 | காளிங்க நர்த்தனம் | Dance on Kaliya | 10.16 | — |
| 14 | காட்டுத் தீ | Swallowing the forest fire | 10.17, 10.19 | — |
| 15 | கோவர்த்தன கிரி | Lifting Govardhan | 10.24–25 | Transition to teen Krishna |
| 16 | புல்லாங்குழல் | The flute that stops the world | 10.21 | — |
| 17 | ராதை | Meeting Radha (flag the source: Gita Govinda / later tradition) | — | — |
| 18 | அக்ரூரர் வருகை | Akrura arrives to take him to Mathura | 10.38–39 | — |
| 19 | கோகுலத்துக்கு விடை | Farewell to Yashoda and Vrindavan | 10.39 | — |
| 20 | கம்ச வதம் | Defeat of Kamsa | 10.44 | — |
| 21+ | Sandipani & Sudama, Rukmini, Dwaraka, Draupadi, Kurukshetra and the Gita | | | |

**Long-form grouping (10–12 min episodes):** each long episode covers 2–3 rows above, and the rows become its Shorts.
Long 1 = rows 1–2 (Gokulam day + universe in the mouth) · Long 2 = rows 3–4 (birth and Yamuna crossing) · Long 3 = rows 5–6 (Putana and the infant demons) · Long 4 = rows 7–8 (Damodara) · Long 5 = rows 9–11 (Vrindavan and the demons) · Long 6 = row 12 · Long 7 = rows 13–14 · Long 8 = rows 15–16 · Long 9 = row 17 · Long 10 = rows 18–20.

## 7. Adapting to other gods
Copy this file to `ganesha-bible.md` / `murugan-bible.md`, keep §1 (style), and replace §2 (characters), §3 (voices) and §6 (roadmap). Example sources: Ganesha (Ganesha Purana, Shiva Purana); Murugan (Kanda Puranam, Thiruppugazh, Tamil temple traditions). Murugan especially suits a Tamil audience (the six Padai Veedu as a natural 6-episode arc).
