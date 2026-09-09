#!/usr/bin/env python3
"""
Build unified i18n name mapping from all data sources (BB, NGC, DC, psohaven).
Generate translated data files for DC and NGC.

Usage: python build_i18n.py
"""

import argparse
import copy
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from drop_data import (
    DROP_TYPES,
    iter_entry_drops,
    iter_cell_drops,
    localize_section_ids,
    load_js_data,
    write_json,
    write_generated_js,
)
from gen_zh import build_name_maps, parse_unitxt

ROOT = Path(__file__).parent.parent
TRANSLATED_VERSIONS = ("dc", "ngc")
DEFAULT_LOCALIZATION_REPO = Path(
    os.environ.get("PSOBB_LOCALIZATION_REPO", ROOT.parent / "psobb-localization")
).expanduser()


# Source spellings from the checked-in legacy charts and authority. Values are
# canonical English Unitxt identities, never a second Chinese translation list.
ITEM_ALIASES = {
    "G-ASSASIN'S ARMS": "Grass Assassin's Arms",
    "Delsabre's Right Arm": "Delsaber's Right Arm",
    "Delsabre's Left Arm": "Delsaber's Left Arm",
    "C-bringer's Right Arm": "Bringer's Right Arm",
    "Belra's Right Arms": "Belra's Right Arm",
    "BOOMA'S RIGHT ARMS": "Booma's Right Arm",
    "GOBOOMA'S RIGHT ARMS": "Gobooma's Right Arm",
    "GIGOBOOMA'S RIGHT ARMS": "Gigobooma's Right Arm",
    "S-BERILL'S ARMS": "Sinow Berill's Arms",
    "GIGUE'S ARMS": "Gi Gue's Body",
    "Gal Gryphon Wing": "Gal Gryphon's Wing",
    "PART OF EGG BLASTER": "Parts of Egg Blaster",
    "KALADGOLG": "Kaladbolg",
    "ANGLE HARP": "Angel Harp",
    "NUG-2000 BAZOOKA": "NUG2000-Bazooka",
    "GREENNILL CARD": "Greenill Card",
    "BRUEFULL CARD": "Bluefull Card",
    "CURE SHOCK": "Cure/Shock",
    "CURE POISON": "Cure/Poison",
    "CURE CONFUSION": "Cure/Confuse",
    "CURE PARALYSIS": "Cure/Paralysis",
    "CURE FROZEN": "Cure/Freeze",
    "CURE SLOW": "Cure/Slow",
    "PARASITIC GENE FLOW": 'Parasitic Gene "Flow"',
    "CUSTOM RAY Ver.00": "Custom Ray ver.OO",
    "CUSTOM FRAME Ver.00": "Custom Frame ver.OO",
    "CUSTOM BARRIER Ver.00": "Custom Barrier ver.OO",
    "HP/Ressurection": "HP/Resurrection",
    "TP/Ressurection": "TP/Resurrection",
    "ADD SLOT": "AddSlot",
    "DISKA OF BRAVEMEN": "Diska of Braveman",
    "METEOR CUDGE": "Meteor Cudgel",
    "PARTISAN OF LIGHTING": "Partisan of Lightning",
    "MAGIC ROCK MOOLA": 'Magic Rock "Moola"',
    "MAGICSTONE IRITISTA": 'Magic Stone "Iritista"',
    "Magic Rock Heart Key": 'Magic Rock "Heart Key"',
    "FIRE SCEPTER:AGNI": "Fire Scepter: Agni",
    "STORM VAND:INDRA": "Storm Wand: Indra",
    "STORM WAND:INDRA": "Storm Wand: Indra",
    "EARTH WAND BROWNIE": "Earth Wand: Brownie",
    "PARASITE WEAR:De Rol": "Parasite Wear: De Rol",
    "PARASITE WEAR:Nelgal": "Parasite Wear: Nelgal",
    "PARASITE WEAR:Vajulla": "Parasite Wear: Vajulla",
    "VIRUS ARMOR:Lafuteria": "Virus Armor: Lafuteria",
    "GODS SHIELD BYAKKO": 'Gods Shield "Byakko"',
    "GODS SHIELD GENBU": 'Gods Shield "Genbu"',
    "GODS SHIELD SEIRYU": 'Gods Shield "Seiryu"',
    "GODS SHIELD SUZAKU": 'Gods Shield "Suzaku"',
    "GOD'S SHIELD \"KOURYU\"": 'Gods Shield "Kouryu"',
    "PROTON LAUNCHER": "Photon Launcher",
    "THE SIGH OF GOD": "The Sigh of a God",
    "GAME MAGAZNE": "Game Magazine",
    "Mr.Naka's Business Card": "Mr. Naka's Business Card",
    "SONICTEAM ARMOR": "Sonic Team Armor",
    "TypeGU/HANDGUN": "TypeGU/Hand",
    "TypeN-SL/CLAW": "TypeSL/Claw",
    "TypeN-SL/J-SWORD": "TypeSL/Katana",
    "TypeN-SL/SABER": "TypeSL/Saber",
    "TypeN-SL/SLICER": "TypeSL/Slicer",
    # Historical dictionary spellings, reviewed beyond active drop cells.
    "DB'S SABER 3062": "DB's Saber (3062)",
    "DB’S Saber 3077": "DB's Saber (3077)",
    "DB’S Saber (No 9*)": "DB's Saber",
    "MARK3": "Mark III",
    "Kit of MARK3": "Kit of Mark III",
    "P-ARMS'S BLADE": "P-Arms' Blade",
    "PRINCIPAL'S GIFT PARASOL": "Tyrell's Parasol",
    "Unused Item0": "Unused Item01",
    "AGITO 1975": "Agito (1975)",
    "AGITO 1977": "Agito (1977)",
    "AGITO 1980": "Agito (1980)",
    "AGITO 1983": "Agito (1983)",
    "AGITO 1991": "Agito (1991)",
    "AGITO 2001": "Agito (2001)",
    "Book of KATANA1": "Book of Katana 1",
    "Book of KATANA2": "Book of Katana 2",
    "Book of KATANA3": "Book of Katana 3",
    "Bronze Weapons Badge": "Weapons Bronze Badge",
    "Silver Weapons Badge": "Weapons Silver Badge",
    "Gold Weapons Badge": "Weapons Gold Badge",
    "Crystal Weapons Badge": "Weapons Crystal Badge",
    "Steel Weapons Badge": "Weapons Steel Badge",
    "Aluminum Weapons Badge": "Weapons Aluminum Badge",
    "Leather Weapons Badge": "Weapons Leather Badge",
    "Bone Weapons Badge": "Weapons Bone Badge",
    "Silver Badge": "Weapons Silver Badge",
    "Gold Badge": "Weapons Gold Badge",
    "Crystal Badge": "Weapons Crystal Badge",
    "Aluminum Badge": "Weapons Aluminum Badge",
    "Leather Badge": "Weapons Leather Badge",
    "Bone Badge": "Weapons Bone Badge",
    "エンジェル/ＴＰ": "Angel/TP",
    "オパオパの心": "Heart of Opa Opa",
    "オモチャオのパーツ": "Parts of RoboChao",
    "カラドボルグ": "Kaladbolg",
    "キュア/ポイズン": "Cure/Poison",
    "クラブ": "Club",
    "サイキックバリア": "Psychic Barrier",
    "セレスティアルシールド": "Celestial Shield",
    "チャオの心": "Heart of Chao",
    "ディグラインダー": "Digrinder",
    "ディヴィニティアーマー": "Divinity Armor",
    "ハンターウォル": "Hunter Wall",
    "ハンターフィールド": "Hunter Field",
    "パラッシュ": "Pallasch",
    "ピアンの心": "Heart of Pian",
    "フォースウォル": "Force Wall",
    "フォースフィールド": "Force Field",
    "マグ細胞２１３": "Cell of Mag 213",
    "マグ細胞５０２": "Cell of Mag 502",
    "マジカルピース": "Magical Piece",
    "レンジャーウォル": "Ranger Wall",
    "レールガン": "Railgun",
    "ロックガン": "Lockgun",
    "四天　参の巻": "Book of Katana 3",
    "四天　壱の巻": "Book of Katana 1",
    "四天　弐の巻": "Book of Katana 2",
    "四神盾「朱雀」": "Gods Shield \"Suzaku\"",
    "四神盾「玄武」": "Gods Shield \"Genbu\"",
    "四神盾「白虎」": "Gods Shield \"Byakko\"",
    "四神盾「青龍」": "Gods Shield \"Seiryu\"",
    "寄生防具「デ・ロル」": "Parasite Wear: De Rol",
    "寄生防具「ネルガル」": "Parasite Wear: Nelgal",
    "寄生防具「ヴァジュラ」": "Parasite Wear: Vajulla",
    "秋子おばさんの中華鍋": "Akiko's Wok",
    "細菌防具「ラフテリア」": "Virus Armor: Lafuteria",
    "雷杖「インドラ」": "Storm Wand: Indra",
    "ＨＰ/ジェネレイト": "HP/Generate",
    "ＴＰ/ジェネレイト": "TP/Generate",
    "ウィジャヤ": "Vjaya",
    "グレイヴ": "Glaive",
    "フロウウウェンの盾": "Flowen's Shield",
    "レンジャーフールド": "Ranger Field",
    "Chaos Bringerの右手": "Bringer's Right Arm",
    "Chaos Sorcererの右手": "Sorcerer's Right Arm",
    "Delsaberの右手": "Delsaber's Right Arm",
    "Delsaberの左手": "Delsaber's Left Arm",
    "Hildebearの頭": "Hildebear's Head",
    "Hildeblueの頭": "Hildeblue's Head",
    "Pan Armsの両手": "P-arm's Arms",
    "Sinow Beatの両手": "S-beat's Arms",
    "Dragonフレーム": "Dragon Frame",
}

