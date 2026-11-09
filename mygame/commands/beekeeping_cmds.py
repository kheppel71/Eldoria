"""
Nightmare LPmud Beekeeping & Mead Commands.
"""

from evennia.commands.command import Command
from world.nightmare_beekeeping import smoke_hive, harvest_hive, brew_mead, craft_candle


class CmdSmokeBees(Command):
    """
    Pacify an angry wild beehive using a bee smoker or torch.

    Usage:
      smoke bees
      smoke hive <target>
    """

    key = "smoke"
    aliases = ["smoker"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        # strip "bees" or "hive" if typed "smoke bees"
        target = args
        for prefix in ["bees", "hive"]:
            if target.lower().startswith(prefix):
                target = target[len(prefix):].strip()

        ok, msg = smoke_hive(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdHarvestHive(Command):
    """
    Harvest sweet honeycombs and pure beeswax from a pacified beehive.

    Usage:
      harvest hive
      harvest honey
    """

    key = "harvest hive"
    aliases = ["harvest honey", "harvesthive"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        args = self.args.strip()
        ok, msg = harvest_hive(caller, args)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBrewMead(Command):
    """
    Ferment sweet wild honeycomb into a potent jug of golden mead.

    Usage:
      brew mead
      brewmead
      ferment mead
    """

    key = "brewmead"
    aliases = ["brew mead", "ferment mead"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = brew_mead(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCraftCandle(Command):
    """
    Craft a fragrant beeswax taper candle from raw beeswax.

    Usage:
      craft candle
      craftcandle
    """

    key = "craftcandle"
    aliases = ["craft candle"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = craft_candle(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

