from __future__ import print_function

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "make-it-alive" / "scripts" / "compose_make_it_alive.py"
SPEC = importlib.util.spec_from_file_location("compose_make_it_alive", str(SCRIPT))
COMPOSER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(COMPOSER)


def file_hash(path):
    digest = hashlib.sha256()
    with open(str(path), "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_fixture(path, size, base, accent):
    image = Image.new("RGB", size, base)
    draw = ImageDraw.Draw(image)
    margin = max(10, min(size) // 10)
    draw.rectangle(
        (margin, margin, size[0] - margin, size[1] - margin),
        outline=accent,
        width=max(5, margin // 3),
    )
    draw.ellipse(
        (size[0] // 3, size[1] // 4, size[0] * 2 // 3, size[1] * 3 // 4),
        fill=accent,
    )
    image.save(str(path), format="PNG")


class ComposeMakeItAliveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scene = self.root / "anime-scene.png"
        make_fixture(self.scene, (1200, 900), (77, 155, 211), (247, 147, 65))

    def tearDown(self):
        self.temp.cleanup()

    def compose(self, photo, output, scene=None, long_edge=800, gap=12):
        return COMPOSER.compose_make_it_alive(
            photo_path=photo,
            scene_path=scene or self.scene,
            output_path=output,
            long_edge=long_edge,
            gap=gap,
        )

    def test_landscape_stacks_original_above_scene(self):
        photo = self.root / "landscape.png"
        landscape_scene = self.root / "landscape-scene.png"
        make_fixture(photo, (1600, 900), (30, 55, 80), (238, 205, 95))
        make_fixture(
            landscape_scene, (1600, 900), (77, 155, 211), (247, 147, 65)
        )
        result = self.compose(
            photo, self.root / "stacked.png", scene=landscape_scene
        )
        with Image.open(str(result)) as final_image:
            self.assertEqual((800, 912), final_image.size)
            self.assertEqual((30, 55, 80), final_image.getpixel((5, 5)))
            self.assertEqual((77, 155, 211), final_image.getpixel((5, 467)))
            self.assertEqual(COMPOSER.DIVIDER_COLOR, final_image.getpixel((5, 455)))

    def test_portrait_places_original_left_and_scene_right(self):
        photo = self.root / "portrait.png"
        make_fixture(photo, (900, 1600), (42, 69, 91), (231, 196, 91))
        portrait_scene = self.root / "portrait-scene.png"
        make_fixture(portrait_scene, (900, 1600), (86, 166, 204), (244, 131, 78))
        result = self.compose(
            photo, self.root / "side-by-side.png", scene=portrait_scene
        )
        with Image.open(str(result)) as final_image:
            self.assertEqual((912, 800), final_image.size)
            self.assertEqual((42, 69, 91), final_image.getpixel((5, 5)))
            self.assertEqual((86, 166, 204), final_image.getpixel((467, 5)))
            self.assertEqual(COMPOSER.DIVIDER_COLOR, final_image.getpixel((455, 5)))

    def test_square_uses_side_by_side_layout(self):
        photo = self.root / "square.png"
        scene = self.root / "square-scene.png"
        make_fixture(photo, (1000, 1000), (48, 72, 104), (235, 202, 84))
        make_fixture(scene, (1000, 1000), (78, 157, 205), (245, 135, 71))
        result = self.compose(photo, self.root / "square-final.png", scene=scene)
        with Image.open(str(result)) as final_image:
            self.assertEqual((1612, 800), final_image.size)

    def test_landscape_portrait_and_square_keep_source_hash_unchanged(self):
        cases = [(1600, 900), (900, 1600), (1000, 1000)]
        for index, size in enumerate(cases):
            with self.subTest(size=size):
                photo = self.root / "source-{}.png".format(index)
                make_fixture(photo, size, (51, 81, 103), (234, 196, 80))
                before = file_hash(photo)
                self.compose(photo, self.root / "result-{}.png".format(index))
                self.assertEqual(before, file_hash(photo))

    def test_mismatched_scene_ratio_fills_panel_without_transparency(self):
        photo = self.root / "landscape.png"
        scene = self.root / "portrait-scene.png"
        make_fixture(photo, (1600, 900), (40, 62, 83), (232, 193, 79))
        make_fixture(scene, (700, 1200), (83, 162, 206), (246, 137, 72))
        result = self.compose(photo, self.root / "mismatch.png", scene=scene)
        with Image.open(str(result)).convert("RGBA") as final_image:
            self.assertEqual((800, 912), final_image.size)
            self.assertTrue(all(pixel[3] == 255 for pixel in final_image.getdata()))

    def test_existing_output_gets_versioned_name(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (1200, 900), (45, 69, 92), (232, 196, 82))
        output = self.root / "make-it-alive.png"
        first = self.compose(photo, output)
        second = self.compose(photo, output)
        self.assertEqual("make-it-alive.png", first.name)
        self.assertEqual("make-it-alive-v2.png", second.name)

    def test_cli_requires_only_photo_scene_and_output(self):
        parsed = COMPOSER.parse_args(
            [
                "--photo",
                "photo.png",
                "--scene",
                "scene.png",
                "--output",
                "final.png",
            ]
        )
        self.assertEqual("photo.png", parsed.photo)
        self.assertEqual("scene.png", parsed.scene)
        self.assertEqual("final.png", parsed.output)
        self.assertFalse(hasattr(parsed, "name"))
        self.assertFalse(hasattr(parsed, "font"))

    def test_invalid_size_controls_are_rejected(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (1200, 900), (45, 69, 92), (232, 196, 82))
        with self.assertRaisesRegex(ValueError, "Long edge"):
            self.compose(photo, self.root / "small.png", long_edge=200)
        with self.assertRaisesRegex(ValueError, "Gap"):
            self.compose(photo, self.root / "wide-gap.png", gap=200)

    def test_missing_scene_has_actionable_error(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (1200, 900), (45, 69, 92), (232, 196, 82))
        with self.assertRaisesRegex(FileNotFoundError, "Transformed scene"):
            self.compose(
                photo,
                self.root / "missing.png",
                scene=self.root / "missing-scene.png",
            )


if __name__ == "__main__":
    unittest.main()
