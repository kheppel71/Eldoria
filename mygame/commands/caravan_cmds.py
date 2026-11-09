"""
Nightmare LPmud Caravan Commands.
"""

from evennia.commands.command import Command
from world.nightmare_caravans import (
    format_caravans_display, join_caravan_escort, trigger_caravan_defense
)


class CmdCaravans(Command):
    """
    View active merchant trade caravans and overland trade routes.

    Usage:
      caravans
      routes
    """

    key = "caravans"
    aliases = ["routes", "tradecaravans"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_caravans_display())


class CmdEscortCaravan(Command):
    """
    Enlist as an armed escort guard for an overland merchant caravan.

    Usage:
      escort <praxis_desert|praxis_docks|praxis_catacombs>
      escort caravan
    """

    key = "escort"
    aliases = ["escortcaravan"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        target_route = self.args.strip() or "praxis_desert"
        ok, msg = join_caravan_escort(caller, target_route)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDefendWagon(Command):
    """
    Rally to defend the trade caravan wagon against highwayman ambushes.

    Usage:
      defendwagon
      defend wagon
    """

    key = "defendwagon"
    aliases = ["defend wagon", "protectwagon"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = trigger_caravan_defense(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

