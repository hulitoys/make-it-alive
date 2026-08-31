---
name: make-it-alive
description: Turn one visible object in each of one or more user-provided everyday photos into an original collectible-style 精灵, repaint each same scene with the 精灵 replacing that object in place, and compose every untouched photo beside its bright hand-painted transformation scene. Use when the user asks to make photographed cups, plants, grass, stones, tools, or other visible objects come alive without copying an existing franchise. Select one object per photo automatically unless the user names it. Do not use for generic photo retouching, exact character replication, or multi-creature sheets.
---

# Make It Alive

Create one original 精灵 from one visible everyday object in each input photo. Show every untouched source photo beside a hand-painted version of the same scene in which that object has become the 精灵. Use one image-generation call per input by default. The only deliverable for each input is its finished A+B spread.

## Non-negotiable output contract

- Treat the number of input photos as the required number of final deliverables: one input produces exactly one finished spread; N inputs produce exactly N finished spreads, in the original input order.
- Process every photo independently. Select one object, create one 精灵, and compose one spread for each photo.
- Deliver only finished A+B spreads. Never expose a transformed scene B, identity sheet, sketch, candidate image, contact sheet, or uncomposed generated image as a deliverable.
- Never generate multiple variants for the user to choose from, ask which image they prefer, or pause for aesthetic selection. Make the design decision yourself and continue to composition.
- Every spread must contain the complete untouched source photo A and, on the right, the same-scene illustration B plus a readable name, personality, hobby, and one small unlabelled introduction sentence. Missing any one of these elements means the spread is not deliverable.
- Do not end after image generation. The deterministic composition and final visual check are mandatory even when B already looks polished.

## Inputs

- Require at least one accessible user-supplied scene photo. Ask for a photo if none is available.
- Accept any number of photos in one request. Do not ask the user to reduce the set or select favorites.
- Accept an optional target object for one or more photos. Honor it when visible; otherwise say which photo does not contain it and ask only for the missing target decision.
- Match names and copy to the user's language. Default to Simplified Chinese for Chinese prompts.

## Workflow

1. Build the input list and inspect every photo in order.
   - If it is a local file, inspect it with `view_image` before generation.
   - Never overwrite, crop, retouch, recolor, publish, or commit the source file.
   - The source may be passed to ImageGen to create a new derivative scene, but it must never be written back to the source path.

2. Select exactly one object per photo.
   - Use the user's named object when provided.
   - Otherwise choose without asking. Rank visible non-human objects and plants by silhouette, surface identity, structural detail, and creature-design potential.
   - Record the object's approximate position and scale plus three nearby landmarks that must remain recognizable in the transformed scene.
   - Stop and request a clearer photo if no suitable object is visible.

3. Read [references/art-direction.md](references/art-direction.md). Use its archetype, naming, writing, fast-path prompt, and QA rules.

4. Draft one concept record per photo:

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
   intro: <24-44-character natural, logically coherent introduction sentence>
   ```

   - Run the reference's spoken-naturalness and logical-coherence checks on personality, hobby, and intro. Rewrite any field that sounds unnatural when read aloud or whose subject, action, object, or causal relationship does not make sense.

5. Generate one transformed scene B per photo in one fast-path call each.
   - In Codex, use built-in `image_gen`. On another agent runtime, use its equivalent single-call image-to-image capability only when available. Do not switch to a paid API or CLI without explicit user approval.
   - Pass the source photo as the composition/edit target for a **new derivative output only**. Do not generate a separate identity sheet first.
   - In the same prompt, define one original 精灵 from the archetype and three preserved cues, remove the selected object, and put the 精灵 at its original position, approximate scale, depth, and ground contact.
   - Repaint the complete photo as a bright gouache-and-colored-pencil creature-card illustration. Preserve the camera viewpoint, source aspect ratio, major spatial relationships, and three landmarks.
   - Require exactly one 精灵 and no generated text, frame, property icon, energy symbol, statistics, logo, watermark, or existing character.
   - Request exactly one image from the image tool. If a runtime nevertheless returns variants, choose the strongest valid one yourself and do not show the variants or ask the user to choose.
   - Inspect B once. Accept it immediately when the mandatory checks pass. Make one focused correction only when the source object remains, the 精灵 is in the wrong region, a landmark drifts badly, generated text appears, or the scene is gloomy, glossy, or 3D. Do not spend another generation on minor aesthetic preferences.

6. Compose every final spread. This step cannot be skipped.
   - Resolve the skill directory to an absolute path and quote all arguments:

     ```text
     python <skill-dir>/scripts/compose_make_it_alive.py \
       --photo <source-photo-A> \
       --scene <transformed-scene-B> \
       --name <name> \
       --personality <personality> \
       --hobby <hobby> \
       --intro <small unlabelled introduction sentence> \
       --output output/make-it-alive/<name>-make-it-alive.png
     ```

   - The script applies EXIF display orientation and proportional containment. It never writes to A and never crops or overlays A.
   - The composer uses `assets/fonts/NotoSansCJKsc-Regular.otf` by default and falls back to a system CJK font only if the bundled asset is absent. Do not pause to ask the user to upload or download a font. `--font <path>` remains an optional explicit override.
   - If Pillow is unavailable, report that it is required and ask before installing it. If the bundled font is missing from an incomplete installation and no system fallback exists, ask the user to reinstall the complete Skill rather than fetching a font during the task.

7. Validate and deliver only the finished spread or spreads.
   - Inspect every final spread with `view_image`.
   - Confirm A is complete and unaltered; B matches its viewpoint and landmarks; the selected object is replaced in place; the 精灵 preserves all three cues; the name, personality, hobby, and small introduction are present, exact, readable, natural, and not clipped.
   - Confirm there is no thick black outline, gloomy gray cast, generated text, trademarked imagery, plastic 3D finish, or watermark.
   - Count the finished spread paths before responding. The count must equal the number of input photos; if it does not, finish the missing compositions first.
   - For one input, display exactly one final A+B spread inline. For N inputs, display exactly N final A+B spreads inline in input order.
   - Keep the response minimal: provide the final image or images and their paths. Do not display or link intermediate B images, candidates, or corrections, and do not ask for a preference after delivery.

## Failure Rules

- If built-in image generation is unavailable, offer the API/CLI fallback only as an explicit opt-in that requires an API key.
- If the named object is absent, do not substitute another object silently.
- If generated art contains text or protected brand elements, regenerate instead of covering them.
- If the transformed scene cannot preserve the location after one correction, explain the mismatch rather than claiming exact correspondence.
- If composition fails, preserve all inputs and rerun only the deterministic composition step.
- If any required text field is missing, unnatural when read aloud, logically incoherent, or clipped, fix it and recompose before delivery.

## Speed Target

- Treat 60 seconds as a best-effort fast-path target, not a guaranteed service level; image-tool queue and model latency are outside the Skill's control.
- Use exactly one generation call per input when the first result passes mandatory QA. Concept drafting and deterministic composition should add only a few seconds on a typical local Python environment.
- Request one generated image per input only. When the runtime exposes size controls, use a roughly 1K-class image at the source aspect ratio because B is placed inside a 915×952 region; do not request 2K/4K or multiple variants by default.
- For multiple inputs, parallelize independent generation and composition when the runtime and image tool allow it, then restore the original input order for delivery.
- Use a runtime's fast prompt-optimization mode when available, but never weaken the mandatory placement, no-text, and no-brand constraints.
- Offer a slower two-stage identity-sheet workflow only when the user explicitly prioritizes character consistency over speed.
