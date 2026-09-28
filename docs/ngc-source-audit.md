# NGC source audit

Scope: every NGC monster cell (Normal to Ultimate, Episodes 1 and 2) compared
with an independent GameCube source. The NGC data derives from
ephinea4haven's `droptable/ngc/*.html` (initial commit `d9f96ff`), which keeps
no reference to the page it was saved from.

## Sources

| Source | Role |
| --- | --- |
| [GC Episode1 rare item list](http://www.dcn.ne.jp/~plastic/pso/ListFiles/ItemList_GC_EP1.htm), [Episode2](http://www.dcn.ne.jp/~plastic/pso/ListFiles/ItemList_GC_EP2.htm) | Cell-by-cell comparison: items, 5-decimal rare rates, monster drop rates |
| newserv `system/tables/rare-table-v3.json` with `names-v3.json` | Item codes and exact rates; decides item identity |
| [Ephinea classic charts](https://ephinea.pioneer2.net/classic-charts/ultimate/) | Unmodified rates; confirms monster drop rates |
| ephinea4haven `droptable/droptable.sql` (`d9f96ff`) | Same-project copy of the classic rates |

## Result

Every matched cell (3,330 before the rows below were restored) agrees on rare rate after rounding to the list's five
decimals. The corrections below were each confirmed by newserv or the classic
chart; all three NGC languages were changed together.

| Location | Before | After |
| --- | --- | --- |
| Ultimate Ep1 Sinow Red / Redria rate | `AGITO` (source printed the item name) | 0.009918212890625% |
| Normal Ep1 | Nano Dragon row missing | Restored: 50%, Sol Atomizer/Trimate 56.25% |
| Normal Ep2 | Dubchic row duplicated in place of Gilchic | Gilchic: 30%, Monogrinder 0.054931640625% in Viridia and Bluefull |
| Ultimate Ep1 Hidelt drop rate | 80% | 85% |
| Ultimate Ep1 Migium drop rate | 5% | 45% |
| Ep2 Merikle, Mericus, Ill Gill, Del Lily, Epsilon drop rates (all difficulties) | `?%` (empty) | 80%, 80%, 40%, 35%, 30% |
| 15 Cure unit cells | Shifted labels, e.g. CURE SHOCK where the table has Cure/Paralysis | Cure/Paralysis, Slow, Shock, Freeze as in newserv |
| Very Hard Ep1 Canane / Viridia | Sense Plate | Smoking Plate |
| 7 Very Hard Ep2 Flowen's Shield cells | Japanese `フロウウェンの鎧` | `フロウウェンの盾` |

## Differences kept

- Episode 2 Mothmant/Mothvert rows are absent from the GC list but present in
  the classic chart (20%); they stay.
- The GC list and the classic chart name the Ultimate Ep2 DB's Saber in Skyly
  3067 and in Purplenum 3064. newserv assigns item codes 009001 and 009003,
  which Unitxt names 3064 and 3067 (see `unitxt-alignment-review.md`); the
  Unitxt identity stays.
- Event Rappies (Saint, Hallo, Egg) exist only in the GC list and are not added.
- The remaining name differences are transliterations of the same items
  (for example ブーマの右手/右腕, ヴィジャヤ/ウィジャヤ).

## Regeneration

`tools/update.sh ngc` does not reproduce the checked-in NGC data even before
this audit: it reverts Unitxt-aligned names such as `Agito (2001)` and
`L&K14 Combat` to raw source labels. The corrections above are therefore made
in the data files and guarded by `tests/test_ngc_source_audit.py`; the Agito
rate erratum is also applied by `parse_ngc.py`.
