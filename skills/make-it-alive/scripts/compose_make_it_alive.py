#!/usr/bin/env python
"""Compose a source photo and its anime transformation with no added text."""

from __future__ import print_function

import argparse
import random
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
except ImportError as error:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install Pillow"
    ) from error


DEFAULT_LONG_EDGE = 1600
DEFAULT_TRANSITION_WIDTH = 48
DEFAULT_GAP = DEFAULT_TRANSITION_WIDTH
DIVIDER_COLOR = (244, 239, 226)
FIBER_DARK = (168, 148, 112)
FIBER_LIGHT = (255, 252, 242)


def _resample_filter():
    try:
        return Image.Resampling.LANCZOS
    except AttributeError:
        return Image.LANCZOS


def _load_image(path):
    with Image.open(str(path)) as opened:
        image = ImageOps.exif_transpose(opened)
        return image.convert("RGBA")


def _fit_dimensions(source_size, target_size, cover=False):
    source_width, source_height = source_size
    target_width, target_height = target_size
    if source_width <= 0 or source_height <= 0:
        raise ValueError("Image dimensions must be positive.")
    scales = (
        float(target_width) / float(source_width),
        float(target_height) / float(source_height),
    )
    scale = max(scales) if cover else min(scales)
    return (
        max(1, int(round(source_width * scale))),
        max(1, int(round(source_height * scale))),
    )


def _panel_size(source_size, long_edge=DEFAULT_LONG_EDGE):
    width, height = source_size
    if width >= height:
        return (
            long_edge,
            max(1, int(round(long_edge * float(height) / float(width)))),
        )
    return (
        max(1, int(round(long_edge * float(width) / float(height)))),
        long_edge,
    )


