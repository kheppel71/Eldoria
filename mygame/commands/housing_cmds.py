"""
Housing, physical keys, and lockpicking commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_housing import (
    lock_target, unlock_target, pick_lock, claim_player_house
)


class CmdLock(default_cmds.MuxCommand):
    """
    Lock a chest, gate, or door with a physical key

    Usage:
      lock <target> with <key>
    """
    key = "lock"
    locks = "cmd:all()"
    help_category = "Housing"

    def func(self):
        caller = self.caller
        if not self.args or "with" not in self.args:
            caller.msg("Usage: lock <target> with <key>")
            return

        t_name, k_name = self.args.split("with", 1)
        t_name = t_name.strip()
        k_name = k_name.strip()

        target = caller.search(t_name, location=caller.location)
        if not target:
            target = caller.search(t_name, location=caller)
        if not target:
            return

        key_obj = caller.search(k_name, location=caller)
        if not key_obj:
            return

        ok, msg = lock_target(caller, target, key_obj)
        if not ok:
            caller.msg(msg)


class CmdUnlock(default_cmds.MuxCommand):
    """
    Unlock a chest, gate, or door with a physical key

    Usage:
      unlock <target> with <key>
    """
    key = "unlock"
    locks = "cmd:all()"
    help_category = "Housing"

    def func(self):
        caller = self.caller
        if not self.args or "with" not in self.args:
            caller.msg("Usage: unlock <target> with <key>")
            return

        t_name, k_name = self.args.split("with", 1)
        t_name = t_name.strip()
        k_name = k_name.strip()

        target = caller.search(t_name, location=caller.location)
        if not target:
            target = caller.search(t_name, location=caller)
        if not target:
            return

        key_obj = caller.search(k_name, location=caller)
        if not key_obj:
            return

        ok, msg = unlock_target(caller, target, key_obj)
        if not ok:
            caller.msg(msg)


class CmdPickLock(default_cmds.MuxCommand):
    """
    Attempt to pick open a locked chest or door using lockpicks

    Usage:
      pick <target> with <lockpick>
    """
    key = "pick"
    aliases = ["picklock"]
    locks = "cmd:all()"
    help_category = "Thievery"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: pick <target> with <lockpick>")
            return

        if "with" in self.args:
            t_name, p_name = self.args.split("with", 1)
        else:
            t_name = self.args.strip()
            p_name = "lockpick"

        target = caller.search(t_name.strip(), location=caller.location)
        if not target:
            target = caller.search(t_name.strip(), location=caller)
        if not target:
            return

        pick = caller.search(p_name.strip(), location=caller)
        if not pick:
            caller.msg("You do not have a lockpick tool!")
            return

        ok, msg = pick_lock(caller, target, pick)


class CmdKeyring(default_cmds.MuxCommand):
    """
    Inspect all physical keys on your keyring

    Usage:
      keyring
      keys
    """
    key = "keyring"
    aliases = ["keys"]
    locks = "cmd:all()"
    help_category = "Housing"

    def func(self):
        caller = self.caller
        keys = [o for o in caller.contents if getattr(o.db, "is_key", False)]

        caller.msg("\n|w========================= KEYRING =========================|n")
        if not keys:
            caller.msg("You have no physical keys on your keyring.")
        else:
            for k in keys:
                caller.msg(f"  |y[*] {k.key:<30}|n (Key Code: |c{k.db.key_code}|n)")
        caller.msg("|w" + "=" * 54 + "|n\n")


class CmdBuyHouse(default_cmds.MuxCommand):
    """
    Purchase a residential deed to a private cottage in the city

    Usage:
      buyhouse <cottage_name>
    """
    key = "buyhouse"
    locks = "cmd:all()"
    help_category = "Housing"

    def func(self):
        caller = self.caller
        name = self.args.strip() if self.args else f"{caller.key}'s Cottage"
        ok, msg = claim_player_house(caller, name)
        if not ok:
            caller.msg(msg)

