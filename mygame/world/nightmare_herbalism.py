"""
Nightmare LPmud Wilderness Herbalism, Poultices & Blade Poison Engine.

Implements:
1. Wilderness herbal foraging ('forage') for rare flora:
   - Kingsbloom, Nightshade, Grave Moss, Sunroot.
2. Medicinal Poultice Crafting ('craftpoultice') & Application ('applypoultice')
   to heal wounds and stabilize damaged limbs.
3. Deadly Blade Poison Brewing ('craftpoison') & Weapon Coating ('coatweapon')
   to inflict venomous damage during combat.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

FORAGEABLE_HERBS = [
    {
        "name": "Kingsbloom Flower",
        "desc": "A vibrant golden wildflower known for its restorative medicinal nectar.",
        "type": "healing",
        "cure_amount": 35
    },
    {
        "name": "Grave Moss",
        "desc": "A cool, spongy grey moss gathered from stone vaults that halts bleeding and soothes burns.",
        "type": "healing",
        "cure_amount": 25
    },
    {
        "name": "Sunroot Tuber",
        "desc": "A gnarled, fibrous root packed with invigorating herbal nutrients.",
        "type": "stamina",
        "cure_amount": 30
    },
    {
        "name": "Nightshade Belladonna",
        "desc": "A dark purple flowering weed dripping with potent paralytic toxins.",
        "type": "poison",
        "cure_amount": 0
    }
]


def forage_herbs(caller):
    """Forages current location for wild medicinal plants and toxic flora."""
    room = caller.location
    if not room:
        return False, "You cannot forage into the void."

    # Chance to discover flora
    herb_data = random.choice(FORAGEABLE_HERBS)
    herb = create_object(Object, key=herb_data["name"], location=caller)
    herb.db.desc = herb_data["desc"]
    herb.db.is_herb = True
    herb.db.herb_type = herb_data["type"]
    herb.db.cure_amount = herb_data["cure_amount"]

    caller.msg(f"\n|G[FORAGING SUCCESS]|n You search the undergrowth and carefully harvest a fresh |w{herb.key}|n!\n")
    if room:
        room.msg_contents(f"{caller.key} forages carefully through the underbrush and collects wild herbs.", exclude=[caller])
    return True, f"Harvested {herb.key}."


def craft_poultice(caller):
    """Crafts a healing poultice from medicinal herbs in inventory."""
    herb = None
    for obj in caller.contents:
        if getattr(obj.db, "is_herb", False) and obj.db.herb_type in ("healing", "stamina"):
            herb = obj
            break

    if not herb:
        return False, "You need a healing herb (Kingsbloom, Grave Moss, Sunroot) in your inventory to craft a poultice!"

    herb_name = herb.key
    heal_power = getattr(herb.db, "cure_amount", 25)
    herb.delete()

    poultice = create_object(Object, key="Herbal Medicinal Poultice", location=caller)
    poultice.db.desc = f"A soothing compress made from crushed {herb_name}, wrapped in clean linen."
    poultice.db.is_poultice = True
    poultice.db.heal_val = heal_power

    caller.msg(f"\n|YYou grind the {herb_name} into a fragrant paste and wrap it in linen, creating an |wHerbal Medicinal Poultice|Y!|n\n")
    return True, "Poultice crafted."


def apply_poultice(caller, target=None):
    """Applies a healing poultice to oneself or an ally."""
    poultice = None
    for obj in caller.contents:
        if getattr(obj.db, "is_poultice", False):
            poultice = obj
            break

    if not poultice:
        return False, "You do not have any herbal medicinal poultices in your pack!"

    recipient = target if target else caller
    heal_val = getattr(poultice.db, "heal_val", 25)
    poultice.delete()

    curr_hp = getattr(recipient.db, "hp", 100) or 100
    max_hp = getattr(recipient.db, "max_hp", 100) or 100
    recipient.db.hp = min(max_hp, curr_hp + heal_val)

    # If recipient has damaged limbs, mend them partially
    limbs = getattr(recipient.db, "limbs", {}) or {}
    for lname, ldata in limbs.items():
        if isinstance(ldata, dict) and "current" in ldata and "max" in ldata:
            ldata["current"] = min(ldata["max"], ldata["current"] + heal_val)
    recipient.db.limbs = limbs

    caller.msg(f"\n|gYou gently press the soothing medicinal poultice against {recipient.key}'s wounds (+{heal_val} HP)!|n\n")
    if recipient != caller:
        recipient.msg(f"\n|g{caller.key} applies a fragrant medicinal poultice to your wounds (+{heal_val} HP)!|n\n")

    return True, f"Poultice applied to {recipient.key}."


def craft_poison(caller):
    """Brews venom from toxic nightshade flora."""
    nightshade = None
    for obj in caller.contents:
        if getattr(obj.db, "is_herb", False) and obj.db.herb_type == "poison":
            nightshade = obj
            break

    if not nightshade:
        return False, "You need Nightshade Belladonna to extract and distill weapon poison!"

    nightshade.delete()
    poison_vial = create_object(Object, key="Vial of Viper Venom", location=caller)
    poison_vial.db.desc = "A small glass vial filled with viscous, iridescent green serpent toxin."
    poison_vial.db.is_blade_poison = True
    poison_vial.db.poison_charges = 5
    poison_vial.db.poison_dmg = 15

    caller.msg("\n|mYou distill the lethal juices into a concentrated |wVial of Viper Venom|m!|n\n")
    return True, "Poison distilled."


def coat_weapon_with_poison(caller, weapon_target=""):
    """Coats an equipped or carried weapon with blade venom."""
    vial = None
    for obj in caller.contents:
        if getattr(obj.db, "is_blade_poison", False):
            vial = obj
            break

    if not vial:
        return False, "You do not have a vial of weapon poison in your pack!"

    weapon = None
    if weapon_target:
        weapon = caller.search(weapon_target, location=caller)
    else:
        # Check equipped hands
        equipped = getattr(caller.db, "equipped_slots", {}) or {}
        weapon = equipped.get("right_hand") or equipped.get("left_hand")

    if not weapon:
        return False, "You must hold or specify a weapon to coat in venom!"

    charges = getattr(vial.db, "poison_charges", 5)
    dmg = getattr(vial.db, "poison_dmg", 15)
    vial.delete()

    weapon.db.poison_coated = True
    weapon.db.poison_charges = charges
    weapon.db.poison_dmg = dmg

    caller.msg(f"\n|gYou carefully unstopper the venom and coat the edge of {weapon.key}. The blade glimmers with toxic death ({charges} strikes)!|n\n")
    return True, f"{weapon.key} coated in venom."

