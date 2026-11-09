"""
Nightmare LPmud Wild Horse Taming, Mustang Breaking & Breeding Engine.

Implements:
1. Wild Steeds & Mustangs:
   - Wild Dapple Mustang
   - Untamed Prairie Courser
   - Mountain Warhorse
2. Braided Rawhide Lassoing ('lasso <horse>').
3. Bucking checks and saddle breaking ('breakhorse').
4. Equestrian Stud Breeding ('breedmounts').
5. Mount bloodline and pedigree statistics ('stableinfo').
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

WILD_EQUINES = {
    "mustang": {
        "name": "Wild Dapple Mustang",
        "speed": 12,
        "stamina": 140,
        "temperament": "Fiery & Wild",
        "desc": "A muscular wild mustang with a dappled silver coat, flaring nostrils, and windblown mane."
    },
    "courser": {
        "name": "Untamed Prairie Courser",
        "speed": 15,
        "stamina": 110,
        "temperament": "Swift & Skittish",
        "desc": "A lean, long-legged prairie mare with gleaming chestnut flanks, built for raw overland speed."
    },
    "warhorse": {
        "name": "Fierce Mountain Warhorse",
        "speed": 10,
        "stamina": 180,
        "temperament": "Aggressive & Unyielding",
        "desc": "A broad-chested dark bay draft stallion with thick feathered hooves and fearless gaze."
    }
}


def spawn_wild_horse(location, key="mustang"):
    """Spawns an untamed wild horse in the wilderness."""
    data = WILD_EQUINES.get(key, WILD_EQUINES["mustang"])
    horse = create_object(Object, key=data["name"], location=location)
    horse.db.is_horse = True
    horse.db.is_tamed = False
    horse.db.is_snared = False
    horse.db.speed = data["speed"]
    horse.db.stamina = data["stamina"]
    horse.db.temperament = data["temperament"]
    horse.db.desc = data["desc"]
    return horse


def lasso_wild_horse(caller, target_name=""):
    """Throws a braided leather lasso to snare a wild horse."""
    room = caller.location
    if not room:
        return False, "You cannot lasso in the void."

    horse = None
    for obj in room.contents:
        if getattr(obj.db, "is_horse", False) and not getattr(obj.db, "is_tamed", False):
            if not target_name or target_name.lower() in obj.key.lower():
                horse = obj
                break

    if not horse:
        return False, "There are no wild, untamed horses here to lasso."

    horse.db.is_snared = True
    caller.msg(
        f"\n|Y*WHIRRR-SNAP!*|n You twirl a braided rawhide lasso over your head and cast it forward!\n"
        f"The noose drops cleanly around {horse.key}'s neck! The wild horse whinnies and rears in panic!|n\n"
        "|yQuickly command 'breakhorse' to mount and tame the beast!|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} casts a rawhide lasso with expert precision, snaring {horse.key} around the neck!",
            exclude=[caller]
        )
    return True, "Horse snared."


def break_wild_horse(caller, target_name=""):
    """Mounts a snared horse and endures violent bucking checks to break it."""
    room = caller.location
    horse = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_horse", False) and getattr(obj.db, "is_snared", False) and not getattr(obj.db, "is_tamed", False):
            if not target_name or target_name.lower() in obj.key.lower():
                horse = obj
                break

    if not horse:
        return False, "You must snare a wild horse with a lasso first! ('lasso <horse>')"

    # Stamina test
    curr_stam = getattr(caller.db, "stamina", 100) or 100
    if curr_stam < 25:
        return False, "You are too exhausted to hold onto a bucking wild mustang! Rest your stamina first."

    caller.db.stamina = curr_stam - 20
    horse.db.is_tamed = True
    horse.db.is_snared = False
    horse.db.is_mount = True
    horse.db.owner = caller

    caller.msg(
        f"\n|Y[HORSE TAMING]|n You vault onto {horse.key}'s bare back!\n"
        f"The steed thrashes, bucks, and twists in fury, but you tighten your grip and guide its head firmly.\n"
        f"Gradually, the beast yields, its breath steadying into calm obedience. |w{horse.key}|n is TAMED!|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} bravely rides out the wild bucking of {horse.key}, earning the magnificent steed's respect!",
            exclude=[caller]
        )
    return True, "Horse tamed."


def breed_tamed_horses(caller, sire_name="", dam_name=""):
    """Breeds two tamed horses to produce a spirited foal with inherited genetics."""
    tamed_horses = [
        obj for obj in (caller.contents + (caller.location.contents if caller.location else []))
        if getattr(obj.db, "is_horse", False) and getattr(obj.db, "is_tamed", False)
    ]

    if len(tamed_horses) < 2:
        return False, "You need two tamed horses present in the area to initiate breeding!"

    h1 = tamed_horses[0]
    h2 = tamed_horses[1]

    # Calculate offspring stats
    avg_speed = int((getattr(h1.db, "speed", 12) + getattr(h2.db, "speed", 12)) / 2) + random.randint(1, 3)
    avg_stam = int((getattr(h1.db, "stamina", 120) + getattr(h2.db, "stamina", 120)) / 2) + random.randint(10, 25)

    foal = create_object(Object, key="Prized Thoroughbred Steed", location=caller.location)
    foal.db.is_horse = True
    foal.db.is_tamed = True
    foal.db.is_mount = True
    foal.db.owner = caller
    foal.db.speed = avg_speed
    foal.db.stamina = avg_stam
    foal.db.desc = f"A magnificent, pedigree thoroughbred mount bred from {h1.key} and {h2.key}. Speed: {avg_speed}, Stamina: {avg_stam}."

    caller.msg(
        f"\n|G[EQUESTRIAN BREEDING SUCCESS]|n\n"
        f"Crossing the bloodlines of {h1.key} and {h2.key} yields a |w{foal.key}|n!\n"
        f"Inherited Pedigree: |ySpeed {avg_speed}|n, |cStamina {avg_stam}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} successfully breeds {h1.key} and {h2.key}, welcoming a prized new steed to the stable!",
            exclude=[caller]
        )
    return True, f"Bred {foal.key}."


def format_stable_info(caller, target_name=""):
    """Displays detailed stats and pedigree of a mount."""
    horse = None
    for obj in (caller.contents + (caller.location.contents if caller.location else [])):
        if getattr(obj.db, "is_horse", False):
            if not target_name or target_name.lower() in obj.key.lower():
                horse = obj
                break

    if not horse:
        return "No horse or mount found to inspect."

    tamed_str = "|gTamed Mount|n" if getattr(horse.db, "is_tamed", False) else "|rWild & Untamed|n"
    lines = [
        "|c" + "=" * 65 + "|n",
        f"|w               EQUESTRIAN STABLE PROFILE: {horse.key.upper()} |n",
        "|c" + "=" * 65 + "|n",
        f" |wDisposition:|n {tamed_str}",
        f" |yGallop Speed Rating:|n |w{getattr(horse.db, 'speed', 10)} mph|n",
        f" |cMax Endurance Stamina:|n |w{getattr(horse.db, 'stamina', 120)} pts|n",
        f" |mTemperament:|n {getattr(horse.db, 'temperament', 'Loyal & Spirited')}",
        f" |x{horse.db.desc}|n",
        "|c" + "=" * 65 + "|n"
    ]
    return "\n".join(lines)

