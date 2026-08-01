"""Regression tests for Ephinea drop-cell parsing."""

import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from drop_data import iter_cell_drops  # noqa: E402
from scraper import parse_drop_cell, parse_entry_drop_rate  # noqa: E402


class ParseDropCellTest(unittest.TestCase):
    """Verify single- and multi-item section-ID cells."""

    def parse(self, html):
        """Parse a test ``td`` and return the scraper's cell mapping."""
        td = BeautifulSoup(html, "html.parser").find("td")
        return parse_drop_cell(td)

    def test_single_drop_preserves_legacy_shape(self):
        cell = self.parse(
            "<td><b>Vjaya</b><abbr><sup>1</sup>/<sub>630.1</sub></abbr></td>"
        )

        self.assertEqual(cell, {"item": "Vjaya", "rate": "1/630.1"})

    def test_multiple_drops_are_preserved_in_one_cell(self):
        cell = self.parse(
            "<td>"
            "<b>Vjaya</b><abbr><sup>1</sup>/<sub>630.1</sub></abbr>"
            "<br><b>AddSlot</b><abbr><sup>1</sup>/<sub>1170.3</sub></abbr>"
            "</td>"
        )

        self.assertEqual(
            list(iter_cell_drops(cell)),
            [
                {"item": "Vjaya", "rate": "1/630.1"},
                {"item": "AddSlot", "rate": "1/1170.3"},
            ],
        )

    def test_empty_cell_preserves_legacy_shape(self):
        self.assertEqual(
            self.parse("<td>&nbsp;</td>"),
            {"item": "", "rate": ""},
        )

    def test_japanese_overall_drop_rate(self):
        td = BeautifulSoup(
            '<td><abbr title="ドロップ率: 1/1.2 (85%)&#10;レア率: 1/315.1">'
            "<b>アイテム</b></abbr></td>",
            "html.parser",
        ).find("td")

        self.assertEqual(parse_entry_drop_rate(td), "1/1.2")


if __name__ == "__main__":
    unittest.main()
