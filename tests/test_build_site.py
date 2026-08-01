import tempfile
import unittest
from pathlib import Path

from tools import build_site


class BuildSiteTest(unittest.TestCase):
    def test_builds_complete_versioned_pages_artifact(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory) / "site"

            file_count = build_site.build_site(
                output_dir,
                asset_version="test-version",
            )

            self.assertGreater(file_count, 0)
            self.assertEqual(
                (output_dir / "CNAME").read_text(encoding="utf-8"),
                "dropcharts.psohaven.com\n",
            )
            self.assertTrue((output_dir / "bb" / "data" / "en.js").is_file())
            self.assertTrue((output_dir / "dc" / "data" / "en.js").is_file())
            self.assertTrue((output_dir / "ngc" / "data" / "en.js").is_file())

            html = (output_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("?v=test-version", html)
            self.assertNotIn("__ASSET_VERSION__", html)

    def test_rejects_repository_root_as_output(self):
        with self.assertRaises(ValueError):
            build_site.build_site(
                build_site.ROOT,
                asset_version="test-version",
            )
