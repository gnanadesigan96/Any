# Gemini-Only Prompt Pack: video with Tamil dialogue built in

For the **Gemini-only** workflow ([GEMINI-ONLY-WORKFLOW.md](GEMINI-ONLY-WORKFLOW.md)). Here Veo speaks the Tamil dialogue itself, so lip-sync happens automatically. Narration comes from Gemini TTS, and music from Gemini's music tool (Lyria).

**Clip lengths:** Veo makes clips of fixed lengths (usually 4, 6 or 8 seconds). Generate the nearest length at or above the duration shown, and trim it in the editor.

For each shot: **① First frame** in the Gemini app (attach the listed refs) → **② Video** in Flow: *Frames to Video*, upload the frame, paste the video prompt → **③ Narration** (if any) in Google AI Studio → Generate speech.

> Generated from the episode files. If you change a line there, ask Claude to rebuild this pack so the two stay identical.


## Voice tags (keep these identical in every prompt so each character sounds the same)

| Character | Voice tag used in every Veo prompt |
|---|---|
| கண்ணன் / Kannan | high, bright, playful, giggly voice of a 5-year-old Tamil boy |
| யசோதை / Yashoda | warm, soft, medium-low voice of a young Tamil mother in her late twenties |
| பலராமன் / Balarama | firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's |
| ஸ்ரீதாமா / Shridama | loud, round, slightly husky voice of a chubby 6-year-old Tamil boy |
| சுபலன் / Subala | thin, nervous, whiny voice of a small 5-year-old Tamil boy |
| கோமதி / Gomathi | loud, sharp, theatrical voice of a 30-year-old Tamil village woman |
| பாட்டி / Paati | slow, slightly shaky, aged voice of a 65-year-old Tamil grandmother |
| கமலா / Kamala | bright, lively, higher voice of a 22-year-old Tamil village girl |
| கம்சன் / Kamsa | very deep, cold, menacing voice of a 40-year-old king, with hidden fear |
| ஸ்ரீதாமா & சுபலன் / Shridama and Subala | two small Tamil boys' voices speaking together, one round and loud, one thin and nervous |
| கதைசொல்லி / Narrator | **Not Veo.** Gemini TTS in AI Studio, one fixed voice (see Part C) |


---

## Part A: Short #1 வெண்ணெய் திருடன் (9:16)

In Flow, set the aspect ratio to **9:16** first.


### SHOT 1: The Hook (0:00–0:03, 3 s) · LS

**Shot 1: ① First frame** · Refs: krishna_child_front, krishna_child_turnaround
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Extreme close-up, vertical 9:16. Child Krishna (exactly as in reference images) peeking over the rim of a round terracotta pot filled with fresh white butter, only his eyes, eyebrows, peacock feather and top of his head visible above the rim, his small blue-black hand inside the butter, a butter-smeared fingertip. Mischievous sparkling eyes looking straight into camera. Dim earthen storeroom, single warm shaft of morning light from a small window, glowing dust particles, very shallow depth of field.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 1: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Slow tilt up and gentle push-in. The boy raises his head slightly above the pot rim, lifts one butter-covered finger to his lips in a "shh" gesture, whispers to camera, then giggles with his eyes squeezing shut. Dust motes drift in the light beam.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, conspiratorial whisper, giggle at the end; breaks the 4th wall) says in Tamil: "ஷ்ஷ்... யார்கிட்டயும் சொல்லாதீங்க!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 3 seconds.
```


### SHOT 2: Gokulam at sunrise + title sting (0:03–0:08, 5 s) · VO

**Shot 2: ① First frame** · Refs: none
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Wide aerial view at sunrise of an ancient Indian cowherd village (Gokulam) on the bank of the Yamuna river, thatched-roof mud houses with white rice-flour kolam patterns at doorsteps, banyan and kadamba trees, herds of white and brown cows with painted horns, village women in colourful saris carrying brass pots, thin smoke rising from cooking fires, soft mist over the river, gold and pink sky, birds flying. Vertical 9:16, leading lines toward one larger house with a courtyard in the centre.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 2: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Smooth cinematic drone shot gliding forward and slowly descending over the village toward the central house with the courtyard. Birds cross the frame, smoke drifts, cows move slowly, mist moves on the river.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

**Shot 2: ③ Narration (AI Studio TTS)**
```
கோகுலத்துல ஒரு குட்டித் திருடன் இருக்கான்... அவன் திருடுறது தங்கம் இல்ல... வெண்ணெய்!
```


### SHOT 3: The plan (0:08–0:15, 7 s) · LS (Krishna)

**Shot 3: ① First frame** · Refs: krishna_child_front, shridama_front, subala_front (Ingredients)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Interior of an ancient Indian village house, mud walls painted with simple white motifs, wooden pillars, shelves of shining brass vessels, a large round terracotta pot hanging high from a wooden ceiling beam in a jute rope sling, a stone grinding mortar on the floor, open window with neem leaves outside. Low camera angle from behind three small boys looking up at the hanging pot: Child Krishna in the centre (yellow dhoti, peacock feather), chubby Shridama on the left (green headband, off-white dhoti), small thin Subala on the right (saffron dhoti, small stick). Warm sunbeams through the window.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 3: ② Video prompt (Flow, Frames to Video, 9:16)**
```
The three boys stare up at the hanging pot, then the camera pushes in as Krishna turns toward camera-left to his friends with a big mischievous grin, speaks excitedly, taps his temple with one finger. Subala on the right shakes his head nervously. Krishna then points at the chubby boy and gestures "bend down". Ambient room tone, birds outside.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, excited whisper) says in Tamil: "டேய், வெண்ணெய் அந்த உறியில தான் இருக்கு!"
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy, worried, whiny) says in Tamil: "அவ்வளவு உயரமா? எப்படிடா எட்டும்?"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, sly, then bossy-playful. **check ழ in வழி) says in Tamil: "ஒரு வழி இருக்கு... (to Shridama) குனிடா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```


### SHOT 4: The tower (0:15–0:21, 6 s) · no lip-sync

