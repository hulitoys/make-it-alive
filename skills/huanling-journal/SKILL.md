---
name: huanling-journal
description: Turn one visible object in a user-provided everyday photo into an original collectible-style 精灵, repaint the same scene with the 精灵 replacing that object in place, and compose the untouched photo beside the bright hand-painted transformation scene. Use when the user asks to 唤灵, create a 精灵 from a photographed cup, plant, grass, stone, tool, or other visible object, or make an original creature-card-like scene without copying any existing franchise. Select one object automatically unless the user names it. Do not use for generic photo retouching, exact character replication, or multi-creature sheets.
---

# Huanling Journal

Create one original 精灵 from one visible everyday object. Show the untouched source photo beside a hand-painted version of the same scene in which that object has become the 精灵. Generate intermediate art only to keep the design consistent; deliver one final A+B image.

## Inputs

- Require one accessible user-supplied scene photo. Ask for one if none is available.
- Accept an optional target object. Honor it when visible; otherwise say it cannot be found and ask for another choice.
- Match names and copy to the user's language. Default to Simplified Chinese for Chinese prompts.

## Workflow

1. Inspect the photo.
   - If it is a local file, inspect it with `view_image` before generation.
   - Never overwrite, crop, retouch, recolor, publish, or commit the source file.
   - The source may be passed to ImageGen to create a new derivative scene, but it must never be written back to the source path.

2. Select exactly one object.
   - Use the user's named object when provided.
   - Otherwise choose without asking. Rank visible non-human objects and plants by silhouette, surface identity, structural detail, and creature-design potential.
   - Record the object's approximate position and scale plus three nearby landmarks that must remain recognizable in the transformed scene.
   - Stop and request a clearer photo if no suitable object is visible.

3. Read [references/art-direction.md](references/art-direction.md). Use its archetype, naming, writing, two-stage prompt, and QA rules.

4. Draft the concept record:

   ```text
   selected_object: <one visible object>
   source_region: <relative position and scale>
   scene_landmarks: [<nearby landmark 1>, <landmark 2>, <landmark 3>]
   preserved_cues: [<silhouette>, <color/material>, <structural detail>]
   archetype: <gentle|nimble|fierce|evolved-guardian>
   name_candidates: [<five original names>]
   name: <selected 2-4-character Chinese name, or compact localized name>
   personality: <2-6 Chinese characters>
   hobby: <4-10 Chinese characters>
   lore: <one original behavioral sentence, normally 24-44 Chinese characters>
   ```

5. Generate a temporary, text-free 精灵 design.
   - Use built-in `image_gen` in `stylized-concept` mode. Do not switch to API or CLI unless the user explicitly requests it.
   - Pass the photo as a reference image, not an edit target for this stage.
   - Generate exactly one full-body 精灵 on a simple light background. Preserve all three cues as simplified anatomy with a clear silhouette, expressive face, and collectible companion character language.
   - Use bright gouache and colored pencil with no thick black outline. Require no text, numbers, logos, card UI, watermark, or existing franchise element.
   - Inspect the result and make one focused correction if a cue is missing, the design is too realistic or gloomy, or forbidden content appears.

6. Generate the transformed scene B.
   - Use built-in `image_gen` with the source photo as Image 1, the composition/edit target for a **new derivative output only**, and the temporary 精灵 design as Image 2, a supporting identity reference.
   - Repaint the complete photo as a bright gouache-and-colored-pencil creature-card illustration. Preserve the camera viewpoint, major spatial relationships, source aspect ratio, and the three recorded landmarks.
   - Remove the selected object and place the same 精灵 at its original position, approximate scale, depth, and ground contact. Keep exactly one 精灵 and make it the visual focus without turning the location into a different place.
   - Require no generated text, frame, property icon, energy symbol, statistics, logo, watermark, or existing character.
   - Inspect B. Correct once if the original object remains, the 精灵 moves to the wrong area, the landmarks drift, the design identity changes, or the scene becomes gray, gloomy, glossy, or 3D.

7. Compose one final image.
   - Do not copy the intermediate design into the project or present intermediate images as deliverables.
   - Resolve the skill directory to an absolute path and quote all arguments:

     ```text
     python <skill-dir>/scripts/compose_journal.py \
       --photo <source-photo-A> \
       --scene <transformed-scene-B> \
       --name <name> \
       --personality <personality> \
       --hobby <hobby> \
       --lore <lore> \
       --output output/huanling-journal/<name>-journal.png
     ```

   - The script applies EXIF display orientation and proportional containment. It never writes to A and never crops or overlays A.
   - If Pillow is unavailable, report that it is required and ask before installing it. If no CJK font is found, request a font path and rerun with `--font <path>`.

8. Validate and deliver.
   - Inspect the final spread with `view_image`.
   - Confirm A is complete and unaltered; B matches its viewpoint and landmarks; the selected object is replaced in place; the 精灵 matches its temporary design; all deterministic text is exact and readable.
   - Confirm there is no thick black outline, gloomy gray cast, generated text, trademarked imagery, plastic 3D finish, or watermark.
   - Display the final A+B image inline and return only its path. Briefly state the selected object, final name, archetype, three cues, and whether correction was needed.

## Failure Rules

- If built-in image generation is unavailable, offer the API/CLI fallback only as an explicit opt-in that requires an API key.
- If the named object is absent, do not substitute another object silently.
- If generated art contains text or protected brand elements, regenerate instead of covering them.
- If the transformed scene cannot preserve the location after one correction, explain the mismatch rather than claiming exact correspondence.
- If composition fails, preserve all inputs and rerun only the deterministic composition step.
