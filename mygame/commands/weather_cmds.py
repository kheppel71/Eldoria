"""
Celestial clock and weather commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_weather import (
    get_game_time, get_moon_phase, get_current_weather, set_weather, WEATHER_FRONTS
)


class CmdTime(default_cmds.MuxCommand):
    """
    Check the current in-game time of day and celestial cycle

    Usage:
      time
      clock
    """
    key = "time"
    aliases = ["clock"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        hour, period, desc, is_night = get_game_time()
        moon_name, moon_desc, mana_bonus = get_moon_phase()

        caller.msg(f"\n|w============================= CELESTIAL CLOCK =============================|n")
        caller.msg(f"Hour: |c{hour:02d}:00|n    Period: |y{period}|n    Light: {'|mNOCTURNAL|n' if is_night else '|YDIURNAL|n'}")
        caller.msg(f"\n{desc}")
        if is_night:
            caller.msg(f"\n|cCurrent Lunar Phase:|n |w{moon_name}|n")
            caller.msg(f"  {moon_desc}")
            if mana_bonus > 0:
                caller.msg(f"  |mArcane Resonance: +{mana_bonus} MP Regeneration bonus active!|n")
        caller.msg("|w" + "=" * 74 + "|n\n")


class CmdWeather(default_cmds.MuxCommand):
    """
    Look up at the heavens to examine the sky, weather front, and atmosphere

    Usage:
      weather
      sky
    """
    key = "weather"
    aliases = ["sky"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        hour, period, _, is_night = get_game_time()
        w = get_current_weather()
        moon_name, _, _ = get_moon_phase()

        caller.msg(f"\n|c=== The Skies Above Sigil ===|n")
        caller.msg(f"Time: |w{period} ({hour:02d}:00)|n    Current Weather: |y{w['name']}|n")
        caller.msg(f"Atmospheric Details: {w['desc']}")
        caller.msg(f"Environmental Effect: |g{w['modifier']}|n")
        if is_night:
            caller.msg(f"Moon: |m{moon_name}|n")
        caller.msg("|c" + "=" * 32 + "|n\n")


class CmdSetWeather(default_cmds.MuxCommand):
    """
    Admin command to manipulate realm weather

    Usage:
      setweather <clear/overcast/rainstorm/thunderstorm/dense_fog/blizzard>
    """
    key = "setweather"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg(f"Available weather fronts: {', '.join(WEATHER_FRONTS.keys())}")
            return

        ok, msg = set_weather(self.args.strip())
        caller.msg(msg)

