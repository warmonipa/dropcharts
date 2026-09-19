# BB banner highlights

The BB viewer uses the explicitly named items in the
[Ephinea Wiki Banners list](https://wiki.pioneer2.net/w/Banners), reviewed
2026-09-19 against revision 38974. This presentation rule does not change items,
drop rates or server behavior. DC/NGC retain their legacy SS list.

## Appearance

- No Hit requirement: animated rainbow name, with no badge or underline.
- Named weapon with a Hit requirement: steady gold name. Hover its name for the
  required **untekked** Hit percentage. The condition is also included in its
  accessible name. Color identifies eligibility, not the actual rolled Hit.
- Search matches use a subtle background lift without a red outline.
- Probabilities keep their normal text color. Links, image previews and keyboard
  focus outlines remain functional. The page and table palette is unchanged.
- No separate legend row is shown. The localized condition is available on each
  highlighted item name; clicking the name still opens the item detail page.

Hit tooltips state only the condition, for example
“公告条件：未鉴定 Hit ≥ 30%。” English, Japanese and Chinese are supported.
Scope explanations stay in this document rather than the tooltip. Missing
translations fall back to English; internal translation keys are never displayed.

Gold thresholds are 20, 30, 40 or 50 Hit. For example, Frozen Shooter requires
30 Hit and Spread Needle requires 40 Hit. The table has no rolled Hit values.

## Boundaries

Technique **disks** are excluded; technique weapons such as cards and Psycho Wand
are included. Agito (1975)'s no-Hit banner is Classic-only and is not applied to
these main-server charts. Weapon box drops are excluded. Named non-weapons can
still qualify in boxes.

The general rule for any rare weapon with 90 untekked Hit is documented on the
Wiki but deliberately does not color every rare weapon in this chart. The colors
identify explicitly named items, not every possible announcement. Event rewards
not present in the drop data are not added as invented drop rows. Exact names are
used: `Heart of Poumn` and unlisted hearts do not qualify by prefix alone.

## Generation and checks

`tools/banner_rules.py` owns the BB name/threshold list. `tools/mark_ss.py` keeps
its existing command name for the update pipeline. It derives `ss: true` for
no-Hit BB items or `bannerHit: 20|30|40|50` for conditional weapons from English
names and row type, then applies metadata to all three languages by coordinate.
These fields are mutually exclusive. The script removes stale flags and is
idempotent. Legacy DC/NGC SS classification is unchanged.

Coordinate synchronization and validation include both metadata fields. Tests
cover thresholds, Classic/technique/box exclusions, exact-name matching, nested
multi-item cells, preservation of translations/rates, idempotence and rendering
in all three BB languages.
