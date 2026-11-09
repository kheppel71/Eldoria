"""
Nightmare LPmud Player Housing, Physical Keys & Lockpicking System.

Implements:
1. Physical Key & Lock pairing (doors, padlocks, chests).
2. Keyring management ('keyring').
3. Rogue Lockpicking ('pick <target> with lockpick') with tumbler checks and pick breakage.
4. Player Housing Deeds & Apartment claiming.
"""

import random
from evennia.utils.create import create_object
from typeclasses.rooms import Room
from typeclasses.objects import Object
from world.nightmare_core import trigger_skill_tick


def create_lockable_chest(key_code, location, chest_name="Reinforced Iron Chest"):
    """Spawns a lockable chest with specific key pairing."""
    chest = create_object(Object, key=chest_name, location=location)
    chest.db.is_container = True
    chest.db.is_lockable = True
    chest.db.is_locked = True
    chest.db.lock_code = key_code
    chest.db.lock_difficulty = 30
    return chest


def create_physical_key(key_code, location, key_name="Ornate Brass Key"):
    """Creates a physical key tied to a specific lock code."""
    k = create_object(Object, key=key_name, location=location)
    k.db.is_key = True
    k.db.key_code = key_code
    k.db.desc = f"A finely notched brass key engraved with serial code '{key_code}'."
    return k


def lock_target(caller, target, key_obj):
    """Locks a chest or door using a matching physical key."""
    if not getattr(target.db, "is_lockable", False):
        return False, f"{target.key} does not have a lock mechanism."

    if getattr(target.db, "is_locked", False):
        return False, f"{target.key} is already locked."

    if not getattr(key_obj.db, "is_key", False):
        return False, f"{key_obj.key} is not a valid key."

    if key_obj.db.key_code != target.db.lock_code:
        return False, f"{key_obj.key} does not fit the tumbler of {target.key}."

    target.db.is_locked = True
    caller.msg(f"|yYou turn {key_obj.key} in the lock. *CLACK!* {target.key} is now locked securely.|n")
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} locks {target.key} with a solid metallic click.",
            exclude=[caller]
        )
    return True, "Locked."


def unlock_target(caller, target, key_obj):
    """Unlocks a chest or door using a matching physical key."""
    if not getattr(target.db, "is_lockable", False):
        return False, f"{target.key} does not have a lock mechanism."

    if not getattr(target.db, "is_locked", False):
        return False, f"{target.key} is already unlocked."

    if not getattr(key_obj.db, "is_key", False):
        return False, f"{key_obj.key} is not a valid key."

    if key_obj.db.key_code != target.db.lock_code:
        return False, f"{key_obj.key} does not fit the lock of {target.key}."

    target.db.is_locked = False
    caller.msg(f"|gYou slide {key_obj.key} into {target.key} and turn. *CLICK!* It unlocks smoothly.|n")
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} unlocks {target.key}.",
            exclude=[caller]
        )
    return True, "Unlocked."


def pick_lock(caller, target, lockpick):
    """Rogue lockpicking attempt against locked doors or chests."""
    if not getattr(target.db, "is_lockable", False):
        return False, f"{target.key} has no lock to pick."

    if not getattr(target.db, "is_locked", False):
        return False, f"{target.key} is already unlocked."

    if "lockpick" not in lockpick.key.lower():
        return False, f"{lockpick.key} is not a lockpick tool."

    diff = getattr(target.db, "lock_difficulty", 30) or 30
    dex = caller.db.dex or 10
    bonus = 15 if getattr(caller.db, "guild", "") == "Rogue" else 0
    roll = dex + bonus + random.randint(1, 30)

    caller.msg(f"|yYou insert the tension wrench and pick into {target.key}'s tumbler, feeling the pins...|n")

    if roll >= diff:
        target.db.is_locked = False
        trigger_skill_tick(caller, "stealth", True)
        caller.msg(f"|G*CLICK!* With delicate precision, you set the final pin! {target.key} swings unlocked!|n")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} picks open the lock on {target.key} with a soft click!",
                exclude=[caller]
            )
        return True, "Picked."
    else:
        # Failure! Check pick snap
        if random.random() < 0.35:
            pick_name = lockpick.key
            lockpick.delete()
            caller.msg(f"|R*SNAP!* Too much torque! Your {pick_name} breaks off inside the keyway!|n")
        else:
            caller.msg(f"|rThe pins slip back into place. You fail to pick the lock.|n")
        return False, "Failed."


def claim_player_house(caller, house_name):
    """Creates a persistent player cottage or apartment."""
    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    cost = 250  # 250 Gold for home deed
    if coins.get("gold", 0) < cost:
        return False, f"A residential property deed costs {cost} Gold (You have {coins.get('gold', 0)} Gold)."

    coins["gold"] -= cost
    caller.db.coins = coins

    house_room = create_object(
        Room,
        key=f"{caller.key}'s Cottage",
        attributes=[
            ("desc", f"A cozy, private residence belonging to {caller.key}. A warm stone hearth glows in the corner, and a sturdy oak chest rests near the bed."),
            ("owner_id", caller.id),
            ("terrain", "city"),
            ("is_player_house", True)
        ]
    )

    # Spawn chest and key
    key_code = f"house_{caller.id}"
    chest = create_lockable_chest(key_code, location=house_room, chest_name=f"{caller.key}'s Private Chest")
    create_physical_key(key_code, location=caller, key_name=f"Key to {caller.key}'s Cottage")

    caller.db.home_room_id = house_room.id
    caller.msg(f"\n|Y[HOME DEED PURCHASED]|n You have purchased a private residence: |w{house_room.key}|n!")
    caller.msg(f"The deed clerk hands you the key to your cottage and personal storage chest.")
    return True, "House claimed."

