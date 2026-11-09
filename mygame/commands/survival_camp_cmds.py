"""
Nightmare LPmud Survival Camp Commands.
"""

from evennia.commands.command import Command
from world.nightmare_survival_camp import (
    pitch_camp_tent, strike_camp_tent, kindle_campfire, rest_in_camp
)


class CmdPitchTent(Command):
    """
    Pitch a canvas expedition tent to shelter from harsh elements.

    Usage:
      pitchtent
      pitchcamp
    """

    key = "pitchtent"
    aliases = ["pitchcamp", "pitch"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = pitch_camp_tent(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdStrikeTent(Command):
    """
    Dismantle and pack up your pitched canvas tent.

    Usage:
      striktent
      packtent
    """

    key = "striktent"
    aliases = ["packtent", "strikecamp"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = strike_camp_tent(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdKindleFire(Command):
    """
    Gather dry wood and kindle a cheerful stone campfire.

    Usage:
      kindlefire
      campfire
    """

    key = "kindlefire"
    aliases = ["campfire", "lightfire"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = kindle_campfire(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdRestCamp(Command):
    """
    Recuperate by a pitched tent and campfire to recover health and stamina.

    Usage:
      restcamp
      camprest
    """

    key = "restcamp"
    aliases = ["camprest"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = rest_in_camp(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

