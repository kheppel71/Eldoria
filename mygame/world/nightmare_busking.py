"""
Nightmare LPmud Street Begging, Busking & Town Performances Engine.

Implements:
1. Street Urchin Alms Begging ('beg [target]').
2. Town Square Busking ('busk'):
   - Dagger Juggling (Acrobatic dexterity)
   - Pennywhistle Reel (Musical performance)
   - Fire-Breathing (Flamboyant crowd-pleaser)
3. Spontaneous coin toss rewards from passersby and spectators.
"""

import random

PERFORMANCE_ACTS = {
    "juggle": {
        "title": "Dagger Juggling",
        "min_coins": 15,
        "max_coins": 30,
        "emote": "You deftly toss three gleaming daggers into the air, spinning them in a dazzling blur of flashing steel!"
    },
    "flute": {
        "title": "Pennywhistle Reel",
        "min_coins": 12,
        "max_coins": 28,
        "emote": "You pull a tin whistle to your lips and play a sprightly, foot-tapping frontier reel!"
    },
    "fire": {
        "title": "Fire-Breathing Spectacle",
        "min_coins": 20,
        "max_coins": 45,
        "emote": "You take a swig of distilled spirits and spray a roaring plume of flame high into the air!"
    }
}


def beg_for_alms(caller, target_name=""):
    """Begs for spare copper or silver coins from nearby folk."""
    room = caller.location
    if not room:
        return False, "You cannot beg in the void."

    # Perform roll
    roll = random.randint(1, 100)
    if roll <= 70:
        coins_given = random.randint(5, 15)
        caller.db.coins = (getattr(caller.db, "coins", 0) or 0) + coins_given

        caller.msg(
            f"\n|yYou hold out a cup with humble posture, asking for spare copper.|n\n"
            f"|wA sympathetic passerby stops, dropping |y{coins_given} coins|w into your cup!|n\n"
        )
        if room:
            room.msg_contents(
                f"{caller.key} humbly begs for alms and receives a few coins from a charitable townsfolk.",
                exclude=[caller]
            )
        return True, "Received alms."
    else:
        caller.msg("\n|xYou ask for alms, but hurried passersby avert their eyes and brush past without stopping.|n\n")
        return False, "No coins received."


def perform_busking(caller, act_key="juggle"):
    """Performs street busking in public squares for audience coin tips."""
    room = caller.location
    if not room:
        return False, "You cannot busk in the void."

    key = act_key.strip().lower()
    matched = next((k for k in PERFORMANCE_ACTS if key in k), None)

    if not matched:
        opts = ", ".join(PERFORMANCE_ACTS.keys())
        return False, f"Unknown busking act '{act_key}'. Available acts: {opts}"

    act = PERFORMANCE_ACTS[matched]
    earned = random.randint(act["min_coins"], act["max_coins"])
    caller.db.coins = (getattr(caller.db, "coins", 0) or 0) + earned

    caller.msg(f"\n|Y[STREET PERFORMANCE]|n {act['emote']}\n")
    caller.msg(
        f"|gA crowd gathers, clapping in appreciation and tossing |y{earned} coins|g into your upturned hat!|n\n"
    )
    if room:
        room.msg_contents(
            f"|C{caller.key} performs an entertaining {act['title']}! Spectators applaud and toss coins into their hat!|n",
            exclude=[caller]
        )
    return True, f"Busked {act['title']}."

