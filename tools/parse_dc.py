#!/usr/bin/env python3
"""Parse DC drop chart HTML files into data/en.js format."""

from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from drop_data import make_drop_cell, write_generated_js
from source_html import read_legacy_html

OUT_DIR = Path(__file__).parent.parent / "dc" / "data"

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


def parse_dc_cell(td):
    """Parse every item/rate pair from one DC section-ID cell."""
    text = td.get_text(separator="\n", strip=True)
    if not text or text == "-----":
        return {"item": "", "rate": ""}

    lines = [
        line.strip()
        for line in text.split("\n")
        if line.strip() and line.strip() != "-----"
    ]
    drops = []
    pending_item = ""
    for line in lines:
        if line.endswith("%") and pending_item:
            drops.append({"item": pending_item, "rate": line})
            pending_item = ""
        else:
            if pending_item:
                drops.append({"item": pending_item, "rate": ""})
            pending_item = line
    if pending_item:
        drops.append({"item": pending_item, "rate": ""})
    return make_drop_cell(drops)


def parse_dc_html(html):
    """Parse a DC drop chart HTML document."""
    soup = BeautifulSoup(html, "html.parser")
    table = soup.find("table")
    if not table:
        return {"monsters": {}, "boxes": {}}

    rows = table.find_all("tr")
    entries = []

    for row in rows[2:]:  # Skip header rows
        cells = row.find_all(["th", "td"])
        if len(cells) < 11:
            continue

        # First cell (th) is monster name with drop rate
        name_cell = cells[0]
        name_text = name_cell.get_text(separator="\n", strip=True)
        name_parts = name_text.split("\n")
        name = name_parts[0].strip()
        drop_rate = name_parts[1].strip() if len(name_parts) > 1 else ""

        if not name:
            continue

        # Cells 1-10 are drops for each section ID
        drops = []
        for i in range(1, min(len(cells) - 1, 11)):  # -1 to skip last th
            cell = cells[i]
            if cell.name == "th":
                continue
            drops.append(parse_dc_cell(cell))

        while len(drops) < 10:
            drops.append({"item": "", "rate": ""})

        entry = {"name": name, "drops": drops[:10]}
        if drop_rate:
            entry["dropRate"] = drop_rate
        entries.append(entry)

    return {"monsters": {"Episode 1": entries}, "boxes": {}}


def parse_dc_page(html_path):
    """Parse a DC drop chart page from a filesystem path."""
    return parse_dc_html(html_path.read_text(encoding="utf-8"))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    all_data = {}

    for filename, label in DIFFICULTIES:
        print(f"Parsing DC {label} ({filename})...")
        html = read_legacy_html("dc", filename)
        parsed = parse_dc_html(html)
        m_count = sum(len(v) for v in parsed["monsters"].values())
        print(f"  {m_count} monsters")
        all_data[label] = parsed

    data_obj = {
        "sectionIds": SECTION_IDS,
        "sectionColors": SECTION_COLORS,
        "data": all_data,
    }

    out_path = OUT_DIR / "en.js"
    size = write_generated_js(
        out_path,
        data_obj,
        language="en",
        generator=f"parse_dc.py on {datetime.now().isoformat()}",
        source="Source: DC drop charts",
    )
    print(f"Generated {out_path} ({size / 1024:.1f} KB)")


if __name__ == "__main__":
    main()
