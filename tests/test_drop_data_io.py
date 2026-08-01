"""Tests for the shared drop-data boundary."""

import sys
import tempfile
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from drop_data import (  # noqa: E402
    cell_shape_errors,
    dump_framed_js,
    iter_data_drops,
    load_framed_js,
    load_js_data,
    make_drop_cell,
    write_generated_js,
)


class DropDataIoTest(unittest.TestCase):
    """Verify every producer and consumer can share one file boundary."""

    def test_generated_file_round_trips_with_framing(self):
        data = {"data": {}}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "en.js"
            write_generated_js(
                path,
                data,
                language="en",
                generator="test",
                source="Source: fixture",
            )

            prefix, loaded, suffix = load_framed_js(path, "en")
            loaded["sectionIds"] = []
            dump_framed_js(path, prefix, loaded, suffix)

            self.assertEqual(
                load_js_data(path, "en"),
                {"data": {}, "sectionIds": []},
            )
            self.assertTrue(path.read_text(encoding="utf-8").endswith(";\n"))

    def test_language_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "en.js"
            write_generated_js(
                path,
                {"data": {}},
                language="en",
                generator="test",
                source="Source: fixture",
            )

            with self.assertRaisesRegex(ValueError, "expected JA"):
                load_js_data(path, "ja")

    def test_monsters_and_boxes_share_the_cell_protocol(self):
        monster_cell = make_drop_cell(
            [
                {"item": "Monster A", "rate": "1/2"},
                {"item": "Monster B", "rate": "1/3"},
            ]
        )
        box_cell = make_drop_cell(
            [
                {"item": "Box A", "rate": "1/4"},
                {"item": "Box B", "rate": "1/5"},
            ]
        )
        data = {
            "data": {
                "Normal": {
                    "monsters": {
                        "Episode 1": [{"name": "Enemy", "drops": [monster_cell]}]
                    },
                    "boxes": {
                        "Episode 1": [{"name": "Area", "drops": [box_cell]}]
                    },
                }
            }
        }

        self.assertEqual(
            [drop["item"] for drop in iter_data_drops(data)],
            ["Monster A", "Monster B", "Box A", "Box B"],
        )
        self.assertEqual(cell_shape_errors(monster_cell), [])
        self.assertEqual(cell_shape_errors(box_cell), [])

    def test_noncanonical_or_nested_cells_are_rejected(self):
        self.assertEqual(
            cell_shape_errors(
                {"items": [{"item": "Only", "rate": "1/2"}]}
            ),
            ["cell.items must contain at least two drops"],
        )
        self.assertEqual(
            cell_shape_errors(
                {
                    "items": [
                        {"item": "A", "rate": "1/2", "items": []},
                        {"item": "B", "rate": "1/3"},
                    ]
                }
            ),
            ["drop[0] cannot contain nested items"],
        )


if __name__ == "__main__":
    unittest.main()
