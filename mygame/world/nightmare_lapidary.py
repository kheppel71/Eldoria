"""
Nightmare LPmud Lapidary Gemcutting, Faceting & Jeweled Filigree Engine.

Implements:
1. Rough Gemstones:
   - Rough Ruby Nodule
   - Cloudy Raw Sapphire
   - Uncut Forest Emerald
2. Lapidary Wheel Faceting ('facetgem'):
   - Brilliant-Cut Star Ruby
   - Flawless Deep Ocean Sapphire
   - Radiant Emerald Cut Gem
3. Precious Jeweled Filigree Setting ('craftjewelry'):
   - Filigree Star-Ruby Signet Ring
   - Deep Ocean Sapphire Pendant
   - Gilded Emerald Crown Circlet
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

GEM_CATALOG = {
    "ruby": {
        "raw_name": "Rough Ruby Nodule",
        "cut_name": "Brilliant-Cut Star Ruby",
        "value": 60,
        "desc": "A masterfully faceted blood-red ruby whose polished facets cast vivid crimson sparkles."
    },
    "sapphire": {
        "raw_name": "Cloudy Raw Sapphire",
        "cut_name": "Flawless Deep Ocean Sapphire",
        "value": 75,
        "desc": "An intensely blue faceted sapphire capturing the deep azure radiance of oceanic depths."
    },
    "emerald": {
        "raw_name": "Uncut Forest Emerald",
        "cut_name": "Radiant Emerald Cut Gem",
        "value": 70,
        "desc": "A rectangular step-cut green beryl gemstone shimmering with tranquil forest vitality."
    }
}

JEWELRY_RECIPES = {
    "ring": {
        "name": "Filigree Star-Ruby Signet Ring",
        "slot": "ring",
        "cost": 30,
        "desc": "An ornate sterling silver filigree ring holding a blazing Brilliant-Cut Star Ruby."
    },
    "pendant": {
        "name": "Deep Ocean Sapphire Pendant",
        "slot": "neck",
        "cost": 45,
        "desc": "A delicate platinum necklace suspending a Flawless Deep Ocean Sapphire."
    },
    "circlet": {
        "name": "Gilded Emerald Crown Circlet",
        "slot": "head",
        "cost": 60,
        "desc": "A slender coronet of twisted gold wire centered with a Radiant Emerald Cut Gem."
    }
}


def create_rough_gem(location, gem_type="ruby"):
    """Spawns an uncut mineral nodule."""
    data = GEM_CATALOG.get(gem_type, GEM_CATALOG["ruby"])
    gem = create_object(Object, key=data["raw_name"], location=location)
    gem.db.is_gem = True
    gem.db.gem_type = gem_type
    gem.db.is_faceted = False
    gem.db.desc = f"An unpolished rough mineral crystal waiting for a lapidary wheel."
    return gem


def facet_rough_gemstone(caller, target_name=""):
    """Grinds and facets a rough mineral crystal at a lapidary wheel."""
    gem = None
    for obj in caller.contents:
        if getattr(obj.db, "is_gem", False) and not getattr(obj.db, "is_faceted", False):
            if not target_name or target_name.lower() in obj.key.lower():
                gem = obj
                break

    if not gem:
        return False, "You do not have any uncut rough gemstones in your pack to facet!"

    gtype = gem.db.gem_type
    data = GEM_CATALOG[gtype]

    gem.key = data["cut_name"]
    gem.db.is_faceted = True
    gem.db.value = data["value"]
    gem.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[LAPIDARY WHEEL]|n Pressing the mineral against the diamond-grit grinding lap,\n"
        f"you cut fifty-seven perfect optical facets into the stone!\n"
        f"You produce a breathtaking |w{gem.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} spins the diamond lapidary wheel, polishing a dazzling {gem.key}!",
            exclude=[caller]
        )
    return True, f"Faceted {gem.key}."


def craft_jeweled_filigree(caller, piece_type="ring"):
    """Sets a faceted gem into silver or gold filigree jewelry."""
    key = piece_type.strip().lower()
    matched = next((k for k in JEWELRY_RECIPES if key in k), None)

    if not matched:
        opts = ", ".join(JEWELRY_RECIPES.keys())
        return False, f"Unknown jewelry setting '{piece_type}'. Options: {opts}"

    recipe = JEWELRY_RECIPES[matched]

    # Look for faceted gem
    gem = None
    for obj in caller.contents:
        if getattr(obj.db, "is_gem", False) and getattr(obj.db, "is_faceted", False):
            gem = obj
            break

    if not gem:
        return False, "You need a polished, faceted gemstone in your pack to set into jewelry! Use 'facetgem' first."

    gem.delete()
    jewelry = create_object(Object, key=recipe["name"], location=caller)
    jewelry.db.is_jewelry = True
    jewelry.db.slot = recipe["slot"]
    jewelry.db.desc = recipe["desc"]

    caller.msg(
        f"\n|G[MASTER JEWELER SUCCESS]|n Using jewelers' pliers and gold solder,\n"
        f"you secure the dazzling faceted stone into intricate wire prongs!\n"
        f"You fashion a breathtaking |w{jewelry.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} solders delicate filigree metalwork, completing a magnificent {jewelry.key}!",
            exclude=[caller]
        )
    return True, f"Crafted {jewelry.key}."

