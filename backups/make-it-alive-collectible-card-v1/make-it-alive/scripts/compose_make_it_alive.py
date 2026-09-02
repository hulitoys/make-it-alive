#!/usr/bin/env python
"""Compose a source photo and transformed scene as an original collectible-card spread."""

from __future__ import print_function

import argparse
import colorsys
import hashlib
import os
import random
import sys
import tempfile
import urllib.request
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
except ImportError:
    raise SystemExit(
        "Pillow is required. Install it in the active Python environment, then rerun."
    )


CANVAS_SIZE = (2400, 1600)
PAPER = (22, 27, 39)
PAGE = (250, 247, 235)
INK = (38, 39, 43)
MUTED_INK = (82, 82, 86)
DEFAULT_ACCENT = (67, 145, 137)
DEFAULT_SECONDARY = (222, 105, 78)
PHOTO_MAT = (232, 227, 213)
FOIL = (226, 194, 103)

SKILL_DIR = Path(__file__).resolve().parents[1]
BUNDLED_FONT = SKILL_DIR / "assets" / "fonts" / "NotoSansCJKsc-Regular.otf"
FONT_DOWNLOAD_URL = (
    "https://raw.githubusercontent.com/notofonts/noto-cjk/main/"
    "Sans/OTF/SimplifiedChinese/NotoSansCJKsc-Regular.otf"
)
FONT_SHA256 = "2c76254f6fc379fddfce0a7e84fb5385bb135d3e399294f6eeb6680d0365b74b"
AUTO_FONT_CACHE = (
    Path(tempfile.gettempdir())
    / "make-it-alive-fonts"
    / "NotoSansCJKsc-Regular.otf"
)
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


