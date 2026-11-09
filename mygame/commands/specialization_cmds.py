"""
Combat specialization commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_specialization import choose_specialization, SPECIALIZATIONS


class CmdSpecialize(default_cmds.MuxCommand):
    """
    Train with master weaponmasters to choose a permanent combat specialization

    Usage:
      specialize
      specialize <dualwield/bulwark/lethality/spellweaving>
    """
    key = "specialize"
    aliases = ["specialization", "mastery"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        my_spec = getattr(caller.db, "specialization", "None") or "None"

        if not self.args:
            caller.msg(f"\n|w================== MASTER COMBAT SPECIALIZATIONS ==================|n")
            caller.msg(f"Your Current Mastery: |y{my_spec}|n")
            caller.msg("|b" + "-" * 68 + "|n")

            for s_k, data in SPECIALIZATIONS.items():
                caller.msg(f"|y{data['name']:<26}|n (Requires Lvl {data['req_level']})")
                caller.msg(f"   |xMastery Perk:|n {data['desc']}\n")

            caller.msg("|w" + "=" * 68 + "|n")
            caller.msg("To adopt a specialization: |wspecialize <name>|n\n")
            return

        ok, msg = choose_specialization(caller, self.args.strip())
        if not ok:
            caller.msg(msg)

