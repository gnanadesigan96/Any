# Aura Grand Stay — Happy Diwali Poster
## Photorealistic production brief

**Why this brief exists:** the session that produced it has no native image generation.
The two HTML/SVG posters in this folder are illustrations and are **not** the intended final look.
Use the prompts below in a photorealistic image engine (e.g. Midjourney v6+, GPT-Image / ChatGPT,
Google Imagen / Gemini, Adobe Firefly Image 3, Ideogram), then add the typography from Part 3.

**Recommended workflow (best quality, no misspelled names):**
1. Generate the **background plate (Prompt A)** — no text in the image.
2. Upscale to at least 2160 × 2700 px.
3. Set the typography in Canva / Photoshop / Figma using **Part 3**.

Use **Prompt B** only if you want a one-shot result from an engine that renders text well
(GPT-Image, Ideogram, Imagen). Check every letter of "Alwarappan" and "Aura Grand Stay" before sending.

---

## Part 1 — Prompt A: background plate (no text) — RECOMMENDED

**Aspect ratio:** 4:5 portrait (1080 × 1350 / 2160 × 2700)

```
Premium photorealistic commercial advertising photograph for a luxury service apartment's Diwali campaign, shot at blue hour on the open-air pool terrace of a modern upscale residential building in Madurai, Tamil Nadu, India.

Composition (4:5 portrait): symmetrical, eye-level, centred vanishing point. The upper-centre 55% of the frame is clean, uncluttered deep indigo-to-violet evening sky with soft, even gradation, kept free of objects as negative space for headline typography. Far in the distance, small and softly out of focus on the horizon, the silhouette of a South Indian Dravidian temple gopuram glows with warm festival lights.

Left side: a contemporary 6-storey residential building in warm beige stone and glass, balconies lined with warm white string lights and small clay diyas, interior windows glowing 2700K tungsten, realistic architecture, accurate perspective, no distortion.
Right side: a tall carved brass-and-teak jaali screen panel backlit by warm light, casting delicate patterned shadows on a cream stone wall.
Top corners: rich maroon silk drapes softly framing the scene; brass Moroccan-style pierced hanging lanterns glowing from inside, casting starry light patterns.

Midground: a long infinity pool reflecting the violet sky, lined along its edge with a row of lit terracotta and brass diyas whose flames reflect as long golden streaks on the water and on polished stone. Real Diwali fireworks bursting in the distant sky — fine, sparse, natural golden and magenta sparks, long-exposure trails, not oversaturated, placed only near the upper left and upper right edges.

Foreground (bottom 30%): a low round teak coffee table with a polished surface reflecting candlelight, holding two tall brass lanterns with intricate cutwork, a hammered brass urli bowl filled with fresh orange and yellow marigolds, several lit clay diyas, a gold-wrapped gift box with satin ribbon. Bottom right: a vibrant traditional rangoli made of coloured powder and fresh flower petals on the stone floor with lit diyas around it. Bottom left: out-of-focus marigold and jasmine garlands in the extreme foreground creating soft bokeh.

Lighting: natural blue-hour ambient sky light mixed with warm practical light from diyas, lanterns and windows (2200K–2700K). Realistic falloff, soft contact shadows, physically accurate reflections on water, brass and polished stone, subtle atmospheric haze catching the light, gentle bloom on flames only.

Camera: full-frame DSLR, 35mm lens, f/4, ISO 800, tripod, sharp focus throughout midground, shallow foreground bokeh. Colour grade: luxury hospitality advertising — rich indigo and violet shadows, warm gold and amber highlights, deep maroon accents, high dynamic range, natural skin of materials, no oversaturation.

Style references: Taj Hotels / Oberoi / Four Seasons festive campaign photography, Architectural Digest India editorial, cinematic, ultra-detailed, 8K, photographic realism.

No text, no letters, no logos, no watermarks, no people.
```

**Negative prompt** (for engines that support it, e.g. Stable Diffusion, Firefly, Leonardo):

```
text, letters, words, typography, logo, watermark, signature, people, faces, hands, cartoon, illustration, vector art, flat design, 3D render look, CGI, plastic materials, clip art, anime, painting, oversaturated colours, neon, cheap fireworks, lens flare overload, warped architecture, distorted perspective, duplicated lanterns, floating objects, melted candles, extra flames, low resolution, noise, blur on midground, HDR halos
```

**Midjourney suffix:** `--ar 4:5 --style raw --stylize 150 --v 6.1` (add `--no text, letters, logo, people, cartoon, illustration`)

---

## Part 2 — Prompt B: one-shot with text (only for text-capable engines)

