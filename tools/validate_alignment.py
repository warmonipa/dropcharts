#!/usr/bin/env python3
"""Validate drop-table coordinates across every version and language."""

import argparse
import json
from pathlib import Path

from drop_data import (
    DROP_TYPES,
    LANGUAGES,
    VERSIONS,
    cell_shape_errors,
    iter_cell_drops,
    load_js_data,
)


ROOT = Path(__file__).parent.parent


def _drop_signature(cell):
    """Return language-independent coordinate fields for one cell."""
    drops = list(iter_cell_drops(cell))
    return {
        "count": len(drops),
        "present": [bool(drop.get("item")) for drop in drops],
        "rates": [drop.get("rate", "") for drop in drops],
        "ss": [bool(drop.get("ss")) for drop in drops],
    }


def validate_version(version, *, root=ROOT):
    """Return alignment errors and summary counts for one game version."""
    datasets = {
        language: load_js_data(
            root / version / "data" / f"{language}.js",
            language,
        )
        for language in LANGUAGES
    }
    english = datasets["en"]
    errors = []
    summary = {
        "entries": 0,
        "items": 0,
        "multi_cells": 0,
    }

    section_ids = english.get("sectionIds", [])
    if len(section_ids) != 10:
        errors.append(f"{version}/en: expected 10 section IDs, got {len(section_ids)}")
    if len(english.get("sectionColors", [])) != len(section_ids):
        errors.append(f"{version}/en: section color count mismatch")

    for language in LANGUAGES[1:]:
        localized = datasets[language]
        if localized.get("sectionIds") != section_ids:
            errors.append(f"{version}/{language}: section IDs differ from en")
        if set(localized.get("data", {})) != set(english.get("data", {})):
            errors.append(f"{version}/{language}: difficulty keys differ from en")

    for difficulty, english_types in english["data"].items():
        for type_name in DROP_TYPES:
            english_episodes = english_types.get(type_name, {})
            for language in LANGUAGES[1:]:
                localized_episodes = datasets[language]["data"][difficulty].get(
                    type_name,
                    {},
                )
                if set(localized_episodes) != set(english_episodes):
                    errors.append(
                        f"{version}/{language}/{difficulty}/{type_name}: "
                        "episode keys differ from en"
                    )

            for episode, english_entries in english_episodes.items():
                localized_entries = {
                    language: datasets[language]["data"][difficulty][type_name][episode]
                    for language in LANGUAGES
                }
                counts = {
                    language: len(entries)
                    for language, entries in localized_entries.items()
                }
                if len(set(counts.values())) != 1:
                    errors.append(
                        f"{version}/{difficulty}/{type_name}/{episode}: "
                        f"entry counts differ {counts}"
                    )
                    continue

                for entry_index, english_entry in enumerate(english_entries):
                    summary["entries"] += 1
                    entries = {
                        language: localized_entries[language][entry_index]
                        for language in LANGUAGES
                    }
                    drop_rates = {
                        language: entry.get("dropRate", "")
                        for language, entry in entries.items()
                    }
                    if len(set(drop_rates.values())) != 1:
                        errors.append(
                            f"{version}/{difficulty}/{type_name}/{episode}/"
                            f"{entry_index}: entry drop rates differ {drop_rates}"
                        )

                    column_counts = {
                        language: len(entry.get("drops", []))
                        for language, entry in entries.items()
                    }
                    if set(column_counts.values()) != {len(section_ids)}:
                        errors.append(
                            f"{version}/{difficulty}/{type_name}/{episode}/"
                            f"{entry_index}: expected {len(section_ids)} columns, "
                            f"got {column_counts}"
                        )
                        continue

                    for column_index in range(len(section_ids)):
                        cells = {
                            language: entries[language]["drops"][column_index]
                            for language in LANGUAGES
                        }
                        invalid_cells = False
                        for language, cell in cells.items():
                            for shape_error in cell_shape_errors(cell):
                                invalid_cells = True
                                errors.append(
                                    f"{version}/{language}/{difficulty}/"
                                    f"{type_name}/{episode}/{entry_index}/"
                                    f"{column_index}: {shape_error}"
                                )
                        if invalid_cells:
                            continue

                        signatures = {
                            language: _drop_signature(cell)
                            for language, cell in cells.items()
                        }
                        if len(
                            {
                                json.dumps(signature, sort_keys=True)
                                for signature in signatures.values()
                            }
                        ) != 1:
                            errors.append(
                                f"{version}/{difficulty}/{type_name}/{episode}/"
                                f"{entry_index}/{column_index}: "
                                f"cell coordinates differ {signatures}"
                            )
                        english_drops = list(
                            iter_cell_drops(
                                cells["en"],
                            )
                        )
                        summary["items"] += sum(
                            bool(drop.get("item")) for drop in english_drops
                        )
                        if len(english_drops) > 1:
                            summary["multi_cells"] += 1

    return errors, summary


def validate_all(*, root=ROOT, versions=VERSIONS):
    """Return combined errors and per-version summaries."""
    errors = []
    summaries = {}
    for version in versions:
        version_errors, summary = validate_version(version, root=root)
        errors.extend(version_errors)
        summaries[version] = summary
    return errors, summaries


def main():
    """Run the alignment validator."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "versions",
        choices=VERSIONS,
        nargs="*",
        default=VERSIONS,
    )
    args = parser.parse_args()
    errors, summaries = validate_all(versions=args.versions)
    for version, summary in summaries.items():
        print(
            f"{version}: {summary['entries']} entries, "
            f"{summary['items']} items, "
            f"{summary['multi_cells']} multi-item cells"
        )
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("All versions and languages are coordinate-aligned.")


if __name__ == "__main__":
    main()
