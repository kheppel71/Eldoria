"""
Nightmare LPmud Glassblowing Commands.
"""

from evennia.commands.command import Command
from world.nightmare_glassblowing import gather_silica_quartz, blow_glass_item


class CmdGatherQuartz(Command):
    """
    Sift through riverbeds, beaches, or quarries for pure silica quartz sand.

    Usage:
      gatherquartz
      gathersand
    """

    key = "gatherquartz"
    aliases = ["gathersand", "siftsand"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = gather_silica_quartz(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBlowGlass(Command):
    """
    Shape molten quartz into delicate alchemical phials, alembics, or stained glass.

    Usage:
      blowglass <phial|alembic|stainedtile>
    """

    key = "blowglass"
    aliases = ["craftglass", "glassblow"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "phial"
        ok, msg = blow_glass_item(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")

