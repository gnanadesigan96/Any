# Voice Casting and Cinematic Flow

Two things make AI clips feel like a **movie** instead of a slideshow: **voices that truly fit each character** and **continuity**, meaning picture and sound flow from one shot to the next. This file covers both.

---

# Part A: Tamil voice casting

## A1. Casting rules (all characters)
1. **Age and gender must match what you see.** A 5-year-old boy sounds like a 5-year-old boy; a 60-year-old paati sounds like a paati. No adult-sounding children and no young-sounding grandparents.
2. **Every character has a different voice.** Close your eyes during a conversation: you should always know who is speaking. Vary **pitch** (high/low), **texture** (bright, husky, soft, gravelly) and **speed**.
3. **Native Tamil sound.** Natural spoken Tamil, Tamil Nadu accent, correct ழ / ள / ற. No English or Hindi accent.
4. **One character = one voice forever.** Save each voice, write down its exact settings, and never change them between episodes (except when the character grows up; see A5).
5. **Emotion first.** The same line can be angry, teasing or loving. Each line in the script has a tone note; the voice must deliver *that* tone.

## A2. The best way to get each type of voice (honest assessment)

AI Tamil voices are **excellent for adults and the narrator**, and **still the weakest for small children**: they often sound like an adult putting on a "baby voice". For a real movie feel, use this hybrid approach:

