"""
Weapon sheathing and drawing commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_scabbards import sheathe_weapon, draw_weapon


class CmdSheathe(default_cmds.MuxCommand):
    """
    Sheathe your equipped weapon into a leather scabbard

    Usage:
      sheathe <weapon>
      sheathe
    """
    key = "sheathe"
    aliases = ["sheath"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        weapon = None

        if self.args:
            weapon = caller.search(self.args.strip(), location=caller)
        else:
            # Check equipped right hand
            equipped = getattr(caller.db, "equipped_slots", {}) or {}
            weapon = equipped.get("right_hand") or equipped.get("left_hand")

        if not weapon:
            caller.msg("What weapon do you want to sheathe?")
            return

        ok, msg = sheathe_weapon(caller, weapon)
        if not ok:
            caller.msg(msg)


class CmdDraw(default_cmds.MuxCommand):
    """
    Quick-draw your sheathed weapon from its scabbard into your hand

    Usage:
      draw
      draw <weapon>
    """
    key = "draw"
    aliases = ["unsheathe"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = draw_weapon(caller, self.args.strip() if self.args else "")
        if not ok:
            caller.msg(msg)

