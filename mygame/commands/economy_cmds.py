"""
Merchant haggling and peddler commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_economy import peddler_buy_item


class CmdPeddler(default_cmds.MuxCommand):
    """
    Browse wares or buy trade supplies from a traveling peddler

    Usage:
      peddler
      peddler list
      peddler buy <item>
    """
    key = "peddler"
    aliases = ["wares"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        loc = caller.location
        if not loc:
            return

        peddler = None
        for obj in loc.contents:
            if getattr(obj.db, "is_peddler", False):
                peddler = obj
                break

        if not peddler:
            caller.msg("There is no peddler or traveling merchant here.")
            return

        if not self.args or self.args.strip() == "list":
            caller.msg(f"\n|w===================== {peddler.key}'s Wares =====================|n")
            caller.msg(f"{'Item':<24} {'Price (Gold)':<14} {'Description'}")
            caller.msg("|b" + "-" * 70 + "|n")

            wares = peddler.db.wares or []
            for w in wares:
                caller.msg(f"|y{w['name']:<24}|n |w{w['price']} Gold|n       |x{w['desc']}|n")

            cons = peddler.db.consignment_stock or []
            if cons:
                caller.msg("\n|cConsignment & Secondhand Goods:|n")
                for c in cons:
                    caller.msg(f"|c{c['name']:<24}|n |w{c['price']} Gold|n")

            caller.msg("|w" + "=" * 70 + "|n")
            caller.msg("To purchase: |wpeddler buy <item>|n (Haggling applied automatically!)\n")
            return

        parts = self.args.strip().split(None, 1)
        subcmd = parts[0].lower()
        item_name = parts[1].strip() if len(parts) > 1 else ""

        if subcmd == "buy":
            if not item_name:
                caller.msg("Usage: peddler buy <item>")
                return
            ok, msg = peddler_buy_item(caller, peddler, item_name)
            if not ok:
                caller.msg(msg)
        else:
            caller.msg("Usage: peddler [list | buy <item>]")

