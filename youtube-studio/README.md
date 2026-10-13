# Mythology Video Studio (Tamil)

Turns a folder of pictures plus a narration into a finished YouTube episode:
pictures with slow zoom/pan, smooth transitions, a female Tamil voice, background
music that automatically gets quieter while she speaks, sound effects (thunder,
rain, conch, temple bells, chains ...), burned-in Tamil subtitles, an `.srt` file
for YouTube, a thumbnail and vertical Shorts.

All music and sound effects are **synthesised from scratch** by this code (no
samples), so they can't trigger a copyright claim. To use a better track instead,
drop a file with the same name into `assets/music/` (for example `assets/music/divine.mp3`)
or `assets/sfx/` (for example `assets/sfx/thunder.mp3`) and it's used automatically.

## Episode 1 is ready to fill in

`episodes/ep01_kannan_pirandhan/` - **கண்ணன் பிறந்தான்** (Krishna's birth), 30 scenes, about 6 minutes.

| File | What it is |
|---|---|
| `episode.yaml` | The whole episode: Tamil narration, music, sound effects and camera move for each scene |
| `IMAGE_PROMPTS.md` | One English image prompt per scene (paste into Gemini / Whisk / Ideogram), plus video-clip prompts |
| `narration_full.txt` | All narration, with 1.5 s pauses between scenes, to paste into the ElevenLabs website |
| `narration_by_scene.txt` | The same text, numbered by scene |

## Your steps for each episode

1. **Pictures.** Make one image per scene from `IMAGE_PROMPTS.md`. Save them as
   `images/01.jpg`, `images/02.jpg` ... `images/30.jpg` (png/webp also work).
   Optional: `images/intro.jpg` and `images/outro.jpg` become blurred backgrounds behind the title cards,
   and `images/thumbnail.jpg` is used for the thumbnail.
2. **Video clips (optional).** Scenes 06, 15, 21 and 27 are the big moments. If you make a 5-10 s AI clip
   for them, save it as `clips/06.mp4` etc. Without a clip, the picture is used.
3. **Voice.** Choose one way:
   - **ElevenLabs website:** pick a female Tamil voice, paste `narration_full.txt`, model
     *Eleven Multilingual v2*, download the MP3, then run
     `python make.py split episodes/ep01_kannan_pirandhan full.mp3`. This cuts it into one file per scene at the pauses.
   - **ElevenLabs API (automatic):** put your voice ID in `episode.yaml` (`voice_id:`), set the
     `ELEVENLABS_API_KEY` environment variable (never paste the key in a chat or commit it), then run
     `python make.py voice episodes/ep01_kannan_pirandhan`.
4. **Render.**
   ```
   python make.py check  episodes/ep01_kannan_pirandhan      # shows what's still missing
   python make.py render episodes/ep01_kannan_pirandhan --preview   # quick 720p draft
   python make.py render episodes/ep01_kannan_pirandhan      # final 1080p
   python make.py thumb  episodes/ep01_kannan_pirandhan      # thumbnail.jpg with Tamil title
   python make.py short  episodes/ep01_kannan_pirandhan --from 15 --to 18   # vertical Short
   ```
   Everything is written to `episodes/<episode>/build/`. Upload `<episode>.mp4`, `thumbnail.jpg`
   and `<episode>.srt` (as Tamil subtitles). The YouTube title, description and tags are at the bottom
   of `episode.yaml`.

Missing pictures show up as labelled placeholders, so you can render a draft at any time.

## Making the next episode

Copy the `ep01_kannan_pirandhan` folder, rename it, and edit `episode.yaml`: change the text,
`music:`, `ambience:`, `sfx:` and `image_prompt:` of each scene. Then run `python make.py text <folder>`
to regenerate the prompt and narration files.

**Sound names you can use in `episode.yaml`:**
- `music:` calm, night, sad, tension, storm, divine, celebration
- `ambience:` (loops under the whole scene) rain, river, wind, crickets, heartbeat
- `sfx:` (one-off) temple_bell, puja_bell, conch, thunder, chains, gate_open, gate_close, whoosh,
  shimmer, sword, impact. `at:` is seconds from the start of the scene; a negative number means seconds before the end.

**Camera moves (`motion:`):** zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down, zoom_in_top, static.

**Transitions (`transition:`):** fade (default), fadewhite (lightning or divine flash), fadeblack, dissolve,
plus any ffmpeg `xfade` name.

To hear every built-in sound, run `python make.py sounds` and play `assets/_generated/sound_preview.wav`.

## Running it on your own computer

You need Python 3.10+ and ffmpeg installed, then:
```
pip install -r requirements.txt
```
The free Tamil fonts (Noto Sans/Serif Tamil and Catamaran, SIL Open Font License) download automatically
on first run. A final 6-minute 1080p render takes about 15 minutes on a 4-core machine.
