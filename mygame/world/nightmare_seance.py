"""
Nightmare LPmud Graveyard Séances, Spirit Mediums & Talking Boards Engine.

Implements:
1. Inscribed Cedar Spirit Boards & Black Candles.
2. Holding séances in graveyards and crypts ('seance').
3. Summoning deceased spectral apparitions ('summonspirit').
4. Questioning ghosts for crypt lore and forgotten secrets ('questionghost <topic>').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

SPIRIT_LORE = {
    "treasure": "The phantom points a translucent finger into the gloom: \"Beneath the third flagstone of the crypt altar lies the gilded coffer of the Abbot...\"",
    "curse": "The spirit moans softly: \"The obsidian ring drinks life... only holy water and sacred prayer can break the binding...\"",
    "murder": "The ghost's eyes blaze with spectral fury: \"It was the guildmaster's blade that took my breath in the dark alley! Avenge my blood!\"",
    "default": "The apparition whispers hollowly: \"The veil is thin, traveler. Tread lightly among the resting stones...\""
}


def create_spirit_board(location, name="Inscribed Cedar Spirit Board"):
    """Spawns an occult séance talking board."""
    board = create_object(Object, key=name, location=location)
    board.db.is_spirit_board = True
    board.db.desc = "A polished cedar board inscribed with archaic runes, alphabet arcs, and a teardrop horn planchette."
    return board


def begin_seance(caller):
    """Initiates a spiritual séance circle in a graveyard or crypt."""
    room = caller.location
    if not room:
        return False, "You cannot hold a séance in the void."

    # Look for spirit board
    has_board = any(
        getattr(obj.db, "is_spirit_board", False) or "spirit board" in obj.key.lower()
        for obj in (caller.contents + room.contents)
    )

    if not has_board:
        return False, "You need an Inscribed Spirit Board to conduct a séance! ('seance')"

    room.db.active_seance = True
    caller.msg(
        "\n|m[OCCULT SÉANCE INITIATED]|n You light black tallow candles around the cedar spirit board.\n"
        "The ambient air temperature drops to a bone-chilling cold! Shadows stretch and flicker!\n"
        "|wThe séance circle is OPEN. Command 'summonspirit' to call forth the dead!|n\n"
    )
    if room:
        room.msg_contents(
            f"|m{caller.key} lights black candles upon a spirit board; the room chills with supernatural cold!|n",
            exclude=[caller]
        )
    return True, "Séance started."


def summon_spectral_spirit(caller, spirit_name="Ghost of Lady Eleanor"):
    """Summons a spectral ghost into the active séance circle."""
    room = caller.location
    if not room or not getattr(room.db, "active_seance", False):
        return False, "You must open a séance circle first! ('seance')"

    ghost = create_object(Object, key=spirit_name, location=room)
    ghost.db.is_ghost_apparition = True
    ghost.db.desc = f"A translucent, floating spectral figure with sorrowful hollow eyes, suspended in misty luminescence."

    caller.msg(
        f"\n|C*WHOOOOSH!*|n A gust of freezing wind blows out the candles!\n"
        f"Misty ectoplasm coalesces into the floating apparition of |w{ghost.key}|n!\n"
        "|yUse 'questionghost <treasure|curse|murder>' to commune with the spirit!|n\n"
    )
    if room:
        room.msg_contents(
            f"|CA translucent spectral apparition of {ghost.key} manifests from the swirling mist!|n",
            exclude=[caller]
        )
    return True, f"Summoned {ghost.key}."


def question_spectral_ghost(caller, topic="treasure"):
    """Interrogates a summoned ghost on historical or crypt lore."""
    room = caller.location
    ghost = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_ghost_apparition", False):
            ghost = obj
            break

    if not ghost:
        return False, "There is no summoned ghost apparition present to question! Use 'summonspirit' first."

    key = topic.strip().lower()
    answer = SPIRIT_LORE.get(key, SPIRIT_LORE["default"])

    caller.msg(f"\n|mYou touch the planchette on the spirit board and inquire about |w'{topic}'|m...|n\n")
    caller.msg(f"|C{ghost.key} speaks in a voice like rustling dry autumn leaves:|n\n|w\"{answer}\"|n\n")

    if room:
        room.msg_contents(
            f"{caller.key} questions {ghost.key}; the ghost's spectral whispers drift through the room.",
            exclude=[caller]
        )
    return True, "Ghost questioned."

