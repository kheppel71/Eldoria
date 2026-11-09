"""
Nightmare LPmud Courier Pigeon Commands.
"""

from evennia.commands.command import Command
from world.nightmare_pigeons import (
    format_aviary_directory, dispatch_courier_pigeon, read_pigeon_letter
)


class CmdPigeonLoft(Command):
    """
    Inspect the town rooftop aviary and homing pigeon status.

    Usage:
      pigeonloft
      aviary
    """

    key = "pigeonloft"
    aliases = ["aviary", "skymail"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_aviary_directory())


class CmdSendPigeon(Command):
    """
    Dispatch a homing courier pigeon to deliver a private letter across the realm.

    Usage:
      sendpigeon <player> <message>
    """

    key = "sendpigeon"
    aliases = ["mailpigeon", "pigeonmail"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        parts = self.args.strip().split(maxsplit=1)
        if len(parts) < 2:
            caller.msg("Usage: sendpigeon <player> <message>")
            return

        target_name = parts[0]
        msg = parts[1]

        target = caller.search(target_name, global_search=True)
        if not target:
            return

        ok, out_msg = dispatch_courier_pigeon(caller, target, msg)
        if not ok:
            caller.msg(f"|r{out_msg}|n")


class CmdReadLetter(Command):
    """
    Unroll and read a parchment letter delivered by a courier pigeon.

    Usage:
      readletter
      readmissive
    """

    key = "readletter"
    aliases = ["readmissive", "unrollletter"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        ok, msg = read_pigeon_letter(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")

