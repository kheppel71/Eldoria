"""
Nightmare LPmud Truffle Hunting, Sniffer Hounds & Culinary Feasts Engine.

Implements:
1. Leashed Truffle Hunting Hounds ('leashhound').
2. Forest Floor Truffle Sniffing & Excavation ('trufflehunt', 'digtruffle'):
   - Black Perigord Oak Truffle
   - Golden Sun Truffle
   - White Winter Morel
3. Gourmet Banquet Cooking ('cookfeast') granting the 'Well-Fed Vitality' buff (+HP/Stamina).
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

TRUFFLE_VARIETIES = [
    {
        "name": "Black Perigord Oak Truffle",
        "value": 45,
        "flavor": "pungent, dark woodland musk",
        "desc": "A knobby, coal-black subterranean fungus renowned for its intoxicating earthy aroma."
    },
    {
        "name": "Golden Sun Truffle",
        "value": 75,
        "flavor": "sweet hazelnut and rich honey",
        "desc": "An exceedingly rare ochre truffle found only near the roots of lightning-struck beeches."
    },
    {
        "name": "White Winter Morel",
        "value": 30,
        "flavor": "smoky cream and wild butter",
        "desc": "A fragrant ribbed subterranean mushroom treasured by royal palace chefs."
    }
]


def leash_truffle_hound(caller):
    """Leashes a keen-nosed truffle hunting hound."""
    caller.db.has_truffle_hound = True
    caller.msg(
        "\n|Y[HOUND COMPANION]|n You clip a sturdy leather lead to a shaggy, keen-nosed |wTruffle Hound|n!\n"
        "The hound wags its tail, nose quivering as it catches the scent of subterranean delicacies!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} leads forth a trained shaggy truffle hound on a leather leash.",
            exclude=[caller]
        )
    return True, "Hound leashed."


def hunt_truffles_in_area(caller):
    """Commands the truffle hound to sniff out subterranean fungi."""
    if not getattr(caller.db, "has_truffle_hound", False):
        return False, "You need a trained truffle hound to locate buried truffles! Use 'leashhound' first."

    room = caller.location
    if not room:
        return False, "You cannot hunt in the void."

    # Mark room as having discovered scent
    caller.db.truffle_scent_found = True
    caller.msg(
        "\n|g*SNIFF SNIFF!* Your truffle hound eagerly drags you toward the gnarled roots of a nearby oak!\n"
        "The hound begins pawing passionately at the damp leaf mould, whining with excitement!|n\n"
        "|yUse 'digtruffle' to carefully unearth the buried delicacy!|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key}'s hound catches a strong subterranean scent and paws enthusiastically at the forest loam.",
            exclude=[caller]
        )
    return True, "Scent detected."


def dig_up_truffle(caller):
    """Carefully excavates the detected subterranean truffle."""
    if not getattr(caller.db, "truffle_scent_found", False):
        return False, "Your hound has not detected any fresh truffle scent here! Command 'trufflehunt' first."

    caller.db.truffle_scent_found = False
    data = random.choice(TRUFFLE_VARIETIES)

    truffle = create_object(Object, key=data["name"], location=caller)
    truffle.db.is_truffle = True
    truffle.db.value = data["value"]
    truffle.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[PRIZED HARVEST]|n Kneeling in the loam, you gently brush away moss and roots with a horn spade.\n"
        f"You cradle a magnificent |w{truffle.key}|n! Aroma: |c{data['flavor']}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} carefully brushes away forest roots and unearths a prized {truffle.key}!",
            exclude=[caller]
        )
    return True, f"Harvested {truffle.key}."


def cook_truffle_feast(caller):
    """Prepares an exquisite truffle banquet that restores and buffs party members."""
    truffle = None
    for obj in caller.contents:
        if getattr(obj.db, "is_truffle", False) or "truffle" in obj.key.lower():
            truffle = obj
            break

    if not truffle:
        return False, "You need a fresh truffle in your pack to prepare a gourmet culinary feast!"

    tname = truffle.key
    truffle.delete()

    curr_hp = getattr(caller.db, "hp", 100) or 100
    max_hp = getattr(caller.db, "max_hp", 100) or 100
    caller.db.hp = min(max_hp, curr_hp + 35)

    curr_stam = getattr(caller.db, "stamina", 100) or 100
    max_stam = getattr(caller.db, "max_stamina", 100) or 100
    caller.db.stamina = min(max_stam, curr_stam + 35)

    caller.db.well_fed_buff = True

    caller.msg(
        f"\n|Y[CULINARY BANQUET]|n Slicing {tname} paper-thin over braised meats and buttered root mash,\n"
        f"you partake in an unforgettable epicurean feast!\n"
        f"|gYou gain the |W'Well-Fed Vitality'|g buff! (+35 HP, +35 Stamina)|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"A mouth-watering aroma fills the air as {caller.key} serves an exquisite truffle-infused feast!",
            exclude=[caller]
        )
    return True, "Feast prepared."

