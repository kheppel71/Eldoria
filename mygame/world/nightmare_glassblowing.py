"""
Nightmare LPmud Glassblowing, Alchemical Phials & Stained Glass Artistry Engine.

Implements:
1. Silica Quartz Sand Harvesting ('gatherquartz').
2. Blowpipe Glass Shaping ('blowglass'):
   - Reinforced Alchemical Phials (Heat-tempered potion containers)
   - Distillation Alembics & Retorts (High-tier alchemy glass)
   - Prismatic Stained Glass Tiles (Artisan decorative mosaic glass)
3. Glass Annealing and stress-relief cooling.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

GLASS_RECIPES = {
    "phial": {
        "name": "Reinforced Alchemical Phial",
        "sand_cost": 1,
        "value": 15,
        "desc": "A thick, heat-tempered borosilicate glass phial sealed with ground-glass stopper, ideal for volatile potions."
    },
    "alembic": {
        "name": "Curved Distillation Alembic",
        "sand_cost": 2,
        "value": 35,
        "desc": "A beautifully blown glass retort with a swan-neck condenser tube, prized by master alchemists."
    },
    "stainedtile": {
        "name": "Prismatic Stained Glass Tile",
        "sand_cost": 2,
        "value": 40,
        "desc": "A luminous sheet of cobalt and ruby stained glass that refracts sunlight into dazzling rainbow patterns."
    }
}


def gather_silica_quartz(caller):
    """Gathers fine silica quartz sand from shores, riverbeds, and gravel banks."""
    room = caller.location
    if not room:
        return False, "You cannot gather materials in the void."

    sand = create_object(Object, key="Pouch of Pure Silica Quartz", location=caller)
    sand.db.is_silica = True
    sand.db.desc = "A pouch of powdery, sparkling white quartz sand suitable for melting in a glassblower's furnace."

    caller.msg("\n|Y[GATHERING]|n You sift fine, glistening white quartz sand from the earth into a pouch!\n")
    if room:
        room.msg_contents(f"{caller.key} sifts through the sand and collects fine quartz crystals.", exclude=[caller])
    return True, "Quartz gathered."


def blow_glass_item(caller, item_key="phial"):
    """Shapes molten glass using an iron blowpipe and furnace heat."""
    key = item_key.strip().lower()
    matched = next((k for k in GLASS_RECIPES if key in k), None)

    if not matched:
        opts = ", ".join(GLASS_RECIPES.keys())
        return False, f"Unknown glass recipe '{item_key}'. Options: {opts}"

    recipe = GLASS_RECIPES[matched]
    needed_sand = recipe["sand_cost"]

    # Check for silica sand
    sand_items = [obj for obj in caller.contents if getattr(obj.db, "is_silica", False) or "silica" in obj.key.lower()]
    if len(sand_items) < needed_sand:
        return False, f"Crafting a {recipe['name']} requires {needed_sand} pouches of Pure Silica Quartz (you have {len(sand_items)})."

    # Consume sand
    for _ in range(needed_sand):
        sand_items.pop().delete()

    glass_obj = create_object(Object, key=recipe["name"], location=caller)
    glass_obj.db.is_glassware = True
    glass_obj.db.value = recipe["value"]
    glass_obj.db.desc = recipe["desc"]

    caller.msg(
        f"\n|Y[GLASSBLOWING ARTISTRY]|n You gather a gather of molten glass upon the blowpipe!\n"
        f"Spinning and blowing through the pipe with controlled lung pressure, you shape a pristine |w{glass_obj.key}|n!\n"
        f"You place it into the annealing lehr to cool slowly and relieve internal stress.\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} spins an iron blowpipe with expert breathwork, fashioning a gleaming {glass_obj.key}!",
            exclude=[caller]
        )
    return True, f"Crafted {glass_obj.key}."

