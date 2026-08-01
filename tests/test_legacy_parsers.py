"""Regression tests for legacy DC/NGC source parsing."""

import sys
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from drop_data import iter_cell_drops  # noqa: E402
from parse_dc import parse_dc_cell  # noqa: E402
from source_html import read_legacy_html  # noqa: E402


class DcCellTest(unittest.TestCase):
    """Verify DC cells retain every item/rate pair."""

    def test_multiple_drops(self):
        td = BeautifulSoup(
            "<td>Item A<br>1.25%<br>Item B<br>0.5%</td>",
            "html.parser",
        ).find("td")

        self.assertEqual(
            list(iter_cell_drops(parse_dc_cell(td))),
            [
                {"item": "Item A", "rate": "1.25%"},
                {"item": "Item B", "rate": "0.5%"},
            ],
        )


class SourceHtmlTest(unittest.TestCase):
    """Verify an explicit source directory takes priority over Git history."""

    def test_reads_explicit_source_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "n.html"
            path.write_text("<html>fixture</html>", encoding="utf-8")

            self.assertEqual(
                read_legacy_html("dc", "n.html", source_dir=directory),
                "<html>fixture</html>",
            )


if __name__ == "__main__":
    unittest.main()
