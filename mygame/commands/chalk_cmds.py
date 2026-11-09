"""
Nightmare LPmud Chalk Mark Commands.
"""

from evennia.commands.command import Command
from world.nightmare_chalkmarks import (
    inscribe_chalk_mark, read_room_chalk_marks, wipe_chalk_marks
)


class CmdChalkMark(Command):
    """
    Scrawl a colored chalk wayfinding symbol and note onto dungeon walls.

    Usage:
      chalkmark <arrow|skull|eye|cross> [message]
    """

    key = "chalkmark"
    aliases = ["chalk", "scrawl"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        args = self.args.strip().split(maxsplit=1)
        if not args:
            caller.msg("Usage: chalkmark <arrow|skull|eye|cross> [message]")
            return

        symbol = args[0]
        note = args[1] if len(args) > 1 else ""
        ok, msg = inscribe_chalk_mark(caller, symbol, note)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdReadMarks(Command):
    """
    Read all navigational chalk markings and warnings inscribed on the room walls.

    Usage:
      readmarks
      chalkmarks
    """

    key = "readmarks"
    aliases = ["chalkmarks", "checkmarks"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        caller.msg(read_room_chalk_marks(caller))


class CmdClearChalk(Command):
    """
    Wipe away and erase all chalk markings from the local stone walls.

    Usage:
      clearchalk
      eremarks
    """

    key = "clearchalk"
    aliases = ["eremarks", "wipemarks"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        ok, msg = wipe_chalk_marks(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

