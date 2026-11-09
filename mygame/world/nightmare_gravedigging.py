"""
Nightmare LPmud Gravedigging, Crypt Excavation & Relic Hunting Engine.

Implements:
1. Iron Shovel & Excavation Tools.
2. Crypt and Graveyard soil excavation ('dig', 'excavate').
3. Relic discovery: burial urns, rusted coffers, ancient signet rings, grave dust.
4. Crypt Ghoul and vengeful spirit ambush encounters.
"""

import random
from evennia.utils.create import create_object
from typeclasses.objects import Object

GRAVE_REWARD_TABLE = [
    {
        "name": "Ancient Signet Ring",
        "desc": "A tarnished silver signet ring bearing a faded noble family seal.",
        "coins": 45,
        "type": "relic"
    },
    {
        "name": "Burial Urn of Ashes",
        "desc": "An ornate ceramic funerary urn sealed with pitch, flecked with gold leaf.",
        "coins": 75,
        "type": "relic"
    },
    {
        "name": "Pouch of Grave Dust",
        "desc": "A pinch of consecrated soil and pulverized bone, prized by necromancers and alchemists.",
        "coins": 30,
        "type": "reagent"
    },
    {
        "name": "Carved Bone Dagger",
        "desc": "A wickedly sharp ritual dagger carved from an ancient humanoid femur.",
        "coins": 60,
        "type": "weapon"
    },
    {
        "name": "Rotted Coffer of Old Coins",
        "desc": "A crumbling wooden chest bound in verdigris-crusted copper filled with antique coins.",
        "coins": 120,
        "type": "treasure"
    }
]

AMBUSH_MONSTERS = [
    {
        "name": "Crypt Ghoul",
        "desc": "A snarling, pale-skinned humanoid with elongated claws and hunger-crazed eyes!",
        "hp": 95,
        "level": 6
    },
    {
        "name": "Vengeful Tomb Wraith",
        "desc": "A shrieking apparition of chilling spectral mist disturbed from its eternal slumber!",
        "hp": 110,
        "level": 7
    },
    {
        "name": "Restless Skeleton",
        "desc": "A clattering skeleton brandishing a rusted cemetery scythe!",
        "hp": 80,
        "level": 5
    }
]


def create_iron_shovel(location, name="Heavy Iron Shovel"):
    """Spawns an iron excavation shovel."""
    shovel = create_object(Object, key=name, location=location)
    shovel.db.is_shovel = True
    shovel.db.desc = "A sturdy iron-headed spade with an ash wood handle, perfect for digging earth and unearthing crypts."
    return shovel


def is_excavation_site(room):
    """Determines if a room is eligible for gravedigging."""
    if not room:
        return False
    if getattr(room.db, "can_dig", False) or getattr(room.db, "is_graveyard", False):
        return True

    text = f"{room.key} {room.db.desc or ''}".lower()
    keywords = ["grave", "cemetery", "crypt", "catacomb", "tomb", "mausoleum", "barrow", "burial"]
    return any(kw in text for kw in keywords)


def perform_excavation(caller):
    """Performs excavation in the caller's room."""
    room = caller.location
    if not is_excavation_site(room):
        return False, "The soil here is too compact or paved over. You can only excavate in graveyards, crypts, and ancient burial sites."

    # Check for shovel
    shovel = None
    for obj in caller.contents:
        if getattr(obj.db, "is_shovel", False) or "shovel" in obj.key.lower() or "spade" in obj.key.lower():
            shovel = obj
            break

    if not shovel:
        return False, "You need a shovel or spade in your inventory to dig here!"

    # Perform excavation roll
    roll = random.randint(1, 100)

    # 30% Ambush encounter
    if roll <= 30:
        ambush_data = random.choice(AMBUSH_MONSTERS)
        monster = create_object(Object, key=ambush_data["name"], location=room)
        monster.db.desc = ambush_data["desc"]
        monster.db.hp = ambush_data["hp"]
        monster.db.max_hp = ambush_data["hp"]
        monster.db.level = ambush_data["level"]

        caller.msg(
            f"\n|R[AMBUSH!]|n As your shovel strikes wood deep in the burial earth, the soil explodes outward!\n"
            f"|rA {monster.key} claws its way out of the grave and lunges at you!|n\n"
        )
        if room:
            room.msg_contents(
                f"|r*ROAR!* A {monster.key} erupts from the newly opened grave, attacking {caller.key}!|n",
                exclude=[caller]
            )
        return True, "Encounter triggered."

    # 55% Loot discovery
    elif roll <= 85:
        relic_data = random.choice(GRAVE_REWARD_TABLE)
        item = create_object(Object, key=relic_data["name"], location=caller)
        item.db.desc = relic_data["desc"]
        item.db.value = relic_data["coins"]

        # Award bonus silver/gold coins
        caller.db.coins = (getattr(caller.db, "coins", 0) or 0) + relic_data["coins"]

        caller.msg(
            f"\n|Y*CLINK!*|n Your shovel strikes a submerged stone cavity!\n"
            f"You unearth |w{item.key}|n and recover |y{relic_data['coins']} ancient coins|n from the burial earth!\n"
        )
        if room:
            room.msg_contents(
                f"{caller.key} thrusts their shovel into the earth and unearths an ancient relic!",
                exclude=[caller]
            )
        return True, "Relic unearthed."

    # 15% Empty dirt
    else:
        caller.msg("\nYou shovel aside damp grave dirt, but find only rotted wood shards and worms.\n")
        if room:
            room.msg_contents(f"{caller.key} digs through the cemetery loam with their shovel.", exclude=[caller])
        return True, "Empty dig."

