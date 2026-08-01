# BB Drop Table User Guide

This viewer shows monster and box drops for Phantasy Star Online: Blue Burst (Episodes 1, 2, and 4). The data comes from the Ephinea server.

## Coverage

- **Episodes:** 1, 2, and 4
- **Difficulties:** Normal, Hard, Very Hard, and Ultimate
- **Drop types:** Monsters and boxes
- **Languages:** English, Japanese, and Chinese

## Features

### Language selection

Select `EN`, `日本語`, or `中文` to change the interface language and the displayed monster and item names.

You can also set the language in the URL, for example `?lang=zh`.

### Difficulty selection

Select `Normal`, `Hard`, `Very Hard`, or `Ultimate` to change the difficulty.

- Normal through Very Hard use the standard monster names.
- Ultimate uses alternate monster names, such as Hildelt instead of Hildebear.

You can also set the difficulty in the URL, for example `?diff=Ultimate`.

### Drop type

Select `Monsters` or `Boxes` to switch between enemy and box drops.

- **Monsters:** Items dropped by defeated enemies
- **Boxes:** Items found in area boxes

### Episode filter

Select `All`, `Ep.1`, `Ep.2`, or `Ep.4` to filter the table by episode.

- **Episode 1:** Forest, Caves, Mines, and Ruins; shared by DC, NGC, and BB
- **Episode 2:** Temple, Spaceship, Central Control Area, Seabed, and Control Tower; shared by NGC and BB
- **Episode 4:** Crater and Desert areas; exclusive to BB

### Drop-rate format

Select `%` or `Fraction` to change the probability format.

- **%:** Percentage, such as `0.45%`
- **Fraction:** The game's underlying fractional probability, such as `1/222`

### Search

Enter text in the search box to filter monster and item names as you type. Matching item cells are highlighted.

### Table layout

| Column | Contents |
| --- | --- |
| First column | Monster or box name and its overall drop rate |
| Remaining columns | The item and probability for each of the ten Section IDs |

A Section ID is assigned when a character is created and determines which rare items can drop. A single Section ID cell may contain several independent drops. The viewer displays each item with its own probability. For example, an Ultimate Episode 4 area box may list both ordinary equipment and a `Photon Crystal`; these are separate drops, not alternate localized names for one item.

### URL parameters

Parameters can be combined, as in `?lang=zh&diff=Ultimate`.

| Parameter | Values | Purpose |
| --- | --- | --- |
| `lang` | `en`, `ja`, or `zh` | Interface language |
| `diff` | `Normal`, `Hard`, `Very Hard`, or `Ultimate` | Difficulty |

## Blue Burst-specific content

Blue Burst is the most comprehensive version in this viewer. Compared with NGC, it adds:

- **Episode 4:** Every Crater and Desert enemy, including Zu, Dorphon, the Goran family, and the three major bosses
- **Box-drop data:** Area-specific box contents
- **Fractional drop rates:** The game's underlying probability representation
- **Ephinea-specific balance:** Drop rates adjusted by the Ephinea team, which may differ from official servers

## Data sources

English and Japanese BB data is scraped from the [Ephinea Drop Charts](https://ephinea.pioneer2.net/drop-charts). Chinese data is generated from the game client's `unitxt` files.
