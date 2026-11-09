"""
Nightmare LPmud Foraging, Monster Skinning & Blade Poison System.

Implements:
1. Corpse Butchering & Skinning (hides, pelts, dragon scales, venison).
2. Biome-based Herbal Foraging (Kingsfoil, Nightshade, Silverleaf, Viper Lily).
3. Alchemy & Weapon Envenoming ('apply poison to <weapon>').
4. Poison debuff ticks during combat.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

HERBS = {
    "forest": [
        ("Kingsfoil", "A soothing green leaf with potent wound-knitting properties.", "heal"),
        ("Nightshade", "A dark bell-shaped flower dripping with lethal neurotoxin.", "poison"),
        ("Silverleaf", "A shimmering silver herb that replenishes mental clarity.", "mana")
    ],
    "mountain": [
        ("Frostmint", "A biting cold alpine leaf that cools fever and soothes wounds.", "heal"),
        ("Ironbark Root", "A dense fibrous root that hardens the skin.", "stoneskin")
    ],
    "swamp": [
        ("Viper Lily", "A foul-smelling violet bloom oozing paralyzing venom.", "poison"),
        ("Bog Spores", "Noxious fungal spores that induce blinding sickness.", "poison")
    ],
    "underdark": [
        ("Glowshroom", "Bioluminescent mushroom that emits a soft subterranean glow.", "light"),
        ("Shadow Thistle", "A prickly blackened stalk laced with deadly shadow poison.", "poison")
    ]
}


def skin_corpse(caller, corpse):
    """Skins and butchers a fallen creature's corpse for pelts, hides, or meat."""
    if not corpse or not corpse.key.lower().startswith("corpse"):
        return False, "You can only skin fallen corpses!"

    if getattr(corpse.db, "is_skinned", False):
        return False, "This corpse has already been stripped of its usable hides and meat."

    corpse.db.is_skinned = True
    c_name = corpse.key.replace("Corpse of ", "").strip()

    # Determine harvest loot
    loot_created = []
    if "Dragon" in c_name or "Drake" in c_name:
        scale = create_object(Object, key=f"Gleaming {c_name} Scale", location=caller)
        scale.db.desc = f"A hard, iridescent scale harvested from a {c_name}. Used in masterwork armorsmithing."
        scale.db.value = 120
        scale.db.weight = 3
        loot_created.append(scale.key)
    elif "Wolf" in c_name or "Bear" in c_name or "Beast" in c_name:
        pelt = create_object(Object, key=f"Thick {c_name} Pelt", location=caller)
        pelt.db.desc = f"A dense, warm pelt skinned from a {c_name}."
        pelt.db.value = 45
        pelt.db.weight = 2
        loot_created.append(pelt.key)
    else:
        leather = create_object(Object, key="Tanned Leather Hide", location=caller)
        leather.db.desc = "A workable square of cured leather hide."
        leather.db.value = 20
        leather.db.weight = 2
        loot_created.append(leather.key)

    meat = create_object(Object, key=f"Chunk of Fresh {c_name} Meat", location=caller)
    meat.db.desc = "Raw monster venison. Can be cooked or fed to beasts."
    meat.db.value = 5
    meat.db.weight = 1
    loot_created.append(meat.key)

    caller.msg(f"|gWith swift, practiced incisions, you skin and butcher {corpse.key}!|n")
    caller.msg(f"Harvested: |w{', '.join(loot_created)}|n.")

    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} field-dresses and skins {corpse.key}.",
            exclude=[caller]
        )
    return True, "Harvest complete."


def forage_herbs(caller):
    """Searches current room's terrain for natural herbs and flora."""
    loc = caller.location
    if not loc:
        return False, "You cannot forage in the void."

    terrain = getattr(loc.db, "terrain", "forest") or "forest"
    terrain_key = terrain.lower()

    herb_table = HERBS.get(terrain_key, HERBS["forest"])
    roll = random.randint(1, 100) + (caller.db.wis or 10)

    # Cooldown per room instance
    loc_searched_key = f"_foraged_{loc.id}"
    if getattr(caller.ndb, loc_searched_key, False):
        return False, "You have already scoured this immediate area for herbs. Search elsewhere."

    setattr(caller.ndb, loc_searched_key, True)

    if roll < 40:
        return False, "You search through the undergrowth, but find no useful flora here."

    name, desc, effect = random.choice(herb_table)
    herb = create_object(Object, key=name, location=caller)
    herb.db.desc = desc
    herb.db.herb_effect = effect
    herb.db.value = 15
    herb.db.weight = 1

    caller.msg(f"|gYou forage carefully through the brush and discover: |y{name}|g!|n")
    caller.msg(f"|xProperty:|n {desc}")
    return True, f"Found {name}."


def apply_poison_to_weapon(caller, herb_or_poison, weapon):
    """Envenoms a bladed weapon with poison charges."""
    if not getattr(herb_or_poison.db, "herb_effect", None) == "poison" and "Poison" not in herb_or_poison.key:
        return False, f"{herb_or_poison.key} does not contain an active toxin!"

    slot = getattr(weapon.db, "slot", None)
    if slot not in ["right_hand", "left_hand"] and getattr(weapon.db, "damage_bonus", None) is None:
        return False, f"{weapon.key} is not a valid weapon to envenom!"

    weapon.db.poison_charges = (weapon.db.poison_charges or 0) + 6
    weapon.db.poison_potency = random.randint(6, 12)

    herb_key = herb_or_poison.key
    herb_or_poison.delete()

    caller.msg(f"|GYou crush the {herb_key} and coat the cutting edge of {weapon.key} with glistening, virulent venom!|n")
    caller.msg(f"Poison charges remaining: |w{weapon.db.poison_charges}|n strikes.")
    return True, "Weapon envenomed."

