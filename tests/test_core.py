import os
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from phxpict.database import PhotoDatabase
from phxpict.indexer import index_folder, iter_images
from phxpict.providers import (
    FilenameTagProvider,
    GracefulFallbackTagProvider,
    LocalCLIPTagProvider,
    ProviderUnavailableError,
    VISUAL_CATEGORY_LABELS,
    OTHER_VISUAL_LABEL,
)


class PixelAwareClassifier:
    """Tiny test double that reads pixels, proving paths reach visual inference."""

    def __init__(self):
        self.pixel_seen = None

    def __call__(self, image_path, *, candidate_labels, hypothesis_template):
        with Image.open(image_path) as image:
            self.pixel_seen = image.convert("RGB").getpixel((0, 0))
        scores = {label: 0.01 for label in candidate_labels}
        needle = "an airplane, aircraft, jet, or aviation scene"
        scores[needle] = 0.92 if self.pixel_seen == (255, 0, 0) else 0.01
        return [{"label": label, "score": score} for label, score in scores.items()]


class MissingVisualProvider(LocalCLIPTagProvider):
    def tags_for(self, image_path):
        raise ProviderUnavailableError("optional model unavailable")


class CategoryPixelClassifier:
    def __init__(self, color_to_label):
        self.color_to_label = color_to_label

    def __call__(self, image_path, *, candidate_labels, hypothesis_template):
        with Image.open(image_path) as image:
            red = image.convert("RGB").getpixel((0, 0))[0]
        target = self.color_to_label[red]
        return [
            {"label": label, "score": 0.95 if label == target else 0.01}
            for label in candidate_labels
        ]


class OtherPixelClassifier:
    def __call__(self, image_path, *, candidate_labels, hypothesis_template):
        return [
            {"label": label, "score": 0.98 if label == OTHER_VISUAL_LABEL else 0.01}
            for label in candidate_labels
        ]


class CoreTests(unittest.TestCase):
    def test_filename_categories(self):
        provider = FilenameTagProvider()
        self.assertEqual(provider.tags_for(Path("family/portrait_at_beach.jpg")), ["nature", "people"])
        self.assertEqual(provider.tags_for(Path("museum/war_plane.png")), ["planes", "warfare"])

    def test_index_and_search(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image_path = root / "family_car.jpg"
            Image.new("RGB", (64, 32), "blue").save(image_path)
            timestamp = 1_700_000_000
            os.utime(image_path, (timestamp, timestamp))
            database = PhotoDatabase(root / "index.sqlite3")
            self.assertEqual(index_folder(root, database), 1)
            results = database.search("automobiles")
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].width, 64)
            self.assertIn("people", results[0].tags)
            by_date = database.search(date_field="modified_date", start="2023-01-01", end="2024-12-31")
            self.assertEqual(len(by_date), 1)
            database.close()

    def test_supported_extensions_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "note.txt").write_text("ignore")
            Image.new("RGB", (1, 1)).save(root / "photo.png")
            self.assertEqual([p.name for p in iter_images(root)], ["photo.png"])

    def test_search_pagination_and_count(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            database = PhotoDatabase(root / "index.sqlite3")
            for number in range(5):
                image_path = root / f"nature_{number}.png"
                Image.new("RGB", (2, 2), "green").save(image_path)
            self.assertEqual(index_folder(root, database), 5)
            self.assertEqual(database.search_count("nature"), 5)
            first = database.search("nature", limit=2, offset=0)
            second = database.search("nature", limit=2, offset=2)
            self.assertEqual(len(first), 2)
            self.assertEqual(len(second), 2)
            self.assertNotEqual({p.path for p in first}, {p.path for p in second})
            database.close()

    def test_local_visual_provider_reads_pixels_and_indexes_tags(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            image_path = root / "unlabeled.png"
            Image.new("RGB", (8, 8), (255, 0, 0)).save(image_path)
            classifier = PixelAwareClassifier()
            provider = LocalCLIPTagProvider(classifier=classifier)
            database = PhotoDatabase(root / "index.sqlite3")
            self.assertEqual(index_folder(root, database, provider=provider), 1)
            self.assertEqual(classifier.pixel_seen, (255, 0, 0))
            results = database.search("planes")
            self.assertEqual(len(results), 1)
            self.assertIn("planes", results[0].tags)
            database.close()

    def test_visual_dependency_failure_falls_back_to_filename_tags(self):
        provider = GracefulFallbackTagProvider(MissingVisualProvider())
        tags = provider.tags_for(Path("family/portrait_at_beach.jpg"))
        self.assertEqual(tags, ["nature", "people"])
        self.assertFalse(provider.primary_enabled)
        self.assertIn("unavailable", provider.fallback_reason)

    def test_ambiguous_images_can_remain_untagged(self):
        provider = LocalCLIPTagProvider(classifier=OtherPixelClassifier())
        self.assertEqual(provider.tags_for(Path("abstract-image.jpg")), [])

    def test_all_requested_visual_categories_are_searchable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            color_to_label = {}
            for red, (category, label) in enumerate(VISUAL_CATEGORY_LABELS.items(), start=1):
                color_to_label[red] = label
                Image.new("RGB", (4, 4), (red, 0, 0)).save(root / f"image_{red}.png")
            provider = LocalCLIPTagProvider(classifier=CategoryPixelClassifier(color_to_label))
            database = PhotoDatabase(root / "index.sqlite3")
            self.assertEqual(index_folder(root, database, provider=provider), 7)
            for category in VISUAL_CATEGORY_LABELS:
                with self.subTest(category=category):
                    results = database.search(category)
                    self.assertEqual(len(results), 1)
                    self.assertIn(category, results[0].tags)
            database.close()


if __name__ == "__main__":
    unittest.main()
