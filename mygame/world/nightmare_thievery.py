"""
Nightmare LPmud Rogue Thievery, Pickpocketing & Fence System.

Implements:
1. Sneak Peek / Snoop into target's pockets and coin pouches.
2. High-stakes Pickpocketing of coins and items with contested checks.
3. Botched thefts triggering public alarms and Outlaw crime records.
4. Underworld Fences to offload stolen goods and contraband.
"""

import random
from world.nightmare_justice import record_crime
from world.nightmare_core import trigger_skill_tick, start_combat


def peek_target(caller, target):
    """
    Quietly inspects a target's pockets and carried coin purse.
    Contested check: caller Dex vs target Wis.
    """
    if target == caller:
        return False, "You search your own pockets... you know what you have."

    if getattr(target.db, "is_ghost", False):
        return False, f"{target.key} is a spirit with no physical pockets."

    caller_dex = (caller.db.dex or 10) + (10 if getattr(caller.db, "guild", "") == "Rogue" else 0)
    target_wis = target.db.wis or 10

    roll_caller = caller_dex + random.randint(1, 20)
    roll_target = target_wis + random.randint(1, 20)

    if roll_caller >= roll_target:
        # Success! Undetected inspection
        coins = target.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        inv = [o.key for o in target.contents if not o.destination][:4]
        inv_str = ", ".join(inv) if inv else "empty hands"

        caller.msg(f"\n|c[Sleight of Hand]|n You discreetly snoop through {target.key}'s pockets unnoticed:")
        caller.msg(f"  Carried Coins: |y{coins.get('gold', 0)} Gold|n, |w{coins.get('silver', 0)} Silver|n, |r{coins.get('copper', 0)} Copper|n")
        caller.msg(f"  Visible Gear: |w{inv_str}|n\n")
        trigger_skill_tick(caller, "stealth", True)
        return True, "Peek successful."
    else:
        # Failure! Target notices
        caller.msg(f"|rYou try to peer into {target.key}'s pockets, but they catch your gaze!|n")
        target.msg(f"|RYou catch {caller.key} awkwardly snooping around your belt pouch!|n")
        if caller.location:
            caller.location.msg_contents(
                f"{target.key} glares suspiciously at {caller.key}, catching them eyeing their pockets.",
                exclude=[caller, target]
            )
        return False, "Detected."


def pickpocket_target(caller, target, target_type="coins", item_name=""):
    """
    Attempts to steal coins or an item from target's person.
    """
    if target == caller:
        return False, "You cannot steal from yourself!"

    if getattr(target.db, "is_ghost", False):
        return False, f"{target.key} is a spirit; you cannot steal from ghosts."

    caller_dex = (caller.db.dex or 10) + (15 if getattr(caller.db, "guild", "") == "Rogue" else 0)
    target_defense = (target.db.wis or 10) + ((target.db.dex or 10) // 2)

    roll_caller = caller_dex + random.randint(1, 20)
    roll_target = target_defense + random.randint(1, 20)

    if roll_caller >= roll_target:
        # Successful theft!
        trigger_skill_tick(caller, "stealth", True)

        if target_type == "coins":
            t_coins = target.db.coins or {"gold": 0, "silver": 0, "copper": 0}
            avail_gold = t_coins.get("gold", 0)
            if avail_gold <= 0:
                return False, f"You slip your hand into {target.key}'s purse, but find no gold coins!"

            stolen = max(1, min(avail_gold, random.randint(2, 10)))
            t_coins["gold"] -= stolen
            target.db.coins = t_coins

            c_coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
            c_coins["gold"] = c_coins.get("gold", 0) + stolen
            caller.db.coins = c_coins

            caller.msg(f"|G[SUCCESSFUL THEFT]|n With ghostly finesse, you lift |y{stolen} Gold|n from {target.key}'s purse completely unnoticed!")
            return True, f"Stole {stolen} gold."
        else:
            # Item theft
            found_item = None
            for it in target.contents:
                if item_name.lower() in it.key.lower():
                    found_item = it
                    break

            if not found_item:
                return False, f"{target.key} does not have '{item_name}' in their pack."

            found_item.move_to(caller, quiet=True)
            caller.msg(f"|G[SUCCESSFUL THEFT]|n You deftly slip {found_item.key} out of {target.key}'s pack and into your cloak!")
            return True, f"Stole {found_item.key}."
    else:
        # Botched theft! Alarm sounds!
        caller.msg(f"\n|R*** BOTCHED THEFT! *** {target.key} grabs your wrist as your hand slips into their pocket!|n\n")
        target.msg(f"\n|R*** THIEF! *** You grab {caller.key}'s wrist right as they try to pick your pocket!|n\n")

        # Record crime and flag outlaw
        record_crime(caller, "Attempted Theft & Pickpocketing", victim=target, bounty_add=50)

        if caller.location:
            caller.location.msg_contents(
                f"|r{target.key} shouts: 'THIEF! GUARDS! {caller.key} tried to rob me!'|n",
                exclude=[caller, target]
            )

        # Retaliation
        start_combat(target, caller)
        return False, "Botched theft."


def fence_item(caller, item):
    """Sells an item to an underworld fence for quick coin."""
    if not item or item.location != caller:
        return False, "You do not have that item in your inventory."

    val = getattr(item.db, "value", 10) or 10
    fence_payout = max(1, int(val * 0.70))  # 70% fence payout

    gold = fence_payout // 100
    silver = (fence_payout % 100) // 10
    copper = fence_payout % 10

    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    coins["gold"] = coins.get("gold", 0) + gold
    coins["silver"] = coins.get("silver", 0) + silver
    coins["copper"] = coins.get("copper", 0) + copper
    caller.db.coins = coins

    item_key = item.key
    item.delete()

    caller.msg(f"|yThe underworld fence slips {item_key} beneath the counter and hands you |y{gold} Gold|n, |w{silver} Silver|n, |r{copper} Copper|n.|n")
    return True, "Fenced item."

