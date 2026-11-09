"""
Grand Arena dueling commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_arena import (
    challenge_duel, accept_duel, get_or_create_spectator_stands
)


class CmdDuel(default_cmds.MuxCommand):
    """
    Challenge an adventurer to a formal arena duel or accept a pending challenge

    Usage:
      duel challenge <player> [wager_gold]
      duel accept
    """
    key = "duel"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: duel challenge <player> [wager_gold] OR duel accept")
            return

        parts = self.args.strip().split()
        subcmd = parts[0].lower()

        if subcmd == "accept":
            ok, msg = accept_duel(caller)
            if not ok:
                caller.msg(msg)

        elif subcmd == "challenge":
            if len(parts) < 2:
                caller.msg("Usage: duel challenge <player> [wager_gold]")
                return
            target_name = parts[1]
            wager = 0
            if len(parts) >= 3:
                try:
                    wager = int(parts[2])
                except ValueError:
                    wager = 0

            target = caller.search(target_name)
            if not target:
                return

            ok, msg = challenge_duel(caller, target, wager=wager)
            if not ok:
                caller.msg(msg)
        else:
            caller.msg("Usage: duel challenge <player> [wager_gold] OR duel accept")


class CmdSpectate(default_cmds.MuxCommand):
    """
    Take a seat in the Grand Colosseum spectator balcony to watch duels

    Usage:
      spectate
    """
    key = "spectate"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        stands = get_or_create_spectator_stands()
        caller.move_to(stands, quiet=True)
        caller.msg(f"\n|cYou take your place among the spectators in {stands.key}, overlooking the blood sands!|n\n")

