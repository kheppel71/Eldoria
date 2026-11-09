"""
Nightmare LPmud Runestone Inscription & Gem Socketing System.

Implements:
1. Elemental Runestones (Pyros, Frostbite, Leeching).
2. Weapon imbuing ('inscribe <weapon> with <rune>') adding proc damage on hit.
3. Socketed Gemstones (Rubies, Sapphires, Diamonds) boosting health, mana, and armor.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

RUNES = {
    "pyros": {
        "name": "Rune of Pyros",
        "element": "Fire",
        "dmg": 8,
        "desc": "A crimson runestone glowing with smoldering elemental embers."
    },
    "frostbite": {
        "name": "Rune of Frostbite",
        "element": "Frost",
        "dmg": 6,
        "desc": "An azure runestone radiating a biting, glacial chill."
    },
    "leeching": {
        "name": "Rune of Leeching",
        "element": "Vampiric",
        "dmg": 5,
        "desc": "A deep obsidian runestone that pulses like a beating heart."
    }
}

GEMS = {
    "ruby": {
        "name": "Cut Star Ruby",
        "bonus_type": "hp",
        "bonus_val": 35,
        "desc": "A brilliant faceted ruby glowing with inner vitality (+35 HP)."
    },
    "sapphire": {
        "name": "Cut Lapis Sapphire",
        "bonus_type": "mana",
        "bonus_val": 30,
        "desc": "A deep cobalt sapphire humming with arcane potential (+30 Mana)."
    },
    "diamond": {
        "name": "Flawless Diamond",
        "bonus_type": "armor",
        "bonus_val": 4,
        "desc": "An adamantine cut diamond providing impregnable warding (+4 Armor)."
    }
}


def inscribe_weapon_with_rune(caller, rune_obj, weapon_obj):
    """Inscribes an elemental runestone into a weapon."""
    r_key = None
    for k, data in RUNES.items():
        if k in rune_obj.key.lower() or data["element"].lower() in rune_obj.key.lower():
            r_key = k
            break

    if not r_key:
        return False, f"{rune_obj.key} is not an elemental runestone!"

    if getattr(weapon_obj.db, "damage_bonus", None) is None and getattr(weapon_obj.db, "slot", "") not in ["right_hand", "left_hand"]:
        return False, f"{weapon_obj.key} is not a valid weapon to inscribe!"

    r_data = RUNES[r_key]
    weapon_obj.db.rune_enchant = {
        "name": r_data["name"],
        "element": r_data["element"],
        "damage": r_data["dmg"]
    }

    rune_name = rune_obj.key
    rune_obj.delete()

    caller.msg(f"\n|Y[RUNE INSCRIPTION]|n You place {rune_name} against {weapon_obj.key}. The runestone melts into glowing lines of power across the blade!")
    caller.msg(f"|G{weapon_obj.key} is now imbued with {r_data['element']} damage (+{r_data['dmg']} {r_data['element']})!|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"Arcane sparks fly as {caller.key} inscribes an elemental rune onto {weapon_obj.key}!",
            exclude=[caller]
        )
    return True, "Inscribed."


def socket_gem_into_gear(caller, gem_obj, gear_obj):
    """Sockets a precious gemstone into open equipment sockets."""
    g_key = None
    for k, data in GEMS.items():
        if k in gem_obj.key.lower():
            g_key = k
            break

    if not g_key:
        return False, f"{gem_obj.key} is not a socketable gemstone!"

    if getattr(gear_obj.db, "socketed_gem", None):
        return False, f"{gear_obj.key} already has a gemstone set in its socket!"

    g_data = GEMS[g_key]
    gear_obj.db.socketed_gem = g_data

    # Apply bonus
    if g_data["bonus_type"] == "armor":
        gear_obj.db.armor_value = (gear_obj.db.armor_value or 0) + g_data["bonus_val"]
    elif g_data["bonus_type"] == "hp":
        caller.db.max_hp = (caller.db.max_hp or 100) + g_data["bonus_val"]
    elif g_data["bonus_type"] == "mana":
        caller.db.max_mana = (caller.db.max_mana or 100) + g_data["bonus_val"]

    gem_name = gem_obj.key
    gem_obj.delete()

    caller.msg(f"\n|Y[GEM SOCKETED]|n You set {gem_name} into the socket of {gear_obj.key}! It clicks firmly into place with a brilliant flash of light!")
    caller.msg(f"|GGranted Bonus: {g_data['desc']}|n\n")
    return True, "Socketed."

