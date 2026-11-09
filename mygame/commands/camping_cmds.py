"""
Wilderness camping and campfire commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_camping import pitch_campsite_tent, light_campfire, strike_campsite


class CmdPitchTent(default_cmds.MuxCommand):
    """
    Pitch a weather-tight canvas tent shelter in the wilderness

    Usage:
      pitchtent
      camp
    """
    key = "pitchtent"
    aliases = ["camp", "makepicamp"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        kit = None
        for obj in caller.contents:
            if "tent" in obj.key.lower():
                kit = obj
                break

        if not kit:
            caller.msg("You do not have a canvas tent kit in your pack!")
            return

        ok, msg = pitch_campsite_tent(caller, kit)
        if not ok:
            caller.msg(msg)


class CmdLightCampfire(default_cmds.MuxCommand):
    """
    Strike flint and tinder to kindle a warm pine campfire

    Usage:
      lightcampfire
      kindlefire
    """
    key = "lightcampfire"
    aliases = ["campfire", "kindlefire"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        ok, msg = light_campfire(caller, None)
        if not ok:
            caller.msg(msg)


class CmdStrikeCamp(default_cmds.MuxCommand):
    """
    Pack up your canvas tent shelter and extinguish the fire

    Usage:
      strikecamp
      packcamp
    """
    key = "strikecamp"
    aliases = ["packcamp"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        ok, msg = strike_campsite(caller)
        if not ok:
            caller.msg(msg)

