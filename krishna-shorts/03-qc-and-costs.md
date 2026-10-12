# Quality Control and Costs

## 1. Quality-control checklist (run on every Short and every long episode)

Watch the export **on a phone, full-screen, at normal volume**, then once more muted (to check subtitles).

### Story and tradition
- [ ] The story is coherent; a first-time viewer understands who is who without background knowledge
- [ ] The traditional basis is correct (check the source verses listed in the episode file)
- [ ] Invented details are never presented as scripture; the description carries the adaptation note
- [ ] The tone is respectful: playful but never mocking; divine moments treated with awe

### Tamil and voices
- [ ] Every line sounds like spoken Tamil, not written Tamil (read it aloud: would a Tamil family say it this way?)
- [ ] Grammar understandable; ழ / ள / ல, ற / ர, ண / ந / ன pronounced correctly
- [ ] The correct character speaks each line (match the voice file name to the script)
- [ ] Each character has the same voice as in previous episodes (same voice ID)
- [ ] Emotion matches the moment (scolding vs. teasing vs. awe)
- [ ] No TTS artefacts: robotic words, clipped endings, wrong stress, breathing glitches

### Visuals
- [ ] Krishna is recognisable in every shot: skin tone, kohl eyes, cheek dot, peacock feather, yellow dhoti, flute
- [ ] Costumes and jewellery are consistent within a scene (watch Yashoda's saree border, bangles and jasmine)
- [ ] No distorted faces, extra fingers or melting limbs, especially during fast motion
- [ ] No modern objects, text or watermarks in frame
- [ ] Lip-sync is believable on every **LS** shot; no teeth flicker or jaw warping
- [ ] Shot-to-shot colour matches (apply the same LUT)
- [ ] **Short:** faces and action sit in the centre, not hidden by the like/comment buttons on the right or the caption at the bottom
- [ ] **Long:** nothing important hidden behind YouTube's progress bar in the bottom 10%

### Audio
- [ ] Dialogue is always clearly louder than the music
- [ ] Music isn't continuous wall-to-wall; silence used at key moments (the kolusu beat, the reveal)
- [ ] Every situation has its planned BGM cue and the mood matches ([BGM checklist](05-music-bgm-plan.md#7-bgm-checklist-add-to-qc))
- [ ] SFX line up with on-screen action (pot crash, anklets)
- [ ] Final loudness ≈ −14 LUFS, no clipping

### Subtitles
- [ ] Subtitle text matches the spoken words exactly
- [ ] Each cue appears with its line and disappears after it
- [ ] Max 2 lines, readable at phone size; Krishna's lines in gold
- [ ] No spelling mistakes (have one Tamil-reading person check)

### Hook and ending
- [ ] Something visual or spoken happens in the first 2 seconds
- [ ] The middle has a clear story beat, not just pretty shots
- [ ] The ending lands (laugh, emotion or reveal) **and** teases the next episode honestly
- [ ] Title, description, tags, cover and AI-content disclosure are filled in

### When to regenerate (and when not to)
| Problem | Fix |
|---|---|
| Face wrong in the **first frame** | Regenerate the image (cheap) and never animate a bad frame |
| Face drifts during motion | Shorten the clip, simplify the action, or use a cut instead of continuous motion |
| Hand or finger glitch for a few frames | Trim around it in the edit rather than regenerating |
| Wrong costume detail in a wide shot | Usually fine; fix only if noticeable on a phone |
| Lip-sync off in a close-up | Redo the sync; if still bad, re-edit so the line plays over a reaction shot |

## 2. Cost estimate: 60-second Short (Episode 1)

Prices are approximate (late 2026, 1 USD ≈ ₹85). Check current pricing; Google's Flow credit amounts in particular change often.

| Item | Usage | Cost |
|---|---|---|
| Gemini / Google AI Pro | Character refs + ~15 first frames (Nano Banana); ~30 Veo Fast clips (2 takes × 15) ≈ 600 credits + 2 hero shots in Quality ≈ 200–400 credits | **Already paid** (~₹1,950/mo). One Short uses most of a month's credits. |
| ElevenLabs | ~20 lines × 3 takes ≈ 3–4k characters + SFX | Starter $5 or Creator $22/mo (Creator gives more room and better voice tools) |
| Lip-sync (sync.so / Kling) | 6 shots, ~30 s total | ~$3–8 |
| Suno | 4–5 cues | Pro ~$10/mo (needed for commercial rights) |
| CapCut | Edit, subtitles, export | Free |
| **Marginal cost for the first Short** | | **≈ $20–40 (₹1,700–3,400)** on top of Gemini Pro |
| Time | First Short | 6–8 hours |

## 3. Long-form episode (10–12 min)

The episode is **95 shots** ([details](episodes/ep01-long-kokulathin-kutti-thirudan.md#f-production-budget-for-this-episode)). With retakes, that's about 170 video generations.

| Option | How | Approx. monthly cost | Episodes / month | Notes |
|---|---|---|---|---|
| **A. AI Pro only** | Everything in Veo Fast, spread over months | ₹0 extra | ~1 long episode every 3–4 months | Too slow for a series; fine for learning |
| **B. Hybrid (recommended)** | Veo (Pro credits) for the ~13 hero and vision shots; **Kling** (or Hailuo / Seedance) for the ~82 dialogue and action shots | Kling ~$30–65 + ElevenLabs $22 + Suno $10 + lip-sync ~$15–30 ≈ **$80–130 (₹7,000–11,000)** | 1 long episode + 4 Shorts | Best quality-for-money. Keep the same Nano Banana first frames so both tools share one look. |
| **C. Google AI Ultra** | Upgrade from Pro (~25,000 Flow credits/mo) | ~$250/mo (check the India price) + voice, music and lip-sync ≈ **$300+** | 3–4 long episodes | Only worth it once the channel earns, or at a 2+ episodes/month pace |
| **D. Add Flow top-up credits** | If available on your plan | Pay as you go | — | Check Flow's settings for current top-up options |

**Recommendation:** start with **Short #1 on AI Pro only** to learn the pipeline. Then go **Hybrid (B)** for the long episode. Decide on Ultra only after 2–3 episodes, once you know your real retake rate.

### Long-episode budget at a glance (Option B)
| Item | Est. |
|---|---|
| Video (Veo Pro credits + Kling) | $30–65 |
| Voices (ElevenLabs Creator) | $22 |
| Lip-sync (~3.5 min synced) | $15–30 |
| Music (Suno Pro) | $10 |
| Editing (CapCut / Resolve) | $0 |
| **Total for long Ep 1 + its 4 Shorts** | **≈ $80–130 (₹7,000–11,000)** + Gemini Pro |
| Time | 40–60 h for the first episode, 25–35 h afterwards |

### Ways to cut cost without looking cheap
- Lines delivered off-screen, from behind or in wide shots don't need lip-sync (the scripts already use this).
- Narration over establishing shots and visual montages costs less than dialogue close-ups.
- Reuse establishing shots (Gokulam aerial, the courtyard, the riverbank) across episodes.
- Build a **shot library**: a good "Kannan laughing", "Yashoda smiling" or "cows at dusk" clip can be reused as a cutaway later.
- Spend Quality credits only where viewers stare: the hook, the reveal, and the cover-image shot.