MONSTER_NAME_ALIASES = {
    "Hidelt": "Hildelt",
    "Hildetor": "Hildetorr",
    "Pouifully Slime": "Pofuilly Slime",
    "ゴルドラゴン": "Gol Dragon",
    "Dark Falz?": "Dark Falz",
    "ダークファルス?": "Dark Falz",
    "Olga Flow?": "Olga Flow",
    "オルガ・フロウ?": "Olga Flow",
}

# These legacy English family labels lose the year carried by the paired
# Japanese source. Only DB 3069 also needs its Section ID to select a maker.
LEGACY_WEAPON_FAMILIES = {
    "DB'S SWORD": ("DBの剣", "DB's Saber"),
    "FLOWEN'S SWORD": ("フロウウェンの剣", "Flowen's Sword"),
}
DB_3069_MANUFACTURERS = {"Bluefull": "Chris", "Pinkal": "Torato"}


@dataclass(frozen=True)
class NameLookup:
    """Exact, normalized and Japanese indexes for one kind of name."""

    exact: dict
    normalized: dict
    japanese: dict


def normalize_key(name):
    """Normalize a name for fuzzy matching: NFKC, lowercase, strip spaces."""
    s = unicodedata.normalize("NFKC", name)
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    # Normalize apostrophes/quotes to hyphens for matching
    s = s.replace("'", "-").replace("\u2019", "-")
    return s


