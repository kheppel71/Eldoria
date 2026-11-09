"""
Nightmare LPmud Library & Lore Commands.
"""

from evennia.commands.command import Command
from world.nightmare_library import read_lore_tome, transcribe_lore_tome, format_lore_profile


class CmdReadTome(Command):
    """
    Study and decipher an ancient scholarly tome or codex.

    Usage:
      readtome <tome>
      studytome <tome>
    """

    key = "readtome"
    aliases = ["studytome", "readbook"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What ancient tome do you wish to study?")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target and caller.location:
            target = caller.location.search(self.args.strip())
        if not target:
            return

        ok, msg = read_lore_tome(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdTranscribe(Command):
    """
    Transcribe historical excerpts from an ancient codex into scholarly notes.

    Usage:
      transcribe <tome>
    """

    key = "transcribe"
    aliases = ["copytome"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What ancient tome do you wish to transcribe?")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target and caller.location:
            target = caller.location.search(self.args.strip())
        if not target:
            return

        ok, msg = transcribe_lore_tome(caller, target)
        if not ok:
            caller.msg(f"|r{msg}|n")


class CmdLore(Command):
    """
    View your archaeological knowledge dossier, studied manuscripts, and Lore ranking.

    Usage:
      lore
      scholar
    """

    key = "lore"
    aliases = ["scholar", "archaeology"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        caller.msg(format_lore_profile(caller))

