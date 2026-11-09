"""
Thievery, pickpocketing and fence commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_thievery import peek_target, pickpocket_target, fence_item


class CmdPeek(default_cmds.MuxCommand):
    """
    Quietly inspect a target's pockets and coin purse

    Usage:
      peek <target>
      snoop <target>
    """
    key = "peek"
    aliases = ["snoop"]
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Peek into whose pockets?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        ok, msg = peek_target(caller, target)


class CmdSteal(default_cmds.MuxCommand):
    """
    Attempt to pickpocket coins or an item from an unsuspecting target

    Usage:
      steal coins from <target>
      steal <item> from <target>
    """
    key = "steal"
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        if not self.args or "from" not in self.args:
            caller.msg("Usage: steal coins from <target> OR steal <item> from <target>")
            return

        what, target_name = self.args.split("from", 1)
        what = what.strip().lower()
        target_name = target_name.strip()

        target = caller.search(target_name, location=caller.location)
        if not target:
            return

        if what in ["coins", "gold", "money"]:
            ok, msg = pickpocket_target(caller, target, target_type="coins")
        else:
            ok, msg = pickpocket_target(caller, target, target_type="item", item_name=what)


class CmdFence(default_cmds.MuxCommand):
    """
    Sell hot items or contraband to an underworld fence

    Usage:
      fence <item>
    """
    key = "fence"
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Fence what item?")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        ok, msg = fence_item(caller, item)

