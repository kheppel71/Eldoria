"""
Taxidermy and trophy commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_trophies import craft_taxidermy_trophy, mount_trophy_on_wall


class CmdTaxidermy(default_cmds.MuxCommand):
    """
    Commission a taxidermist to preserve monster parts into a wall trophy

    Usage:
      taxidermy <pelt/skull/scale>
    """
    key = "taxidermy"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Taxidermy what monster part?")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target:
            return

        ok, msg = craft_taxidermy_trophy(caller, target)
        if not ok:
            caller.msg(msg)


class CmdMountTrophy(default_cmds.MuxCommand):
    """
    Hang a trophy plaque upon the wall of your room or guildhall

    Usage:
      mounttrophy <trophy>
    """
    key = "mounttrophy"
    aliases = ["hangtrophy"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Mount what trophy plaque?")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target:
            return

        ok, msg = mount_trophy_on_wall(caller, target)
        if not ok:
            caller.msg(msg)


class CmdTrophies(default_cmds.MuxCommand):
    """
    View trophies mounted upon the walls of this room

    Usage:
      trophies
    """
    key = "trophies"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        loc = caller.location
        if not loc:
            return

        trophies = getattr(loc.db, "wall_trophies", []) or []
        caller.msg(f"\n|w=================== MOUNTED TROPHIES: {loc.key} ===================|n")
        if not trophies:
            caller.msg("No monster trophies are mounted upon the walls here.")
        else:
            for t in trophies:
                caller.msg(f"  |Y[*] {t['name']}|n (Slain by |w{t['slayer']}|n)")
                caller.msg(f"      |x{t['desc']}|n")
        caller.msg("|w" + "=" * 65 + "|n\n")

