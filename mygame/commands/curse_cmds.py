"""
Uncurse and purification commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_curses import uncurse_item


class CmdUncurse(default_cmds.MuxCommand):
    """
    Channel holy power to shatter a cursed binding fusing an item to flesh

    Usage:
      uncurse <item>
      uncurse <item> on <player>
    """
    key = "uncurse"
    aliases = ["purifycurse", "exorcise"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Uncurse which item?")
            return

        target_char = caller
        item_name = self.args.strip()

        if "on" in self.args:
            parts = self.args.split("on", 1)
            item_name = parts[0].strip()
            target_name = parts[1].strip()
            target_char = caller.search(target_name, location=caller.location)
            if not target_char:
                return

        # Search equipped or inventory
        equipped = getattr(target_char.db, "equipped_slots", {}) or {}
        item = None
        for s, it in equipped.items():
            if it and it.key.lower() == item_name.lower():
                item = it
                break

        if not item:
            item = target_char.search(item_name, location=target_char)
        if not item:
            caller.msg(f"Could not find '{item_name}'.")
            return

        ok, msg = uncurse_item(caller, item, target=target_char)
        if not ok:
            caller.msg(msg)

