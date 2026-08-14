# Data Update and Deployment Guide

This guide describes how to refresh, rebuild, validate, and deploy the drop-table data.

## Prerequisites

- Python 3.10 or later and `uv`; Python dependencies are managed by `pyproject.toml` and `uv.lock`.
- A local checkout of the `ephinea4haven.github.io` source-data repository next to this repository. The DC and NGC source HTML is no longer stored in this working tree. The parsers read it from verified commit `7280fec3e435bf06b2d0a25659478ef5375eb86c`. Set `EPHINEA4HAVEN_REPO` to use another checkout.
- A local checkout of `psobb-localization` next to this repository. Its aligned
  English reference and unified Chinese mixed-width Unitxt align the Chinese
  names in the sole authority, `i18n_names.json`. Set
  `PSOBB_LOCALIZATION_REPO` when the checkout is elsewhere.

## Quick start

```bash
# Refresh BB, DC, NGC, and localization data.
npm run update

# Build a local Pages artifact after validation succeeds.
npm run build
```

## Targeted updates

```bash
npm run update:bb      # Refresh BB, then align, mark SS drops, and validate.
npm run update:dc      # Refresh and localize DC, then align, mark, and validate.
npm run update:ngc     # Refresh and localize NGC, then align, mark, and validate.
npm run update:i18n    # Rebuild DC/NGC localizations and derived data.
npm run update:reorder # Reorder BB, then realign, mark, and validate.
npm run update:ss      # Realign, rebuild SS markers, and validate.
```

The pipeline can also be invoked directly:

```bash
./tools/update.sh [all|bb|dc|ngc|i18n|reorder|align|ss]
```

## Data pipeline

### 1. BB (Blue Burst)

| Script | Input | Output |
| --- | --- | --- |
| `scraper.py` | Live Ephinea Drop Charts | `bb/data/en.js`, `bb/data/ja.js` |
| `gen_zh.py` | `psobb-localization/localization/{en,zh}/unitxt_j.prs` | `bb/data/zh.js` |
| `reorder.py` | All BB language datasets | The same files, with monsters in canonical order |

- `scraper.py` requires network access to `ephinea.pioneer2.net`.
- `gen_zh.py` requires psobb-localization's aligned English and unified Chinese
  Unitxt files. It preserves the source's mixed widths, maps
  Ephinea chart aliases back to canonical Unitxt indexes, and fails rather than
  silently using a stale translation fallback. Use `--localization-repo` or
  `PSOBB_LOCALIZATION_REPO` to select a non-sibling checkout.
- BB publishes one Chinese dataset from that unified mixed-width source; the viewer does
  not generate or select separate full-width and half-width variants.
- `reorder.py` runs automatically at the end of `update:bb`. It orders BB enemies as common enemies, elite enemies, then bosses within each area, matching DC and NGC.

Every version and every monster or area/box row uses one cell protocol. Each `drops` array always corresponds to the ten Section ID columns. An empty or single-drop cell has the form `{"item": "...", "rate": "..."}`. A cell with several independent drops uses `{"items": [{"item": "...", "rate": "..."}, ...]}`. Consumers must iterate through `tools/drop_data.py` in Python or `cellDrops()` in the viewer instead of assuming a cell cardinality from the `monsters` or `boxes` type. Multi-drop cells currently occur in BB area boxes, but the model also supports future multi-drop monster cells.

### 2. DC (Dreamcast)

| Script | Input | Output |
| --- | --- | --- |
| `parse_dc.py` | `dc/*.html` from the local `ephinea4haven` repository | `dc/data/en.js` |

### 3. NGC (GameCube)

| Script | Input | Output |
| --- | --- | --- |
| `parse_ngc.py` | `ngc/*.html` from the local `ephinea4haven` repository | `ngc/data/en.js`, `ngc/data/ja.js` |

### 4. Localization rebuild

| Script | Input | Output |
| --- | --- | --- |
| `build_i18n.py` | `i18n_names.json`, BB/NGC datasets, and aligned Unitxt | Updated authority plus `dc/data/ja.js`, `dc/data/zh.js`, `ngc/data/zh.js` |

`i18n_names.json` is the sole name authority. The rebuild preserves entries
outside Unitxt, fills missing Japanese metadata from platform datasets, and
replaces every matching Chinese name with the exact mixed-width Unitxt value.
Localization depends on the BB and NGC datasets, so update those inputs first.
A full update enforces the correct order automatically.

BB monster rows encode standard and Ultimate names as the first and second parts of a
compound label. When both parts share one English name but have different translations,
`build_i18n.py` uses the second, Ultimate translation in its flat cross-version mapping.
This preserves the Ultimate-tier names expected by the DC and NGC derived datasets.

### 5. BB monster ordering

| Script | Input | Output |
| --- | --- | --- |
| `reorder.py` | `bb/data/*.js` in all languages | The same files in canonical monster order |

