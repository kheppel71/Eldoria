"""
Nightmare LPmud Invasions & World Boss Command.
"""

from evennia.commands.command import Command
from world.nightmare_raids import format_raids_display, start_raid, end_raid


class CmdEvents(Command):
    """
    View active town invasions, world boss incursions, and realm defense alerts.

    Usage:
      events
      raids
      events start <goblin_siege|abyssal_rift|undead_scourge>  (Admin / Immortal)
      events end <goblin_siege|abyssal_rift|undead_scourge>    (Admin / Immortal)
    """

    key = "events"
    aliases = ["raids", "invasions"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg(format_raids_display())
            return

        parts = args.split(maxsplit=1)
        subcmd = parts[0].lower()

        if subcmd == "start":
            if not caller.check_permstring("Builder"):
                caller.msg("|rOnly realm Immortals may trigger invasions manually.|n")
                return
            if len(parts) < 2:
                caller.msg("Usage: events start <goblin_siege|abyssal_rift|undead_scourge>")
                return
            raid_id = parts[1].strip().lower()
            ok, msg = start_raid(raid_id, room=caller.location)
            caller.msg(msg)

        elif subcmd == "end":
            if not caller.check_permstring("Builder"):
                caller.msg("|rOnly realm Immortals may conclude invasions manually.|n")
                return
            if len(parts) < 2:
                caller.msg("Usage: events end <goblin_siege|abyssal_rift|undead_scourge>")
                return
            raid_id = parts[1].strip().lower()
            ok, msg = end_raid(raid_id, killer=caller)
            caller.msg(msg)
        else:
            caller.msg("Usage: events, raids, or events <start|end> <raid_id>")

