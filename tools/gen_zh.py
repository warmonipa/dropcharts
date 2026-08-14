#!/usr/bin/env python3
"""Generate BB Chinese drop-chart data from psobb-localization Unitxt files.

English drop data is the coordinate base. Display names come from the aligned
English and unified Chinese mixed-width Unitxt resources maintained by the
psobb-localization project.

Usage: python gen_zh.py [--localization-repo PATH]
"""

import argparse
import copy
import hashlib
import os
import struct
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from drop_data import DROP_TYPES, iter_entry_drops, load_js_data, write_generated_js
from prs import decompress


ROOT = Path(__file__).parent.parent
DEFAULT_LOCALIZATION_REPO = Path(
    os.environ.get("PSOBB_LOCALIZATION_REPO", ROOT.parent / "psobb-localization")
).expanduser()

EXPECTED_GROUP_COUNT = 73
EXPECTED_ENTRY_COUNT = 4935
ITEM_GROUP = 1
STANDARD_MONSTER_GROUP = 2
ULTIMATE_MONSTER_GROUP = 4
AREA_GROUP = 10

# These names occur at multiple Unitxt indexes. The drop chart refers to the
# weapon entries, not the enemy-part or ordinary-claw entries.
ITEM_INDEX_OVERRIDES = {
    "Dragon's Claw": 482,
    "Nei's Claw": 580,
}

# Ephinea chart spelling -> canonical English Unitxt spelling. Aliases never
# contain Chinese text; psobb-localization remains authoritative for names.
MONSTER_ALIASES = {
    "Dal Ral Lie": "Dal Ra Lie",
    "Gilchic": "Gillchic",
    "Gilchich": "Gillchich",
    "Gulgus-Gue": "Gulgus-gue",
    "Halo Rappy": "Hallo Rappy",
    "Saint Million": "Saint-Milion",
    "St. Rappy": "St Rappy",
    "Vol Opt ver. 2": "Vol Opt ver.2",
}

AREA_ALIASES = {
    "CCA": "Central Control Area",
    "Crater East": "Crater (Eastern Route)",
    "Crater West": "Crater (Western Route)",
    "Crater South": "Crater (Southern Route)",
    "Crater North": "Crater (Northern Route)",
    "Crater Int.": "Crater Interior",
    "Desert 1": "Subterranean Desert 1",
    "Desert 2": "Subterranean Desert 2",
    "Desert 3": "Subterranean Desert 3",
    "Jungle East": "Jungle Area East",
    "Jungle North": "Jungle Area North",
    "Mountain": "Mountain Area",
    "Seabed: Lower Levels": "Seabed Lower levels",
    "Seabed: Upper Levels": "Seabed Upper levels",
    "Seaside": "Seaside Area",
    "VR Spaceship: Alpha": "VR Spaceship Alpha",
    "VR Spaceship: Beta": "VR Spaceship Beta",
    "VR Temple: Alpha": "VR Temple Alpha",
    "VR Temple: Beta": "VR Temple Beta",
}

# This is a drop-chart category, not a game resource name.
CHART_ONLY_AREAS = {"Boss": "首领"}


@dataclass(frozen=True)
class UnitxtNameMaps:
    """Chinese names separated by Unitxt role and row-name context."""

    items: dict[str, str]
    standard_monsters: dict[str, str]
    ultimate_monsters: dict[str, str]
    areas: dict[str, str]


def parse_unitxt(path: Path) -> list[list[str]]:
    """Decode a PRS-compressed Unitxt file into indexed string groups."""
    data = decompress(path.read_bytes())

    num_groups = struct.unpack_from("<i", data, 0)[0]
    counts = [struct.unpack_from("<i", data, 4 + group * 4)[0] for group in range(num_groups)]

    def read_string(offset: int) -> str:
        if offset < 0 or offset >= len(data):
            return ""
        end = offset
        while end + 1 < len(data):
            if data[end] | (data[end + 1] << 8) == 0:
                break
            end += 2
        return data[offset:end].decode("utf-16-le") if end > offset else ""

    table_position = 4 + num_groups * 4
    groups = []
    for count in counts:
        strings = []
        for string_index in range(count):
            offset = struct.unpack_from("<I", data, table_position + string_index * 4)[0]
            strings.append(read_string(offset))
        table_position += count * 4
        groups.append(strings)
    return groups


