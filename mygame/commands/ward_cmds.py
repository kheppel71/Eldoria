"""
Nightmare LPmud Ward & Rune Commands.
"""

from evennia.commands.command import Command
from world.nightmare_wards import carve_ward, disarm_ward


class CmdCarveRune(Command):
    """
    Carve a protective ward or explosive sigil into the room or an object.

    Usage:
      carverune <alarm|frost|explosive>
      etchglyph <alarm|frost|explosive> on <object>
    """

    key = "carverune"
    aliases = ["etchglyph", "ward"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg("Usage: carverune <alarm|frost|explosive> [on <target>]")
            return

        target_obj = None
        ward_type = args

        if " on " in args.lower():
            parts = args.lower().split(" on ", 1)
            ward_type = parts[0].strip()
            target_name = parts[1].strip()
            target_obj = caller.search(target_name, location=caller) or (caller.location.search(target_name) if caller.location else None)
            if not target_obj:
                return

        ok, msg = carve_ward(caller, ward_type, target_obj)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDisarmGlyph(Command):
    """
    Carefully dismantle and defuse a magical ward or explosive floor rune.

    Usage:
      disarmglyph
      disarmglyph <object>
    """

    key = "disarmglyph"
    aliases = ["disarmward", "unward"]
    locks = "cmd:all()"
    help_category = "Adventure"

    def func(self):
        caller = self.caller
        target_obj = None
        if self.args:
            target_obj = caller.search(self.args.strip(), location=caller) or (caller.location.search(self.args.strip()) if caller.location else None)
            if not target_obj:
                return

        ok, msg = disarm_ward(caller, target_obj)
        if not ok:
            caller.msg(f"|r{msg}|n")

