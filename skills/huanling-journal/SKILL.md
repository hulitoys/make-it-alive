---
name: huanling-journal
description: Turn a user-provided everyday-scene photo into an original hand-drawn creature journal spread. Use when the user asks to 唤灵, create a 宠兽 or 灵兽 from a photographed cup, plant, grass, stone, tool, or other visible object, or place the untouched source photo beside a colored-pencil-and-watercolor creature card. Select one object automatically unless the user names it. Do not use for generic photo retouching, exact replication of existing characters, or multi-creature sheets.
---

# Huanling Journal

Create one original creature from one visible everyday object, then compose the source photo and creature record as an open field-journal spread. Keep the source file untouched and keep all card text out of the generated artwork.

## Inputs

- Require one user-supplied scene photo. If none is attached or accessible, ask the user to attach it.
- Accept an optional target object. Honor it when it is visible; otherwise explain that it cannot be found and ask for another choice.
- Match names and descriptive text to the user's language. Default to Simplified Chinese for Chinese prompts.

## Workflow

1. Inspect the photo.
   - Treat it as a **reference image**, never as an edit target.
   - If it is a local file, inspect it with `view_image` before generation.
   - Do not overwrite, crop, retouch, recolor, or commit the source photo.

2. Select exactly one object.
   - Use the user's named object when provided.
   - Otherwise choose without asking for confirmation. Rank visible non-human objects and plants by silhouette clarity, distinctive color or material, structural detail, and creature-design potential.
   - Prefer a clear object over a large but visually generic region. Do not infer sensitive traits about people in the scene.
   - If no suitable object is visible, stop and ask for a clearer photo.

3. Read [references/art-direction.md](references/art-direction.md). Use its archetype rules, writing limits, prompt template, and QA checklist.

4. Draft a compact concept record before generating:

   ```text
   selected_object: <one visible object>
   preserved_cues: [<silhouette>, <color/material>, <structural detail>]
   archetype: <gentle|nimble|fierce|evolved-guardian>
   name: <2-5 Chinese characters, or a similarly compact localized name>
   personality: <2-6 Chinese characters>
   hobby: <4-10 Chinese characters>
   lore: <one original behavioral sentence, normally 24-44 Chinese characters>
   ```

5. Generate only the creature artwork.
   - Use the built-in `image_gen` tool in `stylized-concept` mode. Do not switch to an API or CLI fallback unless the user explicitly requests it.
   - Pass the photo as a reference image and state that it is not an edit target. Use the smallest recent-image count that includes it when it has no local path.
   - Ask for a square, full-body or nearly full-body three-quarter creature portrait on warm, lightly textured blank sketchbook paper.
   - Preserve all three recorded cues while transforming the object into a coherent living creature rather than merely adding eyes and limbs.
   - Require no letters, words, numbers, logos, card borders, type icons, watermarks, or existing franchise elements. The compositor adds all text later.
   - Inspect the result. If a major cue is missing, the style is glossy or 3D, or any text appears, make one targeted correction and re-check.

6. Save the deliverables non-destructively.
   - Create `output/huanling-journal/` in the user's current project.
   - Copy the selected generated artwork to `<name>-creature.png`, using `-v2`, `-v3`, and so on when needed.
   - Compose the journal with the bundled script. Resolve the skill directory to an absolute path and quote every path and text argument:

     ```text
     python <skill-dir>/scripts/compose_journal.py \
       --photo <source-photo> \
       --creature <saved-creature-art> \
       --name <name> \
       --personality <personality> \
       --hobby <hobby> \
       --lore <lore> \
       --output output/huanling-journal/<name>-journal.png
     ```

   - The script reads the photo, applies EXIF display orientation, scales it proportionally without cropping, and never writes to the source path.
   - If Pillow is unavailable, report that `Pillow` is required and ask before installing it. Do not skip the final composition.
   - If no CJK font is found, ask for a font path and rerun with `--font <path>`.

7. Validate the final spread with `view_image`.
   - Confirm that the whole source composition is visible, with no crop or overlay.
   - Confirm that the creature occupies the right-page art area and remains recognizable from the three cues.
   - Confirm that the name, personality, hobby, and lore are exact and readable.
   - Confirm that there is no generated text, trademarked imagery, plastic 3D finish, or watermark.

8. Deliver both paths.
   - Return the saved creature artwork path and final journal path.
   - Briefly state the selected object, archetype, three preserved cues, and whether a corrective generation pass was needed.
   - Never publish or commit the user's photo or generated output unless the user explicitly asks.

## Failure Rules

- If built-in image generation is unavailable, say so and offer the API/CLI fallback only as an explicit opt-in that requires an API key.
- If the named object is absent, do not silently substitute another object.
- If the generated image contains text, regenerate the artwork rather than trying to cover it.
- If the compositor fails, preserve both input files, report the exact error, and fix or rerun only the composition step.
