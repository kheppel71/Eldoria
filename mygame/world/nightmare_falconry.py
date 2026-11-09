"""
Nightmare LPmud Falconry, Hunting Birds & Aerial Reconnaissance Engine.

Implements:
1. Birds of Prey:
   - Peregrine Hunting Falcon (Speed & aerial reconnaissance)
   - Crimson Mountain Harrier (Vicious dive strikes)
   - Midnight Barn Owl (Silent nocturnal perception)
2. Leather falconry gauntlet and calling companion birds ('callhawk').
3. Aerial scouting of adjacent wilderness exits ('sendhawk scout <direction>').
4. Hunting strikes on wild quarry for feathers and game meat ('sendhawk strike').
5. Bird care and feeding ('feedhawk', 'perch').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

BIRD_BREEDS = {
    "falcon": {
        "name": "Peregrine Hunting Falcon",
        "specialty": "Lightning Reconnaissance",
        "desc": "A sleek, sharp-eyed falcon with barred grey wings and razor-sharp talons, resting alertly."
    },
    "harrier": {
        "name": "Crimson Mountain Harrier",
        "specialty": "Vicious Quarry Dive",
        "desc": "A fierce upland bird of prey with rust-red plumage and predatory amber eyes."
    },
    "owl": {
        "name": "Midnight Barn Owl",
        "specialty": "Nocturnal Stealth Scouting",
        "desc": "A silent-winged predator with heart-shaped white facial disc and keen night vision."
    }
}


def call_hunting_bird(caller, breed_key="falcon"):
    """Whistles to summon or bond a hunting bird to the caller's arm gauntlet."""
    key = breed_key.strip().lower()
    matched = next((k for k in BIRD_BREEDS if key in k), None)

    if not matched:
        opts = ", ".join(BIRD_BREEDS.keys())
        return False, f"Unknown bird breed '{breed_key}'. Choose from: {opts}"

    data = BIRD_BREEDS[matched]
    caller.db.hunting_bird = {
        "key": matched,
        "name": data["name"],
        "loyalty": 100,
        "is_perched": True
    }

    caller.msg(
        f"\n|Y[FALCONRY CALL]|n You raise your heavy leather gauntlet and give a sharp, piercing whistle.\n"
        f"A magnificent |w{data['name']}|n swoops down from the clouds and perches securely upon your arm!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"A sharp whistle echoes as a {data['name']} descends from the sky and lands on {caller.key}'s arm.",
            exclude=[caller]
        )
    return True, f"Called {data['name']}."


def scout_with_bird(caller, direction="north"):
    """Sends the bird to scout the adjacent room in the given direction."""
    bird = getattr(caller.db, "hunting_bird", None)
    if not bird:
        return False, "You do not have a trained hunting bird on your gauntlet! Use 'callhawk' first."

    room = caller.location
    if not room:
        return False, "You cannot scout from the void."

    # Look for matching exit
    dir_clean = direction.strip().lower()
    target_exit = None
    for ex in room.exits:
        if dir_clean in ex.key.lower() or dir_clean in ex.aliases:
            target_exit = ex
            break

    if not target_exit or not target_exit.destination:
        return False, f"There is no clear flight path heading {direction}."

    dest = target_exit.destination
    dest_name = dest.key
    occupants = [o.key for o in dest.contents if getattr(o.db, "is_character", False) and o != caller]
    items = [o.key for o in dest.contents if not getattr(o.db, "is_character", False)]

    occ_str = ", ".join(occupants) if occupants else "None (area is quiet)"
    items_str = ", ".join(items[:4]) if items else "No noteworthy objects"

    caller.msg(
        f"\n|C[AERIAL RECONNAISSANCE - {bird['name'].upper()}]|n\n"
        f"Your bird launches from your wrist and circles high above |w{dest_name}|n to the {direction}!\n"
        f"  |ySpotted Figures:|n {occ_str}\n"
        f"  |yGround Landmarks:|n {items_str}\n"
        f"The bird returns, beating its powerful wings and settling back onto your gauntlet.\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key}'s {bird['name']} takes wing into the sky, scouting to the {direction} before returning.",
            exclude=[caller]
        )
    return True, f"Scouted {dest_name}."


def hunt_quarry_with_bird(caller):
    """Sends the bird on a hunting dive to strike wild game."""
    bird = getattr(caller.db, "hunting_bird", None)
    if not bird:
        return False, "You do not have a hunting bird ready to strike quarry."

    room = caller.location
    meat = create_object(Object, key="Fresh Wild Poultry", location=caller)
    meat.db.desc = "A plump wild pheasant taken cleanly by a hunting bird of prey. Can be cooked or fed."
    meat.db.is_food = True
    meat.db.heal_hp = 20

    feather = create_object(Object, key="Pristine Raptor Plume", location=caller)
    feather.db.desc = "A handsome flight feather shed during a high-speed hunting stoop, prized by fletchers."

    caller.msg(
        f"\n|Y*SCREEECH!*|n You thrust your fist forward, releasing {bird['name']}!\n"
        f"The bird folds its wings into a 150mph stoop, striking clean through the brush!\n"
        f"It returns carrying |w{meat.key}|n and a |w{feather.key}|n!\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key}'s {bird['name']} dives like a lightning bolt from the clouds and claims fresh game!",
            exclude=[caller]
        )
    return True, "Quarry hunted."


def feed_hunting_bird(caller):
    """Feeds the bird fresh meat to reward loyalty."""
    bird = getattr(caller.db, "hunting_bird", None)
    if not bird:
        return False, "You do not have a hunting bird to feed."

    food = None
    for obj in caller.contents:
        if getattr(obj.db, "is_food", False) or "poultry" in obj.key.lower() or "meat" in obj.key.lower():
            food = obj
            break

    if not food:
        return False, "You need a piece of meat or poultry in your pack to feed your hunting bird."

    food.delete()
    bird["loyalty"] = min(100, bird.get("loyalty", 100) + 15)
    caller.db.hunting_bird = bird

    caller.msg(
        f"\n|gYou slice off tender strips of meat and offer them to {bird['name']}.\n"
        f"The bird eagerly snatches the morsels, clicking its beak contentedly! (Loyalty: 100%)|n\n"
    )
    return True, "Bird fed."

