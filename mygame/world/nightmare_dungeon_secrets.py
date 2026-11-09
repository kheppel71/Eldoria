"""
Nightmare LPmud Dungeon Environmental Hazards & Secret Passageway Engine.

Implements:
1. Dungeon traps (Poison Darts, Falling Deadfalls, Spike Pits).
2. Secret Illusory Walls and Concealed Passageways.
3. Wall searching ('searchwall') and trap disarming ('disarmtrap').
4. Secret door triggering ('pushbrick').
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object


def search_dungeon_walls(caller):
    """Searches current room's masonry for hidden traps and secret illusory walls."""
    loc = caller.location
    if not loc:
        return False, "Nowhere to search."

    caller.msg(f"|yYou carefully inspect the masonry, running your fingers along mortar seams and floor stones...|n")

    wis = caller.db.wis or 10
    roll = wis + random.randint(1, 20)

    found_anything = False

    # Check for environmental hazard
    hazard = getattr(loc.db, "dungeon_hazard", None)
    if hazard and not hazard.get("detected"):
        if roll >= 15:
            hazard["detected"] = True
            loc.db.dungeon_hazard = hazard
            caller.msg(f"\n|R[HAZARD DETECTED]|n You discover a concealed {hazard['type']} mechanism embedded in the stones! (Use: |wdisarmtrap|n)")
            found_anything = True

    # Check for secret passageway
    secret = getattr(loc.db, "secret_passage", None)
    if secret and not secret.get("revealed"):
        if roll >= 16:
            secret["revealed"] = True
            loc.db.secret_passage = secret
            caller.msg(f"\n|G[SECRET REVEALED]|n You find a hollow stone brick that shifts under thumb pressure! (Use: |wpushbrick|n)")
            found_anything = True

    if not found_anything:
        caller.msg("The walls and flagstones appear solid and undisturbed.")

    return True, "Search completed."


def disarm_dungeon_trap(caller):
    """Attempts to disarm a detected dungeon hazard."""
    loc = caller.location
    if not loc:
        return False, "No location."

    hazard = getattr(loc.db, "dungeon_hazard", None)
    if not hazard or not hazard.get("detected"):
        return False, "No detected traps are in this room to disarm."

    if hazard.get("disarmed"):
        return False, "This trap mechanism has already been safely dismantled."

    dex = caller.db.dex or 10
    bonus = 15 if getattr(caller.db, "guild", "") == "Rogue" else 0
    roll = dex + bonus + random.randint(1, 20)

    diff = hazard.get("diff", 25)

    if roll >= diff:
        hazard["disarmed"] = True
        loc.db.dungeon_hazard = hazard

        # Salvage scrap gears
        scrap = create_object(Object, key="Intricate Clockwork Gears", location=caller)
        scrap.db.desc = "Delicate brass gears salvaged from a disarmed dungeon trap."
        scrap.db.value = 25

        caller.msg(f"\n|G[TRAP DISARMED]|n You carefully wedge a pin into the counterweight, neutralizing the {hazard['type']}!")
        caller.msg("You salvage |wIntricate Clockwork Gears|n from the disabled mechanism.\n")
        if loc:
            loc.msg_contents(
                f"{caller.key} expertly disarms a concealed dungeon trap mechanism.",
                exclude=[caller]
            )
        return True, "Disarmed."
    else:
        # Spring the trap!
        dmg = random.randint(20, 40)
        caller.db.hp = max(0, (caller.db.hp or 0) - dmg)
        caller.msg(f"\n|R*** TRIGGERED! *** Your pick slips! The {hazard['type']} fires, hitting you for {dmg} damage!|n\n")
        if loc:
            loc.msg_contents(
                f"|r*THWACK!* The dungeon trap springs violently, striking {caller.key} for {dmg} damage!|n",
                exclude=[caller]
            )
        return False, "Triggered."


def push_secret_brick(caller):
    """Pushes the revealed stone brick, opening the secret passage."""
    loc = caller.location
    if not loc:
        return False, "No location."

    secret = getattr(loc.db, "secret_passage", None)
    if not secret or not secret.get("revealed"):
        return False, "There is no revealed secret brick here to push."

    secret["opened"] = True
    loc.db.secret_passage = secret

    caller.msg("\n|G*GRIND... RUMBLE!* You push the stone brick inward! A hidden stone doorway grinds open into a concealed alcove!|n\n")
    if loc:
        loc.msg_contents(
            f"|gA hidden section of the wall grinds aside as {caller.key} presses a concealed stone brick!|n",
            exclude=[caller]
        )
    return True, "Opened."

