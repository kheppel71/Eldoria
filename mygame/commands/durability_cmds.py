"""
Equipment durability and blacksmithing commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_durability import (
    get_item_condition, repair_item, sharpen_weapon, init_item_durability
)


class CmdCondition(default_cmds.MuxCommand):
    """
    Inspect the structural durability and condition of equipment

    Usage:
      condition
      condition <item>
      durability
    """
    key = "condition"
    aliases = ["durability", "cond"]
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        caller = self.caller

        if self.args:
            target = caller.search(self.args.strip(), location=caller)
            if not target:
                target = caller.search(self.args.strip(), location=caller.location)
            if not target:
                return

            init_item_durability(target)
            pct, label, desc = get_item_condition(target)
            cur = target.db.durability or 0
            max_d = target.db.max_durability or 100

            caller.msg(f"\n|w=== Condition: {target.key} ===|n")
            caller.msg(f"Durability: {cur}/{max_d} [{pct}%] - Status: {label}")
            caller.msg(f"Evaluation: It is {desc}")
            hone = target.db.hone_bonus
            if hone:
                caller.msg(f"Sharpened: |y+{hone} Damage bonus ({target.db.hone_charges or 0} strikes remaining)|n")
            caller.msg("|w" + "=" * 32 + "|n\n")
            return

        # Overview of all equipped gear
        equipped = getattr(caller.db, "equipped_slots", {}) or {}
        caller.msg(f"\n|w====================== EQUIPPED GEAR CONDITION ======================|n")
        caller.msg(f"{'Slot':<14} {'Item':<26} {'Durability':<14} {'Condition'}")
        caller.msg("|b" + "-" * 70 + "|n")

        if not equipped:
            caller.msg("You are not currently wearing or wielding any equipment.")
        else:
            for slot, item in equipped.items():
                if not item:
                    continue
                init_item_durability(item)
                pct, label, _ = get_item_condition(item)
                cur = item.db.durability or 0
                max_d = item.db.max_durability or 100
                dur_str = f"{cur}/{max_d} ({pct}%)"
                caller.msg(f"{slot.replace('_', ' ').title():<14} {item.key:<26} {dur_str:<14} {label}")

        caller.msg("|b" + "-" * 70 + "|n")
        caller.msg("To repair damaged equipment: |wrepair <item>|n at the Blacksmith.\n")


class CmdRepair(default_cmds.MuxCommand):
    """
    Commission a blacksmith to repair your damaged equipment

    Usage:
      repair <item>
    """
    key = "repair"
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: repair <item>")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target:
            # Check equipped
            equipped = getattr(caller.db, "equipped_slots", {}) or {}
            for s, it in equipped.items():
                if it and it.key.lower() == self.args.strip().lower():
                    target = it
                    break
        if not target:
            caller.msg(f"Could not find '{self.args.strip()}' to repair.")
            return

        ok, msg = repair_item(caller, target)
        caller.msg(msg)


class CmdSharpen(default_cmds.MuxCommand):
    """
    Hone your weapon with a whetstone for bonus combat damage

    Usage:
      sharpen <weapon>
      hone <weapon>
    """
    key = "sharpen"
    aliases = ["hone"]
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: sharpen <weapon>")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target:
            # Check equipped hand slots
            equipped = getattr(caller.db, "equipped_slots", {}) or {}
            for s in ["right_hand", "left_hand"]:
                it = equipped.get(s)
                if it and it.key.lower() == self.args.strip().lower():
                    target = it
                    break
        if not target:
            caller.msg(f"Could not find '{self.args.strip()}' in your hands or pack.")
            return

        ok, msg = sharpen_weapon(caller, target)
        caller.msg(msg)

