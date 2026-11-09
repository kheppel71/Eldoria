"""
Nightmare LPmud Astrological Constellations, Star Signs & Zodiac Engine.

Implements:
1. 5 Celestial Star Signs:
   - The Dragon (Fiery fury, +Damage)
   - The Shadowblade (Silent lethality, +Stealth/Crit)
   - The Gilded Chalice (Vitality & restoration, +Healing/Regen)
   - The Iron Bull (Fortitude & endurance, +Armor/Stamina)
   - The Celestial Comet (Arcane surge, +Mana/Magic potency)
2. Astral horoscope readings & celestial phase alignment.
3. Character star sign attunement ('stars', 'horoscope', 'stars choose <sign>').
"""

import random

ZODIAC_SIGNS = {
    "the dragon": {
        "name": "The Dragon",
        "element": "Fire",
        "boon": "+10% Fire & Physical Damage",
        "favored_phase": "Noon & Sun blazes",
        "desc": "The sign of blazing ambition, primal wrath, and fiery strength. Born warriors and fire mages.",
        "stat_boost": "strength"
    },
    "the shadowblade": {
        "name": "The Shadowblade",
        "element": "Shadow",
        "boon": "+15% Critical Chance & Stealth",
        "favored_phase": "Midnight & New Moon",
        "desc": "The sign of the unseen stalker, nocturnal mystery, and surgical lethality.",
        "stat_boost": "dexterity"
    },
    "the gilded chalice": {
        "name": "The Gilded Chalice",
        "element": "Life",
        "boon": "+15% Healing Received & Vitality Regen",
        "favored_phase": "Dawn & Waxing Moon",
        "desc": "The sign of divine benevolence, enduring renewal, and generous abundance.",
        "stat_boost": "constitution"
    },
    "the iron bull": {
        "name": "The Iron Bull",
        "element": "Earth",
        "boon": "+15% Armor Fortitude & Max Stamina",
        "favored_phase": "Dusk & Overcast skies",
        "desc": "The sign of immovable resilience, unyielding resolve, and mountain-shattering grit.",
        "stat_boost": "constitution"
    },
    "the celestial comet": {
        "name": "The Celestial Comet",
        "element": "Aether",
        "boon": "+20% Max Mana & Spell Potency",
        "favored_phase": "Night & Full Moon",
        "desc": "The sign of the visionary scholar, astral enlightenment, and cosmic surges.",
        "stat_boost": "intelligence"
    }
}


def init_character_zodiac(char, sign=None):
    """Initializes character astrological sign."""
    if not hasattr(char, "db"):
        return
    if char.db.zodiac_sign is None:
        if sign:
            char.db.zodiac_sign = sign
        else:
            # Assign random default sign
            char.db.zodiac_sign = "The Celestial Comet"


def set_character_zodiac(char, sign_name):
    """Sets the character's birth sign."""
    key = sign_name.strip().lower()
    if not key.startswith("the "):
        key = "the " + key

    if key not in ZODIAC_SIGNS:
        valid_signs = ", ".join([v["name"] for v in ZODIAC_SIGNS.values()])
        return False, f"Unknown star sign '{sign_name}'. Choose from: {valid_signs}"

    sign_data = ZODIAC_SIGNS[key]
    char.db.zodiac_sign = sign_data["name"]
    return True, f"You are now attuned to the constellation of |w{sign_data['name']}|n ({sign_data['boon']})."


def get_character_zodiac(char):
    """Retrieves character's current star sign data."""
    init_character_zodiac(char)
    sign_name = char.db.zodiac_sign or "The Celestial Comet"
    key = sign_name.lower()
    return ZODIAC_SIGNS.get(key, ZODIAC_SIGNS["the celestial comet"])


def format_constellations_display(char=None):
    """Formats celestial signs and horoscope display."""
    lines = [
        "|c" + "=" * 70 + "|n",
        "|w               ASTRAL CONSTELLATIONS & ZODIAC ALIGNMENTS            |n",
        "|c" + "=" * 70 + "|n"
    ]

    active_sign = get_character_zodiac(char)["name"] if char else None

    for key, data in ZODIAC_SIGNS.items():
        is_active = "|g[* ACTIVE SIGN *]|n " if active_sign == data["name"] else "                 "
        lines.append(f"\n{is_active}|Y{data['name']}|n [Element: |w{data['element']}|n]")
        lines.append(f"  |yBoon:|n {data['boon']}")
        lines.append(f"  |yAscendant Harmony:|n {data['favored_phase']}")
        lines.append(f"  |x{data['desc']}|n")

    lines.append("\n|c" + "=" * 70 + "|n")
    if char:
        lines.append(f"|wYour Attuned Birth Sign:|n |G{active_sign}|n")
        lines.append("|xTo align with another sign: 'stars choose <sign>'|n")
    return "\n".join(lines)

