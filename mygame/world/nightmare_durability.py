"""
Nightmare LPmud Equipment Durability & Blacksmithing System.

Implements:
1. Item Durability and Condition Stages (Pristine, Good, Worn, Damaged, Cracked, Broken).
2. Combat wear and tear during attacks and defensive blocks.
3. Blacksmith repair service and mobile maintenance kits.
4. Weapon honing (sharpening) for temporary critical sharpness bonuses.
"""

CONDITION_TIERS = [
    (100, "|gPristine|n", "in flawless, pristine condition."),
    (75, "|yGood|n", "in good shape with minor scuffs."),
    (50, "|yWorn|n", "visibly worn and battered from battle."),
    (25, "|rDamaged|n", "heavily dented and nicked."),
    (1, "|rCracked / Notched|n", "severely fractured and near destruction!"),
    (0, "|RBROKEN|n", "completely broken and unusable until repaired!")
]


def init_item_durability(item, max_dur=100):
    """Ensures an item has durability attributes."""
    if not hasattr(item, "db"):
        return
    if item.db.max_durability is None:
        item.db.max_durability = max_dur
    if item.db.durability is None:
        item.db.durability = item.db.max_durability
    if item.db.is_broken is None:
        item.db.is_broken = False


def get_item_condition(item):
    """Returns the condition tier tuple: (percentage, tier_label, description)."""
    init_item_durability(item)
    max_d = item.db.max_durability or 100
    cur_d = item.db.durability or 0
    pct = int((cur_d / max_d) * 100) if max_d > 0 else 0

    for thresh, label, desc in CONDITION_TIERS:
        if pct >= thresh:
            return pct, label, desc
    return 0, "|RBROKEN|n", "completely broken."


def apply_wear(item, amount=1, owner=None):
    """
    Reduces item durability through combat strain.
    If durability reaches 0, the item breaks!
    """
    init_item_durability(item)
    if item.db.durability <= 0:
        return

    item.db.durability = max(0, item.db.durability - amount)
    if item.db.durability == 0 and not item.db.is_broken:
        item.db.is_broken = True
        if owner:
            owner.msg(f"|R*** CRACK! *** Your {item.key} has broken from severe combat strain!|n")
            if owner.location:
                owner.location.msg_contents(
                    f"|rWith a sharp metallic snap, {owner.key}'s {item.key} shatters and breaks!|n",
                    exclude=[owner]
                )


def repair_item(caller, item, cost_per_point=1):
    """
    Restores an item's durability to full at a blacksmith forge.
    Cost is charged in Silver coins (1 silver per point of damage).
    """
    init_item_durability(item)
    max_d = item.db.max_durability or 100
    cur_d = item.db.durability or 0
    missing = max_d - cur_d

    if missing <= 0:
        return False, f"{item.key} is already in pristine condition and requires no repairs."

    cost_silver = missing * cost_per_point
    cost_gold = cost_silver // 10
    rem_silver = cost_silver % 10

    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    total_caller_silver = (coins.get("gold", 0) * 10) + coins.get("silver", 0)

    if total_caller_silver < cost_silver:
        return False, f"Repairing {item.key} costs {cost_silver} Silver ({cost_gold} Gold, {rem_silver} Silver). You do not have enough coins."

    # Deduct cost
    total_caller_silver -= cost_silver
    coins["gold"] = total_caller_silver // 10
    coins["silver"] = total_caller_silver % 10
    caller.db.coins = coins

    item.db.durability = max_d
    item.db.is_broken = False

    return True, f"The blacksmith hammers and quenches your {item.key}, restoring it to |gPristine|n condition for {cost_silver} Silver!"


def sharpen_weapon(caller, weapon):
    """Hones a blade with a whetstone, adding a temporary +2 damage hone bonus."""
    init_item_durability(weapon)
    if weapon.db.is_broken:
        return False, f"{weapon.key} is broken and cannot be sharpened until repaired!"

    weapon.db.hone_bonus = 2
    weapon.db.hone_charges = 20  # Lasts for 20 strikes

    return True, f"You run a whetstone along the edge of {weapon.key}, honing it to razor sharpness! (+2 Damage for 20 strikes)"

