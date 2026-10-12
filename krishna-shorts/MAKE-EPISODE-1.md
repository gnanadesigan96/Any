# How to Make Episode 1: the complete step-by-step guide

**Tools:** Gemini app (pictures, music) · Google Flow (video) · ElevenLabs (voices, sound effects) · CapCut desktop or YouTube Create (final edit).

**What you'll make first:** **Short #1: வெண்ணெய் திருடன்** (60 s, vertical). It's Episode 1's first release, and it teaches you the whole process with little risk. The full 11-minute Episode 1 then uses exactly the same steps, scene by scene (Phase 8).

**Time:** about 8–10 sessions of 1–2 hours. **Tick each box as you go.**

> Menus in Gemini, Flow, ElevenLabs and CapCut change often. If a button name is different on your screen, pick the closest one.

---

## PHASE 0: Set up (1 hour)

### 0.1 Make your project folder
On your computer (or Google Drive), create:
```
Kannan Kathaigal/
  refs/          ← character and background pictures
  EP01-short/
    frames/      ← first frame of each shot (PNG)
    clips/       ← Veo video clips (MP4)
    voice/       ← ElevenLabs voice lines (WAV/MP3)
    sfx/         ← sound effects and ambience
    music/       ← music tracks
    export/      ← final video
```
- [ ] Folder created

### 0.2 Open the files you'll copy from
Go to **https://github.com/gnanadesigan96/Any/tree/claude/modest-turing-kfxpi6/krishna-shorts** and keep these tabs open:
1. **[GEMINI-PROMPT-PACK.md](GEMINI-PROMPT-PACK.md):** character and background picture prompts (Parts 1–2)
2. **[GEMINI-ONLY-PROMPT-PACK.md](GEMINI-ONLY-PROMPT-PACK.md):** shot prompts (Part A = the Short)
3. **[episodes/ep01-voice-lines-elevenlabs.md](episodes/ep01-voice-lines-elevenlabs.md):** all the voice lines
4. **[04-voices-and-cinematic-flow.md](04-voices-and-cinematic-flow.md):** voice descriptions
5. **[05-music-bgm-plan.md](05-music-bgm-plan.md):** music prompts
6. **[episodes/ep01-subtitles.srt](episodes/ep01-subtitles.srt):** download this file into `EP01-short/`

- [ ] Tabs open, SRT downloaded

### 0.3 Check your accounts
- [ ] **Gemini:** signed in with your Gemini Pro account at gemini.google.com
- [ ] **Flow:** open **labs.google/flow** with the same account; note your **credits** (top-right or profile menu). The Short needs about 30–40 Fast generations.
- [ ] **ElevenLabs:** a **paid plan** (Starter or above) for commercial use; note your credits
- [ ] **Editor:** install **CapCut desktop** (free), or **YouTube Create** on Android

---

## PHASE 1: Create the voices (ElevenLabs, 2 hours, done once for the whole series)

You need these voices for the Short: **Kannan, Yashoda, Subala, Shridama, Balarama, Narrator.**

### 1.1 Design each voice
> **Shortcut:** [tools/create_elevenlabs_voices.py](tools/README.md) creates all 11 voices automatically. You just listen to 3 previews per character and pick one. If you use it, skip to 1.2.

For each character, in this order: Yashoda → Narrator → Kannan → Subala → Shridama → Balarama.

