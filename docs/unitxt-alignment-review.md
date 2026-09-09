# Unitxt alignment review

Scope: align the working datasets with the finalized Chinese Unitxt, preserving
English/Japanese inputs, drop probabilities, coordinates, and SS markers.
DC Japanese is generated output and is included in the role-collision repair.

| ID | Status | Root cause and expanded scope | Closing evidence |
| --- | --- | --- | --- |
| UA-01 | Fixed | Legacy item/monster spellings bypassed canonical Unitxt names; a family label collapsed distinct DB weapons. Expanded to every active DC/NGC name and related authority aliases. | Source-backed aliases overwrite stale Chinese while preserving Japanese metadata; missing canonical identities fail; both weapon families use paired Japanese identities; all 18 dated variants retain year/manufacturer. |
| UA-02 | Fixed | A flat lookup let item `Claw` overwrite monster `Claw`; item entries also masked Japanese monster translations. Expanded to exact, normalized and Japanese paths in both languages. | Separate role indexes; regressions assert 爪虫 versus 光子爪 and クロー, plus case-sensitive Blade/BLADE behavior. |
| UA-03 | Fixed | Structural checks and reviewing only changed strings missed unchanged stale names; the i18n entry point omitted BB regeneration. | Full name gate in npm test; source gate after update:i18n; independent Japanese-year checks; multi-identity census; negative mutations; repeated generation; final build. |

The earlier completion claim was premature: it verified changed strings and
structural integrity, but did not compare unchanged consumers with their canonical
identity. The first two focused regressions reproduced the old alias and Claw bugs
before their implementation was changed. Later review expanded UA-01 to Japanese
boss aliases and the nine DB variants before closing it.

## Identity evidence

The aligned Chinese Unitxt is psobb-localization commit
`5a679c5e2f9857f54b83a9b8b415931ac172324e`, `localization/zh/unitxt_j.prs`,
SHA-256 `720cfd525b5645198d89661ea71c628696df6e024e4a03ef4db75bf1110cf401`.
EN, JP and ZH resources were decoded separately with newserv and compared by
Unitxt group/index. This is independent of the droptable translation generator.

The second independent audit inspects dated Japanese identities before English
matches. It found zero mismatches among 6,710 BB, 1,442 DC and 3,292 NGC drop
occurrences, including all 18 dated NGC weapons. Remaining legacy spellings and
cross-version items are covered by the explicit evidence below. The first audit's
English-first rule missed nine dated Flowen swords; its earlier clean result was
not sufficient evidence of identity preservation.

- Japanese pairs directly identify the misspellings KALADGOLG, ANGLE HARP,
  G-ASSASIN'S ARMS, Delsabre's arms, S-BERILL'S ARMS, Belra's Right Arms,
  GIGUE'S ARMS, PART OF EGG BLASTER, NUG-2000 BAZOOKA, section-ID cards,
  and all six CURE variants.
- Booma/Gobooma/Gigobooma arm labels differ in plural spelling and Japanese
  手/腕 wording; each refers to the same named enemy part, never its converted
  weapon. Gal Gryphon Wing differs by possessive/punctuation.
- CUSTOM equipment Ver.00 spellings refer to the three corresponding Unitxt
  ver.OO equipment entries. MAGIC ROCK MOOLA and PARASITIC GENE FLOW are the
  same upgrade resources despite legacy Japanese spelling differences.
- C-bringer is the legacy Chaos Bringer abbreviation; METEOR CUDGE is Meteor
  Cudgel. Other authority aliases cover punctuation, quoting and established
  legacy spellings. Aliases contain only canonical English identities, not
  duplicate Chinese translation literals.
- DC-only Sound Source FM, SH2, SH4, 68000, High-level Mag Cell/Armor, Special
  Gene Flou, Joint Parts, Modem and Power VR retain repository-owned names.
  Special Gene Flou is not automatically mapped to the BB Flow gene.
- `SH2`, `SH4` and `68000` are intentional Latin hardware identifiers. They
  account for the 15 unchanged item occurrences in DC's coverage report.
