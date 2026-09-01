#!/usr/bin/env python
"""Compose an untouched photo and its transformed scene into an editorial field-guide spread."""

from __future__ import print_function

import argparse
import colorsys
import os
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError:
    raise SystemExit(
        "Pillow is required. Install it in the active Python environment, then rerun."
    )


CANVAS_SIZE = (2400, 1600)
PAPER = (239, 233, 219)
PAGE = (255, 252, 242)
INK = (43, 48, 47)
MUTED_INK = (85, 91, 88)
DEFAULT_ACCENT = (67, 145, 137)
DEFAULT_SECONDARY = (222, 105, 78)
PHOTO_MAT = (232, 227, 213)

SKILL_DIR = Path(__file__).resolve().parents[1]
BUNDLED_FONT = SKILL_DIR / "assets" / "fonts" / "NotoSansCJKsc-Regular.otf"
CLOSING_PUNCTUATION = frozenset("，。！？；：、）】》」』…")

REGULAR_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",
    r"C:\Windows\Fonts\simkai.ttf",
    r"C:\Windows\Fonts\simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

BOLD_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyhbd.ttc",
    r"C:\Windows\Fonts\simhei.ttf",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc",
]


def _resample_filter():
    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS


def _existing_font(candidates):
    for candidate in candidates:
        if os.path.isfile(candidate):
            return candidate
    return None


def resolve_fonts(explicit_font=None):
    if explicit_font:
        if not os.path.isfile(explicit_font):
            raise FileNotFoundError(
                "Font not found: {}. Pass --font with a readable CJK .ttf/.ttc path.".format(
                    explicit_font
                )
            )
        return explicit_font, explicit_font

    if BUNDLED_FONT.is_file():
        bundled = str(BUNDLED_FONT)
        return bundled, bundled

    regular = _existing_font(REGULAR_FONT_CANDIDATES)
    bold = _existing_font(BOLD_FONT_CANDIDATES) or regular
    if not regular:
        raise FileNotFoundError(
            "The bundled CJK font is missing and no system fallback was found. "
            "Reinstall the complete Skill or rerun with --font <path-to-CJK-font>."
        )
    return regular, bold


def next_available_path(path):
    path = Path(path)
    if not path.exists():
        return path
    index = 2
    while True:
        candidate = path.with_name("{}-v{}{}".format(path.stem, index, path.suffix))
        if not candidate.exists():
            return candidate
        index += 1


def _text_bbox(draw, text, font):
    try:
        return draw.textbbox((0, 0), text, font=font)
    except AttributeError:
        width, height = draw.textsize(text, font=font)
        return (0, 0, width, height)


def _text_width(draw, text, font):
    box = _text_bbox(draw, text, font)
    return box[2] - box[0]


def _font_that_fits(draw, text, font_path, max_width, start_size, min_size):
    for size in range(start_size, min_size - 1, -2):
        font = ImageFont.truetype(font_path, size)
        if _text_width(draw, text, font) <= max_width:
            return font
    return ImageFont.truetype(font_path, min_size)


def _required_text(value, label):
    normalized = " ".join(str(value).split())
    if not normalized:
        raise ValueError("{} must not be empty.".format(label))
    return normalized


def _wrap_text(draw, text, font, max_width):
    lines = []
    current = ""
    for character in text:
        candidate = current + character
        if not current or _text_width(draw, candidate, font) <= max_width:
            current = candidate
            continue
        lines.append(current.strip())
        current = character.lstrip()
    if current:
        lines.append(current.strip())
    return [line for line in lines if line]


def _wrapped_font_that_fits(
    draw, text, font_path, max_width, max_lines, start_size, min_size
):
    for size in range(start_size, min_size - 1, -1):
        font = ImageFont.truetype(font_path, size)
        lines = _wrap_text(draw, text, font, max_width)
        has_orphaned_punctuation = any(
            line and line[0] in CLOSING_PUNCTUATION for line in lines[1:]
        )
        if len(lines) <= max_lines and not has_orphaned_punctuation:
            return font, lines
    raise ValueError(
        "Introduction is too long for the two-line layout. Shorten --intro and rerun."
    )


def _load_image(path):
    with Image.open(str(path)) as source:
        oriented = ImageOps.exif_transpose(source)
        return oriented.convert("RGBA")


def _fit_dimensions(source_size, target_size):
    source_width, source_height = source_size
    target_width, target_height = target_size
    scale = min(
        float(target_width) / float(source_width),
        float(target_height) / float(source_height),
    )
    return (
        max(1, int(round(source_width * scale))),
        max(1, int(round(source_height * scale))),
    )


