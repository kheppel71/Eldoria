"""
Nightmare LPmud Eldritch Tarot Divination & Fate Cards Engine.

Implements:
1. Mystic 22-Card Major Arcana Deck:
   - The Fool, The Magician, The High Priestess, The Hermit,
     Wheel of Fortune, Death, The Tower, The Star, The Sun.
2. Single-card daily fate omen draw ('drawcard').
3. Three-Card Past/Present/Future Divination Spread ('tarotread <target>').
4. Fortune reading roleplay and fate blessings.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

MAJOR_ARCANA = [
    {
        "num": "0",
        "name": "The Fool",
        "upright": "Spontaneous adventure, innocent trust, uncharted horizons.",
        "blessing": "+10 Luck & Free Spirit"
    },
    {
        "num": "I",
        "name": "The Magician",
        "upright": "Arcane mastery, willpower, elemental manifestation.",
        "blessing": "+15 Max Mana & Spell Focus"
    },
    {
        "num": "II",
        "name": "The High Priestess",
        "upright": "Intuitive wisdom, veiled mysteries, lunar subconscious.",
        "blessing": "Heightened Hazard Detection"
    },
    {
        "num": "IX",
        "name": "The Hermit",
        "upright": "Solitary enlightenment, lantern of truth, quiet contemplation.",
        "blessing": "+20% Rest Recuperation"
    },
    {
        "num": "X",
        "name": "Wheel of Fortune",
        "upright": "Whims of destiny, turn of the karmic tides, unexpected wealth.",
        "blessing": "Spontaneous Coin Fortune"
    },
    {
        "num": "XIII",
        "name": "Death",
        "upright": "Profound transformation, conclusion of cycles, inevitable rebirth.",
        "blessing": "Resilience against Fatal Blows"
    },
    {
        "num": "XVI",
        "name": "The Tower",
        "upright": "Sudden revelation, shattering illusions, sudden lightning strike.",
        "blessing": "+15% Critical Strike"
    },
    {
        "num": "XVII",
        "name": "The Star",
        "upright": "Serene hope, cosmic inspiration, healing starlight.",
        "blessing": "+25 Health Regeneration"
    },
    {
        "num": "XIX",
        "name": "The Sun",
        "upright": "Radiant triumph, abundant vitality, clarity of purpose.",
        "blessing": "+10 Physical Power & Morale"
    }
]


def create_tarot_deck(location, name="Velvet Deck of Major Arcana"):
    """Spawns an occult tarot card deck."""
    deck = create_object(Object, key=name, location=location)
    deck.db.is_tarot_deck = True
    deck.db.desc = "A velvet-wrapped box containing heavy parchment cards gilded with celestial gold leaf and eldritch arcana."
    return deck


def draw_single_fate_card(caller):
    """Draws a single fortune card from the Major Arcana."""
    card = random.choice(MAJOR_ARCANA)

    lines = [
        "|c" + "=" * 55 + "|n",
        f"|w             MAJOR ARCANA: [{card['num']}] {card['name'].upper()} |n",
        "|c" + "=" * 55 + "|n",
        f" |yDivination Meaning:|n {card['upright']}",
        f" |gOmen Blessing:|n {card['blessing']}",
        "|c" + "=" * 55 + "|n"
    ]
    caller.msg("\n" + "\n".join(lines) + "\n")

    if caller.location:
        caller.location.msg_contents(
            f"|m{caller.key} cuts the velvet tarot deck and draws [{card['num']}] {card['name']}!|n",
            exclude=[caller]
        )
    return True, card["name"]


def perform_three_card_spread(caller, target_char=None):
    """Performs a 3-card spread (Past, Present, Future) for the target."""
    target = target_char if target_char else caller
    cards = random.sample(MAJOR_ARCANA, 3)

    lines = [
        "|c" + "=" * 70 + "|n",
        f"|w               THREE-CARD FATE SPREAD FOR {target.key.upper()}       |n",
        "|c" + "=" * 70 + "|n",
        f"\n|Y[I. THE PAST]|n    : |w[{cards[0]['num']}] {cards[0]['name']}|n",
        f"  |yInfluences:|n {cards[0]['upright']}",
        f"\n|Y[II. THE PRESENT]|n: |w[{cards[1]['num']}] {cards[1]['name']}|n",
        f"  |yCrossroads:|n {cards[1]['upright']}",
        f"\n|Y[III. THE FUTURE]|n: |w[{cards[2]['num']}] {cards[2]['name']}|n",
        f"  |yDestiny:|n {cards[2]['upright']}",
        f"  |gAscendant Fate Blessing:|n {cards[2]['blessing']}",
        "\n|c" + "=" * 70 + "|n"
    ]

    spread_text = "\n".join(lines)
    caller.msg("\n" + spread_text + "\n")

    if target != caller:
        target.msg(
            f"\n|m{caller.key} lays out three velvet tarot cards across the table for your reading:\n" + spread_text + "\n"
        )

    if caller.location:
        caller.location.msg_contents(
            f"|m{caller.key} spreads three glowing tarot cards across the table, reading the fate of {target.key}.|n",
            exclude=[caller, target]
        )
    return True, "Reading completed."

