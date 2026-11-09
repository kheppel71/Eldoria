"""
Nightmare LPmud Spelunking Commands.
"""

from evennia.commands.command import Command
from world.nightmare_spelunking import (
    tie_rappelling_rope, execute_rappel, anchor_chasm_bridge
)


class CmdTieRope(Command):
    """
    Anchor climbing rope to a stone outcrop or cavern rim to rig a rappelling line.

    Usage:
      tierope
      anchorline
    """

    key = "tierope"
    aliases = ["anchorline", "rigrope"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        ok, msg = tie_rappelling_rope(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdRappel(Command):
    """
    Rappel down a dark vertical cavern shaft or ascend back up.

    Usage:
      rappel
      rappel <down|up>
    """

    key = "rappel"
    aliases = ["descendrope", "ascendrope"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        direction = self.args.strip() or "down"
        ok, msg = execute_rappel(caller, direction)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdAnchorBridge(Command):
    """
    Tension a rope traverse bridge across a bottomless abyss or cavern chasm.

    Usage:
      anchorbridge
      rigbridge
    """

    key = "anchorbridge"
    aliases = ["rigbridge", "crosschasm"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        ok, msg = anchor_chasm_bridge(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

