"""
Nightmare LPmud Mounts, Mounted Combat & Pack Beast System.

Implements:
1. Steeds & Mounts (Warhorses, Dire Wolves, Pack Mules, Armored Drakes).
2. Mounting and Dismounting mechanics ('mount', 'dismount').
3. Saddlebag storage for traveling pack beasts.
4. Devastating Mounted Charge in combat ('charge <target>').
"""

import random
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.objects import Object


MOUNT_PROFILES = {
    "warhorse": {
        "key": "Armored Warhorse",
        "desc": "A muscular, barded destrier bred for heavy cavalry charges.",
        "charge_dmg": (20, 35),
        "capacity": 100
    },
    "wolf": {
        "key": "Dire Wolf Steed",
        "desc": "A ferocious, silver-furred dire wolf with keen predatory instincts.",
        "charge_dmg": (18, 30),
        "capacity": 60
    },
    "mule": {
        "key": "Sturdy Pack Mule",
        "desc": "A sure-footed, docile beast of burden laden with reinforced leather packs.",
        "charge_dmg": (8, 15),
        "capacity": 250
    },
    "drake": {
        "key": "Armored Battle Drake",
        "desc": "A scaled reptile of draconic descent, exhaling wisps of smoke from nostrils.",
        "charge_dmg": (28, 48),
        "capacity": 120
    }
}


def create_mount(mount_type, location, owner=None):
    """Spawns a mount object in the given room."""
    data = MOUNT_PROFILES.get(mount_type, MOUNT_PROFILES["warhorse"])
    mount = create_object(Character, key=data["key"], location=location)
    mount.db.desc = data["desc"]
    mount.db.is_mount = True
    mount.db.mount_type = mount_type
    mount.db.owner_id = owner.id if owner else None
    mount.db.rider = None
    mount.db.charge_dmg = data["charge_dmg"]
    mount.db.saddlebags = []
    mount.db.capacity = data["capacity"]
    return mount


def mount_beast(rider, mount):
    """Mounts a steed."""
    if not getattr(mount.db, "is_mount", False):
        return False, f"{mount.key} is not a mountable beast!"

    if mount.location != rider.location:
        return False, f"{mount.key} is not here."

    if getattr(rider.db, "is_mounted", False):
        return False, "You are already mounted! Dismount first."

    if mount.db.rider:
        return False, f"{mount.key} is already being ridden by {mount.db.rider.key}!"

    rider.db.is_mounted = True
    rider.db.current_mount = mount
    mount.db.rider = rider

    rider.msg(f"\n|gYou swing your leg over the saddle and mount {mount.key}!|n")
    if rider.location:
        rider.location.msg_contents(
            f"{rider.key} smoothly mounts up on {mount.key}.",
            exclude=[rider]
        )
    return True, f"Mounted {mount.key}."


def dismount_beast(rider):
    """Dismounts from current mount."""
    if not getattr(rider.db, "is_mounted", False):
        return False, "You are not currently riding a mount."

    mount = getattr(rider.db, "current_mount", None)
    if mount:
        mount.db.rider = None

    rider.db.is_mounted = False
    rider.db.current_mount = None

    rider.msg("\n|yYou swing down from the saddle to the ground.|n")
    if rider.location:
        rider.location.msg_contents(
            f"{rider.key} dismounts and steps to the ground.",
            exclude=[rider]
        )
    return True, "Dismounted."


def mounted_charge(rider, target):
    """Delivers a devastating mounted charge attack into an opponent."""
    from world.nightmare_core import start_combat, is_in_combat, trigger_skill_tick

    if not getattr(rider.db, "is_mounted", False):
        return False, "You must be mounted on a steed to perform a cavalry charge!"

    mount = getattr(rider.db, "current_mount", None)
    if not mount:
        return False, "You have no active mount!"

    stamina = rider.db.stamina or 0
    if stamina < 20:
        return False, "You and your mount are too exhausted for a full charge! (Requires 20 Stamina)"

    rider.db.stamina = max(0, stamina - 20)

    dmg_min, dmg_max = getattr(mount.db, "charge_dmg", (15, 30))
    str_bonus = (rider.db.str or 10) // 2
    charge_dmg = random.randint(dmg_min, dmg_max) + str_bonus

    rider.msg(f"\n|Y*** THUNDERING CAVALRY CHARGE! ***|n")
    rider.msg(f"|yYou lower your weapon and spur {mount.key} into a ferocious galloping charge straight into {target.key}!|n")
    rider.msg(f"|rThe impact crushes {target.key} for {charge_dmg} devastating damage!|n\n")

    target.msg(f"\n|R*** CAVALRY CHARGE! *** {rider.key} thunders down upon you atop {mount.key} for {charge_dmg} crushing damage!|n\n")

    if rider.location:
        rider.location.msg_contents(
            f"|r{rider.key} charges down {target.key} atop {mount.key} with thunderous momentum!|n",
            exclude=[rider, target]
        )

    target.db.hp = max(0, (target.db.hp or 0) - charge_dmg)
    trigger_skill_tick(rider, "melee", True)

    if not is_in_combat(rider):
        start_combat(rider, target)

    return True, "Charge executed."

