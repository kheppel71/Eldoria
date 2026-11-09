"""
Nightmare LPmud Mercenary Commands.
"""

from evennia.commands.command import Command
from world.nightmare_hirelings import (
    format_hirelings_display, hire_mercenary, order_mercenary, dismiss_mercenary
)


class CmdHirelings(Command):
    """
    View the roster of available mercenaries and sellswords for hire.

    Usage:
      hirelings
      mercenaries
    """

    key = "hirelings"
    aliases = ["mercenaries"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_hirelings_display())


class CmdHire(Command):
    """
    Hire a mercenary companion to fight by your side.

    Usage:
      hire <duran|lyra|eldrin>
    """

    key = "hire"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: hire <mercenary_name> (Type 'hirelings' to view roster)")
            return

        ok, msg = hire_mercenary(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdOrderHireling(Command):
    """
    Issue tactical orders to your contracted mercenary.

    Usage:
      order <follow|guard|attack [target]>
      order <hireling> <follow|guard|attack [target]>
    """

    key = "order"
    aliases = ["command"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: order <follow|guard|attack [target]>")
            return

        parts = self.args.strip().split(maxsplit=1)
        # If first part is a command keyword like follow or guard
        if parts[0].lower() in ("follow", "guard", "attack"):
            ok, msg = order_mercenary(caller, "", self.args.strip())
        else:
            merc_name = parts[0]
            cmd_str = parts[1] if len(parts) > 1 else "guard"
            ok, msg = order_mercenary(caller, merc_name, cmd_str)

        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDismissHireling(Command):
    """
    Dismiss your hired companion from service.

    Usage:
      dismiss
      dismiss <hireling>
    """

    key = "dismiss"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = dismiss_mercenary(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")

