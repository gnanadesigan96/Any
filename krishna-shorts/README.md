# Krishna Stories — 60-second animated Shorts

Faceless channel: one Krishna story per Short, told by an AI narrator over animated scenes,
word-by-word captions, soft music. No host, no interaction.

```
Claude (story + scene prompts) ─► image tool (one picture per scene) ─► optional image-to-video
        │                                                                     │
        └──► ElevenLabs (voice + word timings) ──► ffmpeg (make_short.py) ◄───┘ ──► short.mp4
```

## One-time setup

1. **Tools**: Python 3.9+, `ffmpeg` (with libass, the normal builds have it), `pip install pillow`
   (only used for placeholder frames).
2. **ElevenLabs**
   - Pick a narrator in the Voice Library (search "storyteller", "Indian", "warm narrator",
     or clone/design your own). Copy its **Voice ID**.
   - Profile → API Keys → create a key.
   - ```
     export ELEVENLABS_API_KEY=sk_...
     export ELEVENLABS_VOICE_ID=...
     ```
   - Always use the same voice: the voice is your channel's identity.
   - Hindi / Tamil / Telugu narration works too (`eleven_multilingual_v2` is the default model);
     set `"caption_font": "Noto Sans Devanagari"` (or Tamil etc.) in `story.json` so captions render.
3. **Images**: Claude and ElevenLabs's voice API don't draw pictures, so you need one image tool.
   Any that supports **9:16** and a **character reference** works: ChatGPT image generation,
   Midjourney (`--oref`/character reference), Leonardo, Ideogram, Flux. ElevenLabs's web app also
   has an Image & Video studio. Check whether your plan includes it before paying for another tool.
4. **Animation (optional, recommended)**: an image-to-video tool (Kling, Hailuo, Runway, Veo,
   or ElevenLabs's video studio) turns a still into a 5 s moving clip. Even without it,
   `make_short.py` animates stills with slow zooms/pans, crossfades and live captions.
5. **Music**: a calm flute/sitar track from the YouTube Audio Library or ElevenLabs Music,
   saved as `music.mp3` in the episode folder. It's ducked under the voice automatically.

## Making an episode (~30–45 min once you're used to it)

```bash
mkdir -p episodes/02-kaliya/images
```

1. **Story** — paste `prompts/claude_story_prompt.md` into Claude with the story name. Save the
   JSON reply as `episodes/02-kaliya/story.json`. Read it once aloud: 125–140 words ≈ 55 s.
2. **Pictures** — for each scene build the prompt with `prompts/image_prompt_template.md`
   (style + character + scene), generate at 9:16, save as `images/scene01.png`, `scene02.png`, …
3. **Animate key scenes (optional)** — turn 2–3 big moments into 5 s clips and save as
   `images/sceneNN.mp4` (it replaces the still for that scene; short clips are looped/slowed to fit).
4. **Voice**
   ```bash
   python3 scripts/make_voice.py episodes/02-kaliya
   ```
   Writes `voice.mp3` + `alignment.json` (exact timing of every word). Don't like the read?
   Tweak `voice_settings` in story.json (`stability` lower = more emotion, `speed` 0.7–1.2) and rerun.
5. **Render**
   ```bash
   python3 scripts/make_short.py episodes/02-kaliya
   ```
   → `episodes/02-kaliya/short.mp4`: 1080×1920, 30 fps, H.264/AAC, loudness −14 LUFS.
   Each picture stays on screen exactly while its sentences are spoken.
6. **Upload** as a Short using `youtube.title/description/tags` from story.json.

Try the whole thing for free first: `make_voice.py <episode> --fake` makes silent audio with
estimated timings, and missing images become labelled placeholders, so you can check the
edit before spending credits. `episodes/01-govardhan/` is a complete example story.

## What the video looks like

- 0–3 s: hook title at the top, first scene zooming in, narrator asks the hook question.
- Each scene: slow Ken Burns move (`motion` per scene), 0.5 s crossfade, warm grade + vignette.
- Captions: 1–3 words at a time, spoken word in saffron-gold, placed above the Shorts UI.
- End: "Jai Shri Krishna" (`outro_text`), fade out.

## Growing the channel

- **Consistency beats volume**: same voice, same Krishna design, same caption style, every episode.
  Post 1/day or at least 4/week at a fixed time.
- **Hook in the first 2 s** decides everything for Shorts. Always open with a question or
  a shocking line, never "Once upon a time".
- **Series** keep people binging: Bal Leela (childhood), Krishna vs demons, Mahabharata, Gita lessons
  in 60 s. Name them `Part 1/2/3` when a story is too long for one Short.
- **Monetisation note**: YouTube's *inauthentic content* policy demonetises mass-produced,
  template-only AI videos. Keep it original: your own script edits, a consistent hand-made
  character, real storytelling. Don't upload near-identical videos.
- Repurpose the same `short.mp4` to Instagram Reels and Facebook.

## Files

- `scripts/make_voice.py` — ElevenLabs text-to-speech with timestamps (stdlib only).
- `scripts/make_short.py` — the ffmpeg editor (scenes, motion, crossfades, captions, music ducking).
- `prompts/` — Claude story prompt and the image prompt template.
- `episodes/NN-name/` — one folder per Short.
