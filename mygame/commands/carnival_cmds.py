"""
Nightmare LPmud Carnival Commands.
"""

from evennia.commands.command import Command
from world.nightmare_carnival import (
    format_carnival_directory, play_high_striker, play_balloon_target
)


class CmdCarnival(Command):
    """
    View the traveling carnival attractions and game booths.

    Usage:
      carnival
      midway
    """

    key = "carnival"
    aliases = ["midway", "carnivalgames"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_carnival_directory())


class CmdTestStrength(Command):
    """
    Slam the carnival mallet into the High Striker base pin to ring the brass bell.

    Usage:
      teststrength
      highstriker
    """

    key = "teststrength"
    aliases = ["highstriker", "strikehigh"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = play_high_striker(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdPlayTarget(Command):
    """
    Throw daggers at the spinning carnival balloon target board.

    Usage:
      playtarget
      balloontoss
    """

    key = "playtarget"
    aliases = ["balloontoss", "spintarget"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = play_balloon_target(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

