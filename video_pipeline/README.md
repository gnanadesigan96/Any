# Faceless YouTube video pipeline

One command turns a topic into a finished, reviewable YouTube package:

```
python make_video.py next --niche "Engineering Disasters"
```

| Stage | What happens | Tool |
|---|---|---|
| 1. Script | Research-style script split into ~10s scenes, 3 titles, description, tags, chapters, Shorts picks, and a fact-check list | Claude (`claude-opus-5-5`) |
| 2. Voice | Narration per scene with word-level timestamps | ElevenLabs |
| 3. Images | One illustration per scene in your fixed channel style, plus a thumbnail background | OpenAI image API |
| 4. Video | 1080p, slow zoom/pan on every image, word-synced captions, background music, loudness normalised to -14 LUFS | ffmpeg |
| 5. Shorts | 2-3 vertical 1080x1920 clips with a hook title | ffmpeg |
| 6. Review | `REVIEW.md` checklist + `metadata.json` (title, description with chapters and sources, tags) | - |
| 7. Upload | Only after you approve: private upload (optionally scheduled), thumbnail, Shorts | YouTube Data API |

**You stay in the loop on purpose.** Nothing uploads until you've watched the video, checked the
fact-check table and set `"approved": true`. That review is what keeps the channel monetisable under
YouTube's rules on mass-produced content.

Every stage saves its output in `runs/<topic>/`. If anything fails, fix it and re-run the same
command: finished stages are reused, so you only pay for what's missing.

## Shorts or long videos

Set `format` in `config.yaml`:

- `format: "shorts"` (default in `config.free.example.yaml`): each topic becomes **3 standalone vertical
  Shorts** (`short_1.mp4` ... `short_3.mp4`), each with its own hook, ~35-45 seconds of narration, a new
  visual every 3-4 seconds, big captions and the hook text on screen. Change the count with `shorts.per_topic`.
- `format: "long"`: one ~10-minute video per topic plus a few Shorts cut from it.

After rendering, the pipeline reports any silence longer than 1 second with its timestamp
(`Warning: 1.4s of silence at 0:21.3 in short_2.mp4`) so you can spot voice dropouts without
watching everything.

## Story series (one story, 20 Shorts)

```
python make_video.py series "Dracula by Bram Stoker" --parts 20 --style "graphic novel"
```

Retells one story as a numbered series of ~40-second Shorts (`part_01.mp4` ... `part_20.mp4`). Each part opens
with a one-line recap and ends on a cliffhanger, the top of the screen shows "Series · Part 3/20", and every image
uses the same art style and character designs, so the series looks like one world.

- **Script (free):** the command writes `PROMPT_1_outline.txt`. Paste it into a new claude.ai chat and save the reply
  as `reply_1_outline.txt`, then re-run. It then asks for the parts in batches of 5 (`PROMPT_2_...`, `PROMPT_3_...`),
  so a 20-part series takes 5 paste rounds in total. Use a new chat for each prompt.
- **Images (free):** illustrations are generated on your Mac by Z-Image-Turbo through mflux (Apache-2.0, commercial
  use allowed). It needs an Apple Silicon Mac with 16 GB+ memory and about 20 GB free disk for the one-time model
  download. Expect very roughly 30-90 seconds per image, so a 20-part series (about 160-200 images) takes a few
  hours. Leave it running; it resumes where it stopped if interrupted.
- **Try it small first:** `--first 2` renders only parts 1-2 so you can check the style before committing hours.
  Run again without `--first` to render the rest.
- **Choosing stories:** public-domain stories (classic novels, myths, folk tales, films from the 1920s) are safe to
  retell in full. For recent movies, never use real footage, posters or actors' likenesses; your own narration over
  your own illustrations is much safer, but retelling a whole recent film still carries some copyright risk.

## Free setup ($0 per video)

Every paid part has a free replacement. Start with this; switch any piece to the paid option later
by changing one line in `config.yaml`.

| Part | Free option | Paid option |
|---|---|---|
| Script | `script.provider: manual`: the pipeline writes a prompt, you paste it into the free **Claude.ai** chat and paste the reply back (about 5 minutes) | `api`: Claude API, fully automatic |
| Voice | `voice.provider: kokoro`: open-source voice that runs on your computer (Apache-2.0, commercial use allowed) | `elevenlabs` |
| Visuals | `images.provider: stock`: real stock **video clips** and photos from Pexels and Pixabay (free API keys, free for commercial use) | `openai`: AI illustrations |

1. Do steps 1–3 of Setup below.
2. `cp config.free.example.yaml config.yaml` and edit the `channel` section.
3. Get two free keys and put them in `.env` (`cp .env.example .env`):
   - Pexels: sign up at pexels.com, then go to pexels.com/api and click "Your API Key".
   - Pixabay: sign up at pixabay.com; your key is shown on pixabay.com/api/docs.
4. Pick a voice: `python make_video.py voices` writes a sample of each voice to `voice_samples/`.
   Put your favourite in `voice.kokoro.voice`. The first run downloads the voice model (~350 MB, one time).
