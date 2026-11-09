"""
Deity, prayer, and sacrifice commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_deities import (
    worship_deity, pray_at_altar, sacrifice_to_deity, DEITIES
)


class CmdDeities(default_cmds.MuxCommand):
    """
    View the pantheon of gods, their domains, and divine blessings

    Usage:
      deities
      gods
    """
    key = "deities"
    aliases = ["gods", "pantheon"]
    locks = "cmd:all()"
    help_category = "Religion"

    def func(self):
        caller = self.caller
        my_deity = getattr(caller.db, "deity", "None") or "None"
        favor = getattr(caller.db, "divine_favor", 0) or 0

        caller.msg(f"\n|w======================== NIGHTMARE PANTHEON ========================|n")
        caller.msg(f"Your Chosen Patron: |y{my_deity}|n    Divine Favor: |g{favor} Points|n")
        caller.msg("|b" + "-" * 70 + "|n")

        for d_k, data in DEITIES.items():
            caller.msg(f"|y{data['name']:<28}|n Domain: |c{data['domain']}|n")
            caller.msg(f"   |xBlessing:|n {data['blessing']}")
            caller.msg(f"   |xMythos:|n   {data['desc']}\n")

        caller.msg("|w" + "=" * 70 + "|n")
        caller.msg("To swear devotion: |wworship <deity_name>|n\n")


class CmdWorship(default_cmds.MuxCommand):
    """
    Dedicate your faith to a deity

    Usage:
      worship <deity_name>
    """
    key = "worship"
    locks = "cmd:all()"
    help_category = "Religion"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: worship <solaris/moradin/nocturna/khorne>")
            return

        ok, msg = worship_deity(caller, self.args.strip())
        if not ok:
            caller.msg(msg)


class CmdPray(default_cmds.MuxCommand):
    """
    Pray to your patron deity for guidance and restoration

    Usage:
      pray
    """
    key = "pray"
    locks = "cmd:all()"
    help_category = "Religion"

    def func(self):
        caller = self.caller
        ok, msg = pray_at_altar(caller)
        if not ok:
            caller.msg(msg)


class CmdSacrifice(default_cmds.MuxCommand):
    """
    Sacrifice gold coins or a relic upon the altar to earn Divine Favor

    Usage:
      sacrifice <gold_amount>
      sacrifice <item_name>
    """
    key = "sacrifice"
    locks = "cmd:all()"
    help_category = "Religion"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: sacrifice <gold_amount> OR sacrifice <item_name>")
            return

        ok, msg = sacrifice_to_deity(caller, self.args.strip())
        if not ok:
            caller.msg(msg)

