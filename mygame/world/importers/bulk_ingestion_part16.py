"""
Bulk World Ingestion Engine — Part 16: The "3,500+ Rooms Epic Expansion"

Crosses the 3,500-room threshold (reaching 3,518 rooms) across 4 mythic, draconic, aerial, and maritime adventure realms:
1. The Sunken Dragon Temple of Tiamat & Wyrmtooth Abyss [Level 22-30 Draconic Endgame, 60 Rooms]
2. The Floating Islands of the Djinn Caliphate & Mount Qaf [Level 18-26 Aerial Planar, 60 Rooms]
3. The Petrified Forest of the Gorgon & Basilisk Lair [Level 16-24 Stone Horror, 60 Rooms]
4. The Abyssal Sunken Galleon Graveyard of the Sargasso Sea [Level 17-25 Ghost Maritime, 60 Rooms]

Total Rooms Created in Part 16: 241 Rooms (including 'The Djinn Zephyr Skyship Wind Dancer' weather deck)
Cumulative World Total: 3,277 + 241 = 3,518 Rooms!

Features:
- New 'The Djinn Zephyr Skyship Wind Dancer' cloud transit route in sailing.py
- 100% GMCP Room.Info automapper telemetry with relative 3D coordinate graphs
- Fixed danger ratings, full Nightmare LPmud combat sheets, and mythic artifacts
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
    TAG_WORLD
)
from world.importers.bulk_ingestion import init_mob_combat
import world.sailing as sailing


# =============================================================================
# ZONE 62: THE DRAGON TEMPLE OF TIAMAT & WYRMTOOTH ABYSS [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_tiamat_abyss():
    zone_key = "tiamat_abyss"
    zone_name = "The Sunken Dragon Temple of Tiamat & Wyrmtooth Abyss"
    rooms = {}

    rooms["tiamat_wyrmtooth_chasm_entrance"] = {
        "name": "The Jawbones of the Wyrmtooth Chasm",
        "desc": "A colossal archway formed from the fossilized jaws of an ancient dragon turtle. Boiling red-hot steam rises from chasms below, where the roaring echoes of chromatic dragons reverberate.",
        "terrain": "caves",
        "exits": {"north": {"dest_id": "tiamat_dragon_cult_procession", "alias": "n"}},
        "npcs": [{"name": "Dragon Cult Blood-Cleric", "desc": "A fanatical priest draped in dragon scales chanting praises to the Five-Headed Queen.", "level": 22, "role": "mage"}]
    }

    rooms["tiamat_dragon_cult_procession"] = {
        "name": "The Five-Fold Procession Avenue",
        "desc": "A wide cavernous avenue paved with obsidian flags. Banners representing the five chromatic flights (Red, Blue, Green, Black, White) hang from stalactites overhead.",
        "terrain": "caves",
        "exits": {
            "south": {"dest_id": "tiamat_wyrmtooth_chasm_entrance", "alias": "s"},
            "east": {"dest_id": "tiamat_altar_of_red_flame", "alias": "e"},
            "west": {"dest_id": "tiamat_altar_of_blue_lightning", "alias": "w"},
            "north": {"dest_id": "tiamat_wyrm_cavern_01", "alias": "n"}
        },
        "npcs": [{"name": "Dragon-Born Wyrmguard", "desc": "A muscular draconic warrior armed with a flaming halberd.", "level": 24, "role": "warrior"}]
    }

    rooms["tiamat_altar_of_red_flame"] = {
        "name": "The Altar of Incandescent Flame",
        "desc": "An altar carved of volcanic basalt surrounded by basins of boiling sulfur and burning oil, dedicated to the red dragon brood.",
        "terrain": "fire",
        "exits": {"west": {"dest_id": "tiamat_dragon_cult_procession", "alias": "w"}},
        "npcs": [{"name": "Red Dragon Wyrmling", "desc": "A young crimson dragon breathing torrents of fire at intruders.", "level": 25, "role": "warrior"}],
        "items": [{"name": "Ruby Scale of the Fire Wyrm", "desc": "A molten dragon scale that radiates intense warmth."}]
    }

    rooms["tiamat_altar_of_blue_lightning"] = {
        "name": "The Altar of Crackling Lightning",
        "desc": "An altar of desert sandstone where arcs of blue static electricity leap between copper rods, dedicated to the blue dragon brood.",
        "terrain": "caves",
        "exits": {"east": {"dest_id": "tiamat_dragon_cult_procession", "alias": "e"}},
        "npcs": [{"name": "Blue Dragon Wyrmling", "desc": "An azure dragon crackling with ozone and electrical sparks.", "level": 25, "role": "mage"}]
    }

    rooms["tiamat_hall_of_five_altars"] = {
        "name": "The Great Vault of the Five Broods",
        "desc": "A colossal dome where the remaining green, black, and white dragon altars converge around an enormous sacrificial pool of chromatic essence.",
        "terrain": "caves",
        "exits": {
            "south": {"dest_id": "tiamat_wyrm_cavern_18", "alias": "s"},
            "north": {"dest_id": "tiamat_avatar_sanctum_approach", "alias": "n"}
        },
        "npcs": [{"name": "High Dragon Priestess", "desc": "A terrifying sorceress commanding all five elemental dragon breaths.", "level": 27, "role": "mage"}]
    }

    rooms["tiamat_avatar_sanctum_approach"] = {
        "name": "The Dragon Queen's Hoard Vault",
        "desc": "Mountains of gold coins, gemstone chalices, and shattered crowns stolen from a hundred kingdoms. The skeletal remains of slain wyrm-slayers litter the treasure mounds.",
        "terrain": "caves",
        "exits": {
            "south": {"dest_id": "tiamat_hall_of_five_altars", "alias": "s"},
            "north": {"dest_id": "tiamat_throne_of_the_dragon_queen", "alias": "n"}
        },
        "npcs": [{"name": "Chromatic Dragon Warden", "desc": "A gargantuan five-headed hydra-dragon guarding the inner hoard.", "level": 28, "role": "warrior"}]
    }

    rooms["tiamat_throne_of_the_dragon_queen"] = {
        "name": "The Wyrmtooth Throne of Tiamat",
        "desc": "The primordial lair of the Dragon Queen. Sitting upon a throne of dragon bone is the titanic five-headed Avatar of Tiamat, each head glaring with absolute malice.",
        "terrain": "caves",
        "exits": {"south": {"dest_id": "tiamat_avatar_sanctum_approach", "alias": "s"}},
        "npcs": [{"name": "Avatar of Tiamat, the Dragon Queen", "desc": "A titanic five-headed chromatic dragon queen representing Red, Blue, Green, Black, and White dragons. Her roar shakes the very mantle of the earth.", "level": 30, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Five-Headed Dragon Scepter", "desc": "A mythic golden scepter crowned with five miniature dragon heads that unleash all five chromatic breaths."},
            {"name": "Scale-Mail of the Chromatic Tyrant", "desc": "Heavy armor crafted from scales of the five chromatic dragon flights, granting complete elemental immunity."}
        ]
    }

    # 53 connected wyrm caverns, sulfur tunnels, and gold-lined chambers
    for i in range(1, 54):
        r_key = f"tiamat_wyrm_cavern_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Vast subterranean caverns glowing with volcanic magma and crackling with lightning arcs. "
            f"Dragon bones and gold coins litter the jagged stone ledges. [Wyrmtooth Abyss #{i}]"
        )
        r_name = f"Wyrmtooth Abyss Cavern #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"tiamat_wyrm_cavern_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"tiamat_wyrm_cavern_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"tiamat_wyrm_cavern_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"tiamat_wyrm_cavern_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "tiamat_dragon_cult_procession", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "tiamat_hall_of_five_altars", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "tiamat_avatar_sanctum_approach", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Black Dragon Wyrmling", "desc": "An amphibious dark dragon spewing corrosive acid.", "level": 23, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Cult Sorcerer of the Wyrm", "desc": "A robed spellcaster channeling draconic breath magic.", "level": 24, "role": "mage"})

        if i == 20:
            items.append({"name": "Ancient Draconic Gold Coin", "desc": "A heavy platinum coin minted during the reign of the ancient dragon lords."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "caves",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "caves",
        "base_coords": (-60, -200, -100),
        "rooms": rooms
    }


# =============================================================================
# ZONE 63: THE FLOATING ISLANDS OF THE DJINN CALIPHATE [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_djinn_caliphate():
    zone_key = "djinn_caliphate"
    zone_name = "The Floating Islands of the Djinn Caliphate & Mount Qaf"
    rooms = {}

    rooms["djinn_caliphate_cloud_docks"] = {
        "name": "The Cloud Docks of Mount Qaf",
        "desc": "A terrace of pure white marble anchored to a massive floating cloud island. Shimmering flying carpets and brass skiffs bob gently at mooring posts made of solid gold.",
        "terrain": "air",
        "exits": {"north": {"dest_id": "djinn_caliphate_zephyr_bazaar", "alias": "n"}},
        "npcs": [{"name": "Djinn Cloud-Sentry", "desc": "A noble genie hovering in a whirlwind of sweet-smelling air, brandishing a curved silver scimitar.", "level": 19, "role": "warrior"}]
    }

    rooms["djinn_caliphate_zephyr_bazaar"] = {
        "name": "The Great Bazaar of the Trade Winds",
        "desc": "Silk-tented pavilions pitched on floating alabaster discs. Genies trade captured storm clouds, bottled thunderbolts, and perfumed oils under a sky of azure daylight.",
        "terrain": "marble",
        "exits": {
            "south": {"dest_id": "djinn_caliphate_cloud_docks", "alias": "s"},
            "east": {"dest_id": "djinn_caliphate_turquoise_fountain", "alias": "e"},
            "west": {"dest_id": "djinn_caliphate_magic_carpet_loft", "alias": "w"},
            "north": {"djinn_caliphate_island_path_01": "n", "dest_id": "djinn_caliphate_island_path_01", "alias": "n"}
        },
        "npcs": [{"name": "Djinn Merchant of Spices", "desc": "A genial genie floating cross-legged on a carpet offering rare saffron and frankincense.", "level": 20, "role": "civilian"}]
    }

    rooms["djinn_caliphate_turquoise_fountain"] = {
        "name": "The Fountain of Liquid Wind",
        "desc": "A fountain sculpted of solid turquoise where streams of singing, effervescent liquid air bubble upward, defying gravity to dance into the sky.",
        "terrain": "marble",
        "exits": {"west": {"dest_id": "djinn_caliphate_zephyr_bazaar", "alias": "w"}},
        "npcs": [{"name": "Sylph Courtesan", "desc": "A translucent winged spirit of the breeze singing melodies of the upper atmosphere.", "level": 21, "role": "rogue"}],
        "items": [{"name": "Phial of Bottled Trade Wind", "desc": "A sealed crystal phial containing the invigorating breath of the Four Winds."}]
    }

    rooms["djinn_caliphate_magic_carpet_loft"] = {
        "name": "The Flying Carpet Weavery",
        "desc": "Looms strung with threads of spun sunlight and cloud-silk, where master artisans weave flying carpets capable of traversing the Plane of Air.",
        "terrain": "marble",
        "exits": {"east": {"dest_id": "djinn_caliphate_zephyr_bazaar", "alias": "e"}},
        "npcs": [{"name": "Grand Carpet Weaver", "desc": "An elderly djinn artisan floating with needles of gold in hand.", "level": 22, "role": "civilian"}]
    }

    rooms["djinn_caliphate_grand_palace_gate"] = {
        "name": "The Golden Gates of the Zephyr Palace",
        "desc": "Towering minarets of lapis lazuli and white jade flanking gates made of hammered gold. Cool mountain breezes carry the fragrance of blooming jasmine.",
        "terrain": "marble",
        "exits": {
            "south": {"dest_id": "djinn_caliphate_island_path_16", "alias": "s"},
            "north": {"dest_id": "djinn_caliphate_hall_of_thousand_cushions", "alias": "n"}
        },
        "npcs": [{"name": "Palace Guard Mamluk", "desc": "An elite djinn swordsman wielding dual scimitars surrounded by slicing wind vortexes.", "level": 24, "role": "warrior"}]
    }

    rooms["djinn_caliphate_hall_of_thousand_cushions"] = {
        "name": "The Hall of a Thousand Cushions",
        "desc": "An immense audience chamber floor covered in velvet and silk cushions of crimson and gold. Hookahs bubbling with fragrant scented tobacco drift in the breeze.",
        "terrain": "marble",
        "exits": {
            "south": {"dest_id": "djinn_caliphate_grand_palace_gate", "alias": "s"},
            "north": {"dest_id": "djinn_caliphate_throne_of_the_caliph", "alias": "n"}
        },
        "npcs": [{"name": "Grand Vizier of the Djinn", "desc": "A regal genie holding a staff of carved amber and whispering planar counsels.", "level": 26, "role": "mage"}]
    }

    rooms["djinn_caliphate_throne_of_the_caliph"] = {
        "name": "The Cloud Throne of Caliph Al-Zahr",
        "desc": "The highest pinnacle of Mount Qaf. Hovering upon a throne of solid crystallized wind and sapphires sits Caliph Al-Zahr, Sultan of the Zephyr Winds, commanding the sky.",
        "terrain": "air",
        "exits": {"south": {"dest_id": "djinn_caliphate_hall_of_thousand_cushions", "alias": "s"}},
        "npcs": [{"name": "Caliph Al-Zahr of the Zephyr Winds", "desc": "The majestic sovereign of the Djinn, crowned with starlight and wielding the legendary Scimitar of the Four Winds.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Scimitar of the Four Winds", "desc": "A scimitar whose edge is forged of compressed whirlwind, capable of deflecting missile attacks and casting gale-force bursts."},
            {"name": "Ring of Djinn Command", "desc": "A golden signet ring set with an uncut sapphire that grants mastery over wind and flight."}
        ]
    }

    # 53 connected floating islands, cloud bridges, and marble plazas
    for i in range(1, 54):
        r_key = f"djinn_caliphate_island_path_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Alabaster causeways linking floating cloud islands thousands of feet above the earth. "
            f"Pure mountain air and warm breezes carry the chiming of golden bells. [Mount Qaf Terrace #{i}]"
        )
        r_name = f"Mount Qaf Cloud Terrace #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"djinn_caliphate_island_path_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"djinn_caliphate_island_path_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"djinn_caliphate_island_path_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"djinn_caliphate_island_path_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "djinn_caliphate_zephyr_bazaar", "alias": "s"}
        if i == 16:
            exits["north"] = {"dest_id": "djinn_caliphate_grand_palace_gate", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "djinn_caliphate_hall_of_thousand_cushions", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Air Elemental Scout", "desc": "A swift vortex of whistling wind scouting the cloud perimeters.", "level": 20, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Cloud Giant Merchant", "desc": "A smiling giant dressed in flowing silks trading sky-pearls.", "level": 22, "role": "warrior"})

        if i == 19:
            items.append({"name": "Shard of Aerocrystal", "desc": "A crystalline stone lighter than air that floats when dropped."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "marble",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "marble",
        "base_coords": (40, 220, 150),
        "rooms": rooms
    }


# =============================================================================
# ZONE 64: THE PETRIFIED FOREST OF THE GORGON [Level 16-24, 60 Rooms]
# =============================================================================

def build_zone_petrified_forest():
    zone_key = "petrified_forest"
    zone_name = "The Petrified Forest of the Gorgon & Basilisk Lair"
    rooms = {}

    rooms["petrified_forest_gnarled_verge"] = {
        "name": "The Gnarled Stone Verge",
        "desc": "The living trees of the wilderness abruptly turn to grey, petrified stone. Branches of solid granite hang frozen in silent agony, and no birds sing in this lifeless woodland.",
        "terrain": "forest",
        "exits": {"north": {"dest_id": "petrified_forest_avenue_of_statues", "alias": "n"}},
        "npcs": [{"name": "Petrified Forest Ranger", "desc": "A hunter partially transformed into stone, warning travelers away with rasping breath.", "level": 16, "role": "warrior"}]
    }

    rooms["petrified_forest_avenue_of_statues"] = {
        "name": "The Avenue of Fallen Adventurers",
        "desc": "A pathway lined with lifelike statues of knights, wizards, and thieves, their expressions frozen forever in masks of stark terror. Moss grows across their stone eyes.",
        "terrain": "forest",
        "exits": {
            "south": {"dest_id": "petrified_forest_gnarled_verge", "alias": "s"},
            "east": {"dest_id": "petrified_forest_basilisk_burrow", "alias": "e"},
            "west": {"dest_id": "petrified_forest_cockatrice_roost", "alias": "w"},
            "north": {"dest_id": "petrified_forest_stone_path_01", "alias": "n"}
        },
        "npcs": [{"name": "Greater Basilisk", "desc": "An eight-legged reptilian beast with glowing yellow eyes that turn flesh into stone.", "level": 18, "role": "warrior"}]
    }

    rooms["petrified_forest_basilisk_burrow"] = {
        "name": "The Den of the Eight-Legged Basilisks",
        "desc": "A subterranean trench carved beneath petrified roots, littered with the gnawed stone bones of previous victims.",
        "terrain": "hills",
        "exits": {"west": {"dest_id": "petrified_forest_avenue_of_statues", "alias": "w"}},
        "npcs": [{"name": "Noxious Basilisk Broodmother", "desc": "A colossal basilisk spitting acidic bile and glaring with lethal petrifying gaze.", "level": 20, "role": "warrior"}],
        "items": [{"name": "Basilisk Eye Phial", "desc": "A preserved reptilian eye that can be ground into an unguent against petrification."}]
    }

    rooms["petrified_forest_cockatrice_roost"] = {
        "name": "The Roost of the Cockatrices",
        "desc": "Nests built of petrified twigs on stone branches where half-rooster, half-serpent monsters peck among petrified eggs.",
        "terrain": "forest",
        "exits": {"east": {"dest_id": "petrified_forest_avenue_of_statues", "alias": "e"}},
        "npcs": [{"name": "Frenzied Cockatrice", "desc": "A screeching avian monstrosity whose beak delivers a petrifying venom.", "level": 17, "role": "rogue"}]
    }

    rooms["petrified_forest_gorgon_temple_steps"] = {
        "name": "The Steps of the Obsidian Mirror Temple",
        "desc": "Broad stairs of black volcanic glass leading up to an ancient Greek temple. The walls are polished to a high mirror sheen so that no creature may look directly upon its mistress.",
        "terrain": "hills",
        "exits": {
            "south": {"dest_id": "petrified_forest_stone_path_16", "alias": "s"},
            "north": {"dest_id": "petrified_forest_sanctum_of_mirrors", "alias": "n"}
        },
        "npcs": [{"name": "Medusa Priestess", "desc": "A serpent-tailed woman with venomous vipers for hair, drawing an obsidian longbow.", "level": 22, "role": "rogue"}]
    }

    rooms["petrified_forest_sanctum_of_mirrors"] = {
        "name": "The Hall of Shifting Reflections",
        "desc": "A hall lined with thousands of curved silver and obsidian mirrors. Every step produces a dizzying cascade of disorienting reflections to confuse mortal senses.",
        "terrain": "hills",
        "exits": {
            "south": {"dest_id": "petrified_forest_gorgon_temple_steps", "alias": "s"},
            "north": {"dest_id": "petrified_forest_throne_of_the_gorgon", "alias": "n"}
        },
        "npcs": [{"name": "Iron Gorgon Construct", "desc": "A bull forged of solid steel plate snorting green petrifying vapor.", "level": 24, "role": "warrior"}]
    }

    rooms["petrified_forest_throne_of_the_gorgon"] = {
        "name": "The Petrified Throne of Stheno",
        "desc": "The inner sanctum of the Gorgon Matriarch. Surrounding her throne of stone heroes sits Stheno, the Immortal Gorgon, her living serpent crown hissing in fury.",
        "terrain": "hills",
        "exits": {"south": {"dest_id": "petrified_forest_sanctum_of_mirrors", "alias": "s"}},
        "npcs": [{"name": "Stheno, the Immortal Gorgon Matriarch", "desc": "The ancient immortal sister of Medusa, whose hair of coiled vipers and glowing emerald gaze petrifies any living thing that meets her eyes.", "level": 26, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Serpent-Hair Aegis Shield", "desc": "A round bronze shield bearing the carved visage of the Gorgon that can paralyze attacking foes in terror."},
            {"name": "Gaze-Deflecting Obsidian Mirror", "desc": "A flawless hand-mirror of volcanic glass that grants total immunity to gaze attacks and petrification."}
        ]
    }

    # 53 connected petrified trails, stone glades, and rocky hollows
    for i in range(1, 54):
        r_key = f"petrified_forest_stone_path_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Silent forest tracks where oak trunks and pine needles have turned to cold stone. "
            f"Petrified wildlife—stone squirrels, granite wolves, and marble eagles—perch motionless. [Petrified Sector #{i}]"
        )
        r_name = f"Petrified Forest Pathway #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"petrified_forest_stone_path_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"petrified_forest_stone_path_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"petrified_forest_stone_path_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"petrified_forest_stone_path_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "petrified_forest_avenue_of_statues", "alias": "s"}
        if i == 16:
            exits["north"] = {"dest_id": "petrified_forest_gorgon_temple_steps", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "petrified_forest_sanctum_of_mirrors", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Petrified Timber Wolf", "desc": "A stone wolf animated by dark curses stalking silently across the crags.", "level": 17, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Gorgon Viper Swarm", "desc": "A writhing nest of emerald-scaled venomous vipers.", "level": 19, "role": "rogue"})

        if i == 22:
            items.append({"name": "Stone Acorn of Warding", "desc": "A petrified acorn that protects against transmutation curses."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "forest",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "forest",
        "base_coords": (-90, 160, 30),
        "rooms": rooms
    }


# =============================================================================
# ZONE 65: SARGASSO SEA GALLEON GRAVEYARD [Level 17-25, 60 Rooms]
# =============================================================================

def build_zone_sargasso_graveyard():
    zone_key = "sargasso_graveyard"
    zone_name = "The Abyssal Sunken Galleon Graveyard of the Sargasso Sea"
    rooms = {}

    rooms["sargasso_graveyard_rotting_wharf"] = {
        "name": "The Tangled Kelp Verge of the Sargasso",
        "desc": "A vast, stagnant ocean covered with miles of thick, golden-brown sargassum weed. Trapped in the weed are hundreds of ruined galleons, sloops, and pirate frigates from across three centuries.",
        "terrain": "water_swim",
        "exits": {"north": {"dest_id": "sargasso_graveyard_derelict_flagship_deck", "alias": "n"}},
        "npcs": [{"name": "Barnacled Zombie Sailor", "desc": "A drowned sailor draped in sea-weed and barnacles, groaning with water in his lungs.", "level": 17, "role": "warrior"}]
    }

    rooms["sargasso_graveyard_derelict_flagship_deck"] = {
        "name": "The Tilted Deck of the 'Black Leviathan'",
        "desc": "The slippery, barnacled oak deck of a three-masted galleon listing heavily to port. Tattered sails flutter in the moist sea fog, and the ship's wheel turns by itself.",
        "terrain": "water_swim",
        "exits": {
            "south": {"dest_id": "sargasso_graveyard_rotting_wharf", "alias": "s"},
            "east": {"dest_id": "sargasso_graveyard_flooded_captain_cabin", "alias": "e"},
            "west": {"dest_id": "sargasso_graveyard_wrecked_powder_hold", "alias": "w"},
            "north": {"dest_id": "sargasso_graveyard_wreck_drift_01", "alias": "n"}
        },
        "npcs": [{"name": "Ghostly Boatswain", "desc": "A spectral mariner blowing an eerie silver whistle that summons phantom gulls.", "level": 18, "role": "rogue"}]
    }

    rooms["sargasso_graveyard_flooded_captain_cabin"] = {
        "name": "The Flooded Captain's Stateroom",
        "desc": "Knee-deep green seawater sloshes over mildewed navigation charts, empty rum bottles, and a rusted bronze compass mounted on rotting mahogany.",
        "terrain": "water_swim",
        "exits": {"west": {"dest_id": "sargasso_graveyard_derelict_flagship_deck", "alias": "w"}},
        "npcs": [{"name": "Phantom Pirate Captain", "desc": "A spectral corsair with a glowing spectral cutlass, guarding his treasure map.", "level": 20, "role": "warrior"}],
        "items": [{"name": "Waterlogged Pirate Logbook", "desc": "An ancient leather-bound logbook detailing the coordinates of lost sunken galleons."}]
    }

    rooms["sargasso_graveyard_wrecked_powder_hold"] = {
        "name": "The Flooded Powder Magazine",
        "desc": "Waterlogged barrels of spoiled black powder and crates of rusted cannonballs covered in thick colonies of orange sea anemones.",
        "terrain": "water_swim",
        "exits": {"east": {"dest_id": "sargasso_graveyard_derelict_flagship_deck", "alias": "e"}},
        "npcs": [{"name": "Giant Sargasso Crab", "desc": "A massive sea crab with shells resembling shipwreck timber.", "level": 19, "role": "warrior"}]
    }

    rooms["sargasso_graveyard_davy_jones_approach"] = {
        "name": "The Hull of the 'Flying Dutchman'",
        "desc": "The dreaded ghost ship itself, its timber hull fused with living brain coral, barnacles, and starfish. A cold supernatural stench of salt brine and eternity hangs heavy in the air.",
        "terrain": "water_swim",
        "exits": {
            "south": {"dest_id": "sargasso_graveyard_wreck_drift_16", "alias": "s"},
            "north": {"dest_id": "sargasso_graveyard_ghostly_poop_deck", "alias": "n"}
        },
        "npcs": [{"name": "Cursed Hammerhead Crewman", "desc": "A mutant mariner with the head of a predatory hammerhead shark wielding a jagged boarding axe.", "level": 23, "role": "warrior"}]
    }

    rooms["sargasso_graveyard_ghostly_poop_deck"] = {
        "name": "The Poop Deck of the Dutchman",
        "desc": "High above the tangled sea of weed, the stern of the cursed vessel looks out over hundreds of decaying shipwrecks. Green witch-fire burns silently in the stern lanterns.",
        "terrain": "water_swim",
        "exits": {
            "south": {"dest_id": "sargasso_graveyard_davy_jones_approach", "alias": "s"},
            "north": {"dest_id": "sargasso_graveyard_throne_of_davy_jones", "alias": "n"}
        },
        "npcs": [{"name": "Siren of the Drowned", "desc": "An ethereal apparition singing a mournful dirge for lost souls.", "level": 25, "role": "mage"}]
    }

    rooms["sargasso_graveyard_throne_of_davy_jones"] = {
        "name": "The Abyssal Helm of Davy Jones",
        "desc": "The captain's deck of the Dutchman. Standing beside the barnacled helm is Captain Davy Jones, the immortal collector of drowned souls, holding his crab-claw cane and the key to his dreaded chest.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "sargasso_graveyard_ghostly_poop_deck", "alias": "s"}},
        "npcs": [{"name": "Captain Davy Jones, Warden of the Deep", "desc": "The legendary tyrant of the deep ocean, with tentacles for a beard, an enormous crab claw for an arm, and a gaze cold as the bottom of the sea.", "level": 27, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Dead Man's Chest Key", "desc": "An ancient iron skeleton key that unlocks the mythical chest of Davy Jones."},
            {"name": "Cutlass of the Barnacled Deep", "desc": "A serrated cutlass encrusted with razor barnacles that inflicts deep bleeding wounds and slows enemies."}
        ]
    }

    # 53 connected drifting ship hulls, tangled weed paths, and floating masts
    for i in range(1, 54):
        r_key = f"sargasso_graveyard_wreck_drift_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Rotting ship timbers and tangled ropes connecting derelict ship hulls across the golden weed. "
            f"Ghostly fog drifts over the stagnant green swells. [Sargasso Wreck #{i}]"
        )
        r_name = f"Sargasso Galleon Wreck #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"sargasso_graveyard_wreck_drift_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"sargasso_graveyard_wreck_drift_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"sargasso_graveyard_wreck_drift_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"sargasso_graveyard_wreck_drift_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "sargasso_graveyard_derelict_flagship_deck", "alias": "s"}
        if i == 16:
            exits["north"] = {"dest_id": "sargasso_graveyard_davy_jones_approach", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "sargasso_graveyard_ghostly_poop_deck", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Drowned Marine", "desc": "A skeletal redcoat soldier still clutching a rusted musket.", "level": 18, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Sargasso Ghost Jellyfish", "desc": "A phosphorescent jellyfish drifting through the submerged hulls.", "level": 20, "role": "mage"})

        if i == 25:
            items.append({"name": "Flask of Smuggler's Spiced Rum", "desc": "Century-old spiced rum that cures fear and warms the spirit."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "water_swim",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "water_swim",
        "base_coords": (160, -220, -10),
        "rooms": rooms
    }


# =============================================================================
# MARITIME ROUTE HELPER
# =============================================================================

def register_wind_dancer_ferry_routes():
    """Ensures The Djinn Zephyr-Carpet Skyship 'Wind Dancer' is registered in sailing.FERRY_ROUTES."""
    if "wind_dancer_ship" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["wind_dancer_ship"] = {
            "key": "wind_dancer_ship",
            "name": 'The Djinn Zephyr Skyship "The Wind Dancer"',
            "operator": "Djinn Navigator Rashid",
            "operator_title": "Grand Aeronaut of the Trade Winds",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "djinn_caliphate_cloud_docks", "mount_qaf_docks"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "djinn_caliphate_cloud_docks": "The Cloud Docks of Mount Qaf",
                "mount_qaf_docks": "The Cloud Docks of Mount Qaf"
            },
            "fares": {
                ("south_docks", "djinn_caliphate_cloud_docks"): 120,
                ("djinn_caliphate_cloud_docks", "south_docks"): 120,
                ("praxis_province_praxis_harbor", "djinn_caliphate_cloud_docks"): 105,
                ("djinn_caliphate_cloud_docks", "praxis_province_praxis_harbor"): 105,
                ("south_docks", "mount_qaf_docks"): 120,
                ("mount_qaf_docks", "south_docks"): 120,
                ("praxis_province_praxis_harbor", "mount_qaf_docks"): 105,
                ("mount_qaf_docks", "praxis_province_praxis_harbor"): 105
            },
            "desc": "A flying skyship fitted with giant outriggers of woven cloud-silk and sails that billow with perpetual warm trade winds, steered with a golden astrolabe.",
            "deck_key": "wind_dancer_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 16
# =============================================================================

def run_bulk_ingestion_part16(clean_existing=False):
    """
    Executes Part 16 of the bulk world expansion ("3,500+ Rooms Epic Expansion"):
    - The Sunken Dragon Temple of Tiamat & Wyrmtooth Abyss (60 rooms)
    - The Floating Islands of the Djinn Caliphate & Mount Qaf (60 rooms)
    - The Petrified Forest of the Gorgon & Basilisk Lair (60 rooms)
    - The Abyssal Sunken Galleon Graveyard of the Sargasso Sea (60 rooms)
    Plus The Djinn Zephyr Skyship 'The Wind Dancer' weather deck (1 room).
    Total: 241 rooms!
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
        build_zone_tiamat_abyss,
        build_zone_djinn_caliphate,
        build_zone_petrified_forest,
        build_zone_sargasso_graveyard
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("tiamat_abyss", "tiamat_wyrmtooth_chasm_entrance", "chasm_bridge", "descend into wyrmtooth abyss of tiamat", "ascend dragon chasm back to howling bridge"),
        ("djinn_caliphate", "djinn_caliphate_cloud_docks", "summit", "soar upward to cloud docks of mount qaf", "descend trade winds back to summit"),
        ("petrified_forest", "petrified_forest_gnarled_verge", "foothills", "enter petrified forest of the gorgon", "retreat from petrified forest to craggy foothills"),
        ("sargasso_graveyard", "sargasso_graveyard_rotting_wharf", "dead_mans_cove", "sail into sargasso galleon graveyard", "escape tangled sargasso back to dead mans cove")
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

        coords_map = compute_relative_coordinates(rooms_dict, base_coords=base_coords)
        created_rooms = {}

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

            for itm in r_info.get("items", []):
                item_obj = create_object(Object, key=itm["name"], location=room_obj, tags=[TAG_WORLD])
                item_obj.tags.add(zone_key, category="zone")
                item_obj.db.desc = itm["desc"].strip()
                report["items_created"] += 1

            for npc_data in r_info.get("npcs", []):
                npc_obj = create_object(Character, key=npc_data["name"], location=room_obj, tags=[TAG_WORLD])
                npc_obj.tags.add(zone_key, category="zone")
                npc_obj.db.desc = npc_data["desc"].strip()

                lvl = npc_data.get("level", 1)
                role = npc_data.get("role", "warrior")
                tier = npc_data.get("danger_tier", "normal")
                init_mob_combat(npc_obj, level=lvl, role=role, danger_tier=tier)

                report["npcs_created"] += 1

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

    # 3. Create Anchors
    for zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world in ANCHOR_MAPPINGS:
        world_room = find_room_by_key(world_room_key)
        imported_room = find_room_by_key(f"{zone_key}_{zone_room_id}")

        if world_room and imported_room:
            ex_out = create_object(
                Exit,
                key=dir_to_zone,
                location=world_room,
                destination=imported_room,
                aliases=STANDARD_ALIASES.get(dir_to_zone.lower(), []),
                tags=[TAG_WORLD]
            )
            ex_out.tags.add(zone_key, category="zone")

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

    # 4. Register Wind Dancer Skyship Ferry Route & Weather Deck
    wind_dancer_deck = find_room_by_key("wind_dancer_deck")
    if not wind_dancer_deck:
        wind_dancer_deck = create_object(Room, key='The Djinn Zephyr Skyship "The Wind Dancer" - Weather Deck', tags=[TAG_WORLD])
        wind_dancer_deck.tags.add("wind_dancer_deck", category="room_key")
        wind_dancer_deck.tags.add("djinn_caliphate", category="zone")
        wind_dancer_deck.db.room_key = "wind_dancer_deck"
        wind_dancer_deck.db.desc = (
            "You stand upon the silk-carpeted flying deck of the zephyr skyship. "
            "Enormous outriggers of spun cloud-silk catch the high-altitude jet streams, "
            "gliding effortlessly across the azure horizon."
        )
        wind_dancer_deck.db.zone = "Trade Winds"
        wind_dancer_deck.db.terrain = "air"
        wind_dancer_deck.db.coords = (40, 200, 140)
        report["rooms_created"] += 1

    register_wind_dancer_ferry_routes()
    report["ferry_routes_added"].append('The Djinn Zephyr Skyship "The Wind Dancer" (south_docks <-> praxis_province_praxis_harbor <-> djinn_caliphate_cloud_docks)')

    return report

