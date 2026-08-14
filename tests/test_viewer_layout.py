"""Regression tests for the responsive drop-chart table contract."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parent.parent


class ViewerLayoutTest(unittest.TestCase):
    """Keep the frozen-label layout stable across renderer changes."""

    @classmethod
    def setUpClass(cls):
        cls.viewer = (ROOT / "shared" / "viewer.js").read_text(encoding="utf-8")
        cls.styles = (ROOT / "shared" / "style.css").read_text(encoding="utf-8")

    def test_renderer_has_one_label_column(self):
        self.assertEqual(self.viewer.count('<th class="monster-col">'), 1)
        self.assertEqual(self.viewer.count('<td class="monster-name"'), 1)
        self.assertIn("data.sectionIds.length + 1", self.viewer)
        self.assertNotIn("data.sectionIds.length + 2", self.viewer)

    def test_label_header_and_cells_are_frozen(self):
        for selector in ("th.monster-col", "td.monster-name"):
            block = re.search(
                rf"\.drop-table {re.escape(selector)} \{{(?P<body>.*?)\n\}}",
                self.styles,
                re.DOTALL,
            )
            self.assertIsNotNone(block, selector)
            self.assertIn("position: sticky", block.group("body"))
            self.assertIn("left: 0", block.group("body"))

    def test_area_labels_track_the_scrollport_center(self):
        self.assertIn('class="area-label"', self.viewer)
        self.assertIn("wrap.clientWidth / 2", self.viewer)
        self.assertIn("--area-label-center", self.viewer)
        self.assertIn("left: var(--area-label-center", self.styles)

    def test_search_normalizes_mixed_width_names(self):
        self.assertIn("text.normalize('NFKC').toLowerCase()", self.viewer)
        self.assertIn("term.normalize('NFKC').toLowerCase()", self.viewer)


if __name__ == "__main__":
    unittest.main()