def extract_names(data):
    """Extract all monster names and item names from drop data."""
    monsters = []
    items = []
    for diff_data in data["data"].values():
        for section_key in DROP_TYPES:
            section = diff_data.get(section_key, {})
            for ep_entries in section.values():
                for entry in ep_entries:
                    monsters.append(entry["name"])
                    for drop in iter_entry_drops(entry):
                        if drop.get("item"):
                            items.append(drop["item"])
    return monsters, items


def add_name_parts(
    en_name,
    ja_name,
    zh_name,
    target_map,
    target_norm,
    *,
    prefer_later_parts,
):
    """Merge a compound chart label into the flat cross-version name map.

    BB monster labels encode standard and Ultimate names as the first and
    second parts. If both parts have the same English name but different
    translations, downstream DC/NGC data needs the Ultimate translation.
    """
    en_parts = en_name.split("/")
    translations = {
        "ja": ja_name.split("/") if ja_name else [],
        "zh": zh_name.split("/") if zh_name else [],
    }

    for part_index, en_part in enumerate(en_parts):
        en_part = en_part.strip()
        if not en_part:
            continue

        normalized = normalize_key(en_part)
        if normalized not in target_norm:
            target_norm[normalized] = en_part
            target_map[en_part] = {}
        canonical = target_norm[normalized]

        for language, parts in translations.items():
            if part_index >= len(parts) or not parts[part_index].strip():
                continue
            if language not in target_map[canonical] or (
                prefer_later_parts and part_index > 0
            ):
                target_map[canonical][language] = parts[part_index].strip()


def load_authoritative_names():
    """Load the sole hand-maintained name authority."""
    path = ROOT / "i18n_names.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if set(data) != {"monsters", "items"}:
        raise ValueError("i18n_names.json must contain monsters and items")
    return data


def load_unitxt_name_maps(localization_repo: Path):
    """Load psobb-localization's aligned mixed-width Unitxt name maps."""
    localization_dir = localization_repo.resolve() / "localization"
    en_path = localization_dir / "en" / "unitxt_j.prs"
    zh_path = localization_dir / "zh" / "unitxt_j.prs"
    missing = [path for path in (en_path, zh_path) if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "psobb-localization Unitxt source missing: "
            + ", ".join(str(path) for path in missing)
        )
    return build_name_maps(parse_unitxt(en_path), parse_unitxt(zh_path))


