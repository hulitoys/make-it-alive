from __future__ import print_function

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "huanling-journal" / "scripts" / "compose_journal.py"
SPEC = importlib.util.spec_from_file_location("compose_journal", str(SCRIPT))
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
    margin = max(12, min(size) // 12)
    draw.rectangle(
        (margin, margin, size[0] - margin, size[1] - margin),
        outline=accent,
        width=max(6, margin // 3),
    )
    draw.ellipse(
        (
            size[0] // 3,
            size[1] // 4,
            size[0] * 2 // 3,
            size[1] * 3 // 4,
        ),
        fill=accent,
    )
    image.save(str(path), format="PNG")


class ComposeJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scene = self.root / "transformed-scene.png"
        make_fixture(
            self.scene, (1200, 900), (143, 205, 224), (247, 139, 86)
        )

    def tearDown(self):
        self.temp.cleanup()

    def compose(self, photo, output, lore=None, font_path=None):
        return COMPOSER.compose_journal(
            photo_path=photo,
            scene_path=self.scene,
            name="茶咕",
            personality="慢热好奇",
            hobby="收集清晨露珠",
            lore=lore
            or "受惊时，它会合拢杯沿般的耳翼，让积存的雨声滚成低低的警告。",
            output_path=output,
            font_path=font_path,
        )

    def test_landscape_portrait_and_square_keep_source_unchanged(self):
        cases = [(1600, 900), (900, 1600), (1024, 1024)]
        for index, size in enumerate(cases):
            with self.subTest(size=size):
                photo = self.root / "photo-{}.png".format(index)
                make_fixture(photo, size, (92, 139, 179), (250, 204, 96))
                before = file_hash(photo)
                result = self.compose(
                    photo, self.root / "journal-{}.png".format(index)
                )
                after = file_hash(photo)
                self.assertEqual(before, after)
                self.assertTrue(result.is_file())
                with Image.open(str(result)) as final_image:
                    self.assertEqual(COMPOSER.CANVAS_SIZE, final_image.size)
                    self.assertEqual("PNG", final_image.format)

    def test_containment_preserves_aspect_ratio_without_crop(self):
        target = (1110, 1362)
        for source in [(1600, 900), (900, 1600), (1024, 1024)]:
            with self.subTest(source=source):
                fitted = COMPOSER._fit_dimensions(source, target)
                self.assertLessEqual(fitted[0], target[0])
                self.assertLessEqual(fitted[1], target[1])
                self.assertTrue(fitted[0] == target[0] or fitted[1] == target[1])
                self.assertAlmostEqual(
                    float(source[0]) / float(source[1]),
                    float(fitted[0]) / float(fitted[1]),
                    places=2,
                )

    def test_existing_output_gets_versioned_name(self):
        photo = self.root / "photo.png"
        output = self.root / "journal.png"
        make_fixture(photo, (1200, 900), (120, 150, 110), (235, 190, 95))
        first = self.compose(photo, output)
        second = self.compose(photo, output)
        self.assertEqual("journal.png", first.name)
        self.assertEqual("journal-v2.png", second.name)

    def test_long_lore_fits_without_failure(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 1400), (140, 105, 155), (225, 205, 95))
        lore = (
            "每当风从窗边经过，它就会把层层叶片竖成天线，收集屋里每一声细响，"
            "再悄悄藏进柔软的腹甲里。" * 3
        )
        result = self.compose(photo, self.root / "long-lore.png", lore=lore)
        self.assertTrue(result.is_file())

    def test_lore_uses_secondary_text_scale(self):
        regular_font, _ = COMPOSER.resolve_fonts()
        image = Image.new("RGB", (1000, 300), "white")
        draw = ImageDraw.Draw(image)
        font, lines = COMPOSER._fit_lore(
            draw,
            "听见幼鸟叫声时，它会走到树下抬起叶冠，为鸟巢挡住迎面吹来的风。",
            regular_font,
            870,
        )
        self.assertLessEqual(font.size, 32)
        self.assertLessEqual(len(lines), 2)

    def test_missing_explicit_font_has_actionable_error(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 900), (120, 130, 150), (220, 190, 90))
        with self.assertRaisesRegex(FileNotFoundError, "--font"):
            self.compose(
                photo,
                self.root / "missing-font.png",
                font_path=str(self.root / "missing-font.ttf"),
            )

    def test_cli_interface_uses_scene_argument(self):
        parsed = COMPOSER.parse_args(
            [
                "--photo",
                "photo.png",
                "--scene",
                "scene.png",
                "--name",
                "茶咕",
                "--personality",
                "慢热好奇",
                "--hobby",
                "收集清晨露珠",
                "--lore",
                "风起时，它会把耳翼转向最先响起的窗沿。",
                "--output",
                "journal.png",
            ]
        )
        self.assertEqual("scene.png", parsed.scene)
        self.assertFalse(hasattr(parsed, "creature"))

    def test_missing_scene_has_actionable_error(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 900), (120, 130, 150), (220, 190, 90))
        with self.assertRaisesRegex(FileNotFoundError, "Transformed scene"):
            COMPOSER.compose_journal(
                photo_path=photo,
                scene_path=self.root / "missing-scene.png",
                name="茶咕",
                personality="慢热好奇",
                hobby="收集清晨露珠",
                lore="风起时，它会把耳翼转向最先响起的窗沿。",
                output_path=self.root / "missing-scene.png",
            )


if __name__ == "__main__":
    unittest.main()