**Shot 4: ① First frame** · Refs: krishna_child_full, shridama_full, subala_full
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Same village house interior. A comic human tower of children: small Subala (saffron dhoti) crouching and holding a stone mortar steady with both hands, chubby Shridama (green headband) standing wobbly on top of the mortar, Child Krishna (yellow dhoti, peacock feather, gold anklets) standing on Shridama's shoulders, stretching one arm up toward a hanging terracotta butter pot in a rope sling near the ceiling. Full vertical composition from floor to ceiling, low angle. Warm sunbeams, dust in the air. All hands and feet anatomically correct.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 4: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Camera tilts upward from the boys' feet to the hanging pot, following Krishna as he climbs onto the chubby boy's shoulders. The middle boy's legs tremble, he grimaces with effort; the boy at the bottom grips the mortar and looks up in fear. Krishna stretches on his tiptoes, fingertips just touching the pot. Playful, slightly wobbly physical comedy.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy, straining, comic. **check ள in தோள்) says in Tamil: "சீக்கிரம் கண்ணா... தோள் வலிக்குது!"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, stretching effort, then triumph) says in Tamil: "அசையாதடா... இதோ... கிடைச்சுடுச்சு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```


### SHOT 5: Butter for everyone (0:21–0:26, 5 s) · wide, no lip-sync

**Shot 5: ① First frame** · Refs: krishna_child_full, shridama_full, subala_full
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Same interior, medium-wide low angle. Child Krishna balanced on top of the boy tower, one hand deep in the hanging butter pot, the other hand throwing a lump of white butter downward, laughing joyfully, butter on his cheeks. Below, Shridama and Subala with mouths open catching butter, laughing. At the open window a grey langur monkey reaching out to catch butter. Warm sunlight, flying droplets of butter frozen in light.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 5: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Krishna laughs and tosses lumps of butter down; the two boys catch them and laugh with butter on their faces; the monkey at the window snatches a lump and munches happily. Joyful chaotic energy, slight camera shake.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, generous, laughing) says in Tamil: "எல்லாருக்கும் உண்டு! குரங்கு மாமா, உனக்கும் தான்!"
Audio includes: children's joyful laughter, a monkey chattering.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```


### SHOT 6: Kolusu (0:26–0:30, 4 s) · no lip-sync

**6a: ① First frame** · Refs: yashoda_full (for saree/anklet match)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Extreme low close-up at floor level of a woman's bare feet with silver anklets (kolusu) and a red saree hem with mustard border stepping onto a wooden doorway threshold decorated with turmeric and kolam. Bright daylight behind her, silhouette effect.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**6a: ② Video prompt (Flow, Frames to Video, 9:16)**
```
One slow deliberate step onto the threshold, anklets swinging.
Audio includes: silver anklets jingling with each step.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 2 seconds.
```

**6b: ① First frame** · Refs: krishna_child_full, shridama_full, subala_full
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

The three boys in their human tower frozen mid-action, eyes wide with shock, butter dripping from Krishna's hand, all looking toward camera-right (the door). Comic freeze.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**6b: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Boys freeze, only their eyes slowly turn toward the door; the tower starts to wobble.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy, terrified whisper) says in Tamil: "டேய்... கொலுசு சத்தம்... அம்மா!"
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, off-screen (not visible), voice heard from outside the frame, long, sing-song warning, half-angry half-amused) says in Tamil: "கண்ணா...!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```


### SHOT 7: Collapse (0:30–0:34, 4 s) · SFX only

**Shot 7: ① First frame** · Refs: krishna_child_full, shridama_full, subala_full
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Same interior, wide shot. Comic chaos: the boy tower collapsing in mid-air, the terracotta butter pot falling from its rope sling, Shridama and Subala diving toward the open window, Child Krishna falling onto his bottom. Motion blur on limbs, butter splashing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 7: ② Video prompt (Flow, Frames to Video, 9:16)**
```
The tower collapses comically; the pot falls and shatters on the floor with butter splashing; two boys scramble out through the window and disappear; Krishna lands sitting on the floor amid broken pot pieces, butter on his face, then quickly hides both hands behind his back. Slapstick, family-friendly.
Audio includes: a clay pot crashing and shattering, whooshes, children scrambling.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```


### SHOT 8: Caught (0:34–0:41, 7 s) · LS ×2  ⭐ hero shot; use Quality mode

**8a: ① First frame** · Refs: yashoda_front, yashoda_full
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Medium low-angle shot of Yashoda (exactly as reference: red saree with mustard border, jasmine in braid, kumkum, bangles) standing in a doorway, hands on her hips, one eyebrow raised, lips pressed trying to look angry but eyes betraying amusement. Bright daylight behind her creating a warm rim light. Broken clay pot pieces and butter on the floor in the foreground.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**8a: ② Video prompt (Flow, Frames to Video, 9:16)**
```
She taps her foot once and speaks a scolding question with natural mouth movement; one eyebrow rises.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, stern but with an amused crack in her voice) says in Tamil: "கண்ணா, திரும்பவும் வெண்ணெய் திருடித் தின்னியா?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 3 seconds.
```

**8b: ① First frame** · Refs: krishna_child_front, krishna_child_expressions (innocent)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

High-angle close-up from an adult's point of view looking down at Child Krishna sitting on the floor, face, cheeks, nose and hair smeared with white butter, peacock feather crooked, both hands hidden behind his back, looking up with enormous innocent glistening eyes and a tiny pout. Soft warm light on his face, broken pot pieces around him. Adorable, expressive.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**8b: ② Video prompt (Flow, Frames to Video, 9:16)**
```
He blinks slowly with big innocent eyes, shakes his head side to side and speaks with natural mouth movement and a little pout.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, exaggerated innocence, sing-song, eyelashes fluttering) says in Tamil: "அம்மா, நான் ஒண்ணுமே பண்ணலையே!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```


### SHOT 9: The excuse (0:41–0:47, 6 s) · LS ×2

**Shot 9: ① First frame** · Refs: yashoda_front, krishna_child_front (Ingredients)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Eye-level two-shot in profile: Yashoda kneeling on the floor facing Child Krishna, holding up her index finger with a dab of white butter on it, teasing smile; Krishna, butter-smeared face, looking at her finger cross-eyed, about to make an excuse. Window with neem tree behind them, soft warm light, both faces clearly visible.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 9: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Slow push-in. Yashoda speaks a teasing question with natural mouth movement while showing the butter on her finger. Krishna looks at the finger, thinks for a beat, then brightens and points confidently toward the window while answering with natural mouth movement.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, teasing, raised eyebrow) says in Tamil: "அப்போ உன் மூக்குல இருக்கிறது என்ன?"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, quick thinking, confident lie, points at window) says in Tamil: "அதுவா... குரங்கு மாமா பூசிட்டுப் போயிட்டாரும்மா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```


