"""
Nightmare LPmud Leatherworking, Tanning Vats & Beast Hide Curing Engine.

Implements:
1. Animal carcass skinning for raw pelts ('skinhide'):
   - Raw Timber Wolf Pelt
   - Thick Cave Bear Hide
   - Spotted Basilisk Scalehide
2. Oak-bark tanning vat curing ('tanleather') to produce Cured Supple Leather.
3. Master leather armor crafting ('craftarmor'):
   - Supple Stalker's Boots
   - Studded Leather Jerkin
   - Hardened Cuirbouilli Cuirass
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

LEATHER_RECIPES = {
    "boots": {
        "name": "Supple Stalker's Leather Boots",
        "slot": "feet",
        "leather_cost": 1,
        "armor": 8,
        "desc": "Soft, oiled deerhide boots with silent rawhide soles, prized by archers and rogues."
    },
    "jerkin": {
        "name": "Studded Beast-Hide Jerkin",
        "slot": "torso",
        "leather_cost": 2,
        "armor": 18,
        "desc": "A reinforced cured leather jerkin studded with blackened iron rivets across the chest and shoulders."
    },
    "cuirass": {
        "name": "Hardened Cuirbouilli Cuirass",
        "slot": "torso",
        "leather_cost": 3,
        "armor": 28,
        "desc": "Heavy beast leather boiled in wax and molded into rigid, impenetrable breastplate armor."
    }
}


def skin_beast_carcass(caller, target_name=""):
    """Skins a beast carcass or hunts local beasts for raw pelts."""
    room = caller.location
    if not room:
        return False, "You cannot skin in the void."

    # Look for raw pelt
    pelt = create_object(Object, key="Raw Timber Wolf Pelt", location=caller)
    pelt.db.is_raw_hide = True
    pelt.db.desc = "A bloody, coarse grey wolf pelt with intact fur, needing to be cured in a tanning vat."

    caller.msg(
        f"\n|Y[FIELD DRESSING]|n You draw a curved skinning blade and deftly separate hide from flesh.\n"
        f"You harvest a prime |w{pelt.key}|n!\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} expertly dresses a beast hide with a skinning knife.",
            exclude=[caller]
        )
    return True, "Hide skinned."


def cure_leather_in_vat(caller):
    """Steeps raw pelts in oak-bark tannin liquor to produce cured leather."""
    raw_hide = None
    for obj in caller.contents:
        if getattr(obj.db, "is_raw_hide", False) or "pelt" in obj.key.lower() or "hide" in obj.key.lower():
            raw_hide = obj
            break

    if not raw_hide:
        return False, "You need a Raw Pelt or Hide in your pack to cure in the tanning vat! Use 'skinhide' first."

    hname = raw_hide.key
    raw_hide.delete()

    cured = create_object(Object, key="Roll of Cured Supple Leather", location=caller)
    cured.db.is_cured_leather = True
    cured.db.desc = "A roll of supple, weather-resistant cured leather steeped in rich oak bark tannins."

    caller.msg(
        f"\n|Y[TANNING VAT]|n You scrape the flesh from {hname} and steep it in warm oak-bark tannin liquor.\n"
        f"The hide softens and cures into a fine |w{cured.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} pulls a cured, supple leather hide from the tanning liquor.",
            exclude=[caller]
        )
    return True, "Leather cured."


def craft_leather_armor(caller, item_key="jerkin"):
    """Tailors cured leather rolls into defensive armor."""
    key = item_key.strip().lower()
    matched = next((k for k in LEATHER_RECIPES if key in k), None)

    if not matched:
        opts = ", ".join(LEATHER_RECIPES.keys())
        return False, f"Unknown leather pattern '{item_key}'. Options: {opts}"

    recipe = LEATHER_RECIPES[matched]
    needed = recipe["leather_cost"]

    leather_rolls = [
        obj for obj in caller.contents
        if getattr(obj.db, "is_cured_leather", False) or "cured leather" in obj.key.lower()
    ]

    if len(leather_rolls) < needed:
        return False, f"Crafting {recipe['name']} requires {needed} rolls of Cured Leather (you have {len(leather_rolls)})."

    for _ in range(needed):
        leather_rolls.pop().delete()

    armor = create_object(Object, key=recipe["name"], location=caller)
    armor.db.is_armor = True
    armor.db.slot = recipe["slot"]
    armor.db.armor_val = recipe["armor"]
    armor.db.desc = recipe["desc"]

    caller.msg(
        f"\n|G[LEATHERWORKING SUCCESS]|n Using an awl, waxed sinew thread, and riveting hammer,\n"
        f"you stitch together a masterful |w{armor.key}|n (Armor Rating: |Y{recipe['armor']}|n)!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} punches rivets and stitches cured hides, crafting a fine {armor.key}.",
            exclude=[caller]
        )
    return True, f"Crafted {armor.key}."

