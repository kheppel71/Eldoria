"""
Bulk World Ingestion Engine — Part 9: The "1,800 Rooms Milestone" Super-Expansion

Expands Eldoria with an additional 289 rooms across 4 legendary adventure realms:
1. The Grand Labyrinth of Minos & Cretan Catacombs [Level 8-15, 72 Rooms]
2. The City-State of Ankh-Morpork & The Patrician's Palace [Level 6-14, 72 Rooms]
3. The Obsidian Dragon Wastes & Wyrm Peak [Level 18-26, 72 Rooms]
4. The Sunken Deep Trench of R'lyeh & Cyclopean Ruins [Level 22-30 Endgame, 72 Rooms]

Total Rooms Created in Part 9: 289 Rooms
Cumulative World Total: 1,513 + 289 = 1,802 Rooms!

Features:
- New 'The Cargo-Barge Pride of the Ankh' maritime river route
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
# ZONE 34: THE GRAND LABYRINTH OF MINOS [Level 8-15, 72 Rooms]
# =============================================================================

def build_zone_labyrinth():
    zone_key = "labyrinth_minos"
    zone_name = "The Grand Labyrinth of Minos"
    rooms = {}

    rooms["labyrinth_minos_bronze_gate"] = {
        "name": "The Bronze Gate of Daedalus",
        "desc": "A monumental portal of cast bronze flanked by relief sculptures of horned bulls and twisting labyrinths. Beyond lies the legendary maze built to imprison the beast.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "hall_of_mirrors_daedalus", "alias": "n"}},
        "npcs": [{"name": "Cretan Sentry Guard", "desc": "A disciplined hoplite in bronze cuirass with a long thrusting spear.", "level": 8, "role": "warrior"}]
    }

    rooms["hall_of_mirrors_daedalus"] = {
        "name": "The Hall of Bronze Mirrors",
        "desc": "Polished sheets of reflective bronze line the twisting stone walls, distorting perspective and multiplying shadows in disorienting geometric illusions.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "labyrinth_minos_bronze_gate", "alias": "s"}, "north": {"dest_id": "labyrinth_turn_01", "alias": "n"}, "east": {"dest_id": "gorgon_petrified_colonnade", "alias": "e"}},
        "items": [{"name": "Polished Bronze Mirror Shield", "desc": "A gleaming shield that reflects gaze attacks and illusion spells."}]
    }

    rooms["gorgon_petrified_colonnade"] = {
        "name": "The Colonnade of Petrified Heroes",
        "desc": "Life-sized stone statues of screaming warriors, shields raised in futility, frozen forever in gray limestone. The sound of hissing snakes echoes faintly.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "hall_of_mirrors_daedalus", "alias": "w"}, "north": {"dest_id": "labyrinth_turn_15", "alias": "n"}},
        "npcs": [{"name": "Labyrinth Gorgon", "desc": "A serpent-bodied monstrous woman with writhing vipers for hair and petrifying golden eyes.", "level": 12, "role": "mage"}]
    }

    rooms["golden_thread_alcove"] = {
        "name": "The Alcove of Ariadne's Thread",
        "desc": "A hidden niche where a spool of glowing golden silk thread is anchored to an iron peg, offering hope to desperate wanderers.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "labyrinth_turn_30", "alias": "s"}},
        "items": [{"name": "Spool of Ariadne's Golden Thread", "desc": "A magical thread that glows softly, guiding the bearer back toward safety."}]
    }

    rooms["labyrinth_center_altar"] = {
        "name": "The Blood Altar of Asterion",
        "desc": "In the very center of the maze opens a colossal amphitheater of cracked marble. A massive blood-stained granite altar rises in the center beneath a skylight shaft.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "labyrinth_turn_45", "alias": "s"}},
        "npcs": [{"name": "Asterion the Minotaur King", "desc": "A nine-foot bull-headed warlord with curling iron horns, scarred muscular shoulders, brandishing a massive double-bladed labrys axe.", "level": 15, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Cretan Labrys of the Bull King", "desc": "A colossal two-headed bronze battleaxe that delivers bone-crushing cleaving blows."}]
    }

    rooms["dead_end_bone_pit"] = {
        "name": "The Chasm of Trapped Skeletons",
        "desc": "A pit filled with the gnawed bones of hundreds of tribute victims who lost their way in the maze.",
        "terrain": "catacombs",
        "exits": {"east": {"dest_id": "labyrinth_turn_20", "alias": "e"}},
        "items": [{"name": "Ancient Bronze Hoplite Shield", "desc": "A round bronze shield stamped with the gorgon crest."}]
    }

    # 66 Maze corridor and turn rooms to reach 72 rooms
    for i in range(1, 67):
        r_key = f"labyrinth_turn_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"High limestone walls polished smooth by centuries of desperate clawing fingers. "
            f"The passage bends sharply, concealing what lies ahead. [Maze Corridor #{i}]"
        )
        r_name = f"Labyrinth Stone Passage #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"labyrinth_turn_{i-1:02d}", "alias": "s"}
        if i < 66:
            exits["north"] = {"dest_id": f"labyrinth_turn_{i+1:02d}", "alias": "n"}
        if i + 6 <= 66:
            exits["east"] = {"dest_id": f"labyrinth_turn_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"labyrinth_turn_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "hall_of_mirrors_daedalus", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "gorgon_petrified_colonnade", "alias": "s"}
        if i == 20:
            exits["west"] = {"dest_id": "dead_end_bone_pit", "alias": "w"}
        if i == 30:
            exits["north"] = {"dest_id": "golden_thread_alcove", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "labyrinth_center_altar", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Minotaur Marauder", "desc": "A muscular beast-man wielding an iron-tipped war club.", "level": 10, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Maze Trap Mechanist", "desc": "A dwarven rogue resetting deadly spring-blade traps.", "level": 9, "role": "rogue"})

        if i == 12:
            items.append({"name": "Sack of Athenian Silver Drachmas", "desc": "Heavy silver coins stamped with an owl."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "catacombs",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "catacombs",
        "base_coords": (-20, -15, -20),
        "rooms": rooms
    }


# =============================================================================
# ZONE 35: THE CITY-STATE OF ANKH-MORPORK [Level 6-14, 72 Rooms]
# =============================================================================

def build_zone_ankh_morpork():
    zone_key = "ankh_morpork"
    zone_name = "The City-State of Ankh-Morpork"
    rooms = {}

    rooms["ankh_morpork_brass_bridge_wharf"] = {
        "name": "The Brass Bridge Wharf of Ankh-Morpork",
        "desc": "A bustling timber wharf flanking the legendary River Ankh, a river so thick with historical silt and industrial runoff that you can practically walk across it.",
        "terrain": "city",
        "exits": {"north": {"dest_id": "shades_alley_dark", "alias": "n"}, "east": {"dest_id": "dagon_street_market", "alias": "e"}},
        "npcs": [{"name": "Corporal Nobby Nobbs", "desc": "A small, disreputable watchman who carries a certificate proving he is human.", "level": 6, "role": "rogue"}]
    }

    rooms["shades_alley_dark"] = {
        "name": "The Treacherous Alleys of the Shades",
        "desc": "The most dangerous slum in the city. Narrow, leaning timber tenements block out the sun, and cutpurses lurk in every soot-stained shadow.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "ankh_morpork_brass_bridge_wharf", "alias": "s"}, "north": {"dest_id": "night_watch_treacle_mine", "alias": "n"}, "west": {"dest_id": "ankh_street_01", "alias": "w"}}
    }

    rooms["night_watch_treacle_mine"] = {
        "name": "The Treacle Mine Road Watch House",
        "desc": "The headquarters of the City Watch. The room smells of old tobacco, wet iron, and leather. A battered chalkboard lists unsolved crimes.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "shades_alley_dark", "alias": "s"}, "north": {"dest_id": "patrician_oblong_office", "alias": "n"}},
        "npcs": [{"name": "Commander Samuel Vimes", "desc": "The hard-bitten, cynical commander of the City Watch with a smoldering cigar stub and cardboard boots.", "level": 13, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Vimes' Copper City Watch Badge", "desc": "A tarnished copper shield badge representing the absolute incorruptibility of the law."}]
    }

    rooms["patrician_oblong_office"] = {
        "name": "The Oblong Office of Lord Vetinari",
        "desc": "An impeccably neat office furnished with bare black wood and a single desk. Behind it sits Lord Havelock Vetinari, the supreme ruler of Ankh-Morpork.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "night_watch_treacle_mine", "alias": "s"}},
        "npcs": [{"name": "Lord Havelock Vetinari", "desc": "The Patrician of Ankh-Morpork, clad in austere black velvet, regarding you with cool, razor-sharp intellectual dominance.", "level": 14, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Stiletto of Absolute Tyranny", "desc": "An exquisite balance dagger that strikes vital nerves with surgical precision."}]
    }

    rooms["unseen_university_library"] = {
        "name": "The High Library of the Unseen University",
        "desc": "Thousands of magical grimoires chained to granite shelves. Books whisper and warp gravitational physics.",
        "terrain": "indoors",
        "exits": {"east": {"dest_id": "ankh_street_20", "alias": "e"}},
        "npcs": [{"name": "The Librarian", "desc": "A 300-pound orangutan in a velvet waistcoat reading a spellbook. 'Oook!' he grunts warningly.", "level": 12, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Enchanted Yellow Banana of Knowledge", "desc": "A mystical snack that boosts intellect and restores spell slots."}]
    }

    rooms["dagon_street_market"] = {
        "name": "The Scented Bazaars of Dagon Street",
        "desc": "Stalls selling dried figs, pickled eels, dubious magical talismans, and hot pies of mysterious meat content.",
        "terrain": "city",
        "exits": {"west": {"dest_id": "ankh_morpork_brass_bridge_wharf", "alias": "w"}, "north": {"dest_id": "ankh_street_40", "alias": "n"}},
        "items": [{"name": "C.M.O.T. Dibbler's Sausage-in-a-Bun", "desc": "A hot sausage in a roll. It sizzles ominously. Eating it is an adventure."}]
    }

    # 66 Ankh-Morpork streets, bridges, and guild houses to reach 72 rooms
    for i in range(1, 67):
        r_key = f"ankh_street_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Cobblestones slick with river fog and horse traffic. "
            f"Guild crests hang from iron brackets above shops and taverns. [City Sector #{i}]"
        )
        r_name = f"Ankh-Morpork Cobbled Street #{i}"
        
        exits = {}
        if i > 1:
            exits["west"] = {"dest_id": f"ankh_street_{i-1:02d}", "alias": "w"}
        if i < 66:
            exits["east"] = {"dest_id": f"ankh_street_{i+1:02d}", "alias": "e"}
        if i + 6 <= 66:
            exits["north"] = {"dest_id": f"ankh_street_{i+6:02d}", "alias": "n"}
        if i - 6 >= 1:
            exits["south"] = {"dest_id": f"ankh_street_{i-6:02d}", "alias": "s"}

        if i == 1:
            exits["east"] = {"dest_id": "shades_alley_dark", "alias": "e"}
        if i == 20:
            exits["west"] = {"dest_id": "unseen_university_library", "alias": "w"}
        if i == 40:
            exits["south"] = {"dest_id": "dagon_street_market", "alias": "s"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Thieves' Guild Licensed Cutpurse", "desc": "A rogue who politely hands you a receipt after stealing your purse.", "level": 7, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Unseen University Wizard Student", "desc": "A young apprentice in pointy hat covered in singed astrological stars.", "level": 8, "role": "mage"})

        if i == 15:
            items.append({"name": "Bottle of Dwarf Bread Crumb Ale", "desc": "Beer as thick and hard as a dwarven battle-loaf."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "city",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "city",
        "base_coords": (10, 15, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 36: THE OBSIDIAN DRAGON WASTES [Level 18-26, 72 Rooms]
# =============================================================================

def build_zone_dragon_wastes():
    zone_key = "dragon_wastes"
    zone_name = "The Obsidian Dragon Wastes & Wyrm Peak"
    rooms = {}

    rooms["dragon_wastes_cinder_pass"] = {
        "name": "The Ash-Choked Cinder Pass",
        "desc": "A narrow mountain defile strewn with volcanic basalt boulders and drifts of suffocating gray ash. Smoke drifts from volcanic vents in the red rock.",
        "terrain": "mountain",
        "exits": {"north": {"dest_id": "sulfur_caldera_basin", "alias": "n"}},
        "npcs": [{"name": "Magma Drake Hatchling", "desc": "A six-foot scaled drake with wings of embers that spits globs of liquid fire.", "level": 18, "role": "warrior"}]
    }

    rooms["sulfur_caldera_basin"] = {
        "name": "The Great Sulfur Steam Caldera",
        "desc": "A crater of boiling sulfur geysers and yellow mineral terraces. The air is caustic and stings mortal lungs.",
        "terrain": "mountain",
        "exits": {"south": {"dest_id": "dragon_wastes_cinder_pass", "alias": "s"}, "north": {"dest_id": "obsidian_ridge_peak", "alias": "n"}, "east": {"dest_id": "dragonkin_hatchery_volcano", "alias": "e"}}
    }

    rooms["dragonkin_hatchery_volcano"] = {
        "name": "The Dragonkin Magma Hatchery",
        "desc": "Pits of liquid magma where leathery red dragon eggs are nurtured by elite draconian priests in spiked brass armor.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "sulfur_caldera_basin", "alias": "w"}, "north": {"dest_id": "waste_canyon_01", "alias": "n"}},
        "npcs": [{"name": "Dragonkin High Zealot", "desc": "A hulking dragonborn cleric wielding a blazing serrated glaive.", "level": 21, "role": "cleric"}]
    }

    rooms["obsidian_ridge_peak"] = {
        "name": "The Obsidian Spire Lookout",
        "desc": "A pinnacle of black volcanic glass rising above sea-level clouds, looking out across the smoking craters of the Dragon Wastes.",
        "terrain": "air",
        "exits": {"south": {"dest_id": "sulfur_caldera_basin", "alias": "s"}, "up": {"dest_id": "wyrm_hoard_cavern", "alias": "u"}}
    }

    rooms["wyrm_hoard_cavern"] = {
        "name": "The Titanic Gold Hoard of Pyrothrax",
        "desc": "A cavern large enough to hold an army, buried beneath mountains of sparkling gold coin, jewel-encrusted crowns, and the charred bones of dragon-slayers.",
        "terrain": "mountain",
        "exits": {"down": {"dest_id": "obsidian_ridge_peak", "alias": "d"}},
        "npcs": [{"name": "Pyrothrax the Ancient Red Wyrm", "desc": "A colossal red dragon sixty feet from snout to tail, clad in impenetrable crimson scales, breathing tempestuous hellfire.", "level": 26, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Scale of the Firestorm Dragon", "desc": "A dragon scale large as a tower shield that renders the bearer completely impervious to fire."}]
    }

    # 67 Cinder canyons, lava tubes, and ash wastes to reach 72 rooms
    for i in range(1, 68):
        r_key = f"waste_canyon_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Black volcanic basalt ridges cracked by subterranean heat. "
            f"Fumes of sulfur and orange sparks drift along the barren stone. [Wastes Canyon #{i}]"
        )
        r_name = f"Volcanic Cinder Ridge #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"waste_canyon_{i-1:02d}", "alias": "s"}
        if i < 67:
            exits["north"] = {"dest_id": f"waste_canyon_{i+1:02d}", "alias": "n"}
        if i + 6 <= 67:
            exits["east"] = {"dest_id": f"waste_canyon_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"waste_canyon_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "dragonkin_hatchery_volcano", "alias": "s"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Fire Elemental Salamander", "desc": "A serpent of living flame dancing across molten rocks.", "level": 19, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Ash Drake Stalker", "desc": "A predatory grey winged reptile that strikes from smoke clouds.", "level": 20, "role": "rogue"})

        if i == 25:
            items.append({"name": "Chunk of Crystallized Fire Opal", "desc": "A precious gem that pulses with internal fiery light."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "mountain",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "mountain",
        "base_coords": (60, -10, 20),
        "rooms": rooms
    }


# =============================================================================
# ZONE 37: THE SUNKEN CYCLOPEAN RUINS OF R'LYEH [Level 22-30, 72 Rooms]
# =============================================================================

def build_zone_rlyeh():
    zone_key = "rlyeh_trench"
    zone_name = "The Sunken Deep Trench of R'lyeh"
    rooms = {}

    rooms["rlyeh_trench_cyclopean_pylon"] = {
        "name": "The Slime-Encrusted Cyclopean Pylon",
        "desc": "A titanic megalith of non-Euclidean black stone rising thousands of feet from the ocean floor. Strange sea-green slime coats impossible angles that hurt mortal eyes.",
        "terrain": "underwater",
        "exits": {"down": {"dest_id": "non_euclidean_hall", "alias": "d"}},
        "npcs": [{"name": "Deep One Vanguard", "desc": "A fish-frog humanoid with staring bulging eyes and glistening gray-green scales holding a trident.", "level": 22, "role": "warrior"}]
    }

    rooms["non_euclidean_hall"] = {
        "name": "The Hall of Non-Euclidean Geometry",
        "desc": "A vast hall where walls converge at angles that seem both acute and obtuse at the same time. Walking along the floor feels like climbing an impossible ceiling.",
        "terrain": "catacombs",
        "exits": {"up": {"dest_id": "rlyeh_trench_cyclopean_pylon", "alias": "u"}, "north": {"dest_id": "deep_one_spawning_reef", "alias": "n"}, "east": {"dest_id": "star_spawn_monolith", "alias": "e"}},
        "npcs": [{"name": "Star-Spawn Inquisitor", "desc": "A towering octopoid monstrosity with bat wings that projects madness into mortal thoughts.", "level": 24, "role": "mage"}]
    }

    rooms["deep_one_spawning_reef"] = {
        "name": "The Sunken Reef of the Deep Ones",
        "desc": "Subterranean trenches littered with carved golden tiaras and unholy biological incubators where hybrid monstrosities hatch.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "non_euclidean_hall", "alias": "s"}, "north": {"dest_id": "vault_of_the_sleeper", "alias": "n"}},
        "npcs": [{"name": "Father Dagon Champion", "desc": "A colossal ancient Deep One the size of a whale, armed with a serrated barnacle harpoon.", "level": 27, "role": "boss", "danger_tier": "boss"}]
    }

    rooms["star_spawn_monolith"] = {
        "name": "The Monolith of the Great Old Ones",
        "desc": "An unholy black obelisk humming with low-frequency sonic vibrations that echo across dimensions.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "non_euclidean_hall", "alias": "w"}, "north": {"dest_id": "rlyeh_vault_01", "alias": "n"}},
        "items": [{"name": "Carved Green Soapstone Idol of Cthulhu", "desc": "An idol depicting a creature with tentacles, wings, and rubbery body that radiates cosmic dread."}]
    }

    rooms["vault_of_the_sleeper"] = {
        "name": "The Tomb of the Slumbering Elder God",
        "desc": "In the deepest abyss of R'lyeh, behind an immense carved portal of black basalt that oozes green luminescent ichor, slumbers the Great Old One.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "deep_one_spawning_reef", "alias": "s"}},
        "npcs": [{"name": "The Sleeper of R'lyeh", "desc": "The cosmic titan avatar of Cthulhu, towering hundreds of feet high, crowned with writhing tentacles, eyes burning with madness from beyond the stars.", "level": 30, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Cosmic Eye of the Star-Spawn", "desc": "The supreme cosmic relic capable of tearing dimensional rifts and sundering mortal sanity."}]
    }

    # 67 Non-Euclidean passages, flooded vaults, and slime trenches to reach 72 rooms
    for i in range(1, 68):
        r_key = f"rlyeh_vault_{i:02d}"
        if r_key in rooms:
            continue
        
        terrain = "underwater" if i % 3 == 0 else "catacombs"
        desc = (
            f"Black stone blocks mortared with green cosmic slime. "
            f"The architecture bends in disturbing impossible dimensions. [R'lyeh Vault #{i}]"
        )
        r_name = f"Cyclopean Vault #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"rlyeh_vault_{i-1:02d}", "alias": "s"}
        if i < 67:
            exits["north"] = {"dest_id": f"rlyeh_vault_{i+1:02d}", "alias": "n"}
        if i + 6 <= 67:
            exits["east"] = {"dest_id": f"rlyeh_vault_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"rlyeh_vault_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "star_spawn_monolith", "alias": "s"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Shoggoth Protoplasmic Mass", "desc": "A terrifying shapeless monster of bubbling eyes and ravenous mouths.", "level": 25, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Deep One Priestess", "desc": "A chanting aquatic sorceress holding a curved bone sacrificial knife.", "level": 23, "role": "cleric"})

        if i == 30:
            items.append({"name": "Golden Tiara of the Deep Ones", "desc": "A tiara of unearthly gold engraved with bizarre aquatic horrors."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": terrain,
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "catacombs",
        "base_coords": (-60, -70, -50),
        "rooms": rooms
    }


# =============================================================================
# INGESTION RUNNER & REGISTRATION
# =============================================================================

def register_ankh_ferry_routes():
    """Register the Ankh-Morpork Cargo-Barge transit route."""
    if "ankh_barge" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["ankh_barge"] = {
            "key": "ankh_barge",
            "name": 'The Cargo-Barge "Pride of the Ankh"',
            "operator": "Bargemaster C.M.O.T. Dibbler",
            "operator_title": "Purveyor of Fine River Cruises & Hot Meat Pies",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "ankh_morpork_brass_bridge_wharf", "ankh_wharf"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "ankh_morpork_brass_bridge_wharf": "The Brass Bridge Wharf of Ankh-Morpork",
                "ankh_wharf": "The Brass Bridge Wharf of Ankh-Morpork"
            },
            "fares": {
                ("south_docks", "ankh_morpork_brass_bridge_wharf"): 50,
                ("ankh_morpork_brass_bridge_wharf", "south_docks"): 50,
                ("praxis_province_praxis_harbor", "ankh_morpork_brass_bridge_wharf"): 40,
                ("ankh_morpork_brass_bridge_wharf", "praxis_province_praxis_harbor"): 40,
                ("south_docks", "ankh_wharf"): 50,
                ("ankh_wharf", "south_docks"): 50,
                ("praxis_province_praxis_harbor", "ankh_wharf"): 40,
                ("ankh_wharf", "praxis_province_praxis_harbor"): 40
            },
            "desc": "A flat-bottomed wooden cargo barge smelling faintly of fried onions, stagnant river mud, and mystery meat sausages.",
            "deck_key": "ankh_barge_deck"
        }


def run_bulk_ingestion_part9(clean_existing=False):
    """
    Executes Part 9 of the bulk world expansion ("1,800 Rooms Milestone"):
    - The Grand Labyrinth of Minos (72 rooms)
    - The City-State of Ankh-Morpork (72 rooms)
    - The Obsidian Dragon Wastes (72 rooms)
    - The Sunken Deep Trench of R'lyeh (72 rooms)
    Total: 289 rooms (including the Ankh-Morpork Cargo-Barge weather deck)!
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
        build_zone_labyrinth,
        build_zone_ankh_morpork,
        build_zone_dragon_wastes,
        build_zone_rlyeh
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("labyrinth_minos", "labyrinth_minos_bronze_gate", "foothills", "enter the maze of daedalus", "escape the labyrinth"),
        ("ankh_morpork", "ankh_morpork_brass_bridge_wharf", "north_gate", "cross onto brass bridge", "leave brass bridge"),
        ("dragon_wastes", "dragon_wastes_cinder_pass", "chasm_bridge", "cross into dragon wastes", "return to howling bridge"),
        ("rlyeh_trench", "rlyeh_trench_cyclopean_pylon", "dead_mans_cove", "descend into cyclopean trench", "surface to smuggler's cove")
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

    # 4. Register Ankh-Morpork Cargo-Barge Route & Weather Deck
    ankh_deck = find_room_by_key("ankh_barge_deck")
    if not ankh_deck:
        ankh_deck = create_object(Room, key='The Cargo-Barge "Pride of the Ankh" - Weather Deck', tags=[TAG_WORLD])
        ankh_deck.tags.add("ankh_barge_deck", category="room_key")
        ankh_deck.tags.add("ankh_morpork", category="zone")
        ankh_deck.db.room_key = "ankh_barge_deck"
        ankh_deck.db.desc = (
            "You stand upon the rough timber deck of the cargo barge. "
            "A small charcoal stove sizzles with mysterious meat pies, and the sluggish, "
            "nutrient-rich waters of the River Ankh lap sluggishly against the hull."
        )
        ankh_deck.db.zone = "River Ankh"
        ankh_deck.db.terrain = "water_swim"
        ankh_deck.db.coords = (10, 20, 0)
        report["rooms_created"] += 1

    register_ankh_ferry_routes()
    report["ferry_routes_added"].append('The Cargo-Barge "Pride of the Ankh" (south_docks <-> praxis_harbor <-> ankh_wharf)')

    return report