### SHOT 10: Melted (0:47–0:51, 4 s) · no lip-sync

**Shot 10: ① First frame** · Refs: yashoda_front, krishna_child_front
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Medium close-up: Yashoda laughing with eyes closed, hugging Child Krishna tightly to her chest, wiping his buttery cheek with the end of her red saree; Krishna giggling with eyes squeezed shut, cheek pressed against her shoulder. Warm golden backlight, tender, loving.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**Shot 10: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Slow orbit around mother and child as she laughs, hugs him and rocks him gently, wiping his face with her saree.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, soft, adoring, whispered into his hair) says in Tamil: "(laughs) என் செல்லத் திருடா..."
Audio includes: a mother's warm laughter, bangles clinking.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```


### SHOT 11: Balarama's complaint (0:51–0:57, 6 s) · LS (Yashoda; Balarama's line can be OS as he runs in)

**11a: ① First frame** · Refs: balarama_full
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Balarama (7-year-old, fair skin, indigo dhoti, topknot) bursting through the bright doorway, out of breath, pointing accusingly toward camera with one arm outstretched, mouth open shouting. Dust swirling in the sunbeam.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**11a: ② Video prompt (Flow, Frames to Video, 9:16)**
```
He runs in, skids to a stop and points accusingly.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Balarama (firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's, breathless, tattling big brother) says in Tamil: "அம்மா! கண்ணன் மண்ணு தின்னான்! நானே பார்த்தேன்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 2 seconds.
```

**11b: ① First frame** · Refs: yashoda_front, krishna_child_front
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Close-up of Yashoda, her laughter fading into a worried frown, holding Child Krishna by both shoulders in the foreground (back of his head and peacock feather visible, out of focus). The light starts to cool slightly.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**11b: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Her smile drops into concern, she speaks a sharp short question, then a slow firm command with natural mouth movement.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, shock → firm, slow command. **check ற in திற) says in Tamil: "என்னது?! கண்ணா... வாயைத் திற!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```


### SHOT 12: The reveal + hook (0:57–1:02, 5 s) · VO  ⭐ hero shot; use Quality mode

**12a: ① First frame** · Refs: krishna_child_front
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Close-up of Child Krishna's face, a little butter still on one cheek, calm knowing gentle smile, eyes glowing faintly, lips just beginning to part, a soft golden-white light starting to glow from inside his mouth onto his chin. Room behind him darkened, deep indigo shadows, tiny floating golden particles. Divine, awe-inspiring, reverent.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**12a: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Very slow push-in. His smile becomes serene, he slowly opens his mouth and an intense golden-white divine light with swirling stars and tiny galaxies spills out, lighting the particles in the air. Reverent, not scary.
Audio includes: a deep humming 'om' and shimmering bells, no music.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 3 seconds.
```

**12a: ③ Narration (AI Studio TTS)**
```
அந்தச் சின்ன வாய்க்குள்ள... யசோதா என்ன பார்த்தாங்க?
```

**12b: ① First frame** · Refs: yashoda_front
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), vertical 9:16 composition, subject framed for mobile viewing, film grain subtle.

Extreme close-up of Yashoda's face lit only by golden-white light from below-front, eyes wide with awe and shock, tiny stars and galaxies reflected in her pupils, mouth slightly open, jasmine in her hair glowing. Dark indigo background.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**12b: ② Video prompt (Flow, Frames to Video, 9:16)**
```
Light flickers across her face, a tear forms, her lips part in wonder. Then light flares to white.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 2 seconds.
```


---

## Part B: Episode 1, full (16:9), all 95 shots

In Flow, set the aspect ratio to **16:9** first. Shots marked 🌟 are hero shots: use Quality mode if your credits allow.


### COLD OPEN (0:00–0:45)
Refs for this scene: **krishna_child_front/full, gomathi_full**

#### C1 🌟 (4 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

ECU: Kannan's eyes and peacock feather peeking over a butter pot rim in a pitch-dark storeroom; a soft blue-gold glow from his skin and jewels is the only light.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow tilt up; he lifts a buttery finger to his lips, whispers to camera, giggles.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "ஷ்ஷ்... யார்கிட்டயும் சொல்லாதீங்க!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

#### C2 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Dark corridor; a woman's hand holding an oil lamp approaches, flame flickering on mud walls.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Lamp moves closer, shadows sway.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman, off-screen (not visible), voice heard from outside the frame) says in Tamil: "யாரது? யாரு உள்ள?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### C3 (4 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan grinning in the glow, half-eaten butter pot beside him.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He winks at camera and darts out of frame; the hanging pot swings.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

#### C4 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Aerial: Gokulam at sunrise on the Yamuna (reuse Short Shot 2 prompt, 16:9).

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow drone glide forward.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
இவன் தான் கண்ணன். கோகுலத்துல எல்லாரும் இவனை உயிரா நேசிக்கிறாங்க...
```

#### C5 (10 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Village lane; Kannan running and laughing with a butter lump, three gopis chasing him waving ladles, cows scattering.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Tracking shot alongside him, playful.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 10 seconds.
```

**③ Narration (AI Studio TTS)**
```
...ஆனா எல்லார் வீட்டு வெண்ணெயும் இவனைக் கண்டாலே பயப்படுது!
```

#### C6 (12 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Peacock feather wipe → black background with golden particles.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Title animates in (CapCut): **கண்ணன் கதைகள்** / **அத்தியாயம் 1 — கோகுலத்தின் குட்டித் திருடன்**.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 12 seconds.
```


### SCENE 1: Dawn, the butter is churned (0:45–1:55)
Refs for this scene: **yashoda_front/full, krishna_child_front/full**

#### 1.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Wide courtyard at dawn: tulsi platform, kolam at the door, cows in a cowshed, herdsmen leaving with staffs.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow crane down into the courtyard.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

**③ Narration (AI Studio TTS)**
```
கோகுலத்துல காலை விடியறதே... தயிர் கடையற சத்தத்துல தான்.
```

#### 1.2 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda seated, churning curd in a big clay pot with a wooden churning rod pulled by a rope, hair loose, bangles shining.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Rhythmic churning, she hums with eyes half-closed, smiling.
Yashoda softly hums a gentle Tamil lullaby tune (humming only, no clear words).
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

