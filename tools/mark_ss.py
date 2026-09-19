#!/usr/bin/env python3
"""Mark BB banner highlights and legacy DC/NGC SS-tier drops.

Runs as the final pipeline step after all language data files exist. BB
uses banner_rules.py; the legacy SS name list below applies to DC/NGC.

Rarity is a property of the *item*, not of its localized name, so the
canonical English name is the language-independent key. For each version
the English file decides which (difficulty, type, episode, entry, drop)
coordinates receive highlights; that metadata is then stamped onto the en/ja/zh files in
lockstep (their structures are parallel by construction).

BB uses the named main-server banner list in banner_rules.py: no-Hit items
get `ss: true`, and conditional weapons get `bannerHit`. DC/NGC retain the
legacy FFSKY list. The viewer hard-codes no item names.
"""
import argparse
import re
from pathlib import Path
from banner_rules import banner_hit

from drop_data import (
    LANGUAGES,
    DROP_TYPES,
    VERSIONS,
    dump_framed_js,
    iter_data_drops,
    iter_cell_drops,
    load_framed_js,
    load_js_data,
)

# Canonical English names of SS-tier rare items. The ONLY place this list
# lives. Note: only 8 of the 10 section-ID cards are SS (Viridia and Whitill
# cards are intentionally excluded), matching the original game tier list.
SS_RARE_EN = frozenset({
    'Sealed J-Sword',
    "Madam's Parasol",
    'Yasha',
    "Nei's Claw",
    'Handgun: Guld',
    'Heaven Punisher',
    'Evil Curst',
    'Psycho Wand',
    'Prophets of Motav',
    'Greenill Card',
    'Skyly Card',
    'Bluefull Card',
    'Purplenum Card',
    'Pinkal Card',
    'Redria Card',
    'Oran Card',
    'Yellowboze Card',
})

# Known misspellings of SS items in the source data (NGC charts) that
# normalization alone can't reconcile. Listed here so the NGC pages still
# highlight them; fix upstream and these can be dropped.
SS_RARE_ALIASES = frozenset({
    'Bruefull Card',   # NGC source typo for 'Bluefull Card'
    'Greennill Card',  # NGC source typo for 'Greenill Card'
})


def _norm(name):
    """Language-independent, case/space-insensitive match key.

    Item names vary in case and spacing across versions (NGC uses ALL CAPS,
    'HANDGUN:GULD' drops the space), so fold case and strip whitespace before
    comparing against the canonical set.
    """
    return re.sub(r'\s+', '', name).lower()


_SS_NORM = frozenset(_norm(n) for n in SS_RARE_EN | SS_RARE_ALIASES)


def is_ss(name):
    return bool(name) and _norm(name) in _SS_NORM

ROOT = Path(__file__).parent.parent


def iter_drops(data):
    """Yield drops through the shared dataset traversal API."""
    yield from iter_data_drops(data)


def mark_version(version):
    en_path = ROOT / version / "data" / "en.js"
    if not en_path.exists():
        return None
    en_data = load_js_data(en_path, "en")
    # Per-coordinate presentation metadata, derived from English identities.
    flags = []
    for types in en_data["data"].values():
        for kind in DROP_TYPES:
            episodes = types.get(kind, {})
            for entries in episodes.values():
                for entry in entries:
                    for cell in entry["drops"]:
                        for drop in iter_cell_drops(cell):
                            name = drop.get("item", "")
                            hit = banner_hit(name, kind) if version == "bb" else None
                            ss = hit == 0 if version == "bb" else is_ss(name)
                            flags.append((ss, hit if hit else None))
    total = sum(ss or hit is not None for ss, hit in flags)

    for language in LANGUAGES:
        path = ROOT / version / "data" / f"{language}.js"
        if not path.exists():
            continue
        prefix, data, suffix = load_framed_js(path, language)
        drops = list(iter_drops(data))
        if len(drops) != len(flags):
            raise ValueError(
                f"{path}: structure drift vs en ({len(drops)} != {len(flags)})"
            )
        for drop, (ss, hit) in zip(drops, flags):
            if ss:
                drop["ss"] = True
            else:
                drop.pop("ss", None)  # idempotent: clear stale flags
            if hit is not None:
                drop["bannerHit"] = hit
            else:
                drop.pop("bannerHit", None)
        dump_framed_js(path, prefix, data, suffix)
    return total


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "versions",
        choices=VERSIONS,
        nargs="*",
        default=VERSIONS,
    )
    args = parser.parse_args()
    for version in args.versions:
        total = mark_version(version)
        if total is None:
            print(f"  {version}: skipped (no en.js)")
        else:
            print(f"  {version}: marked {total} highlighted drops across languages")


if __name__ == "__main__":
    main()
