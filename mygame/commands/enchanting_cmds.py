"""
Enchanting and socketing commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_enchanting import inscribe_weapon_with_rune, socket_gem_into_gear


class CmdInscribe(default_cmds.MuxCommand):
    """
    Inscribe an elemental runestone onto a weapon to imbue proc damage

    Usage:
      inscribe <weapon> with <rune>
    """
    key = "inscribe"
    aliases = ["imbue"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        if not self.args or "with" not in self.args:
            caller.msg("Usage: inscribe <weapon> with <rune>")
            return

        w_name, r_name = self.args.split("with", 1)
        w_name = w_name.strip()
        r_name = r_name.strip()

        weapon = caller.search(w_name, location=caller)
        if not weapon:
            # Check equipped hand slots
            equipped = getattr(caller.db, "equipped_slots", {}) or {}
            for s in ["right_hand", "left_hand"]:
                it = equipped.get(s)
                if it and it.key.lower() == w_name.lower():
                    weapon = it
                    break
        if not weapon:
            return

        rune = caller.search(r_name, location=caller)
        if not rune:
            return

        ok, msg = inscribe_weapon_with_rune(caller, rune, weapon)
        if not ok:
            caller.msg(msg)


class CmdSocket(default_cmds.MuxCommand):
    """
    Set a cut gemstone into an open equipment socket

    Usage:
      socket <gem> into <equipment>
    """
    key = "socket"
    aliases = ["inset"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        if not self.args or "into" not in self.args:
            caller.msg("Usage: socket <gem> into <equipment>")
            return

        g_name, eq_name = self.args.split("into", 1)
        g_name = g_name.strip()
        eq_name = eq_name.strip()

        gem = caller.search(g_name, location=caller)
        if not gem:
            return

        gear = caller.search(eq_name, location=caller)
        if not gear:
            equipped = getattr(caller.db, "equipped_slots", {}) or {}
            for s, it in equipped.items():
                if it and it.key.lower() == eq_name.lower():
                    gear = it
                    break
        if not gear:
            return

        ok, msg = socket_gem_into_gear(caller, gem, gear)
        if not ok:
            caller.msg(msg)