def merge_names(source, target_map, target_norm, *, replace):
    """Merge an English-keyed translation mapping by normalized identity."""
    for en_name, translations in source.items():
        normalized = normalize_key(en_name)
        if normalized in target_norm:
            canonical = target_norm[normalized]
        else:
            canonical = en_name
            target_norm[normalized] = canonical
            target_map[canonical] = {}
        for language in ("ja", "zh"):
            value = translations.get(language)
            if value and (replace or language not in target_map[canonical]):
                target_map[canonical][language] = value


def merge_source_aliases(source, target_map, target_norm, aliases):
    """Replace an existing alias from its canonical source, preserving metadata."""
    for alias, canonical in aliases.items():
        target = target_norm.get(normalize_key(alias))
        if target is None:
            continue
        if canonical not in source:
            raise ValueError(f"Unitxt canonical identity missing for {alias!r}: {canonical!r}")
        suffix = "?" if alias.endswith("?") else ""
        target_map[target]["zh"] = source[canonical] + suffix


def merge_unitxt_item_names(source, target_map, target_norm):
    """Merge Unitxt items without collapsing case-sensitive name identities."""
    groups = {}
    for name, zh_name in source.items():
        groups.setdefault(normalize_key(name), []).append((name, zh_name))

    regular = {}
    case_sensitive = []
    for entries in groups.values():
        if len({zh_name for _, zh_name in entries}) > 1:
            case_sensitive.extend(entries)
        else:
            regular.update({name: {"zh": zh_name} for name, zh_name in entries})

    merge_names(regular, target_map, target_norm, replace=True)

    for name, zh_name in case_sensitive:
        target_map.setdefault(name, {})["zh"] = zh_name
        target_norm.setdefault(normalize_key(name), name)

    merge_source_aliases(source, target_map, target_norm, ITEM_ALIASES)


def merge_unitxt_context_names(unitxt, items_map):
    """Refresh existing non-item labels without crossing a real item identity."""
    context = unitxt.standard_monsters | unitxt.ultimate_monsters | unitxt.areas
    for alias, canonical in MONSTER_NAME_ALIASES.items():
        if canonical in context:
            context[alias] = context[canonical] + ("?" if alias.endswith("?") else "")
    item_identities = {normalize_key(name) for name in unitxt.items}
    for name in items_map.keys() & context.keys():
        if normalize_key(name) not in item_identities:
            items_map[name]["zh"] = context[name]


def resolve_ngc_item_name(name, japanese_name, section_id):
    """Recover a legacy weapon identity from its paired Japanese label."""
    family = LEGACY_WEAPON_FAMILIES.get(name)
    if family is None:
        return name
    japanese_base, canonical_base = family
    if name == "FLOWEN'S SWORD" and japanese_name == japanese_base:
        return canonical_base
    match = re.fullmatch(re.escape(japanese_base) + r"\[(\d{4})\]", japanese_name)
    if match is None:
        raise ValueError(f"Missing or invalid Japanese variant for {name!r}: {japanese_name!r}")
    year = match[1]
    if name == "DB'S SWORD" and year == "3069":
        maker = DB_3069_MANUFACTURERS.get(section_id)
        if maker is None:
            raise ValueError(f"Unknown DB 3069 manufacturer: {section_id!r}")
        year += f" {maker}"
    return f"{canonical_base} ({year})"


def resolve_ngc_item_names(data, japanese_data, known_items):
    """Resolve family labels before authority merging or display translation."""
    result = copy.deepcopy(data)
    for difficulty, types in result["data"].items():
        for kind in DROP_TYPES:
            for episode, rows in types.get(kind, {}).items():
                for row_index, row in enumerate(rows):
                    for column, cell in enumerate(row.get("drops", [])):
                        drops = list(iter_cell_drops(cell))
                        if not any(drop.get("item") in LEGACY_WEAPON_FAMILIES for drop in drops):
                            continue
                        try:
                            ja_row = japanese_data["data"][difficulty][kind][episode][row_index]
                            ja_drops = list(iter_cell_drops(ja_row["drops"][column]))
                        except (KeyError, IndexError) as error:
                            raise ValueError("Missing paired Japanese weapon cell") from error
                        if len(drops) != len(ja_drops):
                            raise ValueError("Paired Japanese weapon cell cardinality differs")
                        for drop, ja_drop in zip(drops, ja_drops):
                            name = drop.get("item", "")
                            if name not in LEGACY_WEAPON_FAMILIES:
                                continue
                            canonical = resolve_ngc_item_name(
                                name, ja_drop.get("item", ""), data["sectionIds"][column]
                            )
                            if canonical not in known_items:
                                raise ValueError(f"Unitxt weapon variant missing: {canonical!r}")
                            drop["item"] = canonical
    return result


