"""
Nightmare LPmud Clockwork Tinkering, Automatons & Mechanical Decoy Engine.

Implements:
1. Gnomish Tinkering Blueprint Crafting ('tinker'):
   - Clockwork Ticking Decoy (Combat distractor & shrapnel detonation)
   - Mechanical Brass Spider (Crevice exploration automaton)
   - Pocket Gnomish Chronometer (Precision celestial timepiece)
2. Mainspring Winding ('windgadget').
3. Combat Decoy Deployment ('deploydecoy').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

TINKER_BLUEPRINTS = {
    "decoy": {
        "name": "Clockwork Ticking Decoy",
        "cost": 40,
        "desc": "A brass mannequin chassis fitted with whirring cogs, flashing copper bells, and a spring-loaded clockwork core."
    },
    "spider": {
        "name": "Mechanical Brass Spider",
        "cost": 30,
        "desc": "An eight-legged arachnid automaton with sapphire eye lenses that clicks rhythmically as its legs twitch."
    },
    "chronometer": {
        "name": "Pocket Gnomish Chronometer",
        "cost": 25,
        "desc": "A gilded pocket watch displaying 24-hour celestial movements, lunar conjunctions, and escapement gears."
    }
}


def craft_tinker_gadget(caller, gadget_key="decoy"):
    """Assembles a clockwork mechanism using brass gears and mainsprings."""
    key = gadget_key.strip().lower()
    matched = next((k for k in TINKER_BLUEPRINTS if key in k), None)

    if not matched:
        opts = ", ".join(TINKER_BLUEPRINTS.keys())
        return False, f"Unknown gadget blueprint '{gadget_key}'. Options: {opts}"

    blueprint = TINKER_BLUEPRINTS[matched]
    cost = blueprint["cost"]
    coins = getattr(caller.db, "coins", 0) or 0

    if coins < cost:
        return False, f"Tinkering components and gears require {cost} gold coins (you have {coins})."

    caller.db.coins = coins - cost

    gadget = create_object(Object, key=blueprint["name"], location=caller)
    gadget.db.is_gadget = True
    gadget.db.gadget_type = matched
    gadget.db.is_wound = False
    gadget.db.desc = blueprint["desc"]

    caller.msg(
        f"\n|Y[TINKERING SUCCESS]|n Using tiny screwdrivers, tweezers, and brass cogs,\n"
        f"you assemble an intricate |w{gadget.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} tightens precision brass gears, constructing a clever {gadget.key}.",
            exclude=[caller]
        )
    return True, f"Crafted {gadget.key}."


def wind_clockwork_gadget(caller, gadget_name=""):
    """Winds the mainspring of a clockwork automaton."""
    gadget = None
    for obj in caller.contents:
        if getattr(obj.db, "is_gadget", False):
            if not gadget_name or gadget_name.lower() in obj.key.lower():
                gadget = obj
                break

    if not gadget:
        return False, "You do not have a clockwork gadget to wind."

    gadget.db.is_wound = True
    caller.msg(f"\n|Y*CRICK-CRACK-CRICK!* You insert the brass winding key and tightly coil the mainspring of {gadget.key}!|n\n")
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} winds the brass clockwork key of {gadget.key} until the spring is taut.",
            exclude=[caller]
        )
    return True, "Gadget wound."


def deploy_clockwork_decoy(caller):
    """Deploys a wound ticking decoy into the room to divert enemy attention."""
    decoy = None
    for obj in caller.contents:
        if getattr(obj.db, "gadget_type", "") == "decoy":
            decoy = obj
            break

    if not decoy:
        return False, "You do not have a Clockwork Ticking Decoy in your pack! Craft one with 'tinker decoy'."

    if not getattr(decoy.db, "is_wound", False):
        return False, f"{decoy.key}'s spring is unwound! Use 'windgadget' first."

    room = caller.location
    decoy.move_to(room, quiet=True)
    decoy.db.is_deployed = True

    caller.msg(
        f"\n|R[DECOY DEPLOYED]|n You set down {decoy.key} and release the escapement ratchet!\n"
        "|Y*CLATTER-CLATTER-DING!* Sparks fly and bells chime furiously, drawing all eyes away from you!|n\n"
    )
    if room:
        room.msg_contents(
            f"|Y*CLATTER-CLATTER!* {caller.key} deploys a whirring Clockwork Decoy that flashes and clatters loudly!|n",
            exclude=[caller]
        )
    return True, "Decoy deployed."

