"""
Disguise and scrutiny commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_disguise import apply_disguise, remove_disguise, scrutinize_target


class CmdDisguise(default_cmds.MuxCommand):
    """
    Assume a false identity using a theatrical disguise kit

    Usage:
      disguise as <fake_name>
    """
    key = "disguise"
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        if not self.args or "as" not in self.args:
            caller.msg("Usage: disguise as <fake_name>")
            return

        fake_name = self.args.split("as", 1)[1].strip()

        kit = None
        for obj in caller.contents:
            if getattr(obj.db, "is_disguise_kit", False) or "disguise" in obj.key.lower():
                kit = obj
                break

        if not kit:
            caller.msg("You do not have a disguise kit in your inventory!")
            return

        ok, msg = apply_disguise(caller, fake_name, kit)
        if not ok:
            caller.msg(msg)


class CmdUnmask(default_cmds.MuxCommand):
    """
    Remove your disguise and reveal your true identity

    Usage:
      unmask
    """
    key = "unmask"
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        ok, msg = remove_disguise(caller)
        if not ok:
            caller.msg(msg)


class CmdScrutinize(default_cmds.MuxCommand):
    """
    Carefully inspect a suspicious character to detect a false disguise

    Usage:
      scrutinize <target>
    """
    key = "scrutinize"
    aliases = ["inspectperson"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Scrutinize who?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        scrutinize_target(caller, target)

