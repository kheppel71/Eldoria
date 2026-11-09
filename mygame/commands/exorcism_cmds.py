"""
Nightmare LPmud Exorcism & Curse Commands.
"""

from evennia.commands.command import Command
from world.nightmare_exorcism import inspect_curse, perform_exorcism


class CmdCurseInfo(Command):
    """
    Examine an item for dark spiritual curses, hexes, and unholy bindings.

    Usage:
      curseinfo <item>
      curses
    """

    key = "curseinfo"
    aliases = ["curses", "checkcurse"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: curseinfo <item>")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target and caller.location:
            target = caller.location.search(self.args.strip())
        if not target:
            return

        caller.msg(inspect_curse(caller, target))


class CmdExorcise(Command):
    """
    Perform an exorcism rite to cleanse a cursed relic of demonic corruption.

    Usage:
      exorcise <item>
      purify <item>
    """

    key = "exorcise"
    aliases = ["purify", "banishcurse"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        ok, msg = perform_exorcism(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")

