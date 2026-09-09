#!/usr/bin/env python3
"""Validate every generated name, optionally against the current Unitxt source.

This is a generation consistency gate, not independent translation evidence.
Alias identity evidence and reviewed exceptions live in docs/unitxt-alignment-review.md.
"""

import argparse
import copy
import json
import re
from pathlib import Path

import build_i18n
import gen_zh
from drop_data import DROP_TYPES, iter_entry_drops, load_js_data

ROOT = Path(__file__).resolve().parents[1]


def name_fields(data):
    """Index all row and item names by their stable chart position."""
    result = {}
    for difficulty, types in data["data"].items():
        for kind in DROP_TYPES:
            for episode, rows in types.get(kind, {}).items():
                for index, row in enumerate(rows):
                    key = (difficulty, kind, episode, index)
                    result[key + ("name",)] = row["name"]
                    for drop_index, drop in enumerate(iter_entry_drops(row)):
                        result[key + ("item", drop_index)] = drop.get("item", "")
    return result


def compare_names(expected, actual, label):
    """Report mismatches including empty names and missing/extra positions."""
    expected_fields, actual_fields = name_fields(expected), name_fields(actual)
    return [
        f"{label}/{key}: expected {expected_fields.get(key)!r}, got {actual_fields.get(key)!r}"
        for key in expected_fields.keys() | actual_fields.keys()
        if expected_fields.get(key) != actual_fields.get(key)
    ]


def validate_variant_labels(japanese, chinese):
    """Check every dated source item independently of English alias matching."""
    errors = []
    chinese_fields = name_fields(chinese)
    for key, name in name_fields(japanese).items():
        if "item" not in key:
            continue
        year = re.search(r"\[(\d{4})\]$", name)
        if year and year[1] not in chinese_fields.get(key, ""):
            errors.append(f"ngc/zh/{key}: lost Japanese item year {year[1]} from {name!r}")
    return errors


def validate_translation_coverage(data, lookups, language, label):
    """Reject implicit original-text fallback; explicit same-text names are valid."""
    errors = []
    for key, value in name_fields(data).items():
        is_row = key[-1] == "name"
        role = "monsters" if is_row and key[1] == "monsters" else "items"
        lookup = lookups[role]
        parts = [part.strip() for part in value.split("/")] if is_row else [value]
        for name in parts:
            if not name:
                continue
            candidates = (
                lookup.exact.get(name, {}),
                lookup.japanese.get(name, {}),
                lookup.normalized.get(build_i18n.normalize_key(name), {}),
            )
            # Honor the same index precedence as translation: a blank exact
            # entry must not be hidden by a valid lower-priority candidate.
            text = next((entry[language] for entry in candidates if language in entry), None)
            if not isinstance(text, str) or not text.strip():
                errors.append(f"{label}/{key}: missing {language} translation for {name!r}")
    return errors


def validate_names(*, root=ROOT, localization_repo=None):
    authority = json.loads((root / "i18n_names.json").read_text(encoding="utf-8"))
    errors = []
    unitxt = None
    if localization_repo is not None:
        unitxt = build_i18n.load_unitxt_name_maps(localization_repo)
        expected = copy.deepcopy(authority)
        item_norm = {build_i18n.normalize_key(k): k for k in expected["items"]}
        monster_norm = {build_i18n.normalize_key(k): k for k in expected["monsters"]}
        build_i18n.merge_unitxt_item_names(unitxt.items, expected["items"], item_norm)
        monsters = unitxt.standard_monsters | unitxt.ultimate_monsters
        build_i18n.merge_names(
            {k: {"zh": v} for k, v in monsters.items()},
            expected["monsters"], monster_norm, replace=True,
        )
        build_i18n.merge_source_aliases(
            monsters, expected["monsters"], monster_norm, build_i18n.MONSTER_NAME_ALIASES
        )
        for role in ("monsters", "items"):
            for name, translation in expected[role].items():
                if translation.get("zh") != authority[role].get(name, {}).get("zh"):
                    errors.append(f"authority/{role}/{name}: stale or missing Unitxt name")

    lookups = build_i18n.build_translation_lookup(
        authority["monsters"], authority["items"], {}
    )
    for version, languages in (("dc", ("ja", "zh")), ("ngc", ("zh",))):
        english = load_js_data(root / version / "data/en.js", "en")
        if version == "ngc":
            english = build_i18n.resolve_ngc_item_names(
                english, load_js_data(root / "ngc/data/ja.js", "ja"), authority["items"]
            )
        for language in languages:
            errors.extend(validate_translation_coverage(
                english, lookups, language, f"{version}/{language}"
            ))
            expected = build_i18n.translate_data(english, lookups, language)
            actual = load_js_data(root / version / "data" / f"{language}.js", language)
            errors.extend(compare_names(expected, actual, f"{version}/{language}"))
            if version == "ngc":
                errors.extend(validate_variant_labels(
                    load_js_data(root / "ngc/data/ja.js", "ja"), actual
                ))
    if unitxt is not None:
        english = load_js_data(root / "bb/data/en.js", "en")
        expected = gen_zh.translate_data(english, unitxt)
        actual = load_js_data(root / "bb/data/zh.js", "zh")
        errors.extend(compare_names(expected, actual, "bb/zh"))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--localization-repo", type=Path)
    args = parser.parse_args()
    errors = validate_names(localization_repo=args.localization_repo)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("All DC/NGC generated names match the authority.")
    if args.localization_repo is not None:
        print("Authority and all BB Chinese names match the current Unitxt source.")


if __name__ == "__main__":
    main()
