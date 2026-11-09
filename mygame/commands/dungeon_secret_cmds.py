"""
Dungeon hazards, trap disarming, and secret door commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_dungeon_secrets import (
    search_dungeon_walls, disarm_dungeon_trap, push_secret_brick
)


class CmdSearchWall(default_cmds.MuxCommand):
    """
    Carefully inspect dungeon masonry for concealed traps and secret passageways

    Usage:
      searchwall
      inspectwall
    """
    key = "searchwall"
    aliases = ["inspectwall", "tapwall"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        search_dungeon_walls(caller)


class CmdDisarmTrap(default_cmds.MuxCommand):
    """
    Attempt to safely disable a detected dungeon trap mechanism

    Usage:
      disarmtrap
    """
    key = "disarmtrap"
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        ok, msg = disarm_dungeon_trap(caller)
        if not ok and msg != "Triggered.":
            caller.msg(msg)


class CmdPushBrick(default_cmds.MuxCommand):
    """
    Push a revealed stone brick to open a concealed secret passageway

    Usage:
      pushbrick
      openpassage
    """
    key = "pushbrick"
    aliases = ["openpassage"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = push_secret_brick(caller)
        if not ok:
            caller.msg(msg)