def _file_sha256(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _download_verified_font():
    """Download the licensed fallback once when an installer omitted assets."""
    if AUTO_FONT_CACHE.is_file() and _file_sha256(AUTO_FONT_CACHE) == FONT_SHA256:
        return str(AUTO_FONT_CACHE)

    AUTO_FONT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    partial_path = AUTO_FONT_CACHE.with_suffix(".otf.part")
    request = urllib.request.Request(
        FONT_DOWNLOAD_URL,
        headers={"User-Agent": "make-it-alive-skill/1.0"},
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response, open(
            str(partial_path), "wb"
        ) as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                handle.write(chunk)
        if _file_sha256(partial_path) != FONT_SHA256:
            raise ValueError("downloaded font checksum did not match")
        os.replace(str(partial_path), str(AUTO_FONT_CACHE))
    finally:
        if partial_path.exists():
            try:
                partial_path.unlink()
            except OSError:
                pass
    return str(AUTO_FONT_CACHE)


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
    if regular:
        return regular, bold

    try:
        downloaded = _download_verified_font()
        return downloaded, downloaded
    except Exception as error:
        raise FileNotFoundError(
            "No usable CJK font could be resolved. The bundled asset was missing, "
            "no system fallback was present, and the verified automatic fallback "
            "failed: {}".format(error)
        )


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


def _inset_box(box, amount):
    return (
        box[0] + amount,
        box[1] + amount,
        box[2] - amount,
        box[3] - amount,
    )


def _fit_cover_dimensions(source_size, target_size):
    source_width, source_height = source_size
    target_width, target_height = target_size
    scale = max(
        float(target_width) / float(source_width),
        float(target_height) / float(source_height),
    )
    return (
        max(1, int(round(source_width * scale))),
        max(1, int(round(source_height * scale))),
    )


def _collector_backdrop(size, accent, secondary, seed=2409):
    width, height = size
    top = _mix_color(accent, (10, 14, 27), 0.78)
    bottom = _mix_color(secondary, (14, 18, 31), 0.84)
    gradient = Image.new("RGBA", (1, height), (0, 0, 0, 255))
    pixels = []
    for y in range(height):
        ratio = float(y) / float(max(1, height - 1))
        color = _mix_color(top, bottom, ratio)
        pixels.append(color + (255,))
    gradient.putdata(pixels)
    backdrop = gradient.resize(size)

    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(
        (-280, 40, 900, 1220), fill=accent + (92,)
    )
    glow_draw.ellipse(
        (1450, 240, 2700, 1510), fill=secondary + (74,)
    )
    glow = glow.filter(ImageFilter.GaussianBlur(150))
    backdrop = Image.alpha_composite(backdrop, glow)

    pattern = Image.new("RGBA", size, (0, 0, 0, 0))
    pattern_draw = ImageDraw.Draw(pattern)
    for offset in range(-height, width + height, 190):
        pattern_draw.polygon(
            (
                (offset, 0),
                (offset + 78, 0),
                (offset - height + 78, height),
                (offset - height, height),
            ),
            fill=(255, 255, 255, 10),
        )
    rng = random.Random(seed)
    for _ in range(180):
        x = rng.randrange(18, width - 18)
        y = rng.randrange(18, height - 18)
        radius = rng.choice((1, 1, 2, 2, 3))
        color = rng.choice((accent + (80,), secondary + (72,), FOIL + (92,)))
        pattern_draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    return Image.alpha_composite(backdrop, pattern)


def _draw_sparkle(draw, center, radius, color):
    x, y = center
    draw.polygon(
        (
            (x, y - radius),
            (x + max(1, radius // 4), y - max(1, radius // 4)),
            (x + radius, y),
            (x + max(1, radius // 4), y + max(1, radius // 4)),
            (x, y + radius),
            (x - max(1, radius // 4), y + max(1, radius // 4)),
            (x - radius, y),
            (x - max(1, radius // 4), y - max(1, radius // 4)),
        ),
        fill=color,
    )


def _draw_collectible_card(canvas, box, accent, secondary, seed):
    accent_dark = _mix_color(accent, (20, 22, 30), 0.60)
    foil = _mix_color(FOIL, accent, 0.18)
    _draw_panel(
        canvas,
        box,
        accent_dark + (255,),
        radius=44,
        shadow_alpha=105,
        shadow_offset=(0, 20),
    )
    draw = ImageDraw.Draw(canvas)
    _rounded_rectangle(draw, _inset_box(box, 6), 39, accent + (255,))
    _rounded_rectangle(draw, _inset_box(box, 13), 34, foil + (255,))
    _rounded_rectangle(draw, _inset_box(box, 20), 30, accent_dark + (255,))
    surface = _inset_box(box, 29)
    _rounded_rectangle(draw, surface, 25, PAGE + (255,))
    _rounded_rectangle(
        draw,
        _inset_box(surface, 5),
        21,
        None,
        outline=_mix_color(accent, PAGE, 0.42),
        width=2,
    )

    rng = random.Random(seed)
    for _ in range(9):
        side = rng.choice(("left", "right", "top", "bottom"))
        if side in ("left", "right"):
            x = box[0] + rng.choice((11, 17)) if side == "left" else box[2] - rng.choice((11, 17))
            y = rng.randrange(box[1] + 65, box[3] - 65)
        else:
            x = rng.randrange(box[0] + 65, box[2] - 65)
            y = box[1] + rng.choice((11, 17)) if side == "top" else box[3] - rng.choice((11, 17))
        _draw_sparkle(draw, (x, y), rng.choice((4, 5, 7)), (255, 245, 190, 180))
    return surface


def _paste_showcase(canvas, image, box, accent, seed=88):
    """Fill the window with a blurred cover layer and a complete sharp image."""
    left, top, right, bottom = box
    width = right - left
    height = bottom - top

    cover_size = _fit_cover_dimensions(image.size, (width, height))
    cover = image.resize(cover_size, _resample_filter())
    crop_left = max(0, (cover_size[0] - width) // 2)
    crop_top = max(0, (cover_size[1] - height) // 2)
    cover = cover.crop((crop_left, crop_top, crop_left + width, crop_top + height))
    blur_radius = max(18, min(width, height) // 32)
    cover = cover.filter(ImageFilter.GaussianBlur(blur_radius))
    canvas.alpha_composite(cover, (left, top))

    wash = Image.new("RGBA", (width, height), accent + (22,))
    canvas.alpha_composite(wash, (left, top))

    padding = 22
    sharp_size = _fit_dimensions(image.size, (width - padding * 2, height - padding * 2))
    sharp = image.resize(sharp_size, _resample_filter())
    x = left + (width - sharp_size[0]) // 2
    y = top + (height - sharp_size[1]) // 2
    sharp_box = (x, y, x + sharp_size[0], y + sharp_size[1])

    shadow = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rectangle(
        (sharp_box[0] - 7, sharp_box[1] - 7, sharp_box[2] + 7, sharp_box[3] + 7),
        fill=(7, 10, 16, 110),
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(14))
    canvas.alpha_composite(shadow)

    draw = ImageDraw.Draw(canvas)
    draw.rectangle(
        (sharp_box[0] - 7, sharp_box[1] - 7, sharp_box[2] + 7, sharp_box[3] + 7),
        fill=(255, 252, 238, 255),
    )
    canvas.alpha_composite(sharp, (x, y))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle(sharp_box, outline=_mix_color(accent, INK, 0.50), width=3)

    rng = random.Random(seed)
    for _ in range(8):
        px = rng.randrange(left + 20, right - 20)
        py = rng.randrange(top + 20, bottom - 20)
        if sharp_box[0] - 14 <= px <= sharp_box[2] + 14 and sharp_box[1] - 14 <= py <= sharp_box[3] + 14:
            continue
        _draw_sparkle(draw, (px, py), rng.choice((3, 4, 5)), (255, 250, 220, 135))
    return sharp_box


def _draw_art_window(canvas, image, outer_box, accent, secondary, seed):
    draw = ImageDraw.Draw(canvas)
    accent_dark = _mix_color(accent, (20, 22, 28), 0.58)
    foil = _mix_color(FOIL, secondary, 0.16)
    _rounded_rectangle(draw, outer_box, 24, accent_dark + (255,))
    _rounded_rectangle(draw, _inset_box(outer_box, 6), 19, foil + (255,))
    _rounded_rectangle(draw, _inset_box(outer_box, 12), 15, accent + (255,))
    image_box = _inset_box(outer_box, 18)
    sharp_box = _paste_showcase(canvas, image, image_box, accent, seed=seed)
    draw = ImageDraw.Draw(canvas)
    _rounded_rectangle(draw, outer_box, 24, None, outline=(20, 22, 28, 210), width=3)
    return image_box, sharp_box


def _draw_trait_panel(draw, box, label, value, font_path, accent):
    accent_dark = _mix_color(accent, INK, 0.42)
    tint = _mix_color(accent, PAGE, 0.86)
    _rounded_rectangle(draw, box, 18, tint + (255,), outline=accent_dark, width=2)
    header_bottom = box[1] + 32
    _rounded_rectangle(
        draw,
        (box[0], box[1], box[2], header_bottom + 8),
        18,
        accent_dark + (255,),
    )
    draw.rectangle((box[0], header_bottom - 2, box[2], header_bottom + 8), fill=accent_dark)
    label_font = ImageFont.truetype(font_path, 17)
    draw.text((box[0] + 18, box[1] + 7), label, font=label_font, fill=PAGE)
    value_font = _font_that_fits(
        draw, value, font_path, box[2] - box[0] - 36, 30, 21
    )
    draw.text((box[0] + 18, box[1] + 48), value, font=value_font, fill=INK)


def _draw_lore_panel(draw, box, intro, font_path, accent, secondary):
    tint = _mix_color(accent, PAGE, 0.90)
    border = _mix_color(FOIL, secondary, 0.18)
    _rounded_rectangle(draw, box, 20, tint + (255,), outline=border, width=3)
    draw.polygon(
        (
            (box[0], box[1] + 28),
            (box[0] + 18, box[1] + 10),
            (box[0] + 18, box[3] - 10),
            (box[0], box[3] - 28),
        ),
        fill=accent,
    )
    font, lines = _wrapped_font_that_fits(
        draw,
        intro,
        font_path,
        max_width=box[2] - box[0] - 74,
        max_lines=2,
        start_size=24,
        min_size=19,
    )
    sample = _text_bbox(draw, "示例Ag", font)
    line_height = sample[3] - sample[1] + 13
    total_height = line_height * len(lines) - 13
    y = box[1] + (box[3] - box[1] - total_height) // 2 - sample[1]
    for line in lines:
        draw.text((box[0] + 44, y), line, font=font, fill=INK)
        y += line_height


def _source_card_layout(image_size):
    """Choose a card silhouette that respects the source image orientation."""
    aspect = float(image_size[0]) / float(image_size[1])
    if aspect >= 1.15:
        return {
            "card": (48, 238, 1216, 1370),
            "band": (100, 290, 1164, 370),
            "art": (100, 388, 1164, 1138),
            "footer": (100, 1156, 1164, 1318),
            "label": (126, 307),
            "meta": (958, 315),
            "footer_title": (126, 1183),
            "footer_meta": (126, 1224),
            "swatches": (1040, 1200),
        }
    if aspect <= 0.88:
        return {
            "card": (64, 72, 1148, 1540),
            "band": (116, 122, 1096, 202),
            "art": (116, 220, 1096, 1388),
            "footer": (116, 1406, 1096, 1488),
            "label": (142, 139),
            "meta": (898, 147),
            "footer_title": (140, 1423),
            "footer_meta": (140, 1457),
            "swatches": (982, 1436),
        }
    return {
        "card": (48, 140, 1216, 1460),
        "band": (100, 192, 1164, 272),
        "art": (100, 290, 1164, 1254),
        "footer": (100, 1272, 1164, 1408),
        "label": (126, 209),
        "meta": (958, 217),
        "footer_title": (126, 1295),
        "footer_meta": (126, 1334),
        "swatches": (1040, 1312),
    }


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
    photo_accent, _ = _derive_palette(photo)

    canvas = _collector_backdrop(CANVAS_SIZE, accent, secondary)

    # Two deliberately card-shaped shells create a collectible display rather than
    # another flat editorial split. The slight vertical offset adds depth.
    source_layout = _source_card_layout(photo.size)
    left_card = source_layout["card"]
    right_card = (1252, 30, 2336, 1498)
    _draw_collectible_card(canvas, left_card, photo_accent, secondary, seed=701)
    _draw_collectible_card(canvas, right_card, accent, secondary, seed=1701)
    draw = ImageDraw.Draw(canvas)

    # Source card header.
    source_band = source_layout["band"]
    _rounded_rectangle(
        draw,
        source_band,
        18,
        _mix_color(photo_accent, INK, 0.50) + (255,),
        outline=_mix_color(FOIL, photo_accent, 0.18),
        width=3,
    )
    source_label_font = ImageFont.truetype(regular_font_path, 27)
    source_meta_font = ImageFont.truetype(regular_font_path, 17)
    draw.text(source_layout["label"], "A · 原景", font=source_label_font, fill=PAGE)
    draw.text(source_layout["meta"], "SOURCE FRAME", font=source_meta_font, fill=(245, 236, 204))

    # A stays complete and sharp; a blurred cover crop fills the card window.
    source_art_outer = source_layout["art"]
    _draw_art_window(
        canvas,
        photo,
        source_art_outer,
        photo_accent,
        secondary,
        seed=211,
    )
    draw = ImageDraw.Draw(canvas)
    source_footer = source_layout["footer"]
    _rounded_rectangle(
        draw,
        source_footer,
        18,
        _mix_color(photo_accent, PAGE, 0.88) + (255,),
        outline=_mix_color(photo_accent, INK, 0.50),
        width=2,
    )
    footer_title_font = ImageFont.truetype(regular_font_path, 21)
    footer_small_font = ImageFont.truetype(regular_font_path, 16)
    draw.text(source_layout["footer_title"], "完整原图", font=footer_title_font, fill=INK)
    draw.text(source_layout["footer_meta"], "FULL FRAME · SOURCE FILE UNCHANGED", font=footer_small_font, fill=MUTED_INK)
    swatch_x, swatch_y = source_layout["swatches"]
    for index, color in enumerate((photo_accent, secondary, _mix_color(photo_accent, INK, 0.55))):
        x = swatch_x + index * 28
        draw.ellipse((x, swatch_y, x + 15, swatch_y + 15), fill=color)

    # Creature card header follows collectible-card hierarchy: identity first.
    draw.text((1306, 74), "MAKE IT ALIVE", font=footer_small_font, fill=accent_dark)
    name_font = _font_that_fits(draw, str(name), bold_font_path, 720, 66, 44)
    _draw_weighted_text(draw, (1304, 98), str(name), name_font, INK)
    number_font = ImageFont.truetype(regular_font_path, 21)
    draw.text((2160, 114), "No. 001", font=number_font, fill=accent_dark)
    draw.line((1304, 174, 2284, 174), fill=_mix_color(FOIL, accent, 0.24), width=5)
    draw.line((1304, 181, 1608, 181), fill=secondary, width=5)

    scene_art_outer = (1304, 196, 2284, 1028)
    _draw_art_window(
        canvas,
        scene,
        scene_art_outer,
        accent,
        secondary,
        seed=431,
    )
    draw = ImageDraw.Draw(canvas)

    descriptor_band = (1304, 1046, 2284, 1092)
    _rounded_rectangle(
        draw,
        descriptor_band,
        20,
        accent_dark + (255,),
        outline=_mix_color(FOIL, secondary, 0.18),
        width=2,
    )
    descriptor_font = ImageFont.truetype(regular_font_path, 18)
    draw.text((1330, 1057), "原创精灵档案 · ORIGINAL COMPANION", font=descriptor_font, fill=PAGE)
    draw.text((2184, 1057), "001", font=descriptor_font, fill=(245, 236, 204))

    _draw_trait_panel(
        draw,
        (1304, 1110, 1782, 1212),
        "性格 / PERSONALITY",
        personality,
        regular_font_path,
        accent,
    )
    _draw_trait_panel(
        draw,
        (1802, 1110, 2284, 1212),
        "爱好 / HOBBY",
        hobby,
        regular_font_path,
        secondary,
    )
    _draw_lore_panel(
        draw,
        (1304, 1234, 2284, 1390),
        intro,
        regular_font_path,
        accent,
        secondary,
    )

    draw.line((1304, 1412, 2144, 1412), fill=_mix_color(accent, PAGE, 0.52), width=2)
    draw.text((1304, 1427), "MAKE IT ALIVE · FIELD GUIDE", font=footer_small_font, fill=MUTED_INK)
    _draw_sparkle(draw, (2222, 1436), 10, _mix_color(FOIL, secondary, 0.20))
    draw.text((2250, 1425), "01", font=number_font, fill=accent_dark)

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
