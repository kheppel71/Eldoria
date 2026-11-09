"""
Nightmare LPmud Begging & Busking Commands.
"""

from evennia.commands.command import Command
from world.nightmare_busking import beg_for_alms, perform_busking


class CmdBeg(Command):
    """
    Humbly beg for copper coins from charitable citizens and merchants.

    Usage:
      beg
      beg <target>
    """

    key = "beg"
    aliases = ["begalms", "askalms"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = beg_for_alms(caller, self.args.strip())


class CmdBusk(Command):
    """
    Perform acrobatic, musical, or fiery street busking for coin tips.

    Usage:
      busk
      busk <juggle|flute|fire>
    """

    key = "busk"
    aliases = ["juggle", "streetperform"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        act_choice = self.args.strip() or "juggle"
        ok, msg = perform_busking(caller, act_choice)
        if not ok:
            caller.msg(f"|r{msg}|n")

