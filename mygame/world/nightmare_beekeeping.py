"""
Nightmare LPmud Wild Beekeeping, Honeycombs & Mead Fermentation Engine.

Implements:
1. Wild Beehives nestled in forest canopies and meadows.
2. Hive pacification via smoke torches/smokers ('smoke bees' / 'smoke hive').
3. Stinging swarm defense if harvested without smoke pacification.
4. Honeycomb and Beeswax harvesting ('harvest hive' / 'harvest honey').
5. Mead cask fermentation ('brewmead' / 'ferment mead').
6. Beeswax candle crafting ('craftcandle').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def create_wild_beehive(location, name="Wild Buzzing Beehive"):
    """Spawns an interactive wild beehive."""
    hive = create_object(Object, key=name, location=location)
    hive.db.is_beehive = True
    hive.db.is_pacified = False
    hive.db.honey_charges = 3
    hive.db.desc = "A large papery wild beehive hanging from heavy boughs, alive with industrious golden bees."
    return hive


def create_bee_smoker(location, name="Tin Bee Smoker"):
    """Spawns a bee smoker tool."""
    smoker = create_object(Object, key=name, location=location)
    smoker.db.is_bee_smoker = True
    smoker.db.desc = "A small tin bellows-canister billowing aromatic dried pine needles and herbal smoke."
    return smoker


def smoke_hive(caller, hive_name=""):
    """Smokes a beehive to pacify the bees."""
    room = caller.location
    hive = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_beehive", False):
            if not hive_name or hive_name.lower() in obj.key.lower():
                hive = obj
                break

    if not hive:
        return False, "There is no beehive here to smoke."

    has_smoker = any(
        getattr(obj.db, "is_bee_smoker", False) or "smoker" in obj.key.lower() or "torch" in obj.key.lower()
        for obj in caller.contents
    )

    if not has_smoker:
        return False, "You need a bee smoker or a lit torch to produce smoke!"

    hive.db.is_pacified = True
    caller.msg(f"\n|yYou puff gentle, herbal smoke into {hive.key}. The angry buzzing subsides into a drowsy hum.|n\n")
    if room:
        room.msg_contents(
            f"{caller.key} wafts thick herbal smoke into {hive.key}, calming the hive.",
            exclude=[caller]
        )
    return True, "Hive pacified."


def harvest_hive(caller, hive_name=""):
    """Harvests honeycomb and beeswax from a hive."""
    room = caller.location
    hive = None
    for obj in (room.contents if room else []):
        if getattr(obj.db, "is_beehive", False):
            if not hive_name or hive_name.lower() in obj.key.lower():
                hive = obj
                break

    if not hive:
        return False, "There is no beehive here to harvest."

    charges = getattr(hive.db, "honey_charges", 0) or 0
    if charges <= 0:
        return False, f"{hive.key} has already been emptied of its golden honey. Give the bees time to replenish."

    # If not pacified, bees attack!
    if not getattr(hive.db, "is_pacified", False):
        curr_hp = getattr(caller.db, "hp", 100) or 100
        caller.db.hp = max(1, curr_hp - 15)
        caller.msg(
            "\n|R*BZZZZZT!* An enraged cloud of stinging honeybees erupts from the hive and attacks you!|n\n"
            "|rYou are stung repeatedly across your face and arms! (-15 HP)|n\n"
            "|yTip: Use a bee smoker or lit torch with 'smoke bees' first!|n\n"
        )
        if room:
            room.msg_contents(
                f"|rA furious swarm of bees pours out of {hive.key} and stings {caller.key} vigorously!|n",
                exclude=[caller]
            )
        return False, "Attacked by swarm."

    hive.db.honey_charges = charges - 1
    # Create honeycomb
    comb = create_object(Object, key="Golden Honeycomb", location=caller)
    comb.db.desc = "A pristine hexagon-patterned comb dripping with fragrant, sweet wild clover honey."
    comb.db.is_honeycomb = True
    comb.db.is_food = True
    comb.db.heal_hp = 25

    # Create beeswax
    wax = create_object(Object, key="Chunk of Pure Beeswax", location=caller)
    wax.db.desc = "A fragrant block of golden beeswax, ideal for candle making and sealing letters."
    wax.db.is_beeswax = True

    caller.msg(
        f"\n|YYou carefully reach into {hive.key} with a comb blade, lifting out a rich, dripping |wGolden Honeycomb|Y and a |wChunk of Pure Beeswax|Y!|n\n"
    )
    if room:
        room.msg_contents(
            f"{caller.key} harvests fresh honeycombs and wax from {hive.key}.",
            exclude=[caller]
        )
    return True, "Harvested successfully."


def brew_mead(caller):
    """Ferments golden mead from harvested honeycomb."""
    comb = None
    for obj in caller.contents:
        if getattr(obj.db, "is_honeycomb", False) or "honeycomb" in obj.key.lower():
            comb = obj
            break

    if not comb:
        return False, "You need a Golden Honeycomb to ferment wild mead!"

    comb.delete()
    mead = create_object(Object, key="Jug of Golden Clover Mead", location=caller)
    mead.db.desc = "A stoneware jug of sweet, potent fermented honey mead that warms the chest with liquid courage."
    mead.db.is_drink = True
    mead.db.potency = 20

    caller.msg(
        "\n|YYou combine rich wild honey with pure spring water and yeast, letting it ferment into a potent |wJug of Golden Clover Mead|Y!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} ferments fragrant honeycombs into a jug of golden mead.",
            exclude=[caller]
        )
    return True, "Mead brewed."


def craft_candle(caller):
    """Crafts beeswax candles from harvested wax."""
    wax = None
    for obj in caller.contents:
        if getattr(obj.db, "is_beeswax", False) or "beeswax" in obj.key.lower():
            wax = obj
            break

    if not wax:
        return False, "You need a Chunk of Pure Beeswax to craft candles!"

    wax.delete()
    candle = create_object(Object, key="Fragrant Beeswax Taper Candle", location=caller)
    candle.db.desc = "A hand-rolled beeswax taper candle with a braided hemp wick. Burns with a clean, honey-scented flame."
    candle.db.is_light = True

    caller.msg("\n|YYou warm and roll the beeswax around a hemp wick, crafting a |wFragrant Beeswax Taper Candle|Y!|n\n")
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} hand-crafts a fragrant beeswax candle.",
            exclude=[caller]
        )
    return True, "Candle crafted."

