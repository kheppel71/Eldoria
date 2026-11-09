"""
Bulk World Ingestion Engine — Part 6: The "1,000 Rooms Club" Mega-Expansion

Expands Eldoria with an additional 305 rooms across 4 legendary classic zones:
1. The Great Sewers & Thieves' Underground of Midgaard [Level 3-8, 75 Rooms]
2. The Ancient Primeval Forest of Haon-Dor & Spider Glen [Level 5-11, 75 Rooms]
3. The Haunted Graveyard & Catacomb Crypts of Midgaard [Level 6-12, 75 Rooms]
4. The Dwarven Kingdom of Moria (Dwarrowdelf & Balin's Tomb) [Level 10-18, 80 Rooms]

Total Rooms Created in Part 6: 305 Rooms
Cumulative World Total: 697 + 305 = 1,002 Rooms!

Features:
- 100% GMCP Room.Info automapper telemetry with relative 3D coordinate graphs
- Fixed danger ratings, full Nightmare LPmud combat sheets, and classic boss artifacts
- Four reciprocal overland and underground anchors linking directly to Midgaard and Frostfang Pass
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
# ZONE 22: THE GREAT SEWERS OF MIDGAARD [Level 3-8, 75 Rooms]
# =============================================================================

def build_zone_sewers():
    zone_key = "midgaard_sewers"
    zone_name = "The Great Sewers of Midgaard"
    rooms = {}

    # 1. Major Landmark Hubs
    rooms["sewer_grate_market"] = {
        "name": "Iron Sewer Grating Beneath the Market",
        "desc": "A shaft of dusty light filters down through the iron street grate above. Sluggish green water rushes past slick brick ledges.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "sewer_corridor_01", "alias": "n"}, "east": {"dest_id": "sewer_sluice_01", "alias": "e"}},
        "npcs": [{"name": "Giant Sewer Rat", "desc": "A diseased rat the size of a hound with yellow chisel teeth.", "level": 3, "role": "warrior"}]
    }

    rooms["central_junction_pool"] = {
        "name": "The Central Sludge Cistern",
        "desc": "A vast vaulted brick chamber where four colossal sewer channels converge into a deep whirlpool of bubbling muck.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "sewer_corridor_05", "alias": "s"}, "north": {"dest_id": "wererat_warren_entrance", "alias": "n"}, "east": {"dest_id": "thieves_guild_black_door", "alias": "e"}, "west": {"dest_id": "alligator_sump", "alias": "w"}},
        "npcs": [{"name": "Putrid Gelatinous Slime", "desc": "A translucent acidic cube undulating through the muck digesting refuse.", "level": 5, "role": "warrior"}]
    }

    rooms["wererat_warren_entrance"] = {
        "name": "The Wererat Sentry Warren",
        "desc": "Bones and tattered clothing litter the entrance to a network of gnawed burrow tunnels. Crude wooden barricades narrow the approach.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "central_junction_pool", "alias": "s"}, "north": {"dest_id": "wererat_throne_room", "alias": "n"}},
        "npcs": [{"name": "Wererat Sentry", "desc": "A bipedal rat-man clutching a notched shortsword and a light crossbow.", "level": 6, "role": "rogue"}]
    }

    rooms["wererat_throne_room"] = {
        "name": "The Filth Throne of the Rat King",
        "desc": "A mountain of discarded city garbage and sewer debris forms a towering throne where the Rat King commands his subterranean horde.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "wererat_warren_entrance", "alias": "s"}, "east": {"dest_id": "sewer_corridor_20", "alias": "e"}},
        "npcs": [{"name": "Rat King Splinterclaw", "desc": "A massive scarred wererat chieftain wearing a crown of bent spoons and wielding an envenomed rapier.", "level": 8, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Venomous Stiletto of the Sewer King", "desc": "A rusted assassin's stiletto coated in virulent sewer fever venom."}]
    }

    rooms["thieves_guild_black_door"] = {
        "name": "The Shadow Door of the Guild",
        "desc": "A heavy iron-reinforced oak door marked with the secret guild sign of a dagger through a coin.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "central_junction_pool", "alias": "w"}, "east": {"dest_id": "thieves_guild_headquarters", "alias": "e"}}
    }

    rooms["thieves_guild_headquarters"] = {
        "name": "The Den of the Shadow Blades",
        "desc": "A dry, well-guarded underground sanctum illuminated by amber lantern light. Maps of the city above are spread across heavy oak planning tables.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "thieves_guild_black_door", "alias": "w"}, "north": {"dest_id": "sewer_corridor_25", "alias": "n"}},
        "npcs": [{"name": "Guildmaster Vane", "desc": "A silken-voiced rogue master in black velvet, spinning a balance dagger between his fingers.", "level": 9, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Shadow Cloak of the Silent Step", "desc": "A supple velvet cloak that dampens footfalls and muffles armor clatter."}]
    }

    rooms["alligator_sump"] = {
        "name": "The Submerged Alligator Sump",
        "desc": "Dark stagnant water stretches beneath low mossy arches. Yellow reptilian eyes break the surface in predatory silence.",
        "terrain": "water_swim",
        "exits": {"east": {"dest_id": "central_junction_pool", "alias": "e"}, "west": {"dest_id": "sewer_corridor_30", "alias": "w"}},
        "npcs": [{"name": "Albino Sewer Alligator", "desc": "A monstrous fifteen-foot pale crocodilian that has thrived in the city dark.", "level": 7, "role": "warrior"}]
    }

    # 2. Build 68 Grid/Corridor Rooms to complete 75 rooms
    # We create a 5x13 + 3 interconnected grid layout
    for i in range(1, 69):
        r_key = f"sewer_corridor_{i:02d}"
        if r_key in rooms:
            continue
        
        # Sector variation
        terrain = "water_swim" if i % 4 == 0 else "catacombs"
        desc = (
            f"A damp brick sewer vault smelling of mildew and stagnant runoff. "
            f"Iron runoff pipes vent waste into the central flow. [Sector {i}]"
        )
        r_name = f"Sewer Conduit #{i}"
        
        # Exit interconnects
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"sewer_corridor_{i-1:02d}", "alias": "s"}
        if i < 68:
            exits["north"] = {"dest_id": f"sewer_corridor_{i+1:02d}", "alias": "n"}
        
        # Cross links
        if i + 5 <= 68:
            exits["east"] = {"dest_id": f"sewer_corridor_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"sewer_corridor_{i-5:02d}", "alias": "w"}

        # Link to landmarks
        if i == 1:
            exits["south"] = {"dest_id": "sewer_grate_market", "alias": "s"}
        if i == 5:
            exits["north"] = {"dest_id": "central_junction_pool", "alias": "n"}

        # Wandering mobs & loot
        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Wererat Skulker", "desc": "A hunched rat-man scouting for victims.", "level": 4, "role": "rogue"})
        elif i % 11 == 0:
            npcs.append({"name": "Carrion Slug", "desc": "A bloated purple slug that dissolves flesh.", "level": 4, "role": "warrior"})
        
        if i == 15:
            items.append({"name": "Rusted Copper Drain Key", "desc": "A heavy key that opens municipal maintenance grates."})
        elif i == 45:
            items.append({"name": "Pouch of Waterlogged Silver Coins", "desc": "A lost purse dropped down a street sewer grating."})

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
        "base_coords": (0, 0, -10),
        "rooms": rooms
    }


# =============================================================================
# ZONE 23: THE ANCIENT FOREST OF HAON-DOR [Level 5-11, 75 Rooms]
# =============================================================================

def build_zone_haondor():
    zone_key = "haon_dor_forest"
    zone_name = "The Ancient Forest of Haon-Dor"
    rooms = {}

    # 1. Landmark Hubs
    rooms["haon_dor_western_verge"] = {
        "name": "The Western Verge of Haon-Dor",
        "desc": "The ancient timber of Haon-Dor rises like a dark green wall against the sky. Giant gnarled oaks blot out the sun, leaving the mossy forest floor in eternal twilight.",
        "terrain": "forest",
        "exits": {"east": {"dest_id": "haon_dor_path_01", "alias": "e"}},
        "npcs": [{"name": "Haon-Dor Timber Wolf", "desc": "A grey-furred predator with gleaming yellow eyes stalking through the undergrowth.", "level": 5, "role": "warrior"}]
    }

    rooms["whispering_pine_crossroad"] = {
        "name": "The Crossroad of the Whispering Pines",
        "desc": "Four worn deer paths intersect at a moss-covered boulder. Scent of pine needles and damp earth hangs heavy in the quiet air.",
        "terrain": "forest",
        "exits": {"west": {"dest_id": "haon_dor_path_05", "alias": "w"}, "north": {"dest_id": "bandit_camp_stockade", "alias": "n"}, "east": {"dest_id": "spider_glen_entrance", "alias": "e"}, "south": {"dest_id": "haon_dor_path_10", "alias": "s"}}
    }

    rooms["bandit_camp_stockade"] = {
        "name": "The Stockade of the Forest Bandits",
        "desc": "Sharpened wooden stakes and watch platforms enclose a hidden forest encampment. A roaring campfire crackles in the center.",
        "terrain": "forest",
        "exits": {"south": {"dest_id": "whispering_pine_crossroad", "alias": "s"}, "north": {"dest_id": "bandit_lord_tent", "alias": "n"}},
        "npcs": [{"name": "Bandit Highwayman", "desc": "A rough brigand in boiled leather wielding a heavy broadsword.", "level": 7, "role": "warrior"}]
    }

    rooms["bandit_lord_tent"] = {
        "name": "Pavilion of Bandit Lord Malrik",
        "desc": "A spacious silk tent furnished with looted merchant carpets and chests of stolen goods.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "bandit_camp_stockade", "alias": "s"}},
        "npcs": [{"name": "Bandit Lord Malrik", "desc": "A ruthless scarred warlord in blackened steel plate, wielding a massive greataxe.", "level": 11, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Malrik's Blood-Forged Greataxe", "desc": "A terrifying two-handed battleaxe notched from dozens of ambush raids."}]
    }

    rooms["spider_glen_entrance"] = {
        "name": "The Web-Choked Briar Hollow",
        "desc": "Dense thorny briars are cocooned in thick sheets of sticky grey spider silk. Skeletons of deer and men hang suspended in the trees.",
        "terrain": "forest",
        "exits": {"west": {"dest_id": "whispering_pine_crossroad", "alias": "w"}, "east": {"dest_id": "arachnid_matriarch_nest", "alias": "e"}},
        "npcs": [{"name": "Giant Wood Spider", "desc": "An eight-legged horror dripping digestive venom from its black mandibles.", "level": 8, "role": "rogue"}]
    }

    rooms["arachnid_matriarch_nest"] = {
        "name": "Nest of the Arachnid Matriarch",
        "desc": "A hollow clearing surrounded by dead, petrified pines completely enclosed in suffocating spider silk webs.",
        "terrain": "forest",
        "exits": {"west": {"dest_id": "spider_glen_entrance", "alias": "w"}},
        "npcs": [{"name": "The Arachnid Matriarch", "desc": "A horse-sized bloated spider with eight crimson eyes and fangs sharp as daggers.", "level": 10, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Gossamer Chitin Shield", "desc": "A buckler woven from compressed spider silk as resilient as hardened iron."}]
    }

    rooms["druid_stone_circle"] = {
        "name": "The Menhirs of the Oak Circle",
        "desc": "Twelve massive mossy standing stones arranged in a perfect ring beneath the boughs of a thousand-year-old oak tree.",
        "terrain": "field",
        "exits": {"south": {"dest_id": "haon_dor_path_25", "alias": "s"}},
        "npcs": [{"name": "Arch-Druid Kieran", "desc": "A venerable druid with mistletoe in his long white beard, holding a staff of living rowan.", "level": 9, "role": "cleric"}],
        "items": [{"name": "Rowan Wood Staff of the Grove", "desc": "A staff infused with the primal restorative vitality of Haon-Dor."}]
    }

    # 2. Build 68 Forest Path & Thicket Rooms to complete 75 rooms
    for i in range(1, 69):
        r_key = f"haon_dor_path_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Ancient oaks and towering firs arch high overhead. "
            f"Ferns brush against your boots along the winding dirt trail. [Sector {i}]"
        )
        r_name = f"Haon-Dor Woodland Track #{i}"
        
        exits = {}
        if i > 1:
            exits["west"] = {"dest_id": f"haon_dor_path_{i-1:02d}", "alias": "w"}
        if i < 68:
            exits["east"] = {"dest_id": f"haon_dor_path_{i+1:02d}", "alias": "e"}
        if i + 6 <= 68:
            exits["north"] = {"dest_id": f"haon_dor_path_{i+6:02d}", "alias": "n"}
        if i - 6 >= 1:
            exits["south"] = {"dest_id": f"haon_dor_path_{i-6:02d}", "alias": "s"}

        if i == 1:
            exits["west"] = {"dest_id": "haon_dor_western_verge", "alias": "w"}
        if i == 5:
            exits["east"] = {"dest_id": "whispering_pine_crossroad", "alias": "e"}
        if i == 25:
            exits["north"] = {"dest_id": "druid_stone_circle", "alias": "n"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Forest Black Bear", "desc": "A powerful bear foraging for honey and defending its territory.", "level": 6, "role": "warrior"})
        elif i % 9 == 0:
            npcs.append({"name": "Haon-Dor Bandit Scout", "desc": "A hidden archer with a yew shortbow nocked with flint-tipped arrows.", "level": 6, "role": "rogue"})
        
        if i == 20:
            items.append({"name": "Bundle of Forest Medicinal Herbs", "desc": "Aromatic wild herbs known to purge fevers and soothe wounds."})
        elif i == 50:
            items.append({"name": "Hunter's Sturdy Boar Spear", "desc": "An ash-hafted spear fitted with cross-bars to stop charging beasts."})

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
        "base_coords": (-25, 20, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 24: THE HAUNTED GRAVEYARD OF MIDGAARD [Level 6-12, 75 Rooms]
# =============================================================================

def build_zone_graveyard():
    zone_key = "midgaard_graveyard"
    zone_name = "The Haunted Graveyard of Midgaard"
    rooms = {}

    # 1. Landmark Hubs
    rooms["graveyard_iron_gate"] = {
        "name": "The Rusted Wrought-Iron Cemetery Gate",
        "desc": "A pair of creaking black iron gates hangs from crumbling stone pillars carved with weeping cherubs. Fog curls around moss-covered tombstones.",
        "terrain": "field",
        "exits": {"north": {"dest_id": "avenue_of_tombs", "alias": "n"}},
        "npcs": [{"name": "Gravekeeper Skeleton", "desc": "An animated skeleton clutching a rusted spade and a dented lantern.", "level": 6, "role": "warrior"}]
    }

    rooms["avenue_of_tombs"] = {
        "name": "The Fog-Shrouded Avenue of Tombs",
        "desc": "A broad cobblestone avenue flanked by rows of family vaults and cracked marble monuments. Raven cries pierce the eerie silence.",
        "terrain": "field",
        "exits": {"south": {"dest_id": "graveyard_iron_gate", "alias": "s"}, "north": {"dest_id": "mausoleum_of_kings", "alias": "n"}, "east": {"dest_id": "ghoul_trench_burial", "alias": "e"}, "west": {"dest_id": "grave_plot_01", "alias": "w"}}
    }

    rooms["mausoleum_of_kings"] = {
        "name": "The Grand Royal Mausoleum",
        "desc": "A neoclassical marble sepulcher where the ancient rulers of Midgaard rest. Heavy bronze doors stand slightly ajar, venting chilling crypt air.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "avenue_of_tombs", "alias": "s"}, "down": {"dest_id": "catacomb_descent_stairs", "alias": "d"}},
        "npcs": [{"name": "Spectral Tomb Guardian", "desc": "A shimmering phantom in ghostly chainmail brandishing an ethereal longsword.", "level": 8, "role": "paladin"}]
    }

    rooms["catacomb_descent_stairs"] = {
        "name": "The Marble Stair of the Restless Dead",
        "desc": "Cold marble steps spiral down into deep subterranean crypts. Water drips with rhythmic dread into the dark below.",
        "terrain": "catacombs",
        "exits": {"up": {"dest_id": "mausoleum_of_kings", "alias": "u"}, "north": {"dest_id": "crypt_wight_throne", "alias": "n"}},
        "npcs": [{"name": "Crypt Ghoul", "desc": "A feral undead feasting upon ancient bones with sickening crunching sounds.", "level": 7, "role": "rogue"}]
    }

    rooms["crypt_wight_throne"] = {
        "name": "The Sepulcher of the Crypt Wight Sovereign",
        "desc": "An underground chamber lined with thousand skull niches. Upon a throne of cracked sarcophagus stone sits the Wight Sovereign.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "catacomb_descent_stairs", "alias": "s"}},
        "npcs": [{"name": "The Crypt Wight Sovereign", "desc": "A terrifying undead warlord wrapped in rotted shroud silk, eyes burning with icy hatred.", "level": 12, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Rime-Forged Wight Blade", "desc": "A jagged broadsword that drains the warmth and life energy from its victims."}]
    }

    rooms["ghoul_trench_burial"] = {
        "name": "The Trench of the Restless Ghouls",
        "desc": "Open graves and shattered coffins litter a mud trench reeking of death and decay.",
        "terrain": "field",
        "exits": {"west": {"dest_id": "avenue_of_tombs", "alias": "w"}, "east": {"dest_id": "grave_plot_20", "alias": "e"}},
        "npcs": [{"name": "Ghast Packleader", "desc": "A diseased ghast exuding a stench so foul it sickens living mortals.", "level": 8, "role": "warrior"}]
    }

    rooms["ossuary_vault_crypt"] = {
        "name": "The Subterranean Vault of Thousand Bones",
        "desc": "Walls completely built of stacked human femurs and skulls mortared together in macabre patterns.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "grave_plot_40", "alias": "n"}},
        "items": [{"name": "Silver Aspergillum of Consecration", "desc": "A sacred holy water sprinkler that banishes lesser undead."}]
    }

    # 2. Build 68 Grave Plots & Catacomb Rooms to complete 75 rooms
    for i in range(1, 69):
        r_key = f"grave_plot_{i:02d}"
        if r_key in rooms:
            continue
        
        terrain = "catacombs" if i > 40 else "field"
        desc = (
            f"Ancient sunken headstones lean among overgrown weeds and swirling graveyard fog. "
            f"Chiseled epitaphs are eroded by centuries of rain. [Plot #{i}]"
        )
        r_name = f"Graveyard Plot #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"grave_plot_{i-1:02d}", "alias": "s"}
        if i < 68:
            exits["north"] = {"dest_id": f"grave_plot_{i+1:02d}", "alias": "n"}
        if i + 5 <= 68:
            exits["east"] = {"dest_id": f"grave_plot_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"grave_plot_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["east"] = {"dest_id": "avenue_of_tombs", "alias": "e"}
        if i == 20:
            exits["west"] = {"dest_id": "ghoul_trench_burial", "alias": "w"}
        if i == 40:
            exits["south"] = {"dest_id": "ossuary_vault_crypt", "alias": "s"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Restless Tomb Zombie", "desc": "A shambling corpse clad in rotten burial linens.", "level": 6, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Wailing Banshee Spirit", "desc": "A weeping ghostly apparition whose shriek chills the blood.", "level": 8, "role": "mage"})
        
        if i == 25:
            items.append({"name": "Tarnished Silver Funerary Urn", "desc": "An urn engraved with protective holy runes."})
        elif i == 55:
            items.append({"name": "Amulet of Grave-Dust Warding", "desc": "An amulet that protects the wearer from necromantic chills."})

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
        "default_terrain": "field",
        "base_coords": (0, 25, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 25: THE DWARVEN KINGDOM OF MORIA [Level 10-18, 80 Rooms]
# =============================================================================

def build_zone_moria():
    zone_key = "moria_mines"
    zone_name = "The Dwarven Kingdom of Moria"
    rooms = {}

    # 1. Landmark Hubs
    rooms["moria_west_gate_durin"] = {
        "name": "The West Gate of Moria - Doors of Durin",
        "desc": "Carved into the sheer black cliff face of the mountain, the Doors of Durin glow with faint ithildin silver starlight. Carvings of hammers, anvils, and the Crown of Durin adorn the portal.",
        "terrain": "mountain",
        "exits": {"east": {"dest_id": "guardroom_of_durin", "alias": "e"}},
        "npcs": [{"name": "Watcher in the Water Spawn", "desc": "A slimy green tentacle slithering from the dark mountain tarn.", "level": 10, "role": "warrior"}]
    }

    rooms["guardroom_of_durin"] = {
        "name": "The Ancient Dwarf Bastion of the Gates",
        "desc": "Massive granite stone benches and arrow slits look down upon the threshold. Dwarven shields of bronze and iron hang from the walls.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "moria_west_gate_durin", "alias": "w"}, "east": {"dest_id": "grand_pillared_hall", "alias": "e"}}
    }

    rooms["grand_pillared_hall"] = {
        "name": "The Great Pillared Hall of Dwarrowdelf",
        "desc": "Vast as a mountain cavern, soaring stone pillars carved like giant stone trees support a ceiling lost in shadows. Echoes of footsteps reverberate for miles.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "guardroom_of_durin", "alias": "w"}, "north": {"dest_id": "twenty_first_hall", "alias": "n"}, "east": {"dest_id": "chamber_of_mazarbul", "alias": "e"}, "down": {"dest_id": "mithril_quarry_abyss", "alias": "d"}},
        "npcs": [{"name": "Moria Goblin Archer", "desc": "A yellow-fanged goblin armed with a horn bow and poisoned arrows.", "level": 11, "role": "rogue"}]
    }

    rooms["chamber_of_mazarbul"] = {
        "name": "The Chamber of Records & Balin's Tomb",
        "desc": "A ray of sunlight streams through an overhead shaft, striking a white stone sarcophagus. Runes carved in Daeron's cirth read: 'Balin Son of Fundin, Lord of Moria'.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "grand_pillared_hall", "alias": "w"}, "north": {"dest_id": "troll_deep_arena", "alias": "n"}},
        "npcs": [{"name": "Balin's Shadow Wraith", "desc": "The tormented shade of the dwarven lord, wreathed in frost and sorrow, wielding an ancestral warhammer.", "level": 17, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Book of Mazarbul Record Fragment", "desc": "An ancient scorched parchment: 'We cannot get out... drums in the deep... they are coming.'"}, {"name": "Hammer of the Mountain Lord", "desc": "A heavy mithril-inlaid warhammer that shatters stone and construct armor."}]
    }

    rooms["troll_deep_arena"] = {
        "name": "The Cavern of the Great Cave Troll",
        "desc": "Smashed stone masonry and shattered dwarf bones litter a massive subterranean hall where the drums in the deep thunder.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "chamber_of_mazarbul", "alias": "s"}, "east": {"dest_id": "abyssal_chasm_bridge", "alias": "e"}},
        "npcs": [{"name": "Armored Cave Troll Crusher", "desc": "A twelve-foot mountain troll clad in bolted iron plates, swinging a granite hammer on an iron chain.", "level": 18, "role": "boss", "danger_tier": "boss"}]
    }

    rooms["abyssal_chasm_bridge"] = {
        "name": "The Narrow Bridge of Khazad-Dum",
        "desc": "A slender arch of stone fifty feet long, without rail or curb, spanning a black chasm of unfathomable depth. Heat and red sulfur glow from the abyss.",
        "terrain": "mountain",
        "exits": {"west": {"dest_id": "troll_deep_arena", "alias": "w"}, "east": {"dest_id": "moria_gallery_30", "alias": "e"}},
        "npcs": [{"name": "Moria Orc Chieftain", "desc": "A muscular orc in scaly mail with a curved scimitar and a wolf-head helm.", "level": 14, "role": "warrior"}]
    }

    rooms["twenty_first_hall"] = {
        "name": "The Twenty-First Hall of the North",
        "desc": "Carved of dark polished granite, this northern hall was once the gathering place of the Dwarf Kings. Ancient heraldic banners hang in tatters.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "grand_pillared_hall", "alias": "s"}, "north": {"dest_id": "moria_gallery_15", "alias": "n"}}
    }

    rooms["mithril_quarry_abyss"] = {
        "name": "The Deep Mithril Mines",
        "desc": "Veins of gleaming silvery-blue true-silver (Mithril) shimmer in the dark rock walls. Deep mine cart rails lead down into the abyss.",
        "terrain": "catacombs",
        "exits": {"up": {"dest_id": "grand_pillared_hall", "alias": "u"}, "south": {"dest_id": "moria_gallery_45", "alias": "s"}},
        "items": [{"name": "Raw Chunk of Moria Mithril Ore", "desc": "Incredibly light and harder than dragon scales, the rarest metal in the world."}]
    }

    # 2. Build 72 Dwarf Gallery, Shaft & Barracks Rooms to complete 80 rooms
    for i in range(1, 73):
        r_key = f"moria_gallery_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Towering granite walls carved with dwarven geometric masonry. "
            f"Mine cart rails cross the floor beside deep air shafts. [Gallery #{i}]"
        )
        r_name = f"Moria Stone Gallery #{i}"
        
        exits = {}
        if i > 1:
            exits["west"] = {"dest_id": f"moria_gallery_{i-1:02d}", "alias": "w"}
        if i < 72:
            exits["east"] = {"dest_id": f"moria_gallery_{i+1:02d}", "alias": "e"}
        if i + 8 <= 72:
            exits["north"] = {"dest_id": f"moria_gallery_{i+8:02d}", "alias": "n"}
        if i - 8 >= 1:
            exits["south"] = {"dest_id": f"moria_gallery_{i-8:02d}", "alias": "s"}

        if i == 15:
            exits["south"] = {"dest_id": "twenty_first_hall", "alias": "s"}
        if i == 30:
            exits["west"] = {"dest_id": "abyssal_chasm_bridge", "alias": "w"}
        if i == 45:
            exits["north"] = {"dest_id": "mithril_quarry_abyss", "alias": "n"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Moria Orc Slasher", "desc": "A black-skinned orc soldier wielding a jagged serrated scimitar.", "level": 12, "role": "warrior"})
        elif i % 9 == 0:
            npcs.append({"name": "Dwarven Skeleton Guardian", "desc": "An ancient dwarf warrior risen in death to protect his gold.", "level": 11, "role": "warrior"})
        
        if i == 22:
            items.append({"name": "Dwarven Mason's Granite Chisel", "desc": "A mastercraft tempered chisel that carves runes into bedrock."})
        elif i == 60:
            items.append({"name": "Flask of Dwarven Mountain Ale", "desc": "A potent, heady brew that warms the blood against subterranean cold."})

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
        "base_coords": (50, 60, -30),
        "rooms": rooms
    }


# =============================================================================
# INGESTION RUNNER & REGISTRATION
# =============================================================================

def run_bulk_ingestion_part6(clean_existing=False):
    """
    Executes Part 6 of the bulk world expansion ("1,000 Rooms Club"):
    - The Great Sewers of Midgaard (75 rooms)
    - The Ancient Forest of Haon-Dor (75 rooms)
    - The Haunted Graveyard of Midgaard (75 rooms)
    - The Dwarven Kingdom of Moria (80 rooms)
    Total: 305 rooms!
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
        build_zone_sewers,
        build_zone_haondor,
        build_zone_graveyard,
        build_zone_moria
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("midgaard_sewers", "sewer_grate_market", "midgaard_district_market_square", "lift iron sewer grate", "climb ladder to market"),
        ("haon_dor_forest", "haon_dor_western_verge", "deep_woods", "enter ancient woods of haon-dor", "return to whispering woods"),
        ("midgaard_graveyard", "graveyard_iron_gate", "midgaard_district_temple_square", "enter cemetery iron gates", "return to temple square"),
        ("moria_mines", "moria_west_gate_durin", "frostfang_pass", "approach doors of durin", "return to frostfang pass")
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

