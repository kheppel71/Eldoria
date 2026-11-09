"""
Nightmare LPmud Cheesemaking & Dairy Commands.
"""

from evennia.commands.command import Command
from world.nightmare_cheesemaking import (
    milk_farm_livestock, churn_dairy_butter, press_artisan_cheese, age_cheese_in_cellar
)


class CmdMilkLivestock(Command):
    """
    Milk pasture dairy cows or mountain goats into a tin milk pail.

    Usage:
      milklivestock
      milkcow
    """

    key = "milklivestock"
    aliases = ["milkcow", "milkgoat"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = milk_farm_livestock(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdChurnButter(Command):
    """
    Churn fresh milk cream in a wooden churn to create salted butter.

    Usage:
      churnbutter
      makebutter
    """

    key = "churnbutter"
    aliases = ["makebutter"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = churn_dairy_butter(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdPressCheese(Command):
    """
    Press curds into a round wheel of artisan cheese.

    Usage:
      presscheese <cheddar|stilton|gouda>
    """

    key = "presscheese"
    aliases = ["makecheese"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "cheddar"
        ok, msg = press_artisan_cheese(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdAgeCheese(Command):
    """
    Age and mature a cheese wheel on cellar cedar racks.

    Usage:
      agecheese
      cellarcheese
    """

    key = "agecheese"
    aliases = ["cellarcheese", "maturecheese"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = age_cheese_in_cellar(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