def build_mapping(localization_repo=DEFAULT_LOCALIZATION_REPO):
    """Build unified i18n mapping from all sources."""
    unitxt = load_unitxt_name_maps(Path(localization_repo))

    # Mapping: normalized_en -> {"en": original_en, "ja": ja, "zh": zh}
    # We track both monsters and items separately
    monsters_map = {}  # en_name -> {"ja": ..., "zh": ...}
    items_map = {}     # en_name -> {"ja": ..., "zh": ...}

    # Also keep lookup indices: normalized -> canonical en name
    monster_norm = {}  # normalized -> en_name
    item_norm = {}     # normalized -> en_name

    # Additional: JA -> EN reverse lookup for DC items that may be in Japanese
    ja_to_en_items = {}  # ja_name -> en_name

    def ensure_monster(en_name):
        nk = normalize_key(en_name)
        if nk not in monster_norm:
            monster_norm[nk] = en_name
            monsters_map[en_name] = {}
        return monster_norm[nk]

    def ensure_item(en_name):
        nk = normalize_key(en_name)
        if nk not in item_norm:
            item_norm[nk] = en_name
            items_map[en_name] = {}
        return item_norm[nk]

    # ========== 1. BB data (highest priority) ==========
    print("Loading BB data...")
    bb_en = load_js_data(ROOT / "bb" / "data" / "en.js", "en")
    bb_ja = load_js_data(ROOT / "bb" / "data" / "ja.js", "ja")
    bb_zh = load_js_data(ROOT / "bb" / "data" / "zh.js", "zh")

    # Pair by position
    for diff_name in bb_en["data"]:
        for section_key in DROP_TYPES:
            en_section = bb_en["data"][diff_name].get(section_key, {})
            ja_section = bb_ja["data"][diff_name].get(section_key, {})
            zh_section = bb_zh["data"][diff_name].get(section_key, {})
            for ep in en_section:
                en_entries = en_section[ep]
                ja_entries = ja_section.get(ep, [])
                zh_entries = zh_section.get(ep, [])
                for i, en_entry in enumerate(en_entries):
                    ja_entry = ja_entries[i] if i < len(ja_entries) else None
                    zh_entry = zh_entries[i] if i < len(zh_entries) else None

                    target_map = monsters_map if section_key == "monsters" else items_map
                    target_norm = monster_norm if section_key == "monsters" else item_norm
                    add_name_parts(
                        en_entry["name"],
                        ja_entry["name"] if ja_entry else "",
                        zh_entry["name"] if zh_entry else "",
                        target_map,
                        target_norm,
                        prefer_later_parts=section_key == "monsters",
                    )

                    # Item names in drops
                    ja_drops = list(iter_entry_drops(ja_entry)) if ja_entry else []
                    zh_drops = list(iter_entry_drops(zh_entry)) if zh_entry else []
                    for di, drop in enumerate(iter_entry_drops(en_entry)):
                        en_item = drop.get("item", "")
                        if not en_item:
                            continue
                        nk = normalize_key(en_item)
                        if nk not in item_norm:
                            item_norm[nk] = en_item
                            items_map[en_item] = {}
                        canonical = item_norm[nk]

                        if di < len(ja_drops):
                            ja_item = ja_drops[di].get("item", "")
                            if ja_item and "ja" not in items_map[canonical]:
                                items_map[canonical]["ja"] = ja_item
                                ja_to_en_items[ja_item] = canonical
                        if di < len(zh_drops):
                            zh_item = zh_drops[di].get("item", "")
                            if zh_item and "zh" not in items_map[canonical]:
                                items_map[canonical]["zh"] = zh_item

    bb_monsters = len(monsters_map)
    bb_items = len(items_map)
    print(f"  BB: {bb_monsters} monsters, {bb_items} items")

    # ========== 2. NGC data ==========
    print("Loading NGC data...")
    ngc_en = load_js_data(ROOT / "ngc" / "data" / "en.js", "en")
    ngc_ja = load_js_data(ROOT / "ngc" / "data" / "ja.js", "ja")
    ngc_en = resolve_ngc_item_names(ngc_en, ngc_ja, unitxt.items)

    # NGC: monster names are the same in EN and JA (JA for normal, EN for ultimate)
    # Items differ between EN and JA
    for diff_name in ngc_en["data"]:
        for section_key in DROP_TYPES:
            en_section = ngc_en["data"][diff_name].get(section_key, {})
            ja_section = ngc_ja["data"][diff_name].get(section_key, {})
            for ep in en_section:
                en_entries = en_section[ep]
                ja_entries = ja_section.get(ep, [])
                for i, en_entry in enumerate(en_entries):
                    ja_entry = ja_entries[i] if i < len(ja_entries) else None

                    # Monster names - for NGC, EN has JA names for non-ultimate
                    # and EN names for ultimate. Both files have the same names.
                    # We can use these JA names to populate ja mapping for monsters
                    # that we already know the EN name for
                    monster_name = en_entry["name"]
                    # Check if this is a JA name (katakana/kanji)
                    has_jp = any(
                        unicodedata.category(c).startswith("Lo")
                        or "KATAKANA" in unicodedata.name(c, "")
                        or "HIRAGANA" in unicodedata.name(c, "")
                        for c in monster_name
                        if ord(c) > 127
                    )
                    if not has_jp or monster_name in MONSTER_NAME_ALIASES:
                        # Register English names and reviewed Japanese aliases.
                        ensure_monster(monster_name)

                    # Items - pair EN and JA by position
                    ja_drops = list(iter_entry_drops(ja_entry)) if ja_entry else []
                    for di, drop in enumerate(iter_entry_drops(en_entry)):
                        en_item = drop.get("item", "")
                        if not en_item:
                            continue
                        nk = normalize_key(en_item)
                        if nk not in item_norm:
                            item_norm[nk] = en_item
                            items_map[en_item] = {}
                        canonical = item_norm[nk]

                        if di < len(ja_drops):
                            ja_item = ja_drops[di].get("item", "")
                            if ja_item and "ja" not in items_map[canonical]:
                                items_map[canonical]["ja"] = ja_item
                                ja_to_en_items[ja_item] = canonical

    ngc_new_items = len(items_map) - bb_items
    print(f"  NGC added: {len(monsters_map) - bb_monsters} monsters, {ngc_new_items} items")

    # ========== 3. Sole authority ==========
    print("Loading authoritative names from i18n_names.json...")
    authoritative = load_authoritative_names()
    merge_names(authoritative["monsters"], monsters_map, monster_norm, replace=True)
    merge_names(authoritative["items"], items_map, item_norm, replace=True)

    # ========== 4. psobb-localization Unitxt ==========
    # Unitxt controls Chinese wording and per-name character width wherever an
    # aligned English identity exists. Uncovered authority entries are kept.
    print("Aligning authoritative Chinese names from mixed-width Unitxt...")
    merge_unitxt_item_names(unitxt.items, items_map, item_norm)
    merge_unitxt_context_names(unitxt, items_map)
    monster_names = {
        name: {"zh": zh} for name, zh in unitxt.standard_monsters.items()
    }
    monster_names.update(
        {name: {"zh": zh} for name, zh in unitxt.ultimate_monsters.items()}
    )
    merge_names(monster_names, monsters_map, monster_norm, replace=True)
    print(
        f"  Authority: {len(monsters_map)} monsters, {len(items_map)} items"
    )

    merge_source_aliases(
        {name: translations["zh"] for name, translations in monster_names.items()},
        monsters_map, monster_norm, MONSTER_NAME_ALIASES,
    )

    # Store ja_to_en_items for DC translation
    return monsters_map, items_map, ja_to_en_items


