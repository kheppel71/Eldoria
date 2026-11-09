"""
Nightmare LPmud Confession & Absolution Commands.
"""

from evennia.commands.command import Command
from world.nightmare_confession import (
    enter_confession, perform_holy_penance, receive_divine_absolution
)


class CmdConfess(Command):
    """
    Kneel in the cathedral confessional to whisper your moral misdeeds to the priest.

    Usage:
      confess <sin_or_misdeed>
    """

    key = "confess"
    aliases = ["confession", "confessional"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: confess <sin_or_misdeed>")
            return

        ok, msg = enter_confession(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdPerformPenance(Command):
    """
    Perform your assigned holy penance and alms donation to the poor.

    Usage:
      performpenance
      penance
    """

    key = "performpenance"
    aliases = ["penance", "dopenance"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = perform_holy_penance(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdAbsolve(Command):
    """
    Receive divine absolution from the High Confessor, cleansing spiritual stains.

    Usage:
      absolve
      receiveabsolution
    """

    key = "absolve"
    aliases = ["receiveabsolution", "absolution"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = receive_divine_absolution(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

