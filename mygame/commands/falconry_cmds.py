"""
Nightmare LPmud Falconry & Hunting Bird Commands.
"""

from evennia.commands.command import Command
from world.nightmare_falconry import (
    call_hunting_bird, scout_with_bird, hunt_quarry_with_bird, feed_hunting_bird
)


class CmdCallHawk(Command):
    """
    Call a trained bird of prey to perch upon your leather falconry gauntlet.

    Usage:
      callhawk
      callhawk <falcon|harrier|owl>
    """

    key = "callhawk"
    aliases = ["falcon", "birdcall"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        breed = self.args.strip() or "falcon"
        ok, msg = call_hunting_bird(caller, breed)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdSendHawk(Command):
    """
    Send your perched hunting bird on an aerial mission.

    Usage:
      sendhawk scout <direction>
      sendhawk strike
    """

    key = "sendhawk"
    aliases = ["hawk", "falconry"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        args = self.args.strip().split()

        if not args:
            caller.msg("Usage: sendhawk scout <direction>  OR  sendhawk strike")
            return

        action = args[0].lower()
        if action == "scout":
            direction = args[1] if len(args) > 1 else "north"
            ok, msg = scout_with_bird(caller, direction)
            if not ok:
                caller.msg(f"|r{msg}|n")
        elif action in ("strike", "hunt"):
            ok, msg = hunt_quarry_with_bird(caller)
            if not ok:
                caller.msg(f"|r{msg}|n")
        else:
            caller.msg("Usage: sendhawk scout <direction>  OR  sendhawk strike")


class CmdFeedHawk(Command):
    """
    Feed your companion bird fresh meat to maintain its loyalty.

    Usage:
      feedhawk
      feedbird
    """

    key = "feedhawk"
    aliases = ["feedbird"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = feed_hunting_bird(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

