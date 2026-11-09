"""
Nightmare LPmud War Banner Commands.
"""

from evennia.commands.command import Command
from world.nightmare_banners import (
    plant_war_banner, uproot_war_banner, sound_rallying_warhorn
)


class CmdPlantBanner(Command):
    """
    Plant a towering guild battle standard into the ground to project an inspiring aura.

    Usage:
      plantbanner
      raisebanner
    """

    key = "plantbanner"
    aliases = ["raisebanner", "setstandard"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = plant_war_banner(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdUprootBanner(Command):
    """
    Uproot a planted battle standard from the ground to carry on the march.

    Usage:
      uprootbanner
      packbanner
    """

    key = "uprootbanner"
    aliases = ["packbanner", "retrievebanner"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = uproot_war_banner(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBlowWarhorn(Command):
    """
    Blow a thunderous martial blast from a warhorn to rally nearby allies.

    Usage:
      blowwarhorn
      soundhorn
    """

    key = "blowwarhorn"
    aliases = ["soundhorn", "warhorn"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = sound_rallying_warhorn(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

