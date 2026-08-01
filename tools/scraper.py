#!/usr/bin/env python3
"""
Ephinea PSOBB Drop Chart Scraper (i18n)

Fetches drop chart data in multiple languages and generates:
  data/en.js  — English game data
  data/ja.js  — Japanese game data

Usage: python scraper.py
"""

import argparse
import re
from datetime import datetime
from itertools import zip_longest
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from drop_data import load_js_data, make_drop_cell, write_generated_js

# Language configs: (lang_code, base_url, difficulty_slugs)
LANGUAGES = {
    "en": {
        "base_url": "https://ephinea.pioneer2.net/drop-charts",
        "difficulties": [
            ("normal", "Normal"),
            ("hard", "Hard"),
            ("very-hard", "Very Hard"),
            ("ultimate", "Ultimate"),
        ],
    },
    "ja": {
        "base_url": "https://ephinea.pioneer2.net/drop-charts-japanese",
        "difficulties": [
            ("normal-j", "Normal"),
            ("hard-j", "Hard"),
            ("very-hard-j", "Very Hard"),
            ("ultimate-j", "Ultimate"),
        ],
    },
}

SECTION_IDS = [
    "Viridia", "Greenill", "Skyly", "Bluefull", "Purplenum",
    "Pinkal", "Redria", "Oran", "Yellowboze", "Whitill",
]
SECTION_COLORS = [
    "#00A562", "#76FE43", "#59F9F9", "#4488FF", "#CC00FF",
    "#FF87CB", "#F70F0F", "#F7830F", "#F7F715", "#FFFFFF",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def parse_drop_cell(td):
    """Parse every item and rate from one section-ID table cell."""
    item_tags = td.find_all("b")
    sup_tags = td.find_all("sup")
    sub_tags = td.find_all("sub")
    rates = [
        f"{sup.get_text(strip=True)}/{sub.get_text(strip=True)}"
        for sup, sub in zip(sup_tags, sub_tags)
    ]
    parsed = [
        {
            "item": item_tag.get_text(strip=True),
            "rate": rate,
        }
        for item_tag, rate in zip_longest(item_tags, rates, fillvalue="")
        if item_tag
    ]

    if not parsed:
        text = td.get_text(strip=True)
        if text and text != "\xa0" and text != "&nbsp;":
            parsed.append({"item": text, "rate": ""})

    return make_drop_cell(parsed)


def parse_monster_name(td):
    """Extract monster name from first column."""
    u_tag = td.find("u")
    if u_tag:
        for br in u_tag.find_all("br"):
            br.replace_with("/")
        name = u_tag.get_text(strip=True)
        name = re.sub(r"/+", "/", name)
        return name

    text = td.get_text(strip=True)
    return text if text and text != "\xa0" else ""


def parse_entry_drop_rate(td):
    """Extract the language-independent overall drop rate from a cell."""
    abbr = td.find("abbr")
    if not abbr:
        return ""
    title = abbr.get("title", "")
    match = re.search(
        r"(?:Drop Rate|ドロップ率):\s*(1/[\d.]+)",
        title,
    )
    return match.group(1) if match else ""


def parse_page(html):
    """Parse a drop chart page and extract all data."""
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table", class_="dropcharttbl")

    result = {"monsters": {}, "boxes": {}}

    for table in tables:
        rows = table.find_all("tr")
        if not rows:
            continue

        header_td = rows[0].find("td", colspan=True)
        if not header_td:
            continue

        header_text = header_td.get_text(strip=True).upper()

        episode = None
        # Normalize: remove spaces, uppercase
        ht = header_text.replace(" ", "").replace("\u3000", "")
        if "EPISODE1" in ht or "エピソード1" in ht:
            episode = "Episode 1"
        elif "EPISODE2" in ht or "エピソード2" in ht:
            episode = "Episode 2"
        elif "EPISODE4" in ht or "エピソード4" in ht:
            episode = "Episode 4"

        if not episode:
            continue

        anchor = table.find_previous("a", attrs={"name": True})
        if anchor:
            anchor_name = anchor.get("name", "")
            if "mob" in anchor_name:
                is_box = False
            elif "box" in anchor_name:
                is_box = True
            else:
                is_box = tables.index(table) >= 3
        else:
            is_box = tables.index(table) >= 3

        target = result["boxes"] if is_box else result["monsters"]
        if episode not in target:
            target[episode] = []

        for row in rows[2:]:
            cells = row.find_all("td")
            if len(cells) < 2:
                continue

            name = parse_monster_name(cells[0])
            if not name:
                continue

            drops = []
            drop_rate = ""
            for i in range(1, min(len(cells), 11)):
                drops.append(parse_drop_cell(cells[i]))
                if not drop_rate:
                    drop_rate = parse_entry_drop_rate(cells[i])

            while len(drops) < 10:
                drops.append({"item": "", "rate": ""})

            entry = {"name": name, "drops": drops[:10]}
            if drop_rate:
                entry["dropRate"] = drop_rate
            target[episode].append(entry)

    return result


def fetch_page(url):
    """Fetch a page."""
    print(f"  Fetching {url}...")
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    return resp.text


def scrape_language(lang_code, lang_config):
    """Scrape all difficulties for one language."""
    base_url = lang_config["base_url"]
    all_data = {}

    for slug, label in lang_config["difficulties"]:
        url = f"{base_url}/{slug}/"
        print(f"\n  [{label}]")
        try:
            html = fetch_page(url)
            print(f"    Received {len(html)} bytes")

            parsed = parse_page(html)

            m_count = sum(len(v) for v in parsed["monsters"].values())
            b_count = sum(len(v) for v in parsed["boxes"].values())
            print(f"    Parsed: {m_count} monsters, {b_count} boxes")

            all_data[label] = parsed
        except Exception as e:
            print(f"    ERROR: {e}")
            all_data[label] = {
                "monsters": {"Episode 1": [], "Episode 2": [], "Episode 4": []},
                "boxes": {},
            }

    return all_data


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
    output_dir = Path(__file__).parent.parent / "bb" / "data"
    output_dir.mkdir(exist_ok=True)

    for lang_code, lang_config in LANGUAGES.items():
        print(f"\n{'='*40}")
        print(f"  Language: {lang_code.upper()}")
        print(f"{'='*40}")

        all_data = scrape_language(lang_code, lang_config)

        out_path = output_dir / f"{lang_code}.js"
        if args.boxes_only:
            data_obj = load_js_data(out_path, lang_code)
            for difficulty, parsed in all_data.items():
                data_obj["data"][difficulty]["boxes"] = parsed["boxes"]
        else:
            data_obj = {
                "sectionIds": SECTION_IDS,
                "sectionColors": SECTION_COLORS,
                "data": all_data,
            }

        size = write_generated_js(
            out_path,
            data_obj,
            language=lang_code,
            generator=f"scraper.py on {datetime.now().isoformat()}",
            source=f"Language: {lang_code}",
        )
        print(f"\n  Generated {out_path.name} ({size / 1024:.1f} KB)")

    print("\nDone!")


if __name__ == "__main__":
    main()
