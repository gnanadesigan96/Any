# What to do now: a step-by-step plan

Goal for the next 7–10 days: **publish Short #1 (வெண்ணெய் திருடன்)**. It's the cheapest way to learn the whole pipeline before spending on the 10–12 minute episode. Don't buy anything except where a step says so.

## Day 1: Set up (1 hour)
- [ ] Create a Google Drive folder `Kannan Kathaigal/` with subfolders `refs/`, `EP01/frames`, `EP01/clips`, `EP01/voice`, `EP01/sync`, `EP01/music`, `EP01/sfx`.
- [ ] Open **Google Flow** (labs.google/flow) with your Gemini Pro account. Check how many **credits** you have this month and what Fast vs. Quality costs. Note the numbers.
- [ ] Create a free **ElevenLabs** account. Don't pay yet.
- [ ] Install **CapCut desktop** (free).
- [ ] Reserve the channel and handle names on YouTube and Instagram: **கண்ணன் கதைகள் / @KannanKathaigal** (or your preferred name).

## Days 1–2: Character references (3–4 hours, Gemini / Nano Banana, no extra cost)
Do the characters **one at a time, in this order**: Child Krishna → Yashoda → Shridama → Subala → Balarama.

For each one ([prompts: English](02-series-bible.md#2-characters) · [Tamil](02b-character-prompts-tamil.md)):
1. Open a **new Gemini chat** and paste STYLE + character + framing line + NEGATIVE.
2. Generate 4–8 versions and pick the one you love. **Spend the most time on Krishna**: the whole series depends on this face.
3. In the same chat, attaching that image, make the **turnaround sheet**, **expression sheet** and **close-up portrait**.
4. Save to `refs/` as `krishna_child_front.png`, `krishna_child_full.png`, `krishna_child_turnaround.png`, `krishna_child_expressions.png`.
5. Check against the anchors: skin colour, kohl eyes, cheek dot, peacock feather, yellow dhoti, flute. If anything is off, regenerate now. Fixing it later costs much more.

✅ **Done when:** 5 characters × 4 images are saved and look like the same person in every image.

## Day 3: The test shot (2–3 hours, decides everything)
Make **Short Shot 8** (Yashoda catches Kannan) completely, before anything else:
1. **Frames:** generate the 8a and 8b first frames in Nano Banana with the refs attached (prompts: "SHOT 8" in [the Short script](episodes/ep01-vennai-thirudan.md)).
2. **Video:** in Flow → *Frames to Video* → 9:16 → paste the motion prompt → generate in **Fast**.
3. **Voice:** in ElevenLabs, use *Voice Design* to create **Yashoda** and **Kannan** voices ([voice briefs](02-series-bible.md#3-voice-casting-elevenlabs-save-each-as-a-named-voice-and-always-reuse-the-same-voice-id)). Generate the two lines, 3 takes each.
4. **Lip-sync:** use the free trial credits on **sync.so** or **Kling** to sync the lines onto the clips.
5. Watch the result on your phone and **ask a Tamil-speaking family member** whether the voices sound natural.

Then decide:
| Result | Next move |
|---|---|
| Looks and sounds good | Continue with Days 4–6 |
| Voice not natural | Try **Sarvam AI (Bulbul)** or Gemini TTS in Google AI Studio for the same lines; or record the lines yourself / a family member and use ElevenLabs *Voice Changer* |
| Lip-sync looks bad | Try the other lip-sync tool; or regenerate the clip with the face more front-on and less head movement |
| Face changes in the video | Shorten the clip, simplify the motion, or try *Ingredients to Video* with the refs |

## Days 4–5: Make the rest of Short #1 (5–6 hours)
- [ ] Make first frames for **all 12 shots** and check them side by side. Animate only after every frame looks right.
- [ ] Animate them in Flow (Fast; use Quality only for Shot 1 and Shot 12 if credits allow).
- [ ] Generate all voice lines. **Now upgrade ElevenLabs to Starter ($5)** if the free credits run out.
- [ ] Lip-sync Shots 1, 3b, 8a, 8b, 9 and 11b.
- [ ] Music: **subscribe to Suno Pro ($10)** only now; you need it for commercial rights. Generate the 4 cues plus the flute motif. Generate SFX in ElevenLabs.

## Day 6: Edit, QC, publish (3–4 hours)
- [ ] Assemble in CapCut following [§E6 of the Short](episodes/ep01-vennai-thirudan.md#e6-editing-and-export), and import `ep01-subtitles.srt`.
- [ ] Run the [QC checklist](03-qc-and-costs.md#1-quality-control-checklist-run-on-every-short-and-every-long-episode) on your phone.
- [ ] Publish with the [title, description and cover](episodes/ep01-vennai-thirudan.md#f-publishing-kit). Tick YouTube's AI/synthetic content disclosure.
- [ ] Note your real numbers: credits used, retakes per shot, hours spent. These decide the budget for the long episode.

## Weeks 2–5: The 10–12 minute Episode 1
- [ ] Based on your Short #1 numbers, choose the budget option (most likely **Hybrid: Veo for 13 hero shots + Kling for the rest**; see [costs](03-qc-and-costs.md#3-long-form-episode-1012-min)).
- [ ] Make refs for the new characters (Gomathi, Paati, Gopi 3).
- [ ] Produce **one scene at a time**: frames → clips → voices → lip-sync. Scenes 5 and 7–8 can reuse your Short #1 work.
- [ ] Publish Short #2 (கோபியர் புகார்) as soon as Scene 4 is done. It keeps the channel active while you finish the rest.
- [ ] Edit the full episode, add chapters, publish, then release the trailer and Short #3 linked to it.

## Things to avoid
- Don't animate before the first frame is right. Fixing an image is cheap; fixing a video costs credits.
- Don't let Veo generate Tamil speech for the final cut unless you've tested it and it's clean.
- Don't buy Ultra, Kling or Suno until the step that needs them.
- Don't publish a line you haven't heard out loud and had checked by a Tamil speaker.

## Where I can help next
- **Review your reference images:** add them to `krishna-shorts/refs/` in this repo (or attach them here) and I'll check consistency against the anchors.
- **Rewrite lines** if any Tamil sounds unnatural when you hear it.
- **Write Episode 2** (சிறையில் ஒரு இரவு), long-form and Shorts, in the same format.
- **Make channel branding** (logo, banner, thumbnail templates), like the Filmy Passport assets in this repo.
