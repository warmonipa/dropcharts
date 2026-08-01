"""Tests for lossless cross-language coordinate synchronization."""

import copy
import sys
import unittest
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS))

from sync_coordinates import sync_dataset  # noqa: E402


def dataset(item, *, entry_rate=None, rate="1/10"):
    """Build a minimal generated dataset."""
    entry = {
        "name": "Example",
        "drops": [{"item": item, "rate": rate}],
    }
    if entry_rate is not None:
        entry["dropRate"] = entry_rate
    return {
        "data": {
            "Normal": {
                "monsters": {"Episode 1": [entry]},
                "boxes": {},
            }
        }
    }


class SyncDatasetTest(unittest.TestCase):
    """Verify metadata repair never discards an English item."""

    def test_fills_missing_item_and_rates(self):
        english = dataset("Item", entry_rate="1/2", rate="1/10")
        localized = dataset("", rate="")

        changes = sync_dataset(english, localized)

        entry = localized["data"]["Normal"]["monsters"]["Episode 1"][0]
        self.assertEqual(entry["dropRate"], "1/2")
        self.assertEqual(entry["drops"][0], {"item": "Item", "rate": "1/10"})
        self.assertEqual(changes["missing_items"], 1)
        self.assertEqual(changes["entry_rates"], 1)
        self.assertEqual(changes["drop_rates"], 1)

    def test_preserves_existing_translation(self):
        english = dataset("Item")
        localized = dataset("物品")
        before = copy.deepcopy(localized)

        changes = sync_dataset(english, localized)

        self.assertEqual(localized, before)
        self.assertEqual(sum(changes.values()), 0)


if __name__ == "__main__":
    unittest.main()
