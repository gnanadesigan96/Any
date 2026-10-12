# Tools and Workflow

Prices and limits are approximate and change frequently; confirm them on each vendor's pricing page before subscribing. Start with the **Essential** set. Add the others only when you hit a specific limit.

## 1. Recommended tool stack

| Stage | Essential (start here) | Optional / alternatives | Why |
|---|---|---|---|
| Story, research, Tamil script | **Gemini Pro** (you have it) + this kit | Claude, ChatGPT | Draft and polish dialogue; always read the Tamil aloud yourself |
| Character design and shot first frames | **Nano Banana in Gemini / Flow** (included) | Midjourney ($10+/mo), Ideogram | Strong face consistency from reference images; edits by instruction ("same boy, now laughing") |
| Image → video | **Veo 3.1 in Google Flow** (included, credit-limited) | Kling 2.x (cheaper per clip, good "elements" consistency), Hailuo, Seedance, Runway | Best-in-class motion and lighting; use *Frames to Video* or *Ingredients to Video* |
| Tamil voices | **ElevenLabs** (Starter ~$5, Creator ~$22/mo) | Sarvam AI Bulbul (Indian-language specialist, low cost), Gemini TTS in Google AI Studio (free tier; test Tamil quality), human voice artist | Distinct, emotional, consistent voices; Voice Design and voice cloning |
| Lip-sync | **sync.so (lipsync-2)** or **Kling Lip Sync** (pay-per-use, ~$5–15 per episode) | Hedra, HeyGen | Language-agnostic: they match mouth shape to the audio waveform, so Tamil works |
| Music | **Suno Pro** (~$10/mo; paid plan needed for commercial rights) | YouTube Audio Library (free), Udio, licensed stock | Custom devotional/playful score per episode |
| Sound effects | **ElevenLabs Sound Effects** (same subscription) | Pixabay / Freesound (check licence) | Anklets, cows, pot breaking, divine shimmer |
| Edit, subtitles, export | **CapCut** (free; desktop) | DaVinci Resolve (free, more control) | 9:16 timeline, SRT import, Tamil fonts, quick export |

**Essential monthly cost:** Gemini Pro (already paid) + ElevenLabs Creator (~$22) + Suno Pro (~$10) + lip-sync pay-per-use (~$10) ≈ **$40–45/month (~₹3,500)** on top of Gemini. See [03-qc-and-costs.md](03-qc-and-costs.md).

## 2. Comparison

Ratings are 1–5.

| Tool | Visual / audio quality | Tamil support | Character consistency | Ease | Price | Main limitation |
|---|---|---|---|---|---|---|
| Veo 3.1 (Flow) | 5 | 2 (native speech unreliable in Tamil) | 4 with reference images | 4 | Included, credit-capped | ~8 s clips; monthly credits run out fast on "Quality" |
| Nano Banana | 5 | n/a | 5 | 5 | Included | Occasionally changes jewellery or costume details; check every image |
| Kling 2.x | 4–5 | 1 (use external audio) | 4 ("Elements") | 4 | ~$10/mo + credits | Slower queue on free tier |
| ElevenLabs | 5 | 4 (good; review pronunciation of ழ/ள/ற) | 5 (same voice ID every time) | 5 | $5–22/mo | Child voices: Voice Design may refuse "child" prompts; use "young, high-pitched, playful" or a consented recording |
| Sarvam Bulbul | 4 | 5 (built for Indian languages) | 4 | 4 | Low | Fewer emotional controls |
| sync.so / Kling Lip Sync | 4 | 5 (audio-driven) | n/a | 4 | Pay-per-second | Works best on front/three-quarter faces, weaker on stylised or tiny faces |
| Suno | 4–5 | Tamil lyrics possible; use instrumental for clarity | n/a | 5 | $10/mo | Free tier is non-commercial |
| CapCut | 4 | Tamil text and fonts OK; auto-captions for Tamil are inconsistent, so import the SRT | n/a | 5 | Free | Some effects are watermarked "Pro" |

## 3. Why a combination, not one tool

No single tool reliably does **consistent characters + natural Tamil speech + lip-sync + editing**. The reliable chain is:

