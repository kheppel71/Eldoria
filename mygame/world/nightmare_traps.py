"""
Nightmare LPmud Hunting Traps, Bear Traps & Caltrops System.

Implements:
1. Concealed Room Traps ('settrap beartrap/snare').
2. Trigger mechanics inflicting heavy leg limb damage and pinning foes.
3. Small game snaring for wilderness survival meat and pelt harvesting.
4. Combat Caltrops punishing fleeing or charging opponents.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object


def set_room_trap(caller, trap_type, trap_item):
    """Arms and conceals a trap in the current room."""
    loc = caller.location
    if not loc:
        return False, "You cannot set a trap in the void."

    t_type = trap_type.lower().strip()
    if t_type not in ["beartrap", "bear trap", "snare", "tripwire"]:
        return False, f"Unknown trap type '{trap_type}'. Available: beartrap, snare."

    traps = getattr(loc.db, "room_traps", []) or []

    trap_record = {
        "type": "beartrap" if "bear" in t_type else "snare",
        "setter_id": caller.id,
        "setter_name": caller.key,
        "damage": (25, 45) if "bear" in t_type else (5, 12)
    }

    traps.append(trap_record)
    loc.db.room_traps = traps
    trap_item.delete()

    caller.msg(f"\n|yYou carefully prime the coiled iron spring, concealing the {trap_record['type']} beneath leaves and dirt.|n")
    if loc:
        loc.msg_contents(
            f"{caller.key} kneels down and conceals something beneath the forest floor.",
            exclude=[caller]
        )
    return True, "Trap set."


def spring_room_traps(victim, room):
    """Triggers any concealed traps when a character moves or steps unwarily."""
    if not room or not hasattr(room, "db"):
        return False

    traps = getattr(room.db, "room_traps", []) or []
    if not traps:
        return False

    # Trigger the first armed trap
    trap = traps.pop(0)
    room.db.room_traps = traps

    if trap["type"] == "snare":
        # Snared small game!
        game = create_object(Object, key="Snared Forest Hare", location=room)
        game.db.desc = "A plump wild hare captured in a hempen wire snare."
        game.db.value = 10
        room.msg_contents(
            f"|y*SNAP!* A hidden wire snare snaps shut, catching a plump forest hare!|n"
        )
        return True
    else:
        # Bear trap on victim!
        dmg_min, dmg_max = trap["damage"]
        dmg = random.randint(dmg_min, dmg_max)

        victim.db.hp = max(0, (victim.db.hp or 0) - dmg)

        # Damage leg limb if limbs present
        limbs = getattr(victim.db, "limbs", {}) or {}
        leg = limbs.get("right leg") or limbs.get("left leg")
        if leg:
            leg["hp"] = max(0, leg.get("hp", 50) - dmg)

        victim.msg(f"\n|R*** SNAP-CRUNCH! *** You step directly onto a hidden serrated Bear Trap!|n")
        victim.msg(f"|rThe steel jaws clamp viciously into your leg for {dmg} crushing damage!|n\n")

        room.msg_contents(
            f"|r*CLANG-CRUNCH!* {victim.key} steps right into a concealed bear trap! Steel teeth bite into their leg for {dmg} damage!|n",
            exclude=[victim]
        )
        return True


def scatter_caltrops(caller, caltrop_bag):
    """Scatters sharp four-pronged iron caltrops across the room floor."""
    loc = caller.location
    if not loc:
        return False, "Nowhere to scatter."

    loc.db.has_caltrops = True
    caltrop_bag.delete()

    caller.msg("|yYou scatter a handful of sharp, spiked iron caltrops across the stones!|n")
    if loc:
        loc.msg_contents(
            f"|r{caller.key} scatters sharp four-pronged iron caltrops across the ground! Fleeing or moving will be treacherous!|n",
            exclude=[caller]
        )
    return True, "Caltrops scattered."

