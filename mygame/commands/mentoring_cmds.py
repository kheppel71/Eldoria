"""
Player mentoring and novice channel commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_mentoring import register_as_guide, broadcast_newbie_channel, establish_tutoring


class CmdGuide(default_cmds.MuxCommand):
    """
    Enlist as an official Realm Guide to mentor newcomers

    Usage:
      guide
    """
    key = "guide"
    aliases = ["guideenlist"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        ok, msg = register_as_guide(caller)
        if not ok:
            caller.msg(msg)


class CmdNewbie(default_cmds.MuxCommand):
    """
    Speak on the global novice advice and assistance channel

    Usage:
      newbie <question_or_advice>
    """
    key = "newbie"
    aliases = ["novice"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: newbie <message>")
            return

        broadcast_newbie_channel(caller, self.args)


class CmdTutor(default_cmds.MuxCommand):
    """
    Take an apprentice under your wing for a +15% shared XP bonus

    Usage:
      tutor <novice_player>
    """
    key = "tutor"
    aliases = ["apprentice"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Tutor which novice player?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        ok, msg = establish_tutoring(caller, target)
        if not ok:
            caller.msg(msg)

