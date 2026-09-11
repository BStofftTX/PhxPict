import os
from pathlib import Path
import tempfile
import unittest

from PIL import Image

from phxpict.database import PhotoDatabase
from phxpict.indexer import index_folder, iter_images
from phxpict.providers import FilenameTagProvider


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


if __name__ == "__main__":
    unittest.main()

