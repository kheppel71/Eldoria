"""
Cartography and map drawing commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_cartography import draw_room_map, annotate_map_landmark, view_drawn_map


class CmdDrawMap(default_cmds.MuxCommand):
    """
    Survey the current location and sketch a cartographic parchment map

    Usage:
      drawmap
      cartography
    """
    key = "drawmap"
    aliases = ["chartmap"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        parchment = None
        for obj in caller.contents:
            if "vellum" in obj.key.lower() or "parchment" in obj.key.lower():
                parchment = obj
                break

        if not parchment:
            caller.msg("You need a sheet of blank vellum or parchment in your pack to draw a map!")
            return

        ok, msg = draw_room_map(caller, parchment)
        if not ok:
            caller.msg(msg)


class CmdLandmark(default_cmds.MuxCommand):
    """
    Inscribe a custom landmark or secret note onto a hand-drawn map

    Usage:
      landmark <note_text>
      landmark <note_text> on <map>
    """
    key = "landmark"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: landmark <note_text> [on <map>]")
            return

        note = self.args.strip()
        map_obj = None

        if "on" in self.args:
            parts = self.args.split("on", 1)
            note = parts[0].strip()
            m_name = parts[1].strip()
            map_obj = caller.search(m_name, location=caller)
        else:
            # Find map in pack
            for obj in caller.contents:
                if getattr(obj.db, "is_map", False):
                    map_obj = obj
                    break

        if not map_obj:
            caller.msg("You do not have a cartographic map in your pack to annotate!")
            return

        ok, msg = annotate_map_landmark(caller, map_obj, note)
        if not ok:
            caller.msg(msg)


class CmdViewMap(default_cmds.MuxCommand):
    """
    Examine the topographic survey and landmarks on a drawn map

    Usage:
      viewmap
      viewmap <map>
    """
    key = "viewmap"
    aliases = ["readmap"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        map_obj = None
        if self.args:
            map_obj = caller.search(self.args.strip(), location=caller)
        else:
            for obj in caller.contents:
                if getattr(obj.db, "is_map", False):
                    map_obj = obj
                    break

        if not map_obj:
            caller.msg("View which map?")
            return

        ok, msg = view_drawn_map(caller, map_obj)
        if not ok:
            caller.msg(msg)

