"""
Bulk World Ingestion Engine — Part 8: The "1,500 Rooms Milestone" Super-Expansion

Expands Eldoria with an additional 260 rooms across 4 iconic classic realms:
1. The Temple of Elemental Evil & Elemental Nodes [Level 10-20, 65 Rooms]
2. The Peaceful Shire & Green Dragon Vale (Halfling Burrows) [Level 1-5, 65 Rooms]
3. The Sunken Atlantis Upper Shelf & Coral Gardens [Level 14-22, 65 Rooms]
4. The Seven Silver Heavens of Mount Celestia [Level 20-28, 65 Rooms]

Total Rooms Created in Part 8: 260 Rooms
Cumulative World Total: 1,253 + 260 = 1,513 Rooms!

Features:
- 100% GMCP Room.Info automapper telemetry with relative 3D coordinate graphs
- Fixed danger ratings, full Nightmare LPmud combat sheets, and legendary relics
- Four reciprocal overland, planar, and submarine anchors
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


# =============================================================================
# ZONE 30: THE TEMPLE OF ELEMENTAL EVIL [Level 10-20, 65 Rooms]
# =============================================================================

def build_zone_elemental_evil():
    zone_key = "temple_evil"
    zone_name = "The Temple of Elemental Evil"
    rooms = {}

    rooms["temple_evil_ruined_moathouse"] = {
        "name": "The Moathouse of the Elemental Eye",
        "desc": "A dilapidated stone outpost surrounded by stagnant swamp water. Cracked walls are painted with the dread eye of the Elder Elemental God.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "temple_courtyard_evil", "alias": "n"}},
        "npcs": [{"name": "Gnoll Sentry", "desc": "A hyena-headed marauder clutching a notched battleaxe.", "level": 10, "role": "warrior"}]
    }

    rooms["temple_courtyard_evil"] = {
        "name": "The Courtyard of the Four Elements",
        "desc": "A vast black basalt courtyard where four titanic pillars representing Fire, Water, Earth, and Air burn with unholy magical auras.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "temple_evil_ruined_moathouse", "alias": "s"}, "north": {"dest_id": "greater_temple_chaos", "alias": "n"}, "east": {"dest_id": "fire_node_sanctum", "alias": "e"}, "west": {"dest_id": "water_node_sanctum", "alias": "w"}}
    }

    rooms["greater_temple_chaos"] = {
        "name": "The Greater Sanctuary of Elemental Chaos",
        "desc": "An unholy cathedral of black stone where High Priest Hedrack leads chanting cultists before a colossal bronze idol of the Triad.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "temple_courtyard_evil", "alias": "s"}, "north": {"dest_id": "zuggtmoy_fungal_sanctum", "alias": "n"}},
        "npcs": [{"name": "Supreme Cleric Hedrack", "desc": "The supreme high priest of the Elemental Eye, wearing robes embroidered with screaming faces.", "level": 19, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Unholy Mace of the Elemental Eye", "desc": "A flanged mace that pulses with chaotic elemental discharges."}]
    }

    rooms["zuggtmoy_fungal_sanctum"] = {
        "name": "The Golden Spore Sanctum of Zuggtmoy",
        "desc": "A horrific cavern of rotting carpets, parasitic molds, and pulsating mycelium stalks. In the center presides the Demon Queen of Fungi.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "greater_temple_chaos", "alias": "s"}},
        "npcs": [{"name": "Demon Queen Zuggtmoy", "desc": "A terrifying demon sovereign draped in rotting silken folds and fungal caps, exhaling mind-rotting spores.", "level": 20, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Fungal Spore Crown of Zuggtmoy", "desc": "A crown of golden mushrooms that confers absolute immunity to poison and disease."}]
    }

    rooms["fire_node_sanctum"] = {
        "name": "The Fire Node Caldera",
        "desc": "A jagged volcanic platform surrounded by rivers of white-hot magma. Ash rains down from ceiling fissures.",
        "terrain": "mountain",
        "exits": {"west": {"dest_id": "temple_courtyard_evil", "alias": "w"}},
        "npcs": [{"name": "Fire Node Efreeti", "desc": "A hulking fiery genie in brass plate wielding a scimitar of undying flames.", "level": 18, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Heart of the Fire Node Crystal", "desc": "A pulsating magma crystal that radiates blistering solar heat."}]
    }

    rooms["water_node_sanctum"] = {
        "name": "The Water Node Trench",
        "desc": "A churning subterranean ocean chamber of frigid whirlpools and brine geysers.",
        "terrain": "water_swim",
        "exits": {"east": {"dest_id": "temple_courtyard_evil", "alias": "e"}},
        "npcs": [{"name": "Water Node Marid", "desc": "A haughty water genasi lord riding a crested sea serpent.", "level": 18, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Trident of the Water Node", "desc": "A coral trident humming with torrential oceanic currents."}]
    }

    # 59 corridors, elemental node tunnels, and cultist barracks to reach 65 rooms
    for i in range(1, 60):
        r_key = f"temple_corridor_{i:02d}"
        if r_key in rooms:
            continue
        
        terrain = "catacombs"
        desc = (
            f"Black basalt masonry etched with disturbing runic eyes. "
            f"Faint sulfur and elemental static charge the stagnant air. [Dungeon Sector #{i}]"
        )
        r_name = f"Elemental Temple Vault #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"temple_corridor_{i-1:02d}", "alias": "s"}
        if i < 59:
            exits["north"] = {"dest_id": f"temple_corridor_{i+1:02d}", "alias": "n"}
        if i + 5 <= 59:
            exits["east"] = {"dest_id": f"temple_corridor_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"temple_corridor_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "temple_courtyard_evil", "alias": "s"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Elemental Cultist Fanatic", "desc": "A robed zealot armed with an obsidian dagger.", "level": 12, "role": "mage"})
        elif i % 9 == 0:
            npcs.append({"name": "Gargoyle Sentry", "desc": "A stony winged brute perching high upon an arch.", "level": 13, "role": "warrior"})

        if i == 20:
            items.append({"name": "Obsidian Triangle of the Eye", "desc": "A black glass holy symbol used by cult officers."})

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
        "base_coords": (15, -60, -25),
        "rooms": rooms
    }


# =============================================================================
# ZONE 31: THE PEACEFUL SHIRE & GREEN DRAGON VALE [Level 1-5, 65 Rooms]
# =============================================================================

def build_zone_shire():
    zone_key = "halfling_shire"
    zone_name = "The Peaceful Shire & Green Dragon Vale"
    rooms = {}

    rooms["shire_brandywine_bridge"] = {
        "name": "The Stone Bridge of the Brandywine",
        "desc": "A charming three-arched stone bridge spanning the tranquil waters of the Brandywine River. Willows weep gracefully along the sunny grassy banks.",
        "terrain": "field",
        "exits": {"west": {"dest_id": "green_dragon_inn", "alias": "w"}},
        "npcs": [{"name": "Shire Shirriff", "desc": "A plump halfling with a feather in his woolen cap carrying a wooden cudgel.", "level": 2, "role": "warrior"}]
    }

    rooms["green_dragon_inn"] = {
        "name": "The Green Dragon Tavern Common Room",
        "desc": "A warm, hearth-lit room with low cedar ceilings, small oak tables, and the fragrant aroma of roast mutton, fresh-baked pies, and dark amber cider.",
        "terrain": "indoors",
        "exits": {"east": {"dest_id": "shire_brandywine_bridge", "alias": "e"}, "north": {"dest_id": "bywater_mill_pond", "alias": "n"}, "west": {"dest_id": "bag_end_smial", "alias": "w"}},
        "npcs": [{"name": "Innkeeper Barliman Butterbur", "desc": "A cheerful, bustling halfling carrying two frothing flagons of ale.", "level": 3, "role": "civilian"}],
        "items": [{"name": "Flagon of Old Winyards Ale", "desc": "A deep, fruity halfling vintage renowned across the land."}]
    }

    rooms["bywater_mill_pond"] = {
        "name": "The Bywater Watermill",
        "desc": "A massive mossy wooden waterwheel slowly turns in the river current, grinding fresh flour for the Shire's bakers.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "green_dragon_inn", "alias": "s"}, "north": {"dest_id": "shire_path_01", "alias": "n"}},
        "npcs": [{"name": "Ted Sandyman the Miller", "desc": "A flour-dusted halfling leaning against a sack of grain.", "level": 2, "role": "civilian"}]
    }

    rooms["bag_end_smial"] = {
        "name": "Bag End - The Round Green Door",
        "desc": "A comfortable smial burrow cut directly into the hillside, featuring a perfectly round green door with a brass doorknob in the exact center.",
        "terrain": "indoors",
        "exits": {"east": {"dest_id": "green_dragon_inn", "alias": "e"}, "north": {"dest_id": "mathom_house_museum", "alias": "n"}},
        "npcs": [{"name": "Mayor Will Whitfoot", "desc": "The esteemed Mayor of Michel Delving, wearing a golden chain of office over his waistcoat.", "level": 4, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Clay Pipe & Longbottom Leaf", "desc": "A fine briar pipe packed with the finest aromatic halfling pipe-weed."}]
    }

    rooms["mathom_house_museum"] = {
        "name": "The Michel Delving Mathom-House",
        "desc": "A repository of curious antiques, dented dwarven shields, old walking sticks, and curios that hobbits have no use for but refuse to throw away.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "bag_end_smial", "alias": "s"}},
        "items": [{"name": "Antique Dwarven Walking Staff", "desc": "A sturdy ash staff notched with the miles of great wanderers."}]
    }

    # 60 Shire country paths, apple orchards, burrow gardens to reach 65 rooms
    for i in range(1, 61):
        r_key = f"shire_path_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Rolling green meadows flanked by hawthorn hedges and yellow marigolds. "
            f"Smoke curls peacefully from round brick chimneys tucked into grassy hillsides. [Shire Lane #{i}]"
        )
        r_name = f"Shire Country Lane #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"shire_path_{i-1:02d}", "alias": "s"}
        if i < 60:
            exits["north"] = {"dest_id": f"shire_path_{i+1:02d}", "alias": "n"}
        if i + 5 <= 60:
            exits["east"] = {"dest_id": f"shire_path_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"shire_path_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "bywater_mill_pond", "alias": "s"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Halfling Orchardist", "desc": "A cheerful hobbit carrying a basket of ripe red apples.", "level": 2, "role": "civilian"})
        elif i % 10 == 0:
            npcs.append({"name": "Shire Bounder", "desc": "A vigilant border guard with a horn and stout bow.", "level": 3, "role": "rogue"})

        if i == 15:
            items.append({"name": "Basket of Fresh Blackberry Tarts", "desc": "Warm, sugary pastries that restore morale."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "field",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "field",
        "base_coords": (-35, 15, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 32: THE SUNKEN ATLANTIS UPPER SHELF [Level 14-22, 65 Rooms]
# =============================================================================

def build_zone_coral_shelf():
    zone_key = "atlantis_shelf"
    zone_name = "The Sunken Atlantis Upper Shelf & Coral Gardens"
    rooms = {}

    rooms["coral_shelf_pearl_shallows"] = {
        "name": "The Iridescent Coral Shallows",
        "desc": "Sunlight filters through thirty feet of turquoise ocean water, dancing across forests of purple brain coral and waving sea anemones.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "giant_clam_atoll", "alias": "s"}},
        "npcs": [{"name": "Reef Manta Ray", "desc": "A graceful ray gliding with wide blue wings over the sandy floor.", "level": 14, "role": "warrior"}]
    }

    rooms["giant_clam_atoll"] = {
        "name": "The Giant Clam Sanctuary",
        "desc": "Monstrous clams five feet wide lie nestled in white sand beds, opening their fluted shells to reveal lustrous opalescent pearls.",
        "terrain": "water_swim",
        "exits": {"north": {"dest_id": "coral_shelf_pearl_shallows", "alias": "n"}, "east": {"dest_id": "merfolk_council_atrium", "alias": "e"}, "down": {"dest_id": "electric_eel_trench", "alias": "d"}},
        "items": [{"name": "Lustrous Blue Ocean Pearl", "desc": "A flawless gemstone harvested from the giant clams of Atlantis."}]
    }

    rooms["merfolk_council_atrium"] = {
        "name": "The Sunken Council of Triton Lords",
        "desc": "Marble colonnades encrusted in pink coral surround a sunken amphitheater where merfolk diplomats swim in regal formations.",
        "terrain": "underwater",
        "exits": {"west": {"dest_id": "giant_clam_atoll", "alias": "w"}, "south": {"dest_id": "empress_thalassa_throne", "alias": "s"}},
        "npcs": [{"name": "Merfolk Triton Paladin", "desc": "A silver-scaled mer-warrior clutching a pearl-inlaid trident.", "level": 17, "role": "paladin"}]
    }

    rooms["empress_thalassa_throne"] = {
        "name": "The Coral Throne of Empress Thalassa",
        "desc": "Carved of living mother-of-pearl and pulsing sea fans, Empress Thalassa rules the upper ocean shelves with serene aquatic majesty.",
        "terrain": "underwater",
        "exits": {"north": {"dest_id": "merfolk_council_atrium", "alias": "n"}},
        "npcs": [{"name": "High Sea Empress Thalassa", "desc": "The sovereign monarch of the upper sea shelves, commanding ocean tides with an abalone scepter.", "level": 22, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Abalone Scepter of Tidal Command", "desc": "A mythic marine artifact capable of summoning whirlpools and calming ocean gales."}]
    }

    rooms["electric_eel_trench"] = {
        "name": "The Electric Eel Abyssal Trench",
        "desc": "A crack in the ocean floor crackling with blue bio-electric arcs. Enormous eels twist in the turbulent currents.",
        "terrain": "underwater",
        "exits": {"up": {"dest_id": "giant_clam_atoll", "alias": "u"}, "south": {"dest_id": "shelf_room_01", "alias": "s"}},
        "npcs": [{"name": "Giant Electric Eel", "desc": "A thirty-foot serpentine predator pulsing with lethal voltage.", "level": 18, "role": "warrior"}]
    }

    # 60 Coral gardens, submerged marble pavilions, and kelp forests to reach 65 rooms
    for i in range(1, 61):
        r_key = f"shelf_room_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Luminous coral reefs arch like living cathedrals beneath the waves. "
            f"Schools of iridescent silver fish dart through dancing kelp stalks. [Shelf Sector #{i}]"
        )
        r_name = f"Atlantis Coral Glade #{i}"
        
        exits = {}
        if i > 1:
            exits["north"] = {"dest_id": f"shelf_room_{i-1:02d}", "alias": "n"}
        if i < 60:
            exits["south"] = {"dest_id": f"shelf_room_{i+1:02d}", "alias": "s"}
        if i + 5 <= 60:
            exits["east"] = {"dest_id": f"shelf_room_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"shelf_room_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["north"] = {"dest_id": "electric_eel_trench", "alias": "n"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Reef Tiger Shark", "desc": "A striped ocean predator with rows of triangular serrated teeth.", "level": 15, "role": "warrior"})
        elif i % 9 == 0:
            npcs.append({"name": "Merfolk Coral Sculptor", "desc": "An aquatic artisan shaping living coral with song magic.", "level": 14, "role": "mage"})

        if i == 18:
            items.append({"name": "Flask of Aquatic Breathing Elixir", "desc": "Alchemical liquid allowing land-dwellers to breathe seawater."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "underwater",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "underwater",
        "base_coords": (-50, 40, -25),
        "rooms": rooms
    }


# =============================================================================
# ZONE 33: THE SEVEN HEAVENS OF MOUNT CELESTIA [Level 20-28, 65 Rooms]
# =============================================================================

def build_zone_mount_celestia():
    zone_key = "mount_celestia"
    zone_name = "The Seven Heavens of Mount Celestia"
    rooms = {}

    rooms["celestia_silver_sea_shore"] = {
        "name": "The Silver Sea Shore of Lunia",
        "desc": "Gentle surf of pure, consecrated holy water washes against a shore of pearlescent sand beneath a sky illuminated by a permanent silver moon.",
        "terrain": "water_swim",
        "exits": {"up": {"dest_id": "platinum_gate_lunia", "alias": "u"}},
        "npcs": [{"name": "Lunia Astral Hound", "desc": "A celestial canine with golden eyes and silver fur that senses evil intent.", "level": 20, "role": "paladin"}]
    }

    rooms["platinum_gate_lunia"] = {
        "name": "The Platinum Portal of Heaven",
        "desc": "A soaring archway of pure platinum polished to mirror brightness. Golden trumpets blow without mortal breath, heralding righteous souls.",
        "terrain": "city",
        "exits": {"down": {"dest_id": "celestia_silver_sea_shore", "alias": "d"}, "up": {"dest_id": "golden_orchards_mercuria", "alias": "u"}},
        "npcs": [{"name": "Sword Archon Gatekeeper", "desc": "A winged celestial warrior clad in brilliant platinum armor wielding twin blades of holy fire.", "level": 22, "role": "warrior"}]
    }

    rooms["golden_orchards_mercuria"] = {
        "name": "The Golden Orchards of Mercuria",
        "desc": "Endless rows of golden fruit trees blossom under a warm golden sun. Healing fountains flow with ambrosia and liquid light.",
        "terrain": "field",
        "exits": {"down": {"dest_id": "platinum_gate_lunia", "alias": "d"}, "up": {"dest_id": "solar_throne_apex", "alias": "u"}, "east": {"dest_id": "celestia_terrace_01", "alias": "e"}},
        "items": [{"name": "Ambrosia Fruit of Mercuria", "desc": "A celestial fruit that heals all wounds and restores magical balance."}]
    }

    rooms["solar_throne_apex"] = {
        "name": "The Empyreal Summit of Mount Celestia",
        "desc": "Bathed in the absolute radiant brilliance of the Divine Light, the summit commands the entire Multiverse. In the center stands Archangel Michael.",
        "terrain": "air",
        "exits": {"down": {"dest_id": "golden_orchards_mercuria", "alias": "d"}},
        "npcs": [{"name": "Archangel Michael the Solar Champion", "desc": "The supreme general of the heavenly hosts, with six wings of incandescent fire, brandishing the Blade of Absolute Justice.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Blade of Absolute Justice", "desc": "A celestial greatsword forged in the heart of the silver sea, dealing devastating holy radiant retribution."}]
    }

    # 61 Ascending terraces, choirs of angels, and crystal spires to reach 65 rooms
    for i in range(1, 62):
        r_key = f"celestia_terrace_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Stairs of polished white alabaster ascend into radiant clouds. "
            f"Choirs of celestial angels sing hymns of eternal harmony and triumph. [Terrace #{i}]"
        )
        r_name = f"Celestia Radiant Terrace #{i}"
        
        exits = {}
        if i > 1:
            exits["down"] = {"dest_id": f"celestia_terrace_{i-1:02d}", "alias": "d"}
        if i < 61:
            exits["up"] = {"dest_id": f"celestia_terrace_{i+1:02d}", "alias": "u"}
        if i + 5 <= 61:
            exits["east"] = {"dest_id": f"celestia_terrace_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"celestia_terrace_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["west"] = {"dest_id": "golden_orchards_mercuria", "alias": "w"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Hound Archon Justicar", "desc": "A noble hound-headed knight in silver plate.", "level": 21, "role": "paladin"})
        elif i % 9 == 0:
            npcs.append({"name": "Solar Trumpet Archon", "desc": "A glowing seraph whose silver trumpet blast stuns evil spirits.", "level": 23, "role": "cleric"})

        if i == 20:
            items.append({"name": "Vial of Silver Sea Holy Water", "desc": "Pure consecrated water that burns fiends like molten acid."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "air",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "air",
        "base_coords": (0, 80, 50),
        "rooms": rooms
    }


# =============================================================================
# INGESTION RUNNER & REGISTRATION
# =============================================================================

def run_bulk_ingestion_part8(clean_existing=False):
    """
    Executes Part 8 of the bulk world expansion ("1,500 Rooms Milestone"):
    - The Temple of Elemental Evil (65 rooms)
    - The Peaceful Shire & Green Dragon Vale (65 rooms)
    - The Sunken Atlantis Upper Shelf (65 rooms)
    - The Seven Heavens of Mount Celestia (65 rooms)
    Total: 260 rooms!
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
        build_zone_elemental_evil,
        build_zone_shire,
        build_zone_coral_shelf,
        build_zone_mount_celestia
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("temple_evil", "temple_evil_ruined_moathouse", "marshland", "enter ruined moathouse", "return to sunken mire"),
        ("halfling_shire", "shire_brandywine_bridge", "north_gate", "cross brandywine bridge", "return to eldoria gate"),
        ("atlantis_shelf", "coral_shelf_pearl_shallows", "dead_mans_cove", "dive into coral shallows", "surface to dead man's cove"),
        ("mount_celestia", "celestia_silver_sea_shore", "summit", "ascend stairway of silver light", "descend to mortal summit")
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

    return report
