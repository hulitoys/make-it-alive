#!/usr/bin/env python
"""Compose a source photo and its anime transformation with no added text."""

from __future__ import print_function

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError as error:
    raise SystemExit(
        "Pillow is required. Install it with: python -m pip install Pillow"
    ) from error


DEFAULT_LONG_EDGE = 1600
DEFAULT_GAP = 24
DIVIDER_COLOR = (244, 239, 226)


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
    gap=DEFAULT_GAP,
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
    if gap < 0 or gap > 160:
        raise ValueError("Gap must be between 0 and 160 pixels.")

    photo = _load_image(photo_path)
    scene = _load_image(scene_path)
    panel_size = _panel_size(photo.size, long_edge=long_edge)

    source_panel = _prepare_panel(photo, panel_size)
    scene_panel = _prepare_panel(scene, panel_size)

    if photo.size[0] > photo.size[1]:
        canvas_size = (panel_size[0], panel_size[1] * 2 + gap)
        source_position = (0, 0)
        scene_position = (0, panel_size[1] + gap)
    else:
        canvas_size = (panel_size[0] * 2 + gap, panel_size[1])
        source_position = (0, 0)
        scene_position = (panel_size[0] + gap, 0)

    canvas = Image.new("RGBA", canvas_size, DIVIDER_COLOR + (255,))
    canvas.alpha_composite(source_panel, source_position)
    canvas.alpha_composite(scene_panel, scene_position)

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
        "--gap",
        type=int,
        default=DEFAULT_GAP,
        help="Neutral divider width in pixels (default: 24)",
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
            gap=args.gap,
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        print("error: {}".format(error), file=sys.stderr)
        return 2
    print(str(final_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
