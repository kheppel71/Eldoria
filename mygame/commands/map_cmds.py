"""
In-Game Mini-Map & Automap Commands for Eldoria MUD

Provides:
- 'map' or 'minimap' [radius] - Renders local 2D ASCII mini-map centered on caller
- 'map auto [on|off]' - Toggles mini-map display in room descriptions on 'look'
"""

from evennia import default_cmds
from world.minimap import get_minimap_panel, render_minimap


class CmdMap(default_cmds.MuxCommand):
    """
    Display a local ASCII mini-map of your surroundings.

    Usage:
      map
      map <radius>
      map auto [on|off]
      minimap

    Options:
      <radius>       - View radius (1 = 3x3, 2 = 5x5, 3 = 7x7). Default is 2.
      auto [on|off]  - Toggle automatic mini-map display on 'look' and movement.

    Examples:
      map
      map 1
      map auto on
      map auto off

    Note:
      Modern MUD clients (Mudlet, TinTin++, CMUD) also receive native GMCP
      Room.Info out-of-band telemetry for full graphical 2D/3D map widgets.
    """

    key = "map"
    aliases = ["minimap"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        location = caller.location

        if not location:
            caller.msg("|rYou are in the void; no map can be rendered.|n")
            return

        if not self.args:
            # Display default map
            caller.msg(get_minimap_panel(location, radius=2, caller=caller))
            return

        args = self.args.strip().split()
        subcmd = args[0].lower()

        if subcmd in ["auto", "toggle"]:
            if len(args) > 1:
                state_arg = args[1].lower()
                if state_arg in ["on", "enable", "true", "yes"]:
                    caller.db.auto_minimap = True
                    caller.msg("\n|gAuto-Minimap ENABLED!|n A mini-map will now be included when looking around.\n")
                elif state_arg in ["off", "disable", "false", "no"]:
                    caller.db.auto_minimap = False
                    caller.msg("\n|yAuto-Minimap DISABLED.|n Standard text descriptions restored.\n")
                else:
                    caller.msg("Usage: map auto [on|off]")
            else:
                curr = bool(caller.db.auto_minimap)
                new_state = not curr
                caller.db.auto_minimap = new_state
                state_txt = "|gENABLED|n" if new_state else "|rDISABLED|n"
                caller.msg(f"\nAuto-Minimap is now {state_txt}.\n")
            return

        if subcmd in ["on", "enable"]:
            caller.db.auto_minimap = True
            caller.msg("\n|gAuto-Minimap ENABLED!|n A mini-map will now be included when looking around.\n")
            return

        if subcmd in ["off", "disable"]:
            caller.db.auto_minimap = False
            caller.msg("\n|yAuto-Minimap DISABLED.|n Standard text descriptions restored.\n")
            return

        # Check numeric radius
        try:
            radius = int(subcmd)
            radius = max(1, min(radius, 3))
            caller.msg(get_minimap_panel(location, radius=radius, caller=caller))
        except ValueError:
            caller.msg("Usage: map [1-3] | map auto [on|off]")

