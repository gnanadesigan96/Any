# Gemini-Only Workflow: making the series with Google tools only

This is the plan if you want to use **only Gemini / Google**, with no ElevenLabs, Suno, Kling or CapCut. Everything below comes with your Google account and Gemini Pro (Google AI Pro) plan.

Ready-to-paste prompts for this workflow: **[GEMINI-ONLY-PROMPT-PACK.md](GEMINI-ONLY-PROMPT-PACK.md)**. Every shot of the Short and the full Episode 1 has the Tamil dialogue built into the video prompt.

> Google renames buttons and moves features often. If a button below has a different name on your screen, look for the closest match.

---

## 1. What does what: the Google-only toolkit

| Job | Google tool | Where |
|---|---|---|
| Script help, Tamil lines, new prompts | **Gemini** (your Gem) | gemini.google.com |
| Character and background pictures, shot first frames | **Nano Banana** (image generation in Gemini) | Gemini app |
| Video clips **with the characters speaking Tamil, lip-synced automatically, plus sound effects** | **Veo 3.1 in Flow** | labs.google/flow |
| Narrator voice | **Gemini TTS** ("Generate speech") | aistudio.google.com (free with a Google account) |
| Background music, title song, lullaby | **Gemini music generation (Lyria)** | Gemini app → music / "Create music" tool |
| Joining clips in order (rough cut) | **Flow Scenebuilder** | labs.google/flow |
| Final edit: music + narration + on-screen subtitles | **YouTube Create** (Google's free editing app, Android) | Play Store |
| Subtitles on YouTube | **YouTube Studio → Subtitles → Upload file** (`ep01-subtitles.srt`) | studio.youtube.com |

### The big change from the earlier plan
In the earlier plan, the Tamil voices came from ElevenLabs and a separate tool matched the mouths. **In the Gemini-only plan, Veo generates the voice and the lip movement together, in the same clip.** You write the Tamil line inside the video prompt, and the character says it on screen.

- ✅ Lip-sync is automatic and natural, and sound effects and ambience come built in.
- ⚠️ You can't fine-tune a voice the way you can in a voice app. Each clip is generated fresh, so **a character's voice can vary a little between clips**. Section 4 shows how to keep that under control.

---

## 2. Honest limits (read before you start)

| Limit | What it means | What we do about it |
|---|---|---|
| **Tamil speech quality in Veo is unproven** | Veo may mispronounce Tamil words (ழ, ள, ற), slip in English-sounding vowels, or invent words | **Test first** (Step 1). Keep lines short and simple. Regenerate bad takes |
| **Voice consistency between clips** | Kannan may sound slightly different in Shot 3 and Shot 8 | The same "voice tag" in every prompt; generate a scene's clips in one sitting; keep only takes that match; use Extend for long conversations |
| **Child voices** | Veo may make a 5-year-old sound older | The voice tags say "5-year-old boy"; reject takes that sound like adults |
| **Credits** | Every take with dialogue costs credits, and dialogue shots need more retakes | See §5: Shorts fit your AI Pro plan; the 11-minute episode does not |
| **Clip length** | Each clip is about 4–8 seconds | Long conversations are split across several clips (already done in the pack) |
| **No full editor inside Gemini** | Gemini and Flow can't mix music, add narration under clips, or burn in subtitles | YouTube Create (Google's free editor) does the final assembly |

---

## 3. Step by step

### Step 1: The Tamil voice test (do this first; 30 minutes)
Before making anything else, find out how well Veo speaks Tamil for you.

1. Open **labs.google/flow** → **New project** → settings: **9:16**, **Veo 3.1 Fast**, **1 output**.
2. Choose **Text to Video** (no picture needed for this test) and paste:
```
Cinematic stylized 3D animation, premium Indian mythological animated film. Close-up of a 5-year-old Indian boy with deep blue-black skin, kohl-lined big eyes, a peacock feather in his topknot, butter on his cheeks, sitting on the floor of an ancient village house, looking up innocently.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync:
- The boy (high, bright, playful, giggly voice of a 5-year-old Tamil boy, exaggerated innocence, sing-song) says in Tamil: "அம்மா, நான் ஒண்ணுமே பண்ணலையே!"
Audio: natural room ambience only. No background music. No subtitles or on-screen text.
Duration: 4 seconds.
```
3. Generate 2–3 times. **Have a Tamil speaker listen:**
   - Are the words clear and correct?
   - Does it sound like a small child?
   - Does the mouth match?

