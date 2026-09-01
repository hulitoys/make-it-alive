# Art Direction and 精灵 Logic

Use this reference for every Make It Alive generation.

## Select and locate the source object

Score candidates on silhouette, surface identity, structural hook, and creature potential. Prefer a distinctive object to generic sky, floor, wall, or shadow. Record:

- Its relative region, such as `left foreground, about one third of image height`.
- Its approximate scale relative to the frame.
- Three nearby landmarks that make correspondence between A and B verifiable.

## Choose the archetype

| Source cues | Archetype | 精灵 language |
| --- | --- | --- |
| Round, soft, small, smooth, pastel | `gentle` | compact proportions, open posture, curious or comforting behavior |
| Thin, flexible, light, vertical, wind-shaped | `nimble` | lean body, quick feet or fins, alert pose, darting behavior |
| Sharp, rough, heavy, angular, dark | `fierce` | grounded stance, defensive ridges, restrained strength, territorial behavior |
| Layered, weathered, mechanical, architectural, unusually complex | `evolved-guardian` | mature but simplified proportions, a clear crest or integrated protection, calm authority |

Base the archetype on the object. Do not make every subject cute, and do not turn fierce or evolved subjects into realistic monsters.

## Preserve three cues

- **Silhouette:** preserve the cup flare, leaf arc, bottle neck, stone mass, branching crown, or another dominant outline.
- **Color/material:** preserve glaze, glass, veins, rust, bark, fiber, petals, or another real surface identity as a simplified palette and texture.
- **Structure:** turn one unmistakable part into anatomy, such as a handle becoming a tail, petals becoming a mane, or branches becoming sensory fins.

Transform cues into coherent anatomy. Simplify aggressively enough to produce a readable collectible companion silhouette. Never leave the literal object intact and merely add eyes and limbs.

## Name the 精灵

For Chinese output:

1. Extract roots from shape, material, motion, sound, habitat, and temperament.
2. Generate exactly five 2-4-character candidates using different combinations of those roots.
3. Reject automatic names ending in `兽` or `精灵`, exact names of recognizable existing characters, brand names, and near-copies that differ by only one character.
4. Prefer the candidate with the strongest rhythm, memorability, temperament fit, and traceable connection to the object.
5. Honor a user-supplied name even when it does not follow the automatic naming pattern.

Good pattern examples are `苔角`, `茶咕`, `巡梢`, and `露芽`; treat them as structural examples, not reserved outputs.

## Write the record

- **Personality:** use 2-6 plain Chinese characters that a person would naturally use to describe temperament. Do not invent poetic labels that need explanation.
- **Hobby:** use 4-10 Chinese characters as a concrete, repeatable verb-object activity that an observer could actually see. Avoid vague or decorative metaphors.
- **Introduction:** write one original 24-44-character Chinese sentence. It must describe a coherent habit or reaction that reveals personality through visible behavior. Write ordinary natural Chinese, not pseudo-poetic setting copy. The final layout shows this sentence as small text without an `观察记录`, `简介`, or other heading.

Use these checks before accepting personality, hobby, or introduction:

1. **Spoken naturalness:** read it aloud once. It should sound like ordinary, fluent Chinese without forced wording, unexplained metaphor, or ambiguity.
2. **Logical coherence:** the subject, action, object, and causal relationship must fit together. An ordinary reader should understand what happens without inventing a missing premise or correcting a category mistake.

If either check fails, rewrite the field in simpler, more direct language before composition.

## Visual language

Aim for the environmental storytelling and strong focal hierarchy of a collectible creature-card illustration, not its branded card frame.

- **Character design:** clear animated silhouette, readable facial expression, simplified anatomy, appealing companion proportions appropriate to the archetype.
- **Medium:** bright opaque gouache with colored-pencil construction, accents, and hatching on visible paper tooth.
- **Edges:** no thick black outline. Separate forms with dark colored pencil, adjacent color contrast, and simple light-shadow groups.
- **Color:** luminous scene color, soft environmental hues, and a few saturated focal accents. Preserve dark source materials without allowing gray-brown to dominate the whole image.
- **Surface:** dry-brush edges, small gaps, uneven fill, colored-pencil strokes, mild asymmetry, and human-looking corrections.
- **Scene:** retain foreground, middle ground, background, viewpoint, and recognizable landmarks. Show one concrete behavior through visible cause and effect, such as leaves bending because the 精灵 blocks the wind.

Avoid photorealistic monsters, gloomy grading, heavy black contouring, 3D render, plastic gloss, airbrushed gradients, neon rim light, perfect symmetry, hyper-detailed armor, generic mascot design, or a location unrelated to the source.

## Fast-path prompt: transformed scene B

```text
Use case: single-call image-to-image transformation
Asset type: text-free transformed-scene illustration for an A+B comparison image
Input images: Image 1 is the source scene and composition/edit target for a new derivative output only
Primary request: repaint the complete source scene as a bright collectible creature-card illustration, remove [selected object], and replace it in place with exactly one original [archetype] 精灵
Subject design: simplify [silhouette cue], [color/material cue], and [structural cue] into coherent anatomy, a clear animated silhouette, an expressive face, and a pose showing [hobby or other concrete behavior]
Scene: preserve the original aspect ratio, camera viewpoint, foreground/middle/background structure, and [three landmarks]; keep it recognizably the same location
Subject placement: use the original object's approximate position, scale, depth, orientation, and ground contact; the original object must be absent
Style/medium: bright opaque gouache, colored-pencil details and hatching, visible paper tooth, handmade irregularities, no thick black outline
Lighting/mood: retain the source time of day while making the palette bright, lively, and welcoming
Constraints: original design; no literal intact object with limbs; no text, letters, numbers, symbols, card frame, property icon, energy mark, statistics, logo, watermark, or existing franchise element
Avoid: different location, moved landmarks, duplicate creature, remaining source object, gloomy gray cast, photorealism, 3D, plastic gloss, heavy black contour, branded trading-card UI, AI gibberish
```

## Review the result

Accept B when exactly one original 精灵 appears at the recorded source region, all three cues remain legible, the literal object is absent, the three landmarks and viewpoint remain recognizable, the scene is bright and layered, and no generated text or branded imagery appears. Request one focused correction only for a mandatory failure; accept harmless stylistic variation to protect the fast path.

## Final spread hierarchy

Use the deterministic composer rather than improvising the A+B layout. The finished spread should read in this order: complete original photograph, transformed scene, name, personality and hobby, then the smaller introduction. Scene-derived accent colors may decorate cards, rules, and tabs, but must not tint, crop, cover, or compete with the source photograph.
