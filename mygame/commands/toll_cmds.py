"""
Nightmare LPmud Toll Bridge Commands.
"""

from evennia.commands.command import Command
from world.nightmare_tolls import pay_bridge_toll, perform_customs_inspection


class CmdPayToll(Command):
    """
    Pay the crossing fee to lower a municipal river drawbridge or toll barrier.

    Usage:
      paytoll
      paytoll <gate>
    """

    key = "paytoll"
    aliases = ["crosstoll", "toll"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        ok, msg = pay_bridge_toll(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCustomsInspect(Command):
    """
    Inspect a traveler or yourself for smuggled black market contraband.

    Usage:
      customsinspect
      customsinspect <target>
    """

    key = "customsinspect"
    aliases = ["customs", "searchcontraband"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        caller.msg(perform_customs_inspection(caller, target))

