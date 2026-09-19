# Drop-chart reading and interaction review

Reviewed on 2026-09-19. The main tasks are finding drops and comparing monsters,
Section IDs and probabilities.

## Final appearance

- Preserve the original blue/purple page, toolbar and table backgrounds, button
  colors, borders and row-hover colors. Section ID colors remain in headers.
- Use soft-white names and secondary gray probabilities. Item/monster text is
  15px regular weight; rates are 13px with tabular numerals and a small gap below
  the name. Monster DAR uses the rate color rather than a separate gold accent.
- Keep language-specific Chinese/Japanese font stacks and 1.5 line height.
- BB banner highlighting now follows [the named-banner rules](banner-highlights.md):
  no-Hit items use rainbow; Hit-conditional weapons use steady gold with a tooltip.
  DC/NGC retain legacy SS classification.
- Keep rainbow names with their outline, glow and four-second animation.
  There is no extra SS badge. Reduced-motion preferences keep the rainbow static.
- Name links have no underlines in normal, hover, keyboard-focus or search-match
  states. Hover/focus changes their color; keyboard focus retains a visible
  outline. Search matches use a subtle background lift and increased text weight, without
  a colored outline.

## Interaction

The table keeps a fixed header and monster column inside a keyboard-scrollable
region. Mobile filters scroll away and touch controls have a 44px minimum height.
Horizontal scrolling preserves the ten-column comparison matrix on small screens.

Monster and item pictures appear on hover/focus; Escape dismisses previews.
Names still open detail pages, including on touch devices. Images supplement
rather than replace names. Item probabilities can show inferred RDR when DAR
is available; no underline is required for that tooltip.

## Verification and limits

Chrome checks covered BB/DC/NGC, English/Japanese/Chinese and widths
320/390/768/1440: 36 combinations without page-level horizontal overflow.
Sampled normal-state text roles had a minimum contrast of 5.47:1 on the final
palette. This measurement excludes rainbow lettering and does not establish
complete WCAG conformance. Keyboard link focus, absence of focus underlines,
and the rainbow animation name were checked. Desktop, mobile and SS search
screenshots were inspected.

Automated viewer tests also cover language/difficulty switching, URL state,
previews, detail links and the reviewed monster-area groups. The existing layout
checks cover sticky identities, scrolling labels, search normalization and
reduced-motion CSS. See [the area review](monster-area-review.md) for source
references and the boundary between chart groups and quest spawn locations.

Reference: [WCAG text contrast](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum).