def build_translation_lookup(monsters_map, items_map, ja_to_en_items):
    """Build separate indexes so item names cannot replace monster names."""
    result = {}
    for role, source in (("monsters", monsters_map), ("items", items_map)):
        lookup = {name: dict(trans) for name, trans in source.items() if trans}
        normalized = {}
        ambiguous = set()
        for name, trans in lookup.items():
            key = normalize_key(name)
            previous = normalized.get(key)
            if previous is not None and previous.get("zh") != trans.get("zh"):
                ambiguous.add(key)
            normalized[key] = trans
        for key in ambiguous:
            normalized.pop(key, None)

        japanese = {}
        if role == "items":
            for ja_name, en_name in ja_to_en_items.items():
                if en_name in lookup:
                    japanese[ja_name] = lookup[en_name]
        for trans in source.values():
            if "ja" in trans:
                japanese.setdefault(trans["ja"], dict(trans))
        result[role] = NameLookup(lookup, normalized, japanese)
    return result


def translate_name(name, names, target_lang):
    """Translate a single name to target language. Returns translated name or original."""
    if not name:
        return name

    lookup, norm_lookup, ja_lookup = names.exact, names.normalized, names.japanese

    # Direct lookup
    if name in lookup and target_lang in lookup[name]:
        return lookup[name][target_lang]

    # JA lookup (for DC items that are already in Japanese)
    if name in ja_lookup:
        if target_lang in ja_lookup[name]:
            return ja_lookup[name][target_lang]
        # If target is ja, the name is already JA
        if target_lang == "ja":
            return name

    # Normalized lookup
    nk = normalize_key(name)
    if nk in norm_lookup and target_lang in norm_lookup[nk]:
        return norm_lookup[nk][target_lang]

    # For JA target and a name that's already Japanese, keep as-is
    if target_lang == "ja":
        has_jp = any(
            unicodedata.category(c).startswith("Lo")
            or "KATAKANA" in unicodedata.name(c, "")
            or "HIRAGANA" in unicodedata.name(c, "")
            for c in name if ord(c) > 127
        )
        if has_jp:
            return name

    return name


