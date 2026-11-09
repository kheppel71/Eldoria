"""
Nightmare LPmud Wilderness Fishing & Angling Engine.

Implements:
1. Fishing rods and live bait attachment.
2. Dynamic river, lake, and coastal angling ('castline', 'reel').
3. Variety of regional fish catches and sunken treasure lockboxes.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object


FISH_TABLE = [
    ("Rainbow River Trout", "A glistening freshwater trout with iridescent pink scales.", 15, 2, "fish"),
    ("Spotted Lake Bass", "A plump, fighting bass with mottled emerald markings.", 20, 3, "fish"),
    ("Luminescent Ghost Carp", "A rare, glowing silver carp prized by alchemists.", 45, 2, "fish"),
    ("Giant Mud Catfish", "A whiskered river catfish that puts up a fierce struggle.", 25, 4, "fish"),
    ("Sunken Barnacled Lockbox", "An ancient waterlogged iron box encrusted with salt and barnacles.", 80, 5, "box")
]


def attach_bait_to_rod(caller, bait_obj, rod_obj):
    """Attaches bait to a fishing rod."""
    if "rod" not in rod_obj.key.lower() and "pole" not in rod_obj.key.lower():
        return False, f"{rod_obj.key} is not a fishing rod!"

    if "bait" not in bait_obj.key.lower() and "worm" not in bait_obj.key.lower() and "grub" not in bait_obj.key.lower():
        return False, f"{bait_obj.key} cannot be used as fishing bait!"

    rod_obj.db.has_bait = True
    rod_obj.db.bait_name = bait_obj.key
    bait_obj.delete()

    caller.msg(f"|yYou spear the {bait_obj.key} onto the hook of {rod_obj.key}. Ready to cast!|n")
    return True, "Baited."


def cast_fishing_line(caller, rod_obj):
    """Casts the baited hook into local waters."""
    loc = caller.location
    if not loc:
        return False, "You cannot fish in the void."

    terrain = getattr(loc.db, "terrain", "coast") or "coast"
    valid_terrains = ["coast", "river", "lake", "ocean", "swamp", "port", "dock"]
    if terrain.lower() not in valid_terrains and "water" not in loc.key.lower() and "docks" not in loc.key.lower() and "river" not in loc.key.lower():
        return False, "There is no open water or river here to fish in!"

    if not getattr(rod_obj.db, "has_bait", False):
        return False, f"Your {rod_obj.key} has no bait on the hook! Attach bait first: |wbait hook with <worm>|n"

    caller.ndb.is_fishing = True
    rod_obj.db.has_bait = False  # Consumed on cast

    caller.msg(f"\n|cWith a fluid flick of your wrist, you cast the line from {rod_obj.key} far out across the ripples!|n")
    caller.msg("|wThe bobber bobs gently upon the surface. Watch for a bite, then: |wreel|n\n")
    if loc:
        loc.msg_contents(
            f"{caller.key} casts a fishing line out into the water.",
            exclude=[caller]
        )
    return True, "Casting."


def reel_fishing_line(caller):
    """Reels in the cast fishing line to land a catch."""
    if not getattr(caller.ndb, "is_fishing", False):
        return False, "You do not have a line cast in the water! Type: |wcastline|n"

    caller.ndb.is_fishing = False
    loc = caller.location

    roll = random.randint(1, 100) + (caller.db.dex or 10)

    if roll < 35:
        caller.msg("|yYou reel in your line quickly, but the hook returns empty! The fish stole the bait.|n")
        return True, "Lost bait."

    # Catch something!
    f_name, f_desc, f_val, f_wt, f_type = random.choice(FISH_TABLE)

    if f_type == "box":
        catch = create_object(Object, key=f_name, location=caller)
        catch.db.desc = f_desc
        catch.db.value = f_val
        catch.db.weight = f_wt
        catch.db.is_lockable = True
        catch.db.is_locked = False
        # Add bonus coins inside
        coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        coins["gold"] += 25
        caller.db.coins = coins
        caller.msg(f"\n|Y*** SUNKEN SALVAGE! ***|n You reel in a heavy, dripping {f_name}!")
        caller.msg(f"Prying the corroded lid open reveals |y25 Gold coins|n and old relics!\n")
    else:
        catch = create_object(Object, key=f_name, location=caller)
        catch.db.desc = f_desc
        catch.db.value = f_val
        catch.db.weight = f_wt
        catch.db.is_fish = True
        caller.msg(f"\n|g*** SPLASH! *** The rod bends double as you fight the current!|n")
        caller.msg(f"|GYou land a prize catch: |w{f_name}|G! ({f_wt} lbs)|n\n")

    if loc:
        loc.msg_contents(
            f"{caller.key} reels in their line and lands a {f_name}!",
            exclude=[caller]
        )
    return True, "Reeled."

