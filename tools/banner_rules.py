"""Named Ephinea banner items, reviewed 2026-09-19.

Source: https://wiki.pioneer2.net/w/Banners (revision 38974).
Main-server charts only: Classic-only Agito (1975), technique disks and the
generic 90-Hit rare-weapon rule are intentionally not item highlights.
"""

WEAPONS_BY_HIT = {
    0: (
        "DB's Saber (3064)", "DB's Saber (3077)", "Evil Curst",
        "Flowen's Sword (3073)", "Flowen's Sword (3077)", "Lavis Cannon",
        "Madam's Parasol", "Nei's Claw", "Sealed J-Sword", "Yasha",
        "Angel Harp", "Handgun: Guld", "Handgun: Milla", "Heaven Punisher",
        "NUG2000-Bazooka", "Bluefull Card", "Greenill Card", "Oran Card",
        "Pinkal Card", "Prophets of Motav", "Psycho Wand", "Purplenum Card",
        "Redria Card", "Skyly Card", "Viridia Card", "Whitill Card", "Yellowboze Card",
    ),
    20: ("Galatine", "Lame d'Argent", "Heaven Striker"),
    30: ("Daylight Scar", "Vivienne", "Cannon Rouge", "Frozen Shooter", "Rambling May"),
    40: (
        "Asteron Belt", "Girasole", "Guren", "Monkey King Bar", "Shouren",
        "Slicer of Fanatic", "Twin Blaze", "Yunchang", "Zanba", "Holy Ray",
        "L&K38 Combat", "Ophelie Seize", "Spread Needle", "Yasminkov 9000M",
    ),
    50: (
        "Chain Sawd", "Demolition Comet", "Diska of Braveman", "Flowen's Sword (3084)",
        "Red Sword", "Sange", "Tyrell's Parasol", "Vjaya", "Yamigarasu",
        "M&A60 Vise", "Panzer Faust", "Yasminkov 7000V", "Clio", "Guardianna",
    ),
}

NON_WEAPONS = (
    "Red Ring", "S-Parts ver2.01",
    "Heart of Ancient Saber", "Heart of Angel Harp", "Heart of Blade Dance",
    "Heart of Chameleon Scythe", "Heart of Crazy Tune", "Heart of Daisy Chain",
    "Heart of DB's Saber", "Heart of Delsaber's Buster", "Heart of Diska of Liberator",
    "Heart of Egg Blaster", "Heart of Flamberge", "Heart of Izmaela",
    "Heart of Laconium Axe", "Heart of Lollipop", "Heart of Partisan of Lightning",
    "Heart of Plantain Huge Fan", "Heart of Rabbit Wand", "Heart of Rianov 303SNR",
    "Heart of Ruby Bullet", "Heart of Samba Maracas", "Heart of Sorcerer's Cane",
    "Heart of Soul Banish", "Heart of Suppressed Gun", "Heart of Tension Blaster",
    "Heart of The Sigh of a God", "Heart of TypeDS/D.Saber", "Heart of TypeSS/Swords",
    "Heart of Yasminkov 9000M", "Anniv. Platinum Badge", "Book of Hitogata",
    'Magic Stone "Iritista"', 'Parasitic Gene "Flow"', "Syncesta",
)

WEAPON_HIT = {name: hit for hit, names in WEAPONS_BY_HIT.items() for name in names}


def banner_hit(name, kind):
    """Return minimum untekked Hit (0 = no requirement), or no named banner."""
    if name in NON_WEAPONS:
        return 0
    if kind == "monsters":
        return WEAPON_HIT.get(name)
    return None
