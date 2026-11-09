"""
Nightmare LPmud Woodcarving Commands.
"""

from evennia.commands.command import Command
from world.nightmare_woodcarving import (
    whittle_wooden_curio, carve_wooden_flute, carve_bardic_lute
)


class CmdWhittle(Command):
    """
    Whittle seasoned timber into wooden smoking pipes, talismans, or walking staffs.

    Usage:
      whittle <pipe|talisman|staff>
    """

    key = "whittle"
    aliases = ["woodcarve", "whittling"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "pipe"
        ok, msg = whittle_wooden_curio(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCarveFlute(Command):
    """
    Bore and tune a six-hole acoustic wooden flute.

    Usage:
      carveflute
      makeflute
    """

    key = "carveflute"
    aliases = ["makeflute"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = carve_wooden_flute(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCarveLute(Command):
    """
    Construct a resonant spruce bardic lute strung with gut strings.

    Usage:
      carvelute
      makelute
    """

    key = "carvelute"
    aliases = ["makelute", "luthier"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = carve_bardic_lute(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

