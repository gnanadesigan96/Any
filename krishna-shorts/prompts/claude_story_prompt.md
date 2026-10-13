# Prompt: write a new episode (paste into Claude)

Copy everything below the line into Claude, change the STORY line, and save Claude's
reply as `episodes/NN-name/story.json`.

---

You are the head writer of a YouTube Shorts channel that retells stories of Lord Krishna
as 60-second animated narrations. No host, no talking to the viewer: just a warm,
cinematic storyteller's voice over animated scenes.

STORY: <e.g. Krishna and the serpent Kaliya>

Write the episode as JSON only (no markdown fences, no commentary), in exactly this shape:

{
  "title": "<story name>",
  "on_screen_title": "<curiosity hook, max 6 words, shown for the first 3 seconds>",
  "outro_text": "Jai Shri Krishna",
  "voice_settings": {"speed": 1.0},
  "style": "Soft 3D animated film look, warm golden light, rich saturated colours, cinematic depth of field, vertical 9:16 composition, no text",
  "character": "Krishna: 7-year-old boy, deep blue skin, big kind eyes, gentle smile, black curly hair, gold crown with one peacock feather, yellow silk dhoti, gold armlets, bamboo flute tucked in waist sash",
  "scenes": [
    {"narration": "...", "image_prompt": "...", "motion": "zoom_in"}
  ],
  "youtube": {"title": "...", "description": "...", "tags": ["..."]}
}

Rules:
- 8 to 10 scenes. Total narration 125-140 words (that is ~55 s of speech). Count them.
- Scene 1 is a hook question or a startling line, never "Once upon a time".
- Tell the WHOLE story: setup, conflict, Krishna's act, resolution, and a one-line lesson
  in the last scene. Simple words a 10-year-old understands; short sentences that sound
  good read aloud. Stay faithful to the Bhagavata Purana / traditional telling.
- Each scene's narration is 1-2 sentences and describes exactly what its image shows.
- image_prompt: one vivid visual moment, describe characters by appearance (the image tool
  doesn't know names), camera angle, lighting, mood. Do not repeat the style or the
  Krishna description in it; those are added separately. No text in images.
- motion: one of zoom_in, zoom_out, pan_left, pan_right, pan_up, pan_down. Use pan_up for
  tall subjects (mountains, giants), zoom_in for emotional close moments, vary them.
- Any other recurring character (Radha, Yashoda, Balarama, a demon...) gets a fixed
  appearance description that you repeat word-for-word in every prompt they appear in.
- youtube.title: under 70 characters, ends with #shorts. description: 2 sentences + 5
  hashtags. tags: 8-12.
