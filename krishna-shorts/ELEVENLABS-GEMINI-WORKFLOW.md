# Gemini + ElevenLabs Workflow (recommended)

**Gemini / Google** for pictures, video and music, and **ElevenLabs** for every voice. This gives you the best of both: Veo's natural movement and lip-sync, with ElevenLabs' consistent, emotional Tamil voices that sound the same in every episode.

**Files you'll use:**
- Voices: **[episodes/ep01-voice-lines-elevenlabs.md](episodes/ep01-voice-lines-elevenlabs.md)**: every line of Episode 1 (Short + full) with the voice, emotion tag and file name.
- Pictures and video: **[GEMINI-ONLY-PROMPT-PACK.md](GEMINI-ONLY-PROMPT-PACK.md)**: first-frame and video prompts for every shot.
- Voice descriptions: **[04-voices-and-cinematic-flow.md](04-voices-and-cinematic-flow.md#a3-character-voice-sheets-part-1-cast)**.
- Music: **[05-music-bgm-plan.md](05-music-bgm-plan.md)**.

> ElevenLabs and Google change their menus often. If a button has a different name on your screen, look for the closest match.

---

## 1. Who does what

| Job | Tool |
|---|---|
| Character and background pictures, shot first frames | Gemini app (Nano Banana) |
| Video clips (movement, acting, lip movement) | Veo in **Flow** |
| **All character voices + the narrator** | **ElevenLabs**: Voice Design, Text to Speech, Voice Changer |
| Sound effects and ambience | **ElevenLabs Sound Effects** (or Veo's own sound) |
| Music, title song, lullaby | Gemini app music tool (Lyria) |
| Final edit | YouTube Create (Google, Android) or CapCut (free); you need an editor that can mute a clip's sound and add your own audio tracks |

---

## 2. The key idea: how the ElevenLabs voice and the Veo mouth stay in sync

Veo makes the mouths move, and ElevenLabs makes the voices. Use **one of three methods** for each shot:

### Method A: "Veo acts, ElevenLabs re-voices" ⭐ best for close-ups
1. Make the Veo clip **with the Tamil line inside the prompt** (the video prompts in the Gemini-only pack already include it). Veo speaks the line with matching mouth movement.
2. Take Veo's audio from that clip, and in **ElevenLabs Voice Changer** turn it into the character's saved ElevenLabs voice.
3. Put the new audio back on the clip in place of the original.

**Result:** perfect lip-sync (the timing comes from Veo's own speech) **and** a consistent ElevenLabs voice.
**Needs:** Veo must have said the Tamil words correctly, because Voice Changer keeps the words and changes only the voice.

### Method B: "ElevenLabs speaks, Veo acts to it" (when Veo's Tamil words come out wrong)
1. Generate the line in ElevenLabs **Text to Speech** first and note how long it is.
2. Make the Veo clip with the same Tamil line in the prompt and a duration at least that long, so the mouth moves for roughly the same number of syllables.
3. In the editor, mute Veo's sound, place the ElevenLabs line, and slide it until the first word matches the first mouth opening.

**Result:** close sync. Very good in medium and wide shots, but sometimes visibly off in tight close-ups. If so, regenerate the clip or use Method A.

### Method C: "No visible mouth" (off-screen lines, backs to camera, wide shots, narrator)
1. Generate the line in ElevenLabs.
2. Make the Veo clip with any motion. The speech in it doesn't matter, because you'll mute it.
3. Place the ElevenLabs line over it. No syncing needed.

### Which method for which shot
- **Short #1:**
  - Method A (fallback B): Shots **1, 3, 8a, 8b, 9, 11b**, the speaking close-ups.
  - Method C: Shots **2, 4, 5, 6, 10, 11a, 12**.
- **Full episode:**
  - Method A (fallback B): every shot marked **LS** in the [shot list](episodes/ep01-long-kokulathin-kutti-thirudan.md).
  - Method C: everything else, including all narrator lines.

---

## 3. Step by step

### Step 1: Check your ElevenLabs plan (5 min)
- To publish on YouTube or Instagram you need a **paid plan** (Starter or above) for commercial rights. Check under **Subscription**.
- Note your monthly **credits**. A 60-second Short needs only a small part of a Starter plan. The full episode with retakes and Voice Changer is more comfortable on **Creator**.

### Step 2: Create the character voices (1–2 hours, once for the whole series)
For each character in [04 §A3](04-voices-and-cinematic-flow.md#a3-character-voice-sheets-part-1-cast):

1. ElevenLabs → **Voices** → **Create / Add a new voice** → **Voice Design**.
2. Paste the character's **Voice Design prompt** (English description).
3. In the preview text, paste the character's **Tamil test line**.
4. Generate. Listen to the 3 options. If none fit, adjust the description (e.g. "younger", "softer", "more nasal") and generate again.
5. **Save** the best one with the exact name: `KK_Kannan`, `KK_Yashoda`, `KK_Balarama`, `KK_Shridama`, `KK_Subala`, `KK_Gomathi`, `KK_Kamala`, `KK_Paati`, `KK_Kamsa`, `KK_Narrator`.
6. Write the voice ID and settings in the [voice register](04-voices-and-cinematic-flow.md#a6-voice-register-fill-this-in-and-never-lose-it).

**Check the voices side by side:**
- The four boys must sound clearly different from each other.
- The women must too: Kamala youngest, Yashoda warmest, Gomathi loudest, Paati oldest.

**Children's voices:** if Voice Design makes the boys sound like adults doing a child voice, use the real-child method from [04 §A2](04-voices-and-cinematic-flow.md#a2-the-best-way-to-get-each-type-of-voice-honest-assessment):
- A child performs the line (with parental consent), and you run it through **Voice Changer** into `KK_Kannan`.
- Or **clone** a consenting child or voice artist's "kid voice" with **Instant Voice Cloning**, and save it as `KK_Kannan`.

### Step 3: Test before producing (30 min)
1. **Text to Speech** → voice `KK_Yashoda` → model **Eleven v3** → paste line 11 from the voice-lines file:
   `[stern but with an amused crack in her voice] கண்ணா, திரும்பவும் வெண்ணெய் திருடித் தின்னியா?`
2. Then `KK_Kannan`, line 12: `[exaggerated innocence] அம்மா, நான் ஒண்ணுமே பண்ணலையே!`
3. **Have a Tamil speaker listen.** If v3 mispronounces words, try **Multilingual v2** for that line (delete the [tag]), or respell the tricky word the way it sounds.
4. In Flow, make Short Shot 8b with the Gemini-only video prompt, then try **Method A** on it (Step 5). If it works, your pipeline is proven.

### Step 4: Generate all the voice lines
Open **[ep01-voice-lines-elevenlabs.md](episodes/ep01-voice-lines-elevenlabs.md)**. For each row:
1. **Text to Speech** → choose the **Voice** in that row → paste **Text to paste** → Generate.
2. Make **3 takes** and keep the most natural one.
3. Download and rename it to the **File** name in the row.

**Faster for whole scenes:** use **ElevenLabs Studio** (projects). Paste a scene's lines, assign each line's voice, generate everything, then export each line separately. Listening to the scene in one go also tells you whether the conversation flows.

**Tips that make it sound like acting:**
- Generate a conversation **in order** and listen back to back. Each reply should react to the line before it.
- Add small reactions where natural: `[laughs]`, `[gasps]`, `[sighs]`, "ம்ம்".
- Don't publish a line a Tamil speaker hasn't approved.

### Step 5: Make the clips and put the voices on them

**Pictures:** the Gemini app. Attach the refs and use the **① First frame** prompts from [GEMINI-ONLY-PROMPT-PACK.md](GEMINI-ONLY-PROMPT-PACK.md).
**Video:** Flow → **Frames to Video**, using the **② Video prompts** from the same pack. They include the Tamil line, so the mouths move to the words.

**Method A, click by click:**
1. In your editor, select the Veo clip → **Extract audio** (CapCut and most editors have this). Export that audio as a file. ElevenLabs Voice Changer may also accept the video file directly.
2. ElevenLabs → **Voice Isolator**: upload it to remove Veo's background sound and music, leaving only the speech. *(Optional, but gives a cleaner result.)*
3. ElevenLabs → **Voice Changer** → choose the character's voice (`KK_Kannan`...) → upload the isolated speech → turn on **Remove background noise** if offered → Generate → download.
4. In the editor, **mute** the Veo clip's sound, and place the Voice Changer audio exactly at the start of the clip. It lines up automatically because the timing is the same.
5. If two characters speak in one clip (e.g. Short Shot 9), run Voice Changer **once per character**, using only that character's part of the audio.

**Method B and C:** use the files from Step 4, as described in §2.

### Step 6: Narrator
Use `KK_Narrator` in ElevenLabs Text to Speech for all narrator lines (in the voice-lines file). Keep the **same voice and settings for the whole series**. The narrator is the show's signature voice.

### Step 7: Sound effects and ambience (ElevenLabs Sound Effects)
- **One ambience bed per scene,** 20–30 seconds, looped under the whole scene. For example: `Ancient Indian village morning ambience, birds chirping, distant cow bells, soft wind, peaceful` · `Quiet dark storeroom ambience, faint dripping, creaking wood` · `River bank ambience, flowing water, birds, distant children` · `Night village ambience, crickets, soft wind` · `Thunderstorm with heavy rain and lightning cracks`.
- **Character signature sounds:** `Small gold anklet bells jingling, child tiptoeing` (Kannan) · `Silver anklets jingling, slow footsteps` (Yashoda) · `Glass bangles clinking` · `Wooden cowbell clonking`.
- **Action SFX** from the episode's SFX lists: the pot crash, butter splat, monkey chatter, door bursting open, cosmic whoosh and so on.

### Step 8: Music
Gemini app → music tool, using the prompts and cue sheet in [05-music-bgm-plan.md](05-music-bgm-plan.md). Every Veo prompt says "No background music", so all music comes from these tracks and flows across the cuts.

### Step 9: Edit (layer by layer)
1. **Video:** clips in shot order, trimmed and cut on action. **Mute every clip's own sound.**
2. **Dialogue:** the ElevenLabs/Voice Changer lines (loudest, peaks about −6 dB).
3. **Ambience beds** under each scene (continuous across cuts).
4. **SFX and signature sounds** on the actions.
5. **Music** per the cue sheet, ducked under dialogue.
6. **Subtitles** (import `ep01-subtitles.srt` for the Short; type them for the long episode) styled per the bible.
7. Title and end cards → export 1080p (9:16 Short / 16:9 episode), about −14 LUFS.

*Tip:* for some shots Veo's own sound effects (footsteps, the pot breaking) are very good. In those cases keep just that part of the Veo audio, at low volume.

---

## 4. Your next 10 days

| Day | Do | Tool |
|---|---|---|
| 1 | Check plan; create `KK_Yashoda`, `KK_Kannan`, `KK_Narrator` | ElevenLabs |
| 1 | Test lines 11 and 12 with a Tamil listener | ElevenLabs |
| 2 | Create the other voices; fill in the voice register | ElevenLabs |
| 2–3 | Kannan's 4 reference pictures, then the other characters | Gemini app |
| 3 | **Pipeline test:** Short Shot 8b with Method A | Gemini + Flow + ElevenLabs |
| 4 | All 18 Short voice lines | ElevenLabs |
| 4–6 | All Short frames and clips; Method A/B/C per shot | Gemini + Flow + ElevenLabs |
| 7 | Ambience, SFX, music | ElevenLabs + Gemini |
| 8 | Edit and export | YouTube Create / CapCut |
| 9 | QC and publish | YouTube |
| 10 | Plan the full episode scene by scene | — |

**After the Shot 8b test, tell me how Method A sounded.** If Veo's Tamil words were off, I'll mark which shots should switch to Method B.