1. ElevenLabs → **Voices** → **+ Create a voice / Add voice** → **Voice Design**.
2. Open [04 §A3](04-voices-and-cinematic-flow.md#a3-character-voice-sheets-part-1-cast) and copy that character's **Voice Design prompt** into the description box.
3. Paste the character's **Tamil test line** into the preview text box.
4. Click **Generate** and listen to the options.
5. Not right? Edit the description (e.g. add "younger", "softer", "more playful") and generate again.
6. Click **Save / Add voice** and name it exactly: `KK_Yashoda`, `KK_Narrator`, `KK_Kannan`, `KK_Subala`, `KK_Shridama`, `KK_Balarama`.

- [ ] KK_Yashoda · [ ] KK_Narrator · [ ] KK_Kannan · [ ] KK_Subala · [ ] KK_Shridama · [ ] KK_Balarama

### 1.2 Compare them
Play the four boys one after another. **Kannan** = brightest and sweetest · **Subala** = thinnest and most nervous · **Shridama** = roundest and loudest · **Balarama** = lowest and firmest. If two sound alike, redesign one.

**If the boys sound like adults doing a child voice:** have a child read the lines on a phone in a quiet room (with a parent's permission), then turn each recording into the character's voice with **Voice Changer** (see 3.3). This gives the most natural result.

- [ ] Voices sound distinct · [ ] Voice IDs written in the [voice register](04-voices-and-cinematic-flow.md#a6-voice-register-fill-this-in-and-never-lose-it)

### 1.3 Test with a Tamil listener (15 min)
1. ElevenLabs → **Text to Speech** → voice **KK_Yashoda** → model **Eleven v3**.
2. Paste: `[stern but with an amused crack in her voice] கண்ணா, திரும்பவும் வெண்ணெய் திருடித் தின்னியா?` → Generate.
3. Switch the voice to **KK_Kannan** and paste: `[exaggerated innocence] அம்மா, நான் ஒண்ணுமே பண்ணலையே!` → Generate.
4. Have a Tamil speaker listen. If a word sounds wrong, try model **Multilingual v2** (remove the [tag]) or respell the word the way it's said.

- [ ] Tamil approved by a listener

---

## PHASE 2: Create the reference pictures (Gemini app, 3–4 hours)

### 2.1 Characters: one chat per character
For **Kannan first**, then Yashoda, Shridama, Subala, Balarama, using [GEMINI-PROMPT-PACK.md Part 1](GEMINI-PROMPT-PACK.md#part-1-character-reference-images-gemini-app-one-chat-per-character):

1. gemini.google.com → **New chat** → **Tools → Create images** (or start with "Generate an image:").
2. Paste **Prompt 1 (full body)** → send.
3. **Check Kannan's must-haves:** deep blue-black skin (not teal or purple) · kohl eyes · black dot on the **left** cheek · peacock feather in the topknot · yellow silk dhoti · flute at the waist · gold anklets.
4. Fix by replying (e.g. *"Same image, but deeper blue-black skin and add the black dot on his left cheek"*) or click **Regenerate**.
5. When it's right: open the image → **Download** → save as `refs/krishna_child_full.png`.
6. In the **same chat**: paste **Prompt 2** → save `krishna_child_turnaround.png`; **Prompt 3** → `krishna_child_expressions.png`; **Prompt 4** → `krishna_child_front.png`.
7. If the face changes in Prompts 2–4: new chat → **+ Upload** your `_full.png` → write *"Use this exact character"* → paste the prompt.

- [ ] Kannan ×4 · [ ] Yashoda ×4 · [ ] Shridama ×4 · [ ] Subala ×4 · [ ] Balarama ×4

### 2.2 Background
[GEMINI-PROMPT-PACK.md Part 2](GEMINI-PROMPT-PACK.md#part-2-background-reference-images-gemini-app-or-flow) → **Main room with the rope sling** → save as `refs/bg_mainroom.png`.
- [ ] bg_mainroom

**📸 Optional check:** upload Kannan's 4 pictures here and I'll compare them with his description before you continue.

---

## PHASE 3: Generate all voice lines (ElevenLabs, 1 hour)

### 3.1 Generate
Open [ep01-voice-lines-elevenlabs.md → Short #1](episodes/ep01-voice-lines-elevenlabs.md#short-1-வெண்ணெய்-திருடன்). For each of the 18 rows:
1. **Text to Speech** → choose the row's **Voice** → model **Eleven v3** → paste **Text to paste** → Generate.
2. Make **3 takes** and keep the best.
3. **Download** and rename it to the row's **File** name (e.g. `EP01S_S08_L2_kannan.wav`) in `EP01-short/voice/`.

**Faster option:** ElevenLabs **Studio** → new project → paste the lines in order → assign each line's voice → generate all → export the lines.

### 3.2 Listen to the whole conversation in order
Play lines 3–5, then 9–10, 11–15 and 16–17 back to back. Each reply should react to the line before it. Redo any line that sounds flat or reads like it's being read aloud.

- [ ] 18 lines saved and named · [ ] Tamil listener approved them

### 3.3 (If needed) Voice Changer for a real child's recording
**Voice Changer** → choose `KK_Kannan` → upload the child's recording → turn on **Remove background noise** → Generate → save with the same file name.

---

## PHASE 4: Quick animatic (CapCut, 30 min, the step that makes it feel like a film)

Before spending video credits, check the timing.

1. CapCut → **New project** → set the ratio to **9:16**.
2. You don't have the shot frames yet, so drop in simple placeholders: your reference pictures, or text cards reading "Shot 1", "Shot 2"...
3. Place the voice lines on the audio track at the times in the **Shot cards** below.
4. Play it. Does each line have room to breathe? Is anything rushed? Note any shot that needs to be longer.

- [ ] Animatic watched; timing notes made

---

## PHASE 5: Make the 12 shots (Gemini + Flow, 5–7 hours over several sessions)

### 5.1 Set up Flow once
1. **labs.google/flow** → **New project** → name it `EP01 Short`.
2. **Settings (⚙):** Aspect ratio **9:16 (portrait)** · Model **Veo 3.1 Fast** · Outputs per prompt **1**.

### 5.2 For every shot (the routine)
1. **First frame (Gemini app):** new chat → **+ Upload** the refs listed on the card → type *"Use these reference images for the characters' exact appearance and the room."* → paste the **① First frame** prompt from [GEMINI-ONLY-PROMPT-PACK.md Part A](GEMINI-ONLY-PROMPT-PACK.md#part-a-short-1-வெண்ணெய்-திருடன்-916) → check the face, hands, costume, vertical format and that there's no text → download → `frames/EP01_S03_v1.png`.
2. **Video (Flow):** mode **Frames to Video** → upload the frame as the **start frame** → paste the **② Video prompt** for that shot → **Generate** (1–3 min).
3. **Check:** Does the face stay the same throughout? Are the hands OK? Does the motion look natural? Does the mouth move when someone speaks?
4. Good → **Download** (1080p if offered) → `clips/EP01_S03_v1.mp4`. Bad → simplify the motion or regenerate (most shots need 1–2 tries).
5. **Voice:** apply the card's **voice method** (A, B or C; see 5.3).

### 5.3 The three voice methods
- **A: Veo acts, ElevenLabs re-voices** (exact lip-sync):
  1. In CapCut, put the clip on the timeline → right-click → **Extract audio** → export that audio.
  2. ElevenLabs → **Voice Isolator** → upload the audio → download the clean speech.
  3. ElevenLabs → **Voice Changer** → choose the character's voice → upload the clean speech → Generate → download as `voice/EP01S_S08_L1_yashoda_VC.wav`.
  4. Use this file instead of the Phase 3 file. Mute the clip and place it at the clip's start. It's already in sync.
  5. **If two characters speak in the clip:** cut the clean speech into each person's part first, and convert each part with that person's voice.
  6. **If Veo said the Tamil words wrongly,** Voice Changer will keep the mistake. Use Method B instead.
- **B: ElevenLabs line + alignment:** mute the clip, place the Phase 3 voice file, and slide it until the first word starts as the mouth opens.
- **C: Voice over, no sync needed:** mute the clip and place the Phase 3 file at the time shown.

### 5.4 Shot cards: Short #1

**SHOT 1 · The whisper hook · 0:00–0:03**
- Refs: `krishna_child_front`, `krishna_child_turnaround`
- Prompts: Part A → SHOT 1 (① and ②) · Quality mode if you have credits (hero shot)
- Voice: **Method A** · `EP01S_S01_L1_kannan`
- SFX: distant birds, faint cow bell · Music: **none** (silence makes the whisper land)
- [ ] frame · [ ] clip · [ ] voice

**SHOT 2 · Gokulam sunrise + title · 0:03–0:08**
- Refs: none
- Prompts: Part A → SHOT 2
- Voice: **Method C** · `EP01S_S02_L1_narrator` (starts ~0:03.6)
- SFX: birds, cow bells, river · Music: series flute motif → Kannan's theme begins · Title text at 0:03.5–0:05.5
- [ ] frame · [ ] clip · [ ] voice

**SHOT 3 · The plan · 0:08–0:15**
- Refs: `krishna_child_front`, `shridama_front`, `subala_front` (+ `bg_mainroom`)
- Prompts: Part A → SHOT 3. If 7 s is too long for one clip, make it as 2 clips: a 3 s wide shot, then a 4 s close-up on Kannan.
- Voice: **Method A, two voices** (Kannan + Subala) · `S03_L1_kannan`, `S03_L2_subala`, `S03_L3_kannan`
- SFX: a "ding" when he taps his head · Music: Kannan's theme, low
- [ ] frame · [ ] clip · [ ] voice

**SHOT 4 · The tower · 0:15–0:21**
- Refs: `krishna_child_full`, `shridama_full`, `subala_full` (+ `bg_mainroom`)
- Prompts: Part A → SHOT 4
- Voice: **Method B** (faces strained or turned away) · `S04_L1_shridama`, `S04_L2_kannan`
- SFX: wood creak, grunts, anklet bells · Music: Kannan's theme, building
- [ ] frame · [ ] clip · [ ] voice

**SHOT 5 · Butter for everyone · 0:21–0:26**
- Refs: `krishna_child_full`, `shridama_full`, `subala_full`
- Prompts: Part A → SHOT 5
- Voice: **Method B** · `S05_L1_kannan` + children's laughter (from the Veo clip or ElevenLabs SFX)
- SFX: butter splats, monkey chatter · Music: Kannan's theme, full, then **stops dead** at 0:26
- [ ] frame · [ ] clip · [ ] voice

**SHOT 6a · Anklets at the door · 0:26–0:28**
- Refs: `yashoda_full`
- Prompts: Part A → SHOT 6 → 6a
- Voice: none
- SFX: **loud silver anklet jingle** + a low drum "dum" · Music: none
- [ ] frame · [ ] clip

**SHOT 6b · The boys freeze · 0:28–0:30**
- Refs: `krishna_child_full`, `shridama_full`, `subala_full`
- Prompts: Part A → SHOT 6 → 6b
- Voice: **Method B** `S06_L1_subala` (whisper) + **Method C** `S06_L2_yashoda` (off-screen "கண்ணா...!")
- [ ] frame · [ ] clip · [ ] voice

**SHOT 7 · The collapse · 0:30–0:34**
- Refs: `krishna_child_full`, `shridama_full`, `subala_full`
- Prompts: Part A → SHOT 7
- Voice: none · SFX: clay pot crash, whooshes, a bump (Veo's own crash sound may be good; keep it if so)
- [ ] frame · [ ] clip

**SHOT 8a · Yashoda in the doorway · 0:34–0:37** ⭐
- Refs: `yashoda_front`, `yashoda_full`
- Prompts: Part A → SHOT 8 → 8a · Quality mode if possible
- Voice: **Method A** · `S08_L1_yashoda`
- Music: light comic plucked strings, low
- [ ] frame · [ ] clip · [ ] voice

**SHOT 8b · Innocent butter face · 0:37–0:41** ⭐ (this is also your cover image)
- Refs: `krishna_child_front`, `krishna_child_expressions`
- Prompts: Part A → SHOT 8 → 8b · Quality mode if possible
- Voice: **Method A** · `S08_L2_kannan`
- [ ] frame · [ ] clip · [ ] voice

**SHOT 9 · The monkey excuse · 0:41–0:47**
- Refs: `yashoda_front`, `krishna_child_front` (+ `bg_mainroom`)
- Prompts: Part A → SHOT 9
- Voice: **Method A, two voices** · `S09_L1_yashoda`, `S09_L2_kannan`
- SFX: monkey chatter on "குரங்கு" · Music: comic strings, with a hit on "குரங்கு மாமா"
- [ ] frame · [ ] clip · [ ] voice

**SHOT 10 · The hug · 0:47–0:51**
- Refs: `yashoda_front`, `krishna_child_front`
- Prompts: Part A → SHOT 10
- Voice: **Method B** · `S10_L1_yashoda`
- SFX: bangles, cloth rustle · Music: **Yashoda's theme** swells
- [ ] frame · [ ] clip · [ ] voice

**SHOT 11a · Balarama runs in · 0:51–0:53**
- Refs: `balarama_full`
- Prompts: Part A → SHOT 11 → 11a
- Voice: **Method B or C** · `S11_L1_balarama`
- SFX: running feet · Music: drops to the low mystery drone
- [ ] frame · [ ] clip · [ ] voice

**SHOT 11b · "வாயைத் திற!" · 0:53–0:57**
- Refs: `yashoda_front`, `krishna_child_front`
- Prompts: Part A → SHOT 11 → 11b
- Voice: **Method A** · `S11_L2_yashoda`
- [ ] frame · [ ] clip · [ ] voice

**SHOT 12a · The mouth opens · 0:57–1:00** ⭐
- Refs: `krishna_child_front`
- Prompts: Part A → SHOT 12 → 12a · Quality mode if possible
- Voice: **Method C** · `S12_L1_narrator`
- SFX: low "om", bell shimmer · Music: **divine swell**
- [ ] frame · [ ] clip · [ ] voice

**SHOT 12b · Yashoda's awe · 1:00–1:02**
- Refs: `yashoda_front`
- Prompts: Part A → SHOT 12 → 12b
- Voice: none · Music: swell → **cut to silence** on black
- [ ] frame · [ ] clip

**END CARD · 1:02–1:05:** made in the editor (see 7.6).

---

## PHASE 6: Sound effects, ambience and music (2 hours)

### 6.1 Ambience beds (ElevenLabs → Sound Effects)
Generate each at about 20–30 s and save to `sfx/`:
- `amb_room.wav`: *"Inside an ancient Indian village house, quiet morning room tone, birds outside the window, distant cow bells"*
- `amb_village.wav`: *"Indian village at sunrise, birds chirping, cow bells, distant river, peaceful"*

### 6.2 Sound effects (ElevenLabs → Sound Effects)
Save each to `sfx/`:
- *"Small gold anklet bells jingling as a child climbs"*
- *"Silver anklets jingling, three slow footsteps on a wooden threshold"*
- *"Single deep dramatic drum hit"*
- *"Clay pot falling and shattering on a mud floor"*
- *"Soft splat of butter"*
- *"Langur monkey chattering"*
- *"Group of small children laughing"*
- *"Glass bangles clinking"*
- *"Child running footsteps on a mud floor"*
- *"Low humming om with shimmering temple bells, divine"*
- *"Quick magical ding"*

### 6.3 Music (Gemini app → music tool)
Use the prompts in [05-music-bgm-plan.md §2](05-music-bgm-plan.md#2-the-theme-library-create-these-once-and-reuse-them-all-series). For the Short you need:
- [ ] **T1 title theme** (vocal, with the lyrics). Use its flute intro and the "கண்ணா... கண்ணா..." chorus.
- [ ] **T2 Kannan's theme** (instrumental)
- [ ] **T3 Yashoda's theme** (instrumental)
- [ ] **T8 divine theme** (instrumental)
- [ ] **T9 mystery motif** (instrumental)

Generate each 3–4 times, keep the catchiest, and save to `music/`.

---

## PHASE 7: Edit the Short (CapCut desktop, 2–3 hours)

### 7.1 Project
**New project** → ratio **9:16** → resolution **1080×1920**, **30 fps**.

### 7.2 Video track
1. Drag the clips in order: 1, 2, 3, 4, 5, 6a, 6b, 7, 8a, 8b, 9, 10, 11a, 11b, 12a, 12b.
2. Trim each one to the times on its shot card. Cut **in the middle of a movement**, not after it stops.
3. Select all clips → **mute** them (or set volume to 0). You'll keep Veo's sound only where you decided to (e.g. the pot crash).

### 7.3 Dialogue track
Place every voice file at its shot. For Method A files, align them to the clip's start. For B, slide until the mouth matches. For C, place at the card's time. Set dialogue volume so its peaks sit around **−6 dB**.

### 7.4 Ambience and effects
1. Lay `amb_village.wav` under Shot 2 and `amb_room.wav` under Shots 3–12, **as one continuous track across the cuts**, at about −24 dB.
2. Place each SFX on its action: the anklets on 6a, the drum on the freeze, the crash on 7, the monkey on 9, and so on.

### 7.5 Music
Follow the [Short cue sheet](05-music-bgm-plan.md#4-short-1-வெண்ணெய்-திருடன்-60-s-cue-sheet):
1. 0:03 title motif.
2. 0:05–0:26 Kannan's theme, building.
3. **Hard stop at 0:26.**
4. 0:34–0:47 light comic plucked strings (a soft part of Kannan's theme works too).
5. 0:47 Yashoda's theme.
6. 0:51 mystery drone.
7. 0:57 divine swell.
8. Silence at the black frame, then the motif under the end card.

Lower the music to about **−24 dB whenever someone speaks**. Use keyframes, or CapCut's **auto-ducking** if available.

### 7.6 Titles, subtitles, end card
1. **Title (0:03.5–0:05.5):** text `கண்ணன் கதைகள் #01` / `வெண்ணெய் திருடன்` in a gold Tamil font (e.g. Mukta Malar ExtraBold), with a quick fade.
2. **Subtitles:** **Text → Import captions / Local captions** → choose `ep01-subtitles.srt`.
   - Style: white, bold, black outline, about 62–68% down the screen.
   - Colour Kannan's lines **gold (#FFD966)** and put the narrator in *italic*.
   - Adjust each cue to match the actual voice timing.
3. **End card (1:02–1:05):** black background + `அடுத்த எபிசோட்: வாய்க்குள் ஒரு பிரபஞ்சம்` + `Follow பண்ணுங்க 🙏`, with the flute motif.

### 7.7 Finish
1. **Colour:** apply one warm filter or LUT to **all clips** at low strength so they match, and add a little film grain.
2. **Export:** 1080p, 30 fps, high bitrate → `export/EP01_short_v1.mp4`.

- [ ] Exported

---

## PHASE 8: Quality check and publish (1 hour)

### 8.1 Watch it four ways (on your phone)
1. Normal, with sound
2. **Sound off:** does the story still make sense?
3. **Eyes closed:** can you tell who's speaking?
4. Show it to a family member who hasn't read the script

Then run the [QC checklist](03-qc-and-costs.md#1-quality-control-checklist-run-on-every-short-and-every-long-episode) and fix anything that fails.

### 8.2 Publish
1. **YouTube** → Create → Upload → the MP4. Because it's vertical and 60 s or under, it becomes a Short.
2. Title, description and hashtags from [the Short's publishing kit](episodes/ep01-vennai-thirudan.md#f-publishing-kit). The description must keep the adaptation note.
3. Tick **"Altered or synthetic content"** (AI disclosure).
4. **Subtitles:** YouTube Studio → **Subtitles** → **Upload file** → `ep01-subtitles.srt`.
5. **Instagram Reels:** same video, cover = Shot 8b, caption from the kit.

- [ ] Published on YouTube · [ ] Published on Instagram

### 8.3 Write down your real numbers
Credits used, retakes per shot, and hours per phase. These decide your budget for the full episode.

---

## PHASE 9: The full Episode 1 (11 minutes), scene by scene

Repeat Phases 2–7 for each scene of the [full episode](episodes/ep01-long-kokulathin-kutti-thirudan.md), with these differences:

| What | Change |
|---|---|
| **Flow** | New project `EP01 Full` → aspect ratio **16:9** |
| **Prompts** | [GEMINI-ONLY-PROMPT-PACK.md Part B](GEMINI-ONLY-PROMPT-PACK.md#part-b-episode-1-full-169-all-95-shots) |
| **Voice lines** | [voice-lines file, Full Episode section](episodes/ep01-voice-lines-elevenlabs.md#full-episode-1-கோகுலத்தின்-குட்டித்-திருடன்) (87 lines) |
| **Voice method** | **Method A** for shots marked **LS**, **B or C** for the rest |
| **New characters** | Create pictures and voices for **Gomathi, Paati and Kamala** before Scene 3; **Kamsa** before Scene 10 |
| **New backgrounds** | courtyard, veranda, lane/banyan, storeroom, Yamuna, night bedroom, Mathura prison |
| **Music** | the [full cue sheet](05-music-bgm-plan.md#3-episode-1-long-cue-sheet-bgm-for-every-situation) (also make T4 gang, T5 sneak, T6 chase, T7 village, T10 Kamsa, T11 lullaby) |
| **Edit** | 16:9, 1920×1080, 24 fps; YouTube chapters from the episode file |

**Suggested order:**
1. Scene 5 first (you've already done it as the Short).
2. Then Scenes 7–9, the emotional core.
3. Then Scenes 1–4 and 6.
4. Then the Cold Open and Scene 10.

Publish each finished scene as a Short (Short #2 = Scene 4, Short #3 = Scenes 7–9) while you work, so the channel stays active.

**Credits:** the full episode needs about 250–300 Flow generations, which is several months of Gemini Pro credits. Plan it scene by scene across months, upgrade to Google AI Ultra while producing it, or trim it to 5–6 minutes. See [GEMINI-ONLY-WORKFLOW.md §5](GEMINI-ONLY-WORKFLOW.md#5-credits-what-you-can-make-on-gemini-pro).

---

## Where to get help
At any phase, share what you made (pictures, a clip, or a voice line described or attached) and tell me what feels off. I'll suggest the fix, rewrite a prompt or line, or rebuild the prompt packs if you change the script.
