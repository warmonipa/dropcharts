#!/usr/bin/env python3
"""Mark SS-tier (FFSKY) rare drops in the generated data files.

Single source of truth for which items are SS rare. Runs as the final
pipeline step, after all language data files exist.

Rarity is a property of the *item*, not of its localized name, so the
canonical English name is the language-independent key. For each version
the English file decides which (difficulty, type, episode, entry, drop)
coordinates are SS; that flag is then stamped onto the en/ja/zh files in
lockstep (their structures are parallel by construction).

Result: every SS drop in every language file gains `"ss": true`. The
viewer reads `drop.ss` directly and hard-codes no item names.
"""
import argparse
import re
from pathlib import Path

from drop_data import (
    LANGUAGES,
    VERSIONS,
    dump_framed_js,
    iter_data_drops,
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
    # Per-coordinate SS verdict, derived once from the English names.
    flags = [is_ss(drop.get("item", "")) for drop in iter_drops(en_data)]
    total = sum(flags)

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
        for drop, ss in zip(drops, flags):
            if ss:
                drop["ss"] = True
            else:
                drop.pop("ss", None)  # idempotent: clear stale flags
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
            print(f"  {version}: marked {total} SS drops across languages")


if __name__ == "__main__":
    main()
