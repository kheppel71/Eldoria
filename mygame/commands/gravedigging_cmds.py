"""
Nightmare LPmud Gravedigging Command.
"""

from evennia.commands.command import Command
from world.nightmare_gravedigging import perform_excavation


class CmdDig(Command):
    """
    Excavate graveyard soil, crypt vaults, and ancient burial mounds for relics.

    Usage:
      dig
      excavate

    Requires an iron shovel or spade in inventory.
    Be wary of resting crypt ghouls and tomb wraiths!
    """

    key = "dig"
    aliases = ["excavate"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        ok, msg = perform_excavation(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

