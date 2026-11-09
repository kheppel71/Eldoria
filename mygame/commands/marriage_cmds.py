"""
Marriage and wedding ring commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_marriage import (
    propose_marriage, accept_proposal, divorce_spouse, ring_telepathy, ring_sense_spouse
)


class CmdPropose(default_cmds.MuxCommand):
    """
    Propose marriage to another adventurer

    Usage:
      propose <player>
    """
    key = "propose"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Propose to whom?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        ok, msg = propose_marriage(caller, target)
        if not ok:
            caller.msg(msg)


class CmdAcceptProposal(default_cmds.MuxCommand):
    """
    Accept a pending marriage proposal

    Usage:
      accept proposal
    """
    key = "accept proposal"
    aliases = ["accept wedding", "say yes"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        ok, msg = accept_proposal(caller)
        if not ok:
            caller.msg(msg)


class CmdDivorce(default_cmds.MuxCommand):
    """
    Legally dissolve your marriage at the town magistrate or chapel

    Usage:
      divorce
    """
    key = "divorce"
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        ok, msg = divorce_spouse(caller)
        if not ok:
            caller.msg(msg)


class CmdWeddingRing(default_cmds.MuxCommand):
    """
    Commune through your enchanted wedding ring with your spouse

    Usage:
      wring <message>
      wring sense
    """
    key = "wring"
    aliases = ["ringtalk"]
    locks = "cmd:all()"
    help_category = "Social"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: wring <message> OR wring sense")
            return

        arg = self.args.strip()
        if arg.lower() == "sense":
            ring_sense_spouse(caller)
        else:
            ring_telepathy(caller, arg)