*Song: use the lullaby track made with Gemini's music tool (see [GEMINI-ONLY-WORKFLOW.md](GEMINI-ONLY-WORKFLOW.md) Step 6) under this shot.*

#### 1.3 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

ECU: fresh white butter rising and clumping on top of the swirling buttermilk.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Butter gathers, churning stick spins.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 1.4 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Inside: Kannan asleep on a reed mat, hugging a small wooden cow toy; morning light on his face.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
His nose twitches, he sniffs, one eye pops open.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, sleepy murmur) says in Tamil: "ம்ம்ம்... வெண்ணெய் வாசனை..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 1.5 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan tiptoeing across the floor, anklet bells jingling.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He freezes at the jingle, grabs both anklets with his hands to silence them, looks at camera guiltily.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 1.6 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan hugging Yashoda from behind as she churns, cheek on her back; her face in profile, smiling.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She keeps churning, smiles without turning.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அம்மா... எனக்குப் பசிக்குது..."
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "பசிக்குதா? இல்ல வெண்ணெய் வேணுமா?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 1.7 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan now in front of her, pouting, holding out both hands.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She laughs, places a small ball of butter in his palms.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "ரெண்டும் தான்!"
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "இந்தா, கொஞ்சம் தான். மீதி அப்பா வந்ததும்."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 1.8 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan with an empty palm, butter on his lips, holding his hand out again with huge eyes.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He gulps, holds out his hand; she shakes her head firmly.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "இன்னும் கொஞ்சம்?"
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "ம்ஹூம்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 1.9 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda on tiptoe placing the butter pot into a jute rope sling hanging from the ceiling beam.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She ties it, dusts her hands, gives Kannan a triumphant look.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "இப்போ பாரு... இதை எப்படி எடுக்குறேன்னு நானும் பாக்குறேன்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 1.10 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Low angle: Kannan looking up at the pot high above.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He slowly turns to camera with a sly smile, eyebrows wiggling.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
யசோதா அம்மா நினைச்சாங்க... பிரச்சனை முடிஞ்சதுன்னு. ஆனா கண்ணனுக்கு... இது ஆரம்பம் தான்!
```


### SCENE 2: The gang and the plan (1:55–2:55)
Refs for this scene: **krishna_child_full, shridama_full, subala_full, balarama_full**

#### 2.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan running down a dusty village lane past cows and a bullock cart, peacock feather bouncing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Tracking shot, low angle.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 2.2 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Under the banyan tree: Shridama and Subala playing marbles (goli) on the ground.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Shridama looks up and grins.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy) says in Tamil: "வந்துட்டான்டா நம்ம தலைவன்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 2.3 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan crouching between them, arms around both, conspiratorial.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He whispers excitedly, eyes darting.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "டேய், ஒரு பெரிய வேலை இருக்கு. கோமதி அக்கா வீட்டுல இன்னைக்கு புது வெண்ணெய் கடைஞ்சிருக்காங்க!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 2.4 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Shridama licking his lips; Subala wide-eyed and scared.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Subala shakes his head.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy) says in Tamil: "ஐயோ! போன வாரம் மாட்டினப்போ அவங்க தொரத்துனது மறந்துட்டியா?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 2.5 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan drawing a plan in the dust with a stick: house, pot, mortar, window.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He taps the drawing proudly.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அதுக்குத்தான் இந்த தடவை ஒரு திட்டம்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 2.6 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Balarama standing behind them, arms crossed, eyebrow raised.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Boys turn around, startled.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Balarama (firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's) says in Tamil: "என்ன திட்டம்? திருட்டுத் திட்டமா?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 2.7 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan smiling sweetly up at Balarama; Balarama turning his face away.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Kannan pleads; Balarama shakes his head.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அண்ணா, நீயும் வாயேன்! உனக்குத்தான் பெரிய பங்கு!"
- Balarama (firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's) says in Tamil: "நான் வரல. அம்மா கிட்ட சொல்லிடுவேன் பாரு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 2.8 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Balarama walking away; Kannan shrugging to friends.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Kannan waves it off.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "விடுடா, அண்ணன் எப்பவுமே இப்படித்தான். வாங்க!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 2.9 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Three boys sprinting off down the lane, dust rising.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Low-angle tracking, then they run past camera.
Audio includes: children's laughter.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```


### SCENE 3: The heist at Gomathi Akka's house (2:55–4:20)
Refs for this scene: **krishna_child_full, shridama_full, subala_full, gomathi_full**

#### 3.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Gomathi stepping out of her house with a brass water pot on her hip.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She walks off toward the river.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman, to herself) says in Tamil: "யமுனைக்குப் போய் தண்ணி எடுத்துட்டு வந்துடறேன்..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.2 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Three small heads peeking from behind a hay pile.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Kannan waves "come on".
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, whisper) says in Tamil: "போயிட்டாங்க... வாங்க!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 3.3 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Inside total darkness; only the boys' eyes and the outline of hanging pots.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Boys shuffle in, bumping into each other.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy) says in Tamil: "டேய்... ஒண்ணுமே தெரியலடா..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.4 🌟 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan stepping forward; a gentle blue-gold light radiating from his skin and jewels illuminates the room, revealing dozens of pots hanging high.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Light spreads; friends' faces light up in awe.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy) says in Tamil: "ஆஹா... கண்ணா, நீ இருந்தா விளக்கே வேண்டாம்டா!"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "ஹிஹி!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 3.5 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan pointing at a heavy stone mortar in the corner.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He gives orders like a general.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அந்த உரலை இங்க உருட்டுங்கடா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.6 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Shridama and Subala straining to roll the heavy mortar under the pots.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Comic pushing, faces red.
Audio includes: children grunting with effort.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.7 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Tower: Subala steadying the mortar, Shridama standing on it, Kannan on his shoulders.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Camera tilts up the tower; Shridama wobbles.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy) says in Tamil: "கண்ணா... நீ குட்டியா இருந்தாலும் கனமா இருக்கடா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 3.8 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan poking the bottom of a hanging pot with Subala's stick; a stream of curd and butter pouring down into Subala's open mouth.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Liquid streams; Subala gulps happily.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy) says in Tamil: "ம்ம்ம்... ஆஹா... அமிர்தம்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.9 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Three monkeys gathered at the small high window.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Kannan tosses them butter; they catch and munch.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "குரங்கு மாமா, நீங்களும் சாப்பிடுங்க!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.10 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Exterior: Gomathi returning with the water pot, stopping, hearing the noise.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She sets down the pot, eyes narrowing.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman) says in Tamil: "உள்ள என்ன சத்தம்?!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 3.11 🌟 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Door flung open; daylight floods the storeroom; the boys and monkeys frozen mid-act, butter everywhere.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Light blasts in, everyone freezes.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman) says in Tamil: "அடேய் கண்ணா!! திரும்பவும் நீயா?!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 3.12 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Chaos: the tower collapses, friends and monkeys flee through the window, Kannan lands on the floor.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Kannan grins at Gomathi and dashes past her out the door.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy, running) says in Tamil: "வெண்ணெய் ரொம்ப நல்லா இருந்துச்சு அக்கா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 3.13 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Village lane: Gomathi chasing with a ladle; other gopis come out of their doors.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Tracking; she shakes the ladle.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman) says in Tamil: "நில்லுடா! இன்னைக்கு உங்க அம்மா கிட்ட சொல்லாம விடமாட்டேன்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```


