# கண்ணன் கதைகள் (Kannan Kathaigal): AI Tamil Mythological Shorts

A production kit for making cinematic 60-second Tamil Shorts/Reels about Lord Krishna, built so the same system can later be reused for Ganesha, Murugan and others.

| File | What it is |
|---|---|
| [NEXT-STEPS.md](NEXT-STEPS.md) | **Start here:** day-by-day plan to get Short #1 published, then the long episode |
| [01-tools-and-workflow.md](01-tools-and-workflow.md) | Which AI tools to use at each stage, how they compare, and the 12-step repeatable workflow |
| [02-series-bible.md](02-series-bible.md) | Locked visual style, character sheets with reusable reference prompts, series identity, episode roadmap |
| [02b-character-prompts-tamil.md](02b-character-prompts-tamil.md) | All character, style and negative prompts in Tamil, plus how to build reference sheets |
| [episodes/ep01-long-kokulathin-kutti-thirudan.md](episodes/ep01-long-kokulathin-kutti-thirudan.md) | **Episode 1, full 10–12 min YouTube episode (16:9)**: 10 scenes + cold open, 95 shots, complete Tamil dialogue, prompts, music, chapters, and the 4 Shorts to cut from it |
| [episodes/ep01-vennai-thirudan.md](episodes/ep01-vennai-thirudan.md) | **Short #1 (60 s, 9:16), production-ready**: story, shot timeline, Tamil dialogue, detailed per-shot AI prompts, voice/music/SFX, editing |
| [episodes/ep01-subtitles.srt](episodes/ep01-subtitles.srt) | Tamil subtitle file for Short #1, timed to the shot list |
| [03-qc-and-costs.md](03-qc-and-costs.md) | Quality-control checklist, cost estimate, regeneration budget |
| [templates/episode-template.md](templates/episode-template.md) | Blank template for every future episode |

---

## "If I upload the script to Gemini, will it make the video?"

**Not as a finished 60-second episode.** Here's what your Gemini (Google AI Pro) plan actually gives you, and how to use it.

**What you get**
- **Veo video generation** in the Gemini app and in **Google Flow** (labs.google/flow). Flow is the better place to work for this project.
- **Nano Banana (Gemini image generation)**, which is very good at keeping a character's face consistent when you give it a reference image. This is your main tool for character sheets and the first frame of each shot.
- **Gemini itself** as a writing assistant for scripts, Tamil dialogue polishing and research.

**What it does not do**
- Veo makes **one clip of about 8 seconds per generation**. You can't paste a 12-shot script and get a 60-second edited episode back. Each shot is generated separately, and you then join the clips in an editor.
- Your AI Pro quota is limited. Google now uses a monthly credit system in Flow (reported as about 1,000 credits/month on AI Pro, roughly 50 "Fast" clips or 10 "Quality" clips). Older reports describe about 3 Veo Fast videos per day in the Gemini app. Google changes these numbers often, so check the Flow help page for current limits.
- Veo can generate speech, but **Tamil dialogue is unreliable**: wrong pronunciation, made-up words, or a different voice from one clip to the next. For a dialogue-heavy series, generate the Tamil voices separately and lip-sync them onto the video.
- Characters drift between clips unless you anchor every shot with the same reference images (see the bible).

**The practical answer:** Gemini Pro covers roughly 60–70% of the job (images, video clips, script help). Add a Tamil voice tool, a lip-sync tool, a music source and a free editor. The exact combination, with costs, is in [01-tools-and-workflow.md](01-tools-and-workflow.md).

## Long episodes + Shorts: how they fit together
Each **long episode (10–12 min, 16:9)** tells one complete arc. **3–4 Shorts (60 s, 9:16)** are then cut from it by recomposing only their key frames to vertical and reusing the same voices and music. Episode 1 yields Short #1 (வெண்ணெய் திருடன்), Short #2 (கோபியர் புகார்), Short #3 (வாய்க்குள் ஒரு பிரபஞ்சம்) and a trailer. A 10–12 minute episode is about 95 AI clips, which is far beyond one month of AI Pro credits. See the cost options in [03-qc-and-costs.md](03-qc-and-costs.md#3-long-form-episode-1012-min).

## Getting started
1. Read the bible and generate the **character reference images** first (Krishna, Yashoda, Balarama, Shridama, Subala). Save the best ones; every later shot reuses them.
2. Make **one test shot** (Ep 1, Shot 8) end-to-end (image → video → voice → lip-sync) before producing the whole episode. This shows you the real cost per shot and whether your lip-sync tool works.
3. Then produce the rest of Episode 1 following the shot list.

> Note on tradition: each episode separates what comes from traditional sources (mainly Srimad Bhagavatam, Canto 10) from creative adaptation (dialogue, comic beats, compressed timelines). Keep that discipline; it protects the series' credibility with a devotional audience.
