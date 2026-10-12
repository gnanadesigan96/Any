# How to Put This into Gemini: Step by Step

> Google renames buttons and menus often. If a button below has a slightly different name on your screen, look for the closest match; the steps stay the same.

## 0. Which Google tool does what

| You want to... | Use | Where |
|---|---|---|
| Make **character and background reference images** | **Gemini app** (image generation, "Nano Banana") | gemini.google.com or the Gemini mobile app |
| Make the **first frame** of each shot | Gemini app, or Flow's image mode | same |
| Turn a frame into a **video clip** | **Google Flow** (Veo) | **labs.google/flow** (use a computer; it's much easier than on a phone) |
| Get help with **scripts, Tamil lines, new prompts** | A **Gem** (your own custom Gemini assistant) | Gemini app → Gems |
| Tamil voices, lip-sync, music, editing | *Not Gemini:* ElevenLabs, sync.so/Kling, Suno, CapCut | see [01-tools-and-workflow.md](01-tools-and-workflow.md) |

Don't paste the whole script into Gemini expecting a video back. Gemini works **one image or one 8-second clip at a time**, and you join the clips in CapCut.

---

## Step 1: Get the files onto your computer or phone

The files are on GitHub:
**https://github.com/gnanadesigan96/Any/tree/claude/modest-turing-kfxpi6/krishna-shorts**

- If you only see other files, use the **branch dropdown** at the top-left of the file list and choose `claude/modest-turing-kfxpi6`.
- **To copy prompts:** open **[GEMINI-PROMPT-PACK.md](GEMINI-PROMPT-PACK.md)**. Every prompt is complete (style and avoid blocks already merged). Hover over a box and click the **copy icon** at its top-right.
- **To download everything:** on the repo page click **Code → Download ZIP**, then unzip it. The `krishna-shorts` folder is inside.

Also create this folder on Google Drive (or your computer) to save your results:
```
Kannan Kathaigal/
  refs/            ← character + background reference images
  EP01-short/frames/
  EP01-short/clips/
```

---

## Step 2 (optional but very useful): Create your "Kannan Kathaigal" Gem
A Gem is a custom Gemini that remembers your series rules, so you don't have to explain the project every time.

1. Open **gemini.google.com** → in the left menu, click **Gems** (or **Explore Gems**) → **New Gem**.
2. **Name:** `கண்ணன் கதைகள் – Production Assistant`
3. **Instructions:** paste this:
```
You are the production assistant for "கண்ணன் கதைகள்", a cinematic Tamil YouTube series about Lord Krishna's life,
made with AI tools. Follow the attached files exactly: 00-series-foundation (story arc, characters, world),
02-series-bible (visual style, STYLE and NEGATIVE prompt blocks, character prompts, voices), and the Episode 1 files.

Rules:
- Dialogue must be natural, everyday spoken Tamil (பேச்சுத் தமிழ்), never formal or literary. Suit each character's age and personality as described.
- When I ask for an image or video prompt, write it in English and ALWAYS include the full STYLE block at the start
  and the full NEGATIVE block at the end, and list which reference images to attach.
- Keep every character's appearance exactly as described in the bible (Kannan: deep blue-black skin, kohl eyes, dhrishti dot on left cheek, peacock feather, yellow silk dhoti).
- Keep tradition and creative adaptation clearly separate; name the source (e.g. Srimad Bhagavatam 10.8) and list what is invented.
- Tone: family-friendly, playful, devotional, never mocking, never gory.
```
4. **Knowledge:** click **Add files** and upload:
   `00-series-foundation.md`, `02-series-bible.md`, `02b-character-prompts-tamil.md`, `04-voices-and-cinematic-flow.md`, `05-music-bgm-plan.md`, `episodes/ep01-screenplay.md`, `episodes/ep01-long-kokulathin-kutti-thirudan.md`
   *If it won't accept `.md` files, rename them to `.txt`, or open each one, copy the text into a Google Doc, and attach the Docs.*
5. Click **Save**.

**What to ask your Gem:**
- *"Shot 3.4: give me the full first-frame prompt and motion prompt."*
- *"Rewrite Subala's lines in Scene 2 to sound more like a scared 5-year-old."*
- *"Write Episode 2 (சிறையில் ஒரு இரவு) in the same screenplay format."*

Use the Gem for **writing**. For **making images**, use a normal Gemini chat (Step 3). It behaves more predictably, and some Gem setups don't generate images.

---

## Step 3: Make the character reference images (Gemini app)

Do **one character per chat**, starting with Kannan. The prompts are in [GEMINI-PROMPT-PACK.md → Part 1](GEMINI-PROMPT-PACK.md#part-1-character-reference-images-gemini-app-one-chat-per-character).

1. Open **gemini.google.com** → **New chat**.
2. Turn on image generation: click **Tools** (or the **+** menu) → **Create images** (it may show a 🍌 banana icon). If you don't see it, just start your message with "Generate an image:"; Gemini switches automatically.
3. Paste **Prompt 1** (full body) and send.
4. **Check it** against Kannan's anchors: deep blue-black skin (not teal or purple), kohl eyes, black dot on the **left** cheek, a peacock feather in the topknot, a yellow silk dhoti, a flute at the waist, and gold anklets.
   - Not right? Reply in the same chat with what to fix, e.g. *"Same image, but make the skin deeper blue-black like a rain cloud and add the black dot on his left cheek."*
   - Totally wrong? Click **Redo / Regenerate**, or start a new chat.
   - Came out square? Reply *"Same image, but vertical 9:16."*
5. When you love it: **open the image → Download** (choose full size if asked). Save it as `refs/krishna_child_full.png`.
6. **In the same chat**, paste **Prompt 2** (turnaround) → download → `krishna_child_turnaround.png`.
7. Same chat: **Prompt 3** (expressions) → `krishna_child_expressions.png`.
8. Same chat: **Prompt 4** (portrait) → `krishna_child_front.png`.
9. Repeat Steps 1–8 in a **new chat** for Yashoda, Shridama, Subala and Balarama.

**If the face changes in Prompts 2–4:** start a new chat, click **+ → Upload** to attach your saved `_full.png`, and write *"Use this exact character. Keep the face, skin colour, hair, clothes and jewellery identical."* before the prompt.

✅ When done you should have **20 images** (5 characters × 4).

---

## Step 4: Make the background reference images
Prompts: [GEMINI-PROMPT-PACK.md → Part 2](GEMINI-PROMPT-PACK.md#part-2-background-reference-images-gemini-app-or-flow).
For Short #1 you need only **`bg_mainroom`** (Yashoda's room with the உறி) and **`bg_storeroom`** (for the long episode). Generate each in a new chat, pick the best, and save to `refs/`.

---

## Step 5: Make the first frame of each shot
Prompts: [GEMINI-PROMPT-PACK.md → Part 3](GEMINI-PROMPT-PACK.md#part-3-short-1-வெண்ணெய்-திருடன்-every-shot). Each shot lists the **Refs** to attach.

1. **New chat** (one chat per shot keeps things clean).
2. Click **+ → Upload files** and attach the refs listed, e.g. for Shot 8b: `krishna_child_front.png` + `krishna_child_expressions.png`. Add the background (`bg_mainroom.png`) for shots inside the house. Keep it to **3–4 images**; too many confuses it.
3. Type one line first: *"Use these reference images for the character's exact appearance and the room."* Then paste the **first-frame prompt**.
4. Check: is the face right? Are the hands normal? Is it vertical? Any text in the image? Fix by replying, or regenerate.
5. Download and save as `EP01-short/frames/EP01_S08b_v1.png`.

**Tip:** do all the frames of a scene, put them side by side, and check the costumes match **before** you make any videos. Fixing an image is free; fixing a video costs credits.

---

## Step 6: Turn each frame into a video clip (Google Flow)

1. On a computer, open **labs.google/flow** and sign in with the same Google account.
2. Click **New project** and name it `EP01 Short`.
3. Open the **settings** (gear / ⚙ icon near the prompt box) and set:
   - **Aspect ratio:** **9:16 (portrait)** for Shorts. (Use 16:9 for the long episode.)
   - **Model:** **Veo 3.1 Fast** (cheaper; good for most shots). Switch to **Quality** only for hero shots 1, 8 and 12.
   - **Outputs per prompt:** **1** (saves credits; generate again only if needed).
4. In the mode dropdown next to the prompt box, choose **Frames to Video**.
5. Click the **start frame** slot (**+**) → **Upload** your frame (e.g. `EP01_S08b_v1.png`). Leave the end frame empty.
6. Paste the shot's **motion prompt** from the pack.
7. Click **Generate** (→ arrow) and wait 1–3 minutes.
8. **Review:** Does the face stay the same throughout? Are the hands OK? Is the motion natural?
   - Good → click the clip → **Download** (choose **1080p / upscaled** if offered) → save as `EP01-short/clips/EP01_S08b_v1.mp4`.
   - Bad → change the motion prompt to something simpler, or make the clip shorter, then generate again.
9. Repeat for every shot.

**Shots with 2–3 characters (3, 9, 10):** if *Frames to Video* drifts, try **Ingredients to Video** instead. Upload up to 3 reference images (e.g. the Kannan and Yashoda portraits + the room) and paste the first-frame **and** motion description together.

**About sound:** Veo adds its own audio. That's fine: you'll mute it in CapCut and use your ElevenLabs Tamil voices, Suno music and sound effects.

**Watch your credits:** Flow shows your remaining credits (usually top-right or in your profile menu). Short #1 needs roughly 15–30 generations in Fast mode.

---

## Step 7: After Gemini
| Next | Tool | Guide |
|---|---|---|
| **Animatic first:** put the still frames + voices on a CapCut timeline to lock timing *before* generating more video | CapCut | [04 §B1](04-voices-and-cinematic-flow.md#b1-work-in-this-order-the-professional-secret-the-animatic) |
| Tamil voices matched to age and gender | ElevenLabs (+ real people via Voice Changer for kids and elders) | [04 Part A](04-voices-and-cinematic-flow.md#part-a-tamil-voice-casting) |
| Lip-sync | sync.so or Kling | [§E2](episodes/ep01-vennai-thirudan.md#e2-lip-sync-shots-1-3b-8a-8b-9-11b) |
| Music & SFX | Suno, ElevenLabs SFX | [§E3–E4](episodes/ep01-vennai-thirudan.md#e3-music-suno-instrumental) |
| Edit & subtitles | CapCut + `ep01-subtitles.srt` | [§E6](episodes/ep01-vennai-thirudan.md#e6-editing-and-export) |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Kannan's skin comes out teal, purple or bright blue | Add *"deep blue-black skin like a monsoon rain cloud, exactly matching reference"*, and attach `krishna_child_front.png` |
| Face changes between images | Always attach `_front.png` + `_full.png`; start a new chat if the old one has drifted |
| Text or letters appear in the image | Reply *"Same image with no text, letters or watermark"* |
| Image comes out square | Reply *"Same image, vertical 9:16"*, or make the frame in Flow's image mode with 9:16 set |
| Gemini refuses a prompt | Remove words that could be misread (e.g. "smash", "attack", "naked chest" → "bare-chested child in a dhoti") and try again. Stylised animation of children is normally fine; photoreal children can be restricted |
| Video face melts mid-clip | Shorter clip (4 s), less movement, a simple camera move; or cut away before the bad frames in the edit |
| "Limit reached" message | Your daily or monthly quota is used up; wait for the reset, or switch that shot to Kling |
| Can't upload `.md` files to the Gem | Rename to `.txt`, or paste the content into Google Docs and attach those |

## Your first session (about 2 hours)
1. Step 1: open the pack.
2. Step 3: make **Kannan only** (4 images). Take your time; this face carries the series.
3. Upload the 4 images here (or to `krishna-shorts/refs/` in the repo) and I'll check them against the character description before you continue with the others.
