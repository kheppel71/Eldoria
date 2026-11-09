"""
Scroll scribing and scroll reading commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_scribing import scribe_spell_scroll, read_magic_scroll


class CmdScribeScroll(default_cmds.MuxCommand):
    """
    Scribe a memorized spell onto blank parchment to forge a single-use spell scroll

    Usage:
      scribescroll <spell_name>
      scribe <spell_name>
    """
    key = "scribescroll"
    aliases = ["scribe"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: scribescroll <spell_name>")
            return

        parchment = None
        for obj in caller.contents:
            if "parchment" in obj.key.lower() or "paper" in obj.key.lower():
                parchment = obj
                break

        if not parchment:
            caller.msg("You need a sheet of blank parchment in your pack to scribe a spell scroll!")
            return

        ok, msg = scribe_spell_scroll(caller, self.args.strip(), parchment)
        if not ok:
            caller.msg(msg)


class CmdReadScroll(default_cmds.MuxCommand):
    """
    Read an inscribed magic scroll aloud, releasing its spell incantation

    Usage:
      readscroll <scroll>
      readscroll <scroll> at <target>
    """
    key = "readscroll"
    aliases = ["invokescroll"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Read which scroll?")
            return

        s_name = self.args.strip()
        target = None

        if "at" in self.args:
            parts = self.args.split("at", 1)
            s_name = parts[0].strip()
            t_name = parts[1].strip()
            target = caller.search(t_name, location=caller.location)
            if not target:
                return

        scroll = caller.search(s_name, location=caller)
        if not scroll:
            return

        ok, msg = read_magic_scroll(caller, scroll, target=target)
        if not ok:
            caller.msg(msg)

