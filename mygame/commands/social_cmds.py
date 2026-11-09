"""
Socials and feelings commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_socials import execute_social, SOCIALS_TABLE


class CmdFeelings(default_cmds.MuxCommand):
    """
    View the directory of expressive social feelings and emotes

    Usage:
      feelings
      socials
    """
    key = "feelings"
    aliases = ["socials"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        verbs = sorted(SOCIALS_TABLE.keys())

        caller.msg(f"\n|w====================== NIGHTMARE SOCIALS & FEELINGS ======================|n")
        caller.msg("Express emotions toward others or the room. Supports adverbs (e.g. 'bow deeply at <target>').\n")

        # Display in 4 columns
        col_width = 18
        lines = []
        cur_line = []
        for i, v in enumerate(verbs):
            cur_line.append(f"|y{v:<{col_width}}|n")
            if (i + 1) % 4 == 0:
                lines.append("".join(cur_line))
                cur_line = []
        if cur_line:
            lines.append("".join(cur_line))

        caller.msg("\n".join(lines))
        caller.msg("\n|w" + "=" * 76 + "|n\n")


class CmdSocialAction(default_cmds.MuxCommand):
    """
    Expressive social feeling action

    Usage:
      <verb>
      <verb> <target>
      <verb> <adverb> at <target>
    """
    key = "nod"
    aliases = [
        "bow", "hug", "glare", "smirk", "cower", "cheer",
        "shrug", "applaud", "wink", "giggle", "salute", "sigh"
    ]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        verb = self.cmdstring.lower()
        execute_social(caller, verb, self.args)

