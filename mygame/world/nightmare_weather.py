"""
Nightmare LPmud Dynamic Celestial Cycle, Lunar Phases & Weather Engine.

Implements:
1. In-game 24-hour Celestial Clock (Dawn, Morning, Noon, Dusk, Night, Midnight).
2. Lunar Phases (New Moon, Waxing Crescent, Full Moon, Waning Gibbous, Blood Moon).
3. Atmospheric Weather Fronts (Clear, Overcast, Rainstorm, Thunderstorm, Dense Fog, Blizzard).
4. Elemental spell and stealth environmental modifiers.
"""

import time

TIME_PERIODS = [
    (0, 4, "Midnight", "|bThe pitch-black silence of the midnight hour envelops the realm.|n", True),
    (5, 7, "Dawn", "|ySoft golden rays break across the eastern horizon, heralding the dawn.|n", False),
    (8, 11, "Morning", "|wBright morning sunlight casts long, crisp shadows across the lands.|n", False),
    (12, 16, "Noon", "|YSearing high noon sun blazes directly overhead.|n", False),
    (17, 19, "Dusk", "|rAmber and violet twilight settles over the horizon as dusk falls.|n", False),
    (20, 23, "Night", "|mA blanket of starlight and night sky descends upon the world.|n", True)
]

MOON_PHASES = [
    ("New Moon", "The moon is shrouded in shadow; the night is dark and foreboding.", 0),
    ("Waxing Crescent", "A slender sliver of silver light glimmers in the night sky.", 2),
    ("Full Moon", "A brilliant pearl-white orb bathes the land in luminous lunar radiance (+Mana Regen).", 5),
    ("Waning Gibbous", "The great silver moon slowly recedes into shadow.", 2),
    ("Blood Moon", "An eerie, crimson-tinged moon hangs low, stoking primal predatory instincts.", 8)
]

WEATHER_FRONTS = {
    "clear": {
        "name": "Clear Skies",
        "desc": "The sky is calm and cloudless, offering pristine visibility.",
        "modifier": "None"
    },
    "overcast": {
        "name": "Overcast",
        "desc": "Heavy, iron-grey storm clouds roll across the skies.",
        "modifier": "Reduced solar brightness"
    },
    "rainstorm": {
        "name": "Heavy Downpour",
        "desc": "Sheets of driving rain drench the realm, dampening flames and creating pooling mud.",
        "modifier": "Fire spells dampened (-15% damage)"
    },
    "thunderstorm": {
        "name": "Crackling Thunderstorm",
        "desc": "Jagged forks of blue lightning tear the sky apart amid deafening thunderclaps.",
        "modifier": "Lightning spells empowered (+20% damage)"
    },
    "dense_fog": {
        "name": "Dense Fog",
        "desc": "Thick, swirling banks of damp mist veil the landscape.",
        "modifier": "Stealth and sneak attacks empowered (+15%)"
    },
    "blizzard": {
        "name": "Howling Blizzard",
        "desc": "Blinding squalls of ice and snow lash the earth with freezing fury.",
        "modifier": "Cold spells empowered, movement slowed"
    }
}

# Current global weather state
CURRENT_WEATHER = "clear"


def get_game_time():
    """
    Returns current in-game hour (0-23), period name, atmospheric description, and is_night boolean.
    Calculates time deterministically from epoch time (1 real hour = 1 game day).
    """
    # 1 real hour = 3600 real seconds = 24 game hours (150 real seconds per game hour)
    elapsed = int(time.time())
    game_hour = (elapsed // 150) % 24

    for start_h, end_h, name, desc, is_night in TIME_PERIODS:
        if start_h <= game_hour <= end_h:
            return game_hour, name, desc, is_night

    return game_hour, "Night", "|mThe dark night sky watches overhead.|n", True


def get_moon_phase():
    """Returns the current lunar phase tuple (phase_name, description, mana_bonus)."""
    # Lunar cycle rotates every 4 real hours
    cycle_index = (int(time.time()) // (3600 * 4)) % len(MOON_PHASES)
    return MOON_PHASES[cycle_index]


def get_current_weather():
    """Returns the current weather dictionary."""
    global CURRENT_WEATHER
    return WEATHER_FRONTS.get(CURRENT_WEATHER, WEATHER_FRONTS["clear"])


def set_weather(weather_key):
    """Sets the realm's current weather front."""
    global CURRENT_WEATHER
    if weather_key.lower() in WEATHER_FRONTS:
        CURRENT_WEATHER = weather_key.lower()
        return True, f"Weather changed to {WEATHER_FRONTS[CURRENT_WEATHER]['name']}."
    return False, f"Unknown weather '{weather_key}'."

