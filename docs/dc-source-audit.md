# DC Version 2 source audit

The DC viewer covers four difficulties, 45 enemies per difficulty and ten
Section IDs (1,800 cells). This audit corrects DC v2 data and rate presentation;
it does not change BB or GameCube data.

## What was wrong and what changed

| Defect | Affected path | Result after correction |
| --- | --- | --- |
| Conditional RDR was displayed as final DR, then divided by DAR again for the tooltip | `shared/viewer.js`, DC branch; `docs/manual-dc.md` | Display `DAR × RDR`; tooltip reads source RDR directly; Dark Falz displays 0% final DR |
| Two incorrect rates and six missing rates in preserved input | `tools/dc_source_errata.py`; all three `dc/data/*.js` files | Verified RDR values restored, with source-drift checks on future ingestion |
| Sixteen rate tokens contain `<`, `)` or `>` from damaged source markup | `tools/parse_dc.py`; all three `dc/data/*.js` files | Numeric percentage tokens parse and render correctly |
| Thirteen generated cells identify different items from the v2 reference | `tools/parse_dc.py`; all three `dc/data/*.js` files; Lockgun Japanese name in `i18n_names.json` | Canonical item identities and corresponding translations restored |
| Two new tests required an unconfigured sibling repository, so CI would fail before building | `tests/test_dc_source_audit.py` | Four pinned local fixtures retain full DC coverage without an external checkout |

The CI failure was missed by the first verification because the workstation
already contained the source repository. Review reproduced two
`FileNotFoundError` errors with that repository unavailable. The corrected
tests read local fixtures directly rather than falling back or skipping.

## Sources and rate meaning

- [Lost Technology DC v2 rare item list](http://www.dcn.ne.jp/~plastic/pso/ListFiles/ItemList_DC_V2.htm):
  enemy coverage, DAR, conditional RDR, item names and unobtainable Dark Falz drops.
- newserv `system/tables/rare-table-v2.json`, `Normal/Episode1`: independent v2
  item codes and exact RDR fractions for the corrections below. `VeryHard` and
  `Greennill` are the literal keys in that source.
  Checked at revision `e89ac8ebf201fbd2c86251d8597bf3ea3083501f`.
- Preserved `ephinea4haven` HTML selected by `tools/source_html.py`: the input
  used by the existing DC generator.

DC `drop.rate` stores **RDR**, not final per-kill DR. The viewer now computes
`DR = DAR × RDR` for the displayed item rate and shows source RDR in the tooltip.
BB and GC retain their existing rate handling. The source percentages are rounded;
display conversion does not claim exact binary probabilities.

For example, Normal Dark Gunner has DAR 40% and RDR 0.219727%, giving DR
0.0878908%. Previously the viewer displayed RDR as DR and divided it by DAR
again, incorrectly reporting an RDR of approximately 0.549%.
Dark Falz has DAR 0%; its stored rare items remain visible with final DR 0%.

## Confirmed corrections

| Difficulty and location | Previous | Corrected source value | Independent v2 evidence |
| --- | --- | --- | --- |
| Normal Delsaber, Pinkal | RDR 1.367188% | 1.269531% | `13/1024`, item `030D03` |
| Normal Chaos Bringer, Pinkal | RDR 1.269531% | 1.367188% | `7/512`, item `000E00` |
| Very Hard Dark Belra, Greenill / Bluefull / Purplenum / Pinkal / Yellowboze / Whitill | Missing RDR | 0.000429% | `9/2097152`, Celestial Armor `010117` |
| Normal La Dimenian, Redria | Flowen's Frame | Dragon Frame | `01010C` |
| Normal La Dimenian, Oran | Railgun | Lockgun | `000602` |
| Hard Sinow Gold, Viridia through Purplenum | HP/Revival | HP/Generate | `010334` |
| Hard Sinow Gold, Pinkal through Whitill | TP/Revival | TP/Generate | `010337` |
| Hard Dimenian, Oran | HP/Revival | HP/Generate | `010334` |

Sixteen other rate strings contained source-markup artifacts: trailing `<`
or `)`, or leading `>`. The DC parser removes these artifacts from numeric
percentage tokens before assigning item/rate pairs. All three generated
languages contain the same corrected probabilities.

| Malformed rate location | Section IDs | Original token → corrected token |
| --- | --- | --- |
| Normal Pouilly Slime | Yellowboze, Whitill | `40.625000%<` → `40.625000%` |
| Normal Dark Belra | Yellowboze | `0.781250%)` → `0.781250%` |
| Hard Nar Lily | Skyly, Bluefull, Purplenum, Pinkal, Redria, Oran, Yellowboze, Whitill | `62.500000%<` → `62.500000%` |
| Very Hard Savage Wolf | Bluefull, Pinkal, Oran, Whitill | `0.097656%<` → `0.097656%` |
| Very Hard Death Gunner | Yellowboze | `>0.000191%` → `0.000191%` |

The eight missing/incorrect numerical cells are corrected in
`tools/dc_source_errata.py`, with expected-old-value checks that reject source
drift. The parser resolves the four affected source item labels to their
canonical English identities before translation. Existing spelling and naming
differences that do not change item identity are preserved.

## Verification

`tests/test_dc_source_audit.py` checks all 1,800 generated rate cells in each
language against corrected ingestion, validates populated rates, and covers
the affected item identities and malformed source tokens.
Its four unmodified HTML inputs are pinned in `tests/fixtures/dc-v2`, with
source revision and SHA-256 hashes in `README.txt`. Tests read these fixtures
directly, so a clean checkout needs no sibling source repository or network.
`tests/test_viewer.cjs` covers DAR 0%, 40% and 100%, source RDR tooltips,
small probabilities, and all DC difficulties and languages.

Use `npm test` for the full regression suite. `tools/update.sh dc` applies the
ingestion corrections on subsequent data updates.

Validation on 2026-10-07:

- Configured workstation: 79 Python tests and 18 JavaScript tests passed.
- With `EPHINEA4HAVEN_REPO` pointing to a nonexistent path: the complete test
  command passed (78 Python tests passed; the existing NGC external-source
  test skipped; all 18 JavaScript tests passed). All six DC audit tests ran.
- All six DC audit tests also passed with subprocess execution prohibited.
- All four fixture files were byte-compared with the pinned Git inputs.
- Build produced 570 files; `git diff --check` passed.

These checks validate local source and build output, not a live deployment.
