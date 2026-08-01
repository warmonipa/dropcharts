#!/usr/bin/env python3
"""
Generate Chinese drop chart data (data/zh.js).

Uses English drop data (data/en.js) as base, replaces monster/item names
with Chinese names extracted from the game's unitxt files.

  EN unitxt: D:/PSO/EphineaPSO2/data/unitxt_j.prs  (English original)
  ZH unitxt: D:/PSO/EphineaPSO/data/unitxt_j.prs   (Chinese patched)

Usage: python gen_zh.py
"""

import argparse
import copy
import json
import struct
from datetime import datetime
from pathlib import Path

from drop_data import (
    DROP_TYPES,
    iter_entry_drops,
    load_js_data,
    write_generated_js,
)
from prs import decompress

ROOT = Path(__file__).parent.parent
EN_UNITXT = r"D:\PSO\EphineaPSO2\data\unitxt_j.prs"
ZH_UNITXT = r"D:\PSO\EphineaPSO\data\unitxt_j.prs"


def parse_unitxt(path):
    """Parse a PRS-compressed unitxt file into groups of strings."""
    with open(path, "rb") as f:
        data = decompress(f.read())

    num_groups = struct.unpack_from("<i", data, 0)[0]
    counts = [struct.unpack_from("<i", data, 4 + g * 4)[0] for g in range(num_groups)]

    def read_str(offset):
        if offset < 0 or offset >= len(data):
            return ""
        end = offset
        while end + 1 < len(data):
            if data[end] | (data[end + 1] << 8) == 0:
                break
            end += 2
        return data[offset:end].decode("utf-16-le", errors="replace") if end > offset else ""

    table_pos = 4 + num_groups * 4
    groups = []
    for g in range(num_groups):
        strings = []
        for s in range(counts[g]):
            off = struct.unpack_from("<I", data, table_pos + s * 4)[0]
            strings.append(read_str(off))
        table_pos += counts[g] * 4
        groups.append(strings)
    return groups


def build_name_map(en_groups, zh_groups):
    """Build EN->ZH name mapping from unitxt groups."""
    name_map = {}

    # Group 1: Item names
    for i in range(min(len(en_groups[1]), len(zh_groups[1]))):
        en_name = en_groups[1][i].strip()
        zh_name = zh_groups[1][i].strip()
        if en_name and zh_name:
            name_map[en_name] = zh_name

    # Group 2: Monster names (Normal/Hard/VHard)
    for i in range(min(len(en_groups[2]), len(zh_groups[2]))):
        en_name = en_groups[2][i].strip()
        zh_name = zh_groups[2][i].strip()
        if en_name and zh_name:
            name_map[en_name] = zh_name

    # Group 4: Monster names (Ultimate)
    for i in range(min(len(en_groups[4]), len(zh_groups[4]))):
        en_name = en_groups[4][i].strip()
        zh_name = zh_groups[4][i].strip()
        if en_name and zh_name:
            name_map[en_name] = zh_name

    # Group 5: Technique names
    if len(en_groups) > 5 and len(zh_groups) > 5:
        for i in range(min(len(en_groups[5]), len(zh_groups[5]))):
            en_name = en_groups[5][i].strip()
            zh_name = zh_groups[5][i].strip()
            if en_name and zh_name:
                name_map[en_name] = zh_name

    return name_map


def translate_entry_name(en_name, name_map):
    """Translate a monster/box name that may contain '/' separators."""
    parts = en_name.split("/")
    translated = []
    for part in parts:
        p = part.strip()
        translated.append(name_map.get(p, p))
    return "/".join(translated)


def translate_data(en_data, name_map):
    """Deep-copy EN data and replace all names with ZH equivalents."""
    zh_data = copy.deepcopy(en_data)

    for diff_name, diff_data in zh_data["data"].items():
        for type_key in DROP_TYPES:
            type_data = diff_data.get(type_key, {})
            for ep, entries in type_data.items():
                for entry in entries:
                    # Translate monster/box name
                    entry["name"] = translate_entry_name(entry["name"], name_map)
                    # Translate item names in drops
                    for drop in iter_entry_drops(entry):
                        if drop.get("item"):
                            drop["item"] = name_map.get(drop["item"], drop["item"])

    return zh_data


def load_fallback_name_map():
    """Load EN-to-ZH names from the generated cross-version mapping."""
    path = ROOT / "i18n_names.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    name_map = {}
    for section in ("monsters", "items"):
        for en_name, translations in data.get(section, {}).items():
            if zh_name := translations.get("zh"):
                name_map[en_name] = zh_name
    return name_map


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--boxes-only",
        action="store_true",
        help="refresh box tables while preserving existing monster data",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    unitxt_available = Path(EN_UNITXT).is_file() and Path(ZH_UNITXT).is_file()
    if unitxt_available:
        print("Parsing EN unitxt...")
        en_groups = parse_unitxt(EN_UNITXT)
        print(f"  Items: {len(en_groups[1])}, Monsters: {len(en_groups[2])}")

        print("Parsing ZH unitxt...")
        zh_groups = parse_unitxt(ZH_UNITXT)
        print(f"  Items: {len(zh_groups[1])}, Monsters: {len(zh_groups[2])}")

        print("Building name map from unitxt...")
        name_map = build_name_map(en_groups, zh_groups)
        source_desc = "names from unitxt_j.prs Chinese patch"
    else:
        print("unitxt files unavailable; using i18n_names.json fallback...")
        name_map = load_fallback_name_map()
        source_desc = "names from i18n_names.json fallback"
    print(f"  {len(name_map)} name mappings")

    print("Loading EN drop data...")
    en_js_path = ROOT / "bb" / "data" / "en.js"
    en_data = load_js_data(en_js_path, "en")

    print("Translating to ZH...")
    zh_data = translate_data(en_data, name_map)
    out_path = ROOT / "bb" / "data" / "zh.js"
    if args.boxes_only:
        existing_zh = load_js_data(out_path, "zh")
        for difficulty, translated in zh_data["data"].items():
            existing_zh["data"][difficulty]["boxes"] = translated["boxes"]
        zh_data = existing_zh

    # Count untranslated names
    untranslated = set()
    for diff_data in zh_data["data"].values():
        for type_data in (diff_data.get("monsters", {}), diff_data.get("boxes", {})):
            for entries in type_data.values():
                for entry in entries:
                    for drop in iter_entry_drops(entry):
                        item = drop.get("item", "")
                        if item and not any(0x4E00 <= ord(c) <= 0x9FFF for c in item):
                            # Still ASCII — might be untranslated
                            if item not in name_map.values():
                                untranslated.add(item)
    if untranslated:
        print(f"  {len(untranslated)} untranslated items (kept as-is):")
        for name in sorted(untranslated)[:20]:
            print(f"    {name}")
        if len(untranslated) > 20:
            print(f"    ... and {len(untranslated) - 20} more")

    print("Writing data/zh.js...")
    output_dir = ROOT / "bb" / "data"
    output_dir.mkdir(exist_ok=True)

    size = write_generated_js(
        out_path,
        zh_data,
        language="zh",
        generator=f"gen_zh.py on {datetime.now().isoformat()}",
        source=f"Language: zh ({source_desc})",
    )
    print(f"  Generated zh.js ({size / 1024:.1f} KB)")
    print("Done!")


if __name__ == "__main__":
    main()
