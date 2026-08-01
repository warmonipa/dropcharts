#!/usr/bin/env python3
"""Synchronize language-independent drop coordinates from English data."""

import argparse
from pathlib import Path

from drop_data import (
    DROP_TYPES,
    LANGUAGES,
    VERSIONS,
    dump_framed_js,
    iter_cell_drops,
    load_framed_js,
    load_js_data,
)


ROOT = Path(__file__).parent.parent
LOCALIZED_LANGUAGES = LANGUAGES[1:]


def sync_dataset(english, localized):
    """Synchronize metadata and losslessly fill missing localized items."""
    changes = {
        "entry_rates": 0,
        "drop_rates": 0,
        "missing_items": 0,
        "ss_flags": 0,
    }
    for difficulty, english_types in english["data"].items():
        for type_name in DROP_TYPES:
            english_episodes = english_types.get(type_name, {})
            localized_episodes = localized["data"][difficulty].get(type_name, {})
            if set(localized_episodes) != set(english_episodes):
                raise ValueError(
                    f"{difficulty}/{type_name}: localized episode structure differs"
                )
            for episode, english_entries in english_episodes.items():
                localized_entries = localized_episodes[episode]
                if len(localized_entries) != len(english_entries):
                    raise ValueError(
                        f"{difficulty}/{type_name}/{episode}: entry count differs"
                    )
                for english_entry, localized_entry in zip(
                    english_entries,
                    localized_entries,
                ):
                    english_entry_rate = english_entry.get("dropRate")
                    if localized_entry.get("dropRate") != english_entry_rate:
                        changes["entry_rates"] += 1
                        if english_entry_rate is None:
                            localized_entry.pop("dropRate", None)
                        else:
                            localized_entry["dropRate"] = english_entry_rate

                    english_cells = english_entry.get("drops", [])
                    localized_cells = localized_entry.get("drops", [])
                    if len(localized_cells) != len(english_cells):
                        raise ValueError(
                            f"{difficulty}/{type_name}/{episode}/"
                            f"{english_entry['name']}: column count differs"
                        )
                    for english_cell, localized_cell in zip(
                        english_cells,
                        localized_cells,
                    ):
                        english_drops = list(iter_cell_drops(english_cell))
                        localized_drops = list(iter_cell_drops(localized_cell))
                        if len(localized_drops) != len(english_drops):
                            raise ValueError(
                                f"{difficulty}/{type_name}/{episode}/"
                                f"{english_entry['name']}: cell item count differs"
                            )
                        for english_drop, localized_drop in zip(
                            english_drops,
                            localized_drops,
                        ):
                            english_item = english_drop.get("item", "")
                            localized_item = localized_drop.get("item", "")
                            if english_item and not localized_item:
                                localized_drop["item"] = english_item
                                changes["missing_items"] += 1
                            elif localized_item and not english_item:
                                raise ValueError(
                                    f"{difficulty}/{type_name}/{episode}/"
                                    f"{english_entry['name']}: localized-only item"
                                )

                            english_rate = english_drop.get("rate", "")
                            if localized_drop.get("rate", "") != english_rate:
                                localized_drop["rate"] = english_rate
                                changes["drop_rates"] += 1

                            english_ss = english_drop.get("ss")
                            if localized_drop.get("ss") != english_ss:
                                changes["ss_flags"] += 1
                                if english_ss is None:
                                    localized_drop.pop("ss", None)
                                else:
                                    localized_drop["ss"] = english_ss
    return changes


def sync_version(version, *, root=ROOT):
    """Synchronize JA/ZH files for one version and return change counts."""
    english = load_js_data(root / version / "data" / "en.js", "en")
    results = {}
    for language in LOCALIZED_LANGUAGES:
        path = root / version / "data" / f"{language}.js"
        prefix, localized, suffix = load_framed_js(path, language)
        changes = sync_dataset(english, localized)
        dump_framed_js(path, prefix, localized, suffix)
        results[language] = changes
    return results


def main():
    """Synchronize every generated version."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "versions",
        choices=VERSIONS,
        nargs="*",
        default=VERSIONS,
    )
    args = parser.parse_args()
    for version in args.versions:
        results = sync_version(version)
        for language, changes in results.items():
            print(f"{version}/{language}: {changes}")


if __name__ == "__main__":
    main()
