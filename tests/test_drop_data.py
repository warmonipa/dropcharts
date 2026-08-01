"""Tests for consumers of multi-item drop cells."""

import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

import build_i18n  # noqa: E402
import gen_zh  # noqa: E402
import mark_ss  # noqa: E402
from drop_data import iter_entry_drops  # noqa: E402


def sample_data():
    """Return a minimal chart containing one multi-item cell."""
    return {
        "data": {
            "Ultimate": {
                "boxes": {
                    "Episode 1": [
                        {
                            "name": "Forest 1",
                            "drops": [
                                {
                                    "items": [
                                        {"item": "Vjaya", "rate": "1/630.1"},
                                        {"item": "AddSlot", "rate": "1/1170.3"},
                                    ]
                                }
                            ],
                        }
                    ]
                },
                "monsters": {},
            }
        }
    }


class MultiItemConsumerTest(unittest.TestCase):
    """Verify shared traversal, translation, and SS marking compatibility."""

    def test_entry_iterator_flattens_cells_in_order(self):
        entry = sample_data()["data"]["Ultimate"]["boxes"]["Episode 1"][0]
        self.assertEqual(
            [drop["item"] for drop in iter_entry_drops(entry)],
            ["Vjaya", "AddSlot"],
        )

    def test_gen_zh_translates_every_item_in_cell(self):
        translated = gen_zh.translate_data(
            sample_data(),
            {"Vjaya": "维加亚", "AddSlot": "追加插槽"},
        )
        entry = translated["data"]["Ultimate"]["boxes"]["Episode 1"][0]
        self.assertEqual(
            [drop["item"] for drop in iter_entry_drops(entry)],
            ["维加亚", "追加插槽"],
        )

    def test_build_i18n_translates_every_item_in_cell(self):
        lookup = {
            "Vjaya": {"zh": "维加亚"},
            "AddSlot": {"zh": "追加插槽"},
        }
        norm_lookup = {
            build_i18n.normalize_key(name): translations
            for name, translations in lookup.items()
        }
        translated = build_i18n.translate_data(
            sample_data(),
            lookup,
            norm_lookup,
            {},
            "zh",
        )
        entry = translated["data"]["Ultimate"]["boxes"]["Episode 1"][0]
        self.assertEqual(
            [drop["item"] for drop in iter_entry_drops(entry)],
            ["维加亚", "追加插槽"],
        )

    def test_ss_iterator_visits_nested_items(self):
        self.assertEqual(
            [drop["item"] for drop in mark_ss.iter_drops(sample_data())],
            ["Vjaya", "AddSlot"],
        )


if __name__ == "__main__":
    unittest.main()
