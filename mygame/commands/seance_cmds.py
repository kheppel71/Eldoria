"""
Nightmare LPmud Séance Commands.
"""

from evennia.commands.command import Command
from world.nightmare_seance import (
    begin_seance, summon_spectral_spirit, question_spectral_ghost
)


class CmdSeance(Command):
    """
    Light black candles around a spirit board to initiate an occult séance.

    Usage:
      seance
      spiritcircle
    """

    key = "seance"
    aliases = ["spiritcircle", "holdseance"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        ok, msg = begin_seance(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdSummonSpirit(Command):
    """
    Call forth a deceased ghost or spectral apparition into the séance circle.

    Usage:
      summonspirit
      summonspirit <name>
    """

    key = "summonspirit"
    aliases = ["callghost", "summonghost"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        spirit_name = self.args.strip() or "Ghost of Lady Eleanor"
        ok, msg = summon_spectral_spirit(caller, spirit_name)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdQuestionGhost(Command):
    """
    Commune with and interrogate a summoned ghost through the spirit board planchette.

    Usage:
      questionghost <treasure|curse|murder>
    """

    key = "questionghost"
    aliases = ["speakwithdead", "askghost"]
    locks = "cmd:all()"
    help_category = "Spells"

    def func(self):
        caller = self.caller
        topic = self.args.strip() or "treasure"
        ok, msg = question_spectral_ghost(caller, topic)
        if not ok:
            caller.msg(f"|r{msg}|n")

