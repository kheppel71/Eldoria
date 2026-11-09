"""
Holy turn undead and necromancy commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_necromancy import turn_undead, animate_dead, order_thrall


class CmdTurnUndead(default_cmds.MuxCommand):
    """
    Channel divine celestial light to rebuke and scorch undead

    Usage:
      turn undead
      turn <undead_target>
    """
    key = "turn"
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        target = None
        if self.args and self.args.strip() != "undead":
            target = caller.search(self.args.strip(), location=caller.location)
            if not target:
                return

        ok, msg = turn_undead(caller, target)
        if not ok:
            caller.msg(msg)


class CmdAnimateDead(default_cmds.MuxCommand):
    """
    Reanimate a fallen monster corpse into a loyal skeletal thrall

    Usage:
      animate dead
      animate <corpse>
    """
    key = "animatedead"
    aliases = ["animate", "reanimate"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        corpse = None
        if not self.args or self.args.strip() == "dead":
            # Search room for corpse
            if caller.location:
                for obj in caller.location.contents:
                    if obj.key.lower().startswith("corpse"):
                        corpse = obj
                        break
            if not corpse:
                caller.msg("No fresh corpses are present here to animate.")
                return
        else:
            corpse = caller.search(self.args.strip(), location=caller.location)
            if not corpse:
                return

        ok, msg = animate_dead(caller, corpse)
        if not ok:
            caller.msg(msg)


class CmdOrderThrall(default_cmds.MuxCommand):
    """
    Command your summoned undead minion

    Usage:
      order thrall attack <target>
      order thrall guard
      order thrall dismiss
    """
    key = "thrall"
    aliases = ["minion"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: thrall attack <target> | thrall guard | thrall dismiss")
            return

        ok, msg = order_thrall(caller, self.args.strip())
        if not ok:
            caller.msg(msg)

