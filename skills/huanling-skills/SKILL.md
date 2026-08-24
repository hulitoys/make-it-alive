---
name: huanling-skills
description: Turn one visible object in a user-provided everyday photo into an original collectible-style 精灵, repaint the same scene with the 精灵 replacing that object in place, and compose the untouched photo beside the bright hand-painted transformation scene. Use when the user asks for Huanling, creates a 精灵 from a photographed cup, plant, grass, stone, tool, or other visible object, or requests an original creature-card-like scene without copying any existing franchise. Select one object automatically unless the user names it. Do not use for generic photo retouching, exact character replication, or multi-creature sheets.
---

# Huanling Skills

Create one original 精灵 from one visible everyday object. Show the untouched source photo beside a hand-painted version of the same scene in which that object has become the 精灵. Use one image-generation call by default and deliver one final A+B image.

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

3. Read [references/art-direction.md](references/art-direction.md). Use its archetype, naming, writing, fast-path prompt, and QA rules.

4. Draft the concept record:

   ```text
   selected_object: <one visible object>
   source_region: <relative position and scale>
   scene_landmarks: [<nearby landmark 1>, <landmark 2>, <landmark 3>]
   preserved_cues: [<silhouette>, <color/material>, <structural detail>]
   archetype: <gentle|nimble|fierce|evolved-guardian>
   name_candidates: [<five original names>]
   name: <selected 2-4-character Chinese name, or compact localized name>
   personality: <2-6 plain Chinese characters>
   hobby: <4-10-character observable verb-object activity>
   ```

   - Run the reference's literal-paraphrase and read-aloud checks on both fields. Rewrite any field that depends on an unexplained metaphor or describes an action an observer could not actually see.

5. Generate transformed scene B in one fast-path call.
   - In Codex, use built-in `image_gen`. On another agent runtime, use its equivalent single-call image-to-image capability only when available. Do not switch to a paid API or CLI without explicit user approval.
   - Pass the source photo as the composition/edit target for a **new derivative output only**. Do not generate a separate identity sheet first.
   - In the same prompt, define one original 精灵 from the archetype and three preserved cues, remove the selected object, and put the 精灵 at its original position, approximate scale, depth, and ground contact.
   - Repaint the complete photo as a bright gouache-and-colored-pencil creature-card illustration. Preserve the camera viewpoint, source aspect ratio, major spatial relationships, and three landmarks.
   - Require exactly one 精灵 and no generated text, frame, property icon, energy symbol, statistics, logo, watermark, or existing character.
   - Inspect B once. Accept it immediately when the mandatory checks pass. Make one focused correction only when the source object remains, the 精灵 is in the wrong region, a landmark drifts badly, generated text appears, or the scene is gloomy, glossy, or 3D. Do not spend another generation on minor aesthetic preferences.

6. Compose one final image.
   - Resolve the skill directory to an absolute path and quote all arguments:

     ```text
     python <skill-dir>/scripts/compose_huanling.py \
       --photo <source-photo-A> \
       --scene <transformed-scene-B> \
       --name <name> \
       --personality <personality> \
       --hobby <hobby> \
       --output output/huanling-skills/<name>-huanling.png
     ```

   - The script applies EXIF display orientation and proportional containment. It never writes to A and never crops or overlays A.
   - If Pillow is unavailable, report that it is required and ask before installing it. If no CJK font is found, request a font path and rerun with `--font <path>`.

7. Validate and deliver.
   - Inspect the final spread with `view_image`.
   - Confirm A is complete and unaltered; B matches its viewpoint and landmarks; the selected object is replaced in place; the 精灵 preserves all three cues; the name, personality, and hobby are exact, readable, and natural.
   - Confirm there is no thick black outline, gloomy gray cast, generated text, trademarked imagery, plastic 3D finish, or watermark.
   - Display the final A+B image inline and return only its path. Briefly state the selected object, final name, archetype, three cues, and whether correction was needed.

## Failure Rules

- If built-in image generation is unavailable, offer the API/CLI fallback only as an explicit opt-in that requires an API key.
- If the named object is absent, do not substitute another object silently.
- If generated art contains text or protected brand elements, regenerate instead of covering them.
- If the transformed scene cannot preserve the location after one correction, explain the mismatch rather than claiming exact correspondence.
- If composition fails, preserve all inputs and rerun only the deterministic composition step.

## Speed Target

- Treat 60 seconds as a best-effort fast-path target, not a guaranteed service level; image-tool queue and model latency are outside the Skill's control.
- Use exactly one generation call when the first result passes mandatory QA. Concept drafting and deterministic composition should add only a few seconds on a typical local Python environment.
- Request one output only. When the runtime exposes size controls, use a roughly 1K-class image at the source aspect ratio because B is placed inside a 915×952 region; do not request 2K/4K or multiple variants by default.
- Use a runtime's fast prompt-optimization mode when available, but never weaken the mandatory placement, no-text, and no-brand constraints.
- Offer a slower two-stage identity-sheet workflow only when the user explicitly prioritizes character consistency over speed.
