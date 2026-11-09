"""
Nightmare LPmud Truffle & Feast Commands.
"""

from evennia.commands.command import Command
from world.nightmare_truffles import (
    leash_truffle_hound, hunt_truffles_in_area, dig_up_truffle, cook_truffle_feast
)


class CmdLeashHound(Command):
    """
    Call forth and leash a trained truffle hunting hound.

    Usage:
      leashhound
      trufflehound
    """

    key = "leashhound"
    aliases = ["trufflehound"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = leash_truffle_hound(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdTruffleHunt(Command):
    """
    Order your truffle hound to sniff the forest floor for buried fungi.

    Usage:
      trufflehunt
      snifftruffles
    """

    key = "trufflehunt"
    aliases = ["snifftruffles"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = hunt_truffles_in_area(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdDigTruffle(Command):
    """
    Carefully dig up the subterranean truffle detected by your hound.

    Usage:
      digtruffle
      excavatetruffle
    """

    key = "digtruffle"
    aliases = ["excavatetruffle"]
    locks = "cmd:all()"
    help_category = "Survival"

    def func(self):
        caller = self.caller
        ok, msg = dig_up_truffle(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdCookFeast(Command):
    """
    Prepare a gourmet truffle banquet feast granting the Well-Fed Vitality buff.

    Usage:
      cookfeast
      preparefeast
    """

    key = "cookfeast"
    aliases = ["preparefeast", "trufflefeast"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        ok, msg = cook_truffle_feast(caller)
        if not ok:
            caller.msg(f"|r{msg}|n")

