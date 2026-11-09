"""
Nightmare LPmud Tarot & Divination Commands.
"""

from evennia.commands.command import Command
from world.nightmare_tarot import draw_single_fate_card, perform_three_card_spread


class CmdDrawCard(Command):
    """
    Draw a single fate card from the Major Arcana for personal omen guidance.

    Usage:
      drawcard
      drawfate
    """

    key = "drawcard"
    aliases = ["drawfate", "tarotcard"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, card_name = draw_single_fate_card(caller)


class CmdTarotRead(Command):
    """
    Conduct a 3-card past/present/future divination spread for yourself or an ally.

    Usage:
      tarotread
      tarotread <target>
    """

    key = "tarotread"
    aliases = ["tarot", "readfate", "fortunetell"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        target_name = self.args.strip()
        target = caller.search(target_name) if target_name else caller
        if not target:
            return

        ok, msg = perform_three_card_spread(caller, target)

