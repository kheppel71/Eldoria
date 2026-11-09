"""
Guild territory control commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_territory import TERRITORIES, claim_territory


class CmdTerritories(default_cmds.MuxCommand):
    """
    View realm strategic territory control nodes and controlling guilds

    Usage:
      territories
      strongholds
    """
    key = "territories"
    aliases = ["strongholds", "zones"]
    locks = "cmd:all()"
    help_category = "Guilds"

    def func(self):
        caller = self.caller

        caller.msg(f"\n|w====================== GUILD TERRITORY CONTROL ======================|n")
        caller.msg(f"{'Strategic Sector':<32} {'Controlling Guild':<18} {'Regional Bonus'}")
        caller.msg("|b" + "-" * 76 + "|n")

        for node_k, data in TERRITORIES.items():
            g_str = f"|c{data['controlling_guild']}|n" if data.get("controlling_guild") else "|xUnclaimed|n"
            caller.msg(f"|y{data['name']:<32}|n {g_str:<28} |g{data['buff']}|n")

        caller.msg("|b" + "-" * 76 + "|n")
        caller.msg("To capture a sector for your guild: |wclaim <territory_key>|n\n")


class CmdClaimTerritory(default_cmds.MuxCommand):
    """
    Plant your guild's war banner and claim a territory

    Usage:
      claim <hive_crossroads/cathedral_gates/high_barracks/arcane_library>
    """
    key = "claim"
    aliases = ["conquer"]
    locks = "cmd:all()"
    help_category = "Guilds"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg(f"Available territory nodes: {', '.join(TERRITORIES.keys())}")
            return

        ok, msg = claim_territory(caller, self.args.strip().lower().replace(" ", "_"))
        if not ok:
            caller.msg(msg)

