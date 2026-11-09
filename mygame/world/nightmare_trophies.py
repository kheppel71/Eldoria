"""
Nightmare LPmud Monster Taxidermy & Trophy Mount System.

Implements:
1. Crafting mounted wall trophies from harvested pelts, heads, and dragon scales.
2. Hanging trophies in player houses or guild strongholds ('mounttrophy <trophy>').
3. Room prestige inspection ('trophies').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def craft_taxidermy_trophy(caller, raw_part):
    """Crafts a decorative mounted trophy from monster parts."""
    p_name = raw_part.key

    coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    cost = 15  # 15 Gold taxidermy fee
    if coins.get("gold", 0) < cost:
        return False, f"Taxidermy costs {cost} Gold (You have {coins.get('gold', 0)} Gold)."

    coins["gold"] -= cost
    caller.db.coins = coins
    raw_part.delete()

    t_key = f"Mounted {p_name} Trophy"
    trophy = create_object(Object, key=t_key, location=caller)
    trophy.db.desc = f"An expertly preserved, plaque-mounted trophy crafted from {p_name}. A testament to martial triumph."
    trophy.db.is_trophy = True
    trophy.db.slayer = caller.key
    trophy.db.value = 75
    trophy.db.weight = 5

    caller.msg(f"\n|Y[TAXIDERMY COMPLETE]|n The taxidermist mounts your trophy upon a polished hardwood plaque: |w{trophy.key}|n!")
    return True, "Crafted."


def mount_trophy_on_wall(caller, trophy):
    """Mounts a trophy onto the wall of the current room."""
    loc = caller.location
    if not loc:
        return False, "Nowhere to mount."

    if not getattr(trophy.db, "is_trophy", False):
        return False, f"{trophy.key} is not a mountable trophy plaque!"

    wall_trophies = getattr(loc.db, "wall_trophies", []) or []
    wall_trophies.append({
        "name": trophy.key,
        "slayer": trophy.db.slayer or caller.key,
        "desc": trophy.db.desc or ""
    })
    loc.db.wall_trophies = wall_trophies

    trophy.delete()

    caller.msg(f"\n|yYou hammer iron brackets into the wall and proudly hang {trophy.key}!|n")
    if loc:
        loc.msg_contents(
            f"|y{caller.key} hangs a magnificent {trophy.key} upon the wall for all to admire!|n",
            exclude=[caller]
        )
    return True, "Mounted."

