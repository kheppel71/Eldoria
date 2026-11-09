"""
Bulk World Ingestion Engine — Part 4: The Outer Planes & Ancient Frontiers

Expands Eldoria with an additional 120 rooms across 4 high-tier adventure realms:
1. The Steampunk Subterranean City of Cogsmith (Gnomish Tinker Capital) [Level 10-16]
2. The Glacial Stronghold of Jötunheim (Nordic Frost Titans) [Level 18-25]
3. The Pirate Haven of Port Tortuga & Buccaneer Reef (High Seas Outlaws) [Level 8-14]
4. The Iron City of Dis in the Nine Hells of Baator (Infernal Planes) [Level 22-28+]

Features:
- New 'Black Skull Corsair Frigate' maritime pirate route
- 100% GMCP Room.Info automapper telemetry
- Fixed danger ratings, full Nightmare LPmud combat sheets, and infernal relics
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
# ZONE 14: COGSMITH STEAMPUNK METROPOLIS [Level 10-16, 30 Rooms]
# =============================================================================

def build_zone_clockwork():
    return {
        "zone_key": "clockwork_city",
        "zone_name": "The Steampunk Metropolis of Cogsmith",
        "default_terrain": "city",
        "base_coords": (10, -10, -20),
        "rooms": {
            "brass_tram_station": {
                "name": "Central Steam-Tram Terminal",
                "desc": "Whistles scream and steam billows from brass locomotives arriving at polished granite platforms. Gigantic interlocking bronze cogs the size of houses turn rhythmically along the ceiling, driving the city's pneumatic systems.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "gyro_square", "alias": "n"}},
                "npcs": [{"name": "Clockwork Rail Guard", "desc": "A mechanical automaton of polished brass with an internal combustion engine and a steam rifle.", "level": 11, "role": "warrior"}]
            },
            "gyro_square": {
                "name": "The Great Gyroscope Plaza",
                "desc": "In the center of the plaza spins the Great Gyroscope, a hundred-foot bronze orrery that measures geological pressure and tectonic balance. Gas-lit street lamps illuminate busy gnomish inventors and dwarven mechanists.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "brass_tram_station", "alias": "s"}, "north": {"dest_id": "mechanist_academy", "alias": "n"}, "east": {"dest_id": "tinker_bazaar", "alias": "e"}, "west": {"dest_id": "foundry_district", "alias": "w"}},
                "npcs": [{"name": "Gnomish Master Tinker", "desc": "An eccentric gnome with thick magnifying goggles holding an oily brass wrench.", "level": 10, "role": "civilian"}]
            },
            "tinker_bazaar": {
                "name": "The Pneumatic Tinker Bazaar",
                "desc": "Stalls crammed with copper pressure gauges, spring-loaded lockpicks, pocket orreries, and miniature mechanical songbirds.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "gyro_square", "alias": "w"}, "east": {"dest_id": "alchemical_fuel_works", "alias": "e"}},
                "items": [{"name": "Spring-Loaded Brass Lockpick", "desc": "An automated mechanical pick that vibrates to align lock tumblers."}]
            },
            "alchemical_fuel_works": {
                "name": "Alchemical Volatile Fuel Refinery",
                "desc": "Pressurized glass tubes siphon amber naphtha and volatile liquid coal into copper storage canisters under constant valve monitoring.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "tinker_bazaar", "alias": "w"}},
                "items": [{"name": "Flask of Pressurized Steam Oil", "desc": "Superheated lubricant capable of igniting when exposed to flame."}]
            },
            "foundry_district": {
                "name": "The High Foundry Smelting Arc",
                "desc": "Automated conveyor belts dump pulverized tin, zinc, and copper into titanic blast furnaces. Rivers of molten bronze glow in floor channels.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "gyro_square", "alias": "e"}, "west": {"dest_id": "automaton_assembly", "alias": "w"}},
                "npcs": [{"name": "Smelting Golem", "desc": "A hulking iron construct with a furnace in its chest that vents coal smoke.", "level": 13, "role": "warrior"}]
            },
            "automaton_assembly": {
                "name": "The Clockwork Assembly Plant",
                "desc": "Pneumatic arms and precision hydraulic presses assemble mechanical limbs and clockwork torsos on moving brass assembly tracks.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "foundry_district", "alias": "e"}},
                "npcs": [{"name": "Automaton Assembly Drone", "desc": "A four-armed mechanical worker equipped with soldering torches.", "level": 12, "role": "warrior"}]
            },
            "mechanist_academy": {
                "name": "The Grand Academy of Horology",
                "desc": "Soaring lecture halls where scholars study advanced mechanics, steam thermodynamics, and artificial clockwork intelligence.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "gyro_square", "alias": "s"}, "north": {"dest_id": "chronos_observatory", "alias": "n"}},
                "npcs": [{"name": "Professor Cogsworth", "desc": "A senior academic in velvet robes whose left arm is a fine mechanical brass prosthesis.", "level": 13, "role": "mage"}]
            },
            "chronos_observatory": {
                "name": "The Chronos Clockwork Apex",
                "desc": "High inside the city's master dome sits the Master Clock that regulates time throughout the subterranean continent. Grand Mechanist Gearloose oversees the giant pendulum.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "mechanist_academy", "alias": "s"}, "down": {"dest_id": "boiler_core_chasm", "alias": "d"}},
                "npcs": [{"name": "Grand Mechanist Gearloose", "desc": "The supreme master of clockwork science, clad in steam-powered exoskeletal battle armor.", "level": 16, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Chronos Pocketwatch of Celerity", "desc": "A jewel-encrusted mechanical watch that hastens combat balance recovery."}]
            },
            "boiler_core_chasm": {
                "name": "The Great Geothermal Boiler Core",
                "desc": "A subterranean volcanic fissure harnessed by hundreds of copper pressure pipes. The heat and thunderous roar of escaping steam are deafening.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "chronos_observatory", "alias": "u"}},
                "npcs": [{"name": "Overheated Steam Fiend", "desc": "An elemental formed of superheated scalding vapor and rattling iron cogs.", "level": 14, "role": "warrior"}]
            },
            "pneumatic_tube_hub": {
                "name": "Pneumatic Dispatch Hub",
                "desc": "Brass message cylinders shoot through glass vacuum tubes that spiderweb across the city ceilings.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "brass_tram_station", "alias": "w"}}
            },
            "clockwork_aviary": {
                "name": "The Mechanical Aviary",
                "desc": "Mechanical birds with feathers of beaten brass singing synthetic songs from perches of copper wire.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "tinker_bazaar", "alias": "n"}}
            },
            "steam_pipe_catwalks": {
                "name": "Overhead Steam Pipe Catwalks",
                "desc": "Narrow iron grating walkways suspended over boiling drainage canals.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "foundry_district", "alias": "d"}}
            },
            "geartrain_hall": {
                "name": "The Mammoth Geartrain Corridor",
                "desc": "Massive beveled gears meshing in endless motion, grinding with ground limestone.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "boiler_core_chasm", "alias": "e"}}
            },
            "watchmakers_shop": {
                "name": "The Chronometer Shop",
                "desc": "Wall-to-wall pendulum clocks, marine chronometers, and miniature music boxes ticking in discordance.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "tinker_bazaar", "alias": "s"}}
            },
            "dynamo_gallery": {
                "name": "The Electrical Magneto Dynamo",
                "desc": "Copper coils spinning within giant horseshoe magnets, throwing blue electrical sparks.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "foundry_district", "alias": "n"}}
            },
            "valve_manifold_room": {
                "name": "Pressure Manifold Chamber",
                "desc": "Dozens of red wheel valves releasing excess steam pressure safely through chimney flues.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "boiler_core_chasm", "alias": "w"}}
            },
            "tinker_guild_taproom": {
                "name": "The Whistling Sprocket Tavern",
                "desc": "A subterranean taproom where inventors drink pressurized steam-lager served by mechanical automaton bartenders.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "gyro_square", "alias": "e"}},
                "items": [{"name": "Mug of Pressurized Cog-Lager", "desc": "A cold, effervescent ale tapped directly from copper pipes."}]
            },
            "patent_office_vault": {
                "name": "The Imperial Patent Archive",
                "desc": "Steel filing cabinets containing blueprints for flying ornithopters, submarines, and repeating crossbows.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "mechanist_academy", "alias": "w"}}
            },
            "steam_exhaust_roof": {
                "name": "The Foggy Roof Terrace",
                "desc": "The upper exterior of the brass dome where warm steam vents create a permanent mist.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "chronos_observatory", "alias": "d"}}
            },
            "battery_storage_cells": {
                "name": "Galvanic Leyden Battery Banks",
                "desc": "Glass jars filled with acid and zinc plates storing electrical charge.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "dynamo_gallery", "alias": "e"}}
            },
            "scrap_recycling_pit": {
                "name": "The Brass Scrap Crucible",
                "desc": "A deep stone pit where broken gears and bent copper pipes are melted down for recasting.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "automaton_assembly", "alias": "s"}}
            },
            "hydraulic_lift_shaft": {
                "name": "The Monumental Piston Lift",
                "desc": "A hydraulic brass elevator cage capable of lifting entire steam wagons to the surface.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "gyro_square", "alias": "u"}}
            },
            "prosthetics_clinic": {
                "name": "Bionic Prosthetics Dispensary",
                "desc": "Articulated mechanical hands, spring-loaded legs, and ocular brass monocles on velvet displays.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "watchmakers_shop", "alias": "n"}}
            },
            "coal_bunkers": {
                "name": "The High Coal Bunkers",
                "desc": "Mountains of black anthracite coal waiting to feed the city's boilers.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "foundry_district", "alias": "s"}}
            },
            "pneumatic_tube_switch": {
                "name": "Dispatch Switchboard",
                "desc": "A maze of routing levers directing message canisters throughout the city.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "pneumatic_tube_hub", "alias": "s"}}
            },
            "alchemical_testing_range": {
                "name": "Steam Cannon Ballistics Range",
                "desc": "Reinforced steel targets pitted by high-velocity pneumatic lead balls.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "alchemical_fuel_works", "alias": "n"}}
            },
            "clockwork_watchtower": {
                "name": "The Internal City Watchtower",
                "desc": "A slender spire overseeing the entire underground cavern with searchlights.",
                "terrain": "city",
                "exits": {"down": {"dest_id": "gyro_square", "alias": "d"}}
            },
            "oil_refinery_drain": {
                "name": "The Lubricant Drainage Sump",
                "desc": "Dark pools of grease and machine oil draining into filters.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "scrap_recycling_pit", "alias": "w"}}
            },
            "air_compressor_vault": {
                "name": "Main Air Compressor Hall",
                "desc": "Steam pistons compressing atmosphere to four hundred pounds per square inch.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "valve_manifold_room", "alias": "e"}}
            },
            "subterranean_rail_head": {
                "name": "The Western Rail Siding",
                "desc": "Where ore trains depart into the dark mountain shafts.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "brass_tram_station", "alias": "e"}}
            }
        }
    }


# =============================================================================
# ZONE 15: JOTUNHEIM FROST TITAN STRONGHOLD [Level 18-25, 30 Rooms]
# =============================================================================

def build_zone_jotunheim():
    return {
        "zone_key": "jotunheim_frost",
        "zone_name": "The Glacial Stronghold of Jötunheim",
        "default_terrain": "mountain",
        "base_coords": (10, 45, 20),
        "rooms": {
            "glacial_portal_pass": {
                "name": "The Ice-Choked Mountain Pass",
                "desc": "A howling blizzard whips horizontal snow across blue ice glaciers. Jagged peaks of frozen ice pierce the grey clouds like dragon fangs.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "ice_bridge_abyss", "alias": "n"}},
                "npcs": [{"name": "Jötun Ice Sentry", "desc": "A sixteen-foot frost giant with a beard of icicles wielding a frozen tree trunk as a club.", "level": 18, "role": "warrior"}]
            },
            "ice_bridge_abyss": {
                "name": "Bridge of the Blue Glacier",
                "desc": "A natural arch of solid glacial ice spanning a bottomless crevasse. Far below, ancient woolly mammoths lie frozen inside clear blue ice walls.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "glacial_portal_pass", "alias": "s"}, "north": {"dest_id": "frost_gates_thrym", "alias": "n"}},
                "npcs": [{"name": "Glacial Frost Wolf", "desc": "A white wolf as large as a horse with eyes of pale sapphire.", "level": 17, "role": "warrior"}]
            },
            "frost_gates_thrym": {
                "name": "The Mammoths' Gate of Jötunheim",
                "desc": "Two colossal mammoth skulls thirty feet across flank the entry archway. Tusks of mammoth ivory curve outward to form defensive spikes.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "ice_bridge_abyss", "alias": "s"}, "north": {"dest_id": "great_mead_hall_ice", "alias": "n"}}
            },
            "great_mead_hall_ice": {
                "name": "The Feast Hall of Jarl Thrym",
                "desc": "A hall carved from living blue glacier ice. Piles of polar bear pelts cover massive stone benches. Braziers burn with magical blue rimefire that radiates freezing chill rather than heat.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "frost_gates_thrym", "alias": "s"}, "north": {"dest_id": "throne_frost_king", "alias": "n"}, "east": {"dest_id": "rimefire_smithy", "alias": "e"}, "west": {"dest_id": "mammoth_stables", "alias": "w"}},
                "npcs": [{"name": "Frost Titan Berserker", "desc": "A giant warrior tattooed with ancient Nordic runes of freezing slaughter.", "level": 20, "role": "warrior"}]
            },
            "throne_frost_king": {
                "name": "The Throne of the Glacial King",
                "desc": "Carved from an unbroken iceberg of permafrost sits the throne of Jarl Thrym. Frost giants and winter wolves bow before the king of winter.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "great_mead_hall_ice", "alias": "s"}, "up": {"dest_id": "blizzard_peak", "alias": "u"}},
                "npcs": [{"name": "Jarl Thrym the Frost King", "desc": "The twenty-two foot sovereign of the frost titans, wearing a crown of glacial spikes and wielding the Frost-Hammer.", "level": 25, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Frost-Hammer of the Glacier King", "desc": "A colossal warhammer encased in eternal rime that freezes blood on contact."}]
            },
            "blizzard_peak": {
                "name": "Pinnacle of the Eternal Blizzard",
                "desc": "The highest peak of Jötunheim where the Winter Gale is born. The wind roars with deafening primeval power.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "throne_frost_king", "alias": "d"}},
                "items": [{"name": "Shard of the Glacial Heart", "desc": "A pulsating blue ice gem that never melts and emits winter auras."}]
            },
            "rimefire_smithy": {
                "name": "The Rimefire Armory",
                "desc": "Anvils of frozen meteoric iron where frost giant smiths hammer weapons tempered in liquid nitrogen.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "great_mead_hall_ice", "alias": "w"}},
                "npcs": [{"name": "Rimefire Smith Hrym", "desc": "A giant blacksmith shaping ice-tempered broadaxes.", "level": 21, "role": "warrior"}],
                "items": [{"name": "Glacial Greatsword of Jötunheim", "desc": "A massive two-handed sword with an edge of razor-sharp blue permafrost."}]
            },
            "mammoth_stables": {
                "name": "The Great Mammoth Stables",
                "desc": "Immense caverns where war mammoths covered in shaggy wool are harnessed with armored howdahs.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "great_mead_hall_ice", "alias": "e"}},
                "npcs": [{"name": "Armored War Mammoth", "desc": "A gargantuan prehistoric pachyderm with steel-clad tusks.", "level": 19, "role": "warrior"}]
            },
            "frozen_lake": {
                "name": "The Mirrored Black Ice Lake",
                "desc": "A smooth expanse of black ice so thick a giant army could march across it without a crack.",
                "terrain": "mountain",
                "exits": {"east": {"dest_id": "glacial_portal_pass", "alias": "e"}, "north": {"dest_id": "ice_caverns_deep", "alias": "n"}}
            },
            "ice_caverns_deep": {
                "name": "Deep Crevasse Ice Cavern",
                "desc": "Walls of translucent sapphire ice glowing with natural phosphorescence.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "frozen_lake", "alias": "s"}, "north": {"dest_id": "yeti_den", "alias": "n"}}
            },
            "yeti_den": {
                "name": "Lair of the Snow Yeti",
                "desc": "Piles of frozen bones in a sheltered snow cave.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "ice_caverns_deep", "alias": "s"}},
                "npcs": [{"name": "Snow Yeti Stalker", "desc": "A shaggy white ape-beast with cruel curved claws.", "level": 18, "role": "warrior"}]
            },
            "avalanche_chute": {
                "name": "The Steep Avalanche Chute",
                "desc": "A treacherous 45-degree slope of packed snow prone to sudden slides.",
                "terrain": "mountain",
                "exits": {"down": {"dest_id": "ice_bridge_abyss", "alias": "d"}}
            },
            "trophy_hall_frost": {
                "name": "The Titan's Trophy Gallery",
                "desc": "Skulls of white dragons, whale ribs, and shattered dwarven war machines.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "throne_frost_king", "alias": "w"}}
            },
            "shrine_ymir": {
                "name": "Altar of the First Giant Ymir",
                "desc": "A rough monolith carved from black rime-stone dedicated to the progenitor of frost giants.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "great_mead_hall_ice", "alias": "n"}}
            },
            "frost_wolf_kennels": {
                "name": "The Winter Wolf Pens",
                "desc": "Iron grates keeping hungry pack wolves from devouring the mead supplies.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "mammoth_stables", "alias": "s"}}
            },
            "ice_stalactite_hall": {
                "name": "Gallery of the Dagger Icicles",
                "desc": "Tens of thousands of razor icicles hanging overhead like suspended swords.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "ice_caverns_deep", "alias": "e"}}
            },
            "polar_bear_den": {
                "name": "The White Bear Cave",
                "desc": "A massive polar bear mother guarding two shaggy cubs.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "frozen_lake", "alias": "w"}}
            },
            "rimefire_well": {
                "name": "The Well of Freezing Flames",
                "desc": "A fountain of blue fire that freezes anything tossed into its depths.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "rimefire_smithy", "alias": "n"}}
            },
            "glacier_crevasse_bottom": {
                "name": "Floor of the Glacier Crevasse",
                "desc": "Dark blue ice crushing together under millions of tons of pressure.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "ice_bridge_abyss", "alias": "u"}}
            },
            "mead_vat_jotunheim": {
                "name": "The Giant's Mead Vats",
                "desc": "Wooden vats holding thousands of gallons of frozen winterbrew.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "rimefire_smithy", "alias": "s"}}
            },
            "aurora_ledge_jotun": {
                "name": "The Northern Lights Ledge",
                "desc": "High cliff edge bathed in dancing green aurora light.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "blizzard_peak", "alias": "s"}}
            },
            "white_dragon_eyrie": {
                "name": "The White Dragon's Nesting Eyrie",
                "desc": "Piles of frozen treasure hoards nestled within windblown snowdrifts.",
                "terrain": "mountain",
                "exits": {"east": {"dest_id": "blizzard_peak", "alias": "e"}},
                "npcs": [{"name": "Elder White Dragon", "desc": "A savage white wyrm whose breath freezes flesh into brittle crystal.", "level": 23, "role": "boss", "danger_tier": "boss"}]
            },
            "mammoth_burial_ground": {
                "name": "The Mammoth Boneyard",
                "desc": "Bleached ribcages forming Gothic arches across the snow.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "mammoth_stables", "alias": "n"}}
            },
            "frost_guard_parapet": {
                "name": "Parapet of the Blue Towers",
                "desc": "Ice ramparts where boulders of blue glacier ice are stacked for hurling.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "frost_gates_thrym", "alias": "w"}}
            },
            "subglacial_stream": {
                "name": "The Subglacial Waterway",
                "desc": "Melting glacial water rushing beneath an ice ceiling.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "frozen_lake", "alias": "n"}}
            },
            "runic_pillar_hall": {
                "name": "The Hall of Rune Stones",
                "desc": "Pillars engraved with tales of the Ragnarök battle.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "shrine_ymir", "alias": "s"}}
            },
            "rime_witch_hovel": {
                "name": "Hovel of the Frost Seer",
                "desc": "An old giant crone reading prophecies in shattered ice shards.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "trophy_hall_frost", "alias": "e"}}
            },
            "frozen_catacomb_giants": {
                "name": "Sepulchers of the Frost Kings",
                "desc": "Giants entombed inside blocks of transparent permafrost.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "throne_frost_king", "alias": "d"}}
            },
            "wind_tunnel_screaming": {
                "name": "The Screaming Gale Tunnel",
                "desc": "Natural wind tunnel whistling in deafening musical tones.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "avalanche_chute", "alias": "n"}}
            },
            "terminus_glacier": {
                "name": "The Glacier Terminus Moraine",
                "desc": "Where the massive glacier grinds against bedrock, spewing pulverized grey gravel.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "glacial_portal_pass", "alias": "s"}}
            }
        }
    }


# =============================================================================
# ZONE 16: PORT TORTUGA & BUCCANEER REEF [Level 8-14, 30 Rooms]
# =============================================================================

def build_zone_tortuga():
    return {
        "zone_key": "tortuga_haven",
        "zone_name": "The Pirate Haven of Port Tortuga",
        "default_terrain": "city",
        "base_coords": (-45, 10, 0),
        "rooms": {
            "tortuga_docks": {
                "name": "The Weathered Wharves of Tortuga",
                "desc": "Creaking wooden piers smelling of rum, stale tobacco, and pitch. Jolly Roger flags flutter from the topmasts of corsair sloops and captured merchant caravels rocking in the bay.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "buccaneer_boardwalk", "alias": "n"}},
                "npcs": [{"name": "One-Eyed Buccaneer", "desc": "A swaggering pirate with an eye patch, silver hoop earring, and a curved cutlass.", "level": 8, "role": "warrior"}]
            },
            "buccaneer_boardwalk": {
                "name": "Buccaneer Strip",
                "desc": "A chaotic wooden boardwalk elevated above the sandy beach on timber stilts. Drunken privateers brawl outside tavernas and gambling dens.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "tortuga_docks", "alias": "s"}, "north": {"dest_id": "skull_rock_cavern", "alias": "n"}, "east": {"dest_id": "black_flag_tavern", "alias": "e"}, "west": {"dest_id": "shipwright_slipway", "alias": "w"}},
                "npcs": [{"name": "Tortuga Cutpurse", "desc": "A nimble rogue picking pockets in the crowds of sailors.", "level": 8, "role": "rogue"}]
            },
            "black_flag_tavern": {
                "name": "The Black Flag Brewhouse",
                "desc": "Raucous accordion shanties, spilling flagons of molasses rum, and smoke from black tobacco. Darts thud into a dartboard painted with the King's face.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "buccaneer_boardwalk", "alias": "w"}},
                "npcs": [{"name": "Barmaid Black-Eyed Sal", "desc": "A tough barmaid carrying six tankards of dark grog at once.", "level": 7, "role": "civilian"}],
                "items": [{"name": "Bottle of 151-Proof Tortuga Rum", "desc": "Spiced blackstrap rum that burns like fire down the throat."}]
            },
            "shipwright_slipway": {
                "name": "The Smuggler's Careenage",
                "desc": "Privateer hulls tilted on their sides for scraping barnacles and recaulking timber seams with boiling pine pitch.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "buccaneer_boardwalk", "alias": "e"}},
                "items": [{"name": "Caulking Mallet & Oakum", "desc": "Tools used to hammer waterproof pitch hemp between ship planks."}]
            },
            "skull_rock_cavern": {
                "name": "The Arch of Dead Man's Skull",
                "desc": "A natural sea arch carved by tides into the grim shape of a human skull. Beyond lies the fortress compound of the Pirate Council.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "buccaneer_boardwalk", "alias": "s"}, "north": {"dest_id": "council_of_captains", "alias": "n"}}
            },
            "council_of_captains": {
                "name": "The High Council of Captains",
                "desc": "A grand fortress room draped in captured naval flags. In the center stands a round table of Spanish mahogany where the Pirate Lords divide their plunder.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "skull_rock_cavern", "alias": "s"}, "down": {"dest_id": "tortuga_vault", "alias": "d"}},
                "npcs": [{"name": "Dread Captain Morgan Blood-Eye", "desc": "The infamous pirate king of Tortuga, wearing a crimson frock coat and twin flintlock pistols.", "level": 14, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Cutlass of Captain Blood-Eye", "desc": "A razor-sharp boarding cutlass engraved with grinning skull crests."}]
            },
            "tortuga_vault": {
                "name": "The Brotherhood's Plunder Cave",
                "desc": "Iron-banded sea chests filled with emerald jewelry, silver bars, and barrels of stolen Dutch tobacco.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "council_of_captains", "alias": "u"}},
                "items": [{"name": "Sack of Spanish Silver Pieces of Eight", "desc": "Clipped silver coins stamped in ancient Caribbean mints."}]
            },
            "smugglers_shantytown": {
                "name": "The Stilt Village Shantytown",
                "desc": "Ramshackle driftwood huts raised above the tidal lagoon on cedar pilings.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "buccaneer_boardwalk", "alias": "w"}}
            },
            "siren_reef_shallow": {
                "name": "The Bleached Coral Reefs",
                "desc": "Jagged coral heads lurking just inches beneath the turquoise surf, notorious for ripping ship bottoms open.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "tortuga_docks", "alias": "e"}}
            },
            "parrot_jungle": {
                "name": "The Wild Macaw Jungle",
                "desc": "Dense tropical palm forest screeching with wild red and yellow macaws.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "smugglers_shantytown", "alias": "n"}}
            },
            "cannon_battery_tortuga": {
                "name": "The Buccaneer Shore Battery",
                "desc": "Heavy naval carronades commanding the narrow harbor entrance channel.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "skull_rock_cavern", "alias": "s"}}
            },
            "rum_distillery_secret": {
                "name": "The Secret Cane Rum Still",
                "desc": "Copper pot stills bubbling with fermented molasses wash.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "black_flag_tavern", "alias": "n"}}
            },
            "gallows_point_tortuga": {
                "name": "The Gibbet at Gallows Point",
                "desc": "An iron cage hanging from a cliff overlooking the ocean where mutineers are left as a warning.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "tortuga_docks", "alias": "w"}}
            },
            "dice_den_blind": {
                "name": "The Loaded Dice Den",
                "desc": "A smoky backroom where privateers wager captured pearls on card games.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "black_flag_tavern", "alias": "s"}}
            },
            "buccaneer_armorer": {
                "name": "The Boarding Pike Armory",
                "desc": "Cutlasses, boarding axes, grappling hooks, and belaying pins.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "shipwright_slipway", "alias": "n"}}
            },
            "sailmakers_loft_tortuga": {
                "name": "The Sailmaker's Drift",
                "desc": "Tattered black and white canvas sails laid out for patching.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "shipwright_slipway", "alias": "s"}}
            },
            "hidden_lagoon_cove": {
                "name": "The Smuggler's Secret Lagoon",
                "desc": "A sheltered cove hidden behind sheer jungle cliffs where longboats unload contraband.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "parrot_jungle", "alias": "n"}}
            },
            "tortuga_market_square": {
                "name": "The Plunder Exchange",
                "desc": "Stalls where stolen silks, tea, and spices are sold without questions.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "buccaneer_boardwalk", "alias": "w"}}
            },
            "locksmith_cage": {
                "name": "The Padlock Smithy",
                "desc": "Skeleton keys and pick sets forged for opening merchant strongboxes.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "tortuga_market_square", "alias": "s"}}
            },
            "powder_store_tortuga": {
                "name": "The Magazine at Sea Bluff",
                "desc": "Barrels of gunpowder kept dry in a limestone cave.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "cannon_battery_tortuga", "alias": "e"}}
            },
            "sea_dog_graveyard": {
                "name": "Dead Men's Sand Spit",
                "desc": "Wooden cross markers stuck in the beach sand, washed over by the tide.",
                "terrain": "field",
                "exits": {"south": {"dest_id": "gallows_point_tortuga", "alias": "s"}}
            },
            "shipwreck_buccaneer": {
                "name": "Wreck of the Spanish Frigate",
                "desc": "A burned-out caravel hull half-buried in the white sand.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "sea_dog_graveyard", "alias": "n"}}
            },
            "tallow_candle_shop": {
                "name": "Whale Tallow Chandler",
                "desc": "Pungent tallow candles and oil for ship lanterns.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "tortuga_market_square", "alias": "e"}}
            },
            "palm_grove_trail": {
                "name": "The Coconut Palm Trail",
                "desc": "A sandy trail meandering through leaning palms.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "parrot_jungle", "alias": "s"}}
            },
            "freshwater_spring_tortuga": {
                "name": "Sweetwater Waterfall",
                "desc": "A cascade of cool mountain water where pirates refill their water casks.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "palm_grove_trail", "alias": "n"}}
            },
            "anchorage_outer": {
                "name": "Outer Roads Anchorage",
                "desc": "Deep blue water where warships anchor beyond cannon range.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "tortuga_docks", "alias": "w"}}
            },
            "pirate_brig_cells": {
                "name": "The Council Brig",
                "desc": "Damp holding cells for pirates who broke the buccaneer code.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "council_of_captains", "alias": "n"}}
            },
            "crow_nest_lookout": {
                "name": "The High Lookout Mast",
                "desc": "A lookout platform strapped to a dead palm scanning for naval patrol ships.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "cannon_battery_tortuga", "alias": "d"}}
            },
            "rum_tasting_cellar": {
                "name": "The Smuggler's Oak Cellar",
                "desc": "Dusty bottles of private reserve vintage rum.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "rum_distillery_secret", "alias": "d"}}
            },
            "buccaneer_beach_sand": {
                "name": "The White Sand Strand",
                "desc": "Warm surf washing ashore on shell-strewn sand.",
                "terrain": "field",
                "exits": {"south": {"dest_id": "siren_reef_shallow", "alias": "s"}}
            }
        }
    }


# =============================================================================
# ZONE 17: NINE HELLS OF BAATOR - CITY OF DIS [Level 22-28+, 30 Rooms]
# =============================================================================

def build_zone_baator():
    return {
        "zone_key": "baator_hells",
        "zone_name": "The Iron City of Dis in the Nine Hells",
        "default_terrain": "catacombs",
        "base_coords": (0, -50, -40),
        "rooms": {
            "infernal_threshold": {
                "name": "The Brimstone Portal to Dis",
                "desc": "A swirling gate of black hellfire set into a wall of red-hot iron. The air smells of sulfur, molten lead, and burning flesh. A blood-red sky glows with hellfire clouds.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "iron_boulevard", "alias": "n"}},
                "npcs": [{"name": "Barbed Devil Sentry", "desc": "A fiend bristling with razor-sharp quills holding an iron spear.", "level": 22, "role": "warrior"}]
            },
            "iron_boulevard": {
                "name": "The Street of Molten Lead",
                "desc": "The road itself is paved with iron plates that blister leather boots. Gutters flow with sluggish streams of boiling lead, illuminating the jagged iron spires of Dis.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "infernal_threshold", "alias": "s"}, "north": {"dest_id": "iron_tower_dispater", "alias": "n"}, "east": {"dest_id": "contract_hall", "alias": "e"}, "west": {"dest_id": "chain_devil_ward", "alias": "w"}},
                "npcs": [{"name": "Damned Soul", "desc": "A wretched spirit weeping tears of molten ash, enslaved to haul iron bricks.", "level": 20, "role": "civilian"}]
            },
            "contract_hall": {
                "name": "The Hall of Infernal Pacts",
                "desc": "Vast archives of burning parchment signed in blood. Devilish advocates and notary fiends draft contracts binding mortal souls to eternal torment.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "iron_boulevard", "alias": "w"}},
                "npcs": [{"name": "Infernal Notary Belial", "desc": "A horned devil in immaculate black silk holding a blood-quill and golden seal.", "level": 23, "role": "mage"}],
                "items": [{"name": "Infernal Soul Contract", "desc": "A parchment written in burning infernal script offering dark power for a soul."}]
            },
            "chain_devil_ward": {
                "name": "The Bastion of Rattle and Chain",
                "desc": "Thousands of animated, barbed iron chains slither across the walls like serpents, hanging meat hooks and flaying knives.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "iron_boulevard", "alias": "e"}},
                "npcs": [{"name": "Chain Devil Kyton", "desc": "A terrifying fiend enveloped in razor chains that lash out with telepathic malice.", "level": 24, "role": "warrior"}]
            },
            "iron_tower_dispater": {
                "name": "The Great Iron Tower of Dispater",
                "desc": "A colossal monolith of green-veined iron soaring miles into the smoky Baator sky. Runes of paranoia and absolute control are stamped into every iron plate.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "iron_boulevard", "alias": "s"}, "up": {"dest_id": "throne_dispater", "alias": "u"}},
                "npcs": [{"name": "Pit Fiend Commander", "desc": "A towering winged arch-devil with dragon wings, a tail of hellfire, and a fiery mace.", "level": 26, "role": "boss", "danger_tier": "boss"}]
            },
            "throne_dispater": {
                "name": "The Obsidian Throne of Lord Dispater",
                "desc": "Surrounded by mirror wards that reflect every corner of the Multiverse, the Arch-Devil Dispater rules the second layer of Hell with cold, calculating intellect.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "iron_tower_dispater", "alias": "d"}},
                "npcs": [{"name": "Arch-Devil Dispater", "desc": "The supreme master of the Iron City, his skin like polished grey metal, wielding the Rod of Iron Dominion.", "level": 28, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Infernal Rod of Dispater's Iron", "desc": "A supreme infernal relic capable of shattering physical and magical barriers with a touch."}]
            },
            "lake_of_boiling_lead": {
                "name": "The Caldera of Boiling Lead",
                "desc": "A grey, sluggish lake bubbling with superheated heavy metal. Slag crusts float like islands.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "infernal_threshold", "alias": "w"}}
            },
            "torture_spire_baator": {
                "name": "The Flaying Spire",
                "desc": "Echoing with the screams of souls being purified through millennia of agony.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "chain_devil_ward", "alias": "n"}}
            },
            "hellfire_foundry": {
                "name": "The Hellfire Engine Foundry",
                "desc": "Demonic engineers forging war machines of iron and trapped souls for the Blood War.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "contract_hall", "alias": "e"}}
            },
            "gargoyle_parapet_dis": {
                "name": "Parapet of the Iron Gargoyles",
                "desc": "Heavy iron gargoyles spitting black oil down upon the streets.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "iron_tower_dispater", "alias": "d"}}
            },
            "sulfur_quarry_baator": {
                "name": "The Brimstone Quarry",
                "desc": "Damned souls mining yellow sulfur crystals with broken bare hands.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "lake_of_boiling_lead", "alias": "s"}},
                "items": [{"name": "Sulfur-Encrusted Brimstone Crystal", "desc": "A jagged yellow crystal radiating suffocating heat and volatile explosive energy."}]
            },
            "bone_bridge_hell": {
                "name": "The Bridge of Damned Skulls",
                "desc": "A bridge formed of mortarless compressed human skulls spanning a trench of fire.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "iron_boulevard", "alias": "e"}}
            },
            "armory_infernal": {
                "name": "Baator Armory of Spiked Iron",
                "desc": "Greatswords forged from damned iron that inflict wounds that never clot.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "hellfire_foundry", "alias": "n"}},
                "items": [{"name": "Hellfire Spiked Shield", "desc": "A heavy iron tower shield bristling with serrated spikes that burn with unholy flames."}]
            },
            "paranoia_vault": {
                "name": "Dispater's Mirror Vault",
                "desc": "Mirrors that reveal the true thoughts and betrayals of anyone who gazes within.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "throne_dispater", "alias": "w"}}
            },
            "blood_war_staging": {
                "name": "The Blood War Muster Yard",
                "desc": "Legions of horned devils, erinyes, and bearded devils marching in iron discipline.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "hellfire_foundry", "alias": "s"}}
            },
            "erinyes_aerie": {
                "name": "The High Aerie of the Erinyes",
                "desc": "Winged fallen angel furies sharpening bows of unholy vengeance.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "gargoyle_parapet_dis", "alias": "d"}}
            },
            "soul_cage_depot": {
                "name": "The Soul Larva Warehouses",
                "desc": "Cages of writhing soul larvae currency stacked in cold storage.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "contract_hall", "alias": "n"}}
            },
            "styx_tributary": {
                "name": "Tributary of the River Styx",
                "desc": "Black, oily water that washes away all memory and identity from those who touch it.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "sulfur_quarry_baator", "alias": "s"}}
            },
            "charon_ferry_dock": {
                "name": "The Styx Skiff Landing",
                "desc": "A solitary wooden landing pole where skeletal ferrymen dock black coracles.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "styx_tributary", "alias": "e"}}
            },
            "ashen_gardens": {
                "name": "The Garden of Crystallized Ash",
                "desc": "Petrified flowers of grey volcanic cinder that crumble at the slightest touch.",
                "terrain": "forest",
                "exits": {"west": {"dest_id": "iron_boulevard", "alias": "w"}}
            },
            "iron_watchtower_dis": {
                "name": "The Watchtower of Ever-Burning Eyes",
                "desc": "Iron turrets with braziers of cursed fire scanning the City of Dis.",
                "terrain": "city",
                "exits": {"down": {"dest_id": "iron_boulevard", "alias": "d"}}
            },
            "court_of_the_inquisitor": {
                "name": "Tribunal of Infernal Justice",
                "desc": "Where devils put each other on trial for breaking the letter of the law.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "contract_hall", "alias": "s"}}
            },
            "brazen_bull_chamber": {
                "name": "The Brazen Bull Kiln",
                "desc": "A hollow brass bull heated red-hot from below with hellfire coals.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "torture_spire_baator", "alias": "n"}}
            },
            "hell_hound_pens": {
                "name": "The Hellhound Kennels",
                "desc": "Canines of solid brimstone and soot that breathe cones of liquid flame.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "blood_war_staging", "alias": "e"}}
            },
            "obsidian_crypt_baator": {
                "name": "Mausoleum of Fallen Arch-Devils",
                "desc": "Tombs of ancient lords who were demoted and destroyed in the politics of Hell.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "ashen_gardens", "alias": "d"}}
            },
            "furnace_exhaust_roof": {
                "name": "The Iron Flue Parapet",
                "desc": "Chimneys belching black soot into the blood-red firmament.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "iron_tower_dispater", "alias": "d"}}
            },
            "sludge_canal_lead": {
                "name": "The Lead Sluice Overlook",
                "desc": "Where waste lead dumps into the burning abyssal trenches.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "lake_of_boiling_lead", "alias": "n"}}
            },
            "council_pit_fiends": {
                "name": "The War Council of the Nine",
                "desc": "Nine obsidian thrones where generals plan the extermination of demons.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "iron_tower_dispater", "alias": "e"}}
            },
            "infernal_treasury": {
                "name": "Vault of Baatorian Rubies",
                "desc": "Gems solidified from the compressed despair of damned empires.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "throne_dispater", "alias": "d"}}
            },
            "chasm_to_minauros": {
                "name": "The Descent to Minauros",
                "desc": "A slimy, sinking chute leading downward into the third layer of the Nine Hells.",
                "terrain": "marsh",
                "exits": {"up": {"dest_id": "lake_of_boiling_lead", "alias": "u"}}
            }
        }
    }


# =============================================================================
# MARITIME ROUTE: THE BLACK SKULL CORSAIR FRIGATE
# =============================================================================

def register_tortuga_ferry_routes():
    """
    Registers the 7th major maritime route:
    'The Black Skull Corsair Frigate' connecting Dead Man's Cove,
    Smuggler's Lagoon, and Port Tortuga.
    """
    pirate_route = {
        "key": "black_skull_ship",
        "name": "The Black Skull Corsair Frigate",
        "operator": "Quartermaster Flint",
        "operator_title": "First Mate of the Brotherhood",
        "ports": ["dead_mans_cove", "isle_cove", "tortuga_haven_tortuga_docks", "tortuga_docks"],
        "port_names": {
            "dead_mans_cove": "Dead Man's Cove (Smuggler's Coast)",
            "isle_cove": "Smuggler's Lagoon (Isle of Serpents)",
            "tortuga_haven_tortuga_docks": "The Weathered Wharves of Tortuga",
            "tortuga_docks": "The Weathered Wharves of Tortuga"
        },
        "fares": {
            ("dead_mans_cove", "tortuga_haven_tortuga_docks"): 45,   # 4 silver 5 copper
            ("tortuga_haven_tortuga_docks", "dead_mans_cove"): 45,
            ("isle_cove", "tortuga_haven_tortuga_docks"): 35,
            ("tortuga_haven_tortuga_docks", "isle_cove"): 35,
            ("dead_mans_cove", "tortuga_docks"): 45,
            ("tortuga_docks", "dead_mans_cove"): 45,
            ("isle_cove", "tortuga_docks"): 35,
            ("tortuga_docks", "isle_cove"): 35
        },
        "desc": "A menacing black-hulled 24-gun frigate flying a tattered black flag with crimson skull and crossed cutlasses.",
        "deck_key": "black_skull_deck"
    }
    sailing.FERRY_ROUTES["black_skull_ship"] = pirate_route
    return pirate_route


# =============================================================================
# MAIN EXPANSION PART 4 RUNNER
# =============================================================================

def run_bulk_ingestion_part4(clean_existing=True):
    """
    Executes bulk ingestion of Part 4 zones (120 rooms) with:
    - Cogsmith Steampunk Metropolis
    - Jötunheim Frost Titan Stronghold
    - Port Tortuga Buccaneer Haven
    - City of Dis in the Nine Hells
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
        build_zone_clockwork,
        build_zone_jotunheim,
        build_zone_tortuga,
        build_zone_baator
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("clockwork_city", "brass_tram_station", "rail_hub", "board steam tram", "disembark tram"),
        ("jotunheim_frost", "glacial_portal_pass", "chasm_bridge", "cross frozen ravine", "return to bridge"),
        ("baator_hells", "infernal_threshold", "catacombs", "enter hellfire rift", "exit hellfire rift")
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

    # 4. Register Black Skull Frigate Maritime Route & Weather Deck
    frigate_deck = find_room_by_key("black_skull_deck")
    if not frigate_deck:
        frigate_deck = create_object(Room, key="The Black Skull Corsair Frigate - Weather Deck", tags=[TAG_WORLD])
        frigate_deck.tags.add("black_skull_deck", category="room_key")
        frigate_deck.tags.add("tortuga_haven", category="zone")
        frigate_deck.db.room_key = "black_skull_deck"
        frigate_deck.db.desc = (
            "You stand upon the broad pitch-sealed weather deck of the corsair frigate. "
            "A menacing Jolly Roger flag snaps in the ocean gale, and twenty-four bronze carronades "
            "glare outward from open gunports over the rolling waves."
        )
        frigate_deck.db.zone = "Pirate Sea"
        frigate_deck.db.terrain = "city"
        frigate_deck.db.coords = (-35, 10, 0)
        report["rooms_created"] += 1

    register_tortuga_ferry_routes()
    report["ferry_routes_added"].append("The Black Skull Corsair Frigate (dead_mans_cove <-> isle_cove <-> tortuga_docks)")

    return report
