"""Regressions for NGC source errors corrected against the GC rare table."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from drop_data import SECTION_IDS, iter_cell_drops, load_js_data  # noqa: E402


def rows(language, difficulty, episode):
    data = load_js_data(ROOT / "ngc" / "data" / f"{language}.js", language)
    return data["data"][difficulty]["monsters"][episode]


def items(row):
    return [(list(iter_cell_drops(cell)) or [{}])[0].get("item", "") for cell in row["drops"]]


class NgcSourceAuditTest(unittest.TestCase):
    def test_restored_rows_follow_the_gc_rare_table(self):
        nano = [row for row in rows("en", "Normal", "Episode 1") if row["name"] == "ナノノドラゴ"]
        self.assertEqual(len(nano), 1)
        self.assertEqual(nano[0]["dropRate"], "50%")
        self.assertEqual(items(nano[0]), [
            "Sol Atomizer", "Trimate", "Trimate", "Sol Atomizer", "Sol Atomizer",
            "Trimate", "Sol Atomizer", "Sol Atomizer", "Sol Atomizer", "Trimate",
        ])
        episode2 = rows("ja", "Normal", "Episode 2")
        names = [row["name"] for row in episode2]
        self.assertEqual(names.count("ギルチック"), 1)
        self.assertEqual(names.count("ダブチック"), 1)
        gilchic = episode2[names.index("ギルチック")]
        self.assertEqual(
            [SECTION_IDS[i] for i, item in enumerate(items(gilchic)) if item],
            ["Viridia", "Bluefull"],
        )

    def test_no_monster_row_is_an_exact_duplicate_of_its_neighbour(self):
        for language in ("en", "ja", "zh"):
            for difficulty in ("Normal", "Hard", "Very Hard", "Ultimate"):
                for episode in ("Episode 1", "Episode 2"):
                    episode_rows = rows(language, difficulty, episode)
                    for previous, current in zip(episode_rows, episode_rows[1:]):
                        self.assertNotEqual(previous, current, (language, difficulty, episode))

    def test_restored_episode2_drop_rates(self):
        expected = {"メリクル": "80%", "メリキュス": "80%", "イルギル": "40%", "デルリリー": "35%", "イプシロン": "30%"}
        for difficulty in ("Normal", "Hard", "Very Hard", "Ultimate"):
            restored = {
                row["name"]: row.get("dropRate")
                for row in rows("ja", difficulty, "Episode 2")
                if row["name"] in expected
            }
            self.assertEqual(restored, expected, difficulty)

    def test_corrected_drop_rates_and_items(self):
        ultimate = {row["name"]: row for row in rows("en", "Ultimate", "Episode 1")}
        self.assertEqual(ultimate["Hidelt"]["dropRate"], "85%")
        self.assertEqual(ultimate["Migium"]["dropRate"], "45%")
        slime = [row for row in rows("en", "Very Hard", "Episode 1") if row["name"] == "プイィスライム"][0]
        self.assertEqual(
            [items(slime)[SECTION_IDS.index(s)] for s in ("Greenill", "Pinkal", "Yellowboze", "Whitill")],
            ["CURE PARALYSIS", "CURE SLOW", "CURE SHOCK", "CURE FROZEN"],
        )
        for difficulty in ("Normal", "Hard", "Very Hard", "Ultimate"):
            for episode in ("Episode 1", "Episode 2"):
                pairs = zip(
                    (i for r in rows("en", difficulty, episode) for i in items(r)),
                    (i for r in rows("ja", difficulty, episode) for i in items(r)),
                )
                for english, japanese in pairs:
                    if english == "FLOWEN'S SHIELD":
                        self.assertEqual(japanese, "フロウウェンの盾")


if __name__ == "__main__":
    unittest.main()