```
[Paste all of Prompt A, but delete the line "No text, no letters, no logos, no watermarks, no people." and add:]

Integrated luxury typography, rendered cleanly and spelled exactly as written:
• Top centre: a minimal gold line-art house-roof icon above the wordmark "Aura Grand Stay" in an elegant high-contrast serif — "Aura Grand" in ivory white, "Stay" in polished brushed gold; beneath it, small tracked-out capitals "SERVICE APARTMENT" between two thin gold rules.
• Below: a slim gold-outlined capsule badge with a location-pin icon and "MADURAI" in gold serif capitals.
• Centre: "Wishes you a" in ivory italic serif, then "Happy Diwali" in large flowing gold calligraphic script with a real metallic gold-leaf texture and soft warm glow, framed by a delicate thin gold half-mandala arch topped by a single lit diya.
• Under the headline, in ivory serif, centred, four lines: "May the festival of lights / bring peace, prosperity, good health, / and lasting happiness to you / and your loved ones."
• Bottom centre, overlapping the foreground table: an ornate deep-maroon velvet plaque with an embossed gold filigree border reading "From" (small gold italic) and "Alwarappan" (large gold italic serif).
All text sharp, legible, correctly spelled, no extra words.
```

---

## Part 3 — Typography & branding layout specification

**Canvas:** 2160 × 2700 px (4:5), RGB, sRGB. Safe margin 120 px on all sides.
Positions are given as the **vertical centre of each element, as % of canvas height**, all horizontally centred.

| # | Element | Text (exact) | Typeface | Size @2160w | Colour / finish | Y-centre |
|---|---------|--------------|----------|-------------|-----------------|----------|
| 1 | Roof icon | — (line icon, 4-pane window) | — | 360 px wide, 6 px stroke | Gold gradient | 5.5% |
| 2 | Wordmark | **Aura Grand** *Stay* | Playfair Display Bold (alt: Bodoni Moda, Didot) | 150 px | "Aura Grand" #FFF8EC; "Stay" gold gradient | 10.5% |
| 3 | Descriptor | SERVICE APARTMENT | Cinzel SemiBold, tracking +600 | 38 px | #F4E4C0, with 120 px gold rules each side | 14% |
| 4 | Location badge | 📍 MADURAI | Cinzel Bold, tracking +200 | 56 px | Gold text; capsule 680×100 px, 5 px gold stroke, fill #140A28 @ 70% | 20% |
| 5 | Lead-in | Wishes you a | Cormorant Garamond Bold Italic | 76 px | #FFF3DA | 30% |
| 6 | Headline 1 | Happy | Great Vibes (alt: Pinyon Script, Bickham Script Pro) | 230 px | Gold foil + glow | 36% |
| 7 | Headline 2 | Diwali | Great Vibes / Bickham Script Pro | 420 px | Gold foil + glow | 45% |
| 8 | Message | May the festival of lights / bring peace, prosperity, good health, / and lasting happiness to you / and your loved ones. | Cormorant Garamond Bold | 58 px, line-height 1.3 | #FFF6E4, shadow 0 4 16 rgba(0,0,0,.8) | 57% |
| 9 | Divider | — (lotus ornament + rules) | — | 640 px wide | Gold | 64% |
| 10 | Plaque label | From | Cormorant Garamond Bold Italic | 64 px | Gold | 86% |
| 11 | Plaque name | Alwarappan | Cormorant Garamond Bold Italic (alt: Playfair Display Italic) | 124 px | Gold foil | 90% |

**Plaque:** 1200 × 260 px, centred at 89%, fill #6A0E2A → #3A0618 vertical gradient, 8 px gold filigree border, pointed side finials, small lotus crest top and bottom.

**Gold foil treatment (Photoshop / Figma):**
- Gradient fill (top → bottom): #FFF7D6 0% · #FFD968 38% · #E8A52A 62% · #FFF0B0 82% · #C7861F 100%
- Bevel & Emboss: inner bevel, depth 60%, size 4 px, soft
- Outer glow: #FFB84A, 25% opacity, 30 px (headline only)
- Drop shadow: #000, 50%, distance 6 px, size 10 px

**Brand palette**

| Role | Hex |
|------|-----|
| Night indigo | #0B0A26 |
| Violet sky | #3F2366 |
| Maroon | #6A0E2A |
| Antique gold | #C7861F |
| Bright gold | #FFD968 |
| Ivory | #FFF8EC |

**Readability rules**
- Add a soft radial darkening (#120626, 40–55% opacity, feather 300 px) behind items 5–8 if the sky is busy.
- Do not place type over fireworks or lantern hotspots; move or mask them instead.
- Keep at least a 4.5:1 contrast ratio between body text and background.

**Exports**
- WhatsApp / Instagram feed: 1080 × 1350 JPG, quality 90
- WhatsApp status / Stories: 1080 × 1920 (extend the sky up and the floor down; same type stack, shifted down by 285 px)
- Print (A4 / A3): re-generate the plate at the highest available resolution, upscale with Topaz or Magnific, 300 dpi, CMYK

**Final proof-read checklist:** Aura Grand Stay · SERVICE APARTMENT · MADURAI · Happy Diwali · Alwarappan
