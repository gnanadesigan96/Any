# Chili Frogs — YouTube Short

`chili_frogs_short.mp4` is a 20-second vertical (1080×1920, 30 fps) Short with captions, music and sound effects. It is drawn and voiced entirely by `make_short.py`, using Pillow, numpy and ffmpeg.

```bash
pip install pillow numpy      # ffmpeg must be on PATH
python make_short.py out.mp4  # ~2 min render
```

To make a new episode, edit `states()` (the timeline and captions), `fat_frog` / `thin_frog` (the characters) and `synth_audio()` (the sound).

| Time | Beat | Caption |
|---|---|---|
| 0–2.6s | Thin frog waves a chili | THE HOTTEST / CHILI CHALLENGE |
| 2.6–3.6s | Chomp | ONE / BITE... |
| 3.6–7s | Turns red, cheeks puff, steam; fat frog laughs | UH OH... / IT'S / TOO HOT!! |
| 7.2–8.6s | Fat frog eats one too | HOLD MY / CHILI |
| 8.6–10.6s | Fat frog turns red, flames sputter | BIG / MISTAKE |
| 10.6–15s | Both rocket into the sky | LIFTOFF!! |
| 15–20s | Hovering, arms crossed, smug | WORTH IT? / FOLLOW / FOR PART 2 |

## Getting the 3D look of the reference video

The reference clip is a Pixar-style 3D AI video. To get that look, generate each shot below in a text/image-to-video tool (Google Veo, Kling, Hailuo/MiniMax, Runway, Pika) at **9:16**, 5–8 seconds per shot. Then cut the shots together in CapCut or another editor and add captions and SFX.

**Style suffix (append to every prompt):**
> 3D Pixar-style animation, glossy clay-like characters, big expressive googly eyes, vibrant saturated colors, sunny summer day, shallow depth of field, cinematic lighting, vertical 9:16, high detail

**Characters (keep this wording identical across shots for consistency):**
- *Big Frog*: a chubby round pale-green frog with huge pink lips and bulging eyes, with a tiny pink baby frog sitting on its head
- *Skinny Frog*: a tall skinny yellow frog with long thin legs and big red-rimmed eyes

1. **Field intro**: Big Frog and Skinny Frog stand in a lush chili pepper field full of bright red chilies. Skinny Frog grins and waves a red chili at the camera.
2. **The bite**: close-up, Skinny Frog bites the red chili with a loud crunch while Big Frog watches, curious.
3. **Heat hits**: Skinny Frog's whole body slowly turns bright red, cheeks puffing up like balloons, eyes bulging, steam shooting out of its head, trembling.
4. **Laugh**: Big Frog laughs hysterically, belly bouncing; the tiny pink frog on its head laughs too.
5. **Hold my chili**: Big Frog confidently eats a whole red chili, then freezes as its body turns red and its cheeks inflate enormously.
6. **Liftoff**: low-angle shot, both frogs blast off into the sky like rockets, fire and smoke shooting from beneath them, chili plants blown back.
7. **Sky**: both red frogs hover high above fluffy white clouds on jets of fire, arms crossed, looking smug at the camera.
8. **Fall (optional cliffhanger)**: aerial view over a forest, the frogs tumble down, still trailing flames.

**Tips**
- Generate one still per character first (Midjourney, Ideogram, Gemini image), then use image-to-video for every shot so the characters stay consistent.
- A video should hook in its first second, so put the bite or the red face as early as possible.
- Keep the total under 60 s, and add trending audio plus sound effects (crunch, boing, rocket whoosh).
- Suggested title: "He ate the hottest chili 🌶️🔥 #shorts #funny #animation"
