"""
Fishing and angling commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_fishing import attach_bait_to_rod, cast_fishing_line, reel_fishing_line


class CmdBaitHook(default_cmds.MuxCommand):
    """
    Attach bait to your fishing rod hook

    Usage:
      baithook <bait> on <rod>
      bait <bait>
    """
    key = "baithook"
    aliases = ["baitrod"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: baithook <bait> on <rod>")
            return

        if "on" in self.args:
            b_name, r_name = self.args.split("on", 1)
        else:
            b_name = self.args.strip()
            r_name = "rod"

        bait = caller.search(b_name.strip(), location=caller)
        if not bait:
            return

        rod = caller.search(r_name.strip(), location=caller)
        if not rod:
            return

        ok, msg = attach_bait_to_rod(caller, bait, rod)
        if not ok:
            caller.msg(msg)


class CmdCastLine(default_cmds.MuxCommand):
    """
    Cast your baited fishing line into nearby waters

    Usage:
      castline
      castline <rod>
    """
    key = "castline"
    aliases = ["fishline"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        rod = None
        if self.args:
            rod = caller.search(self.args.strip(), location=caller)
            if not rod:
                return
        else:
            # Find rod in pack or hands
            for obj in caller.contents:
                if "rod" in obj.key.lower() or "pole" in obj.key.lower():
                    rod = obj
                    break

        if not rod:
            caller.msg("You do not have a fishing rod!")
            return

        ok, msg = cast_fishing_line(caller, rod)
        if not ok:
            caller.msg(msg)


class CmdReelLine(default_cmds.MuxCommand):
    """
    Reel in your cast fishing line to land a catch

    Usage:
      reelline
      reel
    """
    key = "reelline"
    aliases = ["reelhook"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        ok, msg = reel_fishing_line(caller)
        if not ok:
            caller.msg(msg)

