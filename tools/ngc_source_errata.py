"""Corrections for known errors in the preserved NGC drop chart pages.

The pages come from ephinea4haven's droptable/ngc/*.html (initial commit
d9f96ff). docs/ngc-source-audit.md records how each correction was verified
against the GameCube rare item lists, newserv's rare-table-v3 and Ephinea's
classic charts. Every correction first checks that the source still holds the
expected error, so a changed source fails instead of being silently patched.
"""

import json
import re
from pathlib import Path

from drop_data import SECTION_IDS

ROOT = Path(__file__).resolve().parents[1]

# Malformed rate cells, keyed by their leading text. Ultimate Sinow Red /
# Redria prints the item name instead of its rate; the GC Episode 1 rare item
# list, ephinea4haven's droptable.sql and Ephinea's classic chart all give
# Agito (1975) 0.00992% (1/10082.46) there.
RATE_ERRATA = {
    "AGITO 1975 Dousetsu%": "0.009918212890625%",
}

# Source typos in item labels, per language.
ITEM_NAME_ERRATA = {
    "en": {
        "L&K15 COMBAT": "L&K14 Combat",
        "STORM VAND:INDRA": "Storm Wand: Indra",
    },
    "ja": {
        "L&K15コンバット": "L&K14コンバット",
    },
}

# Ultimate rows name monsters in English on both pages. Japanese names come
# from the authority; these source spellings have no authority entry.
ULTIMATE_JA_NAMES = {
    "Gulgus-gue": "ガルグス・グー",
    "GoVulmer": "ゴバルマー",
    "Gillchich": "ギルチッチ",
    "Dark Falz?": "ダークファルス?",
    "Olga Flow?": "オルガ・フロウ?",
}

CURE = {
    "paralysis": ("CURE PARALYSIS", "キュア/パラライズ"),
    "slow": ("CURE SLOW", "キュア/スロー"),
    "shock": ("CURE SHOCK", "キュア/ショック"),
    "freeze": ("CURE FROZEN", "キュア/フリーズ"),
}

# (difficulty, episode, source monster name, Section ID) -> (expected English
# source label, corrected English, corrected Japanese), from newserv item codes.
CELL_ERRATA = {
    ("Very Hard", "Episode 1", "プイィスライム", "Greenill"): ("CURE SHOCK", *CURE["paralysis"]),
    ("Very Hard", "Episode 1", "プイィスライム", "Pinkal"): ("CURE PARALYSIS", *CURE["slow"]),
    ("Very Hard", "Episode 1", "プイィスライム", "Yellowboze"): ("CURE FROZEN", *CURE["shock"]),
    ("Very Hard", "Episode 1", "プイィスライム", "Whitill"): ("CURE SLOW", *CURE["freeze"]),
    ("Very Hard", "Episode 1", "ダブチック", "Redria"): ("CURE SHOCK", *CURE["paralysis"]),
    ("Very Hard", "Episode 1", "カナン", "Viridia"): ("SENSE PLATE", "SMOKING PLATE", "スモーキングプレート"),
    ("Ultimate", "Episode 1", "Gulgus-gue", "Whitill"): ("CURE SLOW", *CURE["freeze"]),
    ("Ultimate", "Episode 1", "Dubchich", "Yellowboze"): ("CURE FROZEN", *CURE["shock"]),
    ("Ultimate", "Episode 1", "Sinow Blue", "Pinkal"): ("CURE PARALYSIS", *CURE["slow"]),
    ("Ultimate", "Episode 1", "Bulclaw", "Greenill"): ("CURE SHOCK", *CURE["paralysis"]),
    ("Very Hard", "Episode 2", "ミギウム", "Redria"): ("CURE SLOW", *CURE["freeze"]),
    ("Ultimate", "Episode 2", "Del-D", "Redria"): ("CURE PARALYSIS", *CURE["slow"]),
    ("Ultimate", "Episode 2", "Meriltas", "Viridia"): ("CURE FROZEN", *CURE["shock"]),
    ("Ultimate", "Episode 2", "Gee", "Greenill"): ("CURE PARALYSIS", *CURE["slow"]),
    ("Ultimate", "Episode 2", "Merikle", "Oran"): ("CURE SLOW", *CURE["freeze"]),
    ("Ultimate", "Episode 2", "Dolmolm", "Skyly"): ("CURE SHOCK", *CURE["paralysis"]),
}

# (difficulty, episode, source monster name) -> (expected source rate, corrected).
_EP2_RATES = {"80%": ("メリクル", "メリキュス"), "40%": ("イルギル",), "35%": ("デルリリー",), "30%": ("イプシロン",)}
_EP2_ULTIMATE = {"メリクル": "Merikle", "メリキュス": "Mericus", "イルギル": "Ill Gill",
                 "デルリリー": "Del Lily", "イプシロン": "Epsilon"}
