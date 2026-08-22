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
        self.creature = self.root / "creature.png"
        make_fixture(
            self.creature, (1024, 1024), (245, 236, 215), (73, 130, 105)
        )

    def tearDown(self):
        self.temp.cleanup()

    def compose(self, photo, output, lore=None, font_path=None):
        return COMPOSER.compose_journal(
            photo_path=photo,
            creature_path=self.creature,
            name="瓷眠兽",
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

    def test_missing_explicit_font_has_actionable_error(self):
        photo = self.root / "photo.png"
        make_fixture(photo, (900, 900), (120, 130, 150), (220, 190, 90))
        with self.assertRaisesRegex(FileNotFoundError, "--font"):
            self.compose(
                photo,
                self.root / "missing-font.png",
                font_path=str(self.root / "missing-font.ttf"),
            )


if __name__ == "__main__":
    unittest.main()
