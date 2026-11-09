"""
Nightmare LPmud Black Market Commands.
"""

from evennia.commands.command import Command
from world.nightmare_blackmarket import (
    verify_shadow_password, format_blackmarket_display, purchase_contraband
)


class CmdWhisperPass(Command):
    """
    Whisper the rotating shadow password to the door sentry for black market entry.

    Usage:
      whisperpass <codephrase>
      shadowpass <codephrase>
    """

    key = "whisperpass"
    aliases = ["shadowpass", "passphrase"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: whisperpass <codephrase>")
            return

        ok, msg = verify_shadow_password(caller, self.args.strip())


class CmdBlackMarket(Command):
    """
    Inspect the covert black market bazaar catalog.

    Usage:
      blackmarket
      contraband
    """

    key = "blackmarket"
    aliases = ["contraband", "smugglerden"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        caller.msg(format_blackmarket_display(caller))


class CmdSmuggleBuy(Command):
    """
    Purchase illegal contraband from the shadow fence.

    Usage:
      smugglebuy <pickset|neurotoxin|papers|cloak>
    """

    key = "smugglebuy"
    aliases = ["buycontraband"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: smugglebuy <item_code> (Type 'blackmarket' to view wares)")
            return

        ok, msg = purchase_contraband(caller, self.args.strip())
        if not ok:
            caller.msg(f"|r{msg}|n")