- Ephinea's source pages use their own monster order. `reorder.py` rearranges each area into common enemies, elite enemies, then bosses, matching DC and NGC.
- `ORDER` in `reorder.py` is the canonical definition. Episodes 1 and 2 follow DC/NGC, while Episode 4's Crater grouping mirrors Episode 1's Forest structure. Only BB is reordered because DC and NGC already arrive in canonical order.
- The permutation is calculated from English data and applied identically to English, Japanese, and Chinese. Unknown monsters produce a warning and remain at the end so no data is discarded.
- This step runs automatically at the end of `update:bb`.

### 6. SS rarity markers

| Script | Input | Output |
| --- | --- | --- |
| `mark_ss.py` | Every `*/data/*.js` language dataset | The same files with `"ss": true` on SS-rarity drops |

- The canonical English item list in `mark_ss.py` is the single source of truth for SS rarity.
- English names act as language-independent keys, allowing markers to be copied by coordinate to the English, Japanese, and Chinese datasets.
- The viewer reads only `drop.ss` and does not hard-code item names.
- The operation is idempotent: repeated runs add or remove only SS markers. Run it after all data and localization files have been generated.

### 7. Cross-language coordinate alignment

```bash
npm run update:align
python3 tools/validate_alignment.py
```

`sync_coordinates.py` treats each version's English dataset as the language-independent coordinate source. It synchronizes row drop rates, per-cell probabilities, and SS markers. If a translation is missing, it preserves the English item name rather than replacing a valid coordinate with an empty value.

`validate_alignment.py` verifies that BB, DC, and NGC have matching difficulties, types, episodes, row counts, ten Section ID columns, cell entry counts, probabilities, empty/nonempty states, and SS markers across English, Japanese, and Chinese.

Do not add parallel supplemental translation files. Add uncovered names to
`i18n_names.json`; subsequent rebuilds retain them and Unitxt wins wherever an
aligned English identity exists.

## Execution order

Full and targeted updates follow the same lifecycle:

```text
source -> parse -> localize -> align -> mark SS -> validate
```

A full update ingests BB, DC, and NGC first, then runs localization, alignment, SS marking, and validation. Each targeted `update:bb`, `update:dc`, or `update:ngc` command also completes all downstream stages for that version. A successful command therefore leaves deployable output without stale translations or missing SS markers.

## Verification

```bash
npm test
```

The suite covers generated data, cross-language coordinates, multi-drop cells, legacy
parsers, build output, and the responsive viewer contract. The layout regression tests
require exactly one monster/location column, verify that its header and cells are frozen,
ensure area labels derive their horizontal position from the visible scroll container, and
verify that mixed-width search normalizes both names and queries.

When changing table layout or responsive breakpoints, also inspect a production build at a
phone-sized viewport and scroll a table horizontally. The frozen label and area heading must
remain stationary while the Section ID cells move.

## Deployment

```bash
# Validate first if no update command has already performed validation.
npm test

npm run build
```

Pushes to `master` are verified and published by GitHub Actions. The production entry point is `https://dropcharts.psohaven.com/`, configured through the repository's `CNAME` file and GitHub Pages settings.

The build command completely replaces the repository's ignored `_site` directory. This guarantees that the viewer, styles, localization code, and all three platform datasets come from the same source revision.

```bash
npm run build
```

Each deployment creates a UTC asset version and replaces every `__ASSET_VERSION__` placeholder in HTML with that value. CSS, viewer, localization, and English/Japanese/Chinese dataset URLs therefore share one version, such as `viewer.js?v=20260718072112`, preventing browser or CDN caches from combining new data with an old viewer.

Set an explicit asset version for reproducible builds:

```bash
DROPTABLE_ASSET_VERSION=20260718.2 npm run build
```

`npm run build` only writes `_site`. GitHub Pages deployment is triggered by pushing a verified source commit to `master`; generated files are not committed.

The former `https://www.psohaven.com/data/droptable/` deployment and legacy `/droptable/{cn,en}/*.html` URLs remain compatibility entry points in the main-site repository. Maintain their redirects when changing routes; external sites still link to those historical URLs. Do not publish Drop Charts artifacts into the main-site repository.

After publishing, verify at least the following:

1. The latest GitHub Pages build corresponds to the pushed `master` commit and completed successfully.
2. `https://dropcharts.psohaven.com/` references the deployment's single asset version.
3. BB Ultimate Episode 4 box cells display every independent drop in the cell.
4. Historical `/droptable/{cn,en}/*.html` URLs redirect to the equivalent chart state.

## Common workflows

### Ephinea changed BB drop rates

```bash
npm run update:bb
npm run build
```

### A translation mapping or PSO Haven localization changed

```bash
npm run update:i18n
npm run build
```

### DC or NGC source HTML changed

```bash
npm run update:dc # Use update:ngc for GameCube data.
npm run build
```
