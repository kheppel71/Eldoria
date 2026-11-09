"""
Nightmare LPmud Illusionism Commands.
"""

from evennia.commands.command import Command
from world.nightmare_illusionism import (
    cast_mirror_images, cast_phantasmal_terror, dispel_illusions
)


class CmdMirrorImage(Command):
    """
    Weave refractive light into 3 shimmering duplicate images that absorb attacks.

    Usage:
      mirrorimage
      castmirror
    """

    key = "mirrorimage"
    aliases = ["castmirror", "doppelganger"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        ok, msg = cast_mirror_images(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdPhantasm(Command):
    """
    Project waking nightmarish horrors into the mind of an enemy.

    Usage:
      phantasm <target>
      phantasmalterror <target>
    """

    key = "phantasm"
    aliases = ["phantasmalterror", "castterror"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: phantasm <target>")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        ok, msg = cast_phantasmal_terror(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDispelIllusion(Command):
    """
    Pierce and banish active mirror duplicates and mental phantasms.

    Usage:
      dispelillusion
      dispelillusion <target>
    """

    key = "dispelillusion"
    aliases = ["pierceglamour", "unmaskillusion"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        target = caller.search(self.args.strip()) if self.args else caller
        if not target:
            return

        ok, msg = dispel_illusions(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")

