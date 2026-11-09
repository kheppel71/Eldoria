"""
Wilderness foraging, monster skinning, and envenoming commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_harvest import skin_corpse, forage_herbs, apply_poison_to_weapon


class CmdSkin(default_cmds.MuxCommand):
    """
    Skin and butcher a fallen corpse for hides, pelts, and meat

    Usage:
      skin <corpse>
      butcher <corpse>
    """
    key = "skin"
    aliases = ["butcher"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        if not self.args:
            # Look for any corpse in the room
            corpse = None
            if caller.location:
                for obj in caller.location.contents:
                    if obj.key.lower().startswith("corpse"):
                        corpse = obj
                        break
            if not corpse:
                caller.msg("What corpse do you want to skin?")
                return
        else:
            corpse = caller.search(self.args.strip(), location=caller.location)
            if not corpse:
                return

        ok, msg = skin_corpse(caller, corpse)
        if not ok:
            caller.msg(msg)


class CmdForage(default_cmds.MuxCommand):
    """
    Forage the surrounding wild terrain for medicinal herbs, reagents, and roots

    Usage:
      forage
    """
    key = "forage"
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        ok, msg = forage_herbs(caller)
        if not ok:
            caller.msg(msg)


class CmdEnvenom(default_cmds.MuxCommand):
    """
    Apply a lethal venom or toxic herb to coat a blade

    Usage:
      envenom <weapon> with <poison_item>
      apply poison to <weapon>
    """
    key = "envenom"
    aliases = ["poison"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args or "with" not in self.args:
            caller.msg("Usage: envenom <weapon> with <herb_or_poison>")
            return

        parts = self.args.split("with", 1)
        w_name = parts[0].strip()
        p_name = parts[1].strip()

        weapon = caller.search(w_name, location=caller)
        if not weapon:
            # Check equipped hand slots
            equipped = getattr(caller.db, "equipped_slots", {}) or {}
            for s in ["right_hand", "left_hand"]:
                it = equipped.get(s)
                if it and it.key.lower() == w_name.lower():
                    weapon = it
                    break
        if not weapon:
            return

        poison = caller.search(p_name, location=caller)
        if not poison:
            return

        ok, msg = apply_poison_to_weapon(caller, poison, weapon)
        if not ok:
            caller.msg(msg)