DROP_RATE_ERRATA = {
    ("Ultimate", "Episode 1", "Hidelt"): ("80%", "85%"),
    ("Ultimate", "Episode 1", "Migium"): ("5%", "45%"),
    **{
        (difficulty, "Episode 2", _EP2_ULTIMATE[name] if difficulty == "Ultimate" else name): ("", rate)
        for difficulty in ("Normal", "Hard", "Very Hard", "Ultimate")
        for rate, names in _EP2_RATES.items()
        for name in names
    },
}

_NANO_DRAGON = ["sol", "tri", "tri", "sol", "sol", "tri", "sol", "sol", "sol", "tri"]
_GILCHIC = ["mono", None, None, "mono", None, None, None, None, None, None]
_ITEMS = {
    "en": {"sol": "Sol Atomizer", "tri": "Trimate", "mono": "Monogrinder"},
    "ja": {"sol": "ソルアトマイザー", "tri": "トリメイト", "mono": "モノグラインダー"},
}


def correct_rate(text):
    """Return the corrected rate for a malformed source rate cell, if known."""
    for malformed, rate in RATE_ERRATA.items():
        if text.startswith(malformed):
            return rate
    return None


def correct_item_name(name, lang, japanese_label, cell_text):
    """Normalize one parsed item label; Agito cells carry their year in the text."""
    if japanese_label == "アギト":
        year = re.search(r"(19|20)\d\d", cell_text)
        if not year:
            raise ValueError(f"Agito cell without a year: {cell_text!r}")
        return "アギト" if lang == "ja" else f"Agito ({year.group(0)})"
    return ITEM_NAME_ERRATA[lang].get(name, name)


def _authority_japanese_monsters():
    monsters = json.loads((ROOT / "i18n_names.json").read_text(encoding="utf-8"))["monsters"]
    return {name: entry["ja"] for name, entry in monsters.items() if entry.get("ja")}


def _row(rows, name, occurrence=0):
    matches = [row for row in rows if row["name"] == name]
    if len(matches) <= occurrence:
        raise ValueError(f"NGC source row missing: {name!r}")
    return matches[occurrence]


def _restored_row(name, drop_rate, pattern, rate, lang):
    drops = [
        {"item": _ITEMS[lang][key], "rate": rate} if key else {"item": "", "rate": "0.0%"}
        for key in pattern
    ]
    return {"name": name, "drops": drops, "dropRate": drop_rate}


def apply(difficulty, parsed, lang):
    """Correct one parsed difficulty for one language in place."""
    monsters = parsed["monsters"]

    for (diff, episode, name, section_id), (expected, english, japanese) in CELL_ERRATA.items():
        if diff != difficulty:
            continue
        cell = _row(monsters[episode], name)["drops"][SECTION_IDS.index(section_id)]
        if cell.get("en", cell["item"]) != expected:
            raise ValueError(f"NGC erratum no longer matches: {(diff, episode, name, section_id)}")
        cell["item"] = english if lang == "en" else japanese

    for (diff, episode, name), (expected, rate) in DROP_RATE_ERRATA.items():
        if diff != difficulty:
            continue
        row = _row(monsters[episode], name)
        if row.get("dropRate", "") != expected:
            raise ValueError(f"NGC drop rate erratum no longer matches: {(diff, episode, name)}")
        row["dropRate"] = rate

    if difficulty == "Normal":
        episode1 = monsters["Episode 1"]
        if any(row["name"] == "ナノノドラゴ" for row in episode1):
            raise ValueError("NGC Normal Episode 1 already lists Nano Dragon")
        episode1.insert(
            episode1.index(_row(episode1, "ナルリリー")) + 1,
            _restored_row("ナノノドラゴ", "50%", _NANO_DRAGON, "56.25%", lang),
        )
        episode2 = monsters["Episode 2"]
        first = episode2.index(_row(episode2, "ダブチック"))
        if episode2[first] != episode2[first + 1]:
            raise ValueError("NGC Normal Episode 2 no longer duplicates Dubchic")
        episode2[first] = _restored_row("ギルチック", "30%", _GILCHIC, "0.054931640625%", lang)

    if lang == "ja":
        for rows in monsters.values():
            for row in rows:
                for cell in row["drops"]:
                    # The Japanese pages label Flowen's Shield as armor in places.
                    if cell.get("item") == "フロウウェンの鎧" and cell.get("en") == "FLOWEN'S SHIELD":
                        cell["item"] = "フロウウェンの盾"
                    cell.pop("en", None)
        if difficulty == "Ultimate":
            authority = _authority_japanese_monsters()
            for rows in monsters.values():
                for row in rows:
                    japanese = ULTIMATE_JA_NAMES.get(row["name"]) or authority.get(row["name"])
                    if not japanese:
                        raise ValueError(f"No Japanese name for NGC Ultimate monster {row['name']!r}")
                    row["name"] = japanese
    return parsed
