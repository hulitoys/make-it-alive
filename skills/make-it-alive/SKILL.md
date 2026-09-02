---
name: make-it-alive
description: Turn one visible object in each user-provided everyday photo into an original anime-style 精灵 in the same scene, then deliver only a text-free before-and-after composite. Use for making photographed objects, plants, stones, tools, or other visible scene elements come alive. Landscape inputs are stacked original-over-transformation; portrait inputs are placed original-left and transformation-right.
---

# Make It Alive

Turn one object in each input photo into an original anime-style 精灵 while keeping the place recognizably the same. The only deliverable is a clean, text-free composite of the complete source photo and the transformed scene.

## Output contract

- One input photo produces exactly one final composite. N photos produce exactly N composites in input order.
- Deliver only the finished composite. Do not show a standalone generated scene, sketch, identity sheet, candidate, or contact sheet.
- Do not generate variants or ask the user to choose. Select the strongest valid result and finish the composition.
- Add no words anywhere: no name, personality, hobby, description, title, labels, numbers, logo, watermark, or generated lettering.
- For a landscape source, place the complete original on top and the transformed scene below.
- For a portrait source, place the complete original on the left and the transformed scene on the right.
- Treat a square source as portrait for layout purposes: original left, transformed scene right.
- Keep both image panels equally sized. A narrow neutral divider is allowed; decorative card frames and information panels are not.

## Workflow

1. Inspect every source photo.
   - Use `view_image` for accessible local files.
   - Never overwrite, retouch, crop, publish, or commit the source file.
   - If the user names a visible target object, use it. Otherwise choose one object automatically based on silhouette, material identity, structural detail, and transformation potential.

2. Record the target's approximate position, scale, three nearby landmarks, and three cues to preserve:
   - dominant silhouette;
   - main color or material;
   - one unmistakable structural detail.

3. Read [references/art-direction.md](references/art-direction.md), then generate one transformed scene per source.
   - Use built-in `image_gen`, or the runtime's equivalent image-to-image tool, with the source photo as the composition reference for a new derivative output only.
   - Repaint the complete location as a bright 2D anime scene and replace the selected object in its original position with exactly one original 精灵.
   - Preserve the source viewpoint, aspect ratio, foreground/middle/background relationships, lighting logic, target scale, ground contact, and the three landmarks.
   - Preserve all three source-object cues in simplified anatomy, an expressive face, and a clear animated silhouette.
   - Require no text, symbols, card frame, statistics, brand elements, existing characters, or watermark.
   - Request one image only. Make one focused correction only for a mandatory failure such as the original object remaining, wrong placement, changed location, duplicate creature, text, or obvious 3D rendering.

4. Compose the final image with the shipped deterministic script:

   ```text
   python <skill-dir>/scripts/compose_make_it_alive.py \
     --photo <source-photo> \
     --scene <text-free-anime-scene> \
     --output output/make-it-alive/make-it-alive.png
   ```

   - The script applies EXIF display orientation and never writes to the source.
   - It chooses top/bottom for landscape and left/right for portrait or square.
   - It proportionally scales the complete source. If the generated scene has a slightly different aspect ratio, it uses a subordinate blurred extension behind a complete sharp scene rather than leaving empty bands.
   - The script adds no text and has no font dependency.
   - Existing outputs are protected with versioned filenames.

5. Inspect every final composite with `view_image` before delivery.
   - Confirm the source is complete and first in reading order.
   - Confirm the second panel is the same scene in bright anime form, with the object replaced in place by exactly one original 精灵.
   - Confirm the viewpoint, landmarks, three object cues, orientation rule, and equal panel sizes.
   - Confirm there is no text, card UI, brand imagery, existing character, photorealistic monster, plastic 3D finish, or watermark.
   - Deliver exactly one final composite per input and do not expose intermediates.

## Failure rules

- If no suitable object is visible, request a clearer photo.
- If a named object is absent, ask for a different target rather than silently substituting one.
- If image generation is unavailable, explain that the transformation cannot be completed. Do not silently switch to a paid API or CLI.
- If Pillow is unavailable, report that it is required and ask before installing it.
- If composition fails, preserve the generated scene and rerun only the deterministic composition step.

## Speed target

- Use one roughly 1K-class generation per input by default and avoid multiple candidates.
- Treat one minute per image as a best-effort target; image-model queue time remains outside the Skill's control.
- Process independent multiple inputs in parallel when the runtime supports it, then restore input order for delivery.