def _paste_contained(canvas, image, box, matte):
    left, top, right, bottom = box
    width = right - left
    height = bottom - top
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(box, fill=matte)
    resized_size = _fit_dimensions(image.size, (width, height))
    resized = image.resize(resized_size, _resample_filter())
    x = left + (width - resized_size[0]) // 2
    y = top + (height - resized_size[1]) // 2
    if resized.mode == "RGBA":
        canvas.alpha_composite(resized, (x, y))
    else:
        canvas.paste(resized, (x, y))
    return (x, y, x + resized_size[0], y + resized_size[1])


def _paper_texture(size, seed=1729):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    rng = random.Random(seed)
    for _ in range(11000):
        x = rng.randrange(0, size[0])
        y = rng.randrange(0, size[1])
        tone = rng.choice([(92, 72, 46, 6), (255, 255, 255, 10)])
        draw.point((x, y), fill=tone)
    for _ in range(120):
        y = rng.randrange(0, size[1])
        alpha = rng.randrange(2, 7)
        draw.line(
            (0, y, size[0], y + rng.choice([-1, 0, 1])),
            fill=(98, 74, 44, alpha),
        )
    return layer


def _draw_sketch_rect(draw, box, color, width=3, seed=13):
    rng = random.Random(seed)
    for _ in range(2):
        offset = rng.choice([-2, -1, 0, 1, 2])
        shifted = (
            box[0] + offset,
            box[1] - offset,
            box[2] - offset,
            box[3] + offset,
        )
        draw.rectangle(shifted, outline=color, width=width)


def _rounded_rectangle(draw, box, radius, fill, outline=None, width=1):
    try:
        draw.rounded_rectangle(
            box, radius=radius, fill=fill, outline=outline, width=width
        )
    except AttributeError:
        draw.rectangle(box, fill=fill, outline=outline, width=width)


def _mix_color(first, second, second_weight):
    return tuple(
        int(round(a * (1.0 - second_weight) + b * second_weight))
        for a, b in zip(first, second)
    )


def _lively_color(rgb, minimum_saturation=0.42, minimum_value=0.54):
    hue, saturation, value = colorsys.rgb_to_hsv(
        rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
    )
    saturation = max(saturation, minimum_saturation)
    value = max(min(value, 0.82), minimum_value)
    red, green, blue = colorsys.hsv_to_rgb(hue, saturation, value)
    return (int(round(red * 255)), int(round(green * 255)), int(round(blue * 255)))


def _derive_palette(image):
    """Choose a stable lively accent and a contrasting companion from the scene."""
    thumbnail = image.convert("RGB").resize((72, 72), _resample_filter())
    quantized = thumbnail.quantize(colors=12)
    raw_colors = quantized.getcolors(maxcolors=256) or []
    palette = quantized.getpalette() or []
    candidates = []
    total = float(sum(count for count, _ in raw_colors) or 1)

    for count, index in raw_colors:
        start = index * 3
        rgb = tuple(palette[start : start + 3])
        if len(rgb) != 3:
            continue
        hue, saturation, value = colorsys.rgb_to_hsv(
            rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0
        )
        if value < 0.20 or value > 0.96 or saturation < 0.16:
            continue
        score = (
            saturation * 0.58
            + min(count / total, 0.34) * 0.60
            - abs(value - 0.68) * 0.30
        )
        candidates.append((score, rgb, hue, saturation, value))

    if not candidates:
        return DEFAULT_ACCENT, DEFAULT_SECONDARY

    candidates.sort(reverse=True)
    _, primary, primary_hue, _, primary_value = candidates[0]
    if primary_value < 0.48:
        primary = _mix_color(primary, (255, 255, 255), 0.24)
    primary = _lively_color(primary)

    secondary = None
    for _, rgb, hue, saturation, value in candidates[1:]:
        hue_distance = min(abs(hue - primary_hue), 1.0 - abs(hue - primary_hue))
        if hue_distance >= 0.16 and saturation >= 0.24 and value >= 0.34:
            secondary = rgb
            break
    if secondary is None:
        secondary = DEFAULT_SECONDARY
    secondary = _lively_color(secondary, minimum_saturation=0.48, minimum_value=0.58)
    return primary, secondary


