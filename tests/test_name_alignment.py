"""Regressions for legacy identity resolution and generated-name validation."""

import copy
import json
import re
from collections import Counter
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import build_i18n
import gen_zh
import validate_names
from drop_data import iter_cell_drops, load_js_data


class NameAlignmentTests(unittest.TestCase):
    def test_role_collision_cannot_cross_normalized_or_japanese_indexes(self):
        lookups = build_i18n.build_translation_lookup(
            {"Claw": {"ja": "クロー", "zh": "爪虫"}},
            {"Claw": {"ja": "クロー", "zh": "光子爪"}}, {},
        )
        for spelling in ("Claw", "CLAW", "クロー"):
            with self.subTest(spelling=spelling):
                self.assertEqual(build_i18n.translate_name(spelling, lookups["monsters"], "zh"), "爪虫")
                self.assertEqual(build_i18n.translate_name(spelling, lookups["items"], "zh"), "光子爪")
        self.assertEqual(build_i18n.translate_name("Claw", lookups["monsters"], "ja"), "クロー")

    def test_case_sensitive_items_do_not_acquire_an_arbitrary_normalized_identity(self):
        lookup = build_i18n.build_translation_lookup(
            {}, {"Blade": {"zh": "突刺匕首"}, "BLADE": {"zh": "匕首"}}, {}
        )["items"]
        self.assertEqual(build_i18n.translate_name("Blade", lookup, "zh"), "突刺匕首")
        self.assertEqual(build_i18n.translate_name("BLADE", lookup, "zh"), "匕首")
        self.assertEqual(build_i18n.translate_name("blade", lookup, "zh"), "blade")

    def test_japanese_boss_alias_is_registered_without_item_metadata(self):
        empty = {"data": {}}
        ngc = {"data": {"Normal": {"monsters": {
            "Episode 2": [{"name": "オルガ・フロウ?", "drops": []}]
        }}}}
        with (
            patch.object(build_i18n, "load_js_data", side_effect=[empty, empty, empty, ngc, ngc]),
            patch.object(build_i18n, "load_authoritative_names", return_value={"monsters": {}, "items": {}}),
            patch.object(build_i18n, "load_unitxt_name_maps", return_value=gen_zh.UnitxtNameMaps(
                {}, {"Olga Flow": "奥尔加·弗洛"}, {}, {}
            )),
        ):
            monsters, items, japanese = build_i18n.build_mapping()
        result = build_i18n.translate_data(
            ngc, build_i18n.build_translation_lookup(monsters, items, japanese), "zh"
        )
        self.assertEqual(result["data"]["Normal"]["monsters"]["Episode 2"][0]["name"], "奥尔加·弗洛?")

    def test_missing_canonical_alias_source_is_an_error(self):
        with self.assertRaisesRegex(ValueError, "Kaladbolg"):
            build_i18n.merge_unitxt_item_names(
                {}, {"KALADGOLG": {"zh": "冰之剑"}}, {"kaladgolg": "KALADGOLG"}
            )

    def test_ngc_db_sword_years_and_manufacturers_remain_distinct(self):
        english = load_js_data(ROOT / "ngc/data/en.js", "en")
        japanese = load_js_data(ROOT / "ngc/data/ja.js", "ja")
        chinese = load_js_data(ROOT / "ngc/data/zh.js", "zh")
        expected_3069 = {"Bluefull": "Chris", "Pinkal": "Torato"}
        found = {}
        for difficulty, types in english["data"].items():
            for kind, episodes in types.items():
                for episode, rows in episodes.items():
                    for index, row in enumerate(rows):
                        ja_row = japanese["data"][difficulty][kind][episode][index]
                        zh_row = chinese["data"][difficulty][kind][episode][index]
                        for column, cell in enumerate(row["drops"]):
                            for drop_index, drop in enumerate(iter_cell_drops(cell)):
                                if drop["item"] != "DB'S SWORD":
                                    continue
                                ja = list(iter_cell_drops(ja_row["drops"][column]))[drop_index]["item"]
                                zh = list(iter_cell_drops(zh_row["drops"][column]))[drop_index]["item"]
                                year = ja.split("[")[1].split("]")[0]
                                sid = english["sectionIds"][column]
                                self.assertIn(year, zh)
                                self.assertTrue(zh.startswith("DB 之剑「"), zh)
                                if year == "3069":
                                    self.assertIn(expected_3069[sid], zh)
                                found[sid] = zh
        self.assertEqual(len(found), 9)
        self.assertEqual(len(set(found.values())), 9)

    def test_all_ngc_dated_weapons_preserve_the_paired_japanese_year(self):
        english = load_js_data(ROOT / "ngc/data/en.js", "en")
        japanese = load_js_data(ROOT / "ngc/data/ja.js", "ja")
        chinese = load_js_data(ROOT / "ngc/data/zh.js", "zh")
        found = []
        for difficulty, types in english["data"].items():
            for kind, episodes in types.items():
                for episode, rows in episodes.items():
                    for index, row in enumerate(rows):
                        ja_row = japanese["data"][difficulty][kind][episode][index]
                        zh_row = chinese["data"][difficulty][kind][episode][index]
                        for column, cell in enumerate(row["drops"]):
                            for drop_index, drop in enumerate(iter_cell_drops(cell)):
                                ja = list(iter_cell_drops(ja_row["drops"][column]))[drop_index]["item"]
                                match = re.search(r"\[(\d{4})\]$", ja)
                                if match is None:
                                    continue
                                zh = list(iter_cell_drops(zh_row["drops"][column]))[drop_index]["item"]
                                with self.subTest(name=drop["item"], japanese=ja):
                                    self.assertIn(match[1], zh)
                                found.append(drop["item"])
        self.assertEqual(Counter(found), {"DB'S SWORD": 9, "FLOWEN'S SWORD": 9})

    def test_weapon_identity_uses_japanese_year_before_section_id(self):
        resolve = build_i18n.resolve_ngc_item_name
        self.assertEqual(resolve("FLOWEN'S SWORD", "フロウウェンの剣", "Skyly"), "Flowen's Sword")
        self.assertEqual(resolve("FLOWEN'S SWORD", "フロウウェンの剣[3084]", "Skyly"), "Flowen's Sword (3084)")
        self.assertEqual(resolve("DB'S SWORD", "DBの剣[3064]", "Bluefull"), "DB's Saber (3064)")
        self.assertEqual(resolve("DB'S SWORD", "DBの剣[3069]", "Bluefull"), "DB's Saber (3069 Chris)")
        self.assertEqual(resolve("DB'S SWORD", "DBの剣[3069]", "Pinkal"), "DB's Saber (3069 Torato)")

    def test_unidentified_weapon_variants_are_rejected(self):
        for name, japanese, section in (
            ("DB'S SWORD", "DBの剣", "Bluefull"),
            ("DB'S SWORD", "DBの剣[3069]", "Viridia"),
            ("FLOWEN'S SWORD", "DBの剣[3064]", "Skyly"),
            ("FLOWEN'S SWORD", "", "Skyly"),
        ):
            with self.subTest(name=name, japanese=japanese):
                with self.assertRaises(ValueError):
                    build_i18n.resolve_ngc_item_name(name, japanese, section)

    def test_paired_resolution_preserves_multi_cells_and_rejects_missing_identity(self):
        english = {"sectionIds": ["Skyly"], "data": {"Ultimate": {"monsters": {
            "Episode 1": [{"name": "Hidelt", "drops": [{"items": [
                {"item": "FLOWEN'S SWORD", "rate": "1/2", "ss": True},
                {"item": "DB'S SWORD", "rate": "1/3"},
            ]}]}]
        }}}}
        original = copy.deepcopy(english)
        japanese = copy.deepcopy(english)
        drops = japanese["data"]["Ultimate"]["monsters"]["Episode 1"][0]["drops"][0]["items"]
        drops[0]["item"], drops[1]["item"] = "フロウウェンの剣[3084]", "DBの剣[3064]"
        known = {"Flowen's Sword (3084)", "DB's Saber (3064)"}
        result = build_i18n.resolve_ngc_item_names(english, japanese, known)
        resolved = result["data"]["Ultimate"]["monsters"]["Episode 1"][0]["drops"][0]["items"]
        self.assertEqual(resolved, [
            {"item": "Flowen's Sword (3084)", "rate": "1/2", "ss": True},
            {"item": "DB's Saber (3064)", "rate": "1/3"},
        ])
        self.assertEqual(english, original)
        with self.assertRaisesRegex(ValueError, "variant missing"):
            build_i18n.resolve_ngc_item_names(english, japanese, set())
        with self.assertRaisesRegex(ValueError, "Missing paired"):
            build_i18n.resolve_ngc_item_names(english, {}, known)
        drops.pop()
        with self.assertRaisesRegex(ValueError, "cardinality"):
            build_i18n.resolve_ngc_item_names(english, japanese, known)

    def test_all_ngc_multi_label_identities_have_been_reviewed(self):
        en = load_js_data(ROOT / "ngc/data/en.js", "en")
        ja = load_js_data(ROOT / "ngc/data/ja.js", "ja")
        en_fields, ja_fields = validate_names.name_fields(en), validate_names.name_fields(ja)
        pairs = {}
        for key, name in en_fields.items():
            if "item" in key and name:
                pairs.setdefault(name, set()).add(ja_fields[key])
        multiple = {name for name, labels in pairs.items() if len(labels) > 1}
        # Families, punctuation/transliteration variants, and the documented
        # shield/armor source error. New cases require an identity review.
        self.assertEqual(multiple, {
            "DB'S SWORD", "FLOWEN'S SWORD", "VISK'235W", "P-arm's Arms", "FLOWEN'S SHIELD",
        })

    def test_name_gate_rejects_missing_authority_even_when_output_matches_fallback(self):
        original_read = Path.read_text
        original_load = validate_names.load_js_data
        chinese = copy.deepcopy(load_js_data(ROOT / "ngc/data/zh.js", "zh"))
        english = load_js_data(ROOT / "ngc/data/en.js", "en")
        replaced = 0
        for difficulty, types in english["data"].items():
            for kind, episodes in types.items():
                for episode, rows in episodes.items():
                    for index, row in enumerate(rows):
                        zh_row = chinese["data"][difficulty][kind][episode][index]
                        for column, cell in enumerate(row["drops"]):
                            for item_index, drop in enumerate(iter_cell_drops(cell)):
                                if drop["item"] == "CURE SHOCK":
                                    list(iter_cell_drops(zh_row["drops"][column]))[item_index]["item"] = "CURE SHOCK"
                                    replaced += 1
        self.assertEqual(replaced, 5)

        def read_without_alias(path, *args, **kwargs):
            text = original_read(path, *args, **kwargs)
            if path.name == "i18n_names.json":
                authority = json.loads(text)
                authority["items"].pop("CURE SHOCK")
                return json.dumps(authority)
            return text

        def load_mutated(path, language=None):
            if path == ROOT / "ngc/data/zh.js":
                return chinese
            return original_load(path, language)

        with patch.object(Path, "read_text", read_without_alias), patch.object(
            validate_names, "load_js_data", load_mutated
        ):
            errors = validate_names.validate_names(root=ROOT)
        self.assertEqual(sum("missing zh translation" in e and "CURE SHOCK" in e for e in errors), 5)

    def test_coverage_accepts_explicit_same_text_and_role_specific_indexes(self):
        data = {"data": {"Normal": {"monsters": {"Episode 1": [{
            "name": "CLAW/クロー", "drops": [{"items": [
                {"item": "SH2", "rate": "1/2"},
                {"item": "カラドボルグ", "rate": "1/3"},
            ]}],
        }]}}}}
        lookups = build_i18n.build_translation_lookup(
            {"Claw": {"zh": "爪虫", "ja": "クロー"}},
            {"SH2": {"zh": "SH2"}, "Kaladbolg": {"ja": "カラドボルグ", "zh": "卡拉德波加"}}, {},
        )
        self.assertEqual(validate_names.validate_translation_coverage(data, lookups, "zh", "test"), [])

    def test_coverage_rejects_missing_row_and_nested_item_target_language(self):
        data = {"data": {"Normal": {"monsters": {"Episode 1": [{
            "name": "Claw", "drops": [{"items": [
                {"item": "SH2", "rate": "1/2"},
                {"item": "Kaladbolg", "rate": "1/3"},
            ]}],
        }]}}}}
        lookups = build_i18n.build_translation_lookup(
            {"Claw": {"ja": "クロー"}},
            {"SH2": {"zh": "SH2"}, "Kaladbolg": {"ja": "カラドボルグ"}}, {},
        )
        errors = validate_names.validate_translation_coverage(data, lookups, "zh", "test")
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("Claw" in error for error in errors))
        self.assertTrue(any("Kaladbolg" in error for error in errors))

    def test_coverage_rejects_blank_exact_name_shadowing_a_valid_japanese_index(self):
        data = {"data": {"Normal": {"monsters": {"Episode 1": [{
            "name": "クロー", "drops": [],
        }]}}}}
        lookups = build_i18n.build_translation_lookup(
            {"Claw": {"zh": "爪虫", "ja": "クロー"}, "クロー": {"zh": ""}}, {}, {},
        )
        errors = validate_names.validate_translation_coverage(data, lookups, "zh", "test")
        self.assertEqual(len(errors), 1)

    def test_all_checked_in_names_match_authority(self):
        self.assertEqual(validate_names.validate_names(root=ROOT), [])

    def test_name_gate_rejects_stale_rows_and_nested_items(self):
        data = {"data": {"Hard": {"monsters": {"Episode 1": [{
            "name": "爪虫", "drops": [{"items": [
                {"item": "解除/感电", "rate": "1/2"},
                {"item": "卡拉德波加", "rate": "1/3"},
            ]}],
        }]}}}}
        broken = copy.deepcopy(data)
        row = broken["data"]["Hard"]["monsters"]["Episode 1"][0]
        row["name"] = "光子爪"
        row["drops"][0]["items"][1]["item"] = "冰之剑"
        errors = validate_names.compare_names(data, broken, "regression")
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("冰之剑" in error for error in errors))

    def test_variant_gate_detects_year_loss_without_reusing_the_translator(self):
        japanese = {"data": {"Ultimate": {"monsters": {"Episode 1": [{
            "name": "ヒルデルト", "drops": [{"item": "フロウウェンの剣[3084]", "rate": "1/2"}],
        }]}}}}
        chinese = copy.deepcopy(japanese)
        drop = chinese["data"]["Ultimate"]["monsters"]["Episode 1"][0]["drops"][0]
        drop["item"] = "弗洛文大剑"
        errors = validate_names.validate_variant_labels(japanese, chinese)
        self.assertEqual(len(errors), 1)
        self.assertIn("3084", errors[0])
        drop["item"] = "弗洛文大剑「3084」"
        self.assertEqual(validate_names.validate_variant_labels(japanese, chinese), [])

    def test_unitxt_gate_rejects_stale_authority_even_when_charts_agree(self):
        source = gen_zh.UnitxtNameMaps(
            {name: "修订译名" for name in build_i18n.ITEM_ALIASES.values()},
            {name: "修订译名" for name in build_i18n.MONSTER_NAME_ALIASES.values()},
            {}, {},
        )
        with (
            patch.object(build_i18n, "load_unitxt_name_maps", return_value=source),
            patch.object(gen_zh, "translate_data", return_value=load_js_data(ROOT / "bb/data/zh.js", "zh")),
        ):
            errors = validate_names.validate_names(root=ROOT, localization_repo=ROOT)
        self.assertTrue(any("authority/items/KALADGOLG" in error for error in errors))


    def test_inactive_dictionary_aliases_follow_canonical_names(self):
        authority = json.loads((ROOT / "i18n_names.json").read_text())["items"]
        pairs = {
            "DB'S SABER 3062": "DB's Saber (3062)",
            "Book of KATANA1": "Book of Katana 1",
            "AGITO 1983": "Agito (1983)",
            "MARK3": "Mark III",
            "Kit of MARK3": "Kit of Mark III",
            "キュア/ポイズン": "Cure/Poison",
            "マグ細胞２１３": "Cell of Mag 213",
            "Silver Badge": "Weapons Silver Badge",
        }
        for alias, canonical in pairs.items():
            with self.subTest(alias=alias):
                matches = [value for name, value in authority.items() if name.casefold() == canonical.casefold()]
                self.assertEqual(len(matches), 1)
                self.assertEqual(authority[alias]["zh"], matches[0]["zh"])

    def test_authority_gate_checks_aliases_without_any_drop_consumer(self):
        items = {"DB'S SABER 3062": {"zh": "DB剑 3062"},
                 "DB's Saber (3062)": {"zh": "DB 之剑「3062」"}}
        self.assertEqual(len(validate_names.validate_authority_aliases(items)), 1)
        items["DB'S SABER 3062"]["zh"] = "DB 之剑「3062」"
        self.assertEqual(validate_names.validate_authority_aliases(items), [])
        del items["DB's Saber (3062)"]
        self.assertEqual(len(validate_names.validate_authority_aliases(items)), 1)

    def test_context_projection_does_not_replace_a_same_named_item(self):
        source = gen_zh.UnitxtNameMaps(
            {"CLAW": "光子爪"}, {"Claw": "爪虫", "Olga Flow": "奥尔加·弗洛"},
            {}, {"Forest 1": "森林区１"},
        )
        items = {"Claw": {"zh": "光子爪"}, "Olga Flow": {"zh": "旧名", "ja": "オルガ・フロウ"},
                 "Forest 1": {"zh": "Forest 1"}, "SH2": {"zh": "SH2"}}
        build_i18n.merge_unitxt_context_names(source, items)
        self.assertEqual(items["Claw"]["zh"], "光子爪")
        self.assertEqual(items["Olga Flow"], {"zh": "奥尔加·弗洛", "ja": "オルガ・フロウ"})
        self.assertEqual(items["Forest 1"]["zh"], "森林区１")
        self.assertEqual(items["SH2"]["zh"], "SH2")


if __name__ == "__main__":
    unittest.main()
