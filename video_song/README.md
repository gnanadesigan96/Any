# Image + Song → Animated Music Video

`make_video.py` turns one still image and an audio track into a 1080p, 30 fps animated video that reacts to the music.

What it animates:
- **Camera:** smooth push-ins and pans across the scene, in this order: wide shot, Shiva's face, the burning peak, the temple gopurams, the devotees, Nandi, then back to wide. There is a small zoom punch on strong beats.
- **Light:** the pillar of light and the god-rays pulse with the bass. The third-eye and face aura glow with the vocal/overall level.
- **Atmosphere:** the clouds breathe gently, the valley mist drifts, and the oil lamps flicker.
- **Particles:** rising embers and golden sparkles.
- **Finish:** a warm highlight roll-off, a vignette, title and closing cards, and fades in and out.

## Requirements
`ffmpeg`, Python 3, `numpy`, `Pillow`, `opencv-python-headless`.

## Usage
```bash
python3 make_video.py image.webp song.mp3 output.mp4 --workers 4
# quick 10 s preview starting at 0:28
python3 make_video.py image.webp song.mp3 preview.mp4 --start 28 --preview 10
```

The scene landmarks (beam position, face, camera keyframes) at the top of the script are set for the *Jothi Darisanam* artwork. Adjust `CAMERA`, `THIRD_EYE`, `BEAM_X` and the related values for a different image.
