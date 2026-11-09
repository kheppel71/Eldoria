"""
Tavern dice gambling commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_gambling import play_dice_hazard


class CmdRollDice(default_cmds.MuxCommand):
    """
    Play Dragon's Hazard dice betting against the tavern house

    Usage:
      dice roll [wager_gold]
      gamble [wager_gold]
    """
    key = "dice"
    aliases = ["gamble", "hazard"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        wager = 5
        if self.args:
            parts = self.args.strip().split()
            # Check if last part is number
            try:
                wager = int(parts[-1])
            except ValueError:
                wager = 5

        if wager <= 0:
            caller.msg("Wager must be at least 1 Gold.")
            return

        ok, msg = play_dice_hazard(caller, wager_gold=wager)
        if not ok:
            caller.msg(msg)

