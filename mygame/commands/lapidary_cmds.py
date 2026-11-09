"""
Nightmare LPmud Lapidary & Jewelry Commands.
"""

from evennia.commands.command import Command
from world.nightmare_lapidary import facet_rough_gemstone, craft_jeweled_filigree


class CmdFacetGem(Command):
    """
    Grind optical facets into rough mineral nodules using a lapidary grinding wheel.

    Usage:
      facetgem
      facetgem <rough_gem>
    """

    key = "facetgem"
    aliases = ["cutgem", "polishgem"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = facet_rough_gemstone(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCraftJewelry(Command):
    """
    Set a faceted gemstone into gold or silver wire filigree jewelry.

    Usage:
      craftjewelry <ring|pendant|circlet>
    """

    key = "craftjewelry"
    aliases = ["makejewelry", "setgem"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "ring"
        ok, msg = craft_jeweled_filigree(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")

