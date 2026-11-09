"""
Mining, prospecting, and smelting commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_mining import prospect_room, mine_ore_deposit, smelt_ore_into_ingot


class CmdProspect(default_cmds.MuxCommand):
    """
    Survey rocky or subterranean terrain for exposed mineral veins

    Usage:
      prospect
    """
    key = "prospect"
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        prospect_room(caller)


class CmdMineOre(default_cmds.MuxCommand):
    """
    Quarry ore chunks from an exposed mineral vein using a pickaxe

    Usage:
      mine
      quarry
    """
    key = "minerevein"
    aliases = ["quarry", "mineore"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        pick = None
        for obj in caller.contents:
            if "pick" in obj.key.lower():
                pick = obj
                break

        if not pick:
            caller.msg("You do not have a miner's pickaxe in your pack or hands!")
            return

        ok, msg = mine_ore_deposit(caller, pick)
        if not ok:
            caller.msg(msg)


class CmdSmelt(default_cmds.MuxCommand):
    """
    Melt raw ore chunks at a forge or foundry to cast refined ingots

    Usage:
      smelt <ore_item>
    """
    key = "smelt"
    aliases = ["foundry"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Smelt which raw ore chunk?")
            return

        ore = caller.search(self.args.strip(), location=caller)
        if not ore:
            return

        ok, msg = smelt_ore_into_ingot(caller, ore)
        if not ok:
            caller.msg(msg)

