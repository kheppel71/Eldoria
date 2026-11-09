"""
Nightmare LPmud Astrology Commands.
"""

from evennia.commands.command import Command
from world.nightmare_astrology import format_constellations_display, set_character_zodiac


class CmdStars(Command):
    """
    View the celestial star signs, your birth horoscope, and astral attunements.

    Usage:
      stars
      horoscope
      constellations
      stars choose <dragon|shadowblade|chalice|bull|comet>
    """

    key = "stars"
    aliases = ["horoscope", "constellations"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        args = self.args.strip()

        if not args:
            caller.msg(format_constellations_display(caller))
            return

        parts = args.split(maxsplit=1)
        subcmd = parts[0].lower()

        if subcmd in ("choose", "set", "align"):
            if len(parts) < 2:
                caller.msg("Usage: stars choose <sign_name>")
                return
            ok, msg = set_character_zodiac(caller, parts[1])
            caller.msg(msg)
        else:
            ok, msg = set_character_zodiac(caller, args)
            caller.msg(msg)

