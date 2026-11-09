"""
Finger, plan, and immortal wizard commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_finger_immortal import (
    get_finger_data, set_player_plan, toggle_invis, teleport_to, summon_player
)


class CmdFinger(default_cmds.MuxCommand):
    """
    Look up player character dossier and plan file

    Usage:
      finger <player>
    """
    key = "finger"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Finger who?")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        dossier = get_finger_data(target)
        if dossier:
            caller.msg(dossier)
        else:
            caller.msg(f"Could not retrieve finger information for '{self.args.strip()}'.")


class CmdPlan(default_cmds.MuxCommand):
    """
    Set your character's public .plan profile or motto

    Usage:
      plan <your text here>
      plan clear
    """
    key = "plan"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        if not self.args:
            current = getattr(caller.db, "plan", "No plan on file.")
            caller.msg(f"\n|wYour current .plan:|n\n  {current}\n\nTo update: |wplan <text>|n\n")
            return

        if self.args.strip().lower() == "clear":
            caller.db.plan = "No plan on file."
            caller.msg("Your .plan has been cleared.")
            return

        set_player_plan(caller, self.args)


class CmdInvis(default_cmds.MuxCommand):
    """
    Toggle ethereal wizard invisibility

    Usage:
      invis
      vis
    """
    key = "invis"
    aliases = ["vis"]
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        toggle_invis(caller)


class CmdGoto(default_cmds.MuxCommand):
    """
    Instantly teleport to a target room or character

    Usage:
      goto <room_or_character>
    """
    key = "goto"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Goto where or who?")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        teleport_to(caller, target)


class CmdTrans(default_cmds.MuxCommand):
    """
    Summon a player to your current location

    Usage:
      trans <player>
    """
    key = "trans"
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Trans who?")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        summon_player(caller, target)


class CmdDestruct(default_cmds.MuxCommand):
    """
    Administratively disintegrate an object from existence

    Usage:
      destruct <item>
    """
    key = "destruct"
    aliases = ["zap"]
    locks = "cmd:perm(Wizards)"
    help_category = "Admin"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Destruct what?")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target:
            target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        t_name = target.key
        target.delete()
        caller.msg(f"|R*ZAP!* {t_name} has been destructed from the universe.|n")
        if caller.location:
            caller.location.msg_contents(
                f"|rWith a flash of ozone, {t_name} ceases to exist.|n",
                exclude=[caller]
            )