- A conflicting Japanese Flowen shield/armor source label is not allowed to
  override its unambiguous English equipment identity.
- Japanese boss spelling aliases and Hidelt/Hildetor/Pouifully Slime resolve
  through monster identities. Existing `?` annotations remain visible.

### NGC DB weapons

NGC `en.js` uses `DB'S SWORD` for nine different weapons. Its paired `ja.js`
provides the years. newserv's `system/tables/rare-table-v3.json` confirms distinct
item codes for these Section IDs; `names-v3.json` confirms the shared legacy
English label. The two 3069 manufacturers additionally agree with the
[Chris source chart](https://wiki.pioneer2.net/w/DB%27s_Saber_%283069_Chris%29)
and [Torato source chart](https://wiki.pioneer2.net/w/DB%27s_Saber_%283069_Torato%29).

| Section ID | v3 item code | Canonical Unitxt identity |
| --- | --- | --- |
| Greenill | 009000 | DB's Saber (3062) |
| Skyly | 009001 | DB's Saber (3064) |
| Bluefull | 009002 | DB's Saber (3069 Chris) |
| Purplenum | 009003 | DB's Saber (3067) |
| Pinkal | 009004 | DB's Saber (3069 Torato) |
| Redria | 009005 | DB's Saber (3073) |
| Oran | 009006 | DB's Saber (3070) |
| Yellowboze | 009007 | DB's Saber (3075) |
| Whitill | 009008 | DB's Saber (3077) |

The ambiguous DB family entry is absent from the authority. Both families resolve
from their paired Japanese source labels before merging or translating names.
Only DB 3069 needs a Section ID to distinguish manufacturers. Missing Japanese
identity, mismatched multi-item cell cardinality, unknown years, and unknown
DB 3069 manufacturers fail instead of falling back to an ordinary weapon.
The regression reads all nine real paired Japanese rows and checks the year and
both 3069 manufacturer names independently of the converter's alias table.

## First-pass verification

The second review below supersedes the first pass's completion claim.

- `npm test`: 43 tests passed; all BB/DC/NGC coordinates and DC/NGC generated
  names passed their complete gates.
- `python3 tools/validate_names.py --localization-repo ../psobb-localization`:
  authority source projections and every BB Chinese name passed.
- `npm run update:i18n`: completed all three versions without source fetching.
  A fault-injection run changed one row in each BB/DC/NGC Chinese dataset and
  KALADGOLG in the authority. The command repaired all four mutations and restored
  the exact semantic baseline for all nine datasets plus the authority.
  Generator timestamp comments are not expected to be byte-idempotent.
- `npm run build`: complete Pages artifact built; generated datasets match the
  final working datasets. This is local build verification, not publication.
- The repair changes DC Chinese by 4 monster rows and 5 item occurrences;
  NGC Chinese by 13 monster rows and 269 item occurrences; DC Japanese by
  174 monster rows previously shadowed by item metadata. It changes 8 monster
  and 41 item authority entries (including removal of the ambiguous DB entry).
  BB Chinese already matched the finalized source and has no further semantic
  change. English inputs and BB/NGC Japanese inputs are unchanged. No drop rate,
  coordinate, row count, cell shape or SS marker changed.

No commit, push, deployment, translation-source edit or runtime UI claim is part
of this review. Local source/data consistency and publication are separate gates.

## Second review: reopened and closed findings

UA-01: The same-English/multiple-Japanese-identity scan found nine dated Flowen swords still rendered as the ordinary sword. The prior DB-only section mapping was an incomplete root-cause fix. Review both families using paired Japanese identities, ordinary versus dated items, manufacturers, and missing/invalid context.

UA-03: The independent item audit preferred any English match and failed to inspect conflicting Japanese identities. The regeneration gate then reproduced the same error. Add a complete family/identity cardinality check and negative regressions, not only another changed-string assertion.


The replacement resolves each dated weapon from its paired Japanese label,
rather than adding another Section-ID-only exception table. Ordinary Flowen
swords remain ordinary; dates must exist in Unitxt. All 18 dated source cells were
compared with independently decoded Unitxt item groups (Flowen indexes 537–545,
DB indexes 546–554). The GC rare table confirms the following Flowen identities:

| Section ID | v3 item code | Year |
| --- | --- | --- |
| Greenill | 008F00 | 3060 |
| Skyly | 008F01 | 3064 |
| Bluefull | 008F02 | 3067 |
| Purplenum | 008F03 | 3073 |
| Pinkal | 008F04 | 3077 |
| Redria | 008F05 | 3082 |
| Oran | 008F06 | 3083 |
| Yellowboze | 008F07 | 3084 |
| Whitill | 008F08 | 3079 |

The census of every English item with multiple Japanese labels found exactly five
families: DB sword, Flowen sword, VISK'235W, P-arm's Arms, and Flowen shield. The
first two carry distinct item identities. VISK and P-arm's labels are spelling
variants. Flowen shield contains the already documented shield/armor source typo.
Tests now require review when another family enters this census and independently
check every dated Japanese item against its generated Chinese name.

Final verification for this review:

- The added all-dated-items regression failed on all nine Flowen years before
  the fix, then passed. Missing identities, unknown manufacturers/years, mixed
  multi-item cells, ordinary versus dated weapons, and input immutability are
  covered alongside the previous role and alias regressions.
- `npm test`: 48 tests passed, plus complete coordinate and name gates.
- `npm run update:i18n`: passed, including the live Unitxt source gate;
  all nine datasets and the authority remained semantically identical after
  repeated generation. Timestamp comments are excluded from this comparison.
- `npm run build`: passed; all nine built datasets equal their repository inputs.
- The only further data changes are the nine NGC Chinese Flowen sword names.
  Their ordinary versions, all DB years/manufacturers, the authority, all BB/DC
  names, every English/Japanese source, rates, coordinates and SS markers retain
  their pre-review values. Across both repairs NGC has 278 corrected item
  occurrences and 13 corrected monster rows relative to the initial alignment.

UA-01 and UA-03 were reopened because the earlier root-cause expansion and its
English-first audit missed another family with collapsed identities. Both are
closed after the broader census, independent year gate and fresh full review.

## Third review: coverage fallback

UA-03 reopened: removing the CURE SHOCK authority entry and replacing its five NGC Chinese occurrences with English passed both the name and current-Unitxt gates. The validator reused permissive original-text fallback without checking translation coverage. Expand to missing item/monster mappings, exact/normalized/Japanese indexes, nested cells, and intentional same-text identifiers.


The coverage gate now requires an explicit nonblank target-language mapping at
the lookup position translation actually selects. It checks exact, Japanese and
normalized indexes in order; a blank exact entry cannot be hidden by a valid
lower-priority match. Intentional unchanged identifiers remain allowed through
explicit authority entries. This gate does not call the translator's permissive
original-text fallback to establish coverage.

Closing evidence:

- The missing CURE SHOCK entry/five-English-output regression failed before the
  fix and now reports all five missing mappings. A second regression exposed a
  blank exact Japanese label shadowing a valid Japanese reverse lookup; it now
  fails coverage as required. Additional cases cover missing monster and nested
  item target languages, role separation, normalized spelling, Japanese lookup,
  and intentional same-text SH2.
- `npm test`: 52 tests passed, plus full coordinate and name gates.
- `python3 tools/validate_names.py --localization-repo ../psobb-localization`:
  all v2/v3 translations have explicit coverage; authority projections and all
  v4 Chinese names match the current Unitxt source.
- `npm run update:i18n`: passed and preserved all nine datasets semantically and
  the authority byte for byte. `npm run build` passed.
- No display names, translations, rates, coordinates, SS flags, or input resources
  changed in this review. Only the validator, regression tests and documentation
  changed. The control missed coverage because matching regenerated fallback text
  was previously mistaken for a verified mapping; UA-03 is closed with a separate
  presence check plus negative regressions.

Coverage of the requested versions:

| Version | Dataset | Rows | Nonempty drop occurrences |
| --- | --- | ---: | ---: |
| v2 | DC | 180 | 1,492 |
| v3 | NGC | 359 | 3,429 |
| v4 | BB | 596 | 6,710 |

Every version's English/Japanese/Chinese coordinate integrity is checked. v2/v3
translation coverage is checked against the authority; v4 generation rejects
missing Unitxt names and the source gate compares every final Chinese name.
Runtime display in original game clients and publication remain outside this
local data review. No commit or push was performed.


## Legacy v2 item formatting alignment

The user requested alignment of the ten v2-only item names with localization's
current rules. `UNITXT_UPDATE_SOP.md` requires half-width Latin/digits and one
half-width space at a direct Chinese boundary, uses 玛古 for MAG, and fixes
Flow's shared proper-name root as 弗洛. Item Gene terminology follows 基因,
as in `侵蚀基因「弗洛」`; the separate legacy item retains 特殊 and is not
mapped to the BB parasitic gene's identity.

| Legacy English identity | Aligned Chinese name |
| --- | --- |
| Sound Source FM | FM 音源 |
| SH2 | SH2 |
| SH4 | SH4 |
| 68000 | 68000 |
| Power VR | PowerVR 显卡 |
| Modem | 调制解调器 |
| Joint Parts | 结合部件 |
| High-level Mag Cell, Eno | 高位玛古细胞「艾诺」 |
| High-level Mag Armor, Uru | 高位玛古装甲「乌尔」 |
| Special Gene Flou | 特殊基因「弗洛」 |

The existing `Sourd Source FM` spelling alias receives the same spacing change.
The other seven identities already follow the relevant format and terminology.
These names remain in droptable's authority; no localization Unitxt slot is
added or replaced. Generation changes 13 DC Chinese drop occurrences (10 FM,
2 Power VR, 1 Special Gene); every other name and all language-independent
fields are preserved. Validation uses `npm test` (52 tests), the current-Unitxt
name gate, full regeneration stability, and the final local Pages build.

## Whole-dictionary consumer review (2026-09-09)

UA-01 / UA-03 reopened: Haven's item lookup renders the complete authority,
including historical labels that no current drop cell uses. The earlier active-
dataset census and explicit alias set missed these consumers. Default tests now
validate every reviewed alias against its canonical dictionary identity, and the
live-source gate also refreshes existing monster/area labels in the dictionary.
Real item identities take precedence over context labels after normalization:
`CLAW` / `Claw` must remain the weapon in the item dictionary and the enemy in
the monster dictionary.

Identity evidence:

- Same-index EN/JP Unitxt confirms the Japanese-key aliases below, including
  Cure/Poison, Mag cells, ordinary equipment, Four Heavens volumes and parts.
- Japanese `ＤＢの剣(3062)` identifies DB's Saber (3062). Explicit English years
  select the corresponding Agito and DB entries; an unqualified DB 3069 cannot
  select Chris versus Torato and is removed from the unused flat aliases.
- newserv `names-v2.json` / `names-v3.json` identify MARK3, Kit of MARK3,
  Book of KATANA1–3 and P-ARMS'S BLADE. The six legacy badge names match v3/v4
  codes 031403–031405 and 031407–031409; their BB identities are Weapons badges.
- Reviewed English/Japanese body-part spellings retain the named enemy and
  Arm/Head role. Tyrell's Parasol is Japanese 総督恩賜パラソル, matching the
  legacy PRINCIPAL'S GIFT PARASOL identity.
- Existing context labels use the current source's standard/Ultimate monster
  and area maps. They cannot override a normalized item identity.
- Ten repository-owned legacy labels (Mag factors 503–507, L&K15 COMBAT and
  four Pen labels) receive only half-width/boundary-spacing normalization;
  their identities are not equated with a different BB item. The all-years
  Agito category uses the common reviewed 颚刀 stem, without choosing a year.

The reviewed unused import aliases removed below have no BB/DC/NGC drop
consumer. They are malformed/annotated duplicate labels or cannot identify one
item. The six dated Agito names and both DB 3069 manufacturers remain available
under their canonical names. No live version-only item is removed.

| Historical dictionary key | Canonical Unitxt identity |
| --- | --- |
| `DB'S SABER 3062` | `DB's Saber (3062)` |
| `DB’S Saber 3077` | `DB's Saber (3077)` |
| `DB’S Saber (No 9*)` | `DB's Saber` |
| `MARK3` | `Mark III` |
| `Kit of MARK3` | `Kit of Mark III` |
| `P-ARMS'S BLADE` | `P-Arms' Blade` |
| `PRINCIPAL'S GIFT PARASOL` | `Tyrell's Parasol` |
| `Unused Item0` | `Unused Item01` |
| `AGITO 1975` | `Agito (1975)` |
| `AGITO 1977` | `Agito (1977)` |
| `AGITO 1980` | `Agito (1980)` |
| `AGITO 1983` | `Agito (1983)` |
| `AGITO 1991` | `Agito (1991)` |
| `AGITO 2001` | `Agito (2001)` |
| `Book of KATANA1` | `Book of Katana 1` |
| `Book of KATANA2` | `Book of Katana 2` |
| `Book of KATANA3` | `Book of Katana 3` |
| `Bronze Weapons Badge` | `Weapons Bronze Badge` |
| `Silver Weapons Badge` | `Weapons Silver Badge` |
| `Gold Weapons Badge` | `Weapons Gold Badge` |
| `Crystal Weapons Badge` | `Weapons Crystal Badge` |
| `Steel Weapons Badge` | `Weapons Steel Badge` |
| `Aluminum Weapons Badge` | `Weapons Aluminum Badge` |
| `Leather Weapons Badge` | `Weapons Leather Badge` |
| `Bone Weapons Badge` | `Weapons Bone Badge` |
| `Silver Badge` | `Weapons Silver Badge` |
| `Gold Badge` | `Weapons Gold Badge` |
| `Crystal Badge` | `Weapons Crystal Badge` |
| `Aluminum Badge` | `Weapons Aluminum Badge` |
| `Leather Badge` | `Weapons Leather Badge` |
| `Bone Badge` | `Weapons Bone Badge` |
| `エンジェル/ＴＰ` | `Angel/TP` |
| `オパオパの心` | `Heart of Opa Opa` |
| `オモチャオのパーツ` | `Parts of RoboChao` |
| `カラドボルグ` | `Kaladbolg` |
| `キュア/ポイズン` | `Cure/Poison` |
| `クラブ` | `Club` |
| `サイキックバリア` | `Psychic Barrier` |
| `セレスティアルシールド` | `Celestial Shield` |
| `チャオの心` | `Heart of Chao` |
| `ディグラインダー` | `Digrinder` |
| `ディヴィニティアーマー` | `Divinity Armor` |
| `ハンターウォル` | `Hunter Wall` |
| `ハンターフィールド` | `Hunter Field` |
| `パラッシュ` | `Pallasch` |
| `ピアンの心` | `Heart of Pian` |
| `フォースウォル` | `Force Wall` |
| `フォースフィールド` | `Force Field` |
| `マグ細胞２１３` | `Cell of Mag 213` |
| `マグ細胞５０２` | `Cell of Mag 502` |
| `マジカルピース` | `Magical Piece` |
| `レンジャーウォル` | `Ranger Wall` |
| `レールガン` | `Railgun` |
| `ロックガン` | `Lockgun` |
| `四天　参の巻` | `Book of Katana 3` |
| `四天　壱の巻` | `Book of Katana 1` |
| `四天　弐の巻` | `Book of Katana 2` |
| `四神盾「朱雀」` | `Gods Shield "Suzaku"` |
| `四神盾「玄武」` | `Gods Shield "Genbu"` |
| `四神盾「白虎」` | `Gods Shield "Byakko"` |
| `四神盾「青龍」` | `Gods Shield "Seiryu"` |
| `寄生防具「デ・ロル」` | `Parasite Wear: De Rol` |
| `寄生防具「ネルガル」` | `Parasite Wear: Nelgal` |
| `寄生防具「ヴァジュラ」` | `Parasite Wear: Vajulla` |
| `秋子おばさんの中華鍋` | `Akiko's Wok` |
| `細菌防具「ラフテリア」` | `Virus Armor: Lafuteria` |
| `雷杖「インドラ」` | `Storm Wand: Indra` |
| `ＨＰ/ジェネレイト` | `HP/Generate` |
| `ＴＰ/ジェネレイト` | `TP/Generate` |
| `ウィジャヤ` | `Vjaya` |
| `グレイヴ` | `Glaive` |
| `フロウウウェンの盾` | `Flowen's Shield` |
| `レンジャーフールド` | `Ranger Field` |
| `Chaos Bringerの右手` | `Bringer's Right Arm` |
| `Chaos Sorcererの右手` | `Sorcerer's Right Arm` |
| `Delsaberの右手` | `Delsaber's Right Arm` |
| `Delsaberの左手` | `Delsaber's Left Arm` |
| `Hildebearの頭` | `Hildebear's Head` |
| `Hildeblueの頭` | `Hildeblue's Head` |
| `Pan Armsの両手` | `P-arm's Arms` |
| `Sinow Beatの両手` | `S-beat's Arms` |
| `Dragonフレーム` | `Dragon Frame` |

Removed unused keys: `1975ドウセツ`, `1977ジョウウン[偽]`, `1980テンガイ[偽]`, `1983ドウセツ[偽]`, `1991キコク[偽]`, `1991キコク[偽])(AGITO 1991 Kikoku[fake]`, `2001キコク[偽])(AGITO 2001 Kikoku[fake]`, `アギト(1975)`, `アギト(1975)(※1)`, `アギト(1977)`, `アギト(1977))`, `アギト(1980)`, `アギト(1983`, `アギト(1983)`, `アギト(1983))`, `アギト(1991)`, `アギト(1991))`, `アギト(2001)`, `アギト(2001))`, `AGITO`, `DB’S Saber 3069`, `Sinow Redの両手`.


## Final downstream handoff (2026-09-09)

UA-01 / UA-03 are closed after the whole-dictionary and downstream checks.
The dictionary repair is published in commit
`62cdfbdbe011ae33ecd3927a6118e371ab7d8878`: 107 Chinese labels corrected,
22 malformed or ambiguous aliases removed, and 1,566 item-dictionary entries
retained. The authority SHA-256 is
`cbb4b89da0cfb213494edba99eccc2aabc7c1660bf5b52022b6575ee82c753ed`.
This documentation follow-up does not change that authority or the nine datasets.

The absence of a BB/DC/NGC drop consumer did not prove an alias was unused by
Haven. Its Black Paper's Deal table still referenced unqualified DB 3069.
The [Ephinea quest chart, revision 42514](https://wiki.pioneer2.net/index.php?title=Black_Paper%27s_Dangerous_Deal&oldid=42514)
identifies Dorphon Normal's reward as DB's Saber (3069 Chris). Haven now uses
`db_s_saber_3069_chris`; the ambiguous alias is not restored. Its regression
checks all 218 Black Paper and 329 Coren structured references, plus the exact
manufacturer in Chinese and English in the browser.

Final local verification:

- `npm test`: 55 tests passed, followed by coordinate and name gates.
- `.venv/bin/python tools/validate_names.py --localization-repo ../psobb-localization`:
  current-source projections and all generated names passed.
- `npm run update:i18n`: regeneration reached the same semantic result; all nine
  BB/DC/NGC datasets and built copies preserve their reviewed values.
- `npm run build`: 410 files built successfully.
- Haven's final build and 122 browser tests passed, including its complete
  dictionary, exact item identities, archived events and dynamic responses.

Current Caduceus, Excalibur and Glide Divine names remain inherited from
localization. The subsequent naming-strategy discussion did not authorize new
translations. Cross-repository consistency is not independent proof of a newly
proposed translation or in-game rendering. The user's follow-up authorizes
committing and pushing the documentation handoff on master; publication results
must be checked separately from these local review results.
