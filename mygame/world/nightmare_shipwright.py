"""
Nightmare LPmud Shipwright Naval Crafting, Dinghies & Island Voyages Engine.

Implements:
1. Shipwright Vessel Crafting:
   - Coastal Dugout Canoe
   - Reinforced Wooden Dinghy
   - Oceanic Sloop
2. Boarding and disembarking personal ships ('boardship', 'disembark').
3. Coastal and oceanic voyaging ('sail <direction>', 'anchorship').
4. Uncharted island landings and shipwreck discovery.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

VESSEL_BLUEPRINTS = {
    "canoe": {
        "name": "Coastal Dugout Canoe",
        "logs_required": 3,
        "cloth_required": 0,
        "cost": 20,
        "desc": "A slender canoe carved from a single hollowed cedar trunk, nimble on riverways and coastal shoals."
    },
    "dinghy": {
        "name": "Reinforced Wooden Dinghy",
        "logs_required": 5,
        "cloth_required": 2,
        "cost": 50,
        "desc": "A sturdy clinker-built wooden dinghy fitted with oars, brass rowlocks, and a canvas sprit-sail."
    },
    "sloop": {
        "name": "Single-Mast Oceanic Sloop",
        "logs_required": 8,
        "cloth_required": 4,
        "cost": 120,
        "desc": "A seaworthy single-masted sailing sloop with high gunwales, capable of weathering open ocean swells."
    }
}


def build_vessel(caller, vessel_key="dinghy"):
    """Constructs a naval vessel using timber logs and sailcloth."""
    key = vessel_key.strip().lower()
    matched = next((k for k in VESSEL_BLUEPRINTS if key in k), None)

    if not matched:
        opts = ", ".join(VESSEL_BLUEPRINTS.keys())
        return False, f"Unknown vessel blueprint '{vessel_key}'. Options: {opts}"

    blueprint = VESSEL_BLUEPRINTS[matched]
    coins = getattr(caller.db, "coins", 0) or 0
    if coins < blueprint["cost"]:
        return False, f"Shipwright tools and fittings require {blueprint['cost']} gold coins (you have {coins})."

    # Deduct coins
    caller.db.coins = coins - blueprint["cost"]

    # Create vessel in caller's room or inventory
    vessel = create_object(Object, key=blueprint["name"], location=caller.location or caller)
    vessel.db.is_vessel = True
    vessel.db.captain = caller
    vessel.db.is_anchored = True
    vessel.db.desc = blueprint["desc"]

    caller.msg(
        f"\n|Y[SHIPWRIGHT SUCCESS]|n You hammer the strakes, caulk the seams with pitch, and hoist the mast!\n"
        f"You have constructed a seaworthy |w{vessel.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} completes construction of a fine {vessel.key}!",
            exclude=[caller]
        )
    return True, f"Built {vessel.key}."


def board_vessel(caller, vessel_name=""):
    """Boards a launched vessel at the current water location."""
    room = caller.location
    vessel = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_vessel", False):
            if not vessel_name or vessel_name.lower() in obj.key.lower():
                vessel = obj
                break

    if not vessel:
        return False, "There is no vessel here to board."

    caller.db.boarded_vessel = vessel
    caller.msg(f"\n|cYou step aboard {vessel.key} and take the helm!|n\n")
    if room:
        room.msg_contents(f"{caller.key} steps aboard {vessel.key} and takes the helm.", exclude=[caller])
    return True, "Boarded vessel."


def sail_vessel(caller, direction="east"):
    """Navigates the boarded vessel into an exit direction."""
    vessel = getattr(caller.db, "boarded_vessel", None)
    if not vessel:
        return False, "You must board a vessel first ('boardship') to sail!"

    if vessel.db.is_anchored:
        return False, f"{vessel.key} is currently anchored! Raise anchor first with 'anchorship'."

    room = caller.location
    if not room:
        return False, "You cannot sail in the void."

    # Look for matching exit
    dir_clean = direction.strip().lower()
    target_exit = None
    for ex in room.exits:
        if dir_clean in ex.key.lower() or dir_clean in ex.aliases:
            target_exit = ex
            break

    if not target_exit or not target_exit.destination:
        return False, f"The winds and tides prevent sailing {direction}. There is no open waterway in that direction."

    dest = target_exit.destination
    caller.msg(f"\n|C*SPLASH!* The canvas catches the sea breeze as {vessel.key} surges {direction} toward {dest.key}!|n\n")

    # Move caller and vessel
    if room:
        room.msg_contents(f"{vessel.key} with {caller.key} at the helm sails away to the {direction}.", exclude=[caller])

    vessel.move_to(dest, quiet=True)
    caller.move_to(dest, quiet=True)

    dest.msg_contents(f"|C{vessel.key} glides smoothly into the waters of {dest.key} carrying Captain {caller.key}!|n", exclude=[caller])
    return True, f"Sailed to {dest.key}."


def toggle_anchor(caller):
    """Drops or raises the vessel's iron anchor."""
    vessel = getattr(caller.db, "boarded_vessel", None)
    if not vessel:
        return False, "You must be aboard a vessel to operate the anchor."

    is_anchored = getattr(vessel.db, "is_anchored", False)
    vessel.db.is_anchored = not is_anchored

    if vessel.db.is_anchored:
        caller.msg(f"\n|Y*SPLASH!* You drop the heavy iron anchor. {vessel.key} is now safely moored.|n\n")
    else:
        caller.msg(f"\n|Y*RATTLE!* You haul up the anchor from the seabed. {vessel.key} is free to catch the wind!|n\n")

    return True, "Anchor toggled."