def validate_unitxt_shape(en_groups: list[list[str]], zh_groups: list[list[str]]) -> None:
    """Reject sources outside psobb-localization's aligned Unitxt contract."""
    en_shape = [len(group) for group in en_groups]
    zh_shape = [len(group) for group in zh_groups]
    if en_shape != zh_shape:
        raise ValueError("English and Chinese Unitxt group shapes differ")
    if len(en_groups) != EXPECTED_GROUP_COUNT or sum(en_shape) != EXPECTED_ENTRY_COUNT:
        raise ValueError(
            "Unexpected Unitxt shape: "
            f"groups={len(en_groups)}, entries={sum(en_shape)}; "
            f"expected {EXPECTED_GROUP_COUNT}/{EXPECTED_ENTRY_COUNT}"
        )


def build_group_map(en_group: list[str], zh_group: list[str]) -> dict[str, str]:
    """Build a same-index map, omitting English names with conflicting meanings."""
    result: dict[str, str] = {}
    ambiguous: set[str] = set()
    for en_raw, zh_raw in zip(en_group, zh_group):
        en_name = en_raw.strip()
        zh_name = zh_raw.strip()
        if not en_name or not zh_name or en_name in ambiguous:
            continue
        previous = result.get(en_name)
        if previous is not None and previous != zh_name:
            result.pop(en_name)
            ambiguous.add(en_name)
        else:
            result[en_name] = zh_name
    return result


def apply_aliases(
    name_map: dict[str, str],
    aliases: dict[str, str],
    *,
    required: bool,
) -> set[str]:
    """Resolve English aliases through canonical Unitxt names."""
    resolved = set()
    for alias, canonical in aliases.items():
        if canonical in name_map:
            name_map[alias] = name_map[canonical]
            resolved.add(alias)
        elif required:
            raise ValueError(f"Unitxt canonical name missing for alias {alias!r}: {canonical!r}")
    return resolved


def build_name_maps(
    en_groups: list[list[str]],
    zh_groups: list[list[str]],
) -> UnitxtNameMaps:
    """Build role-aware English-to-Chinese maps from aligned Unitxt indexes."""
    validate_unitxt_shape(en_groups, zh_groups)

    items = build_group_map(en_groups[ITEM_GROUP], zh_groups[ITEM_GROUP])
    for name, index in ITEM_INDEX_OVERRIDES.items():
        actual_name = en_groups[ITEM_GROUP][index].strip()
        if actual_name != name:
            raise ValueError(
                f"Unitxt item override index {index} contains {actual_name!r}, "
                f"expected {name!r}"
            )
        zh_name = zh_groups[ITEM_GROUP][index].strip()
        if not zh_name:
            raise ValueError(f"Chinese Unitxt item is blank at index {index}: {name!r}")
        items[name] = zh_name

    standard_monsters = build_group_map(
        en_groups[STANDARD_MONSTER_GROUP], zh_groups[STANDARD_MONSTER_GROUP]
    )
    ultimate_monsters = build_group_map(
        en_groups[ULTIMATE_MONSTER_GROUP], zh_groups[ULTIMATE_MONSTER_GROUP]
    )
    resolved_aliases = apply_aliases(
        standard_monsters, MONSTER_ALIASES, required=False
    )
    resolved_aliases |= apply_aliases(
        ultimate_monsters, MONSTER_ALIASES, required=False
    )
    if unresolved := set(MONSTER_ALIASES) - resolved_aliases:
        raise ValueError(f"Monster aliases missing from Unitxt: {sorted(unresolved)}")

    areas = build_group_map(en_groups[AREA_GROUP], zh_groups[AREA_GROUP])
    apply_aliases(areas, AREA_ALIASES, required=True)
    areas.update(CHART_ONLY_AREAS)

    return UnitxtNameMaps(items, standard_monsters, ultimate_monsters, areas)


def translate_monster_name(en_name: str, name_maps: UnitxtNameMaps) -> str:
    """Translate the chart's standard/Ultimate monster-name pair."""
    parts = [part.strip() for part in en_name.split("/")]
    if len(parts) > 2:
        raise ValueError(f"Unexpected monster name shape: {en_name!r}")

    translated = []
    for index, part in enumerate(parts):
        if len(parts) == 1:
            zh_name = (
                name_maps.standard_monsters.get(part)
                or name_maps.ultimate_monsters.get(part)
            )
        else:
            source = name_maps.standard_monsters if index == 0 else name_maps.ultimate_monsters
            zh_name = source.get(part)
        if zh_name is None:
            raise ValueError(f"Unitxt monster mapping missing: {part!r} in {en_name!r}")
        translated.append(zh_name)
    return "/".join(translated)


