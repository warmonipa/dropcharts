"""Regression tests for the responsive drop-chart table contract."""

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parent.parent


class ViewerLayoutTest(unittest.TestCase):
    """Keep the frozen-label layout stable across renderer changes."""

    @classmethod
    def setUpClass(cls):
        cls.viewer = (ROOT / "src/app/chart/chart.component.html").read_text(encoding="utf-8")
        cls.viewport = (ROOT / "src/app/chart/table-viewport.directive.ts").read_text(encoding="utf-8")
        cls.model = (ROOT / "src/app/chart/chart-model.ts").read_text(encoding="utf-8")
        cls.styles = (ROOT / "shared" / "style.css").read_text(encoding="utf-8")

    def test_renderer_has_one_label_column(self):
        self.assertEqual(self.viewer.count('<th class="monster-col"'), 1)
        self.assertEqual(self.viewer.count('<td class="monster-name"'), 1)
        self.assertIn("chart().sections.length + 1", self.viewer)
        self.assertNotIn("chart().sections.length + 2", self.viewer)

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
        self.assertIn("wrap.clientWidth / 2", self.viewport)
        self.assertIn("--area-label-center", self.viewport)
        self.assertIn("left: var(--area-label-center", self.styles)

    def test_search_normalizes_mixed_width_names(self):
        self.assertIn("text.normalize('NFKC').toLowerCase()", self.model)
        self.assertIn("term.normalize('NFKC').toLowerCase()", self.model)

    def test_rare_items_use_rainbow_text_with_reduced_motion_support(self):
        self.assertIn("-webkit-text-fill-color: transparent", self.styles)
        self.assertIn("animation: ssRareRainbow 4s linear infinite", self.styles)
        self.assertIn("@keyframes ssRareRainbow", self.styles)
        self.assertRegex(
            self.styles,
            r"@media \(prefers-reduced-motion: reduce\)\s*\{\s*"
            r"\.drop-cell \.ss-rare-item\s*\{[^}]*animation: none",
        )
        self.assertRegex(self.styles, r"a\.item-name:focus-visible\s*\{[^}]*outline:\s*2px solid currentColor")


if __name__ == "__main__":
    unittest.main()
