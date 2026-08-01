#!/usr/bin/env python3
"""
Extract all unique item names from en.js data files (bb/dc/ngc)
and download their images from wiki.pioneer2.net.

Strategy:
  1. Normalize names: ALL CAPS -> Title Case, spaces -> underscores
  2. Batch-query wiki API for File:<name>.png existence (50 per request)
  3. For misses, retry with base name (strip parenthetical suffixes)
  4. Download found images to shared/images/

Usage:
    python tools/fetch_images.py
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error

from drop_data import iter_data_drops, load_js_data

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEST = os.path.join(ROOT, "shared", "images")
WIKI_API = "https://wiki.pioneer2.net/api.php"


def extract_items_from_js(path):
    """Read a *_en.js file and return all unique item names."""
    try:
        data = load_js_data(path, "en")
    except ValueError:
        print(f"  [WARN] Could not parse {path}")
        return set()
    return {
        drop["item"]
        for drop in iter_data_drops(data)
        if drop.get("item")
    }


def normalize_name(name):
    """Normalize item name to wiki-style Title Case."""
    # Skip Japanese-only names
    if re.fullmatch(r'[\u3000-\u9fff\uff00-\uffef()\[\]0-9\s]+', name):
        return None

    # ALL CAPS -> Title Case (DC/NGC style)
    if name == name.upper() and len(name) > 2:
        # Title case but keep small words lowercase after first word
        words = name.split()
        result = []
        for i, w in enumerate(words):
            if i == 0:
                result.append(w.capitalize())
            elif w.lower() in ('of', 'the', 'and', 'in', 'on', 'at', 'to', 'for', 'a', 'an'):
                result.append(w.lower())
            else:
                result.append(w.capitalize())
        return " ".join(result)

    return name


def base_name(name):
    """Strip parenthetical suffixes: 'Agito (1975)' -> 'Agito'"""
    return re.sub(r'\s*\(.*?\)\s*$', '', name).strip()


def wiki_filename(name):
    return name.replace(" ", "_") + ".png"


def batch_query_images(file_names):
    """Query wiki API for multiple File: pages. Returns {filename: url} for found ones."""
    titles = "|".join("File:" + fn for fn in file_names)
    params = urllib.parse.urlencode({
        "action": "query",
        "titles": titles,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json",
    })
    url = f"{WIKI_API}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "PSO-DropTable/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())

    results = {}
    for page in data.get("query", {}).get("pages", {}).values():
        if "imageinfo" in page and page.get("pageid"):
            # Extract original filename from title "File:XXX.png"
            title = page["title"]
            fname = title.replace("File:", "", 1).replace(" ", "_")
            img_url = page["imageinfo"][0]["url"]
            results[fname] = img_url
    return results


def download(url, out_path):
    req = urllib.request.Request(url, headers={"User-Agent": "PSO-DropTable/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
    with open(out_path, "wb") as f:
        f.write(data)


def main():
    # 1. Collect all unique items
    all_items = set()
    for version in ("bb", "dc", "ngc"):
        path = os.path.join(ROOT, version, "data", "en.js")
        if os.path.exists(path):
            items = extract_items_from_js(path)
            print(f"[{version}] {len(items)} unique items")
            all_items |= items

    print(f"\nTotal unique items: {len(all_items)}")

    # 2. Normalize names and build mapping: normalized_name -> [original_names]
    norm_map = {}  # normalized -> set of originals
    skipped_jp = 0
    for item in all_items:
        normed = normalize_name(item)
        if normed is None:
            skipped_jp += 1
            continue
        norm_map.setdefault(normed, set()).add(item)

    unique_normed = sorted(norm_map.keys())
    print(f"Normalized unique names: {len(unique_normed)} (skipped {skipped_jp} Japanese-only)")

    # 3. Batch query wiki for image existence
    os.makedirs(DEST, exist_ok=True)

    # Build filename list
    fnames = [wiki_filename(n) for n in unique_normed]

    print("\nPhase 1: Batch querying wiki API...")
    found = {}  # filename -> url
    batch_size = 50
    for i in range(0, len(fnames), batch_size):
        batch = fnames[i:i+batch_size]
        try:
            result = batch_query_images(batch)
            found.update(result)
            print(f"  Queried {min(i+batch_size, len(fnames))}/{len(fnames)} - found {len(result)} in this batch")
        except Exception as e:
            print(f"  [ERROR] Batch {i}-{i+batch_size}: {e}")
        time.sleep(0.5)

    print(f"\nPhase 1 result: {len(found)}/{len(fnames)} found")

    # 4. For misses, try base name (strip parenthetical)
    missed_fnames = set(fnames) - set(found.keys())
    retry_map = {}  # base_filename -> [original_filenames]
    for fn in missed_fnames:
        name = fn.replace("_", " ").rsplit(".png", 1)[0]
        bn = base_name(name)
        if bn != name:
            bfn = wiki_filename(bn)
            retry_map.setdefault(bfn, []).append(fn)

    if retry_map:
        print(f"\nPhase 2: Retrying {len(retry_map)} base names...")
        retry_fnames = sorted(retry_map.keys())
        for i in range(0, len(retry_fnames), batch_size):
            batch = retry_fnames[i:i+batch_size]
            try:
                result = batch_query_images(batch)
                for bfn, url in result.items():
                    # Map back to original filenames
                    for orig_fn in retry_map.get(bfn, []):
                        found[orig_fn] = url
                print(f"  Queried {min(i+batch_size, len(retry_fnames))}/{len(retry_fnames)} - found {len(result)}")
            except Exception as e:
                print(f"  [ERROR] Batch: {e}")
            time.sleep(0.5)

        print(f"Phase 2 result: {len(found)}/{len(fnames)} total found")

    # 5. Download all found images
    print(f"\nPhase 3: Downloading {len(found)} images...")
    ok, skip, fail = 0, 0, 0
    # Deduplicate URLs (variants sharing same image)
    url_to_fnames = {}
    for fn, url in found.items():
        url_to_fnames.setdefault(url, []).append(fn)

    downloaded_urls = set()
    for idx, (fn, url) in enumerate(sorted(found.items()), 1):
        out_path = os.path.join(DEST, fn)
        if os.path.exists(out_path):
            skip += 1
            continue
        try:
            # If another variant already downloaded the same URL, just copy
            if url in downloaded_urls:
                # Find the already-downloaded file
                for other_fn in url_to_fnames[url]:
                    other_path = os.path.join(DEST, other_fn)
                    if os.path.exists(other_path) and other_path != out_path:
                        import shutil
                        shutil.copy2(other_path, out_path)
                        break
                ok += 1
                continue

            download(url, out_path)
            downloaded_urls.add(url)
            ok += 1
            if ok % 50 == 0:
                print(f"  Downloaded {ok}...")
            time.sleep(0.2)
        except Exception as e:
            fail += 1
            print(f"  [FAIL] {fn}: {e}")

    print(f"\nDone: {ok} downloaded, {skip} cached, {fail} failed")

    # 6. Report final misses
    final_missing = set(fnames) - set(found.keys())
    if final_missing:
        print(f"\nMissing {len(final_missing)} images:")
        miss_path = os.path.join(DEST, "_missing.txt")
        with open(miss_path, "w", encoding="utf-8") as f:
            for fn in sorted(final_missing):
                name = fn.replace("_", " ").rsplit(".png", 1)[0]
                originals = norm_map.get(name, {name})
                line = f"{fn}\t(originals: {', '.join(sorted(originals))})"
                print(f"  {line}")
                f.write(line + "\n")
        print(f"\nMissing list saved to {miss_path}")

    # 7. Write name -> filename mapping for viewer.js
    mapping = {}
    for normed, originals in norm_map.items():
        fn = wiki_filename(normed)
        if fn in found:
            for orig in originals:
                mapping[orig] = fn

    # 7b. "Heart of XXX" -> use XXX's image
    heart_added = 0
    for normed, originals in norm_map.items():
        for orig in originals:
            if orig in mapping:
                continue
            # Match "Heart of XXX" pattern
            m = re.match(r'^Heart of (.+)$', orig, re.IGNORECASE)
            if not m:
                continue
            weapon_name = m.group(1)
            # Look up weapon in existing mapping
            if weapon_name in mapping:
                mapping[orig] = mapping[weapon_name]
                heart_added += 1
            else:
                # Try normalized version
                weapon_normed = normalize_name(weapon_name)
                if weapon_normed:
                    weapon_fn = wiki_filename(weapon_normed)
                    if weapon_fn in found:
                        mapping[orig] = weapon_fn
                        heart_added += 1

    print(f"\nHeart of -> weapon mappings added: {heart_added}")

    map_path = os.path.join(DEST, "mapping.json")
    with open(map_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"Mapping ({len(mapping)} items) saved to {map_path}")


if __name__ == "__main__":
    main()
