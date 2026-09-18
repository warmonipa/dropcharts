# PSO Drop Charts

Drop charts for Phantasy Star Online on Dreamcast, Nintendo GameCube, and Blue Burst.

The production site is [dropcharts.psohaven.com](https://dropcharts.psohaven.com/).

## Supported versions

- Blue Burst: Episodes 1, 2, and 4, including monster and box drops
- Nintendo GameCube: Episodes 1 and 2 monster drops
- Dreamcast: Episode 1 monster drops
- English, Japanese, and Chinese item data
- Responsive tables with a frozen monster/location column and centered area labels

## Development

Install Python 3.10 or later, [`uv`](https://docs.astral.sh/uv/), and Node.js. Then run:

```bash
npm test
```

The test suite validates data alignment, multi-drop cells, build output, and the responsive
table contract. Layout tests guard the single frozen label column and area-label centering
used during horizontal scrolling.

Build a deployable static site in `_site` with:

```bash
npm run build
```

See [the update and deployment guide](docs/update.md) for the complete data pipeline.

## License

This project is licensed under the ISC License. See [LICENSE](LICENSE).

## BB Wiki identities and artwork

BB monster labels and hover previews select the Normal or Ultimate form with the
current difficulty. Portraits appear on hover, using the same preview as items;
rows show only names and drop rates. Names and artwork come from the maintained Haven Wiki
catalog; Chinese monster names use this repository's i18n_names.json authority.
Both forms and all three languages remain searchable. Monster links preserve
difficulty and language; item links preserve language. Detail URLs use catalog
IDs, including every item in multi-item drop cells and box rows.
Difficulty, language, episode, row type, rate format and search are stored in the
URL, so returning from a detail page or reloading restores the same table.

Regenerate after updating either catalog or the name authority:

```sh
npm run update:wiki -- /path/to/ephinea4haven.github.io
```

Commit the generated bb/data/monsters.js and bb/images/monsters assets together.
Each portrait records its Ephinea Wiki source page in the generated data. Bulk
and Death Gunner currently have no verified independent artwork and therefore have
no image preview. The sync rejects missing monster identities, translations and item
detail IDs; npm test checks every current BB row and link in all languages and
difficulties. The deploy build uses the checked-in assets and needs no Wiki
checkout or runtime request to another site to render the table.
Validation failures (including missing source artwork or item identities) leave
the previously generated catalog and images intact.

Source discrepancy checked on 2026-09-18: the [Ephinea Wiki Gillchic page](https://wiki.pioneer2.net/w/Gillchic)
labels EP1 Ultimate as `ギルチッチ` and EP2 Ultimate as `ギルチック`, while the
Japanese drop-chart row uses `ギルチッチ` in both episodes. The catalog retains
the Wiki's episode-specific labels; this difference is not silently normalized.

## Reading and interaction

The body uses neutral dark surfaces with light-blue detail links (underlined on hover or keyboard focus) and
secondary, tabular-number drop rates. Section ID colors remain in column headers;
SS items use a readable text badge rather than animated rainbow text. Row hover
and keyboard focus highlight the current row. The table freezes its header and
monster column within a keyboard-scrollable region. Mobile filters scroll away
instead of permanently covering the reading area; touch controls retain 44px
minimum heights.

Monster and item images share a hover/focus preview. Escape dismisses it; unknown
portraits have no preview. Clicking names still opens details, including on touch
screens. Images are supplemental and are never required to identify a drop.
See [the interaction review](docs/viewer-interaction-review.md) for rationale and
verification boundaries.
