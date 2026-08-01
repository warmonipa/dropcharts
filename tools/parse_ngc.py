#!/usr/bin/env python3
"""Parse NGC drop chart HTML files into data/en.js format."""

import re
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from drop_data import make_drop_cell, write_generated_js
from source_html import read_legacy_html

OUT_DIR = Path(__file__).parent.parent / "ngc" / "data"

DIFFICULTIES = [
    ("n.html", "Normal"),
    ("h.html", "Hard"),
    ("vh.html", "Very Hard"),
    ("u.html", "Ultimate"),
]

SECTION_IDS = [
    "Viridia", "Greenill", "Skyly", "Bluefull", "Purplenum",
    "Pinkal", "Redria", "Oran", "Yellowboze", "Whitill",
]
SECTION_COLORS = [
    "#00A562", "#76FE43", "#59F9F9", "#4488FF", "#CC00FF",
    "#FF87CB", "#F70F0F", "#F7830F", "#F7F715", "#FFFFFF",
]

# Area to episode mapping
AREA_EP_MAP = {
    "森": "Episode 1", "洞窟": "Episode 1", "坑道": "Episode 1", "遺跡": "Episode 1",
    "神殿": "Episode 2", "宇宙船": "Episode 2", "管理区": "Episode 2",
    "プラント": "Episode 2", "制御塔": "Episode 2",
}


def extract_en_name(td):
    """Extract English item name from NGC cell.
    Format: <nobr>Japanese</nobr><br>ENGLISH NAME<br>
    """
    text = td.get_text(separator="\n", strip=True)
    if not text:
        return ""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    if len(lines) >= 2:
        return lines[1]  # English name is second line
    return lines[0] if lines else ""


def extract_ja_name(td):
    """Extract Japanese item name from NGC cell."""
    nobr = td.find("nobr")
    if nobr:
        return nobr.get_text(strip=True)
    text = td.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    return lines[0] if lines else ""


def extract_rate(td):
    """Extract rate from NGC percentage cell.
    Format: '1.5625%(0.46875%)' or '0.042724609375% (0.011962890625%)'
    Returns first percentage.
    """
    text = td.get_text(separator=" ", strip=True)
    if not text:
        return ""
    # Match first percentage value
    m = re.match(r"([\d.]+%)", text)
    return m.group(1) if m else text.split()[0] if text else ""


def parse_ngc_html(html, lang="en"):
    """Parse a NGC drop chart HTML document.

    NGC layout: 13 columns
    Enemy | VIRIDIA..PURPLENUM | Enemy | PINKAL..WHITILL | Enemy
    Each monster = 2 rows: item row + rate row
    """
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table", class_="itemtable")
    if not table:
        return {"monsters": {}, "boxes": {}}

    rows = table.find_all("tr")
    result = {}
    current_ep = "Episode 1"
    name_func = extract_ja_name if lang == "ja" else extract_en_name

    i = 1  # Skip header row
    while i < len(rows) - 1:
        row = rows[i]
        cells = row.find_all(["th", "td"])

        # Check for spacer row
        if any("spacer" in (c.get("class") or []) for c in cells):
            i += 1
            continue

        # Check if this is a monster row (has normal/rare/boss class in first th)
        first = cells[0] if cells else None
        if not first or first.name != "th":
            i += 1
            continue

        first_cls = first.get("class") or []
        if not any(c in first_cls for c in ["normal", "rare", "boss"]):
            i += 1
            continue

        if len(cells) < 13:
            i += 1
            continue

        # Parse monster name and drop rate
        name_text = first.get_text(separator="\n", strip=True)
        name_parts = name_text.split("\n")
        name = name_parts[0].strip()
        drop_rate = ""
        for p in name_parts[1:]:
            m = re.search(r"\((\d+%)\)", p)
            if m:
                drop_rate = m.group(1)
                break

        if not name:
            i += 1
            continue

        # Extract items from 10 section ID columns
        # Columns: [0]=Enemy, [1-5]=VIRIDIA..PURPLENUM, [6]=Enemy, [7-11]=PINKAL..WHITILL, [12]=Enemy
        item_cells = [cells[j] for j in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]

        # Next row should be the rate row
        rate_row = rows[i + 1] if i + 1 < len(rows) else None
        rate_cells_data = []
        if rate_row:
            rcells = rate_row.find_all(["th", "td"])
            if len(rcells) >= 13:
                rate_cells_data = [rcells[j] for j in [1, 2, 3, 4, 5, 7, 8, 9, 10, 11]]
                # Detect episode from area th
                area_th = rcells[0]
                area_cls = area_th.get("class") or []
                area_text = area_th.get_text(strip=True)
                if area_text in AREA_EP_MAP:
                    current_ep = AREA_EP_MAP[area_text]
                elif any(c.startswith("ep") for c in area_cls):
                    ep_num = next((c for c in area_cls if c.startswith("ep")), "ep1")
                    current_ep = f"Episode {ep_num[2:]}"

        drops = []
        for idx, ic in enumerate(item_cells):
            item = name_func(ic)
            if item in ("未定義", "undefined", "-----"):
                item = ""
            rate = ""
            if idx < len(rate_cells_data):
                rate = extract_rate(rate_cells_data[idx])
            drops.append(make_drop_cell([{"item": item, "rate": rate}]))

        while len(drops) < 10:
            drops.append({"item": "", "rate": ""})

        entry = {"name": name, "drops": drops[:10]}
        if drop_rate:
            entry["dropRate"] = drop_rate

        if current_ep not in result:
            result[current_ep] = []
        result[current_ep].append(entry)

        i += 2  # Skip rate row
        continue

    return {"monsters": result, "boxes": {}}


def parse_ngc_page(html_path, lang="en"):
    """Parse a NGC drop chart page from a filesystem path."""
    return parse_ngc_html(html_path.read_text(encoding="utf-8"), lang=lang)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for lang_code, name_label in [("en", "English"), ("ja", "Japanese")]:
        all_data = {}
        for filename, label in DIFFICULTIES:
            print(f"Parsing NGC {label} ({filename}) [{lang_code}]...")
            html = read_legacy_html("ngc", filename)
            parsed = parse_ngc_html(html, lang=lang_code)
            m_count = sum(len(v) for v in parsed["monsters"].values())
            print(f"  {m_count} monsters")
            all_data[label] = parsed

        data_obj = {
            "sectionIds": SECTION_IDS,
            "sectionColors": SECTION_COLORS,
            "data": all_data,
        }

        out_path = OUT_DIR / f"{lang_code}.js"
        size = write_generated_js(
            out_path,
            data_obj,
            language=lang_code,
            generator=f"parse_ngc.py on {datetime.now().isoformat()}",
            source=f"Source: NGC drop charts ({name_label})",
        )
        print(f"Generated {out_path} ({size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
