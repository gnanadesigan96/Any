# Filmy Passport — YouTube assets

Not part of the SaaS pipeline; kept in its own folder.

- `video/filmy_passport_feel_good_partN_HQ.mp4`: "Feel-Good Movies — Part N" Shorts, 1080×1920, 30 fps, 39 s, H.264 + AAC 192 kbps. Ready to upload.
- `thumbnails/`: cover for the Part 1 Short (vertical 1080×1920) and a 16:9 thumbnail (1280×720).
- `branding/`: channel logo (800×800), banner (2560×1440) and video watermark.
- `branding/logo-options/`: the three minimal logo options (A monogram, B globe, C stamp seal).
- `scripts/`: Python (Pillow + NumPy + ffmpeg) generators for the video and the branding.
  The video script expects poster images in `scripts/posters/` (not committed).

## Making the next part
Each part is a `scripts/parts/partN.json` (5 movies: rank, title, year, cast, genres, description,
particles, motif, accent colour) plus a `posters/` folder with one `<key>.jpg` per movie:

    PART_DIR=<dir with config.json + posters/> python3 scripts/make_feel_good_short.py
    PART=N OUT_DIR=<dir> python3 scripts/make_thumbnail.py
