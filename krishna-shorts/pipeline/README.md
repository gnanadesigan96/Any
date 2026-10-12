# Make the Short by script

One command-line tool, `kk.py`, makes Short #1 (வெண்ணெய் திருடன்) end to end:

| Step | What it makes | Service |
|---|---|---|
| `voices` | The 6 character voices (`KK_Kannan`...) if they don't exist yet | ElevenLabs Voice Design |
| `lines` | All 18 Tamil voice lines | ElevenLabs Text to Speech (Eleven v3, falls back to Multilingual v2) |
| `sfx` | 14 sound effects and ambience beds | ElevenLabs Sound Effects |
| `music` | 5 music cues (title, Kannan, Yashoda, divine, mystery) | ElevenLabs Music |
| `refs` | 21 reference pictures (5 characters × 4 + Yashoda's room) | Gemini API (Nano Banana) |
| `frames` | 16 first frames, each made with its characters' reference pictures | Gemini API |
| `clips` | 16 video clips (Veo, image-to-video, 9:16) | Gemini API (Veo), **paid per second** |
| `revoice` | Lip-sync: takes Veo's own speech, isolates it and converts it into each character's ElevenLabs voice; for other shots it finds where the mouths start talking | ElevenLabs Voice Isolator + Voice Changer |
| `assemble` | The finished MP4 (1080×1920), with every voice placed, ambience across cuts, sound effects, music that dips under speech, colour grade, Tamil subtitles burned in (Kannan in gold, narrator in italic), title and end card, loudness −14 LUFS. Also writes an `.srt` for YouTube | ffmpeg (local) |

Everything it needs (prompts, reference pictures per shot, lines, timings, sound and music cues) is in `episodes/short01.json`, built from the episode files by `make_manifest.py`.

**`assemble` works at any stage.** Shots without a clip use the still frame, and shots without a frame get a placeholder card. So the first run already gives you an animatic with voices and music, before any money is spent on video.

## What you need

| Need | Where | Note |
|---|---|---|
| `ELEVENLABS_API_KEY` | ElevenLabs → Developers → API Keys | Permissions: Text to Speech, Text to Voice / Voices (write), Sound Effects, Music, Voice Changer, Audio Isolation |
| `GEMINI_API_KEY` | **aistudio.google.com/apikey** | **Billing must be enabled** on the key's Google Cloud project for Veo. This is separate from your Gemini Pro subscription: Flow credits can't be used by scripts |
| Python 3.8+ and ffmpeg | Already in the Claude cloud session. On a Mac: python.org + `brew install ffmpeg` | No other packages needed |

**Approximate API costs for one Short** (check the current pricing pages):
- Veo Fast: about 76 s of video ≈ **$12–30** per full pass. Retakes cost extra.
- Images: about 40 ≈ **$2**.
- ElevenLabs: comes out of your plan's credits.

## Run it with Claude (cloud session)
1. In the session's environment settings (title bar → cloud environment → **Edit**):
   - **Allowed domains:** `api.elevenlabs.io`, `generativelanguage.googleapis.com`, and if video downloads fail, also `storage.googleapis.com` and `*.googleusercontent.com`.
   - **Secrets:** `ELEVENLABS_API_KEY` and `GEMINI_API_KEY`.
2. Start a new session on this repo and say: **"Run the Short #1 pipeline in krishna-shorts/pipeline."**
3. Claude runs the steps, looks at every picture it generates, sends you the voice samples, frames and the final MP4 for approval, and regenerates anything that's off.

## Run it yourself
```
cd krishna-shorts/pipeline
export ELEVENLABS_API_KEY=...   GEMINI_API_KEY=...      # Windows: set NAME=value

python kk.py status                 # what's done / missing
python kk.py voices                 # adult voices: 3 previews each → pick with ../tools/create_elevenlabs_voices.py save ...
                                    # child voices: pick from the Voice Library → python kk.py link KK_Kannan <voice_id> (see 'Child voices')
python kk.py lines
python kk.py sfx
python kk.py music
python kk.py assemble               # ← animatic with placeholder cards: check timing now
python kk.py refs --takes 2         # look at work/short01/refs/, pick with: python kk.py choose refs krishna_child_full 2
python kk.py frames --takes 2       # check every frame; redo one: python kk.py frames --only S03 --force
python kk.py assemble               # ← animatic with real frames
python kk.py clips                  # shows the cost; then:  python kk.py clips --yes
python kk.py revoice
python kk.py assemble               # ← the finished Short: work/short01/out/short01_vN.mp4 + short01.srt
```

Useful options:
- `--only S03,S08a` limits a step to some shots, lines or refs.
- `--force` redoes items that already exist.
- `--takes 2` makes alternatives.
- `choose <refs|frames|clips|voice> <id> <take>` promotes an alternative to be the main file.

**Hand-made pieces are fine.** If the API refuses something (Veo may block some shots with children, for example), make it in Flow or Gemini by hand and save it under the same name, e.g. `work/short01/clips/S08b.mp4`. Every step skips files that already exist, and `assemble` uses whatever is there.

## Child voices (Kannan, Balarama, Shridama, Subala)
ElevenLabs **does not allow designing children's voices** with Voice Design ("this prompt potentially doesn't follow our safety guidelines"). The script designs only the adult voices (Yashoda, Narrator) and asks you to pick the four boys' voices yourself. There are two approved ways:

**Automatic:** `python3 boys.py auto` searches the Voice Library for Tamil child-like/character voices, picks 4 different ones, adds them to your account, makes a Tamil test line for each (as published and 3 semitones higher), links them, and writes `work/boys/report.md`. Change any pick with `python3 kk.py link KK_Kannan <voice_id> --pitch 3`.

**A. Voice Library (by hand)**
1. ElevenLabs → **Voices** → **Explore / Voice Library**.
2. Search for **"cartoon"**, **"animated character"** or **"animation"**, and filter **Use case → Characters & Animation**. These are voices made for animated characters (performed by adult voice actors). Choose bright, youthful ones.
3. For each boy, preview a few. Then click **Add to my voices**.
4. Test it speaking Tamil: **Text to Speech** → the voice → model **Eleven v3** → paste his line from `../episodes/ep01-voice-lines-elevenlabs.md`.
5. Copy the **voice ID** (My Voices → the voice → ⋯ → **Copy voice ID**) and link it:
   ```
   python3 kk.py link KK_Kannan <voice_id>
   python3 kk.py link KK_Subala <voice_id>
   python3 kk.py link KK_Shridama <voice_id>
   python3 kk.py link KK_Balarama <voice_id>
   ```
6. Keep the four distinct: Kannan brightest and sweetest, Subala thinnest and most nervous, Shridama roundest and loudest, Balarama lowest and firmest.

**B. A real performer (most natural)**
An adult voice artist who does child voices (common in Tamil dubbing) records the lines, with written consent. Then either create an **Instant Voice Clone** of their "kid voice" (ElevenLabs → Voices → Clone) and link it as above, or convert each recording with **Voice Changer**.

The links are saved in `voice_map.json` (local to your computer). All later steps (`lines`, `revoice`) use them automatically.

## Test without any keys
```
python -I tests/test_pipeline.py
```
This runs all steps against fake services that return generated test media and checks the final video, lip-sync splitting and subtitles.
