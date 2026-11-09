"""
Nightmare LPmud Siege Warfare Commands.
"""

from evennia.commands.command import Command
from world.nightmare_siege import (
    assault_gate_with_ram, repair_siege_gate, format_gate_status
)


class CmdRamGate(Command):
    """
    Drive a heavy battering ram into a fortified gate or portcullis.

    Usage:
      ramgate
      ramgate <gate>
      breachwall
    """

    key = "ramgate"
    aliases = ["breachwall", "ram"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = assault_gate_with_ram(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdRepairGate(Command):
    """
    Reinforce and repair damaged fortress gates using timber and iron braces.

    Usage:
      repairgate
      repairgate <gate>
    """

    key = "repairgate"
    aliases = ["fortifygate", "bracegate"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        ok, msg = repair_siege_gate(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdGateStatus(Command):
    """
    Inspect the structural integrity and breach status of a fortified gate.

    Usage:
      gatestatus
      gatestatus <gate>
    """

    key = "gatestatus"
    aliases = ["gatehealth"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        caller.msg(format_gate_status(caller, self.args.strip()))

