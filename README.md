# PSO Drop Charts

Drop charts for Phantasy Star Online on Dreamcast, Nintendo GameCube, and Blue Burst.

The production site is [dropcharts.psohaven.com](https://dropcharts.psohaven.com/).

## Supported versions

- Blue Burst: Episodes 1, 2, and 4, including monster and box drops
- Nintendo GameCube: Episodes 1 and 2 monster drops
- Dreamcast: Episode 1 monster drops
- English, Japanese, and Chinese item data
- Responsive tables with a frozen monster/location column and centered area labels

## Architecture and development

Angular 22 owns routing, pages and interactions. Standalone components use
signals and zoneless change detection; production builds prerender every page
and hydrate it in the browser. GitHub Pages serves the static artifact without
a backend or rewrite rules.

| Public route | Chart | Compatible old entry |
| --- | --- | --- |
| / | Platform selector | /index.html |
| /blue-burst/ | Blue Burst | /bb/, /bb/index.html |
| /dreamcast/ | Dreamcast | /dc/, /dc/index.html |
| /gamecube/ | GameCube | /ngc/, /ngc/index.html |

Canonical routes use trailing slashes. Language and chart state use the existing
lang, diff, ep, type, rate and q query parameters. Old entries serve the same
prerendered chart and Angular normalizes them to the canonical route, preserving
query parameters and fragments. Navigation within the app uses canonical routes.
Missing directory slashes receive the host’s normal 301 redirect. Explicit
index.html requests remain HTTP 200; Angular performs the canonical route
normalization after hydration. Old standalone scripts and dataset URLs are not
published. Without JavaScript the default table is readable; query-selected
filters require JavaScript.

- src/app/chart/: typed drop model, Angular table, responsive viewport and previews.
- src/app/app.routes.ts: lazy platform data and page routes; compatibility aliases.
- scripts/generate-data.mjs: converts checked-in pipeline datasets to build inputs.
- tools/: Python ingestion, localization, alignment and validation, unchanged.
- scripts/build-site.mjs: Angular prerendering, artifact validation and publication
  into _site; generated files remain ignored.

Install Node.js 24 (see .nvmrc), Python 3.10+ and uv, then run:

```bash
npm ci
npm test
npm run dev       # http://127.0.0.1:5173
npm run build
npm run preview   # http://127.0.0.1:4173
npm run test:e2e
```

Install the browser with `npx playwright install chromium` before running browser
tests. The suite covers direct HTTP entries, prerendered tables without JavaScript,
hydration, URL state, cross-platform navigation, previews and mobile scrolling.
The data tests cover every platform/language/difficulty and multi-drop cell.
After regenerating source data, restart the dev command to refresh its generated
inputs. A production build always regenerates them.

See [the update and deployment guide](docs/update.md) for the data pipeline.

## License

This project is licensed under the ISC License. See [LICENSE](LICENSE).

## BB Wiki identities and artwork

BB monster labels and hover previews select the Normal or Ultimate form with the
current difficulty. Portraits appear on hover, using the same preview as items;
rows show only names and drop rates. Names and artwork come from the maintained Haven Wiki
catalog; Chinese monster names use this repository's i18n_names.json authority.
Both forms and all three languages remain searchable. Monster links preserve
difficulty and language; item links preserve language. Detail URLs use Haven’s semantic /items/{id}/ and /enemies/{id}/ paths with
language prefixes (Chinese unprefixed, English /en/, Japanese /ja/), including
every item in multi-item drop cells and box rows.
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

The original blue/purple interface palette is preserved around the table.
Section ID columns follow Ephinea's drop charts: headers and cells, empty ones
included, are filled with the Section ID color and use Ephinea's fixed white or
black text per column. Item names, rates and item links inherit that text
color; item links underline on hover or keyboard focus, monster links change
color, and keyboard focus keeps a visible outline.
Each header shows the Section ID symbol above its localized name (Japanese and
Chinese use the Unitxt Section ID card names). The symbols are copied unchanged
from ephinea4haven's `assets/img/section/icon/`; see
`shared/images/section-ids/NOTICE.txt`. Phantasy Star Online and the Section ID
symbols are property of SEGA. DC displays per-kill rates calculated as DAR ×
source RDR, with source RDR in the tooltip; 0% DAR means 0% final drop rate.
DC/NGC percentages use three significant digits where supported by the formatter.
See [the DC v2 source audit](docs/dc-source-audit.md) for corrected cells and validation.
BB named banner items without a Hit requirement use rainbow text; those requiring
untekked Hit use steady gold with a dark outline and a condition tooltip. Technique disks are excluded.
DC/NGC retain their legacy SS rainbow rule. There are no extra item badges;
reduced-motion preferences keep the rainbow static. Row hover
and keyboard focus highlight the current row. The table freezes its header and
monster column within a keyboard-scrollable region. Mobile filters scroll away
instead of permanently covering the reading area; touch controls retain 44px
minimum heights.

Monster and item images share a hover/focus preview. Escape dismisses it; unknown
portraits have no preview. Clicking names still opens details, including on touch
screens. Images are supplemental and are never required to identify a drop.
See [the interaction review](docs/viewer-interaction-review.md) for rationale and
verification boundaries.

Monster area groups follow the [area review](docs/monster-area-review.md): Recon is
in Seabed, and six Episode 4 enemies share a Crater / Subterranean Desert group.

See [banner highlight rules](docs/banner-highlights.md) for thresholds and exclusions.
