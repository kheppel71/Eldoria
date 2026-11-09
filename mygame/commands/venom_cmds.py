"""
Nightmare LPmud Venom & Antidote Commands.
"""

from evennia.commands.command import Command
from world.nightmare_venom import (
    milk_creature_venom, brew_antidote_serum, apply_antidote
)


class CmdMilkVenom(Command):
    """
    Carefully extract raw venom from a subdued serpent or arachnid into a glass phial.

    Usage:
      milkvenom
      milkvenom <viper|spider|scorpion>
    """

    key = "milkvenom"
    aliases = ["extractvenom", "harvestvenom"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        creature = self.args.strip() or "viper"
        ok, msg = milk_creature_venom(caller, creature)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBrewAntidote(Command):
    """
    Distill raw venom over activated charcoal to formulate an effective antidote.

    Usage:
      brewantidote
      distillantidote
    """

    key = "brewantidote"
    aliases = ["makeantidote", "distillantidote"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = brew_antidote_serum(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdApplyAntidote(Command):
    """
    Administer an anti-venom serum to yourself or an ally to cure all poison.

    Usage:
      applyantidote
      applyantidote <target>
    """

    key = "applyantidote"
    aliases = ["curepoison", "giveantidote"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        ok, msg = apply_antidote(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")

