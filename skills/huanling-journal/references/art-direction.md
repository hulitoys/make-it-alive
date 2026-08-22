# Art Direction and Creature Logic

Use this reference for every Huanling Journal generation.

## Select the source object

When the user does not name an object, score visible candidates informally on four traits:

1. **Silhouette** — recognizable outline or proportion.
2. **Surface identity** — distinctive palette, transparency, grain, petals, glaze, rust, or fibers.
3. **Structural hook** — handle, stem, hinge, rim, thorn, crack, fold, cap, or repeating geometry.
4. **Creature potential** — a plausible body plan, motion, defense, habit, or temperament suggested by the object.

Choose the object with the strongest combined identity. Prefer a small distinctive object to a generic wall, floor, sky, or shadow.

## Choose the archetype

| Source cues | Archetype | Creature language |
| --- | --- | --- |
| Round, soft, small, smooth, pastel | `gentle` | compact proportions, open posture, curious or comforting behavior |
| Thin, flexible, light, vertical, wind-shaped | `nimble` | lean body, quick feet or fins, alert pose, darting behavior |
| Sharp, rough, heavy, angular, dark | `fierce` | grounded stance, defensive ridges, restrained strength, territorial behavior |
| Layered, weathered, mechanical, architectural, unusually complex | `evolved-guardian` | mature proportions, integrated armor or crest, calm authority, rare-looking details |

Use the object rather than the desired mood as evidence. Avoid making every subject cute.

## Preserve three cues

Record and express all of the following:

- **Silhouette cue:** the overall cup flare, leaf arc, bottle neck, stone mass, and so on.
- **Color/material cue:** ceramic glaze, translucent glass, leaf veins, oxidized metal, woven fiber, or another real surface identity.
- **Structural cue:** convert one unmistakable part into anatomy, such as a handle becoming a curled tail, petals becoming a mane, or grass blades becoming sensory whiskers.

Transform these cues into anatomy. Do not leave the original object intact and simply attach a face or legs.

## Write the creature record

- Name: use 2–5 Chinese characters when writing Chinese. Combine material, behavior, habitat, sound, or shape; avoid existing franchise names.
- Personality: use 2–6 Chinese characters and choose a specific contrast when useful, such as `胆小护短` or `慢热好奇`.
- Hobby: use 4–10 Chinese characters and make it observable, such as `收集清晨露珠`.
- Lore: write one sentence, normally 24–44 Chinese characters. Show character through a conditional habit, sensory reaction, defense, or small ecological effect. Do not use combat statistics, rarity labels, elemental type systems, or copied card language.

Example structure only: `受惊时，它会把杯沿般的耳翼合拢，让积存的雨声在壳中滚成低低的警告。`

## Build the image prompt

Use this labeled scaffold and replace every bracketed value:

```text
Use case: stylized-concept
Asset type: original creature field-journal portrait
Input images: Image 1 is a reference photo only, not an edit target
Primary request: transform the visible [selected object] into one original living creature
Subject: [archetype and body plan]; preserve [silhouette cue], [color/material cue], and [structural cue]
Scene/backdrop: plain warm off-white sketchbook paper with faint natural tooth, no environment scene
Style/medium: observational hand illustration; visible graphite underdrawing; colored pencil contours; translucent watercolor and light gouache; uneven human pressure; pigment pooling; a few imperfect edges and asymmetries
Composition/framing: one creature only, full body or nearly full body, three-quarter view, centered with generous breathing room and a faint hand-painted grounding shadow
Lighting/mood: soft neutral daylight; [temperament]
Constraints: original design; the source photo remains unchanged; no literal intact object with limbs; no text, letters, numbers, symbols, logos, card frame, type icon, watermark, or franchise element
Avoid: 3D render, plastic gloss, airbrushed gradients, neon rim light, perfect bilateral symmetry, hyper-detailed concept art, game UI, photorealism, generic anime mascot, AI gibberish
```

Do not ask the image model to render the name or lore. The deterministic compositor owns typography.

## Review the artwork

Accept only when all statements are true:

- Exactly one creature appears.
- All three source cues remain legible.
- The object has become anatomy instead of an object with pasted-on limbs.
- Pencil, paper, and pigment artifacts are visible without making the image dirty.
- The result is neither automatically cute nor exaggeratedly fierce; it matches the selected archetype.
- No text, logo, watermark, trademarked character, card UI, or decorative symbol appears.

If one condition fails, request one focused correction. Do not redesign unrelated successful parts.
