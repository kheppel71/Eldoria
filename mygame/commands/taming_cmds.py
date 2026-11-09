"""
Animal taming and pet companion commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_taming import tame_wild_beast, order_companion, feed_companion


class CmdTame(default_cmds.MuxCommand):
    """
    Tame a wild beast into a loyal bonded companion using fresh meat

    Usage:
      tame <beast> with <meat>
      tame <beast>
    """
    key = "tame"
    aliases = ["befriend"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Tame what beast?")
            return

        b_name = self.args.split("with")[0].strip()
        target_beast = caller.search(b_name, location=caller.location)
        if not target_beast:
            return

        meat = None
        for obj in caller.contents:
            if "meat" in obj.key.lower() or "steak" in obj.key.lower() or "venison" in obj.key.lower():
                meat = obj
                break

        if not meat:
            caller.msg("You need fresh or roasted meat in your pack to tame wild beasts!")
            return

        ok, msg = tame_wild_beast(caller, target_beast, meat)
        if not ok:
            caller.msg(msg)


class CmdPet(default_cmds.MuxCommand):
    """
    Issue commands to your bonded animal companion

    Usage:
      pet attack <target>
      pet heel
      pet stay
      pet release
    """
    key = "pet"
    aliases = ["companion"]
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        if not self.args:
            pet = getattr(caller.db, "active_companion", None)
            if pet and pet.pk:
                caller.msg(f"\n|wActive Companion:|n |y{pet.key}|n (HP: {pet.db.hp}/{pet.db.max_hp})")
                caller.msg("Commands: |wpet attack <target>|n, |wpet heel|n, |wpet stay|n, |wpet release|n\n")
            else:
                caller.msg("You do not have an active animal companion. Tame one with: |wtame <beast> with <meat>|n")
            return

        ok, msg = order_companion(caller, self.args.strip())
        if not ok:
            caller.msg(msg)


class CmdFeedPet(default_cmds.MuxCommand):
    """
    Feed meat to your animal companion to heal their wounds

    Usage:
      feedpet
      feedpet with <meat>
    """
    key = "feedpet"
    locks = "cmd:all()"
    help_category = "Wilderness"

    def func(self):
        caller = self.caller
        pet = getattr(caller.db, "active_companion", None)
        if not pet or not pet.pk:
            caller.msg("You have no animal companion to feed.")
            return

        meat = None
        for obj in caller.contents:
            if "meat" in obj.key.lower() or "steak" in obj.key.lower():
                meat = obj
                break

        if not meat:
            caller.msg("You do not have any meat in your pack to feed your companion.")
            return

        ok, msg = feed_companion(caller, pet, meat)
        if not ok:
            caller.msg(msg)

