"""
Nightmare LPmud Diving & Salvage Commands.
"""

from evennia.commands.command import Command
from world.nightmare_diving import (
    equip_diving_suit, dive_into_depths, salvage_seabed, pry_open_chest
)


class CmdDivingSuit(Command):
    """
    Equip a heavy brass diving helmet and sea suit for underwater breathing.

    Usage:
      divingsuit
      donhelmet
    """

    key = "divingsuit"
    aliases = ["donhelmet", "divinggear"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = equip_diving_suit(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDive(Command):
    """
    Plunge into coastal waters, coral reefs, or sunken shipwreck depths.

    Usage:
      dive
      submerge
    """

    key = "dive"
    aliases = ["submerge"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        ok, msg = dive_into_depths(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdSalvageDepths(Command):
    """
    Search the submerged seabed and shipwreck ruins for lost treasures.

    Usage:
      salvagedepths
      salvage
    """

    key = "salvagedepths"
    aliases = ["salvage", "searchdepths"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        ok, msg = salvage_seabed(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdPryChest(Command):
    """
    Pry open barnacle-crusted sea chests salvaged from the ocean floor.

    Usage:
      prychest
      openchest
    """

    key = "prychest"
    aliases = ["openchest", "crackchest"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        ok, msg = pry_open_chest(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")

