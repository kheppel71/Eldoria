"""
Nightmare LPmud Mineral Prospecting, Mining & Smelting Engine.

Implements:
1. Room prospecting ('prospect') for mineral veins in subterranean/rocky terrain.
2. Ore extraction with pickaxes ('mine').
3. Foundry smelting ('smelt <ore>') converting raw ores into refined metal ingots.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

ORES = {
    "iron": {"name": "Iron Ore Chunk", "ingot": "Refined Iron Ingot", "val": 8, "ingot_val": 25},
    "silver": {"name": "Silver Ore Chunk", "ingot": "Solid Silver Bar", "val": 20, "ingot_val": 60},
    "mithril": {"name": "Luminous Mithril Ore", "ingot": "Enchanted Mithril Ingot", "val": 65, "ingot_val": 200}
}


def prospect_room(caller):
    """Scans the room's geological features for mineral deposits."""
    loc = caller.location
    if not loc:
        return False, "You cannot prospect in the void."

    terrain = getattr(loc.db, "terrain", "city") or "city"
    if terrain.lower() not in ["mountain", "dungeon", "underdark", "cave", "rocky"]:
        caller.msg("The soil here is loamy and soft; there are no exposed mineral veins to prospect.")
        return True, "No deposits."

    deposit = getattr(loc.db, "ore_deposit", None)
    if not deposit:
        # Generate deposit
        choice = random.choice(["iron", "iron", "silver", "mithril"])
        loc.db.ore_deposit = {"type": choice, "richness": random.randint(3, 7)}
        deposit = loc.db.ore_deposit

    o_type = deposit["type"]
    richness = deposit["richness"]

    caller.msg(f"\n|Y[PROSPECTING SUCCESS]|n You chip away surface scree and discover a vein of |w{ORES[o_type]['name']}|n!")
    caller.msg(f"Richness: |c{richness} ore chunks remaining|n. (Use: |wmine|n with a pickaxe)\n")
    return True, "Prospected."


def mine_ore_deposit(caller, pickaxe_obj):
    """Mines ore chunks from an exposed mineral vein."""
    loc = caller.location
    deposit = getattr(loc.db, "ore_deposit", None)
    if not deposit or deposit.get("richness", 0) <= 0:
        return False, "There are no exposed mineral veins here to mine. Try |wprospect|n first."

    stamina = caller.db.stamina or 0
    if stamina < 15:
        return False, "You are too fatigued to swing the heavy pickaxe! (Requires 15 Stamina)"

    caller.db.stamina -= 15

    o_type = deposit["type"]
    deposit["richness"] -= 1
    loc.db.ore_deposit = deposit

    ore_data = ORES[o_type]
    chunk = create_object(Object, key=ore_data["name"], location=caller)
    chunk.db.desc = f"A heavy, jagged chunk of raw {o_type.capitalize()} ore, glittering with unrefined metallic veins."
    chunk.db.ore_type = o_type
    chunk.db.value = ore_data["val"]
    chunk.db.weight = 3

    caller.msg(f"\n|y*CLANG-CRACK!* You drive {pickaxe_obj.key} into the rock face, dislodging a heavy |w{chunk.key}|y!|n")
    caller.msg(f"Remaining in vein: {deposit['richness']} chunks.\n")

    if loc:
        loc.msg_contents(
            f"|ySparks fly as {caller.key} swings a pickaxe into the rock, quarrying {chunk.key}!|n",
            exclude=[caller]
        )
    return True, "Mined."


def smelt_ore_into_ingot(caller, ore_obj):
    """Smelts raw ore chunks at a forge or foundry into refined metal ingots."""
    o_type = getattr(ore_obj.db, "ore_type", None)
    if not o_type or o_type not in ORES:
        return False, f"{ore_obj.key} is not raw ore that can be smelted."

    ore_data = ORES[o_type]
    ore_name = ore_obj.key
    ore_obj.delete()

    ingot = create_object(Object, key=ore_data["ingot"], location=caller)
    ingot.db.desc = f"A pure, refined bar of {o_type.capitalize()} cast in the foundry molds."
    ingot.db.is_ingot = True
    ingot.db.value = ore_data["ingot_val"]
    ingot.db.weight = 2

    caller.msg(f"\n|Y[FOUNDRY SMELTING]|n You heat {ore_name} in the blazing furnace, pouring the slag away to cast |w{ingot.key}|Y!|n")
    caller.msg(f"Value: |y{ingot.db.value} Gold|n.\n")

    if caller.location:
        caller.location.msg_contents(
            f"Furnace heat roars as {caller.key} pours molten metal into an ingot mold.",
            exclude=[caller]
        )
    return True, "Smelted."

