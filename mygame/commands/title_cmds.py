"""
Title and renown accolade commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_titles import (
    init_character_titles, set_active_title, get_full_titled_name
)


class CmdTitles(default_cmds.MuxCommand):
    """
    Inspect your unlocked renown prefixes, heroic epithets, and active title

    Usage:
      titles
      title set <title_name>
    """
    key = "titles"
    aliases = ["title", "accolades"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_character_titles(caller)

        if self.args:
            parts = self.args.strip().split(None, 1)
            if parts[0].lower() == "set" and len(parts) > 1:
                ok, msg = set_active_title(caller, parts[1])
                if not ok:
                    caller.msg(msg)
                return
            else:
                ok, msg = set_active_title(caller, self.args.strip())
                if not ok:
                    caller.msg(msg)
                return

        full_name = get_full_titled_name(caller)
        prefixes = caller.db.unlocked_prefixes or ["None"]
        epithets = caller.db.unlocked_epithets or ["the Novice Adventurer"]

        caller.msg(f"\n|w===================== RENOWN TITLES & ACCOLADES =====================|n")
        caller.msg(f"Full Titled Name: |c{full_name}|n\n")

        caller.msg("|yUnlocked Honorific Prefixes:|n")
        for p in prefixes:
            star = "|g[*]|n " if p == caller.db.active_prefix else "    "
            caller.msg(f"{star}|w{p}|n")

        caller.msg("\n|yUnlocked Heroic Epithets:|n")
        for e in epithets:
            star = "|g[*]|n " if e == caller.db.active_epithet else "    "
            caller.msg(f"{star}|w{e}|n")

        caller.msg("|w" + "=" * 67 + "|n")
        caller.msg("To change active title: |wtitle set <title_name>|n\n")


class CmdSetTitle(default_cmds.MuxCommand):
    """
    Set active title or epithet.

    Usage:
      settitle <title_name>
    """
    key = "settitle"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: settitle <title_name>")
            return
        ok, msg = set_active_title(caller, self.args.strip())
        if not ok:
            caller.msg(msg)
