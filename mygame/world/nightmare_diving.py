"""
Nightmare LPmud Underwater Diving, Shipwreck Salvage & Doubloon Engine.

Implements:
1. Brass Diving Helmets & Weighted Sea Suits ('divingsuit').
2. Submerging into underwater shipwrecks and coral reefs ('dive <depth>').
3. Seabed wreckage and pearl oyster salvage ('salvagedepths').
4. Barnacle-crusted sea chest prying ('prychest') yielding pirate doubloons.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

SALVAGE_FINDS = [
    {
        "name": "Barnacle-Crusted Pirate Sea Chest",
        "is_chest": True,
        "doubloons": 95,
        "desc": "A heavy oak sea chest bound in verdigris-crusted brass, sealed with pitch and marine barnacles."
    },
    {
        "name": "Giant Iridescent Pearl Oyster",
        "is_chest": False,
        "doubloons": 45,
        "desc": "A heavy, corrugated bivalve shell hiding a lustrous teardrop saltwater pearl."
    },
    {
        "name": "Antique Brass Navigation Quadrant",
        "is_chest": False,
        "doubloons": 60,
        "desc": "An ornate engraved nautical instrument salvaged from a sunken captain's stateroom."
    }
]


def create_diving_gear(location, name="Heavy Brass Diving Helmet"):
    """Spawns underwater breathing diving gear."""
    gear = create_object(Object, key=name, location=location)
    gear.db.is_diving_gear = True
    gear.db.desc = "A spherical brass diver's helmet fitted with thick round glass portholes and a threaded air collar."
    return gear


def equip_diving_suit(caller):
    """Dons or activates weighted diving gear."""
    has_gear = any(
        getattr(obj.db, "is_diving_gear", False) or "diving" in obj.key.lower()
        for obj in caller.contents
    )

    if not has_gear:
        return False, "You need a Brass Diving Helmet in your pack to dive beneath the waves! ('divingsuit')"

    caller.db.is_diving_equipped = True
    caller.msg(
        "\n|C[DIVING GEAR EQUIPPED]|n You tighten the heavy collar bolts and lower the brass diving helmet!\n"
        "The world mutes into the rhythmic whoosh of air through your copper valve. You can breathe underwater!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} bolts on a heavy brass diving helmet, ready to plunge into the oceanic abyss.",
            exclude=[caller]
        )
    return True, "Diving gear equipped."


def dive_into_depths(caller, depth="deep"):
    """Submerges into the undersea world."""
    if not getattr(caller.db, "is_diving_equipped", False):
        return False, "You cannot dive without donning diving gear first! ('divingsuit')"

    room = caller.location
    caller.db.is_submerged = True

    caller.msg(
        f"\n|C*GLUB-GLUB-SPLASH!*|n Weighted lead boots pull you beneath the surface!\n"
        "Shafts of turquoise sunlight filter through swaying kelp forests as you touch down on the sandy seabed.\n"
        "|yUse 'salvagedepths' to search for sunken wreckage and lost pirate chests!|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} steps off into the open water, sinking gracefully into the oceanic depths in brass gear.",
            exclude=[caller]
        )
    return True, "Submerged."


def salvage_seabed(caller):
    """Searches the ocean floor and shipwreck ruins for salvageable treasures."""
    if not getattr(caller.db, "is_submerged", False):
        return False, "You must dive beneath the waves first! ('dive')"

    data = random.choice(SALVAGE_FINDS)
    salvage = create_object(Object, key=data["name"], location=caller)
    salvage.db.is_salvage = True
    salvage.db.is_chest = data["is_chest"]
    salvage.db.doubloons = data["doubloons"]
    salvage.db.is_pried = False
    salvage.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[SALVAGE DISCOVERY]|n Sifting through tangled sea anemones and rotting galleon ribs,\n"
        f"your gloved hands discover a |w{salvage.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} dredges through the seabed sand and hoists up a {salvage.key}!",
            exclude=[caller]
        )
    return True, f"Salvaged {salvage.key}."


def pry_open_chest(caller, target_name=""):
    """Pries open a salvaged barnacle sea chest."""
    chest = None
    for obj in caller.contents:
        if getattr(obj.db, "is_chest", False) and not getattr(obj.db, "is_pried", False):
            if not target_name or target_name.lower() in obj.key.lower():
                chest = obj
                break

    if not chest:
        return False, "You do not have a sealed salvaged sea chest in your pack to pry open."

    doubloons = getattr(chest.db, "doubloons", 80)
    chest.db.is_pried = True
    chest.key = f"Pried Open {chest.key}"
    caller.db.coins = (getattr(caller.db, "coins", 0) or 0) + doubloons

    caller.msg(
        f"\n|Y*CRUNCH!*|n You drive an iron prybar beneath the brass clasp and crack the lid open!\n"
        f"Brine pours out, revealing gleaming Spanish gold doubloons!\n"
        f"You recover |w{doubloons} gold coins|n from the sunken chest!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} pops the rusted brass lid of a sunken sea chest, collecting sparkling doubloons!",
            exclude=[caller]
        )
    return True, "Chest pried open."

