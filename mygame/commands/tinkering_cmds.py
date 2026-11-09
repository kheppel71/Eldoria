"""
Nightmare LPmud Tinkering Commands.
"""

from evennia.commands.command import Command
from world.nightmare_tinkering import (
    craft_tinker_gadget, wind_clockwork_gadget, deploy_clockwork_decoy
)


class CmdTinker(Command):
    """
    Assemble brass gears and springs into clockwork automatons and decoys.

    Usage:
      tinker <decoy|spider|chronometer>
    """

    key = "tinker"
    aliases = ["craftgadget", "clockwork"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        choice = self.args.strip() or "decoy"
        ok, msg = craft_tinker_gadget(caller, choice)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdWindGadget(Command):
    """
    Wind the mainspring of a clockwork gadget using a brass winding key.

    Usage:
      windgadget
      windgadget <gadget>
    """

    key = "windgadget"
    aliases = ["windclockwork", "winddecoy"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = wind_clockwork_gadget(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDeployDecoy(Command):
    """
    Deploy a wound clockwork ticking decoy onto the floor to draw enemy aggro.

    Usage:
      deploydecoy
      dropdecoy
    """

    key = "deploydecoy"
    aliases = ["dropdecoy"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        ok, msg = deploy_clockwork_decoy(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

