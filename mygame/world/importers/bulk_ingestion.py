"""
Bulk World Ingestion Engine for Eldoria MUD

Imports 150+ interconnected rooms across 5 major open-source inspired zones:
1. The Grand City of Midgaard (CircleMUD / tbaMUD) [Level 1-5]
2. The Ironcrag Goblin Mountain & Mines (tbaMUD) [Level 6-11]
3. The Province & Catacombs of Old Praxis (Nightmare IV) [Level 9-15]
4. The Shadowfen Necropolis & Mausoleum (CircleMUD) [Level 13-18]
5. The Astral Rifts & Elemental Spires (High-End / DCSS) [Level 18-25+]

Features:
- Dual Overland & Maritime Ferry access (New Royal Galleon route)
- Fixed danger tiers with complete Nightmare LPmud combat stats & limbs
- DCSS-style item affixes & fantasy relics
- 100% GMCP Room.Info automapper telemetry
"""

from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.characters import Character
from typeclasses.objects import Object
from world.importers.zone_importer import (
    find_room_by_key,
    compute_relative_coordinates,
    purge_zone,
    STANDARD_ALIASES,
    OPPOSITE_DIR,
    TAG_WORLD
)
from world.nightmare_core import EQUIPMENT_SLOTS

DEFAULT_HUMANOID_LIMBS = {
    "head": 0.25,
    "torso": 0.45,
    "right arm": 0.25,
    "left arm": 0.25,
    "right leg": 0.30,
    "left leg": 0.30,
}
import world.sailing as sailing

# =============================================================================
# COMBAT & BESTIARY INITIALIZATION HELPER
# =============================================================================