| Result | What to do |
|---|---|
| Clear Tamil, child-like voice | 🎉 Go ahead with this workflow |
| Mostly good, a few words wrong | Make lines shorter; write a tricky word the way it sounds (e.g. `வெண்-ணெய்`); regenerate |
| Tamil is poor | Fallback inside Google: make the shot with the character **not speaking** (back to camera, wide shot or reaction), generate the line with **Gemini TTS** (Step 4), and lay it over the clip in the edit |

### Step 2: Character and background reference pictures
Exactly as in [GEMINI-GUIDE.md Steps 3–4](GEMINI-GUIDE.md#step-3-make-the-character-reference-images-gemini-app), using [GEMINI-PROMPT-PACK.md](GEMINI-PROMPT-PACK.md) Parts 1–2. Start with Kannan.

### Step 3: Make each shot (picture → talking video)
From **[GEMINI-ONLY-PROMPT-PACK.md](GEMINI-ONLY-PROMPT-PACK.md)**: Part A = the Short (9:16), Part B = the full episode (16:9).

1. **① First frame:** in the Gemini app, attach the listed refs and paste the first-frame prompt. Download it.
2. **② Video:** in Flow → **Frames to Video** → upload the frame as the start frame → paste the video prompt (it already contains the Tamil dialogue and the voice description) → Generate.
3. **Check every take for four things:**
   - Is the Tamil correct (listen twice)?
   - Is the right character speaking, in the right order?
   - Does the voice sound like this character's earlier clips?
   - Is the face consistent, with no melting?
4. Download the good one and name it `EP01_S08b_v2.mp4`.

### Step 4: The narrator (Google AI Studio)
The narrator is never on screen, so he doesn't need Veo. Gemini TTS gives one **fixed voice** that sounds identical in every episode.

1. Open **aistudio.google.com** → **Generate speech** (or "Generate media → Speech").
2. Choose **Single speaker**. Audition a few warm male voices (e.g. Charon, Algenib, Iapetus, Orus) with the first narration line.
3. **Pick one and write its name down.** It's the narrator's voice for the whole series.
4. Paste the style line + one narration line (all of them are in [Part C of the pack](GEMINI-ONLY-PROMPT-PACK.md#part-c-narrator-script-for-google-ai-studio-all-lines-in-order)) → **Run** → download as `NARR_<shot>.wav`.

AI Studio can also do **two-speaker** conversations. That's useful for the Step 1 fallback: you can generate, for example, a Yashoda–Kannan exchange as audio-only, using the same two voices every time.

### Step 5: Music with Gemini (Lyria)
1. Open the **Gemini app** → **Tools** → **Create music** (or ask *"Create a music track: ..."*).
2. Use the prompts from **[05-music-bgm-plan.md](05-music-bgm-plan.md)**. They work with Gemini's music tool too.
   - Choose **instrumental** for background cues.
   - Choose **vocal** for the title song and the lullaby (paste the Tamil lyrics from the plan).
   - Choose the **longer** track option when available.
3. Make the themes you need for Episode 1: the **title song**, **Kannan's theme**, **Yashoda's theme**, the **gang/chase theme**, **sneak theme**, **divine theme**, **mystery motif**, **Kamsa's theme** and the **lullaby**. Generate each a few times and keep the catchiest.
4. Download each and name it as in the plan (`T1_title`, `T2_kannan`...).

**Important:** every Veo prompt in the pack says **"No background music"**. Veo would otherwise add random music to each clip, and it would jump at every cut. All music comes from your Lyria tracks, laid across the whole scene in the edit, which is what makes it feel like one film.

### Step 6: Rough cut in Flow (optional)
In Flow, add your chosen clips to **Scenebuilder** in shot order and play them back to check the story flow and pacing. Download the joined scene if you like, but you'll still do the final mix in Step 7.

### Step 7: Final edit in YouTube Create (Google's free editor)
1. Install **YouTube Create** (Play Store) on your Android phone and sign in with the same account.
2. **New project** → import the clips in shot order (or the joined scene from Flow).
3. Trim each clip to its length in the script, cutting in the middle of movements.
4. Add the **narration** files at the right shots.
5. Add the **music** tracks per the cue sheet in [05-music-bgm-plan.md](05-music-bgm-plan.md). Lower the music volume wherever someone speaks.
6. Add **subtitles as text** (copy from the script or the `.srt`) using the style from the bible: white bold, Kannan's lines in gold, placed above the bottom of the screen.
7. Add the title card (peacock feather + "கண்ணன் கதைகள்") and the end card.
8. Export at **1080p**.
9. On YouTube, also upload the `.srt` in **YouTube Studio → Subtitles** for searchable captions.

*If YouTube Create isn't available on your phone, Google Photos' video editor or YouTube Studio's basic editor can do simple joins and trims, but they can't add your own music and narration tracks in layers. In that case a free editor (CapCut or DaVinci Resolve) is the one non-Google tool you'd need.*

---

## 4. Keeping it movie-like with Veo voices

1. **Use the exact voice tags** from the pack in every prompt. Never shorten or reword them.
2. **Generate a whole scene in one sitting**, in order, and compare each new take to the previous clip's voice before accepting it.
3. **For longer conversations in one shot,** generate the first part, then use Flow's **Extend** on that clip for the next line. The voice and look carry over better than a fresh clip.
4. **Reaction shots hide voice changes:** if one line keeps coming out in the wrong voice, put it over a listener's face or a wide shot instead.
5. **Ambience glue:** Veo adds background sound to each clip, and it changes slightly at every cut. In the edit, lower the clip sound between lines and lay one continuous ambience bed (birds, cows, village) across the scene. Veo can generate an 8-second ambience-only clip of the location; loop its audio.
6. Everything in [04-voices-and-cinematic-flow.md Part B](04-voices-and-cinematic-flow.md#part-b-making-the-whole-episode-flow-like-a-movie) still applies: shot order, eyelines, cutting on action, silence before big moments.

---

## 5. Credits: what you can make on Gemini Pro

Approximate figures: Google AI Pro is reported to give about 1,000 Flow credits a month, with one Veo Fast clip costing about 20 credits (≈ 50 clips/month). Check the real numbers in Flow.

| What | Clips | With retakes | Fits in AI Pro? |
|---|---|---|---|
| **Short #1 (60 s)** | 16 | ~30–40 | ✅ About one month's credits |
| **Each additional Short** | 12–16 | ~30–40 | ✅ One per month, roughly |
| **Full Episode 1 (11 min)** | ~110 | ~250–300 | ❌ About 5–6 months of AI Pro credits |

**Choices for the full 11-minute episode:**
1. **Make it scene by scene over several months** on AI Pro. Publish each scene's Short as it's finished (they're designed to stand alone), then release the full episode when all the scenes are done.
2. **Upgrade to Google AI Ultra** while making the full episode (far more credits), then drop back to Pro.
3. **Shorten the episode to ~5–6 minutes** by dropping or merging scenes (for example Scenes 2 and 6), so it fits in about 2–3 months.

Narration (AI Studio) and music (Gemini app) don't use Flow credits. Picture generation in the Gemini app has its own daily limits, which are generous for this project.

---

## 6. Your plan for the next two weeks (Gemini-only)

| Day | Do | Tool |
|---|---|---|
| 1 | Tamil voice test (Step 1). **Send me what you hear.** | Flow |
| 1–2 | Kannan's 4 reference pictures, then the other 4 characters | Gemini app |
| 3 | Pick the narrator voice; generate the Short's 2 narration lines | AI Studio |
| 3 | Make the title song, Kannan's theme, Yashoda's theme and the divine theme | Gemini app (music) |
| 4–6 | Short #1: 16 frames → 16 talking clips | Gemini app + Flow |
| 7 | Edit: clips + narration + music + subtitles → export | YouTube Create |
| 8 | Check with the [QC checklist](03-qc-and-costs.md#1-quality-control-checklist-run-on-every-short-and-every-long-episode) and publish; upload the `.srt` | YouTube Studio |
| 9+ | Decide how to do the full episode (§5) | — |
