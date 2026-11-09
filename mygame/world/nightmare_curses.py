"""
Nightmare LPmud Cursed Items, Slot Binding & Purification Engine.

Implements:
1. Malevolent cursed items with inescapable limb bindings.
2. Curse debuffs (stamina drain, necrotic murmurs).
3. Holy purification rites ('uncurse <item>', 'purify <player>') to sever the dark bond.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_cursed_item(location, item_name="Cursed Bone Blade", slot="right_hand", curse_name="Torment"):
    """Spawns an item bearing a binding curse."""
    item = create_object(Object, key=item_name, location=location)
    item.db.is_cursed = True
    item.db.curse_name = curse_name
    item.db.slot = slot
    item.db.damage_bonus = 4
    item.db.desc = f"An ominous relic surrounded by a sickening necrotic aura. Dark tendrils seep from the hilt."
    return item


def equip_cursed_item(caller, item):
    """Equips a cursed item, fusing it to the character."""
    if not getattr(item.db, "is_cursed", False):
        return False, "Item is not cursed."

    slot = item.db.slot or "right_hand"
    equipped = getattr(caller.db, "equipped_slots", {}) or {}
    equipped[slot] = item
    caller.db.equipped_slots = equipped

    item.db.is_bound = True
    caller.db.has_active_curse = True

    caller.msg(f"\n|R*** CURSE OF BINDING! ***|n")
    caller.msg(f"|rAs you equip {item.key}, black barbed tendrils shoot outward and pierce into your flesh!|n")
    caller.msg(f"|R{item.key} fuses irreversibly to your {slot}! You cannot remove it without holy purification!|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"|rDark spectral tendrils erupt from {item.key}, fusing it tightly to {caller.key}'s body!|n",
            exclude=[caller]
        )
    return True, "Bound."


def attempt_remove_cursed(caller, item):
    """Checks whether an item can be removed or is held by an active curse."""
    if getattr(item.db, "is_cursed", False) and getattr(item.db, "is_bound", False):
        caller.msg(f"|R*AGONIZING SPASM!* You struggle to pull off {item.key}, but dark malevolent tendrils dig deeper into your bones! You cannot remove it!|n")
        return False
    return True


def uncurse_item(cleric, item, target=None):
    """Channels holy celestial power to break a binding curse."""
    subject = target or cleric

    if not getattr(item.db, "is_cursed", False):
        return False, f"{item.key} bears no dark curses."

    mana = cleric.db.mana or 0
    if mana < 30:
        return False, "You need at least 30 Mana to channel an uncursing exorcism! (Requires 30 Mana)"

    cleric.db.mana -= 30

    item.db.is_cursed = False
    item.db.is_bound = False

    # Safely unequip from subject if equipped
    equipped = getattr(subject.db, "equipped_slots", {}) or {}
    for s, it in list(equipped.items()):
        if it == item:
            equipped.pop(s, None)
            break
    subject.db.equipped_slots = equipped
    subject.db.has_active_curse = False

    cleric.msg(f"\n|Y*** HOLY EXORCISM: CURSE BROKEN! ***|n")
    cleric.msg(f"|yYou sprinkle holy water and chant the purifying rites of Solaris over {item.key}!|n")
    cleric.msg(f"|GThe dark tendrils shriek and dissolve into gray mist! {item.key} clatters harmlessly free!|n\n")

    if subject != cleric:
        subject.msg(f"\n|Y*** PURIFICATION! *** {cleric.key} exorcises the curse from {item.key}! The agonizing bond shatters!|n\n")

    if cleric.location:
        cleric.location.msg_contents(
            f"|YBrilliant sanctified light bursts forth as {cleric.key} purges the dark curse from {item.key}!|n",
            exclude=[cleric, subject]
        )
    return True, "Uncursed."

