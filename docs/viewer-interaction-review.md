# Drop-chart reading and interaction review

The task is repeated lookup and comparison across monsters, Section IDs and
probabilities. Optimize legibility, stable visual anchors and predictable input,
not decorative density. This revision supersedes inline portraits and rainbow
text from the first September 18 release.

- Reserve saturated Section ID colors for headers; neutral body cells reduce
  competition with names and rates. Underlines identify links without relying
  on color. SS remains an explicit badge with readable text.
- Keep 14px item/monster text and 13px tabular rates, 1.5 line height and system
  Chinese/Japanese font families. Name and probability form a compact vertical
  pair. Avoid breaking their relationship merely to right-align all numbers.
- Freeze headers and row identities in a bounded, keyboard-scrollable table.
  This deliberately preserves the comparison matrix rather than turning ten
  Section ID columns into unrelated mobile cards. The tradeoff is horizontal
  scrolling on small screens. Mobile filters scroll away; touch controls are
  at least 44px high.
- Hover/focus shows supplemental images, Escape dismisses them, and previews
  remain stable while inspecting a source. The brief exit delay allows pointer
  travel to the preview. Touch users can follow the same name link to details.
- Highlight the active row for pointer and keyboard use; show clear focus rings.
  Search has an associated label; filter buttons expose their pressed state.

Verification: BB/DC/NGC, English/Japanese/Chinese, widths 320/390/768/1440;
no page-level horizontal overflow; both table axes preserve headers; hover,
leave, Normal/Ultimate images, missing portraits, keyboard focus and Escape.
Measured normal-state text contrast across the tested table/control selectors
has a minimum of 5.01:1. This exceeds WCAG's 4.5:1 normal-text target, but is not
a claim of complete WCAG conformance or a substitute for player usability tests.
Desktop and mobile screenshots were visually inspected with real drop data.

References: [WCAG text contrast](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum),
[non-color link cues](https://www.w3.org/WAI/WCAG21/Techniques/general/G183.html).
