"""
Nightmare LPmud Barber-Surgeon Leeching Commands.
"""

from evennia.commands.command import Command
from world.nightmare_apothecary_leeching import (
    inspect_humors, gather_medicinal_leeches, apply_medicinal_leeches, perform_lancet_bloodletting
)


class CmdHumors(Command):
    """
    Examine the balance of the four bodily humors in yourself or an ally.

    Usage:
      humors
      humors <target>
    """

    key = "humors"
    aliases = ["diagnosehumors", "checkhumors"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        caller.msg(inspect_humors(caller, target))


class CmdJarLeeches(Command):
    """
    Gather a jar of fresh medicinal leeches from reed ponds or marsh pools.

    Usage:
      jarleeches
      gatherleeches
    """

    key = "jarleeches"
    aliases = ["gatherleeches"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = gather_medicinal_leeches(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdApplyLeeches(Command):
    """
    Apply fat medicinal leeches to purge necrotic poisons and wound sepsis.

    Usage:
      applyleeches
      applyleeches <target>
    """

    key = "applyleeches"
    aliases = ["leech", "bleedwithleeches"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        ok, msg = apply_medicinal_leeches(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBloodlet(Command):
    """
    Perform controlled lancet bloodletting to break raging fevers.

    Usage:
      bloodlet
      bloodlet <target>
    """

    key = "bloodlet"
    aliases = ["lancet", "letblood"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        ok, msg = perform_lancet_bloodletting(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")

