from __future__ import print_function

import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from PIL import Image, ImageChops, ImageDraw


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


class ComposeMakeItAliveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.scene = self.root / "transformed-scene.png"
        make_fixture(
            self.scene, (1200, 900), (143, 205, 224), (247, 139, 86)
        )

    def tearDown(self):
        self.temp.cleanup()

    def compose(self, photo, output, font_path=None, intro=None):
        return COMPOSER.compose_make_it_alive(
            photo_path=photo,
            scene_path=self.scene,
            name="茶咕",
            personality="慢热好奇",
            hobby="收集清晨露珠",
            intro=intro
            or "有人靠近时，它会先躲到杯柄后面，确认安全才慢慢探出头。",
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
                    photo, self.root / "make-it-alive-{}.png".format(index)
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

    def test_cover_dimensions_fill_landscape_and_portrait_windows(self):
        target = (944, 1132)
        for source in [(1600, 900), (900, 1600), (1024, 1024)]:
            with self.subTest(source=source):
                fitted = COMPOSER._fit_cover_dimensions(source, target)
                self.assertGreaterEqual(fitted[0], target[0])
                self.assertGreaterEqual(fitted[1], target[1])
                self.assertTrue(fitted[0] == target[0] or fitted[1] == target[1])

    def test_source_card_changes_silhouette_with_photo_orientation(self):
        landscape = COMPOSER._source_card_layout((1600, 900))["card"]
        portrait = COMPOSER._source_card_layout((900, 1600))["card"]
        square = COMPOSER._source_card_layout((1000, 1000))["card"]
        landscape_size = (landscape[2] - landscape[0], landscape[3] - landscape[1])
        portrait_size = (portrait[2] - portrait[0], portrait[3] - portrait[1])
        square_size = (square[2] - square[0], square[3] - square[1])
        self.assertGreater(landscape_size[0], landscape_size[1])
        self.assertLess(portrait_size[0], portrait_size[1])
        self.assertLess(square_size[0], square_size[1])
        self.assertNotEqual(landscape, portrait)

    def test_showcase_uses_blurred_fill_and_complete_sharp_layer(self):
        target = (40, 40, 440, 640)
        for index, source in enumerate([(900, 500), (500, 900)]):
            with self.subTest(source=source):
                fixture = self.root / "showcase-{}.png".format(index)
                make_fixture(fixture, source, (34, 66, 104), (242, 190, 72))
                with Image.open(str(fixture)) as opened:
                    image = opened.convert("RGBA")
                canvas = Image.new("RGBA", (500, 700), (0, 0, 0, 0))
                sharp_box = COMPOSER._paste_showcase(
                    canvas, image, target, (72, 150, 138), seed=30 + index
                )
                self.assertGreaterEqual(sharp_box[0], target[0])
                self.assertGreaterEqual(sharp_box[1], target[1])
                self.assertLessEqual(sharp_box[2], target[2])
                self.assertLessEqual(sharp_box[3], target[3])
                sharp_size = (sharp_box[2] - sharp_box[0], sharp_box[3] - sharp_box[1])
                self.assertAlmostEqual(
                    float(source[0]) / float(source[1]),
                    float(sharp_size[0]) / float(sharp_size[1]),
                    places=2,
                )
                self.assertGreater(canvas.getpixel((target[0] + 2, target[1] + 2))[3], 0)

    def test_existing_output_gets_versioned_name(self):
        photo = self.root / "photo.png"
        output = self.root / "make-it-alive.png"
        make_fixture(photo, (1200, 900), (120, 150, 110), (235, 190, 95))
        first = self.compose(photo, output)
        second = self.compose(photo, output)
        self.assertEqual("make-it-alive.png", first.name)
        self.assertEqual("make-it-alive-v2.png", second.name)

    def test_missing_explicit_font_has_actionable_error(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 900), (120, 130, 150), (220, 190, 90))
        with self.assertRaisesRegex(FileNotFoundError, "--font"):
            self.compose(
                photo,
                self.root / "missing-font.png",
                font_path=str(self.root / "missing-font.ttf"),
            )

    def test_bundled_cjk_font_is_the_default(self):
        regular, bold = COMPOSER.resolve_fonts()
        self.assertEqual(COMPOSER.BUNDLED_FONT.resolve(), Path(regular).resolve())
        self.assertEqual(COMPOSER.BUNDLED_FONT.resolve(), Path(bold).resolve())
        self.assertTrue(COMPOSER.BUNDLED_FONT.is_file())
        self.assertEqual(
            COMPOSER.FONT_SHA256, COMPOSER._file_sha256(COMPOSER.BUNDLED_FONT)
        )

    def test_missing_bundle_and_system_font_use_automatic_fallback(self):
        fallback = str(COMPOSER.BUNDLED_FONT)
        with mock.patch.object(
            COMPOSER, "BUNDLED_FONT", self.root / "missing-font.otf"
        ), mock.patch.object(
            COMPOSER, "REGULAR_FONT_CANDIDATES", []
        ), mock.patch.object(
            COMPOSER, "BOLD_FONT_CANDIDATES", []
        ), mock.patch.object(
            COMPOSER, "_download_verified_font", return_value=fallback
        ) as download:
            regular, bold = COMPOSER.resolve_fonts()
        download.assert_called_once_with()
        self.assertEqual(fallback, regular)
        self.assertEqual(fallback, bold)

    def test_bundled_font_license_is_packaged(self):
        license_path = COMPOSER.BUNDLED_FONT.with_name("OFL.txt")
        self.assertTrue(license_path.is_file())
        self.assertIn("SIL OPEN FONT LICENSE", license_path.read_text(encoding="utf-8"))

    def test_intro_wrap_does_not_orphan_chinese_punctuation(self):
        image = Image.new("RGB", (1000, 200), "white")
        draw = ImageDraw.Draw(image)
        font, lines = COMPOSER._wrapped_font_that_fits(
            draw,
            "它最喜欢在午后的阳光里把纸巾铺平，听见脚步声就立刻钻回柔软的褶皱里。",
            str(COMPOSER.BUNDLED_FONT),
            max_width=878,
            max_lines=2,
            start_size=26,
            min_size=21,
        )
        self.assertIsNotNone(font)
        self.assertFalse(
            any(
                line and line[0] in COMPOSER.CLOSING_PUNCTUATION
                for line in lines[1:]
            )
        )

    def test_scene_palette_is_dynamic_and_keeps_lively_accents(self):
        warm_scene = Image.new("RGB", (120, 120), (196, 78, 44))
        cool_scene = Image.new("RGB", (120, 120), (45, 105, 178))
        warm_accent, _ = COMPOSER._derive_palette(warm_scene)
        cool_accent, _ = COMPOSER._derive_palette(cool_scene)
        self.assertNotEqual(warm_accent, cool_accent)
        for accent in (warm_accent, cool_accent):
            channel_range = max(accent) - min(accent)
            self.assertGreaterEqual(channel_range, 45)

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
                "--intro",
                "怕冷时会把自己埋进纸巾里，只露出两只耳朵听房间里的动静。",
                "--output",
                "make-it-alive.png",
            ]
        )
        self.assertEqual("scene.png", parsed.scene)
        self.assertTrue(parsed.intro.startswith("怕冷时"))
        self.assertFalse(hasattr(parsed, "creature"))

    def test_lore_alias_maps_to_intro_for_compatibility(self):
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
                "紧张时会缩进杯口，只留一双眼睛观察周围。",
                "--output",
                "make-it-alive.png",
            ]
        )
        self.assertEqual(
            "紧张时会缩进杯口，只留一双眼睛观察周围。", parsed.intro
        )

    def test_small_intro_is_rendered_in_the_final_spread(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (1200, 900), (120, 150, 110), (235, 190, 95))
        first = self.compose(
            photo,
            self.root / "intro-a.png",
            intro="怕冷时会钻进纸巾下面，只露出一双耳朵听门外的声音。",
        )
        second = self.compose(
            photo,
            self.root / "intro-b.png",
            intro="晒够太阳以后，它会沿着桌边慢慢巡一圈，再回到原位。",
        )
        with Image.open(str(first)) as first_image, Image.open(
            str(second)
        ) as second_image:
            first_region = first_image.crop((1300, 1228, 2290, 1396))
            second_region = second_image.crop((1300, 1228, 2290, 1396))
            self.assertIsNotNone(
                ImageChops.difference(first_region, second_region).getbbox()
            )

    def test_empty_intro_is_rejected(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 900), (120, 130, 150), (220, 190, 90))
        with self.assertRaisesRegex(ValueError, "Introduction must not be empty"):
            self.compose(photo, self.root / "empty-intro.png", intro="   ")

    def test_missing_scene_has_actionable_error(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 900), (120, 130, 150), (220, 190, 90))
        with self.assertRaisesRegex(FileNotFoundError, "Transformed scene"):
            COMPOSER.compose_make_it_alive(
                photo_path=photo,
                scene_path=self.root / "missing-scene.png",
                name="茶咕",
                personality="慢热好奇",
                hobby="收集清晨露珠",
                intro="怕冷时会钻进纸巾下面，只露出一双耳朵听门外的声音。",
                output_path=self.root / "missing-scene.png",
            )


if __name__ == "__main__":
    unittest.main()