```
Script (this kit)
   │
   ├─► Nano Banana ──► character sheets ──► FIRST FRAME of each shot (PNG, 9:16)
   │                                              │
   │                                              ▼
   │                               Veo (Flow: Frames to Video) ──► 4–8 s clip, ambience only
   │                                                                   │
   ├─► ElevenLabs ──► Tamil line WAVs (one file per line) ─────────────┤
   │                                                                   ▼
   │                                               Lip-sync tool (only close-up speaking shots)
   │                                                                   │
   ├─► Suno (music) + ElevenLabs SFX ─────────────────────────────────►│
   │                                                                   ▼
   └─► SRT subtitles (this kit) ──────────────────────────────► CapCut: assemble, mix, subtitle, export 1080×1920
```

**Design trick that saves money:** write shots so only the close-ups need lip-sync. Lines delivered off-screen, with the speaker's back to camera, in wide shots, or as narration need no lip-sync. Episode 1 has 5 lip-sync shots out of 12.

## 4. The repeatable 12-step workflow

| # | Step | Tool | Output | Time (est.) |
|---|---|---|---|---|
| 1 | Pick the incident from the roadmap ([bible §6](02-series-bible.md#6-krishna-series-roadmap)) | — | Episode idea | 5 min |
| 2 | Research the traditional account; note the source verse and what you'll adapt | Gemini + a Bhagavatam translation | "Tradition vs adaptation" notes | 20 min |
| 3 | Story beats: hook (0–3 s), build, highlight, hook to next episode | [template](templates/episode-template.md) | Beat sheet | 20 min |
| 4 | Tamil dialogue, then **read every line aloud** and simplify | Gemini / you | Script | 40 min |
| 5 | Update character refs if a new character or age appears | Nano Banana | Ref PNGs | 30 min |
| 6 | First frame per shot (style block + refs + shot prompt) | Nano Banana | 12 PNGs | 60 min |
| 7 | Animate each frame (Frames to Video, 9:16, ambience-only audio) | Veo / Flow | 12 clips | 60–90 min |
| 8 | Generate each Tamil line as its own file; pick the best take | ElevenLabs | ~15 WAVs | 30 min |
| 9 | Lip-sync close-up speaking shots | sync.so / Kling | 4–6 synced clips | 30 min |
| 10 | Music (one 60 s cue) + SFX | Suno + ElevenLabs SFX | Audio stems | 30 min |
| 11 | Assemble in CapCut: clips → dialogue → SFX → music (ducked) → SRT → title/end cards → export | CapCut | MP4 1080×1920 | 60 min |
| 12 | QC ([checklist](03-qc-and-costs.md)), then publish with title, description and cover | YouTube / Instagram | Live Short | 30 min |

Plan on **6–8 hours for Episode 1** (learning curve) and **3–4 hours per episode** once the references and templates are settled.

### File naming (keeps the project manageable)
```
EP01/
  frames/  EP01_S03_v2.png
  clips/   EP01_S03_v2.mp4
  voice/   EP01_S08_L1_yashoda_take3.wav
  sync/    EP01_S08_sync.mp4
  music/   EP01_theme.wav
  sfx/     EP01_anklet.wav
  EP01_final_1080x1920.mp4
```

## 5. Using Flow/Veo well
- **Set 9:16** before generating. Cropping a 16:9 clip later loses resolution and framing.
- Use **Frames to Video** with your Nano Banana first frame. It gives far better consistency than text-only generation.
- **Ingredients to Video** (up to 3 reference images) is useful for shots with 2–3 characters.
- Draft on **Fast / Lite**, then spend **Quality** credits only on the 2–3 hero shots (the hook shot and the final reveal).
- In the prompt, say *"no dialogue, no speech, ambient sound only"* for shots you'll dub. For lip-sync shots, say *"the character speaks a short sentence with natural mouth movement"*. The motion helps the lip-sync tool, and you replace the audio anyway.
- Optional experiment: try Veo native Tamil speech on one short line (put the Tamil text in quotes). If it comes out clean, it can save a lip-sync pass. Don't depend on it.
- Generate **2 takes** of each shot and keep the better one. Budget for about 1 in 4 shots needing a third take.
