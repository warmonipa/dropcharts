#!/usr/bin/env python3
"""Build the static PSO Drop Charts site for GitHub Pages."""

import os
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "_site"
SOURCE_DIRECTORIES = ("shared", "bb", "dc", "ngc")
ROOT_FILES = ("index.html", "CNAME")


def build_site(output_dir: Path, *, asset_version: str) -> int:
    """Build the complete static site and return the number of output files.

    Args:
        output_dir: Directory that will contain the generated site.
        asset_version: Cache-busting value inserted into HTML asset URLs.

    Raises:
        ValueError: If the output directory resolves to the repository root.
    """
    output_dir = output_dir.resolve()
    if output_dir == ROOT:
        raise ValueError("The output directory cannot be the repository root")

    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(parents=True)

    for directory in SOURCE_DIRECTORIES:
        shutil.copytree(ROOT / directory, output_dir / directory)
    for filename in ROOT_FILES:
        shutil.copy2(ROOT / filename, output_dir / filename)

    for html_file in output_dir.rglob("*.html"):
        source = html_file.read_text(encoding="utf-8")
        rendered = source.replace("__ASSET_VERSION__", asset_version)
        html_file.write_text(rendered, encoding="utf-8")

    return sum(path.is_file() for path in output_dir.rglob("*"))


def main() -> None:
    """Build `_site` with a reproducible or UTC timestamp asset version."""
    asset_version = os.environ.get("DROPTABLE_ASSET_VERSION")
    if not asset_version:
        asset_version = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")

    file_count = build_site(OUTPUT_DIR, asset_version=asset_version)
    print(f"Built {file_count} files in {OUTPUT_DIR}")
    print(f"Asset version: {asset_version}")


if __name__ == "__main__":
    main()
