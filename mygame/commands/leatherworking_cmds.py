"""
Nightmare LPmud Leatherworking Commands.
"""

from evennia.commands.command import Command
from world.nightmare_leatherworking import (
    skin_beast_carcass, cure_leather_in_vat, craft_leather_armor
)


class CmdSkinHide(Command):
    """
    Skin a slain beast carcass with a skinning knife for raw pelts.

    Usage:
      skinhide
      skinhide <corpse>
    """

    key = "skinhide"
    aliases = ["skin", "fielddress"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = skin_beast_carcass(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdTanLeather(Command):
    """
    Steep raw hides in an oak-bark tanning vat to produce cured leather.

    Usage:
      tanleather
      curehide
    """

    key = "tanleather"
    aliases = ["curehide", "tanning"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = cure_leather_in_vat(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCraftArmor(Command):
    """
    Tailor rolls of cured leather into defensive boots, jerkins, or cuirasses.

    Usage:
      craftarmor <boots|jerkin|cuirass>
    """

    key = "craftarmor"
    aliases = ["stitchleather", "makeleather"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "jerkin"
        ok, msg = craft_leather_armor(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")

