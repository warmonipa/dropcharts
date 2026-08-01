#!/usr/bin/env python3
"""Reorder BB monster entries into a canonical trash -> elite -> boss order.

BB drop data is scraped from the Ephinea website in the site's own row
order, which differs from the DC/NGC charts (laid out trash -> elite ->
boss, grouped by area). This post-processing step reorders BB's monster
arrays into one canonical order so the three versions read consistently.
Run it after scraper.py -- re-scraping would otherwise restore the site
order. Only BB is touched; DC/NGC already follow the desired order at
source.

The canonical order is defined per episode below, keyed on the monster's
English name (the part before '/' in BB's combined "Normal/Ultimate"
name). Episode 1/2 follow the DC/NGC order; Episode 4's Crater segment
mirrors the Episode 1 Forest progression (it is a reskin), with the
Subterranean Desert and bosses kept as-is.

ja.js / zh.js entry names are localized, so they can't be keyed by English
name directly. Instead the index permutation is computed once from en.js
and applied identically to all three language files, keeping their arrays
parallel (the viewer relies on en/ja/zh being positionally aligned). The
order is the same across all four difficulties, but each difficulty is
reordered independently from its own en data for safety. Boxes are left
untouched.
"""
from pathlib import Path

from drop_data import LANGUAGES, dump_framed_js, load_framed_js

# Canonical monster order per episode, by English (pre-'/') name.
# The ONLY place this order lives. If Ephinea adds a monster, this list
# must be updated -- the script warns and parks unknown monsters at the
# end rather than dropping them.
ORDER = {
    "Episode 1": [
        "Booma", "Gobooma", "Gigobooma", "Rag Rappy",
        "Al Rappy", "Mothmant", "Monest", "Savage Wolf",
        "Barbarous Wolf", "Hildebear", "Hildeblue", "Dragon",
        "Evil Shark", "Pal Shark", "Guil Shark", "Poison Lily",
        "Nar Lily", "Grass Assassin", "Nano Dragon", "Pofuilly Slime",
        "Pouilly Slime", "Pan Arms", "Migium", "Hidoom",
        "De Rol Le", "Gilchic", "Dubchic", "Canadine",
        "Canane", "Sinow Beat", "Sinow Gold", "Garanz",
        "Vol Opt", "Dimenian", "La Dimenian", "So Dimenian",
        "Delsaber", "Claw", "Bulk", "Bulclaw",
        "Dark Belra", "Dark Gunner", "Death Gunner", "Chaos Sorcerer",
        "Chaos Bringer", "Dark Falz",
    ],
    "Episode 2": [
        "Dimenian", "La Dimenian", "So Dimenian", "Rag Rappy",
        "Love Rappy", "Egg Rappy", "Halo Rappy", "St. Rappy",
        "Hildebear", "Hildeblue", "Mothmant", "Monest",
        "Grass Assassin", "Poison Lily", "Nar Lily", "Dark Belra",
        "Barba Ray", "Dubchic", "Gilchic", "Recon",
        "Savage Wolf", "Barbarous Wolf", "Pan Arms", "Migium",
        "Hidoom", "Garanz", "Delsaber", "Chaos Sorcerer",
        "Gol Dragon", "Ul Gibbon", "Zol Gibbon", "Merillia",
        "Meriltas", "Gee", "Sinow Berill", "Sinow Spigell",
        "Mericarol", "Merikle", "Mericus", "Gibbles",
        "Gi Gue", "Gal Gryphon", "Dolmolm", "Dolmdarl",
        "Morfos", "Sinow Zoa", "Sinow Zele", "Deldepth",
        "Delbiter", "Olga Flow", "Ill Gill", "Del Lily",
        "Epsilon",
    ],
    "Episode 4": [
        # Crater -- mirrors Ep1 Forest reskin (Boota=Booma, Sand Rappy=Rag
        # Rappy, Satellite Lizard=Savage Wolf, Dorphon=Hildebear), with the
        # Crater-only Zu/Pazuzu/Astark placed before the Dorphon pair.
        "Boota", "Ze Boota", "Ba Boota", "Sand Rappy",
        "Del Rappy", "Satellite Lizard", "Yowie", "Zu",
        "Pazuzu", "Astark", "Dorphon", "Dorphon Eclair",
        # Subterranean Desert + bosses (kept as scraped)
        "Goran", "Pyro Goran", "Goran Detonator", "Merissa A",
        "Merissa AA", "Girtablulu", "Saint Million", "Shambertin",
        "Kondrieu",
    ],
}

ROOT = Path(__file__).parent.parent


def _prekey(name):
    return name.split("/")[0].strip().lower()


def permutation(en_entries, episode):
    """Indices that reorder en_entries into ORDER[episode].

    Unknown monsters (not in ORDER) keep their original relative order and
    are parked at the end. Returns (perm, unknown_names).
    """
    rank = {name.lower(): i for i, name in enumerate(ORDER[episode])}
    end = len(rank)
    unknown = []
    for e in en_entries:
        if _prekey(e["name"]) not in rank:
            unknown.append(e["name"])
    perm = sorted(
        range(len(en_entries)),
        key=lambda i: (rank.get(_prekey(en_entries[i]["name"]), end), i),
    )
    return perm, unknown


def reorder_bb():
    paths = {
        language: ROOT / "bb" / "data" / f"{language}.js"
        for language in LANGUAGES
    }
    if not paths["en"].exists():
        print("  bb: skipped (no en.js)")
        return
    loaded = {
        language: load_framed_js(path, language)
        for language, path in paths.items()
        if path.exists()
    }
    en_data = loaded["en"][1]

    total_moved = 0
    for diff, types in en_data["data"].items():
        monsters = types.get("monsters", {})
        for ep, en_entries in monsters.items():
            if ep not in ORDER:
                print(f"  bb: WARNING unknown episode {ep!r}, left as-is")
                continue
            perm, unknown = permutation(en_entries, ep)
            if unknown:
                print(f"  bb: WARNING {diff}/{ep} monsters not in ORDER "
                      f"(parked at end): {sorted(set(unknown))}")
            if perm != list(range(len(perm))):
                total_moved += 1
            for lang, (_, data, _) in loaded.items():
                arr = data["data"][diff]["monsters"][ep]
                data["data"][diff]["monsters"][ep] = [arr[i] for i in perm]

    for language, (prefix, data, suffix) in loaded.items():
        dump_framed_js(paths[language], prefix, data, suffix)
    print(f"  bb: reordered monster lists ({total_moved} diff/episode arrays "
          f"changed) across {len(loaded)} languages")


def main():
    reorder_bb()


if __name__ == "__main__":
    main()
