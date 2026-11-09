"""
Nightmare LPmud Fossil & Museum Commands.
"""

from evennia.commands.command import Command
from world.nightmare_fossils import (
    clean_fossil_specimen, donate_fossil_to_museum, format_museum_display
)


class CmdCleanSpecimen(Command):
    """
    Carefully chip away rock matrix to clean and restore a prehistoric fossil.

    Usage:
      cleanspecimen
      cleanspecimen <fossil>
    """

    key = "cleanspecimen"
    aliases = ["cleanfossil", "restorefossil"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = clean_fossil_specimen(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDonateMuseum(Command):
    """
    Donate a cleaned fossil to the Praxis Museum for gold grants and curator honor.

    Usage:
      donatemuseum
      donatemuseum <fossil>
    """

    key = "donatemuseum"
    aliases = ["donatespecimen", "curatefossil"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = donate_fossil_to_museum(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdMuseum(Command):
    """
    View the curated prehistoric exhibits in the Museum of Natural History.

    Usage:
      museum
      exhibits
      fossils
    """

    key = "museum"
    aliases = ["exhibits", "fossils"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_museum_display())

