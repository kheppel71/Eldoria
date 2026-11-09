"""
Nightmare LPmud Artifact Identification & Relic Lore Engine.

Implements:
1. Unidentified magical relics and weapons.
2. Divination identification ('identify <item>') via scrolls or Mage/Cleric insight.
3. Deep narrative artifact history and maker lore ('lore <item>').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_unidentified_relic(location, true_name, unidentified_name, lore_text, damage_bonus=8, value=150):
    """Spawns an unidentified relic into the world."""
    item = create_object(Object, key=unidentified_name, location=location)
    item.db.is_identified = False
    item.db.unidentified_name = unidentified_name
    item.db.true_name = true_name
    item.db.lore = lore_text
    item.db.damage_bonus = damage_bonus
    item.db.value = value
    item.db.slot = "right_hand"
    item.db.desc = f"An ancient relic of obscure origin. Faint, dormant runes are etched into the surface."
    return item


def identify_item(caller, item, use_scroll=False):
    """Identifies an item, unveiling its true name, powers, and lore."""
    if not item or item.location != caller:
        return False, "You must be holding the item to identify it."

    if getattr(item.db, "is_identified", True):
        return False, f"{item.key} has already been identified."

    # Mana check if casting divination
    if not use_scroll:
        mana = caller.db.mana or 0
        if mana < 20:
            return False, "You need at least 20 Mana to cast divination! (Requires 20 Mana or an Identify Scroll)"
        caller.db.mana -= 20

    true_name = item.db.true_name or "Enchanted Artifact"
    lore = item.db.lore or "A wondrous relic of forgotten ages."
    dmg = item.db.damage_bonus or 0

    item.db.is_identified = True
    item.key = true_name
    item.db.desc = f"{lore} (Damage Bonus: +{dmg})"

    caller.msg(f"\n|Y*** DIVINATION SUCCEEDS! ***|n")
    caller.msg(f"|yYou channel mystic perception into the runes. The dormant enchantments awaken!|n")
    caller.msg(f"|GTrue Identity Revealed:|n |w{true_name}|n (Damage Bonus: |r+{dmg}|n)")
    caller.msg(f"|xLore History:|n {lore}\n")

    if caller.location:
        caller.location.msg_contents(
            f"|mArcane azure light flashes from {caller.key}'s hands as they identify {true_name}!|n",
            exclude=[caller]
        )
    return True, "Identified."


def read_item_lore(caller, item):
    """Reads the detailed history and narrative lore of an identified item."""
    if not item:
        return False, "Inspect which item?"

    if not getattr(item.db, "is_identified", True):
        caller.msg(f"{item.key} is shrouded in mystery. You must identify it first to read its lore.")
        return False, "Not identified."

    lore = getattr(item.db, "lore", None)
    if not lore:
        caller.msg(f"{item.key} is an ordinary item with no ancient lore recorded.")
        return True, "No lore."

    caller.msg(f"\n|w=== Lore & History: {item.key} ===|n")
    caller.msg(f"  {lore}")
    caller.msg("|w" + "=" * 45 + "|n\n")
    return True, "Lore displayed."

