"""
Nightmare LPmud Bathhouse Commands.
"""

from evennia.commands.command import Command
from world.nightmare_bathhouse import (
    format_bathhouse_directory, soak_in_pool, wash_battle_grime
)


class CmdBathhouse(Command):
    """
    View available thermal mineral pools, steam vaults, and cold plunges.

    Usage:
      bathhouse
      pools
      springs
    """

    key = "bathhouse"
    aliases = ["pools", "springs", "mineralbath"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_bathhouse_directory())


class CmdSoak(Command):
    """
    Soak in a thermal mineral pool or steam room for restorative boons.

    Usage:
      soak <caldarium|steam|frigidarium>
    """

    key = "soak"
    aliases = ["bathe", "immerse"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "caldarium"
        ok, msg = soak_in_pool(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdWashGrime(Command):
    """
    Wash away dried battle gore, soot, and dungeon grime with scented olive soap.

    Usage:
      washgrime
      wash
      cleanse
    """

    key = "washgrime"
    aliases = ["wash", "spongegrime"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        wash_battle_grime(caller)