def _center_cover(image, target_size):
    target_width, target_height = target_size
    cover_size = _fit_dimensions(image.size, target_size, cover=True)
    resized = image.resize(cover_size, _resample_filter())
    left = max(0, (cover_size[0] - target_width) // 2)
    top = max(0, (cover_size[1] - target_height) // 2)
    return resized.crop((left, top, left + target_width, top + target_height))


def _prepare_panel(image, target_size):
    """Fill a panel while keeping a complete sharp image visible on mismatch."""
    target_width, target_height = target_size
    source_ratio = float(image.size[0]) / float(image.size[1])
    target_ratio = float(target_width) / float(target_height)

    if abs(source_ratio - target_ratio) / target_ratio <= 0.015:
        return image.resize(target_size, _resample_filter())

    background = _center_cover(image, target_size)
    blur_radius = max(20, min(target_size) // 28)
    background = background.filter(ImageFilter.GaussianBlur(blur_radius))
    background = ImageEnhance.Brightness(background).enhance(0.78)

    sharp_size = _fit_dimensions(image.size, target_size)
    sharp = image.resize(sharp_size, _resample_filter())
    x = (target_width - sharp_size[0]) // 2
    y = (target_height - sharp_size[1]) // 2
    background.alpha_composite(sharp, (x, y))
    return background


def _mix_color(first, second, amount):
    return tuple(
        int(round(first[index] * (1.0 - amount) + second[index] * amount))
        for index in range(3)
    )


def _derive_transition_colors(scene):
    sample = scene.convert("RGB").resize((48, 48), _resample_filter())
    candidates = []
    for color in sample.getdata():
        brightness = sum(color) / 3.0
        saturation = max(color) - min(color)
        if 38 <= brightness <= 230 and saturation >= 35:
            score = saturation * (1.0 - abs(brightness - 145.0) / 260.0)
            candidates.append((score, color))
    if not candidates:
        return (82, 151, 139), (224, 112, 78)
    candidates.sort(key=lambda item: item[0], reverse=True)
    primary = candidates[0][1]
    secondary = max(
        (item[1] for item in candidates[:180]),
        key=lambda color: sum(
            (color[index] - primary[index]) ** 2 for index in range(3)
        ),
    )
    return primary, secondary


def _jagged_line(length, baseline, amplitude, rng):
    points = [(0, baseline + rng.randint(-amplitude, amplitude))]
    x = 0
    while x < length:
        x = min(length, x + rng.randint(18, 42))
        points.append((x, baseline + rng.randint(-amplitude, amplitude)))
    return points


def _transition_strip(length, width, scene, seed):
    """Create a deterministic horizontal torn-paper transition strip."""
    primary, secondary = _derive_transition_colors(scene)
    rng = random.Random(seed)
    strip = Image.new("RGBA", (length, width), DIVIDER_COLOR + (255,))
    draw = ImageDraw.Draw(strip)

    paper_shadow = _mix_color(DIVIDER_COLOR, FIBER_DARK, 0.34)
    paper_highlight = _mix_color(DIVIDER_COLOR, FIBER_LIGHT, 0.64)
    for _ in range(max(90, length // 3)):
        x = rng.randrange(0, length)
        y = rng.randrange(0, width)
        color = rng.choice((paper_shadow, paper_highlight, DIVIDER_COLOR))
        radius = rng.choice((1, 1, 1, 2))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color + (75,))

    amplitude = max(2, min(7, width // 7))
    top_line = _jagged_line(length, amplitude + 2, amplitude, rng)
    bottom_line = _jagged_line(length, width - amplitude - 3, amplitude, rng)

    shadow = Image.new("RGBA", strip.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.line(top_line, fill=(44, 35, 28, 105), width=7)
    shadow_draw.line(bottom_line, fill=(44, 35, 28, 105), width=7)
    shadow = shadow.filter(ImageFilter.GaussianBlur(3))
    strip = Image.alpha_composite(strip, shadow)
    draw = ImageDraw.Draw(strip)
    draw.line(top_line, fill=paper_highlight + (255,), width=2)
    draw.line(bottom_line, fill=paper_shadow + (235,), width=2)

    for points, inward in ((top_line, 1), (bottom_line, -1)):
        for _ in range(max(28, length // 38)):
            x = rng.randrange(4, max(5, length - 4))
            nearest = min(points, key=lambda point: abs(point[0] - x))
            y = nearest[1]
            fiber_length = rng.randint(3, max(4, width // 5))
            draw.line(
                (x, y, x + rng.randint(-3, 3), y + inward * fiber_length),
                fill=rng.choice((paper_shadow, paper_highlight)) + (145,),
                width=1,
            )

    centers = (width * 2 // 5, width * 3 // 5)
    for color, center, line_width in (
        (primary, centers[0], 4),
        (secondary, centers[1], 3),
    ):
        points = []
        x = -20
        while x <= length + 20:
            points.append((x, center + rng.randint(-3, 3)))
            x += rng.randint(24, 48)
        draw.line(points, fill=color + (185,), width=line_width)
        highlight = _mix_color(color, FIBER_LIGHT, 0.42)
        draw.line(
            [(x, y - 2) for x, y in points],
            fill=highlight + (110,),
            width=1,
        )

    for _ in range(max(18, length // 70)):
        x = rng.randrange(5, max(6, length - 5))
        y = rng.randrange(max(4, width // 5), max(5, width * 4 // 5))
        color = rng.choice((primary, secondary, paper_shadow))
        radius = rng.choice((1, 2, 3))
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color + (155,))
    return strip


def _paste_transition(canvas, scene, panel_size, transition_width, stacked):
    seed = panel_size[0] * 1000003 + panel_size[1] * 97 + transition_width
    if stacked:
        strip = _transition_strip(panel_size[0], transition_width, scene, seed)
        canvas.alpha_composite(strip, (0, panel_size[1]))
        return
    strip = _transition_strip(panel_size[1], transition_width, scene, seed + 31)
    strip = strip.transpose(Image.ROTATE_90)
    canvas.alpha_composite(strip, (panel_size[0], 0))


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


def compose_make_it_alive(
    photo_path,
    scene_path,
    output_path,
    long_edge=DEFAULT_LONG_EDGE,
    transition_width=DEFAULT_TRANSITION_WIDTH,
    gap=None,
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
    if long_edge < 320 or long_edge > 4096:
        raise ValueError("Long edge must be between 320 and 4096 pixels.")
    if gap is not None:
        transition_width = gap
    if transition_width < 16 or transition_width > 160:
        raise ValueError("Transition width must be between 16 and 160 pixels.")

    photo = _load_image(photo_path)
    scene = _load_image(scene_path)
    panel_size = _panel_size(photo.size, long_edge=long_edge)

    source_panel = _prepare_panel(photo, panel_size)
    scene_panel = _prepare_panel(scene, panel_size)

    stacked = photo.size[0] > photo.size[1]
    if stacked:
        canvas_size = (panel_size[0], panel_size[1] * 2 + transition_width)
        source_position = (0, 0)
        scene_position = (0, panel_size[1] + transition_width)
    else:
        canvas_size = (panel_size[0] * 2 + transition_width, panel_size[1])
        source_position = (0, 0)
        scene_position = (panel_size[0] + transition_width, 0)

    canvas = Image.new("RGBA", canvas_size, DIVIDER_COLOR + (255,))
    canvas.alpha_composite(source_panel, source_position)
    canvas.alpha_composite(scene_panel, scene_position)
    _paste_transition(canvas, scene, panel_size, transition_width, stacked)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_path = next_available_path(output_path)
    canvas.convert("RGB").save(str(final_path), format="PNG", optimize=True)
    return final_path


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Compose an original photo and anime transformation with no text."
    )
    parser.add_argument("--photo", required=True, help="Untouched source photo")
    parser.add_argument("--scene", required=True, help="Text-free anime scene")
    parser.add_argument("--output", required=True, help="Requested PNG output path")
    parser.add_argument(
        "--long-edge",
        type=int,
        default=DEFAULT_LONG_EDGE,
        help="Long edge of each image panel (default: 1600)",
    )
    parser.add_argument(
        "--transition-width",
        "--gap",
        dest="transition_width",
        type=int,
        default=DEFAULT_TRANSITION_WIDTH,
        help="Torn-paper transition width in pixels (default: 48; --gap is an alias)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    try:
        final_path = compose_make_it_alive(
            photo_path=args.photo,
            scene_path=args.scene,
            output_path=args.output,
            long_edge=args.long_edge,
            transition_width=args.transition_width,
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        print("error: {}".format(error), file=sys.stderr)
        return 2
    print(str(final_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
