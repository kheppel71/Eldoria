"""
Nightmare LPmud Horse Taming & Breeding Commands.
"""

from evennia.commands.command import Command
from world.nightmare_horse_taming import (
    lasso_wild_horse, break_wild_horse, breed_tamed_horses, format_stable_info
)


class CmdLasso(Command):
    """
    Cast a braided leather lasso to snare an untamed wild horse.

    Usage:
      lasso
      lasso <horse>
    """

    key = "lasso"
    aliases = ["snarehorse"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = lasso_wild_horse(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBreakHorse(Command):
    """
    Mount a snared wild mustang and break it into an obedient tamed mount.

    Usage:
      breakhorse
      tamehorse
    """

    key = "breakhorse"
    aliases = ["tamehorse", "breaksteed"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = break_wild_horse(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBreedMounts(Command):
    """
    Breed two tamed mounts to produce a pedigree thoroughbred foal.

    Usage:
      breedmounts
      breedhorses
    """

    key = "breedmounts"
    aliases = ["breedhorses"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = breed_tamed_horses(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdStableInfo(Command):
    """
    Inspect the speed, endurance, and bloodline pedigree of a mount.

    Usage:
      stableinfo
      stableinfo <mount>
    """

    key = "stableinfo"
    aliases = ["horseinfo", "mountstats"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_stable_info(caller, self.args.strip()))