def translate_data(data, lookups, target_lang):
    """Translate all names in drop data to target language."""
    result = copy.deepcopy(data)
    localize_section_ids(result, target_lang)
    for diff_data in result["data"].values():
        for section_key in DROP_TYPES:
            section = diff_data.get(section_key, {})
            for entries in section.values():
                for entry in entries:
                    # Monster/box name - may be compound
                    parts = entry["name"].split("/")
                    translated_parts = [
                        translate_name(
                            p.strip(), lookups["monsters" if section_key == "monsters" else "items"],
                            target_lang,
                        )
                        for p in parts
                    ]
                    entry["name"] = "/".join(translated_parts)
                    for drop in iter_entry_drops(entry):
                        if name := drop.get("item"):
                            drop["item"] = translate_name(name, lookups["items"], target_lang)
    return result


def write_js(data, path, var_name, lang, source_desc):
    """Write data as JS file."""
    expected_var_name = f"DROP_DATA_{lang.upper()}"
    if var_name != expected_var_name:
        raise ValueError(
            f"Variable {var_name} does not match language {lang}"
        )
    return write_generated_js(
        path,
        data,
        language=lang,
        generator=f"build_i18n.py on {datetime.now().isoformat()}",
        source=f"Source: {source_desc}",
    )


def _is_already_target_lang(name, target_lang):
    """Check if a name is already in the target language (JA/ZH)."""
    if target_lang == "ja":
        return any(
            "KATAKANA" in unicodedata.name(c, "")
            or "HIRAGANA" in unicodedata.name(c, "")
            or "CJK" in unicodedata.name(c, "")
            for c in name if ord(c) > 127
        )
    if target_lang == "zh":
        return any(
            "CJK" in unicodedata.name(c, "")
            for c in name if ord(c) > 127
        )
    return False


