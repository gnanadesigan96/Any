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
| A few images look wrong | Delete those `images/scene_NNN.png` files and `video.mp4`, then re-run `make` |
| Rewrite the whole script | `--redo script` (regenerates everything) |
| New voice settings | `--redo voice` |
| New image style | `--redo images` |
| Re-render only (new music, captions, fonts) | `--redo video` |

## Rough cost per 10-minute video

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
