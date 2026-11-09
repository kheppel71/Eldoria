"""
Nightmare LPmud Shipwright & Sailing Commands.
"""

from evennia.commands.command import Command
from world.nightmare_shipwright import (
    build_vessel, board_vessel, sail_vessel, toggle_anchor
)


class CmdBuildShip(Command):
    """
    Construct a seafaring vessel using shipwright tools and timber.

    Usage:
      buildship <canoe|dinghy|sloop>
    """

    key = "buildship"
    aliases = ["craftship", "shipwright"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        vessel_choice = self.args.strip() or "dinghy"
        ok, msg = build_vessel(caller, vessel_choice)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdBoardShip(Command):
    """
    Board a vessel moored at the dock or beach and take the helm.

    Usage:
      boardship
      boardship <vessel>
    """

    key = "boardship"
    aliases = ["boarddinghy", "boardboat"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        ok, msg = board_vessel(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdSail(Command):
    """
    Set sail and navigate your boarded vessel into an open waterway.

    Usage:
      sail <north|south|east|west|n|s|e|w>
    """

    key = "sail"
    aliases = ["steership"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: sail <direction>")
            return

        ok, msg = sail_vessel(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdAnchorShip(Command):
    """
    Drop or raise your vessel's anchor.

    Usage:
      anchorship
      raiseanchor
      dropanchor
    """

    key = "anchorship"
    aliases = ["anchor", "raiseanchor", "dropanchor"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        ok, msg = toggle_anchor(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