| Voice type | Best option | Good option | Avoid |
|---|---|---|---|
| **Child (boy or girl, 4–8)** | **A real child reads the lines** (family member or friend's child, with parental consent), recorded on a phone in a quiet room. Then pass it through **ElevenLabs Voice Changer** set to that character's saved voice, so it sounds the same in every episode even if a different child records. | **An adult voice artist who does child voices.** Tamil dubbing traditionally has women voicing young boys. Record them, or ask for consent to make a voice clone of their "kid voice". | Plain TTS "child voices" for emotional lines |
| **Women (20–40)** | ElevenLabs Voice Design / Voice Library | Sarvam Bulbul female voices | — |
| **Men (25–50)** | ElevenLabs Voice Design / Voice Library | Sarvam Bulbul male voices | — |
| **Elderly (55+)** | ElevenLabs Voice Design ("elderly", "aged", "slightly shaky") | A real grandparent reading the lines + Voice Changer (sounds wonderfully authentic) | Young voices with lowered pitch |
| **Narrator** | ElevenLabs Voice Design (warm elderly male) | A real elder in your family with a good storytelling voice | — |
| **Villains / divine voices** | ElevenLabs Voice Design + light effects in CapCut (low-end boost, reverb) | — | Overdone robotic effects |

**Consent and rights:** get written consent from any adult whose voice you record or clone, and from a parent or guardian for any child. Never clone a celebrity, film actor or dubbing artist without permission.

### How ElevenLabs Voice Changer keeps a voice consistent
1. Record the line performed with the right emotion (by a child, by you, by anyone).
2. ElevenLabs → **Voice Changer** → upload the recording → choose the character's saved voice (e.g. "Kannan") → generate.
3. The result keeps **the performance** (timing, laughs, emotion) but uses **the character's voice**. This is how you get real acting with a consistent voice.

## A3. Character voice sheets: Part 1 cast

For each character: description to use in **ElevenLabs → Voices → Voice Design** (paste the English description), suggested starting settings, and a **test line** for auditioning. Generate 3–6 options, choose one, click **Save voice**, and name it exactly as below.

> Settings are starting points: **Stability** (lower = more emotional, higher = steadier), **Similarity** ~75%, **Style** (higher = more expressive), **Speed** 1.0 = normal. Write down your final values in the table in A6.

---

### கண்ணன் (Kannan): boy, ~5 years
| | |
|---|---|
| **Sound** | High, bright, sweet, cheeky; giggles inside his sentences; quick bouncy rhythm. Innocent sing-song when lying; **calm, slow and soft** in divine moments |
| **Best source** | A real 5–8-year-old boy (or girl; at this age either works) performing the lines → Voice Changer to the "Kannan" voice |
| **Voice Design prompt** | `A young, high-pitched, playful and mischievous voice of a small boy, native Tamil speaker from Tamil Nadu, speaking natural colloquial Tamil, bright and sweet tone, giggles easily, fast and bouncy rhythm, warm and innocent.` |
| **Settings** | Stability 30–40% · Style 50–60% · Speed 1.05 |
| **Test line** | `டேய், என்னைப் பிடிக்க முடியுமா? பிடிச்சுப் பாரு!` then `அம்மா, நான் ஒண்ணுமே பண்ணலையே!` |
| **Must not sound like** | An adult woman doing a baby voice; a teenager |

### பலராமன் (Balarama): boy, ~7 years
| | |
|---|---|
| **Sound** | Clearly a boy, but **2 years older and lower** than Kannan; firm, proud, a little bossy; clear diction; louder |
| **Voice Design prompt** | `Voice of a confident 7-year-old boy, native Tamil speaker, natural colloquial Tamil, slightly lower and stronger than a small child, firm and proud big-brother tone, clear and loud.` |
| **Settings** | Stability 45% · Style 40% · Speed 1.0 |
| **Test line** | `நான் வரல. அம்மா கிட்ட சொல்லிடுவேன் பாரு!` |

### ஸ்ரீதாமா (Shridama): boy, ~6 years, chubby
| | |
|---|---|
| **Sound** | Round, slightly husky, loud and cheerful; big belly laugh; a bit breathless when straining |
| **Voice Design prompt** | `Voice of a chubby, cheerful 6-year-old boy, native Tamil speaker, colloquial Tamil, slightly husky and round tone, loud, laughs a lot, friendly and simple.` |
| **Settings** | Stability 35% · Style 45% · Speed 0.95 |
| **Test line** | `வந்துட்டான்டா நம்ம தலைவன்!` then `கண்ணா... நீ குட்டியா இருந்தாலும் கனமா இருக்கடா!` |

### சுபலன் (Subala): boy, ~5 years, nervous
| | |
|---|---|
| **Sound** | Thin, small, whiny, worried; voice rises at the end of sentences; whispers when scared |
| **Voice Design prompt** | `Voice of a small, thin, nervous 5-year-old boy, native Tamil speaker, colloquial Tamil, thin and slightly whiny tone, worried, often whispering, voice rising when scared.` |
| **Settings** | Stability 35% · Style 50% · Speed 1.05 |
| **Test line** | `ஐயோ! போன வாரம் மாட்டினப்போ அவங்க தொரத்துனது மறந்துட்டியா?` |

**Check that the boys sound different from each other:** Kannan = brightest and sweetest · Subala = thinnest and most nervous · Shridama = roundest and loudest · Balarama = lowest and firmest.

---

### யசோதை (Yashoda): woman, ~28, mother
| | |
|---|---|
| **Sound** | Warm, soft mid-low female voice; affectionate; "angry" scolding that cracks into laughter; tender whisper for lullabies; real worry in Scene 7 |
| **Voice Design prompt** | `Warm, loving voice of a young Tamil mother in her late twenties, native Tamil speaker from a village in Tamil Nadu, natural colloquial Tamil, soft medium-low pitch, affectionate, playful scolding that easily turns into laughter, gentle and caring.` |
| **Settings** | Stability 45–50% · Style 40% · Speed 1.0 |
| **Test line** | `கண்ணா, திரும்பவும் வெண்ணெய் திருடித் தின்னியா?` then `என் செல்லத் திருடா...` |
| **Lullaby** | Sing it in Suno (female Tamil lullaby) or have a real person hum it. TTS can't sing. |

### கோமதி அக்கா (Gomathi): woman, ~30, loud neighbour
| | |
|---|---|
| **Sound** | Sharper and louder than Yashoda; fast, theatrical, a little nasal; melts at the end |
| **Voice Design prompt** | `Loud, expressive voice of a 30-year-old Tamil village woman, native Tamil speaker, fast colloquial Tamil, sharp and slightly nasal, dramatic and theatrical when angry, but warm underneath.` |
| **Settings** | Stability 35% · Style 55% · Speed 1.1 |
| **Test line** | `அடேய் கண்ணா!! திரும்பவும் நீயா?!` |

### கமலா (Kamala): young woman, ~22
| | |
|---|---|
| **Sound** | Youngest adult woman: lighter and higher than Yashoda and Gomathi; lively, giggly |
| **Voice Design prompt** | `Bright, lively voice of a 22-year-old Tamil village girl, native Tamil speaker, colloquial Tamil, light higher pitch, energetic and giggly, expressive.` |
| **Settings** | Stability 40% · Style 50% · Speed 1.05 |
| **Test line** | `பாரு பாரு! உதட்டுல இன்னும் வெண்ணெய் இருக்கு!` |

### பாட்டி (Paati): elderly woman, ~60–65
| | |
|---|---|
| **Sound** | Aged, slightly shaky, slower, a bit breathy and crackly; dignified; rural |
| **Best source** | A real grandmother reading the line is wonderful here |
| **Voice Design prompt** | `Voice of an elderly Tamil grandmother around 65 years old, native Tamil speaker from a village, slow colloquial Tamil, slightly shaky and breathy aged voice, dignified, scolding gently.` |
| **Settings** | Stability 55% · Style 35% · Speed 0.85 |
| **Test line** | `பால் கறக்குற நேரத்துக்கு முன்னாடியே கன்னுக்குட்டியை அவுத்து விட்டுடறான்!` |

**Check that the women sound different:** Kamala = youngest and highest · Yashoda = warmest and softest · Gomathi = loudest and sharpest · Paati = oldest and slowest.

---

### நந்தகோபர் (Nandagopar): man, ~35, father
| | |
|---|---|
| **Sound** | Deep, calm, slow, kind; a chuckle in his voice |
| **Voice Design prompt** | `Deep, calm and kind voice of a 35-year-old Tamil village chief and father, native Tamil speaker, slow natural colloquial Tamil, warm low pitch, gentle authority, friendly chuckle.` |
| **Settings** | Stability 55% · Style 30% · Speed 0.9 |
| **Test line** | `டேய் கண்ணா, அம்மா சொல்றதைக் கேளு.` |

### கதைசொல்லி (Narrator): young woman, ~28. **Chosen: `female_cinematic`**
| | |
|---|---|
| **Sound** | Deep yet youthful, confident and charismatic, with controlled intensity that grips the audience. Crisp Tamil, dramatic pauses, and energy that rises at the big moments. **The series' signature voice** |
| **Voice Design prompt** | `Strong, gripping voice of a confident young Tamil man in his late twenties, native Tamil speaker, deep yet youthful, powerful and charismatic, crisp clear Tamil diction, natural colloquial Tamil, controlled intensity that holds the listener's attention, dramatic pauses, energy rising at key moments, cinematic storyteller.` |
| **Other styles to try** | `young_intense` (husky, suspenseful) · `young_warm` (friendly, talks straight to the viewer) · `young_heroic` (epic, devotional). Use `python3 ../tools/create_elevenlabs_voices.py preview KK_Narrator:all` |
| **Female styles** | `female_sweet` (soft, melodious, smiling) · `female_bright` (cheerful, talks to the viewer) · `female_devotional` (serene, musical) · `female_cinematic` (velvety, emotional). Use `preview KK_Narrator:female` |
| **Settings** | Stability 45% · Style 45% · Speed 1.0 |
| **Test line** | `கோகுலத்துல ஒரு குட்டித் திருடன் இருக்கான்... அவன் திருடுறது தங்கம் இல்ல... வெண்ணெய்!` |

### கம்சன் (Kamsa): man, ~40, villain
| | |
|---|---|
| **Sound** | Very deep, cold, controlled, with **fear** underneath (he's a frightened tyrant, not a cartoon); slow menacing delivery |
| **Voice Design prompt** | `Very deep, cold and menacing voice of a powerful 40-year-old king, native Tamil speaker, formal but natural Tamil, slow controlled delivery, dark and heavy, with hidden fear and paranoia, cinematic villain.` |
| **Settings** | Stability 55% · Style 50% · Speed 0.85 |
| **Post-processing** | CapCut: slight low-end boost + small hall reverb |
| **Test line** | `என்னைக் கொல்லப் போறவன்... எங்கேயோ பிறந்துட்டானா?!` |

## A4. Future characters (create when their episode arrives)

| Character | Age / gender | Voice description |
|---|---|---|
| **வசுதேவர்** (Vasudeva) | Man, ~35 | Gentle, tired but brave; soft low voice full of love and grief |
| **தேவகி** (Devaki) | Woman, ~25 | Soft, fragile, tearful, but with inner strength; higher and lighter than Yashoda |
| **யோகமாயா** (divine baby girl, Ep 2) | Goddess speaking through a baby | Powerful, echoing adult female divine voice. Not a baby voice: it's the goddess speaking. Add reverb |
| **பூதனை** (Putana) | Woman (demoness) | Starts sweet and honeyed (disguise), then turns harsh and distorted when revealed (pitch-down + distortion in the edit) |
| **Gopi girls / Kannan's girl playmates** | Girls, 5–8 | Real girls reading lines + Voice Changer; or Voice Design: `young, bright, cheerful voice of a small Tamil girl, about 6 years old...`. Make each girl's pitch and personality different |
| **ராதை** (Radha) | Girl, ~13–15 | Soft, shy, musical, gentle; not childish, not adult |
| **இளைஞன் கண்ணன்** (teen Krishna) | Boy, ~16 | See A5 |
| **அக்ரூரர்** (Akrura) | Man, ~55 | Devoted, emotional, slightly aged, respectful |
| **சாந்தீபனி முனிவர்** (Sandipani) | Elderly man, ~70 | Deep, slow, wise sage; distinct from the narrator (lower, more formal) |
| **சுதாமா** (Sudama) | Boy ~12 → poor man ~35 | Humble, gentle, slightly nervous |

## A5. When characters grow up
Keep the **personality and rhythm** the same and change only the age:
- Kannan 5 → **teen Kannan, 16:** same playful rhythm and smile in the voice, but a young man's voice. Design prompt: `Voice of a charming 16-year-old Tamil boy, native Tamil speaker, playful and confident, warm smile in the voice, gentle, slightly deeper than a child but youthful.`
- Kannan → **adult Krishna (Gita, Part 5):** calm, deep, compassionate and authoritative, with the faint smile still there.
- Balarama grows in parallel: always **a little lower and firmer** than Kannan at every age.
- Introduce the new voice with a narrator bridge ("வருடங்கள் ஓடின...") so the change feels natural.

## A6. Voice register: fill this in and never lose it
| Character | ElevenLabs voice name | Voice ID | Model | Stability | Similarity | Style | Speed | Source (Design / Real person + Changer) | Consent on file |
|---|---|---|---|---|---|---|---|---|---|
| Kannan | KK_Kannan_child | | | | | | | | |
| Balarama | KK_Balarama_child | | | | | | | | |
| Shridama | KK_Shridama | | | | | | | | |
| Subala | KK_Subala | | | | | | | | |
| Yashoda | KK_Yashoda | | | | | | | | |
| Gomathi | KK_Gomathi | | | | | | | | |
| Kamala | KK_Kamala | | | | | | | | |
| Paati | KK_Paati | | | | | | | | |
| Nandagopar | KK_Nanda | | | | | | | | |
| Narrator | KK_Narrator | | | | | | | | |
| Kamsa | KK_Kamsa | | | | | | | | |

## A7. Generating lines so they sound like acting, not reading
1. **Model:** try **Eleven v3** first; it supports emotion tags like `[whispering]`, `[laughing]`, `[sighs]`, `[angry]`. If its Tamil pronunciation is worse for a line, use **Multilingual v2** for that line.
2. **One line per generation**, 3 takes each; pick the best.
3. **Add emotion tags and punctuation:** `[whispering] ஷ்ஷ்... யார்கிட்டயும் சொல்லாதீங்க! [giggles]`. Use `...` for pauses and `!` for energy.
4. **Generate conversations in order** and listen to them back to back. Each reply should react to the previous line (an angry question → a nervous answer).
5. **Breaths and reactions:** add small sounds between lines: gasps, giggles, "ம்ம்", "ஹா!". These make it feel alive.
6. **Pronunciation fixes:** if a word comes out wrong, respell it the way it's spoken, or split it (`வெண்-ணெய்`).
7. **Always ask a Tamil speaker** to listen to the complete scene before you lip-sync.

---

# Part B: Making the whole episode flow like a movie

## B1. Work in this order (the professional secret: the animatic)
Most AI videos feel like a slideshow because the clips are made first and the sound is stuck on later. Films do it the other way round.

```
1. Script locked
2. Record / generate ALL voices for the scene
3. ANIMATIC: in CapCut, place each still first frame on the timeline with the voices,
   and set each shot's length to fit the dialogue + reactions. Watch it. Fix pacing NOW.
4. Generate video clips to the exact lengths the animatic needs
5. Lip-sync to the same voice files
6. Replace stills with clips, add music + SFX, grade, subtitle
```
The animatic costs nothing and decides the rhythm of the film. **Never skip it.**

## B2. Picture continuity
| Rule | What it means | In Episode 1 |
|---|---|---|
| **Establish → closer → closest** | Start each scene wide (where are we?), then medium (who's here?), then close-ups (what do they feel?) | Every scene opens on its location (courtyard, banyan tree, riverbank) before the faces |
| **Screen direction (180° rule)** | If Yashoda is on the left facing right, she stays on the left in every shot of that conversation | Shots 8–9: Yashoda left, Kannan right, all the way through |
| **Eyelines match** | If Kannan looks up at Yashoda, the next shot of Yashoda looks down at him | 8a low angle on Yashoda ↔ 8b high angle on Kannan |
| **Physical continuity** | Things that happen stay happened | Butter stays on Kannan's face from the theft until Yashoda wipes it; the pot stays broken; mud on his lip in Scene 9 |
| **Lighting continuity** | The same time of day keeps the same light across a scene | Scene 7 is dusk in every shot; Scene 10 is moonlight and lamp |
| **Every shot moves** | Subject motion **and** gentle camera motion in every shot; no frozen images | Motion prompts all include a camera move |
| **Vary shot sizes** | Never cut wide → wide or close → close of the same person | — |
| **Cut on action** | Cut in the middle of a movement, not after it stops; it hides the join | Tower collapse, the door bursting open |
| **Reaction shots** | Show the listener reacting; that's where emotion lives | Subala's terror, the gopis gasping, Yashoda's tear |
| **Hold emotional moments** | Let important shots breathe 1–2 seconds longer | The universe reveal; the lullaby |

## B3. Sound continuity (the biggest difference between "AI clips" and "movie")
1. **A continuous ambience bed under every scene.** One long track of courtyard sound (birds, cows, distant voices) runs under *all* the shots of Scene 1, across the cuts. Without it, every cut feels like a new clip.
2. **J-cuts and L-cuts.** Let the sound of the next scene start ~0.5–1 s *before* the picture changes (J-cut), or let a line carry over into the next shot (L-cut). Example: Yashoda's "கண்ணா...!" is heard over the frozen boys before we see her.
3. **Dialogue perspective.**
   - Close-ups: dry and close.
   - Wide or distant: lower volume plus a slight room or outdoor echo. Balarama shouting across the riverbank should sound far away.
   - Indoors: small-room reverb (light). Storeroom: dark, slightly boomy. Outdoors: no reverb, more ambience.
4. **Character sound signatures (foley).** Kannan = gold anklet bells; Yashoda = bangles + silver kolusu; Shridama = his wooden cowbell; Paati = churning stick tapping. Add them every time the character moves, and they become part of their identity.
5. **Overlaps.** Real people interrupt and laugh over each other. Overlap reactions and laughter slightly (the gopis' complaints, the boys shouting in Scene 7).
6. **Music themes (leitmotifs).** Generate once, reuse all series long:
   - **Kannan's theme:** playful bansuri flute
   - **Yashoda's theme:** veena and soft strings
   - **Divine theme:** choir hum, bells and strings
   - **Kamsa's theme:** low drums and dark brass
   - **Series motif:** the 4-note flute
7. **Silence is a tool.** Cut all music before big moments (the kolusu beat, "வாயைத் திற", the reveal).
8. **Mix:** dialogue always on top, music ducked under speech, final loudness about −14 LUFS.

## B4. Transitions
| Use | Transition |
|---|---|
| Most cuts | **Hard cut** (invisible) |
| Time passing (morning → afternoon) | Slow **dissolve** over a wide shot, or a sky time-lapse |
| Comedy energy | **Whip pan** |
| Shock / mood change | **Smash cut** (the storm in Scene 10) |
| Entering the vision | **Light flare to white** |
| Never | Flashy CapCut template transitions, spinning cubes, glitch effects |

## B5. Look
- **One colour grade** for the whole episode (a warm cinematic LUT), with scene-specific tweaks only (cool for Mathura, glow for divine).
- **24 fps** for the long episode, with **subtle film grain** on everything so clips from different generations blend.
- **Consistent subtitles** (font, size, position, colours per the bible).

## B6. Movie test before publishing
1. **Picture-only test:** watch with the sound off. Can you still follow the story?
2. **Sound-only test:** close your eyes. Can you tell who's speaking and where they are?
3. **Seam test:** do you ever notice a "new clip starting"? If yes, check ambience continuity, cut-on-action and colour match at that cut.
4. **Family test:** show it to someone who hasn't read the script. Note where they laugh, where they get bored and where they're moved.