def _draw_panel(canvas, box, fill, radius=26, shadow_alpha=42, shadow_offset=(0, 12)):
    shadow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shifted = (
        box[0] + shadow_offset[0],
        box[1] + shadow_offset[1],
        box[2] + shadow_offset[0],
        box[3] + shadow_offset[1],
    )
    _rounded_rectangle(
        shadow_draw, shifted, radius, (65, 48, 31, shadow_alpha)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    canvas.alpha_composite(shadow)
    draw = ImageDraw.Draw(canvas)
    _rounded_rectangle(draw, box, radius, fill)


def _draw_weighted_text(draw, position, text, font, fill):
    x, y = position
    draw.text((x, y), text, font=font, fill=fill)
    draw.text((x + 1, y), text, font=font, fill=fill)


def _draw_meta_card(draw, box, label, value, font_path, accent, tint):
    _rounded_rectangle(draw, box, 22, tint, outline=_mix_color(accent, PAGE, 0.25), width=2)
    label_font = ImageFont.truetype(font_path, 19)
    draw.text((box[0] + 20, box[1] + 12), label, font=label_font, fill=accent)
    available = box[2] - box[0] - 40
    value_font = _font_that_fits(draw, value, font_path, available, 30, 22)
    draw.text((box[0] + 20, box[1] + 39), value, font=value_font, fill=INK)


def _draw_header_tag(draw, box, text, font_path, accent, tint):
    _rounded_rectangle(draw, box, 21, tint)
    font = ImageFont.truetype(font_path, 23)
    bbox = _text_bbox(draw, text, font)
    height = bbox[3] - bbox[1]
    y = box[1] + (box[3] - box[1] - height) // 2 - bbox[1]
    draw.text((box[0] + 18, y), text, font=font, fill=accent)


def compose_make_it_alive(
    photo_path,
    scene_path,
    name,
    personality,
    hobby,
    intro,
    output_path,
    font_path=None,
):
    photo_path = Path(photo_path)
    scene_path = Path(scene_path)
    output_path = Path(output_path)

    if not photo_path.is_file():
        raise FileNotFoundError("Photo not found: {}".format(photo_path))
    if not scene_path.is_file():
        raise FileNotFoundError("Transformed scene not found: {}".format(scene_path))
    if output_path.suffix.lower() != ".png":
        raise ValueError("Output must use a .png extension.")

    name = _required_text(name, "Name")
    personality = _required_text(personality, "Personality")
    hobby = _required_text(hobby, "Hobby")
    intro = _required_text(intro, "Introduction")

    regular_font_path, bold_font_path = resolve_fonts(font_path)
    photo = _load_image(photo_path)
    scene = _load_image(scene_path)
    accent, secondary = _derive_palette(scene)
    accent_dark = _mix_color(accent, INK, 0.46)
    accent_tint = _mix_color(accent, PAGE, 0.84)
    secondary_tint = _mix_color(secondary, PAGE, 0.88)
    photo_accent, _ = _derive_palette(photo)
    photo_matte = _mix_color(photo_accent, PHOTO_MAT, 0.78)

    canvas = Image.new("RGBA", CANVAS_SIZE, PAPER + (255,))
    canvas = Image.alpha_composite(canvas, _paper_texture(CANVAS_SIZE))

    # Layered editorial cards replace the rigid notebook grid while preserving A+B.
    left_card = (42, 52, 1320, 1548)
    right_card = (1278, 28, 2358, 1572)
    _draw_panel(canvas, left_card, PAGE + (255,), radius=30, shadow_alpha=32)
    _draw_panel(canvas, right_card, PAGE + (255,), radius=30, shadow_alpha=54)

    draw = ImageDraw.Draw(canvas)
    _rounded_rectangle(draw, (1278, 28, 1304, 1572), 13, accent + (255,))
    _rounded_rectangle(draw, (56, 72, 65, 1528), 5, secondary + (150,))

    _draw_header_tag(
        draw,
        (88, 80, 252, 124),
        "A · 原景",
        regular_font_path,
        _mix_color(photo_accent, INK, 0.48),
        _mix_color(photo_accent, PAGE, 0.85),
    )
    draw.line((278, 102, 1248, 102), fill=_mix_color(photo_accent, PAGE, 0.35), width=2)

    photo_frame = (78, 144, 1278, 1508)
    _draw_panel(canvas, photo_frame, (255, 255, 251, 255), radius=20, shadow_alpha=24, shadow_offset=(0, 8))
    photo_box = (102, 168, 1254, 1484)
    _paste_contained(canvas, photo, photo_box, photo_matte + (255,))
    draw = ImageDraw.Draw(canvas)
    _draw_sketch_rect(draw, photo_box, _mix_color(photo_accent, INK, 0.55), width=2, seed=21)

    _draw_header_tag(
        draw,
        (1342, 72, 1578, 116),
        "B · MAKE IT ALIVE",
        regular_font_path,
        accent_dark,
        accent_tint,
    )
    draw.line((1604, 94, 2184, 94), fill=_mix_color(accent, PAGE, 0.38), width=2)
    for index, color in enumerate((accent, secondary, accent_dark)):
        x = 2208 + index * 32
        draw.ellipse((x, 83, x + 14, 97), fill=color)

    scene_frame = (1338, 136, 2320, 1020)
    _draw_panel(canvas, scene_frame, (255, 255, 251, 255), radius=22, shadow_alpha=30, shadow_offset=(0, 9))
    scene_box = (1362, 160, 2296, 996)
    _paste_contained(canvas, scene, scene_box, accent_tint + (255,))
    draw = ImageDraw.Draw(canvas)
    _draw_sketch_rect(draw, scene_box, accent_dark, width=2, seed=43)
    name_font = _font_that_fits(draw, str(name), bold_font_path, 930, 82, 50)
    _draw_weighted_text(draw, (1344, 1040), str(name), name_font, INK)
    draw.line((1346, 1141, 1526, 1141), fill=secondary, width=7)
    draw.line((1538, 1141, 2318, 1141), fill=_mix_color(accent, PAGE, 0.52), width=2)

    _draw_meta_card(
        draw,
        (1344, 1170, 1814, 1268),
        "性格 / PERSONALITY",
        personality,
        regular_font_path,
        accent_dark,
        accent_tint,
    )
    _draw_meta_card(
        draw,
        (1832, 1170, 2318, 1268),
        "爱好 / HOBBY",
        hobby,
        regular_font_path,
        _mix_color(secondary, INK, 0.42),
        secondary_tint,
    )

    intro_panel = (1344, 1294, 2318, 1458)
    _rounded_rectangle(draw, intro_panel, 24, _mix_color(accent_tint, PAGE, 0.36))
    _rounded_rectangle(
        draw,
        (intro_panel[0], intro_panel[1], intro_panel[0] + 9, intro_panel[3]),
        5,
        accent,
    )

    intro_font, intro_lines = _wrapped_font_that_fits(
        draw,
        intro,
        regular_font_path,
        max_width=900,
        max_lines=2,
        start_size=25,
        min_size=20,
    )
    intro_y = 1330
    intro_box = _text_bbox(draw, "示例Ag", intro_font)
    intro_line_height = intro_box[3] - intro_box[1] + 14
    for line in intro_lines:
        draw.text((1380, intro_y), line, font=intro_font, fill=MUTED_INK)
        intro_y += intro_line_height

    draw.line((1344, 1494, 2225, 1494), fill=_mix_color(accent, PAGE, 0.40), width=2)
    footer_font = ImageFont.truetype(regular_font_path, 18)
    draw.text((1344, 1512), "MAKE IT ALIVE · FIELD GUIDE", font=footer_font, fill=MUTED_INK)
    page_font = ImageFont.truetype(regular_font_path, 23)
    draw.text((2262, 1506), "01", font=page_font, fill=accent_dark)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_path = next_available_path(output_path)
    canvas.convert("RGB").save(str(final_path), format="PNG", optimize=True)
    return final_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compose a 2400x1600 Make It Alive transformed-scene spread."
    )
    parser.add_argument("--photo", required=True, help="Untouched source scene photo")
    parser.add_argument("--scene", required=True, help="Text-free transformed scene B")
    parser.add_argument("--name", required=True, help="Original spirit name")
    parser.add_argument("--personality", required=True, help="Short personality phrase")
    parser.add_argument("--hobby", required=True, help="Short hobby phrase")
    parser.add_argument(
        "--intro",
        "--lore",
        dest="intro",
        required=True,
        help="Small unlabelled natural-language introduction sentence",
    )
    parser.add_argument("--output", required=True, help="Requested .png output path")
    parser.add_argument("--font", help="Optional CJK .ttf/.ttc font path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        final_path = compose_make_it_alive(
            photo_path=args.photo,
            scene_path=args.scene,
            name=args.name,
            personality=args.personality,
            hobby=args.hobby,
            intro=args.intro,
            output_path=args.output,
            font_path=args.font,
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        print("error: {}".format(error), file=sys.stderr)
        return 2
    print(str(final_path.resolve()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
