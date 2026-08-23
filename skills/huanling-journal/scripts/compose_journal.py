#!/usr/bin/env python
"""Compose an untouched photo and its transformed scene into one journal spread."""

from __future__ import print_function

import argparse
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
PAPER = (245, 239, 221)
PAGE = (255, 251, 237)
INK = (48, 55, 53)
MUTED_INK = (73, 96, 92)
ACCENT = (220, 91, 76)
LINE = (82, 150, 143)
PHOTO_MAT = (235, 229, 211)
CHIP = (239, 231, 196)

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

    regular = _existing_font(REGULAR_FONT_CANDIDATES)
    bold = _existing_font(BOLD_FONT_CANDIDATES) or regular
    if not regular:
        raise FileNotFoundError(
            "No CJK font was found. Rerun with --font <path-to-CJK-font>."
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


def _wrap_chars(draw, text, font, max_width):
    normalized = " ".join(str(text).split())
    if not normalized:
        return [""]
    lines = []
    current = ""
    for char in normalized:
        candidate = current + char
        if current and _text_width(draw, candidate, font) > max_width:
            lines.append(current.rstrip())
            current = char.lstrip()
        else:
            current = candidate
    if current or not lines:
        lines.append(current.rstrip())
    return lines


def _truncate_line(draw, text, font, max_width):
    ellipsis = "…"
    value = text
    while value and _text_width(draw, value + ellipsis, font) > max_width:
        value = value[:-1]
    return value + ellipsis


def _fit_lore(draw, text, font_path, max_width, max_lines=2):
    for size in range(38, 25, -2):
        font = ImageFont.truetype(font_path, size)
        lines = _wrap_chars(draw, text, font, max_width)
        if len(lines) <= max_lines:
            return font, lines
    font = ImageFont.truetype(font_path, 25)
    lines = _wrap_chars(draw, text, font, max_width)
    visible = lines[:max_lines]
    if len(lines) > max_lines:
        visible[-1] = _truncate_line(draw, visible[-1], font, max_width)
    return font, visible


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


def _draw_chip(draw, box, label, value, font_path):
    _rounded_rectangle(draw, box, 24, CHIP, LINE, 2)
    available = box[2] - box[0] - 34
    text = "{}｜{}".format(label, value)
    font = _font_that_fits(draw, text, font_path, available, 31, 22)
    bbox = _text_bbox(draw, text, font)
    text_height = bbox[3] - bbox[1]
    y = box[1] + (box[3] - box[1] - text_height) // 2 - bbox[1]
    draw.text((box[0] + 17, y), text, font=font, fill=MUTED_INK)


def compose_journal(
    photo_path,
    scene_path,
    name,
    personality,
    hobby,
    lore,
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

    regular_font_path, bold_font_path = resolve_fonts(font_path)
    photo = _load_image(photo_path)
    scene = _load_image(scene_path)

    canvas = Image.new("RGBA", CANVAS_SIZE, PAPER + (255,))
    canvas = Image.alpha_composite(canvas, _paper_texture(CANVAS_SIZE))

    shadow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle((54, 66, 2356, 1566), fill=(65, 45, 28, 54))
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    canvas = Image.alpha_composite(canvas, shadow)

    draw = ImageDraw.Draw(canvas)
    left_page = (45, 45, 1280, 1555)
    right_page = (1320, 45, 2355, 1555)
    draw.rectangle(left_page, fill=PAGE, outline=LINE, width=2)
    draw.rectangle(right_page, fill=PAGE, outline=LINE, width=2)
    draw.line((1294, 65, 1294, 1538), fill=(112, 88, 59), width=3)
    draw.line((1305, 65, 1305, 1538), fill=(255, 250, 236), width=3)

    label_font = ImageFont.truetype(regular_font_path, 27)
    draw.text((110, 82), "原景", font=label_font, fill=MUTED_INK)
    draw.line((180, 103, 1220, 103), fill=LINE, width=2)

    photo_box = (110, 128, 1220, 1490)
    _paste_contained(canvas, photo, photo_box, PHOTO_MAT + (255,))
    draw = ImageDraw.Draw(canvas)
    _draw_sketch_rect(draw, photo_box, (91, 75, 54), width=3, seed=21)

    draw.text((1390, 82), "显灵现场", font=label_font, fill=MUTED_INK)
    draw.line((1530, 103, 2268, 103), fill=LINE, width=2)

    scene_box = (1380, 128, 2295, 955)
    _paste_contained(canvas, scene, scene_box, (249, 246, 229, 255))
    draw = ImageDraw.Draw(canvas)
    _draw_sketch_rect(draw, scene_box, LINE, width=2, seed=43)

    name_font = _font_that_fits(draw, str(name), bold_font_path, 850, 78, 48)
    draw.text((1390, 1005), str(name), font=name_font, fill=INK)
    draw.line((1390, 1105, 2268, 1105), fill=ACCENT, width=4)

    _draw_chip(
        draw, (1390, 1140, 1815, 1210), "性格", personality, regular_font_path
    )
    _draw_chip(draw, (1843, 1140, 2268, 1210), "爱好", hobby, regular_font_path)

    label_font = ImageFont.truetype(regular_font_path, 25)
    draw.text((1390, 1250), "观察记录", font=label_font, fill=ACCENT)
    lore_font, lore_lines = _fit_lore(
        draw, lore, regular_font_path, 870, max_lines=2
    )
    y = 1298
    for line in lore_lines:
        draw.text((1390, y), line, font=lore_font, fill=INK)
        bbox = _text_bbox(draw, line, lore_font)
        y += (bbox[3] - bbox[1]) + 18

    draw.line((1390, 1468, 2268, 1468), fill=LINE, width=2)
    footer_font = ImageFont.truetype(regular_font_path, 21)
    draw.text(
        (1390, 1486), "HUANLING · SCENE NOTE", font=footer_font, fill=MUTED_INK
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_path = next_available_path(output_path)
    canvas.convert("RGB").save(str(final_path), format="PNG", optimize=True)
    return final_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compose a 2400x1600 Huanling transformed-scene journal spread."
    )
    parser.add_argument("--photo", required=True, help="Untouched source scene photo")
    parser.add_argument("--scene", required=True, help="Text-free transformed scene B")
    parser.add_argument("--name", required=True, help="Original spirit name")
    parser.add_argument("--personality", required=True, help="Short personality phrase")
    parser.add_argument("--hobby", required=True, help="Short hobby phrase")
    parser.add_argument("--lore", required=True, help="One behavioral lore sentence")
    parser.add_argument("--output", required=True, help="Requested .png output path")
    parser.add_argument("--font", help="Optional CJK .ttf/.ttc font path")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        final_path = compose_journal(
            photo_path=args.photo,
            scene_path=args.scene,
            name=args.name,
            personality=args.personality,
            hobby=args.hobby,
            lore=args.lore,
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
