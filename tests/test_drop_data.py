"""Tests for consumers of multi-item drop cells."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

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


def sample_unitxt_groups():
    """Return a minimal aligned Unitxt shape containing every required alias."""
    en_groups = [[] for _ in range(gen_zh.EXPECTED_GROUP_COUNT)]
    zh_groups = [[] for _ in range(gen_zh.EXPECTED_GROUP_COUNT)]

    en_items = [""] * 581
    zh_items = [""] * 581
    for index, en_name, zh_name in (
        (42, "Dragon's Claw", "龙爪"),
        (384, "Nei's Claw", "妮之爪"),
        (482, "Dragon's Claw", "龙之爪"),
        (580, "Nei's Claw", "真·妮之爪"),
    ):
        en_items[index] = en_name
        zh_items[index] = zh_name
    en_groups[gen_zh.ITEM_GROUP] = en_items
    zh_groups[gen_zh.ITEM_GROUP] = zh_items

    monster_names = sorted(set(gen_zh.MONSTER_ALIASES.values()))
    en_groups[gen_zh.STANDARD_MONSTER_GROUP] = monster_names
    zh_groups[gen_zh.STANDARD_MONSTER_GROUP] = [
        f"普通·{name}" for name in monster_names
    ]

    area_names = sorted(set(gen_zh.AREA_ALIASES.values()))
    en_groups[gen_zh.AREA_GROUP] = area_names
    zh_groups[gen_zh.AREA_GROUP] = [f"区域·{name}" for name in area_names]

    current_entries = sum(map(len, en_groups))
    padding = gen_zh.EXPECTED_ENTRY_COUNT - current_entries
    en_groups[0] = [""] * padding
    zh_groups[0] = [""] * padding
    return en_groups, zh_groups


def sample_name_data(name):
    """Return a minimal dataset containing one monster row and no drops."""
    return {
        "data": {
            "Ultimate": {
                "monsters": {"Episode 2": [{"name": name, "drops": []}]},
                "boxes": {},
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
        name_maps = gen_zh.UnitxtNameMaps(
            items={"Vjaya": "维加亚", "AddSlot": "追加插槽"},
            standard_monsters={},
            ultimate_monsters={},
            areas={"Forest 1": "森林区域１"},
        )
        translated = gen_zh.translate_data(
            sample_data(),
            name_maps,
        )
        entry = translated["data"]["Ultimate"]["boxes"]["Episode 1"][0]
        self.assertEqual(
            [drop["item"] for drop in iter_entry_drops(entry)],
            ["维加亚", "追加插槽"],
        )

    def test_gen_zh_preserves_monster_pair_context(self):
        name_maps = gen_zh.UnitxtNameMaps(
            items={},
            standard_monsters={"Gi Gue": "蜂后"},
            ultimate_monsters={"Gi Gue": "姬蜂后"},
            areas={},
        )

        self.assertEqual(
            gen_zh.translate_monster_name("Gi Gue/Gi Gue", name_maps),
            "蜂后/姬蜂后",
        )

    def test_gen_zh_rejects_missing_item_mapping(self):
        name_maps = gen_zh.UnitxtNameMaps(
            items={"Vjaya": "维加亚"},
            standard_monsters={},
            ultimate_monsters={},
            areas={"Forest 1": "森林区域１"},
        )

        with self.assertRaisesRegex(ValueError, "AddSlot"):
            gen_zh.translate_data(sample_data(), name_maps)

    def test_gen_zh_treats_slashes_in_item_names_as_literal_text(self):
        data = sample_data()
        data["data"]["Ultimate"]["boxes"]["Episode 1"][0]["drops"] = [
            {"item": "God/Power", "rate": "1/2"}
        ]
        name_maps = gen_zh.UnitxtNameMaps(
            items={"God/Power": "天神／力量"},
            standard_monsters={},
            ultimate_monsters={},
            areas={"Forest 1": "森林区域１"},
        )

        translated = gen_zh.translate_data(data, name_maps)

        drop = translated["data"]["Ultimate"]["boxes"]["Episode 1"][0]["drops"][0]
        self.assertEqual(drop["item"], "天神／力量")

    def test_gen_zh_builds_aliases_and_resolves_ambiguous_weapons(self):
        en_groups, zh_groups = sample_unitxt_groups()

        name_maps = gen_zh.build_name_maps(en_groups, zh_groups)

        self.assertEqual(name_maps.items["Dragon's Claw"], "龙之爪")
        self.assertEqual(name_maps.items["Nei's Claw"], "真·妮之爪")
        self.assertEqual(
            name_maps.standard_monsters["Gilchic"],
            name_maps.standard_monsters["Gillchic"],
        )
        self.assertEqual(name_maps.areas["CCA"], name_maps.areas["Central Control Area"])
        self.assertEqual(name_maps.areas["Boss"], "首领")

    def test_gen_zh_rejects_unaligned_unitxt_shape(self):
        with self.assertRaisesRegex(ValueError, "group shapes differ"):
            gen_zh.validate_unitxt_shape([["English"]], [[]])

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

    def test_authority_merge_preserves_uncovered_names_and_replaces_values(self):
        target = {"Existing": {"zh": "旧译名"}}
        identities = {build_i18n.normalize_key("Existing"): "Existing"}

        build_i18n.merge_names(
            {
                "existing": {"zh": "权威译名", "ja": "既存"},
                "Site Only": {"zh": "本站独有"},
            },
            target,
            identities,
            replace=True,
        )

        self.assertEqual(target["Existing"], {"zh": "权威译名", "ja": "既存"})
        self.assertEqual(target["Site Only"], {"zh": "本站独有"})

    def test_build_i18n_prefers_ultimate_name_for_flat_cross_version_map(self):
        bb_en = sample_name_data("Gi Gue/Gi Gue")
        bb_ja = sample_name_data("ギ・グー/ギ・グー")
        bb_zh = sample_name_data("蜂后/姬蜂后")
        ngc_empty = {"data": {}}

        with (
            patch.object(
                build_i18n,
                "load_js_data",
                side_effect=[bb_en, bb_ja, bb_zh, ngc_empty, ngc_empty],
            ),
            patch.object(
                build_i18n,
                "load_authoritative_names",
                return_value={"monsters": {}, "items": {}},
            ),
            patch.object(
                build_i18n,
                "load_unitxt_name_maps",
                return_value=gen_zh.UnitxtNameMaps({}, {}, {}, {}),
            ),
        ):
            monsters, _, _ = build_i18n.build_mapping()

        self.assertEqual(monsters["Gi Gue"]["zh"], "姬蜂后")

    def test_ss_iterator_visits_nested_items(self):
        self.assertEqual(
            [drop["item"] for drop in mark_ss.iter_drops(sample_data())],
            ["Vjaya", "AddSlot"],
        )


if __name__ == "__main__":
    unittest.main()