def init_mob_combat(mob, level=1, role="warrior", danger_tier="normal"):
    """
    Initializes fixed danger-level combat attributes, stats, limbs, skills,
    spells, and currency drops for imported monsters.
    """
    mob.db.level = level
    mob.db.is_character = True
    mob.db.is_npc = True

    # Stat scaling: base 10 + (level * 1.5)
    base_stat = 10 + int(level * 1.4)
    if role == "warrior":
        stats = {
            "str": base_stat + 4, "con": base_stat + 3,
            "dex": base_stat, "int": base_stat - 4,
            "wis": base_stat - 2, "cha": base_stat - 2
        }
        hp_pool = 40 + (level * 25)
        mana_pool = 20 + (level * 5)
    elif role == "mage":
        stats = {
            "str": base_stat - 3, "con": base_stat,
            "dex": base_stat + 2, "int": base_stat + 6,
            "wis": base_stat + 4, "cha": base_stat
        }
        hp_pool = 30 + (level * 18)
        mana_pool = 50 + (level * 35)
    elif role == "rogue":
        stats = {
            "str": base_stat, "con": base_stat + 1,
            "dex": base_stat + 6, "int": base_stat + 2,
            "wis": base_stat - 1, "cha": base_stat + 3
        }
        hp_pool = 35 + (level * 20)
        mana_pool = 30 + (level * 10)
    elif role == "boss":
        stats = {
            "str": base_stat + 8, "con": base_stat + 8,
            "dex": base_stat + 6, "int": base_stat + 6,
            "wis": base_stat + 6, "cha": base_stat + 6
        }
        hp_pool = 100 + (level * 60)
        mana_pool = 80 + (level * 40)
    else:  # civilian / neutral
        stats = {"str": 10, "con": 10, "dex": 10, "int": 10, "wis": 10, "cha": 10}
        hp_pool = 25 + (level * 10)
        mana_pool = 15

    mob.db.stats = stats
    mob.db.max_hp = hp_pool
    mob.db.hp = hp_pool
    mob.db.max_mana = mana_pool
    mob.db.mana = mana_pool
    mob.db.max_stamina = 100 + (level * 10)
    mob.db.stamina = mob.db.max_stamina

    # Limbs
    limbs = {}
    for limb_name, ratio in DEFAULT_HUMANOID_LIMBS.items():
        limb_hp = max(10, int(hp_pool * ratio))
        limbs[limb_name] = {"hp": limb_hp, "max_hp": limb_hp}
    mob.db.limbs = limbs

    # Skills
    skill_val = min(100, 15 + (level * 3))
    mob.db.skills = {
        "blade": skill_val, "blunt": skill_val, "projectile": skill_val,
        "brawl": skill_val, "defense": skill_val, "parry": skill_val // 2,
        "magic attack": skill_val if role in ["mage", "boss"] else 10,
        "magic defense": skill_val // 2
    }

    # Spells for mages and bosses
    if role in ["mage", "boss"]:
        if level >= 15:
            mob.db.spellbook = ["firebolt", "fireball", "lightning", "heal"]
        elif level >= 8:
            mob.db.spellbook = ["firebolt", "fireball", "heal"]
        else:
            mob.db.spellbook = ["firebolt"]
    else:
        mob.db.spellbook = []

    # Coins dropped upon defeat
    if danger_tier == "boss":
        mob.db.coins = {"copper": level * 10, "silver": level * 5, "gold": max(5, level * 2)}
    elif level >= 12:
        mob.db.coins = {"copper": 20, "silver": 12, "gold": max(1, level // 3)}
    elif level >= 5:
        mob.db.coins = {"copper": 25, "silver": level, "gold": 0}
    else:
        mob.db.coins = {"copper": 10 + (level * 2), "silver": 0, "gold": 0}

    mob.db.slots = {slot: None for slot in EQUIPMENT_SLOTS}


# =============================================================================
# BULK ZONE DEFINITIONS (5 ZONES, 150 ROOMS)
# =============================================================================

def build_zone_1_midgaard():
    """Zone 11: The Grand City of Midgaard (CircleMUD / tbaMUD) [Level 1-5] - 35 Rooms"""
    return {
        "zone_key": "midgaard_district",
        "zone_name": "The Grand City of Midgaard",
        "default_terrain": "city",
        "base_coords": (0, 15, 0),
        "rooms": {
            # South Gates & Promenade
            "south_gate": {
                "name": "Midgaard South Gate",
                "desc": "A fortified portcullis of dark iron spans the southern threshold of Midgaard. Stone ramparts flank the archway, draped in blue-and-gold civic banners. Royal guards inspect wagons and pilgrims passing through.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "southern_square", "alias": "n"}},
                "npcs": [{"name": "Midgaard Gate Sentry", "desc": "A stout halberdier in polished brass livery.", "level": 4, "role": "warrior"}]
            },
            "southern_square": {
                "name": "Midgaard Southern Square",
                "desc": "Wide granite cobbles form an expansive plaza humming with activity. Street vendors hawk meat pies, roasted chestnuts, and spun sugar from wooden pushcarts.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "south_gate", "alias": "s"}, "north": {"dest_id": "temple_square", "alias": "n"}, "east": {"dest_id": "bazaar_lane_1", "alias": "e"}, "west": {"dest_id": "thieves_alley_1", "alias": "w"}},
                "npcs": [{"name": "Midgaard Street Urchin", "desc": "A swift youth with nimble fingers and a dusty cap.", "level": 2, "role": "rogue"}]
            },
            "temple_square": {
                "name": "The Great Temple Square",
                "desc": "In the center of Midgaard stands the soaring plaza of the Temple. A magnificent marble fountain depicting an angelic seraph pouring water from an urn creates a soothing murmur.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "southern_square", "alias": "s"}, "north": {"dest_id": "grand_temple_foyer", "alias": "n"}, "east": {"dest_id": "market_square", "alias": "e"}, "west": {"dest_id": "barracks_gate", "alias": "w"}},
                "items": [{"name": "Midgaard Civic Guidebook", "desc": "A printed pamphlet welcoming pilgrims to the realm of Midgaard."}]
            },
            "grand_temple_foyer": {
                "name": "The Grand Temple Foyer",
                "desc": "Sunlight filters through magnificent stained glass depictions of celestial pantheons. Towering marble pillars of white and gold rise into a high painted vaulted ceiling.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "temple_square", "alias": "s"}, "north": {"dest_id": "cleric_sanctum", "alias": "n"}, "east": {"dest_id": "shrine_wisdom", "alias": "e"}, "west": {"dest_id": "shrine_valor", "alias": "w"}},
                "npcs": [{"name": "Temple Novice", "desc": "A pious acolyte sweeping the polished marble flagstones.", "level": 1, "role": "civilian"}]
            },
            "cleric_sanctum": {
                "name": "The Clerics' High Sanctuary",
                "desc": "Incense clouds swirl softly around a massive bronze altar of dawn. Candles flicker in sacred candelabras, casting warm amber light across holy scripture podiums.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "grand_temple_foyer", "alias": "s"}, "down": {"dest_id": "temple_crypt", "alias": "d"}},
                "npcs": [{"name": "High Templar Valerius", "desc": "A silver-haired divine commander wielding a gleaming war hammer.", "level": 6, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Vial of Midgaard Holy Water", "desc": "Consecrated water blessed upon the High Sanctuary altar."}]
            },
            "shrine_wisdom": {
                "name": "Shrine of Celestial Wisdom",
                "desc": "A quiet alcove where scholars and mystics meditate before a statue of an owl perched on an open tome.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "grand_temple_foyer", "alias": "w"}}
            },
            "shrine_valor": {
                "name": "Shrine of Martial Valor",
                "desc": "Trophies of shattered demonic battle-axes and bent shields hang proudly beneath the statue of a winged paladin.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "grand_temple_foyer", "alias": "e"}}
            },
            "temple_crypt": {
                "name": "The Silent Crypt of the Ancients",
                "desc": "Chilly air clings to stone sarcophagi resting in arched niches. The floor is dusted with centuries of consecrated ashes.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "cleric_sanctum", "alias": "u"}, "north": {"dest_id": "tomb_paladins", "alias": "n"}},
                "npcs": [{"name": "Crypt Beetle", "desc": "A hand-sized chitinous scavenger with clicking mandibles.", "level": 2, "role": "warrior"}]
            },
            "tomb_paladins": {
                "name": "Tomb of the Knight-Paladins",
                "desc": "Stone effigies of ancient paladins lie in rest upon carved sepulchers, their carved stone hands clasped around longswords.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "temple_crypt", "alias": "s"}},
                "items": [{"name": "Tarnished Paladin Shield", "desc": "A heavy kite shield bearing an embossed sunburst emblem."}]
            },
            # Market District
            "market_square": {
                "name": "Midgaard Market Square",
                "desc": "A lively open-air bazaar bustling with traders from across the continent. Canopied stalls brim with exotic textiles, spices, weapons, and pottery.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "temple_square", "alias": "w"}, "north": {"dest_id": "bazaar_north", "alias": "n"}, "east": {"dest_id": "port_promenade", "alias": "e"}, "south": {"dest_id": "bazaar_lane_1", "alias": "s"}},
                "npcs": [{"name": "Midgaard Fruit Hawker", "desc": "A jovial merchant calling out prices for ripe figs and winter apples.", "level": 1, "role": "civilian"}]
            },
            "bazaar_north": {
                "name": "Northern Merchant Way",
                "desc": "The northern stretch of the bazaar where master craftsmen ply their trade. The rhythmic clinking of smithy hammers echoes from the east.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "market_square", "alias": "s"}, "east": {"dest_id": "midgaard_smithy", "alias": "e"}, "west": {"dest_id": "midgaard_bakery", "alias": "w"}}
            },
            "midgaard_bakery": {
                "name": "The Crust & Crumb Bakery",
                "desc": "Warm, buttery aromas of freshly baked sourdough loaves and honey cinnamon rolls billow from a large stone hearth oven.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "bazaar_north", "alias": "e"}},
                "items": [{"name": "Crusty Midgaard Sourdough", "desc": "A warm, golden-brown loaf capable of sustaining a traveling adventurer."}]
            },
            "midgaard_smithy": {
                "name": "Ironcrest Armory & Smithy",
                "desc": "A blazing brick forge radiates intense heat. Racks of broadswords, steel halberds, and iron breastplates line the soot-stained walls.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "bazaar_north", "alias": "w"}},
                "npcs": [{"name": "Master Blacksmith Thrain", "desc": "A burly dwarven smith with heavy leather apron and tongs.", "level": 5, "role": "warrior"}],
                "items": [{"name": "Steel Broadsword of Midgaard", "desc": "A finely tempered blade inscribed with the Midgaard crest."}]
            },
            "bazaar_lane_1": {
                "name": "Spice Merchant Row",
                "desc": "The air is fragrant with cinnamon, dried cloves, and peppercorns imported from southern islands.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "market_square", "alias": "n"}, "west": {"dest_id": "southern_square", "alias": "w"}}
            },
            # Harbor & Port Promenade
            "port_promenade": {
                "name": "Midgaard Port Promenade",
                "desc": "A broad stone embankment overlooking the bustling harbor. Sea-gulls wheel overhead, crying out as fishing smacks and merchant galleons arrive at the quays.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "market_square", "alias": "w"}, "east": {"dest_id": "midgaard_port", "alias": "e"}, "north": {"dest_id": "chandler_shop", "alias": "n"}},
                "npcs": [{"name": "Harbor Sailor", "desc": "A weathered mariner coiling thick hemp mooring lines.", "level": 3, "role": "warrior"}]
            },
            "midgaard_port": {
                "name": "Midgaard Royal Wharf",
                "desc": "The primary deep-water anchorage of Midgaard. Stout wooden piers stretch into the azure sea, welcoming international merchant vessels and the Royal Galleon.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "port_promenade", "alias": "w"}, "south": {"dest_id": "fish_market", "alias": "s"}},
                "items": [{"name": "Cask of Salt Cod", "desc": "An oak barrel packed with cured Atlantic cod."}]
            },
            "chandler_shop": {
                "name": "Saltwind Ship Chandler",
                "desc": "Coils of tarred rope, brass compasses, storm lanterns, and marine canvas clutter this maritime supply storefront.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "port_promenade", "alias": "s"}}
            },
            "fish_market": {
                "name": "The Wet Fish Wharf",
                "desc": "Slabs of ice cradle glittering silver mackerel, king crabs, and pink salmon fresh off the fishing boats.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "midgaard_port", "alias": "n"}}
            },
            # High Guard Barracks
            "barracks_gate": {
                "name": "High Guard Fortress Gate",
                "desc": "A massive portcullis and moat protect the headquarters of the Midgaard City Guard. Banners bearing the city lion flutter in the breeze.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "temple_square", "alias": "e"}, "west": {"dest_id": "drill_yard", "alias": "w"}},
                "npcs": [{"name": "Midgaard City Guard", "desc": "A vigilant soldier armed with crossbow and steel arming sword.", "level": 4, "role": "warrior"}]
            },
            "drill_yard": {
                "name": "The Soldier's Drill Yard",
                "desc": "Troops practice sword maneuvers and shield formations across compacted gravel grounds. Training dummies bristling with practice arrows stand along the walls.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "barracks_gate", "alias": "e"}, "north": {"dest_id": "armory_vault", "alias": "n"}, "south": {"dest_id": "guard_mess_hall", "alias": "s"}},
                "npcs": [{"name": "Drill Sergeant Thorne", "desc": "A battle-scarred veteran barking marching orders.", "level": 5, "role": "warrior"}]
            },
            "armory_vault": {
                "name": "Fortress Armory Vault",
                "desc": "Neat rows of chainmail hauberks, steel helms, and crossbow bolts are racked under heavy lock and key.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "drill_yard", "alias": "s"}},
                "items": [{"name": "Guard Crossbow Bolts", "desc": "A quiver of fletched steel-tipped bolts."}]
            },
            "guard_mess_hall": {
                "name": "Guard Mess & Common Hall",
                "desc": "Trestle tables and benches sit beneath mounted beast heads. Off-duty guardsmen share pitchers of amber ale and hearty stew.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "drill_yard", "alias": "n"}}
            },
            # Thieves' Alley District
            "thieves_alley_1": {
                "name": "Shadowed Alleyway",
                "desc": "The bright sunshine of the city fails to penetrate this narrow, damp cobblestone corridor. Overhead laundry lines crisscross between dilapidated tenements.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "southern_square", "alias": "e"}, "west": {"dest_id": "cutthroat_haven", "alias": "w"}, "north": {"dest_id": "pawn_shop", "alias": "n"}},
                "npcs": [{"name": "Sly Cutpurse", "desc": "A hooded rogue lurking in the shadows with an eye on coin pouches.", "level": 3, "role": "rogue"}]
            },
            "cutthroat_haven": {
                "name": "Cutthroat Blind Alley",
                "desc": "A dead-end alley littered with broken crates and rotting barrels. Whispers cease abruptly whenever someone steps near.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "thieves_alley_1", "alias": "e"}, "down": {"dest_id": "thieves_guild_den", "alias": "d"}},
                "npcs": [{"name": "Shadow Footpad", "desc": "A leather-clad ruffian testing the balance of a weighted blackjack.", "level": 4, "role": "rogue"}]
            },
            "pawn_shop": {
                "name": "The Gilded Rat Pawnbroker",
                "desc": "Grubby glass display cases show off mismatched brass rings, dented goblets, and antique pocket knives pawned by desperate locals.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "thieves_alley_1", "alias": "s"}}
            },
            "thieves_guild_den": {
                "name": "The Velvet Dagger Cellar",
                "desc": "A secret subterranean taproom lit by green tallow candles. Rogues, lockpicks, and smugglers gather around dice tables to divide contraband.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "cutthroat_haven", "alias": "u"}},
                "npcs": [{"name": "Fence Rickert", "desc": "A shifty broker who buys jewelry and relics without asking questions.", "level": 5, "role": "rogue"}],
                "items": [{"name": "Set of Brass Lockpicks", "desc": "Delicate steel and brass tension wrenches and picks."}]
            },
            # North Gate & Outskirts
            "north_gate": {
                "name": "Midgaard North Gate",
                "desc": "Massive stone archways open out into the northern rolling plains and the high highway leading to the Eldorian heartland.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "high_road", "alias": "s"}},
                "npcs": [{"name": "Midgaard Cavalry Sentry", "desc": "A mounted lancer watching the northern horizon.", "level": 5, "role": "warrior"}]
            },
            "high_road": {
                "name": "The High King's Way of Midgaard",
                "desc": "A wide paved highway connecting the Grand Temple Square to the North Gate. Fine townhouse facades border the cobblestones.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "north_gate", "alias": "n"}, "south": {"dest_id": "grand_temple_foyer", "alias": "s"}, "east": {"dest_id": "guild_wizards", "alias": "e"}}
            },
            "guild_wizards": {
                "name": "Tower of the Arcane Guild",
                "desc": "A spiral tower of blue granite where orreries spin slowly in midair and glowing runes trace circles along the polished floor.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "high_road", "alias": "w"}, "up": {"dest_id": "observatory", "alias": "u"}},
                "npcs": [{"name": "Guild Magus Corvin", "desc": "An elder mage enveloped in velvet robes embroidered with silver constellations.", "level": 6, "role": "mage"}]
            },
            "observatory": {
                "name": "The High Astrological Observatory",
                "desc": "A domed glass ceiling reveals the celestial vault above. A gigantic brass telescope points toward the north star.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "guild_wizards", "alias": "d"}},
                "items": [{"name": "Astrological Star Chart", "desc": "An illuminated parchment mapping the astral planes and constellations."}]
            },
            # West Gate & Plains
            "west_gate": {
                "name": "Midgaard West Gate",
                "desc": "The western fortified gate overlooks green agricultural pastures and grazing dairy cattle.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "barracks_gate", "alias": "e"}, "west": {"dest_id": "western_plains", "alias": "w"}}
            },
            "western_plains": {
                "name": "Rolling Plains of Midgaard",
                "desc": "Gentle emerald hills sway with tall wild barley and clover. In the distance, windmills turn lazily against the horizon.",
                "terrain": "field",
                "exits": {"east": {"dest_id": "west_gate", "alias": "e"}, "south": {"dest_id": "shepherd_camp", "alias": "s"}},
                "npcs": [{"name": "Wild Hare", "desc": "A quick brown bunny hopping through the tall grass.", "level": 1, "role": "civilian"}]
            },
            "shepherd_camp": {
                "name": "Shepherd's Meadow Cottage",
                "desc": "A cozy stone cottage thatched with dried rye. A flock of woolly sheep graze peacefully inside a split-rail cedar pen.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "western_plains", "alias": "n"}}
            },
            "east_rampart": {
                "name": "The Eastern Battlements",
                "desc": "The crenellated stone walkway high above the city offers a panoramic vista of the sparkling sea and the harbor piers.",
                "terrain": "city",
                "exits": {"down": {"dest_id": "port_promenade", "alias": "d"}}
            },
            "west_rampart": {
                "name": "The Western Battlements",
                "desc": "A windy parapet overlooking the green farmlands. Catapults and ballistas are bolted to the granite floor.",
                "terrain": "city",
                "exits": {"down": {"dest_id": "barracks_gate", "alias": "d"}}
            }
        }
    }


def build_zone_2_goblin_mountain():
    """Zone 12: The Ironcrag Goblin Mountain & Mines (tbaMUD) [Level 6-11] - 30 Rooms"""
    return {
        "zone_key": "goblin_stronghold",
        "zone_name": "Ironcrag Goblin Mountain & Mines",
        "default_terrain": "mountain",
        "base_coords": (15, 20, 0),
        "rooms": {
            "ridge_trail": {
                "name": "Ironcrag Ridge Mountain Trail",
                "desc": "A narrow scree trail snakes along the razor-sharp granite ridge of the Ironcrags. Howling alpine winds toss gravel across the precipice.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "sentry_post", "alias": "n"}},
                "npcs": [{"name": "Goblin Mountain Scout", "desc": "A wiry greenskin wielding a notched hunting bow.", "level": 6, "role": "rogue"}]
            },
            "sentry_post": {
                "name": "Goblin Sentry Barricade",
                "desc": "A crude breastwork of sharpened pine logs, bone totems, and boulders chokes the mountain pass. A smoldering campfire emits pungent sulfur smoke.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "ridge_trail", "alias": "s"}, "north": {"dest_id": "mine_entrance", "alias": "n"}, "east": {"dest_id": "scout_nest", "alias": "e"}},
                "npcs": [{"name": "Goblin Barricade Guard", "desc": "A snarling sentry armed with an iron-shod spear.", "level": 7, "role": "warrior"}]
            },
            "scout_nest": {
                "name": "Cliffside Lookout Nest",
                "desc": "A perilous wooden platform lashed to the sheer cliff face with thick hemp rope. A bronze gong hangs ready to sound the alarm.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "sentry_post", "alias": "w"}}
            },
            "mine_entrance": {
                "name": "Mouth of the Ironcrag Mines",
                "desc": "A jagged yawning opening in the mountain rock. Rotted timber beams support the cracked ceiling, and rusty iron cart rails disappear into the gloom.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "sentry_post", "alias": "s"}, "north": {"dest_id": "mine_shaft_1", "alias": "n"}, "down": {"dest_id": "lower_shaft", "alias": "d"}},
                "items": [{"name": "Discarded Iron Mining Pick", "desc": "A heavy two-handed miner's pick with a chipped steel beak."}]
            },
            "mine_shaft_1": {
                "name": "Upper Cart Tunnel",
                "desc": "Sputtering torches in iron sconces cast dancing shadows across jagged rock walls. Veins of reddish iron ore glitter under the torchlight.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "mine_entrance", "alias": "s"}, "north": {"dest_id": "smelter_chamber", "alias": "n"}, "east": {"dest_id": "ore_crusher", "alias": "e"}},
                "npcs": [{"name": "Enslaved Kobold Miner", "desc": "A scaly, gaunt kobold hauling heavy iron ore in a wicker basket.", "level": 6, "role": "civilian"}]
            },
            "ore_crusher": {
                "name": "The Waterwheel Ore Crusher",
                "desc": "Subterranean stream water powers a massive iron trip-hammer that relentlessly pulverizes rock chunks into dust.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "mine_shaft_1", "alias": "w"}}
            },
            "smelter_chamber": {
                "name": "The Great Goblin Smelting Basin",
                "desc": "A crude blast furnace belches black ash and intense heat into the chamber. Molten iron trickles down stone troughs into crude bar molds.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "mine_shaft_1", "alias": "s"}, "north": {"dest_id": "warren_gate", "alias": "n"}, "east": {"dest_id": "goblin_armory", "alias": "e"}},
                "npcs": [{"name": "Hobgoblin Smelter Master", "desc": "A heavily scarred brute wielding long iron tongs.", "level": 8, "role": "warrior"}]
            },
            "goblin_armory": {
                "name": "Crude Goblin Armory",
                "desc": "Spiked iron clubs, jagged cleavers, and rusted chain shirts hang from bone hooks along the damp limestone walls.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "smelter_chamber", "alias": "w"}},
                "items": [{"name": "Spiked Goblin Morningstar", "desc": "A menacing iron ball studded with crude spikes."}]
            },
            "warren_gate": {
                "name": "Gate of the Ironfang Warrens",
                "desc": "A heavy portcullis made from stolen wagon axletrees blocks the passage into the living quarters of the clan.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "smelter_chamber", "alias": "s"}, "north": {"dest_id": "communal_cavern", "alias": "n"}}
            },
            "communal_cavern": {
                "name": "The Communal Warrens",
                "desc": "Scores of straw nests, gnawed bones, and crude mud ovens fill this sprawling cavern. The din of screeching goblin young and barking wolf-hounds echoes constantly.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "warren_gate", "alias": "s"}, "north": {"dest_id": "chieftain_hall", "alias": "n"}, "east": {"dest_id": "shaman_hollow", "alias": "e"}, "west": {"dest_id": "kennels", "alias": "w"}},
                "npcs": [{"name": "Goblin Scavenger", "desc": "A ragged goblin picking meat scraps from a wolf bone.", "level": 7, "role": "rogue"}]
            },
            "kennels": {
                "name": "The Warg Kennels",
                "desc": "Stout iron cages hold snarling, red-eyed wargs with shaggy grey pelts and bloodstained jaws.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "communal_cavern", "alias": "e"}},
                "npcs": [{"name": "Fierce Mountain Warg", "desc": "A ferocious oversized lupine predator foaming at the mouth.", "level": 8, "role": "warrior"}]
            },
            "shaman_hollow": {
                "name": "Hollow of the Bone Shaman",
                "desc": "Braziers burn with dried swamp herbs and ground sulfur. A gigantic cave bear skull serves as an altar for bloody ritual sacrifices.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "communal_cavern", "alias": "w"}},
                "npcs": [{"name": "Goblin Witch-Doctor Skazz", "desc": "A withered shaman draped in serpent skins holding a skull wand.", "level": 10, "role": "mage"}],
                "items": [{"name": "Skull Wand of Pyros", "desc": "A blackened bone focus crackling with latent evocation heat."}]
            },
            "chieftain_hall": {
                "name": "Great Hall of Chieftain Gornak",
                "desc": "Piles of stolen tapestries and dwarven shield trophies carpet the floor. At the far end rises a throne cobbled from iron ingots, dire wolf fangs, and human skulls.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "communal_cavern", "alias": "s"}, "north": {"dest_id": "treasure_vault", "alias": "n"}, "down": {"dest_id": "chasm_ledge", "alias": "d"}},
                "npcs": [{"name": "Chieftain Gornak Ironfang", "desc": "A hulking, armor-clad goblin warlord wielding a massive serrated cleaver.", "level": 12, "role": "boss", "danger_tier": "boss"}]
            },
            "treasure_vault": {
                "name": "The Ironfang Plunder Vault",
                "desc": "Iron-banded strongboxes pry open to reveal stolen trade goods, sacks of silver coins, and dwarven mining maps.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "chieftain_hall", "alias": "s"}},
                "items": [{"name": "Ironfang Clan War Banner", "desc": "A bloodstained banner emblazoned with a snarling red wolf head."}]
            },
            "lower_shaft": {
                "name": "Flooded Lower Cart Tunnel",
                "desc": "Cold, rust-colored mine runoff pools ankle-deep along the shattered floorboards. Timber roof beams creak ominously under crushing mountain weight.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "mine_entrance", "alias": "u"}, "north": {"dest_id": "chasm_ledge", "alias": "n"}}
            },
            "chasm_ledge": {
                "name": "Ledge Over the Howling Abyss",
                "desc": "The mine breaks through into a staggering subterranean abyss. Far below, a subterranean river roars through the blackness.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "lower_shaft", "alias": "s"}, "up": {"dest_id": "chieftain_hall", "alias": "u"}, "north": {"dest_id": "rope_bridge", "alias": "n"}}
            },
            "rope_bridge": {
                "name": "The Swaying Rope Bridge",
                "desc": "A treacherous bridge of frayed ropes and weathered pine planks spans the yawning void. The bridge swings wildly with every gust of thermal air.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "chasm_ledge", "alias": "s"}, "north": {"dest_id": "fungus_cavern", "alias": "n"}}
            },
            "fungus_cavern": {
                "name": "Bioluminescent Fungus Grotto",
                "desc": "Gigantic toadstools the size of trees grow in dense clusters across the damp floor, emitting an eerie violet and turquoise glow.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "rope_bridge", "alias": "s"}, "east": {"dest_id": "spore_hollow", "alias": "e"}},
                "npcs": [{"name": "Cavern Lurker", "desc": "A multi-legged pale troglodyte that stalks in total silence.", "level": 9, "role": "warrior"}]
            },
            "spore_hollow": {
                "name": "Puffball Spore Hollow",
                "desc": "Thick fungal spore clouds drift lazily through the humid cavern air, tickling the throat and stinging the eyes.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "fungus_cavern", "alias": "w"}},
                "items": [{"name": "Luminous Violet Cap", "desc": "A phosphorescent mushroom cap that glows brightly in the dark."}]
            },
            "deep_well": {
                "name": "The Deep Mineral Sump",
                "desc": "Mineral-rich spring water gushes from a fissure in the rock wall, cascading down a natural limestone amphitheater.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "fungus_cavern", "alias": "s"}}
            },
            "high_perch": {
                "name": "The Eagles' Crag",
                "desc": "High above the tree line, this open-air cliffside perch looks out over the entirety of the western continent.",
                "terrain": "mountain",
                "exits": {"down": {"dest_id": "ridge_trail", "alias": "d"}}
            },
            "abandoned_bivouac": {
                "name": "Abandoned Dwarven Bivouac",
                "desc": "Stone masonry benches and cold hearthstones bear testament to the ancient dwarven prospectors who first carved these mines.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "mine_shaft_1", "alias": "w"}}
            },
            "collapsed_gallery": {
                "name": "Collapsed Quartz Gallery",
                "desc": "Shattered crystals of rose quartz glitter among fallen granite boulders that have permanently sealed the eastern tunnel.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "lower_shaft", "alias": "w"}}
            },
            "bat_roost": {
                "name": "The Howling Bat Roost",
                "desc": "Thousands of leathery bats hang tightly packed from stalactites overhead, chattering in high-pitched clicks.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "scout_nest", "alias": "s"}}
            },
            "sulfur_vent": {
                "name": "Geothermal Sulfur Vent",
                "desc": "Yellow crystalline sulfur crusts around steam vents hissing with scalding geothermal vapor.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "high_perch", "alias": "n"}}
            },
            "wolf_den": {
                "name": "Wild Wolf Den",
                "desc": "A hollow cleft under overhanging boulders littered with the dried carcasses of mountain goats.",
                "terrain": "mountain",
                "exits": {"east": {"dest_id": "ridge_trail", "alias": "e"}}
            },
            "powder_store": {
                "name": "Stolen Blasting Powder Store",
                "desc": "Casks of volatile black mining powder stamped with dwarven runes are stacked carefully away from sparks.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "goblin_armory", "alias": "e"}}
            },
            "slave_pens": {
                "name": "The Iron Slave Pens",
                "desc": "Cramped cells with rusty iron grates where goblin raiders hold captive travelers from merchant caravans.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "communal_cavern", "alias": "w"}}
            },
            "trophy_ledge": {
                "name": "The Skull Trophy Ledge",
                "desc": "Bleached horns of mountain wyverns and antlers of great stags are mounted proudly along the granite wall.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "chieftain_hall", "alias": "e"}}
            },
            "submerged_drain": {
                "name": "Submerged Flood Drain",
                "desc": "Dark water swirls rapidly down a natural sinkhole in the cavern floor.",
                "terrain": "underwater",
                "exits": {"up": {"dest_id": "deep_well", "alias": "u"}}
            }
        }
    }


def build_zone_3_praxis_province():
    """Zone 10: The Province & Catacombs of Old Praxis (Nightmare IV) [Level 9-15] - 35 Rooms"""
    return {
        "zone_key": "praxis_province",
        "zone_name": "The Province & Catacombs of Old Praxis",
        "default_terrain": "city",
        "base_coords": (-25, 0, 0),
        "rooms": {
            "praxis_harbor": {
                "name": "Old Praxis Imperial Pier",
                "desc": "The historic deep-water harbor of Praxis. Centuries-old granite docks extend into the deep sapphire waters. Ancient stone lighthouses guard the harbor mouth against reef hazards.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "praxis_boardwalk", "alias": "n"}, "east": {"dest_id": "customs_pier", "alias": "e"}},
                "npcs": [{"name": "Imperial Harbor Master", "desc": "A proud veteran officer of the old Praxis naval fleet.", "level": 10, "role": "warrior"}]
            },
            "customs_pier": {
                "name": "Praxis Customs & Tariff Office",
                "desc": "Scales, registry ledgers, and locked storage cages fill this imperial customs house where tariffs were collected on spices and silk.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "praxis_harbor", "alias": "w"}},
                "items": [{"name": "Praxis Ledger of Tariffs", "desc": "A heavy parchment book documenting old maritime trade routes."}]
            },
            "praxis_boardwalk": {
                "name": "Praxis Harbor Promenade",
                "desc": "A timber boardwalk lined with nautical tavernas, fishmongers, and repair slipways overlooking the rocking masted caravels.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "praxis_harbor", "alias": "s"}, "north": {"dest_id": "town_square", "alias": "n"}, "west": {"dest_id": "mermaid_tavern", "alias": "w"}, "east": {"dest_id": "praxis_east_gate", "alias": "e"}},
                "npcs": [{"name": "Salty Privateer", "desc": "A rugged corsair with gold hoop earrings and a curved cutlass.", "level": 10, "role": "rogue"}]
            },
            "mermaid_tavern": {
                "name": "The Drowned Mermaid Tavern",
                "desc": "Smells of spiced grog, fried herring, and pipe tobacco fill this bustling sea tavern. A carved mermaid figurehead with emerald glass eyes graces the wall.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "praxis_boardwalk", "alias": "e"}},
                "items": [{"name": "Tankard of Spiced Navy Grog", "desc": "A steaming clay mug of dark rum and cinnamon."}]
            },
            "praxis_east_gate": {
                "name": "Praxis East Coastal Gate",
                "desc": "A battered stone archway leading out toward the crags and smuggler coves of the eastern coastline.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "praxis_boardwalk", "alias": "w"}}
            },
            "town_square": {
                "name": "Praxis Monument Square",
                "desc": "The cultural heart of Praxis. In the center rises an imposing bronze monument honoring the legendary mages and warriors of Nightmare IV history.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "praxis_boardwalk", "alias": "s"}, "north": {"dest_id": "praxis_high_road", "alias": "n"}, "east": {"dest_id": "clocktower_hall", "alias": "e"}, "west": {"dest_id": "sewer_grate", "alias": "w"}},
                "items": [{"name": "Nightmare Memorial Plaque", "desc": "Engraved in bronze: 'Honor to the seekers of knowledge and masters of magic.'"}]
            },
            "clocktower_hall": {
                "name": "The Great Praxis Clocktower",
                "desc": "Gigantic brass cogs, pendulum weights, and chiming bells tick in harmonic synchronization high inside the limestone tower.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "town_square", "alias": "w"}}
            },
            "praxis_high_road": {
                "name": "Praxis High Avenue",
                "desc": "Grand villas and stone academies border this wide avenue paved with grey basalt flags.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "town_square", "alias": "s"}, "north": {"dest_id": "academics_hall", "alias": "n"}, "west": {"dest_id": "crypt_portal", "alias": "w"}}
            },
            "academics_hall": {
                "name": "Hall of Ancient Scribing & Studies",
                "desc": "Rows of polished oak desks equipped with inkwells, vellum, and sand pots. Scholars study ancient dialects of Common and Elven.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "praxis_high_road", "alias": "s"}},
                "items": [{"name": "Praxis Academic Vellum", "desc": "Fine calfskin vellum suitable for scribing arcane runes."}]
            },
            # Catacombs Under Praxis
            "crypt_portal": {
                "name": "Descent to the Praxis Catacombs",
                "desc": "A broad stairway of cracked green marble descends steeply beneath the city into dark, moisture-chilled subterranean corridors.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "praxis_high_road", "alias": "e"}, "down": {"dest_id": "catacomb_gallery", "alias": "d"}}
            },
            "catacomb_gallery": {
                "name": "The Gallery of Weeping Tombs",
                "desc": "Thousands of carved niches hold the sarcophagi of Praxis nobility. Cold groundwater drips continuously from the arched ceiling.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "crypt_portal", "alias": "u"}, "north": {"dest_id": "ossuary_vault", "alias": "n"}, "south": {"dest_id": "sunken_sanctum", "alias": "s"}},
                "npcs": [{"name": "Barnacled Skeleton", "desc": "The animated remains of an old sea warrior encrusted with sea shells.", "level": 10, "role": "warrior"}]
            },
            "ossuary_vault": {
                "name": "The Great Bone Ossuary",
                "desc": "Geometric patterns of bleached skulls and thigh bones decorate the walls in solemn mortuary architecture.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "catacomb_gallery", "alias": "s"}, "east": {"dest_id": "crypt_king", "alias": "e"}},
                "npcs": [{"name": "Crypt Wight", "desc": "A malevolent shadow-shrouded undead entity with glowing eyes.", "level": 12, "role": "warrior"}]
            },
            "crypt_king": {
                "name": "Sepulcher of the Corsair King",
                "desc": "A massive sarcophagus of obsidian rests atop a raised dais. Carvings depict naval battles fought with sorcery and dragons.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "ossuary_vault", "alias": "w"}, "down": {"dest_id": "sunken_grotto", "alias": "d"}},
                "npcs": [{"name": "Ghostly Corsair King", "desc": "A regal translucent phantom wielding a spectral saber.", "level": 15, "role": "boss", "danger_tier": "boss"}]
            },
            "sunken_sanctum": {
                "name": "Flooded Altar to the Deep",
                "desc": "Knee-deep seawater covers the floor of this ancient temple. An altar carved with tentacles and waves stands submerged in the brine.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "catacomb_gallery", "alias": "n"}},
                "items": [{"name": "Black Pearl of Praxis", "desc": "A luminous, thumb-sized pearl radiating cool arcane energy."}]
            },
            "sunken_grotto": {
                "name": "Bioluminescent Sea Grotto",
                "desc": "The catacombs open directly into a sea cave where ocean waves crash against phosphorescent coral beds.",
                "terrain": "water_swim",
                "exits": {"up": {"dest_id": "crypt_king", "alias": "u"}, "south": {"dest_id": "submerged_tunnel", "alias": "s"}}
            },
            "submerged_tunnel": {
                "name": "Submerged Escape Channel",
                "desc": "A completely flooded tunnel leading through the coastal reef.",
                "terrain": "underwater",
                "exits": {"north": {"dest_id": "sunken_grotto", "alias": "n"}}
            },
            # Sewers of Praxis
            "sewer_grate": {
                "name": "Iron Sewer Hatch",
                "desc": "A heavy iron ring hatch set into the street cobbles opens into the ancient municipal drainage network of Praxis.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "town_square", "alias": "e"}, "down": {"dest_id": "sewer_main", "alias": "d"}}
            },
            "sewer_main": {
                "name": "Praxis Main Sewer Canal",
                "desc": "Brackish runoff flows down a central stone culvert. Rusted iron catwalks flank the sludge channel.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "sewer_grate", "alias": "u"}, "north": {"dest_id": "sludge_hub", "alias": "n"}, "south": {"dest_id": "rat_den", "alias": "s"}},
                "npcs": [{"name": "Sewer Skulker", "desc": "A greasy-haired cutthroat hiding in the sewer gloom.", "level": 9, "role": "rogue"}]
            },
            "rat_den": {
                "name": "The Murine Lair",
                "desc": "Piles of rotting rags, bones, and discarded shoes form massive nests where oversized sewer rats breed.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "sewer_main", "alias": "n"}},
                "npcs": [{"name": "Dire Sewer Rat", "desc": "A ravenous rodent the size of a hunting dog with yellowed incisors.", "level": 9, "role": "warrior"}]
            },
            "sludge_hub": {
                "name": "Central Sluice Hub",
                "desc": "Giant cast-iron valve wheels control the flow of floodwaters from the city above into the outer sea.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "sewer_main", "alias": "s"}, "east": {"dest_id": "smuggler_passage", "alias": "e"}}
            },
            "smuggler_passage": {
                "name": "Hidden Smuggler Siphon",
                "desc": "A concealed brick door leads into a dry, torch-lit tunnel used to bypass the harbor customs gates.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "sludge_hub", "alias": "w"}, "up": {"dest_id": "praxis_boardwalk", "alias": "u"}}
            },
            "lighthouse_base": {
                "name": "Base of the Kraken Beacon",
                "desc": "A circular stone chamber at the foot of the sea lighthouse. Coils of cable and casks of whale oil stand ready.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "praxis_harbor", "alias": "w"}, "up": {"dest_id": "lighthouse_lantern", "alias": "u"}}
            },
            "lighthouse_lantern": {
                "name": "Kraken Beacon Lamp Room",
                "desc": "A gigantic polished silver reflector and oil burner rotate under a brass clockwork mechanism, throwing beams across the ocean.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "lighthouse_base", "alias": "d"}}
            },
            "chandler_wharf": {
                "name": "Old Sailmakers' Slip",
                "desc": "Long timber trestles where canvas sails are measured, cut, and stitched with beeswaxed twine.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "praxis_boardwalk", "alias": "n"}}
            },
            "fish_dock": {
                "name": "The Herring Docks",
                "desc": "Wooden drying racks stretch for yards, curing thousands of split silver herring in the sea breeze.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "praxis_harbor", "alias": "e"}}
            },
            "monastery_steps": {
                "name": "Steps to the Sunken Monastery",
                "desc": "Weathered marble steps overgrown with ivy ascending the coastal bluffs toward the ruined abbey.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "town_square", "alias": "s"}, "up": {"dest_id": "abbey_cloister", "alias": "u"}}
            },
            "abbey_cloister": {
                "name": "Cloister of the Coastal Abbey",
                "desc": "A silent stone courtyard where monks of the tides once walked in contemplation beneath ancient cypress trees.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "monastery_steps", "alias": "d"}, "east": {"dest_id": "abbey_chapel", "alias": "e"}}
            },
            "abbey_chapel": {
                "name": "The High Tide Chapel",
                "desc": "Open Gothic arches look out over the stormy ocean. An altar of polished basalt holds unlit beeswax tapers.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "abbey_cloister", "alias": "w"}}
            },
            "outer_bluffs": {
                "name": "Praxis Coastal Bluffs",
                "desc": "Windblown cliffs plunging sheer into the churning ocean breakers far below.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "abbey_cloister", "alias": "s"}}
            },
            "sea_cavern_crypt": {
                "name": "The Drowned Tomb Alcove",
                "desc": "A half-submerged recess where an ancient sarcophagus rests draped in sea kelp.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "sunken_sanctum", "alias": "n"}}
            },
            "coastal_road": {
                "name": "Praxis North Coastal Road",
                "desc": "A scenic gravel carriage road winding along the clifftops.",
                "terrain": "field",
                "exits": {"south": {"dest_id": "praxis_high_road", "alias": "s"}}
            },
            "old_foundry": {
                "name": "Old Naval Cannon Foundry",
                "desc": "Disused brick furnaces where naval brass cannons and round iron shot were cast.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "praxis_boardwalk", "alias": "e"}}
            },
            "damp_cellar": {
                "name": "Flooded Cellar Storage",
                "desc": "Stagnant rainwater fills this old tavern cellar, floating empty wine casks against the rafters.",
                "terrain": "water_swim",
                "exits": {"up": {"dest_id": "mermaid_tavern", "alias": "u"}}
            },
            "quarantine_dock": {
                "name": "The Quarantine Anchorage",
                "desc": "An isolated wooden pier where ships carrying yellow flags were quarantined during past plagues.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "customs_pier", "alias": "w"}}
            },
            "sewer_overflow": {
                "name": "Sewer Sea Overflow",
                "desc": "An iron-barred drain where the city runoff dumps directly into the surging ocean tide.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "sludge_hub", "alias": "n"}}
            }
        }
    }


def build_zone_4_shadowfen():
    """Zone 13: The Shadowfen Necropolis & Mausoleum (CircleMUD) [Level 13-18] - 28 Rooms"""
    return {
        "zone_key": "shadowfen_necropolis",
        "zone_name": "The Shadowfen Necropolis & Mausoleum",
        "default_terrain": "marsh",
        "base_coords": (0, -25, 0),
        "rooms": {
            "misty_moor": {
                "name": "Shadowfen Misty Moor",
                "desc": "A desolate expanse of stagnant peat bogs and twisting black willows. Thick grey fog hovers inches above the black mud, muffling all sound except the mournful croak of ravens.",
                "terrain": "marsh",
                "exits": {"north": {"dest_id": "drowned_causeway", "alias": "n"}},
                "npcs": [{"name": "Bog Willow Bogey", "desc": "A twisted plant-demon with thorn-tipped claws and glowing yellow eyes.", "level": 13, "role": "warrior"}]
            },
            "drowned_causeway": {
                "name": "The Drowned Causeway",
                "desc": "Slippery, moss-covered flagstones rise barely an inch above the murky marsh water. Rotten wooden stakes flank the path, adorned with crow feathers.",
                "terrain": "marsh",
                "exits": {"south": {"dest_id": "misty_moor", "alias": "s"}, "north": {"dest_id": "graveyard_gate", "alias": "n"}, "west": {"dest_id": "witch_hovel", "alias": "w"}}
            },
            "witch_hovel": {
                "name": "The Bog Witch's Sunken Hovel",
                "desc": "A tilted shack supported by rotting stilts over the peat. Strands of dried herbs, toad skins, and blackened candles hang from the low eaves.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "drowned_causeway", "alias": "e"}},
                "npcs": [{"name": "Mire Witch Baba Yorg", "desc": "A hunchbacked crone with long obsidian fingernails stirring a cauldron.", "level": 14, "role": "mage"}],
                "items": [{"name": "Jar of Shadowfen Leeches", "desc": "Squirming black marsh leeches known for extracting poisons."}]
            },
            "graveyard_gate": {
                "name": "Iron Gate of the Necropolis",
                "desc": "Towering wrought-iron gates forged in the likeness of skeletal hands bar the entrance to the ancient graveyard. Cold iron spikes glisten with icy dew.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "drowned_causeway", "alias": "s"}, "north": {"dest_id": "cemetery_path", "alias": "n"}},
                "npcs": [{"name": "Necropolis Gate Guardian", "desc": "A heavy bone golem wrapped in rusted chains.", "level": 14, "role": "warrior"}]
            },
            "cemetery_path": {
                "name": "Avenue of Weeping Angels",
                "desc": "Flanked by mossy marble statues of sorrowful winged figures covering their faces, this path cuts through acres of tilted headstones and collapsed tombs.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "graveyard_gate", "alias": "s"}, "north": {"dest_id": "mausoleum_foyer", "alias": "n"}, "east": {"dest_id": "plague_pit", "alias": "e"}, "west": {"dest_id": "weeping_monument", "alias": "w"}},
                "npcs": [{"name": "Restless Barrow Wight", "desc": "A withered warrior corpse clutching an ancient rusted arming sword.", "level": 15, "role": "warrior"}]
            },
            "plague_pit": {
                "name": "The Unhallowed Plague Pit",
                "desc": "A mass sunken trench marked only by a crude wooden marker. The earth here refuses to grow grass, remaining charred and lifeless.",
                "terrain": "marsh",
                "exits": {"west": {"dest_id": "cemetery_path", "alias": "w"}},
                "npcs": [{"name": "Ravenous Bog Ghoul", "desc": "A hunched, hairless carnivore gnawing on ancient bones.", "level": 14, "role": "warrior"}]
            },
            "weeping_monument": {
                "name": "Monument of the Fallen Order",
                "desc": "An obelisk of weeping black marble engraved with the names of a forgotten knighthood slaughtered centuries ago.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "cemetery_path", "alias": "e"}}
            },
            "mausoleum_foyer": {
                "name": "Mausoleum of the Black Sun",
                "desc": "A monolithic structure of polished black obsidian. Cold air smelling of embalming fluid and ancient myrrh radiates from within.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "cemetery_path", "alias": "s"}, "north": {"dest_id": "hall_of_urns", "alias": "n"}, "east": {"dest_id": "embalming_room", "alias": "e"}},
                "npcs": [{"name": "Cultist of the Black Sun", "desc": "A hooded dark sorcerer chanting foul necromantic incantations.", "level": 16, "role": "mage"}]
            },
            "embalming_room": {
                "name": "Ancient Embalming Chamber",
                "desc": "Stone dissection slabs with drainage channels sit surrounded by jars of natron salts, linen bandages, and copper canopic vessels.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "mausoleum_foyer", "alias": "w"}},
                "items": [{"name": "Copper Canopic Vessel", "desc": "An ancient sealed urn engraved with hieroglyphs of death."}]
            },
            "hall_of_urns": {
                "name": "The Gallery of Eternal Silence",
                "desc": "Thousands of ash urns sit in niches stacked from the floor to the vaulted ceiling. Ghostly whispers flutter at the edge of hearing.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "mausoleum_foyer", "alias": "s"}, "north": {"dest_id": "lich_sanctum", "alias": "n"}, "down": {"dest_id": "deep_catacombs", "alias": "d"}},
                "npcs": [{"name": "Dread Wraith", "desc": "A shadowy wraith that drains the warmth and life from the living.", "level": 17, "role": "rogue"}]
            },
            "lich_sanctum": {
                "name": "Inner Sanctum of Arch-Lich Malakor",
                "desc": "In the heart of the obsidian mausoleum floats a throne of jagged bone suspended above a swirling vortex of necrotic souls.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "hall_of_urns", "alias": "s"}, "east": {"dest_id": "relic_vault", "alias": "e"}},
                "npcs": [{"name": "Arch-Lich Malakor", "desc": "An undying sorcerer in tattered burial robes whose eyes burn with violet necrotic fire.", "level": 19, "role": "boss", "danger_tier": "boss"}]
            },
            "relic_vault": {
                "name": "Vault of the Cursed Regalia",
                "desc": "Cursed crowns, blackened scepters, and grimoires bound in human hide sit within warded crystal cabinets.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "lich_sanctum", "alias": "w"}},
                "items": [{"name": "Phylactery Relic of the Lich", "desc": "A pulsating jeweled locket containing dark immortal essence."}]
            },
            "deep_catacombs": {
                "name": "The Lower Crypt Sump",
                "desc": "Stagnant black swamp water seeps through cracked stone sarcophagi on the bottom level of the mausoleum.",
                "terrain": "water_swim",
                "exits": {"up": {"dest_id": "hall_of_urns", "alias": "u"}}
            },
            "mourning_chapel": {
                "name": "The Desecrated Chapel",
                "desc": "Shattered pews and broken stone crosses lie beneath a collapsed roof where black rain drips steadily.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "graveyard_gate", "alias": "e"}}
            },
            "bell_tower_ruin": {
                "name": "The Silent Campanile",
                "desc": "The bell tower's massive bronze bell lies cracked in two upon the flagstones below.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "mourning_chapel", "alias": "n"}}
            },
            "crypt_knights": {
                "name": "Crypt of the Black Knights",
                "desc": "Twelve stone coffins flanked by rusted iron halberds and cracked heater shields.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "weeping_monument", "alias": "s"}}
            },
            "black_willow_grove": {
                "name": "Heart of the Black Willows",
                "desc": "Gargantuan willows with weeping moss-draped branches that seem to grasp at passing travelers.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "misty_moor", "alias": "e"}}
            },
            "bog_iron_pit": {
                "name": "Bog Iron Seep",
                "desc": "A bubbling puddle of rust-colored sludge where bog iron naturally precipitates from the peat.",
                "terrain": "marsh",
                "exits": {"south": {"dest_id": "black_willow_grove", "alias": "s"}}
            },
            "ossuary_annex": {
                "name": "Ossuary Northern Annex",
                "desc": "Stack after stack of skulls staring with empty eye sockets toward the northern vault.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "hall_of_urns", "alias": "w"}}
            },
            "open_grave": {
                "name": "The Freshly Dug Grave",
                "desc": "A six-foot rectangular pit in the wet earth, a discarded shovel stuck in the dirt heap beside it.",
                "terrain": "marsh",
                "exits": {"south": {"dest_id": "plague_pit", "alias": "s"}}
            },
            "sunken_columbarium": {
                "name": "Sunken Columbarium",
                "desc": "Circular walls holding thousands of terracotta crematorium urns behind rusty iron lattices.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "cemetery_path", "alias": "u"}}
            },
            "rotting_trestle": {
                "name": "Rotting Peat Trestle",
                "desc": "Flimsy pine planks laid over black bottomless quick-mire.",
                "terrain": "marsh",
                "exits": {"north": {"dest_id": "witch_hovel", "alias": "n"}}
            },
            "shrine_death": {
                "name": "Altar of the Dark Mother",
                "desc": "An ancient monolith stained with dried blood offerings honoring the goddess of the grave.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "mausoleum_foyer", "alias": "w"}}
            },
            "shadow_crypt_1": {
                "name": "Vault of the First High Priest",
                "desc": "A gilded sarcophagus surrounded by decaying silk vestments.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "shrine_death", "alias": "e"}}
            },
            "drainage_culvert": {
                "name": "Mausoleum Drainage Culvert",
                "desc": "A narrow stone pipe where cold swamp water discharges out of the lower tombs.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "deep_catacombs", "alias": "n"}}
            },
            "foggy_promontory": {
                "name": "Foggy Marsh Promontory",
                "desc": "A low mound of solid gravel rising above the sea of peat, crowned with twisted gorse bushes.",
                "terrain": "marsh",
                "exits": {"west": {"dest_id": "drowned_causeway", "alias": "w"}}
            },
            "bone_charnel": {
                "name": "The Outer Charnel Yard",
                "desc": "Piles of unburied bones picked clean by ravens and carrion beetles.",
                "terrain": "marsh",
                "exits": {"east": {"dest_id": "cemetery_path", "alias": "e"}}
            },
            "catacomb_drain": {
                "name": "Flooded Sump Drain",
                "desc": "Dark water pooling beneath cracked marble tiles.",
                "terrain": "underwater",
                "exits": {"up": {"dest_id": "drainage_culvert", "alias": "u"}}
            }
        }
    }


def build_zone_5_astral():
    """Zone 14: The Astral Rifts & Elemental Spires (High-End / DCSS) [Level 18-25+] - 22 Rooms"""
    return {
        "zone_key": "astral_rifts",
        "zone_name": "The Astral Rifts & Elemental Spires",
        "default_terrain": "air",
        "base_coords": (0, 0, 30),
        "rooms": {
            "astral_nexus": {
                "name": "The Astral Nexus Platform",
                "desc": "A floating platform of translucent starlight levitating in an infinite void of swirling nebulae and distant cosmic auroras. Gravity here feels light and buoyant.",
                "terrain": "air",
                "exits": {"north": {"dest_id": "void_bridge", "alias": "n"}, "east": {"dest_id": "plane_fire_portal", "alias": "e"}, "west": {"dest_id": "plane_water_portal", "alias": "w"}},
                "npcs": [{"name": "Astral Void Wanderer", "desc": "A translucent being made of crystallized stardust and telepathic thought.", "level": 18, "role": "mage"}]
            },
            "void_bridge": {
                "name": "The Bridge of Pure Starlight",
                "desc": "A shimmering bridge of coherent light spanning across cosmic rifts where fragments of shattered planets drift in zero gravity.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "astral_nexus", "alias": "s"}, "north": {"dest_id": "celestial_pinnacle", "alias": "n"}},
                "npcs": [{"name": "Void Horror", "desc": "A multi-eyed aberration with undulating tentacles that hunger for raw magic.", "level": 20, "role": "warrior"}]
            },
            "celestial_pinnacle": {
                "name": "The Celestial Spire Pinnacle",
                "desc": "A soaring spire of white astral marble crowned by a throne of solidified solar flare energy. Constellations spin rapidly across the overhead firmament.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "void_bridge", "alias": "s"}, "up": {"dest_id": "vault_stars", "alias": "u"}},
                "npcs": [{"name": "Guardian Archon of Dawn", "desc": "A six-winged celestial warrior clad in golden armor and wielding a greatsword of pure sunlight.", "level": 23, "role": "boss", "danger_tier": "boss"}]
            },
            "vault_stars": {
                "name": "The Vault of the Sovereigns",
                "desc": "The highest apex of the astral plane. In the center floats a cosmic orb radiating the primal laws of reality.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "celestial_pinnacle", "alias": "d"}},
                "npcs": [{"name": "The Astral Overseer", "desc": "An ancient titan composed of dark matter and superheated plasma.", "level": 26, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Star-Forged Crown of Sovereignty", "desc": "A legendary relic crowned with miniature orbiting stars that pulses with immense arcane power."}]
            },
            # Plane of Fire
            "plane_fire_portal": {
                "name": "Threshold to the Plane of Pyros",
                "desc": "The air shimmers with unbearable heat as you step through a rift into a volcanic landscape where rivers of orange magma flow across black obsidian plains.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "astral_nexus", "alias": "w"}, "east": {"dest_id": "magma_caldera", "alias": "e"}},
                "items": [{"name": "Molten Obsidian Shard", "desc": "A piece of glass that burns with eternal, inextinguishable flame."}]
            },
            "magma_caldera": {
                "name": "The Great Magma Caldera",
                "desc": "Fountains of liquid fire erupt from a boiling lake of magma. Ash storms blanket the blackened sky in crimson haze.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "plane_fire_portal", "alias": "w"}, "north": {"dest_id": "fire_temple", "alias": "n"}},
                "npcs": [{"name": "Greater Fire Elemental", "desc": "A roaring vortex of living elemental flame and volcanic brimstone.", "level": 20, "role": "warrior"}]
            },
            "fire_temple": {
                "name": "Temple of the Eternal Flame",
                "desc": "Pillars of solid ruby support a domed ceiling carved from black diamond. In the center burns the Primal Spark.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "magma_caldera", "alias": "s"}},
                "items": [{"name": "Flaming Greatsword of Pyros", "desc": "A heavy blade that bursts into searing flame upon being drawn."}]
            },
            # Plane of Water
            "plane_water_portal": {
                "name": "Threshold to the Plane of Aquas",
                "desc": "You step through a shimmering watery veil into an endless sea with no sky and no seafloor. Huge bubbles of breathable air drift through the blue depths.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "astral_nexus", "alias": "e"}, "west": {"dest_id": "coral_palace", "alias": "w"}}
            },
            "coral_palace": {
                "name": "The Sunken Coral Palace",
                "desc": "Living architecture made of iridescent branching sea coral, nautilus shells, and pearl columns where aquatic spirits congregate.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "plane_water_portal", "alias": "e"}, "down": {"dest_id": "abyssal_trench", "alias": "d"}},
                "npcs": [{"name": "Aquas Tidal Leviathan", "desc": "A serpentine sea titan with shimmering scales of sapphire and jade.", "level": 22, "role": "boss", "danger_tier": "boss"}]
            },
            "abyssal_trench": {
                "name": "The Midnight Trench",
                "desc": "A freezing, pitch-black chasm where pressure mounts and bioluminescent sea creatures glide like phantoms.",
                "terrain": "underwater",
                "exits": {"up": {"dest_id": "coral_palace", "alias": "u"}},
                "items": [{"name": "Trident of the Tidal Lord", "desc": "A sea-glass trident crackling with electrical currents."}]
            },
            "crystal_spire_base": {
                "name": "Base of the Resonant Spire",
                "desc": "Fluted columns of harmonic crystal that hum in unison with cosmic radiation.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "astral_nexus", "alias": "s"}, "up": {"dest_id": "spire_gallery", "alias": "u"}}
            },
            "spire_gallery": {
                "name": "Crystal Harmonic Gallery",
                "desc": "Pulsating quartz prisms refract light into rainbow spectrums that illuminate the void.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "crystal_spire_base", "alias": "d"}}
            },
            "comet_landing": {
                "name": "The Drifting Comet Fragment",
                "desc": "A jagged chunk of ice and rock orbiting slowly around the celestial spire.",
                "terrain": "mountain",
                "exits": {"east": {"dest_id": "void_bridge", "alias": "e"}}
            },
            "aurora_platform": {
                "name": "The Aurora Overlook",
                "desc": "Curtains of emerald and violet celestial light ripple gently beneath your boots.",
                "terrain": "air",
                "exits": {"west": {"dest_id": "void_bridge", "alias": "w"}}
            },
            "pyros_basalt_ridge": {
                "name": "Basalt Lava Flow Ridge",
                "desc": "Cooled ropey pahoehoe lava provides a treacherous path across the magma lake.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "magma_caldera", "alias": "n"}}
            },
            "aquas_whirlpool": {
                "name": "The Maelstrom Nexus",
                "desc": "A vortex of spiraling water that teleports debris across the elemental sea.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "coral_palace", "alias": "s"}}
            },
            "astral_archive": {
                "name": "The Scriptorium of Eternity",
                "desc": "Shelves of solidified light holding scrolls written in celestial angelic runes.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "vault_stars", "alias": "d"}}
            },
            "solar_forge": {
                "name": "The Solar Core Forge",
                "desc": "Harnessing the heat of a captive proto-star, celestial smiths forge armor for archons.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "celestial_pinnacle", "alias": "e"}}
            },
            "void_chasm": {
                "name": "The Edge of Nonexistence",
                "desc": "The boundary where spacetime breaks down into absolute zero and silence.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "comet_landing", "alias": "s"}}
            },
            "pearl_lagoon": {
                "name": "The Lagoon of Tears",
                "desc": "A serene pool within the elemental sea where water tastes sweet as spring rainfall.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "coral_palace", "alias": "n"}}
            },
            "elemental_crossroad": {
                "name": "Nexus of Fire and Water",
                "desc": "Steam billows in thunderous clouds where magma flows collide with glacial currents.",
                "terrain": "air",
                "exits": {"east": {"dest_id": "plane_fire_portal", "alias": "e"}, "west": {"dest_id": "plane_water_portal", "alias": "w"}}
            },
            "deep_abyss_floor": {
                "name": "Floor of the Abyssal Ocean",
                "desc": "White hydrothermal vents spew mineral plumes into the crushing deep.",
                "terrain": "underwater",
                "exits": {"up": {"dest_id": "abyssal_trench", "alias": "u"}}
            }
        }
    }


# =============================================================================
# MARITIME FERRY REGISTRATION
# =============================================================================

def register_bulk_ferry_routes():
    """
    Registers the 4th major maritime ferry route:
    'The Royal Galleon Sea Phantom' connecting Eldoria South Docks,
    Old Praxis Imperial Pier, and Midgaard Royal Wharf.
    """
    galleon_route = {
        "key": "praxis_galleon",
        "name": "The Royal Galleon 'Sea Phantom'",
        "operator": "Commodore Ethan Hawke",
        "operator_title": "Grand Admiral of the Royal Fleet",
        "ports": [
            "south_docks",
            "praxis_province_praxis_harbor",
            "midgaard_district_midgaard_port",
            "praxis_harbor",
            "midgaard_port"
        ],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
            "midgaard_district_midgaard_port": "Midgaard Royal Wharf",
            "praxis_harbor": "Old Praxis Imperial Pier",
            "midgaard_port": "Midgaard Royal Wharf"
        },
        "fares": {
            ("south_docks", "praxis_province_praxis_harbor"): 60,   # 6 silver
            ("praxis_province_praxis_harbor", "south_docks"): 60,
            ("south_docks", "midgaard_district_midgaard_port"): 40,   # 4 silver
            ("midgaard_district_midgaard_port", "south_docks"): 40,
            ("praxis_province_praxis_harbor", "midgaard_district_midgaard_port"): 50, # 5 silver
            ("midgaard_district_midgaard_port", "praxis_province_praxis_harbor"): 50,
            ("south_docks", "praxis_harbor"): 60,
            ("praxis_harbor", "south_docks"): 60,
            ("south_docks", "midgaard_port"): 40,
            ("midgaard_port", "south_docks"): 40,
            ("praxis_harbor", "midgaard_port"): 50,
            ("midgaard_port", "praxis_harbor"): 50
        },
        "desc": "A magnificent three-deck imperial galleon with gilded figurehead, black oak hull, and triple rows of bronze cannons.",
        "deck_key": "praxis_galleon_deck"
    }
    sailing.FERRY_ROUTES["praxis_galleon"] = galleon_route
    return galleon_route


# =============================================================================
# MAIN BULK INGESTION RUNNER
# =============================================================================

def run_bulk_ingestion(clean_existing=True):
    """
    Executes complete bulk ingestion of all 5 zones (150 rooms) with:
    - Fixed danger combat tiers
    - Dual overland and maritime ferry integration
    - Reciprocal anchor connections to Eldoria
    """
    report = {
        "zones_processed": 0,
        "rooms_created": 0,
        "exits_created": 0,
        "npcs_created": 0,
        "items_created": 0,
        "anchors_established": [],
        "ferry_routes_added": []
    }

    zone_builders = [
        build_zone_1_midgaard,
        build_zone_2_goblin_mountain,
        build_zone_3_praxis_province,
        build_zone_4_shadowfen,
        build_zone_5_astral
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("midgaard_district", "south_gate", "north_gate", "north", "south"),
        ("goblin_stronghold", "ridge_trail", "foothills", "north", "south"),
        ("praxis_province", "praxis_east_gate", "dead_mans_cove", "west", "east"),
        ("shadowfen_necropolis", "misty_moor", "marshland", "north", "south"),
        ("astral_rifts", "astral_nexus", "silt_islet", "enter portal", "leave portal")
    ]

    # 1. Clean existing if requested
    if clean_existing:
        for builder in zone_builders:
            data = builder()
            purge_zone(data["zone_key"])

    # 2. Build and Ingest Each Zone
    for builder in zone_builders:
        data = builder()
        zone_key = data["zone_key"]
        zone_name = data["zone_name"]
        rooms_dict = data["rooms"]
        base_coords = data.get("base_coords", (0, 0, 0))

        # Coordinate calculation via BFS
        coords_map = compute_relative_coordinates(rooms_dict, base_coords=base_coords)
        created_rooms = {}

        # Create Rooms, Items, and NPCs
        for r_id, r_info in rooms_dict.items():
            full_key = f"{zone_key}_{r_id}"
            room_title = r_info["name"]
            room_desc = r_info["desc"]
            terrain = r_info.get("terrain", data["default_terrain"])
            coords = coords_map.get(r_id) or coords_map.get(str(r_id), (0, 0, 0))

            room_obj = create_object(Room, key=room_title, tags=[TAG_WORLD])
            room_obj.tags.add(full_key, category="room_key")
            room_obj.tags.add(str(r_id), category="room_key")
            room_obj.tags.add(zone_key, category="zone")
            room_obj.db.room_key = full_key
            room_obj.db.desc = room_desc.strip()
            room_obj.db.zone = zone_name
            room_obj.db.terrain = terrain
            room_obj.db.coords = coords

            created_rooms[str(r_id)] = room_obj
            report["rooms_created"] += 1

            # Items
            for itm in r_info.get("items", []):
                item_obj = create_object(Object, key=itm["name"], location=room_obj, tags=[TAG_WORLD])
                item_obj.tags.add(zone_key, category="zone")
                item_obj.db.desc = itm["desc"].strip()
                report["items_created"] += 1

            # NPCs with Combat & Fixed Danger Stats
            for npc_data in r_info.get("npcs", []):
                npc_obj = create_object(Character, key=npc_data["name"], location=room_obj, tags=[TAG_WORLD])
                npc_obj.tags.add(zone_key, category="zone")
                npc_obj.db.desc = npc_data["desc"].strip()
                
                # Apply stats
                lvl = npc_data.get("level", 1)
                role = npc_data.get("role", "warrior")
                tier = npc_data.get("danger_tier", "normal")
                init_mob_combat(npc_obj, level=lvl, role=role, danger_tier=tier)

                report["npcs_created"] += 1

        # Create Internal Exits
        for r_id, r_info in rooms_dict.items():
            src_room = created_rooms[str(r_id)]
            for dir_name, exit_info in r_info.get("exits", {}).items():
                dest_id = exit_info.get("dest_id") or exit_info.get("dest_vnum")
                dest_key = str(dest_id)
                if dest_key in created_rooms:
                    dest_room = created_rooms[dest_key]
                    alias = exit_info.get("alias")
                    aliases = [alias] if alias else STANDARD_ALIASES.get(dir_name.lower(), [])
                    
                    ex_obj = create_object(
                        Exit,
                        key=dir_name,
                        location=src_room,
                        destination=dest_room,
                        aliases=aliases,
                        tags=[TAG_WORLD]
                    )
                    ex_obj.tags.add(zone_key, category="zone")
                    report["exits_created"] += 1

        report["zones_processed"] += 1

    # 3. Create Overland Anchors
    for zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world in ANCHOR_MAPPINGS:
        world_room = find_room_by_key(world_room_key)
        imported_room = find_room_by_key(f"{zone_key}_{zone_room_id}")

        if world_room and imported_room:
            # Outbound into zone
            ex_out = create_object(
                Exit,
                key=dir_to_zone,
                location=world_room,
                destination=imported_room,
                aliases=STANDARD_ALIASES.get(dir_to_zone.lower(), []),
                tags=[TAG_WORLD]
            )
            ex_out.tags.add(zone_key, category="zone")

            # Return exit back to world
            ex_in = create_object(
                Exit,
                key=dir_to_world,
                location=imported_room,
                destination=world_room,
                aliases=STANDARD_ALIASES.get(dir_to_world.lower(), []),
                tags=[TAG_WORLD]
            )
            ex_in.tags.add(zone_key, category="zone")

            report["anchors_established"].append(f"{world_room.key} <==[{dir_to_zone}/{dir_to_world}]==> {imported_room.key}")
            report["exits_created"] += 2

    # 4. Register Maritime Royal Galleon Route & Weather Deck Room
    deck_room = find_room_by_key("praxis_galleon_deck")
    if not deck_room:
        deck_room = create_object(Room, key="The Royal Galleon 'Sea Phantom' - Weather Deck", tags=[TAG_WORLD])
        deck_room.tags.add("praxis_galleon_deck", category="room_key")
        deck_room.tags.add("praxis_province", category="zone")
        deck_room.db.room_key = "praxis_galleon_deck"
        deck_room.db.desc = (
            "You stand upon the broad teak weather deck of the imperial galleon 'Sea Phantom'. "
            "Polished brass binnacles, tall rigging ladders, and heavy three-pounder carronades "
            "line the bulwarks. Three massive masts rise into the sky, their canvas sails taut with sea winds."
        )
        deck_room.db.zone = "High Seas"
        deck_room.db.terrain = "city"
        deck_room.db.coords = (-10, -10, 0)
        report["rooms_created"] += 1

    register_bulk_ferry_routes()
    report["ferry_routes_added"].append("The Royal Galleon 'Sea Phantom' (south_docks <-> praxis_harbor <-> midgaard_port)")

    return report
