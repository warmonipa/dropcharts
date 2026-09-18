# Monster area review

Reviewed on 2026-09-19 against the Ephinea Wiki:

- [Monster lists](https://wiki.pioneer2.net/w/Monsters)
- [Episode 2 groups](https://wiki.pioneer2.net/w/Template:Episode2Monsters)
- [Episode 4 groups](https://wiki.pioneer2.net/w/Template:Episode4Monsters)
- [Crater](https://wiki.pioneer2.net/w/Crater)
- [Subterranean Desert](https://wiki.pioneer2.net/w/Subterranean_Desert)
- [Recon](https://wiki.pioneer2.net/w/Recon)
- [Merikle](https://wiki.pioneer2.net/w/Merikle) and
  [Mericus](https://wiki.pioneer2.net/w/Mericus)

## Grouping convention

These are drop-chart groups, not an exhaustive list of quest spawn locations.
Bosses remain at the end of their associated area, as in the Wiki monster lists;
their separate boss arenas are not additional chart groups. CCA minibosses stay
in Central Control Area, even when they also occur in Control Tower quests.
The Tower group contains Ill Gill, Del Lily and Epsilon.

Episode 1's Forest, Cave, Mine and Ruins groups were checked, including rare
enemies, split enemies and Ultimate forms. No area reassignment was needed.
Episode 2's existing groups match the Wiki after moving Recon to Seabed.

Episode 4 needs a shared group: Sand Rappy, Del Rappy, Satellite Lizard, Yowie,
Zu and Pazuzu occur in both Crater and Subterranean Desert. They now appear
under `Crater / Subterranean Desert`. Crater-only rows precede this group;
desert rows and the associated bosses follow it. Each drop row appears once.

The chart is not a complete bestiary. This review does not add absent rows
such as Recobox or Dubwitch, nor infer any drops from their area membership.
Ephinea's statistics and drop rates are not copied into the legacy versions.

## Legacy names and verification

NGC's English file still contains Japanese monster names in lower difficulties.
Area lookup now accepts these aliases from the repository's name dictionary,
plus its existing spelling variants. A trailing question mark on legacy boss
names is ignored for grouping only; displayed names and drop contents remain
unchanged. Missing Ultimate aliases such as Hildelt/Hildetorr in VR Temple
were also added.

`tests/test_viewer.cjs` checks all BB rows against the reviewed groups across
three languages and four difficulties. It also checks every stored monster row
in BB/DC/NGC for an explicit area match and detects split/repeated area groups.
The data alignment and name validators verify the generated language files.
