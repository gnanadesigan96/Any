# Image prompt template (keeps every scene looking like the same film)

For each scene, paste into your image tool:

    <style from story.json>. <character from story.json>. Scene: <image_prompt of the scene>

Settings:
- Aspect ratio **9:16** (vertical), at least 1080×1920.
- Use the tool's **character / style reference** feature with your best Krishna image as the
  reference, so his face, crown and clothes stay the same across scenes and episodes.
  Make one "hero" Krishna reference image once and reuse it forever; it becomes your
  channel's recognisable look.
- Save as `episodes/NN-name/images/scene01.png`, `scene02.png`, ... in scene order.

For real animation (recommended for the 2-3 key moments, e.g. the mountain lift):
feed the still into an image-to-video tool, ask for 5 s of subtle motion
("rain falling, cloth and hair moving in wind, slow camera push-in, Krishna smiles"),
and save the result as `sceneNN.mp4`. A clip beats the still for that scene automatically.