def translate_area_name(en_name: str, name_maps: UnitxtNameMaps) -> str:
    """Translate every location in a chart box-row label."""
    translated = []
    for part in en_name.split("/"):
        name = part.strip()
        zh_name = name_maps.areas.get(name)
        if zh_name is None:
            raise ValueError(f"Unitxt area mapping missing: {name!r} in {en_name!r}")
        translated.append(zh_name)
    return "/".join(translated)


def translate_data(en_data: dict, name_maps: UnitxtNameMaps) -> dict:
    """Deep-copy English chart data and translate every display name."""
    zh_data = copy.deepcopy(en_data)

    for difficulty_data in zh_data["data"].values():
        for drop_type in DROP_TYPES:
            for entries in difficulty_data.get(drop_type, {}).values():
                for entry in entries:
                    if drop_type == "monsters":
                        entry["name"] = translate_monster_name(entry["name"], name_maps)
                    else:
                        entry["name"] = translate_area_name(entry["name"], name_maps)
                    for drop in iter_entry_drops(entry):
                        if en_item := drop.get("item"):
                            zh_item = name_maps.items.get(en_item)
                            if zh_item is None:
                                raise ValueError(f"Unitxt item mapping missing: {en_item!r}")
                            drop["item"] = zh_item

    return zh_data


def sha256(path: Path) -> str:
    """Return the exact Unitxt source hash for generated-data provenance."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--localization-repo",
        type=Path,
        default=DEFAULT_LOCALIZATION_REPO,
        help=(
            "psobb-localization checkout containing localization/en and localization/zh "
            "(default: sibling checkout or PSOBB_LOCALIZATION_REPO)"
        ),
    )
    return parser.parse_args()


def main() -> None:
    """Load authoritative Unitxt names and regenerate ``bb/data/zh.js``."""
    args = parse_args()
    localization_repo = args.localization_repo.resolve()
    localization_dir = localization_repo / "localization"
    en_unitxt = localization_dir / "en" / "unitxt_j.prs"
    zh_unitxt = localization_dir / "zh" / "unitxt_j.prs"
    missing_sources = [path for path in (en_unitxt, zh_unitxt) if not path.is_file()]
    if missing_sources:
        missing = ", ".join(str(path) for path in missing_sources)
        raise FileNotFoundError(
            f"psobb-localization Unitxt source missing: {missing}; "
            "set PSOBB_LOCALIZATION_REPO or pass --localization-repo"
        )

    print(f"Using psobb-localization: {localization_repo}")
    print("Parsing EN unitxt...")
    en_groups = parse_unitxt(en_unitxt)
    print(f"  Groups: {len(en_groups)}, entries: {sum(map(len, en_groups))}")

    print("Parsing ZH mixed-width unitxt...")
    zh_groups = parse_unitxt(zh_unitxt)
    print(f"  Groups: {len(zh_groups)}, entries: {sum(map(len, zh_groups))}")

    print("Building role-aware name maps from aligned Unitxt indexes...")
    name_maps = build_name_maps(en_groups, zh_groups)
    print(
        "  "
        f"{len(name_maps.items)} items, "
        f"{len(name_maps.standard_monsters)} standard monsters, "
        f"{len(name_maps.ultimate_monsters)} Ultimate monsters, "
        f"{len(name_maps.areas)} areas"
    )

    print("Loading EN drop data...")
    en_js_path = ROOT / "bb" / "data" / "en.js"
    en_data = load_js_data(en_js_path, "en")

    print("Translating to ZH...")
    zh_data = translate_data(en_data, name_maps)
    out_path = ROOT / "bb" / "data" / "zh.js"

    print("Writing data/zh.js...")
    size = write_generated_js(
        out_path,
        zh_data,
        language="zh",
        generator=f"gen_zh.py on {datetime.now().isoformat()}",
        source=(
            "Language: zh (psobb-localization mixed-width Unitxt; "
            f"EN SHA-256 {sha256(en_unitxt)}; ZH SHA-256 {sha256(zh_unitxt)})"
        ),
    )
    print(f"  Generated zh.js ({size / 1024:.1f} KB)")
    print("Done!")


if __name__ == "__main__":
    main()
