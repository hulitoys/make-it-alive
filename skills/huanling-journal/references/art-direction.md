# Art Direction and 精灵 Logic

Use this reference for every Huanling Skills generation.

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

- **Personality:** use 2-6 plain Chinese characters that a person would naturally use to describe temperament, such as `温和警觉`, `胆小护短`, or `外冷内热`. Do not invent poetic labels that need explanation.
- **Hobby:** use 4-10 Chinese characters as a concrete, repeatable verb-object activity that an observer could actually see, such as `收集落叶`, `给幼鸟挡风`, or `趴在窗边晒太阳`. Do not write vague metaphors such as `替风整理树冠`, `收藏月光`, or `梳理回声`.
- **Lore:** use one plain-spoken sentence, normally 24-44 Chinese characters. Write a clear trigger, a concrete action, and an understandable result. The subject must be capable of the verb, and the object must be something that verb can act on. Do not treat sound, shadow, silence, time, or emotion as physical objects that can be carried, hidden, returned, folded, or stored unless the concept record explicitly defines a visible mechanism that does so.
- Prefer familiar verbs such as `听见`, `跑到`, `抬起`, `挡住`, `跟着`, `寻找`, `叫醒`, `躲进`, and `放下`. Keep one main idea per sentence. Do not use battle statistics, rarity labels, type systems, copied card language, or decorative fantasy prose.

Use this three-part check before accepting any record:

1. **Literal paraphrase:** can an ordinary reader restate the sentence without guessing what the metaphor means?
2. **Semantic fit:** can the subject physically perform the verb, and can the object logically receive that action?
3. **Read-aloud test:** does it sound like natural spoken Chinese after one reading?

Reject and rewrite the whole field when any check fails. For example:

- Reject hobby `替风整理树冠`; use `给幼鸟挡风` or `抖落树冠枯叶`.
- Reject lore `它把走散的鸟鸣送回树影里`; use `听见幼鸟叫声时，它会走到树下抬起叶冠，为鸟巢挡住迎面吹来的风。`.

## Visual language

Aim for the environmental storytelling and strong focal hierarchy of a collectible creature-card illustration, not its branded card frame.

- **Character design:** clear animated silhouette, readable facial expression, simplified anatomy, appealing companion proportions appropriate to the archetype.
- **Medium:** bright opaque gouache with colored-pencil construction, accents, and hatching on visible paper tooth.
- **Edges:** no thick black outline. Separate forms with dark colored pencil, adjacent color contrast, and simple light-shadow groups.
- **Color:** luminous scene color, soft environmental hues, and a few saturated focal accents. Preserve dark source materials without allowing gray-brown to dominate the whole image.
- **Surface:** dry-brush edges, small gaps, uneven fill, colored-pencil strokes, mild asymmetry, and human-looking corrections.
- **Scene:** retain foreground, middle ground, background, viewpoint, and recognizable landmarks. Show one concrete behavior through visible cause and effect, such as leaves bending because the 精灵 blocks the wind.

Avoid photorealistic monsters, gloomy grading, heavy black contouring, 3D render, plastic gloss, airbrushed gradients, neon rim light, perfect symmetry, hyper-detailed armor, generic mascot design, or a location unrelated to the source.

## Prompt 1: temporary 精灵 design

```text
Use case: stylized-concept
Asset type: temporary original 精灵 identity reference
Input images: Image 1 is a source-object reference only, not an edit target
Primary request: transform the visible [selected object] into exactly one original collectible companion 精灵
Subject: [archetype and simplified body plan]; preserve [silhouette cue], [color/material cue], and [structural cue]
Scene/backdrop: simple warm light paper with no environment and no card layout
Style/medium: bright opaque gouache, colored-pencil details and hatching, visible paper tooth, handmade irregularities, no thick black outline
Composition/framing: one full-body 精灵, clear animated silhouette, expressive eyes and pose, generous breathing room
Lighting/mood: bright natural light; [temperament]
Constraints: original design; coherent anatomy; no literal intact object with limbs; no text, numbers, symbols, logos, card frame, property icon, watermark, or franchise element
Avoid: realistic monster, gray-brown dominance, gloomy mood, 3D, plastic gloss, heavy black contour, generic anime mascot, existing character resemblance, AI gibberish
```

## Prompt 2: transformed scene B

```text
Use case: compositing and style-transfer
Asset type: text-free transformed-scene illustration for an A+B journal
Input images: Image 1 is the source scene and composition/edit target for a new derivative output only; Image 2 is the exact 精灵 identity reference
Primary request: repaint the complete source scene as a bright collectible creature-card illustration, remove [selected object], and place the same 精灵 from Image 2 at [source region]
Scene: preserve the original camera viewpoint, aspect ratio, foreground/middle/background structure, and [three landmarks]; keep it recognizably the same location
Subject placement: exactly one 精灵 at the original object's approximate position, scale, depth, orientation, and ground contact; the original object must be absent
Style/medium: luminous colored gouache and colored pencil on subtly textured paper; loose environment strokes; crisp readable 精灵 details; no thick black outline
Lighting/mood: retain the source time of day while making the palette bright, lively, and welcoming; show [concrete behavior] through a physically understandable environmental reaction
Constraints: maintain the exact identity, palette, and anatomy from Image 2; no text, letters, numbers, symbols, card frame, property icon, energy mark, statistics, logo, watermark, or existing franchise element
Avoid: different location, moved landmarks, duplicate creature, remaining source object, gloomy gray cast, photorealism, 3D, plastic gloss, heavy black contour, branded trading-card UI, AI gibberish
```

## Review both stages

Accept the temporary design only when exactly one original 精灵 appears, all three cues remain legible, the silhouette is simplified, the expression fits the archetype, and no forbidden content appears.

Accept B only when the same 精灵 appears once at the recorded source region, the original object is absent, the three landmarks and viewpoint remain recognizable, the scene is bright and layered, and no generated text or branded imagery appears. Request one focused correction for a failed condition without redesigning successful parts.
