"""
Trap and hunting commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_traps import set_room_trap, scatter_caltrops


class CmdSetTrap(default_cmds.MuxCommand):
    """
    Arm and conceal a bear trap or wire snare in the room

    Usage:
      settrap <beartrap/snare>
    """
    key = "settrap"
    aliases = ["armtrap"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: settrap <beartrap/snare>")
            return

        t_type = self.args.strip().lower()
        trap_item = None
        for obj in caller.contents:
            if t_type in obj.key.lower() or "trap" in obj.key.lower() or "snare" in obj.key.lower():
                trap_item = obj
                break

        if not trap_item:
            caller.msg(f"You do not have a {t_type} kit in your inventory!")
            return

        ok, msg = set_room_trap(caller, t_type, trap_item)
        if not ok:
            caller.msg(msg)


class CmdCaltrops(default_cmds.MuxCommand):
    """
    Scatter spiked iron caltrops across the floor to hinder and puncture foes

    Usage:
      caltrops
    """
    key = "caltrops"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        caltrop_bag = None
        for obj in caller.contents:
            if "caltrop" in obj.key.lower():
                caltrop_bag = obj
                break

        if not caltrop_bag:
            caller.msg("You do not have a bag of caltrops in your pack!")
            return

        ok, msg = scatter_caltrops(caller, caltrop_bag)
        if not ok:
            caller.msg(msg)