5. Make a video:
   ```
   python make_video.py next --niche "Engineering Disasters"
   ```
   The first run stops and tells you to paste `PROMPT_FOR_CLAUDE.txt` into claude.ai and save the
   reply as `claude_reply.txt` in the run folder. Run the same command again and it finishes the video.
   If Claude's reply gets cut off, type "continue" in the chat and paste the rest after it.

Notes:
- **Captions:** Kokoro doesn't report exact word timings, so captions are timed per sentence and spread
  across the words. They can run up to a fraction of a second ahead of or behind the voice.
- **Visual matching:** stock footage is matched by keywords, so check the visuals during review. Generic
  shots work for most scenes; for rare events you may want to swap a few clips by hand (replace
  `images/scene_NNN.mp4` or `.jpg`, delete `video.mp4`, and re-run).
- **Credits:** stock creators are credited automatically in the video description.

## Setup (one time, ~30 minutes)

1. **Install Python 3.10+ and ffmpeg** (macOS: `brew install ffmpeg`).
2. **Install the Python packages:**
   ```
   cd video_pipeline
   python3 -m venv .venv && source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Try it for free first:** `python make_video.py make "Test topic" --dry-run` builds a full
   video with placeholder images and silent audio. No API keys needed. Open `runs/test-topic-dryrun/`.
4. **API keys:** `cp .env.example .env` and fill in:
   - `ANTHROPIC_API_KEY` from platform.claude.com
   - `ELEVENLABS_API_KEY` from elevenlabs.io (Profile, API keys)
   - `OPENAI_API_KEY` from platform.openai.com (used only for images)
5. **Config:** `cp config.example.yaml config.yaml` and set at least `channel.name`, `channel.niche`
   and `voice.voice_id` (pick a voice in ElevenLabs' Voice Library and copy its ID). Keep
   `images.style` the same for every video; it's your channel's look.
6. **Music (optional):** put a few royalty-free tracks (for example from the YouTube Audio Library)
   in `assets/music/`. One is picked per video and mixed quietly under the voice.

### YouTube upload setup (only needed for `upload`)

1. In Google Cloud Console, create a project and enable **YouTube Data API v3**.
2. Configure the OAuth consent screen (External) and add your own Google account as a test user.
3. Create an **OAuth client ID** of type **Desktop app**, download the JSON, and save it as
   `video_pipeline/client_secret.json`.
4. The first `upload` opens a browser to sign in to the channel; the token is saved to
   `youtube_token.json` for next time.

**Important limitation:** YouTube keeps videos uploaded through an *unverified* API project
locked as private. To publish them you must either pass YouTube's API audit (the "YouTube API
Services - Audit and Quota Extension" form), or upload the finished `video.mp4`,
thumbnail and metadata yourself in YouTube Studio, which takes about 2 minutes. Until you've
passed the audit, uploading through Studio is the practical route. Custom thumbnails also
require a phone-verified channel.

## Daily use

```
# See unused topics from the 1,398-topic bank
python make_video.py topics --niche "Engineering Disasters" --limit 20

# Make the next unused topic (or a random one) in a niche
python make_video.py next --niche "Engineering Disasters"
python make_video.py next --niche "Tech Rise & Fall" --random

# Make any topic you like, optionally with an angle
python make_video.py make "Why the Concorde Failed" --angle "A technical triumph that never made money"
```

After the script is written you'll see the scene, word and character counts and be asked before any
paid voice or image generation runs (`--yes` skips the question).

Then open the run folder:

1. Watch `video.mp4` and the `short_*.mp4` files.
2. Work through `REVIEW.md`: check each fact-check claim against its source.
3. Edit `metadata.json`: pick the `title` and `thumbnail`, tweak the description, then set
   `"approved": true`.
4. Upload (private):
   ```
   python make_video.py upload runs/<run-folder> --shorts
   python make_video.py upload runs/<run-folder> --publish-at 2026-11-01T14:30:00Z   # scheduled
   ```

### Fixing one part

| Problem | Command |
|---|---|
| A few visuals look wrong | Delete (or replace) those `images/scene_NNN.*` files, delete `video.mp4`, then re-run `make` |
| Rewrite the whole script | `--redo script` (regenerates everything) |
| New voice settings | `--redo voice` |
| New image style | `--redo images` |
| Re-render only (new music, captions, fonts) | `--redo video` |

## Rough cost per 10-minute video (paid setup)

The free setup costs $0.

Prices change, so check each provider's current pricing.

| Item | Approx. |
|---|---|
| Claude script (Opus, high effort) | $0.30-1.00 |
| Images (~55 scenes + thumbnail, medium quality) | $2-4 |
| ElevenLabs voice (~9,000 characters) | included in a monthly plan (~10 videos on a ~$22 plan) |
| **Total** | **about $3-5 per video plus the ElevenLabs plan** |

Rendering takes about 1.5-2x the video's length on a typical laptop, so roughly 15-20 minutes for a 10-minute video.

## Tests

```
python -m pytest -q tests
```

The tests run the whole pipeline offline and check the Claude, ElevenLabs and OpenAI requests against
mocked APIs. They need no keys and cost nothing.
