"""
Fishing System for Eldoria
Comprehensive fishing tables, biomes, fish species, weights, and rewards.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object


# =============================================================================
# BIOME FISHING TABLES
# =============================================================================

BIOME_TABLES = {
    "river": {
        "common": [
            ("Rainbow River Trout", 1.5, 4.0, 10, 18),
            ("Speckled Brook Char", 1.0, 3.0, 8, 14),
            ("River Chub", 0.5, 2.0, 6, 12),
        ],
        "uncommon": [
            ("Silver Salmon", 4.0, 12.0, 18, 30),
            ("Striped River Perch", 2.0, 5.0, 12, 20),
        ],
        "rare": [
            ("Golden River Sturgeon", 15.0, 45.0, 30, 60),
        ],
        "junk": [
            ("Water-Logged Leather Boot", 1.0, 2.0, 10, 12),
            ("Tangle of River Kelp", 0.5, 1.0, 12, 24),
        ]
    },
    "ocean": {
        "common": [
            ("Striped Red Snapper", 2.0, 6.0, 12, 22),
            ("Spotted Sea Mackerel", 1.5, 4.5, 10, 18),
            ("Bluefin Herring", 0.8, 2.5, 7, 14),
        ],
        "uncommon": [
            ("Giant Sea Bass", 8.0, 25.0, 24, 42),
            ("Silverfang Barracuda", 6.0, 18.0, 20, 36),
        ],
        "rare": [
            ("Great Leviathan-Fin Tuna", 40.0, 120.0, 48, 80),
        ],
        "junk": [
            ("Barnacled Rum Bottle with Message", 1.0, 1.5, 8, 10),
            ("Driftwood Float with Rusted Hook", 0.5, 1.5, 6, 12),
        ]
    },
    "swamp": {
        "common": [
            ("Slime-Whiskered Catfish", 3.0, 9.0, 14, 26),
            ("Mud Prowler Gudgeon", 1.0, 3.0, 8, 14),
        ],
        "uncommon": [
            ("Mire Leech-Eel", 2.0, 7.0, 16, 32),
            ("Bulbous Swamp Toadfish", 2.5, 6.0, 10, 18),
        ],
        "rare": [
            ("Three-Eyed Marsh Lurker", 12.0, 30.0, 26, 48),
        ],
        "junk": [
            ("Petrified Swamp Root", 2.0, 5.0, 12, 20),
            ("Corroded Dagger Shard", 0.5, 1.0, 6, 8),
        ]
    },
    "subterranean": {
        "common": [
            ("Blind Cave Tetra", 0.3, 1.2, 4, 8),
            ("Pale Sludge Loach", 0.8, 2.5, 6, 12),
        ],
        "uncommon": [
            ("Ghostly Spectral Guppy", 0.5, 2.0, 5, 10),
            ("Cave Armored Catfish", 3.0, 8.0, 12, 22),
        ],
        "rare": [
            ("Ancient Sunken Lockbox", 5.0, 10.0, 10, 12),
        ],
        "junk": [
            ("Sewer Slime Glob", 0.2, 0.5, 4, 6),
            ("Rusted Skeleton Key", 0.1, 0.3, 3, 5),
        ]
    },
    "fey": {
        "common": [
            ("Star-Tail Minnow", 0.4, 1.5, 5, 9),
            ("Iridescent Rainbow Guppy", 0.5, 1.8, 6, 11),
        ],
        "uncommon": [
            ("Shimmering Moon-Carp", 3.0, 8.0, 12, 22),
            ("Silverleaf Darter", 1.2, 3.5, 8, 15),
        ],
        "rare": [
            ("Queen's Golden Lotus Fish", 5.0, 14.0, 16, 28),
        ],
        "junk": [
            ("Glowing Water Lily Bud", 0.2, 0.5, 4, 6),
            ("Polished River Amber", 0.3, 0.8, 2, 4),
        ]
    }
}


def get_room_biome(room):
    """
    Determines the fishing water biome for a given room.
    Returns biome string or None if room has no fishable water.
    """
    key = room.key.lower()

    if any(w in key for w in ["river", "stream", "crossing", "rapids"]):
        return "river"
    if any(w in key for w in ["dock", "promenade", "cove", "wreck", "siren", "ocean", "beach", "cavern", "grotto"]):
        return "ocean"
    if any(w in key for w in ["mire", "marsh", "swamp", "bog"]):
        return "swamp"
    if any(w in key for w in ["cistern", "ossuary", "sewer", "warren"]):
        return "subterranean"
    if any(w in key for w in ["glade", "fey", "spring", "tree", "willow"]):
        return "fey"

    return None


def catch_fish(caller, room, rod=None, bait=None):
    """
    Pulls a fish or item from the room's biome table, adjusted by rod & bait quality.
    Creates and places the caught object into caller's inventory.
    """
    biome = get_room_biome(room)
    if not biome:
        return None, "There is no fishable water here."

    table = BIOME_TABLES[biome]

    # Calculate rarity chances
    # Base: 60% common, 25% uncommon, 5% rare, 10% junk
    rarity_roll = random.random() * 100

    # Bait bonuses
    bonus = 0
    if bait:
        bait_name = bait.key.lower()
        if "beetle" in bait_name or "grub" in bait_name:
            bonus += 15
        elif "squid" in bait_name or "breadcrumb" in bait_name:
            bonus += 10
        elif "worm" in bait_name:
            bonus += 5

    # Rod bonuses
    if rod:
        rod_name = rod.key.lower()
        if "fey" in rod_name or "ghost-iron" in rod_name:
            bonus += 20
        elif "reinforced" in rod_name or "brass" in rod_name:
            bonus += 10

    # Determine tier
    if rarity_roll + bonus >= 100:
        pool = table["rare"]
        tier = "rare"
    elif rarity_roll + bonus >= 70:
        pool = table["uncommon"]
        tier = "uncommon"
    elif rarity_roll >= 15:
        pool = table["common"]
        tier = "common"
    else:
        pool = table["junk"]
        tier = "junk"

    choice = random.choice(pool)
    name, min_w, max_w, min_l, max_l = choice

    weight = round(random.uniform(min_w, max_w), 1)
    length = round(random.uniform(min_l, max_l), 1)

    is_lockbox = "lockbox" in name.lower()
    is_junk = tier == "junk"

    if is_lockbox:
        item = create_object(
            Object,
            key=f"{name} ({weight} lbs)",
            location=caller,
            aliases=["lockbox", "box", "treasure box"],
            tags=["eldoria_world"]
        )
        item.db.desc = (
            f"An ancient water-sealed iron lockbox covered in river moss and mineral crust. "
            f"It rattles with heavy coins inside!"
        )
        item.db.is_lockbox = True
    elif is_junk:
        item = create_object(
            Object,
            key=f"{name}",
            location=caller,
            aliases=["junk", "debris", name.lower()],
            tags=["eldoria_world"]
        )
        item.db.desc = f"A waterlogged curiosity hauled up from the depths, weighing about {weight} lbs."
    else:
        item = create_object(
            Object,
            key=f"{name} ({weight} lbs, {length} in)",
            location=caller,
            aliases=["fish", name.lower(), name.split()[-1].lower()],
            tags=["eldoria_world"]
        )
        item.db.desc = (
            f"A freshly caught {name}, measuring {length} inches long and weighing {weight} lbs. "
            f"Looks plump, fresh, and ready to be cooked at a hearth fire!"
        )
        item.db.is_fish = True
        item.db.cookable = True
        item.db.raw_fish_name = name
        item.db.weight = weight
        item.db.length = length

    return item, tier

