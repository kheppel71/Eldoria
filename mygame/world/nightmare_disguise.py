"""
Nightmare LPmud Rogue Disguise, False Identity & Scrutiny Engine.

Implements:
1. Disguise Kits and False Identities ('disguise as <fake_name>').
2. Evasion of City Watch wanted checks while masked.
3. Unmasking ('unmask') and contested detection ('scrutinize <target>').
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_disguise_kit(location, charges=5):
    """Spawns a rogue disguise kit."""
    kit = create_object(Object, key="Theatrical Disguise Kit", location=location)
    kit.db.desc = "A velvet-lined case containing greasepaint, false mustaches, theatrical putty, and hooded cowls."
    kit.db.is_disguise_kit = True
    kit.db.charges = charges
    kit.db.value = 40
    return kit


def apply_disguise(caller, fake_name, kit_obj):
    """Applies a false identity using a disguise kit."""
    if not getattr(kit_obj.db, "is_disguise_kit", False) and "disguise" not in kit_obj.key.lower():
        return False, f"{kit_obj.key} is not a disguise kit!"

    charges = getattr(kit_obj.db, "charges", 1) or 1
    charges -= 1
    kit_obj.db.charges = charges
    if charges <= 0:
        kit_obj.delete()

    caller.db.disguised_name = fake_name.strip()
    caller.db.is_disguised = True

    caller.msg(f"\n|M[DISGUISE ASSUMED]|n You apply greasepaint, adjust your cowl, and assume the identity of |w{fake_name}|n!")
    caller.msg("The City Watch and passersby will perceive you under this alias.\n")
    if caller.location:
        caller.location.msg_contents(
            f"A shadowy figure pulls their cowl low and slips quietly into view.",
            exclude=[caller]
        )
    return True, "Disguised."


def remove_disguise(caller):
    """Removes active disguise, restoring true identity."""
    if not getattr(caller.db, "is_disguised", False):
        return False, "You are not currently wearing a disguise."

    old = caller.db.disguised_name
    caller.db.is_disguised = False
    caller.db.disguised_name = None

    caller.msg(f"\n|yYou wipe away the greasepaint and pull back your hood, revealing yourself as {caller.key}!|n\n")
    if caller.location:
        caller.location.msg_contents(
            f"{old} pulls back their hood, revealing their true face as {caller.key}!",
            exclude=[caller]
        )
    return True, "Unmasked."


def scrutinize_target(caller, target):
    """Contested check to see through a target's disguise."""
    if not getattr(target.db, "is_disguised", False):
        caller.msg(f"{target.key} is not wearing any disguise.")
        return True, "Not disguised."

    caller_wis = (caller.db.wis or 10) + random.randint(1, 20)
    target_stealth = (target.db.dex or 10) + (10 if getattr(target.db, "guild", "") == "Rogue" else 0) + random.randint(1, 20)

    if caller_wis >= target_stealth:
        # Pierced!
        true_name = target.key
        alias = target.db.disguised_name
        target.db.is_disguised = False
        target.db.disguised_name = None

        caller.msg(f"\n|Y[DISGUISE PIERCED!]|n You spot the theatrical greasepaint and recognize {alias} as the wanted outlaw |r{true_name}|Y!|n\n")
        target.msg(f"\n|R[DISGUISED EXPOSED!]|n {caller.key} scrutinizes your face and exposes your true identity as {true_name}!\n")

        if caller.location:
            caller.location.msg_contents(
                f"|r{caller.key} points at {alias} and shouts: 'That is no traveler, that is {true_name} in disguise!'|n",
                exclude=[caller, target]
            )
        return True, "Exposed."
    else:
        caller.msg(f"You scrutinize {target.db.disguised_name or target.key}, but notice nothing suspicious about their appearance.")
        return False, "Undetected."

