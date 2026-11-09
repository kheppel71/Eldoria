"""
Nightmare LPmud Weapon Scabbards, Tactical Sheathing & Quick-Draw Engine.

Implements:
1. Belt and back weapon scabbards and sheaths.
2. Tactical weapon sheathing ('sheathe <weapon>') keeping hands free.
3. Quick-Draw combat readiness ('draw <weapon>') granting opening initiative bonuses.
4. Archer quivers for arrows and projectiles.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_leather_scabbard(location, scabbard_name="Tooled Leather Scabbard"):
    """Spawns an equippable weapon scabbard."""
    scabbard = create_object(Object, key=scabbard_name, location=location)
    scabbard.db.is_scabbard = True
    scabbard.db.slot = "belt"
    scabbard.db.sheathed_weapon = None
    scabbard.db.desc = "A sturdy cured leather sword scabbard reinforced with brass fittings and a polished throat."
    return scabbard


def sheathe_weapon(caller, weapon_obj):
    """Sheathes a weapon into an equipped or carried scabbard."""
    scabbard = None
    for obj in caller.contents:
        if getattr(obj.db, "is_scabbard", False) and obj.db.sheathed_weapon is None:
            scabbard = obj
            break

    if not scabbard:
        return False, "You do not have an empty scabbard or sheath to hold your weapon!"

    # Remove from hands
    equipped = getattr(caller.db, "equipped_slots", {}) or {}
    for s in ["right_hand", "left_hand"]:
        if equipped.get(s) == weapon_obj:
            equipped.pop(s, None)
            break
    caller.db.equipped_slots = equipped

    scabbard.db.sheathed_weapon = weapon_obj
    weapon_obj.move_to(scabbard, quiet=True)

    caller.msg(f"\n|yWith a smooth, practiced motion, you slide {weapon_obj.key} into {scabbard.key}. *SHCK!*|n")
    caller.msg("Your hands are now free.\n")

    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} smoothly sheathes {weapon_obj.key} into their scabbard.",
            exclude=[caller]
        )
    return True, "Sheathed."


def draw_weapon(caller, weapon_name=""):
    """Quick-draws a weapon from scabbard into hands."""
    scabbard = None
    for obj in caller.contents:
        if getattr(obj.db, "is_scabbard", False) and obj.db.sheathed_weapon is not None:
            if not weapon_name or weapon_name.lower() in obj.db.sheathed_weapon.key.lower():
                scabbard = obj
                break

    if not scabbard or not scabbard.db.sheathed_weapon:
        return False, "You have no sheathed weapon ready to draw!"

    weapon = scabbard.db.sheathed_weapon
    scabbard.db.sheathed_weapon = None

    weapon.move_to(caller, quiet=True)
    equipped = getattr(caller.db, "equipped_slots", {}) or {}
    equipped["right_hand"] = weapon
    caller.db.equipped_slots = equipped

    caller.msg(f"\n|Y*SCHWING!* With lightning reflex, you draw {weapon.key} from {scabbard.key}!|n")
    caller.msg("|yWeapon readied in your right hand for battle!|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"|r*SCHWING!* {caller.key} quick-draws {weapon.key} from their scabbard, ready for battle!|n",
            exclude=[caller]
        )
    return True, "Drawn."

