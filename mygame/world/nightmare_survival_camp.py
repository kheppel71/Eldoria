"""
Nightmare LPmud Wilderness Survival Camps, Canvas Tents & Hearth Engine.

Implements:
1. Portable Canvas Expedition Tents ('pitchtent', 'striktent').
2. Stone Campfires & Hearth Warmth ('kindlefire').
3. Camp rest & accelerated outdoor recuperation ('restcamp').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_portable_tent(location, name="Rolled Canvas Tent"):
    """Spawns an unpackable expedition tent."""
    tent = create_object(Object, key=name, location=location)
    tent.db.is_portable_tent = True
    tent.db.desc = "A tightly rolled canvas expedition tent bound with oiled leather straps and wooden pegs."
    return tent


def pitch_camp_tent(caller):
    """Pitches a canvas tent in the current room."""
    room = caller.location
    if not room:
        return False, "You cannot pitch a tent in the void."

    # Check for rolled tent in inventory
    tent_item = None
    for obj in caller.contents:
        if getattr(obj.db, "is_portable_tent", False) or "canvas tent" in obj.key.lower():
            tent_item = obj
            break

    if not tent_item:
        return False, "You need a Rolled Canvas Tent in your inventory to pitch camp!"

    tent_item.delete()

    pitched_tent = create_object(Object, key="Canvas Expedition Tent", location=room)
    pitched_tent.db.is_pitched_tent = True
    pitched_tent.db.owner = caller
    pitched_tent.db.desc = f"A sturdy canvas field tent secured with taut guy-lines and wooden pegs, pitched by {caller.key}."

    caller.msg(
        "\n|Y[SURVIVAL CAMP]|n You drive the pegs into the earth and hoist the center pole!\n"
        "Your |wCanvas Expedition Tent|n stands firm, offering sanctuary from the harsh elements!\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} pitches a sturdy canvas expedition tent in the clearing.",
            exclude=[caller]
        )
    return True, "Tent pitched."


def strike_camp_tent(caller):
    """Dismantles and packs up a pitched camp tent."""
    room = caller.location
    tent = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_pitched_tent", False):
            if getattr(obj.db, "owner", None) == caller:
                tent = obj
                break

    if not tent:
        return False, "There is no pitched tent belonging to you here to strike."

    tent.delete()
    rolled = create_portable_tent(caller)

    caller.msg("\n|yYou pull the wooden stakes, collapse the canvas, and strap it into a |wRolled Canvas Tent|y!|n\n")
    if room:
        room.msg_contents(f"{caller.key} strikes camp and rolls up their canvas tent.", exclude=[caller])
    return True, "Tent packed."


def kindle_campfire(caller):
    """Gathers kindling and lights a crackling stone campfire."""
    room = caller.location
    if not room:
        return False, "You cannot kindle a fire in the void."

    fire = None
    for obj in room.contents:
        if getattr(obj.db, "is_campfire", False):
            fire = obj
            break

    if fire:
        return False, "There is already a warm campfire crackling here!"

    fire = create_object(Object, key="Crackling Stone Campfire", location=room)
    fire.db.is_campfire = True
    fire.db.desc = "A cheerful campfire enclosed by river stones, crackling warmly and casting dancing embers into the twilight."

    caller.msg(
        "\n|r*FLINT & STEEL!*|n You strike sparks into dry tinder, fanning it into a roaring |wCrackling Stone Campfire|r!\n"
        "Warmth and light fill the camp, chasing away the cold shadows.\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} strikes sparks and kindles a cheerful stone campfire, warming the campsite.",
            exclude=[caller]
        )
    return True, "Campfire lit."


def rest_in_camp(caller):
    """Rests at camp, restoring health, stamina, and mana."""
    room = caller.location
    has_shelter = any(getattr(obj.db, "is_pitched_tent", False) for obj in (room.contents if room else []))
    has_fire = any(getattr(obj.db, "is_campfire", False) for obj in (room.contents if room else []))

    if not has_shelter and not has_fire:
        return False, "You need a pitched tent or a warm campfire to establish a restorative survival camp! ('pitchtent', 'kindlefire')"

    bonus = 40 if (has_shelter and has_fire) else 20
    curr_hp = getattr(caller.db, "hp", 100) or 100
    max_hp = getattr(caller.db, "max_hp", 100) or 100
    caller.db.hp = min(max_hp, curr_hp + bonus)

    curr_stam = getattr(caller.db, "stamina", 100) or 100
    max_stam = getattr(caller.db, "max_stamina", 100) or 100
    caller.db.stamina = min(max_stam, curr_stam + bonus)

    caller.msg(
        f"\n|G[CAMP REST]|n You stretch out by the hearth shelter, letting warmth seep into your weary bones.\n"
        f"You recover |w+{bonus} Health|n and |w+{bonus} Stamina|n!\n"
    )
    if room:
        room.msg_contents(f"{caller.key} relaxes by the campsite hearth, recuperating from their travels.", exclude=[caller])
    return True, "Rested at camp."

