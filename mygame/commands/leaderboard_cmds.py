"""
Nightmare LPmud Leaderboard Command.
"""

from evennia.commands.command import Command
from world.nightmare_leaderboards import format_leaderboard_display


class CmdLeaderboards(Command):
    """
    View the Hall of Champions and realm rankings.

    Usage:
      leaderboards
      rankings
      top [arena|quests|wealth|champions]
    """

    key = "leaderboards"
    aliases = ["rankings", "top", "champions"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        category = self.args.strip().lower() or "all"
        caller.msg(format_leaderboard_display(category))