### SCENE 4: The gopis' complaint (4:20–5:35)
Refs for this scene: **yashoda_full, krishna_child_full, gomathi_full, gopi2_full, gopi3_full**

#### 4.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda on the veranda stringing jasmine; Kannan running in panting, butter on his lip.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He jumps into her lap, curls up and shuts his eyes tight.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 4.2 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda looking down, puzzled; Kannan "asleep" in her lap.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She asks; he answers with his eyes still shut.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "என்னடா, ஓடி வந்து தூங்குற?"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "ஷ்ஷ்... நான் காலையிலிருந்து இங்கதான் தூங்கிட்டு இருக்கேன்."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 4.3 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Gate: four women marching in, led by Gomathi (butter on her saree).

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Determined walk, low angle.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman) says in Tamil: "யசோதா! உன் பையனைக் கொஞ்சம் பாரு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 4.4 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Paati (grandmother gopi) wagging a finger.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Speaks in a shaky, scolding voice.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Paati (slow, slightly shaky, aged voice of a 65-year-old Tamil grandmother) says in Tamil: "பால் கறக்குற நேரத்துக்கு முன்னாடியே கன்னுக்குட்டியை அவுத்து விட்டுடறான்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 4.5 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kamala (Gopi 3) with a pot on her hip, gesturing dramatically.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Animated complaint.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kamala (bright, lively, higher voice of a 22-year-old Tamil village girl) says in Tamil: "வெண்ணெயை குரங்குக்குக் குடுக்கறான்! குரங்கு சாப்பிடலைன்னா பானையையே உடைச்சிடறான்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 4.6 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Gomathi, hands on hips.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Points at the lap.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman) says in Tamil: "பிடிச்சா சிரிச்சுக்கிட்டே ஓடிடறான்! இன்னைக்கு கூட எங்க வீட்டுல..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 4.7 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda, amused, gesturing at the "sleeping" child.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Raises her eyebrows at the women.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "இவனா? இவன் சொல்றான், காலையிலிருந்து இங்கதான் தூங்குறானாம்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 4.8 🌟 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

ECU: Kannan opens one eye, winks at the gopis; a dab of butter on his lip.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow wink, tiny smirk.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 4.9 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The gopis gasp, then burst out laughing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Kamala points.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kamala (bright, lively, higher voice of a 22-year-old Tamil village girl) says in Tamil: "பாரு பாரு! உதட்டுல இன்னும் வெண்ணெய் இருக்கு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 4.10 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Gomathi bending, pinching Kannan's cheek, laughing despite herself.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She softens, everyone laughs.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Gomathi (loud, sharp, theatrical voice of a 30-year-old Tamil village woman) says in Tamil: "திருடனா இருந்தாலும்... இவ்வளவு அழகான திருடனை என்ன பண்றது?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 4.11 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Wide: the gopis leaving through the gate, smiling and looking back at Kannan.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow pull-back.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

**③ Narration (AI Studio TTS)**
```
கோகுலத்துப் பெண்கள் புகார் சொல்லத்தான் வந்தாங்க... ஆனா உண்மையில, கண்ணனைப் பார்க்கத்தான் வந்தாங்க.
```


### SCENE 5: The home pot (5:35–6:30)
Refs for this scene: **as listed in the Short shot**

#### 5.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda at the door with a milk pail, wagging a finger; Kannan on the mat, angelic.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Yashoda at the door with a milk pail, wagging a finger; Kannan on the mat, angelic.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "கண்ணா, நான் மாட்டுக் கொட்டகைக்குப் போயிட்டு வரேன். வெண்ணெய் பக்கம் போகக் கூடாது, சரியா?"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "சரிம்மா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 5.2 (4 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The moment she leaves, Kannan whistles; two heads pop up at the window.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
The moment she leaves, Kannan whistles; two heads pop up at the window.
Audio includes: a short whistle.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

#### 5.3 (7 s)

**① First frame** (from Short Shot 4, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Same village house interior. A comic human tower of children: small Subala (saffron dhoti) crouching and holding a stone mortar steady with both hands, chubby Shridama (green headband) standing wobbly on top of the mortar, Child Krishna (yellow dhoti, peacock feather, gold anklets) standing on Shridama's shoulders, stretching one arm up toward a hanging terracotta butter pot in a rope sling near the ceiling. Full vertical composition from floor to ceiling, low angle. Warm sunbeams, dust in the air. All hands and feet anatomically correct.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Camera tilts upward from the boys' feet to the hanging pot, following Krishna as he climbs onto the chubby boy's shoulders. The middle boy's legs tremble, he grimaces with effort; the boy at the bottom grips the mortar and looks up in fear. Krishna stretches on his tiptoes, fingertips just touching the pot. Playful, slightly wobbly physical comedy.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy) says in Tamil: "சீக்கிரம் கண்ணா... தோள் வலிக்குது!"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அசையாதடா... இதோ... கிடைச்சுடுச்சு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 5.4 (5 s)