def count_coverage(data, lookups, target_lang):
    """Count how many names can be translated vs total."""
    total_monsters = 0
    translated_monsters = 0
    total_items = 0
    translated_items = 0
    gaps_monsters = set()
    gaps_items = set()

    for diff_data in data["data"].values():
        for section_key in DROP_TYPES:
            section = diff_data.get(section_key, {})
            for entries in section.values():
                for entry in entries:
                    parts = entry["name"].split("/")
                    for p in parts:
                        p = p.strip()
                        if not p:
                            continue
                        total_monsters += 1
                        translated = translate_name(
                            p, lookups["monsters" if section_key == "monsters" else "items"],
                            target_lang,
                        )
                        if translated != p or _is_already_target_lang(p, target_lang):
                            translated_monsters += 1
                        else:
                            gaps_monsters.add(p)

                    for drop in iter_entry_drops(entry):
                        item = drop.get("item", "")
                        if not item:
                            continue
                        total_items += 1
                        translated = translate_name(item, lookups["items"], target_lang)
                        if translated != item or _is_already_target_lang(item, target_lang):
                            translated_items += 1
                        else:
                            gaps_items.add(item)

    return {
        "total_monsters": total_monsters,
        "translated_monsters": translated_monsters,
        "total_items": total_items,
        "translated_items": translated_items,
        "gaps_monsters": gaps_monsters,
        "gaps_items": gaps_items,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "versions",
        choices=TRANSLATED_VERSIONS,
        nargs="*",
        default=TRANSLATED_VERSIONS,
        help="translated datasets to rebuild (mapping is always refreshed)",
    )
    parser.add_argument(
        "--localization-repo",
        type=Path,
        default=DEFAULT_LOCALIZATION_REPO,
        help="psobb-localization checkout (default: sibling checkout)",
    )
    args = parser.parse_args()
    versions = set(args.versions)

    print("=" * 60)
    print("Building unified i18n name mapping")
    print("=" * 60)

    monsters_map, items_map, ja_to_en_items = build_mapping(args.localization_repo)
    lookups = build_translation_lookup(
        monsters_map, items_map, ja_to_en_items
    )

    # ========== Write i18n_names.json ==========
    print("\nWriting i18n_names.json...")
    output = {
        "monsters": {k: v for k, v in sorted(monsters_map.items()) if v},
        "items": {k: v for k, v in sorted(items_map.items()) if v},
    }
    i18n_path = ROOT / "i18n_names.json"
    write_json(i18n_path, output)
    m_with_ja = sum(1 for v in monsters_map.values() if "ja" in v)
    m_with_zh = sum(1 for v in monsters_map.values() if "zh" in v)
    i_with_ja = sum(1 for v in items_map.values() if "ja" in v)
    i_with_zh = sum(1 for v in items_map.values() if "zh" in v)
    print(f"  Monsters: {len(monsters_map)} total, {m_with_ja} ja, {m_with_zh} zh")
    print(f"  Items: {len(items_map)} total, {i_with_ja} ja, {i_with_zh} zh")

    # ========== Generate DC translated files ==========
    sources = []
    if "dc" in versions:
        print("\nGenerating DC translations...")
        dc_en = load_js_data(ROOT / "dc" / "data" / "en.js", "en")

        for lang in ("ja", "zh"):
            translated = translate_data(
                dc_en,
                lookups,
                lang,
            )
            out_path = ROOT / "dc" / "data" / f"{lang}.js"
            size = write_js(
                translated,
                out_path,
                f"DROP_DATA_{lang.upper()}",
                lang,
                f"DC drop charts ({lang})",
            )
            print(f"  Written {out_path} ({size / 1024:.1f} KB)")
            sources.append((f"DC -> {lang}", dc_en, lang))

    # ========== Generate NGC zh.js ==========
    if "ngc" in versions:
        print("\nGenerating NGC zh translation...")
        ngc_en = resolve_ngc_item_names(
            load_js_data(ROOT / "ngc" / "data" / "en.js", "en"),
            load_js_data(ROOT / "ngc" / "data" / "ja.js", "ja"),
            items_map,
        )
        ngc_zh = translate_data(
            ngc_en,
            lookups,
            "zh",
        )
        out_path = ROOT / "ngc" / "data" / "zh.js"
        size = write_js(
            ngc_zh,
            out_path,
            "DROP_DATA_ZH",
            "zh",
            "NGC drop charts (zh)",
        )
        print(f"  Written {out_path} ({size / 1024:.1f} KB)")
        sources.append(("NGC -> zh", ngc_en, "zh"))

    # ========== Coverage summary ==========
    print("\n" + "=" * 60)
    print("Coverage Summary")
    print("=" * 60)

    all_gaps = {}
    for label, data, lang in sources:
        cov = count_coverage(data, lookups, lang)
        m_pct = (
            cov["translated_monsters"] / cov["total_monsters"] * 100
            if cov["total_monsters"] else 0
        )
        i_pct = (
            cov["translated_items"] / cov["total_items"] * 100
            if cov["total_items"] else 0
        )
        print(f"\n  {label}:")
        print(f"    Monsters: {cov['translated_monsters']}/{cov['total_monsters']} ({m_pct:.1f}%)")
        print(f"    Items: {cov['translated_items']}/{cov['total_items']} ({i_pct:.1f}%)")

        key = f"{label}"
        if cov["gaps_monsters"] or cov["gaps_items"]:
            all_gaps[key] = {
                "monsters": sorted(cov["gaps_monsters"]),
                "items": sorted(cov["gaps_items"]),
            }

    if all_gaps:
        print("\n" + "=" * 60)
        print("Remaining Gaps")
        print("=" * 60)
        for label, gaps in all_gaps.items():
            if gaps["monsters"]:
                print(f"\n  {label} - untranslated monsters ({len(gaps['monsters'])}):")
                for name in gaps["monsters"][:15]:
                    print(f"    - {name}")
                if len(gaps["monsters"]) > 15:
                    print(f"    ... and {len(gaps['monsters']) - 15} more")
            if gaps["items"]:
                print(f"\n  {label} - untranslated items ({len(gaps['items'])}):")
                for name in gaps["items"][:15]:
                    print(f"    - {name}")
                if len(gaps["items"]) > 15:
                    print(f"    ... and {len(gaps['items']) - 15} more")

    print("\nDone!")


if __name__ == "__main__":
    main()
