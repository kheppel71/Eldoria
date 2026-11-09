"""
Identification and lore commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_identification import identify_item, read_item_lore


class CmdIdentify(default_cmds.MuxCommand):
    """
    Cast divination to unveil an item's true identity, damage, and enchantments

    Usage:
      identify <item>
    """
    key = "identify"
    aliases = ["id"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Identify what item?")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        ok, msg = identify_item(caller, item)
        if not ok:
            caller.msg(msg)


class CmdLore(default_cmds.MuxCommand):
    """
    Read the ancient history and narrative lore of an identified artifact

    Usage:
      lore <item>
    """
    key = "lore"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Read lore of what item?")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            item = caller.search(self.args.strip(), location=caller.location)
        if not item:
            return

        read_item_lore(caller, item)

