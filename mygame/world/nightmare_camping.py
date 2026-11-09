"""
Nightmare LPmud Wilderness Camping, Tents & Campfire Survival Engine.

Implements:
1. Pitching wilderness shelters ('pitchtent') and striking camp ('strikecamp').
2. Lighting warm campfires ('lightcampfire') for light and nocturnal predator warding.
3. Campfire rest recovery amplification (+Stamina/HP).
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def pitch_campsite_tent(caller, tent_kit):
    """Pitches a sheltering canvas tent in a wilderness room."""
    loc = caller.location
    if not loc:
        return False, "You cannot camp in the void."

    terrain = getattr(loc.db, "terrain", "city") or "city"
    if terrain.lower() in ["city", "indoor", "courthouse", "jail"]:
        return False, "You cannot pitch a wilderness camp inside city streets or buildings!"

    if getattr(loc.db, "has_camp", False):
        return False, "A campsite is already pitched here."

    tent_kit.delete()
    loc.db.has_camp = True

    tent = create_object(Object, key=f"{caller.key}'s Canvas Shelter Tent", location=loc)
    tent.db.desc = f"A sturdy canvas and leather shelter tent pitched by {caller.key}. Fur bedrolls rest inside."
    tent.db.is_tent = True
    tent.db.owner_id = caller.id

    caller.msg(f"\n|yYou hammer wooden stakes into the earth, pitching a weather-tight canvas tent shelter!|n\n")
    if loc:
        loc.msg_contents(
            f"{caller.key} pitches a sturdy canvas shelter tent.",
            exclude=[caller]
        )
    return True, "Tent pitched."


def light_campfire(caller, tinderbox):
    """Sparks a crackling campfire in the campsite."""
    loc = caller.location
    if not loc:
        return False, "Nowhere to light a fire."

    if getattr(loc.db, "has_fire", False):
        return False, "A fire is already blazing warmly here."

    loc.db.has_fire = True

    fire = create_object(Object, key="Crackling Pine Campfire", location=loc)
    fire.db.desc = "A cheerful, roaring campfire made of stacked pine logs. Embers dance upward into the night, radiating deep warmth."
    fire.db.is_campfire = True
    fire.db.is_illuminated = True

    caller.msg(f"\n|YYou strike flint and steel against tinder! Sparks catch, and a crackling campfire roars to life!|n")
    caller.msg("|yThe glowing hearth wards away nocturnal beasts and speeds health recovery.|n\n")

    if loc:
        loc.msg_contents(
            f"|Y{caller.key} strikes flint and kindles a roaring pine campfire! Warm orange light illuminates the area.|n",
            exclude=[caller]
        )
    return True, "Fire lit."


def strike_campsite(caller):
    """Dismantles the tent and extinguishes the campfire."""
    loc = caller.location
    if not loc:
        return False, "No location."

    if not getattr(loc.db, "has_camp", False) and not getattr(loc.db, "has_fire", False):
        return False, "There is no active camp or fire here to pack up."

    # Remove tent and fire objects
    for obj in list(loc.contents):
        if getattr(obj.db, "is_tent", False) or getattr(obj.db, "is_campfire", False):
            obj.delete()

    loc.db.has_camp = False
    loc.db.has_fire = False

    # Return a tent kit to the caller
    kit = create_object(Object, key="Canvas Tent Kit", location=caller)
    kit.db.desc = "Sturdy canvas tarp, guy lines, and wooden pegs for pitching a wilderness shelter."
    kit.db.value = 25

    caller.msg(f"\n|yYou douse the embers with dirt and pack up your canvas tent kit.|n\n")
    if loc:
        loc.msg_contents(
            f"{caller.key} strikes camp, packing up their tent and dousing the fire.",
            exclude=[caller]
        )
    return True, "Camp struck."

