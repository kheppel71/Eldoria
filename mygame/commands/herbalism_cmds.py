"""
Nightmare LPmud Herbalism, Poultice & Poison Commands.
"""

from evennia.commands.command import Command
from world.nightmare_herbalism import (
    forage_herbs, craft_poultice, apply_poultice, craft_poison, coat_weapon_with_poison
)


class CmdForage(Command):
    """
    Search the surrounding wilderness for medicinal herbs and poisonous flora.

    Usage:
      forage
      gather herbs
    """

    key = "forage"
    aliases = ["gather herbs", "herbalism"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = forage_herbs(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCraftPoultice(Command):
    """
    Crush harvested medicinal herbs into a healing poultice.

    Usage:
      craftpoultice
      makepoultice
    """

    key = "craftpoultice"
    aliases = ["makepoultice", "craft poultice"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = craft_poultice(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdApplyPoultice(Command):
    """
    Apply an herbal poultice to yourself or an injured ally to mend wounds and limbs.

    Usage:
      applypoultice
      applypoultice <target>
    """

    key = "applypoultice"
    aliases = ["usepoultice", "dresswounds"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        ok, msg = apply_poultice(caller, target=target)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCraftPoison(Command):
    """
    Distill toxic nightshade belladonna into a vial of deadly blade poison.

    Usage:
      craftpoison
      distillpoison
    """

    key = "craftpoison"
    aliases = ["distillpoison"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = craft_poison(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCoatWeapon(Command):
    """
    Coat an equipped or carried weapon with lethal poison.

    Usage:
      coatweapon
      coatweapon <weapon>
    """

    key = "coatweapon"
    aliases = ["poisonweapon", "envenom"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = coat_weapon_with_poison(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")

