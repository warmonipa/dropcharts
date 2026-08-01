# NGC Drop Table User Guide

This viewer shows monster drops for the Nintendo GameCube release of Phantasy Star Online (Episodes 1 and 2).

## Coverage

- **Episodes:** Episode 1 (Forest through Ruins) and Episode 2 (Temple through Control Tower)
- **Difficulties:** Normal, Hard, Very Hard, and Ultimate
- **Drop types:** Monsters only; box drops are not available
- **Languages:** English, Japanese, and Chinese

## Features

### Language selection

Select `EN`, `日本語`, or `中文` to change the interface language and the displayed monster and item names.

You can also set the language in the URL, for example `?lang=ja`.

### Difficulty selection

Select `Normal`, `Hard`, `Very Hard`, or `Ultimate` to view the corresponding drop data. Ultimate uses alternate monster names, such as Bartle instead of Booma.

You can also set the difficulty in the URL, for example `?diff=Ultimate`.

### Episode filter

Select `All`, `Ep.1`, or `Ep.2` to filter the table by episode.

- **Episode 1:** Areas inherited from the Dreamcast version, from Forest through Ruins
- **Episode 2:** Areas added for the GameCube release, from Temple through Control Tower

### Search

Enter text in the search box to filter monster and item names as you type. Search works across languages, so Japanese queries can also match localized entries.

### Drop rates

NGC drop rates are displayed as percentages, such as `1.5625%`.

### Table layout

| Column | Contents |
| --- | --- |
| First column | Monster name and its overall drop rate |
| Remaining columns | The item and probability for each of the ten Section IDs |

The first column remains frozen while the Section ID columns scroll horizontally. There is
no duplicate name column at the right edge. Area headings remain centered in the visible
scrolling region, including on phones and tablets.

## GameCube-specific content

Compared with the Dreamcast version, the GameCube release adds complete Episode 2 monster and drop data, including:

- **Episode 2 enemies:** Merillia, Gi Gue, Sinow Zoa, Delbiter, Olga Flow, and others
- **Episode 2 items:** Additional rare weapons and armor
- **AGITO variants:** Year- and smith-specific versions such as the 1975 Dousetsu and counterfeit 1977 Jou'un models

The source data mixes Japanese and English item names. It also contains spellings that differ slightly from BB, such as `KALADGOLG` instead of `KALADBOLG`; the viewer preserves those source-specific forms.