**① First frame** (from Short Shot 5, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Same interior, medium-wide low angle. Child Krishna balanced on top of the boy tower, one hand deep in the hanging butter pot, the other hand throwing a lump of white butter downward, laughing joyfully, butter on his cheeks. Below, Shridama and Subala with mouths open catching butter, laughing. At the open window a grey langur monkey reaching out to catch butter. Warm sunlight, flying droplets of butter frozen in light.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Krishna laughs and tosses lumps of butter down; the two boys catch them and laugh with butter on their faces; the monkey at the window snatches a lump and munches happily. Joyful chaotic energy, slight camera shake.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "எல்லாருக்கும் உண்டு! குரங்கு மாமா, உனக்கும் தான்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 5.5 (4 s)

*This shot is 2 clips. Make each one and put them back to back.*

**① 6a: First frame** (from Short Shot 6, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Extreme low close-up at floor level of a woman's bare feet with silver anklets (kolusu) and a red saree hem with mustard border stepping onto a wooden doorway threshold decorated with turmeric and kolam. Bright daylight behind her, silhouette effect.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② 6a: Video prompt (Flow, Frames to Video, 16:9)**
```
One slow deliberate step onto the threshold, anklets swinging.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy) says in Tamil: "டேய்... கொலுசு சத்தம்... அம்மா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

**① 6b: First frame** (from Short Shot 6, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The three boys in their human tower frozen mid-action, eyes wide with shock, butter dripping from Krishna's hand, all looking toward camera-right (the door). Comic freeze.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② 6b: Video prompt (Flow, Frames to Video, 16:9)**
```
Boys freeze, only their eyes slowly turn toward the door; the tower starts to wobble.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, off-screen (not visible), voice heard from outside the frame) says in Tamil: "கண்ணா...!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

#### 5.6 (4 s)

**① First frame** (from Short Shot 7, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Same interior, wide shot. Comic chaos: the boy tower collapsing in mid-air, the terracotta butter pot falling from its rope sling, Shridama and Subala diving toward the open window, Child Krishna falling onto his bottom. Motion blur on limbs, butter splashing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
The tower collapses comically; the pot falls and shatters on the floor with butter splashing; two boys scramble out through the window and disappear; Krishna lands sitting on the floor amid broken pot pieces, butter on his face, then quickly hides both hands behind his back. Slapstick, family-friendly.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

#### 5.7 🌟 (7 s)

*This shot is 2 clips. Make each one and put them back to back.*

**① 8a: First frame** (from Short Shot 8, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Medium low-angle shot of Yashoda (exactly as reference: red saree with mustard border, jasmine in braid, kumkum, bangles) standing in a doorway, hands on her hips, one eyebrow raised, lips pressed trying to look angry but eyes betraying amusement. Bright daylight behind her creating a warm rim light. Broken clay pot pieces and butter on the floor in the foreground.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② 8a: Video prompt (Flow, Frames to Video, 16:9)**
```
She taps her foot once and speaks a scolding question with natural mouth movement; one eyebrow rises.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "கண்ணா, திரும்பவும் வெண்ணெய் திருடித் தின்னியா?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

**① 8b: First frame** (from Short Shot 8, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

High-angle close-up from an adult's point of view looking down at Child Krishna sitting on the floor, face, cheeks, nose and hair smeared with white butter, peacock feather crooked, both hands hidden behind his back, looking up with enormous innocent glistening eyes and a tiny pout. Soft warm light on his face, broken pot pieces around him. Adorable, expressive.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② 8b: Video prompt (Flow, Frames to Video, 16:9)**
```
He blinks slowly with big innocent eyes, shakes his head side to side and speaks a short sentence with natural mouth movement and a little pout.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அம்மா, நான் ஒண்ணுமே பண்ணலையே!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 4 seconds.
```

#### 5.8 (6 s)

**① First frame** (from Short Shot 9, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Eye-level two-shot in profile: Yashoda kneeling on the floor facing Child Krishna, holding up her index finger with a dab of white butter on it, teasing smile; Krishna, butter-smeared face, looking at her finger cross-eyed, about to make an excuse. Window with neem tree behind them, soft warm light, both faces clearly visible.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow push-in. Yashoda speaks a teasing question with natural mouth movement while showing the butter on her finger. Krishna looks at the finger, thinks for a beat, then brightens and points confidently toward the window while answering with natural mouth movement.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "அப்போ உன் மூக்குல இருக்கிறது என்ன?"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அதுவா... குரங்கு மாமா பூசிட்டுப் போயிட்டாரும்மா!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 5.9 (5 s)

**① First frame** (from Short Shot 10, now 16:9)
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Medium close-up: Yashoda laughing with eyes closed, hugging Child Krishna tightly to her chest, wiping his buttery cheek with the end of her red saree; Krishna giggling with eyes squeezed shut, cheek pressed against her shoulder. Warm golden backlight, tender, loving.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow orbit around mother and child as she laughs, hugs him and rocks him gently, wiping his face with her saree.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "(laughs) என் செல்லத் திருடா..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```


### SCENE 6: Play on the Yamuna bank (6:30–7:15)
Refs for this scene: **krishna_child_full, shridama_full, subala_full, balarama_full**

#### 6.1 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Wide golden riverbank, boys playing tag, calves grazing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow pan.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

**③ Narration (AI Studio TTS)**
```
சாயங்காலம். யமுனைக் கரையில பசங்க விளையாட்டு.
```

#### 6.2 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan running, looking back over his shoulder, laughing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Tracking.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "டேய், என்னைப் பிடிக்க முடியுமா? பிடிச்சுப் பாரு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 6.3 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Shridama chasing, arms out, puffing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Tracking from front.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy) says in Tamil: "இருடா கண்ணா! இன்னைக்கு உன்னை விடமாட்டேன்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 6.4 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan hiding behind a kadamba tree trunk, then squatting by the wet clay bank.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He peeks out, giggles, sits down.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 6.5 🌟 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

ECU: Kannan's small blue fingers picking up a pinch of wet earth; his face, curious.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He looks at it, puts it in his mouth, smiles serenely; a faint golden sparkle.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 6.6 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Balarama at a distance, freezing, eyes wide, pointing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He shouts across the bank.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Balarama (firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's) says in Tamil: "டேய்! கண்ணன் மண்ணு திங்கிறான்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 6.7 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The friends gathering around Balarama, gasping.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
They run off toward the village.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Balarama (firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's) says in Tamil: "வாங்கடா, அம்மா கிட்ட சொல்லுவோம்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```


### SCENE 7: "Look in my mouth" (7:15–7:55)
Refs for this scene: **yashoda, krishna_child, balarama, shridama, subala**

#### 7.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Balarama, Shridama and Subala bursting into the courtyard.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Shouting over each other.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Balarama (firm, proud voice of a 7-year-old Tamil boy, a little lower than Kannan's) says in Tamil: "அம்மா! அம்மா! கண்ணன் மண்ணு தின்னான்! நானே பார்த்தேன்!"
- Shridama and Subala (two small Tamil boys' voices speaking together, one round and loud, one thin and nervous) say in Tamil: "ஆமா அம்மா! நாங்களும் பார்த்தோம்!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 7.2 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda lighting a lamp, turning sharply; the jasmine string drops.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Shock.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "என்னது?! மண்ணா?!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 7.3 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan strolling in casually; Yashoda grabbing his wrist.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She scolds, worried.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "ஏன்டா இப்படிப் பண்ற? வயிறு வலிக்கும்னு எத்தனை தடவை சொல்றது!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 7.4 🌟 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Close-up of Kannan, calm, almost too calm, lamp light in his eyes.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
He answers steadily.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "அம்மா, நான் தின்னல. இவங்க எல்லாரும் பொய் சொல்றாங்க. நம்பலைன்னா... என் வாயைப் பாரு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 7.5 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda kneeling, holding his chin.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Firm.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "சரி... வாயைத் திற! காட்டு!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 7.6 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan's tiny knowing smile; the boys leaning in behind.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
All sound drains away.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```


### SCENE 8: The universe in his mouth (7:55–9:15) 🌟 visual centrepiece
Refs for this scene: **krishna_child_front, yashoda_front**

#### 8.1 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan's face; lips parting, golden-white light emerging.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Push-in; light floods out.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 8.2 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda's face lit from below, eyes widening.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Light flickers on her face.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### 8.3 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Camera flying into a glowing opening → infinite starfield and spiral galaxies.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Fast fly-through, then slowing.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
அந்தச் சின்ன வாய்க்குள்ள... யசோதா பார்த்தது மண் இல்ல...
```

#### 8.4 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The sun, moon and planets orbiting, stars swirling in deep indigo space.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow orbit.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
...முழு பிரபஞ்சத்தையும்! வானம்... சூரியன்... சந்திரன்... நட்சத்திரங்கள்...
```

#### 8.5 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Majestic mountains, oceans and islands seen from high above, clouds drifting.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Descending glide.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
...மலைகள்... கடல்கள்... தீவுகள்... இந்த பூமி முழுசும்...
```

#### 8.6 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The elements: swirling wind, sacred fire, lightning across the clouds.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Dynamic swirl.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

**③ Narration (AI Studio TTS)**
```
...காற்று... நெருப்பு... மின்னல்...
```

#### 8.7 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Diving down through clouds to a tiny Gokulam village on the shining Yamuna.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Dive, then slowing.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
...அதுக்குள்ளேயே... கோகுலம்!
```

#### 8.8 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Inside the vision: the same courtyard, where Yashoda sees *herself* kneeling before glowing Kannan.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow push toward the "other" Yashoda.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
...அங்கே, கண்ணன் முன்னாடி மண்டியிட்டு உட்கார்ந்திருக்கிற... அவங்களையே!
```

#### 8.9 🌟 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Back to the real Yashoda: trembling, a tear, stars reflected in her eyes.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Micro-expressions.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, whisper) says in Tamil: "இது... கனவா? இல்ல... மாயையா?"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 8.10 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda's face slowly calming into reverence.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
She bows her head slightly.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, as her inner thoughts: her lips do not move, the voice is soft with a gentle echo) says in Tamil: "இல்ல... இவன் சாதாரணக் குழந்தை இல்ல... இந்த உலகத்தையே தாங்குறவன்..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 8.11 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Wide: Yashoda joining her palms in prayer before the radiant child; boys in the background bowing.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow pull-back; music peaks.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```


### SCENE 9: Maya: she forgets, and loves (9:15–9:55)
Refs for this scene: **yashoda, krishna_child, shridama, subala**

#### 9.1 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Kannan's eyes, gentle and loving; a soft golden mist beginning to rise from him.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Mist drifts outward.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

**③ Narration (AI Studio TTS)**
```
அப்போ கண்ணன் நினைச்சான்... அம்மா என்னைக் கடவுளாப் பார்க்க வேண்டாம். அம்மாவாவே பார்க்கட்டும்.
```

#### 9.2 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

The mist touching Yashoda; her folded hands loosening.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
The vision fades from her eyes.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 9.3 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Yashoda blinking, confused, then seeing just her little boy with mud on his lip.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Puzzled smile.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "...என்ன யோசிச்சேன்? ம்ம்... ஞாபகமே இல்லையே..."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 9.4 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

She scoops him into her lap and kisses his forehead.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Tender; he giggles.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties) says in Tamil: "என் கண்ணா... இனிமே மண்ணு திங்கக் கூடாது, சரியா?"
- Kannan (high, bright, playful, giggly voice of a 5-year-old Tamil boy) says in Tamil: "சரிம்மா... (giggle)"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

#### 9.5 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Wide: mother and child in the lamplit courtyard.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow crane up.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

**③ Narration (AI Studio TTS)**
```
வேதங்கள் தேடுற இறைவனை... யசோதா தன் மடியில கொஞ்சிக்கிட்டு இருந்தாங்க.
```

#### 9.6 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Shridama and Subala looking at each other, baffled.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Comic shrug.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Shridama (loud, round, slightly husky voice of a chubby 6-year-old Tamil boy) says in Tamil: "என்னடா நடந்துச்சு?"
- Subala (thin, nervous, whiny voice of a small 5-year-old Tamil boy) says in Tamil: "தெரியல... ஆனா எனக்குப் பசிக்குது!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```


### SCENE 10: Night, and the hook (9:55–10:50)
Refs for this scene: **yashoda, krishna_child; silhouettes for Vasudeva, Devaki and Kamsa**

#### 10.1 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Night: Yashoda rocking a wooden cradle, an oil lamp flickering, Kannan sleeping.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Gentle rocking.
Yashoda softly hums a gentle Tamil lullaby tune (humming only, no clear words).
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

*Song: use the lullaby track made with Gemini's music tool (see [GEMINI-ONLY-WORKFLOW.md](GEMINI-ONLY-WORKFLOW.md) Step 6) under this shot.*

#### 10.2 (8 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Close-up: sleeping Kannan; moonlight on his face; the butter pot's silhouette in the sling above.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow push-in.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Yashoda (warm, soft, medium-low voice of a young Tamil mother in her late twenties, softly) says in Tamil: "நீ யாருடா கண்ணா...? யாரா இருந்தாலும்... நீ என் பிள்ளை தான்."
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 8 seconds.
```

#### 10.3 (7 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Exterior: Gokulam asleep under a full moon, the Yamuna shining.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Slow drift.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 7 seconds.
```

**③ Narration (AI Studio TTS)**
```
ஆனா... இந்தக் குழந்தை கோகுலத்துக்கு எப்படி வந்தான்?
```

#### 10.4 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Smash cut: a storm, lightning over the dark fortress city of Mathura.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Lightning flashes.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

**③ Narration (AI Studio TTS)**
```
அந்தக் கதை... ஒரு புயல் இரவுல... ஒரு சிறைச்சாலையில ஆரம்பிச்சது.
```

#### 10.5 (6 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Stone prison cell: silhouettes of a chained couple, a guard slumping asleep.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
Lightning reveals them.
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 6 seconds.
```

#### 10.6 (5 s)

**① First frame** · attach the scene refs
```
Cinematic stylized 3D animation, premium Indian mythological animated feature film quality, semi-realistic proportions, expressive large eyes, soft subsurface skin shading, highly detailed traditional textiles and gold jewellery, painterly warm golden-hour lighting, volumetric light rays, soft atmospheric haze, shallow depth of field, rich saturated but natural colours (saffron, peacock blue, turmeric yellow, leaf green, terracotta), ancient Indian village setting (Gokulam, Dwapara Yuga), horizontal 16:9 cinematic widescreen composition, film grain subtle.

Lightning reveals only Kamsa's eyes and jagged crown.

Avoid: photorealistic live-action look, anime style, cartoonish flat 2D, distorted or melted faces, extra or missing fingers, extra limbs, crossed eyes, asymmetric eyes, changing costume or jewellery, changing skin colour, modern objects, plastic, text, letters, watermark, logo, subtitles in image, blurry face, oversaturated neon colours, horror tone, sexualised depiction, western medieval clothing.
```

**② Video prompt (Flow, Frames to Video, 16:9)**
```
His eyes narrow.
Dialogue, spoken in natural colloquial Tamil with clear Tamil pronunciation and accurate lip-sync, in this order:
- Kamsa (very deep, cold, menacing voice of a 40-year-old king, with hidden fear, off-screen (not visible), voice heard from outside the frame, deep) says in Tamil: "என்னைக் கொல்லப் போறவன்... எங்கேயோ பிறந்துட்டானா?!"
Audio: natural ambient sound and sound effects of the scene only. No background music. No subtitles, captions or on-screen text.
Duration: 5 seconds.
```

#### End (12 s)

End card: make it in the editor (black background, peacock feather, gold title text, series flute motif). No AI generation needed.


---

## Part C: Narrator script for Google AI Studio (all lines, in order)

AI Studio → **Generate speech** → **single speaker**. Choose one voice and never change it. Audition a few strong young male voices, for example **Fenrir**, **Orus**, **Charon** and **Puck**; voice names can change, so pick from what's listed. Paste the style line, then one narration line at a time, and download each as `NARR_<shot>.wav`.

**Style line (paste before each narration line):**
```
Read this in Tamil like a strong, confident young storyteller who grips the audience: deep, charismatic, controlled intensity, with dramatic pauses at the dots.
```

| Shot | Narration |
|---|---|
| Short Shot 2 | கோகுலத்துல ஒரு குட்டித் திருடன் இருக்கான்... அவன் திருடுறது தங்கம் இல்ல... வெண்ணெய்! |
| Short 12a | அந்தச் சின்ன வாய்க்குள்ள... யசோதா என்ன பார்த்தாங்க? |
| Long C4 | இவன் தான் கண்ணன். கோகுலத்துல எல்லாரும் இவனை உயிரா நேசிக்கிறாங்க... |
| Long C5 | ...ஆனா எல்லார் வீட்டு வெண்ணெயும் இவனைக் கண்டாலே பயப்படுது! |
| Long 1.1 | கோகுலத்துல காலை விடியறதே... தயிர் கடையற சத்தத்துல தான். |
| Long 1.10 | யசோதா அம்மா நினைச்சாங்க... பிரச்சனை முடிஞ்சதுன்னு. ஆனா கண்ணனுக்கு... இது ஆரம்பம் தான்! |
| Long 4.11 | கோகுலத்துப் பெண்கள் புகார் சொல்லத்தான் வந்தாங்க... ஆனா உண்மையில, கண்ணனைப் பார்க்கத்தான் வந்தாங்க. |
| Long 6.1 | சாயங்காலம். யமுனைக் கரையில பசங்க விளையாட்டு. |
| Long 8.3 | அந்தச் சின்ன வாய்க்குள்ள... யசோதா பார்த்தது மண் இல்ல... |
| Long 8.4 | ...முழு பிரபஞ்சத்தையும்! வானம்... சூரியன்... சந்திரன்... நட்சத்திரங்கள்... |
| Long 8.5 | ...மலைகள்... கடல்கள்... தீவுகள்... இந்த பூமி முழுசும்... |
| Long 8.6 | ...காற்று... நெருப்பு... மின்னல்... |
| Long 8.7 | ...அதுக்குள்ளேயே... கோகுலம்! |
| Long 8.8 | ...அங்கே, கண்ணன் முன்னாடி மண்டியிட்டு உட்கார்ந்திருக்கிற... அவங்களையே! |
| Long 9.1 | அப்போ கண்ணன் நினைச்சான்... அம்மா என்னைக் கடவுளாப் பார்க்க வேண்டாம். அம்மாவாவே பார்க்கட்டும். |
| Long 9.5 | வேதங்கள் தேடுற இறைவனை... யசோதா தன் மடியில கொஞ்சிக்கிட்டு இருந்தாங்க. |
| Long 10.3 | ஆனா... இந்தக் குழந்தை கோகுலத்துக்கு எப்படி வந்தான்? |
| Long 10.4 | அந்தக் கதை... ஒரு புயல் இரவுல... ஒரு சிறைச்சாலையில ஆரம்பிச்சது. |
