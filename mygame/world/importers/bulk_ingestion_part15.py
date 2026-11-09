"""
Bulk World Ingestion Engine — Part 15: The "3,250+ Rooms Grand Expansion"

Expands Eldoria beyond 3,250 rooms (reaching 3,277 rooms) across 4 iconic planar, mythic, and subterranean adventure realms:
1. The Clockwork Nirvana of Mechanus & Primus's Modron Cathedral [Level 18-26 Axiomatic Law, 60 Rooms]
2. The Feywild Summer Court & Palace of Queen Titania [Level 16-24 Fey Nature, 60 Rooms]
3. The Shadowfell Fortress of Memories & Raven Queen's Sanctuary [Level 22-30 Shadow Endgame, 60 Rooms]
4. The Subterranean Drow Underdark of Ched Nasad (City of Shimmering Webs) [Level 18-27 Underdark, 60 Rooms]

Total Rooms Created in Part 15: 241 Rooms (including 'The Fey-Barge Gossamer Swan' weather deck)
Cumulative World Total: 3,036 + 241 = 3,277 Rooms!

Features:
- New 'The Fey-Barge Gossamer Swan' enchanted waterway transit route in sailing.py
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
# ZONE 58: THE CLOCKWORK NIRVANA OF MECHANUS [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_mechanus_gears():
    zone_key = "mechanus_gears"
    zone_name = "The Clockwork Nirvana of Mechanus & Modron Cathedral"
    rooms = {}

    rooms["mechanus_planetary_gear_platform"] = {
        "name": "The Planetary Gear Platform of Mechanus",
        "desc": "A vast, slowly rotating gear of interlocking burnished brass miles across. In the distance, endless tiers of planetary cogs rotate in perpetual, mathematically flawless harmony against an orderly golden sky.",
        "terrain": "stone",
        "exits": {"north": {"dest_id": "mechanus_modron_procession_way", "alias": "n"}},
        "npcs": [{"name": "Monodrone Surveyor", "desc": "A spherical modron with a single mechanical eye, brass wings, and a monocle, taking rapid calculations.", "level": 18, "role": "warrior"}]
    }

    rooms["mechanus_modron_procession_way"] = {
        "name": "The Grand Modron Procession Way",
        "desc": "A paved avenue of perfectly polished basalt set atop massive meshed teeth. Columns of modrons march in absolute unison with rhythmic clockwork ticking.",
        "terrain": "stone",
        "exits": {
            "south": {"dest_id": "mechanus_planetary_gear_platform", "alias": "s"},
            "east": {"dest_id": "mechanus_cog_balancing_station", "alias": "e"},
            "west": {"dest_id": "mechanus_inevitable_tribunal", "alias": "w"},
            "north": {"dest_id": "mechanus_gear_rim_01", "alias": "n"}
        },
        "npcs": [{"name": "Duodrone Centurion", "desc": "A rectangular modron directing traffic with precise, jerky arm motions.", "level": 20, "role": "warrior"}]
    }

    rooms["mechanus_cog_balancing_station"] = {
        "name": "The Cog Lubrication & Balancing Station",
        "desc": "Giant reservoirs of refined petroleum and distilled mercury feeding thousands of brass oil-pipes that keep the planetary gear teeth frictionless.",
        "terrain": "stone",
        "exits": {"west": {"dest_id": "mechanus_modron_procession_way", "alias": "w"}},
        "npcs": [{"name": "Tridrone Inspector", "desc": "An inverted pyramid modron with three legs and three spidery multi-jointed arms.", "level": 21, "role": "rogue"}],
        "items": [{"name": "Flask of Frictionless Mechanus Oil", "desc": "A flask of magical oil that eliminates all friction from machinery."}]
    }

    rooms["mechanus_inevitable_tribunal"] = {
        "name": "The Inevitable Tribunal of Absolute Order",
        "desc": "A stark granite courthouse where towering Marut construct judges weigh oaths and contracts made across the multiverse with unyielding planar justice.",
        "terrain": "stone",
        "exits": {"east": {"dest_id": "mechanus_modron_procession_way", "alias": "e"}},
        "npcs": [{"name": "Marut Inevitable Arbiter", "desc": "A massive armored construct of gold and onyx wielding a thunderous slam attack.", "level": 24, "role": "warrior"}]
    }

    rooms["mechanus_modron_cathedral"] = {
        "name": "The Great Modron Cathedral of the Prime Cog",
        "desc": "A monumental temple formed from hundred-foot brass pipes and resonating tuning forks. The deep humming tone of the infinite gear train vibrates through every stone.",
        "terrain": "stone",
        "exits": {
            "south": {"dest_id": "mechanus_gear_rim_18", "alias": "s"},
            "north": {"dest_id": "mechanus_primus_central_spindle", "alias": "n"}
        },
        "npcs": [{"name": "Pentadrone Hierarch", "desc": "A starfish-shaped modron with five arms and five sensory stalks chanting algorithmic prayers.", "level": 25, "role": "mage"}]
    }

    rooms["mechanus_primus_central_spindle"] = {
        "name": "The Spindle of Axiomatic Law",
        "desc": "The primary axis around which an entire cluster of cog-continents revolves. Streams of liquid gold flow along engraved conduits directly toward the apex throne.",
        "terrain": "stone",
        "exits": {
            "south": {"dest_id": "mechanus_modron_cathedral", "alias": "s"},
            "north": {"dest_id": "mechanus_primus_throne_of_order", "alias": "n"}
        },
        "npcs": [{"name": "Secundus Overseer", "desc": "An exalted humanoid modron radiating an aura of absolute mathematical perfection.", "level": 26, "role": "mage"}]
    }

    rooms["mechanus_primus_throne_of_order"] = {
        "name": "The Infinity Throne of Primus",
        "desc": "The apex of Mechanus. Floating above an immense pool of liquid law sits Primus, the One and the Prime, whose right hand holds order and whose left holds energy.",
        "terrain": "stone",
        "exits": {"south": {"dest_id": "mechanus_primus_central_spindle", "alias": "s"}},
        "npcs": [{"name": "Primus, Lord of the Modrons", "desc": "The supreme being of law and order, a titan of clockwork and light whose gaze analyzes every probability in the cosmos.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Infinity Gear of Primus", "desc": "A palm-sized golden gear that synchronizes the wearer's actions with multiversal precision."},
            {"name": "Axiomatic Scepter of Law", "desc": "A scepter of polished brass and chrysolite that dispels planar chaos."}
        ]
    }

    # 53 connected gear rims, clockwork walkways, and planetary cog bridges
    for i in range(1, 54):
        r_key = f"mechanus_gear_rim_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Precision-machined brass teeth and bronze walkways rotating slowly across the void. "
            f"The rhythmic, soothing tick-tock of cosmic machinery fills the air. [Mechanus Cog #{i}]"
        )
        r_name = f"Mechanus Planetary Gear Rim #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"mechanus_gear_rim_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"mechanus_gear_rim_{i+1:02d}", "alias": "n"}
        if i + 6 <= 53:
            exits["east"] = {"dest_id": f"mechanus_gear_rim_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"mechanus_gear_rim_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "mechanus_modron_procession_way", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "mechanus_modron_cathedral", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "mechanus_primus_central_spindle", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Quadrone Taskmaster", "desc": "A cube-shaped modron equipped with four mechanical crossbows.", "level": 22, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Axiomatic Clockwork Hound", "desc": "A mechanical hound forged of bronze plates with steam vents along its spine.", "level": 23, "role": "warrior"})

        if i == 24:
            items.append({"name": "Brass Calibration Rod", "desc": "A finely calibrated measuring tool used to align planetary gears."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "stone",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "stone",
        "base_coords": (120, 240, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 59: THE FEYWILD SUMMER COURT & PALACE OF QUEEN TITANIA [Level 16-24, 60 Rooms]
# =============================================================================

def build_zone_summer_court():
    zone_key = "summer_court"
    zone_name = "The Feywild Summer Court & Palace of Queen Titania"
    rooms = {}

    rooms["summer_court_emerald_gateway"] = {
        "name": "The Emerald Gateway of the Summer Court",
        "desc": "An archway of interwoven weeping willows and flowering honeysuckle opening into an eternal golden twilight. Luminous fireflies dance in swarms, and the scent of wild jasmine hangs sweet in the breeze.",
        "terrain": "forest",
        "exits": {"north": {"dest_id": "summer_court_starlight_promenade", "alias": "n"}},
        "npcs": [{"name": "Summer Court Eladrin Guardian", "desc": "A graceful warrior with emerald hair and gossamer leaf-mail, carrying a bow carved from living yew.", "level": 17, "role": "warrior"}]
    }

    rooms["summer_court_starlight_promenade"] = {
        "name": "The Starlight Promenade",
        "desc": "A wide path carpeted with soft clover and luminescent blue moss that glows beneath every step. Crystal clear brooks murmur beside the path, filled with swimming sylphs.",
        "terrain": "forest",
        "exits": {
            "south": {"dest_id": "summer_court_emerald_gateway", "alias": "s"},
            "east": {"dest_id": "summer_court_fairy_ring_grove", "alias": "e"},
            "west": {"dest_id": "summer_court_pixie_orchard", "alias": "w"},
            "north": {"dest_id": "summer_court_glade_path_01", "alias": "n"}
        },
        "npcs": [{"name": "Dancing Satyr Minstrel", "desc": "A goat-legged satyr playing a lively tune on silver panpipes that urges all travelers to dance.", "level": 18, "role": "rogue"}]
    }

    rooms["summer_court_fairy_ring_grove"] = {
        "name": "The Whispering Fairy Ring",
        "desc": "A circle of giant bioluminescent toadstools pulsing with gentle lavender light. Soft fey laughter echoes just out of sight among the ferns.",
        "terrain": "forest",
        "exits": {"west": {"dest_id": "summer_court_starlight_promenade", "alias": "w"}},
        "npcs": [{"name": "High Will-o'-Wisp", "desc": "A dancing orb of pure fey light that flickers with mischievous amusement.", "level": 19, "role": "mage"}],
        "items": [{"name": "Phial of Fey Dewdrops", "desc": "Sparkling morning dew gathered from the fairy ring that restores vigor."}]
    }

    rooms["summer_court_pixie_orchard"] = {
        "name": "The Pixie Blossom Orchard",
        "desc": "Ancient apple trees with silver bark and crystal fruits that taste of sunshine and cider. Pixies flit between the branches, giggling and tossing flower petals.",
        "terrain": "forest",
        "exits": {"east": {"dest_id": "summer_court_starlight_promenade", "alias": "e"}},
        "npcs": [{"name": "Pixie Prankster", "desc": "A tiny winged sprite with a pouch of glowing dream-dust.", "level": 16, "role": "rogue"}]
    }

    rooms["summer_court_titania_palace_entrance"] = {
        "name": "The Gossamer Gates of the Emerald Palace",
        "desc": "Soaring palace gates woven entirely from living roses without a single nail or cut timber. The air is warm and filled with the music of harps played by unseen wind spirits.",
        "terrain": "forest",
        "exits": {
            "south": {"dest_id": "summer_court_glade_path_16", "alias": "s"},
            "north": {"dest_id": "summer_court_summer_solstice_hall", "alias": "n"}
        },
        "npcs": [{"name": "Centaur Royal Knight", "desc": "A magnificent white centaur wearing a breastplate of polished sunstone and carrying a gleaming lance.", "level": 22, "role": "warrior"}]
    }

    rooms["summer_court_summer_solstice_hall"] = {
        "name": "The Great Hall of the Summer Solstice",
        "desc": "A vast hall supported by living redwood pillars whose boughs form a canopy woven with silver stars. Eladrin nobles sip honeyed mead in eternal celebration of life.",
        "terrain": "forest",
        "exits": {
            "south": {"dest_id": "summer_court_titania_palace_entrance", "alias": "s"},
            "north": {"dest_id": "summer_court_titania_throne_bower", "alias": "n"}
        },
        "npcs": [{"name": "Archfey Courtier", "desc": "An elegant noble of the Summer Court dressed in robes of gossamer silk that shift color with their mood.", "level": 23, "role": "mage"}]
    }

    rooms["summer_court_titania_throne_bower"] = {
        "name": "The Living Bower Throne of Queen Titania",
        "desc": "The heart of the Summer Court. Seated upon a throne of woven golden briars and white lilies is Queen Titania, surrounded by glowing warmth, eternal youth, and natural majesty.",
        "terrain": "forest",
        "exits": {"south": {"dest_id": "summer_court_summer_solstice_hall", "alias": "s"}},
        "npcs": [{"name": "Queen Titania of the Summer Court", "desc": "The sovereign of the Summer Fey, breathtakingly beautiful with gossamer dragonfly wings and eyes full of summer sun.", "level": 26, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Crown of the Summer Solstice", "desc": "A circlet of living golden briars and blooming fire-orchids that grants radiant charm."},
            {"name": "Bow of Fey Starlight", "desc": "A bow carved of lunar silverwood that shoots arrows of pure starlight."}
        ]
    }

    # 53 connected glade paths, blossom terraces, and canopy walkways
    for i in range(1, 54):
        r_key = f"summer_court_glade_path_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Winding paths beneath ancient weeping willow boughs and sparkling starlight streams. "
            f"The air is fragrant with honeysuckle and eternal warm breezes. [Summer Court Tier #{i}]"
        )
        r_name = f"Summer Court Blossom Path #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"summer_court_glade_path_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"summer_court_glade_path_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"summer_court_glade_path_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"summer_court_glade_path_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "summer_court_starlight_promenade", "alias": "s"}
        if i == 16:
            exits["north"] = {"dest_id": "summer_court_titania_palace_entrance", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "summer_court_summer_solstice_hall", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Dryad of the Oak", "desc": "A tree spirit merged with ancient bark, casting healing verdant spells.", "level": 19, "role": "mage"})
        elif i % 10 == 0:
            npcs.append({"name": "Blink Dog Companion", "desc": "An intelligent hound teleporting playfully between sunbeams.", "level": 18, "role": "warrior"})

        if i == 20:
            items.append({"name": "Cluster of Summer Feyberries", "desc": "Succulent berries that taste like sweet honeydew and restore health."})

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
        "base_coords": (80, 180, 20),
        "rooms": rooms
    }


# =============================================================================
# ZONE 60: THE SHADOWFELL FORTRESS OF MEMORIES [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_shadowfell_raven():
    zone_key = "shadowfell_raven"
    zone_name = "The Shadowfell Fortress of Memories & Raven Queen's Sanctuary"
    rooms = {}

    rooms["shadowfell_raven_black_gate"] = {
        "name": "The Obsidian Gates of the Fortress of Memories",
        "desc": "A monumental gateway carved of black volcanic glass rising into a sky of leaden gray. Flights of shadowy ravens circle the towers, their caws carrying the whispered memories of mortals.",
        "terrain": "stone_dungeon",
        "exits": {"north": {"dest_id": "shadowfell_raven_avenue_of_sorrows", "alias": "n"}},
        "npcs": [{"name": "Shadar-kai Gloom Blade", "desc": "A pale warrior with facial piercings and a chain-whip infused with shadowy cold.", "level": 22, "role": "rogue"}]
    }

    rooms["shadowfell_raven_avenue_of_sorrows"] = {
        "name": "The Avenue of Sorrows",
        "desc": "A basalt causeway flanked by pools of pitch-black water. Within the dark waters, luminous memory spheres drift like glowing pearls, playing scenes of grief, triumph, and death.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "shadowfell_raven_black_gate", "alias": "s"},
            "east": {"dest_id": "shadowfell_raven_memory_pool_vault", "alias": "e"},
            "west": {"dest_id": "shadowfell_raven_sorrowsworn_dungeon", "alias": "w"},
            "north": {"dest_id": "shadowfell_raven_crypt_path_01", "alias": "n"}
        },
        "npcs": [{"name": "Shadar-kai Soul Weaver", "desc": "A dark priestess drawing threads of emotion from drifting memory spheres.", "level": 24, "role": "mage"}]
    }

    rooms["shadowfell_raven_memory_pool_vault"] = {
        "name": "The Vault of Crystal Memories",
        "desc": "Shelves of black obsidian holding thousands of glass urns, each preserving the final memory of an ancient king, fallen hero, or forgotten arcanist.",
        "terrain": "stone_dungeon",
        "exits": {"west": {"dest_id": "shadowfell_raven_avenue_of_sorrows", "alias": "w"}},
        "npcs": [{"name": "Memory Custodian", "desc": "A hooded specter with glowing white eyes cataloging soul memories in silence.", "level": 25, "role": "mage"}],
        "items": [{"name": "Sphere of Heroic Memories", "desc": "A crystal orb containing the courageous final thoughts of an ancient warrior."}]
    }

    rooms["shadowfell_raven_sorrowsworn_dungeon"] = {
        "name": "The Hollow of the Sorrowsworn",
        "desc": "A grim cavern filled with chains of dark iron where physical manifestations of despair and lonely grief stalk in the freezing dark.",
        "terrain": "stone_dungeon",
        "exits": {"east": {"dest_id": "shadowfell_raven_avenue_of_sorrows", "alias": "e"}},
        "npcs": [{"name": "The Lonely Sorrowsworn", "desc": "A grotesque, elongated creature with grasping harpoon-arms seeking warmth from the living.", "level": 26, "role": "warrior"}]
    }

    rooms["shadowfell_raven_inner_keep_gateway"] = {
        "name": "The Inner Spire of Ravenloft",
        "desc": "A towering spire of black crystal carved with motifs of unfurled raven wings. Cold winds sweep through gothic arches carrying the chill of the grave.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "shadowfell_raven_crypt_path_18", "alias": "s"},
            "north": {"dest_id": "shadowfell_raven_grand_hall_of_fate", "alias": "n"}
        },
        "npcs": [{"name": "Raven Knight Champion", "desc": "A heavily armored champion clad in blackened steel decorated with real raven feathers.", "level": 27, "role": "warrior"}]
    }

    rooms["shadowfell_raven_grand_hall_of_fate"] = {
        "name": "The Grand Hall of Inevitable Fate",
        "desc": "A cavernous cathedral where thousands of black ravens perch silently on iron rafters. In the center lies an obsidian reflecting pool that shows the exact moment of mortal demise.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "shadowfell_raven_inner_keep_gateway", "alias": "s"},
            "north": {"dest_id": "shadowfell_raven_throne_of_the_raven_queen", "alias": "n"}
        },
        "npcs": [{"name": "Raven Queen Emissary", "desc": "A spectral entity crowned with silver winter-branches who speaks of destiny and doom.", "level": 28, "role": "mage"}]
    }

    rooms["shadowfell_raven_throne_of_the_raven_queen"] = {
        "name": "The Throne of Frozen Memories",
        "desc": "The supreme sanctum of the Shadowfell fortress. A throne sculpted of unmelting black ice and shadow-feathers, looking out over the endless twilight of the afterlife.",
        "terrain": "stone_dungeon",
        "exits": {"south": {"dest_id": "shadowfell_raven_grand_hall_of_fate", "alias": "s"}},
        "npcs": [{"name": "The Raven Queen's High Sorrow Knight", "desc": "The dreaded champion of the Raven Queen, wielding the Scythe of Frozen Memories and wreathed in chilling gloom.", "level": 29, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Scythe of Frozen Memories", "desc": "A terrifying two-handed scythe carved of black ice that reaps the memories and life of foes."},
            {"name": "Raven's Shadow-Feather Cloak", "desc": "A billowing cloak of midnight feathers that allows step through shadows."}
        ]
    }

    # 53 connected crypt pathways, shadow galleries, and icy corridors
    for i in range(1, 54):
        r_key = f"shadowfell_raven_crypt_path_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Cold corridors of smooth black glass lined with alcoves of silent urns. "
            f"Shadows detach from the walls and drift like wisps of soot. [Fortress Sector #{i}]"
        )
        r_name = f"Fortress of Memories Corridor #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"shadowfell_raven_crypt_path_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"shadowfell_raven_crypt_path_{i+1:02d}", "alias": "n"}
        if i + 6 <= 53:
            exits["east"] = {"dest_id": f"shadowfell_raven_crypt_path_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"shadowfell_raven_crypt_path_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "shadowfell_raven_avenue_of_sorrows", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "shadowfell_raven_inner_keep_gateway", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "shadowfell_raven_grand_hall_of_fate", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Shadow Hound", "desc": "A pitch-black hound with blazing red eyes that prowls through the shadows.", "level": 23, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Shadar-kai Archer", "desc": "A quiet marksman with arrows tipped with shadow-ice.", "level": 24, "role": "rogue"})

        if i == 25:
            items.append({"name": "Raven Queen Ice Relic", "desc": "A piece of unmelting black ice that hums with cold necrotic power."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "stone_dungeon",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "stone_dungeon",
        "base_coords": (-150, -80, -40),
        "rooms": rooms
    }


# =============================================================================
# ZONE 61: THE SUBTERRANEAN DROW UNDERDARK OF CHED NASAD [Level 18-27, 60 Rooms]
# =============================================================================

def build_zone_ched_nasad():
    zone_key = "ched_nasad"
    zone_name = "The Subterranean Drow Underdark of Ched Nasad"
    rooms = {}

    rooms["ched_nasad_web_bridge_rim"] = {
        "name": "The Upper Web Chasm Rim of Ched Nasad",
        "desc": "You stand upon a precipice overlooking a cavernous vertical abyss three miles deep. Spanning the void are thousands of multi-layered, calcified spider-silk bridges shimmering with phosphorescent blue and violet webbing.",
        "terrain": "underdark",
        "exits": {"north": {"dest_id": "ched_nasad_calcified_strand_avenue", "alias": "n"}},
        "npcs": [{"name": "Ched Nasad Drow Sentry", "desc": "A dark elf warrior clad in piwafwi cloak and chitin armor, holding a poisoned hand crossbow.", "level": 19, "role": "rogue"}]
    }

    rooms["ched_nasad_calcified_strand_avenue"] = {
        "name": "The Calcified Silk Strand Avenue",
        "desc": "A broad causeway woven of hardened spider-silk suspended hundreds of feet above the dark cavern floor. Below, the tiered palaces of noble Drow houses glow with fairy-fire.",
        "terrain": "underdark",
        "exits": {
            "south": {"dest_id": "ched_nasad_web_bridge_rim", "alias": "s"},
            "east": {"dest_id": "ched_nasad_drider_pen_sanctuary", "alias": "e"},
            "west": {"dest_id": "ched_nasad_fungal_bazaar", "alias": "w"},
            "north": {"dest_id": "ched_nasad_chasm_web_01", "alias": "n"}
        },
        "npcs": [{"name": "Drow Arachnomancer", "desc": "A male drow sorcerer surrounded by scuttling eight-eyed familiars.", "level": 21, "role": "mage"}]
    }

    rooms["ched_nasad_drider_pen_sanctuary"] = {
        "name": "The Chitin Pens of the Driders",
        "desc": "Stalactite cages suspended in the chasm where cursed driders—centaur-like abominations of drow and spider—are kept as shock troops for the Matron Mothers.",
        "terrain": "underdark",
        "exits": {"west": {"dest_id": "ched_nasad_calcified_strand_avenue", "alias": "w"}},
        "npcs": [{"name": "Cursed Drider Vanguard", "desc": "A towering monstrosity with the torso of a dark elf and the bloated body of a giant black spider.", "level": 23, "role": "warrior"}],
        "items": [{"name": "Vial of Abyssal Spider Venom", "desc": "A concentrated vial of neurotoxic venom harvested from pure-bred Underdark arachnids."}]
    }

    rooms["ched_nasad_fungal_bazaar"] = {
        "name": "The Glowing Fungal Bazaar",
        "desc": "A bustling market built along a massive mushroom shelf. Merchants trade deep-cavern truffles, glowing spore potions, and fine adamantine daggers under iridescent violet caps.",
        "terrain": "underdark",
        "exits": {"east": {"dest_id": "ched_nasad_calcified_strand_avenue", "alias": "e"}},
        "npcs": [{"name": "Deep Duergar Merchant", "desc": "A gray dwarf blacksmith haggling over adamantine weapons.", "level": 20, "role": "civilian"}]
    }

    rooms["ched_nasad_great_web_fane"] = {
        "name": "The Great Web Fane of Lolth",
        "desc": "A temple woven from iridescent spider-silk suspended directly in the center of the cavern abyss. Statues of the Spider Queen with eight weeping obsidian eyes line the sanctuary.",
        "terrain": "underdark",
        "exits": {
            "south": {"dest_id": "ched_nasad_chasm_web_18", "alias": "s"},
            "north": {"dest_id": "ched_nasad_matron_mother_council_hall", "alias": "n"}
        },
        "npcs": [{"name": "High Priestess of Lolth", "desc": "A cruel drow noblewoman in spider-silk vestments holding a scourge with five living viper heads.", "level": 25, "role": "mage"}]
    }

    rooms["ched_nasad_matron_mother_council_hall"] = {
        "name": "The Council Hall of the Ruling Houses",
        "desc": "An opulent throne room carved from a hollow stalactite hanging from the cavern ceiling. Tapestries of silver spider-web depict the fall and destruction of Ched Nasad's rivals.",
        "terrain": "underdark",
        "exits": {
            "south": {"dest_id": "ched_nasad_great_web_fane", "alias": "s"},
            "north": {"dest_id": "ched_nasad_throne_of_the_web_mother", "alias": "n"}
        },
        "npcs": [{"name": "First House Swordmaster", "desc": "A master dual-blade fencer whose twin rapier strikes are as fast as striking vipers.", "level": 26, "role": "warrior"}]
    }

    rooms["ched_nasad_throne_of_the_web_mother"] = {
        "name": "The Throne of the Supreme Matron Mother",
        "desc": "The highest seat of power in Ched Nasad. Carved from the skull of a subterranean purple worm, the throne commands a dizzying view of the entire city of shimmering webs.",
        "terrain": "underdark",
        "exits": {"south": {"dest_id": "ched_nasad_matron_mother_council_hall", "alias": "s"}},
        "npcs": [{"name": "Matron Mother of the Web-Sisters", "desc": "The ruthless matriarch of Ched Nasad, draped in gossamer webs and wielding a venom-dripping spider-fang dagger.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Spider-Fang Dagger of Lolth", "desc": "A jagged dagger carved from the pedipalp of a demon spider that injects agonizing necrotic poison."},
            {"name": "Silk-Weave Robes of Ched Nasad", "desc": "Enchanted robes of gossamer spider-silk that grant magic resistance and silent movement."}
        ]
    }

    # 53 connected web chasm bridges, fungal ledges, and drow alleys
    for i in range(1, 54):
        r_key = f"ched_nasad_chasm_web_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Suspended calcified silk bridges swaying gently over the yawning three-mile abyss. "
            f"Phosphorescent fungal spores drift through the still, humid Underdark air. [Ched Nasad Strand #{i}]"
        )
        r_name = f"Ched Nasad Silk Strand #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"ched_nasad_chasm_web_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"ched_nasad_chasm_web_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"ched_nasad_chasm_web_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"ched_nasad_chasm_web_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "ched_nasad_calcified_strand_avenue", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "ched_nasad_great_web_fane", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "ched_nasad_matron_mother_council_hall", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Giant Phase Spider", "desc": "A terrifying predator that blinks in and out of the ethereal plane to ambush prey.", "level": 22, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Ched Nasad Infiltrator", "desc": "A stealthy drow assassin creeping across the webs with silent footsteps.", "level": 24, "role": "rogue"})

        if i == 28:
            items.append({"name": "Spool of Calcified Spider-Silk", "desc": "A spool of thread lighter than cotton but stronger than forged steel."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "underdark",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "underdark",
        "base_coords": (-180, 140, -80),
        "rooms": rooms
    }


# =============================================================================
# MARITIME ROUTE HELPER
# =============================================================================

def register_gossamer_swan_ferry_routes():
    """Ensures The Fey-Barge 'The Gossamer Swan' is registered in sailing.FERRY_ROUTES."""
    if "gossamer_swan_barge" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["gossamer_swan_barge"] = {
            "key": "gossamer_swan_barge",
            "name": 'The Fey-Barge "The Gossamer Swan"',
            "operator": "Eladrin Swan-Keeper Liriel",
            "operator_title": "Navigator of the Enchanted Waterways",
            "ports": ["south_docks", "whispering_silt_islet", "summer_court_emerald_gateway", "summer_court_gateway"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "whispering_silt_islet": "Whispering Silt Islet",
                "summer_court_emerald_gateway": "The Emerald Gateway of the Summer Court",
                "summer_court_gateway": "The Emerald Gateway of the Summer Court"
            },
            "fares": {
                ("south_docks", "summer_court_emerald_gateway"): 75,
                ("summer_court_emerald_gateway", "south_docks"): 75,
                ("whispering_silt_islet", "summer_court_emerald_gateway"): 50,
                ("summer_court_emerald_gateway", "whispering_silt_islet"): 50,
                ("south_docks", "summer_court_gateway"): 75,
                ("summer_court_gateway", "south_docks"): 75,
                ("whispering_silt_islet", "summer_court_gateway"): 50,
                ("summer_court_gateway", "whispering_silt_islet"): 50
            },
            "desc": "A magnificent barge sculpted of pearlescent white wood in the likeness of a crowned swan, propelled silently over starlight waters by giant iridescent wings.",
            "deck_key": "gossamer_swan_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 15
# =============================================================================

def run_bulk_ingestion_part15(clean_existing=False):
    """
    Executes Part 15 of the bulk world expansion ("3,250+ Rooms Grand Expansion"):
    - The Clockwork Nirvana of Mechanus & Modron Cathedral (60 rooms)
    - The Feywild Summer Court & Palace of Queen Titania (60 rooms)
    - The Shadowfell Fortress of Memories & Raven Queen's Sanctuary (60 rooms)
    - The Subterranean Drow Underdark of Ched Nasad (60 rooms)
    Plus The Fey-Barge 'The Gossamer Swan' weather deck (1 room).
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
        build_zone_mechanus_gears,
        build_zone_summer_court,
        build_zone_shadowfell_raven,
        build_zone_ched_nasad
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("mechanus_gears", "mechanus_planetary_gear_platform", "rail_hub", "step into interlocking gear portal to mechanus", "step off planetary gear back to subterranean rail hub"),
        ("summer_court", "summer_court_emerald_gateway", "deep_woods", "pass through whispering willow archway into summer court", "return through willow arch back to deep woods"),
        ("shadowfell_raven", "shadowfell_raven_black_gate", "ossuary", "pass into shadow rift towards fortress of memories", "return through obsidian archway back to sunken ossuary"),
        ("ched_nasad", "ched_nasad_web_bridge_rim", "chasm_bridge", "descend web strands into chasm of ched nasad", "ascend calcified webs back to chasm bridge")
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

    # 4. Register Gossamer Swan Ferry Route & Weather Deck
    gossamer_swan_deck = find_room_by_key("gossamer_swan_deck")
    if not gossamer_swan_deck:
        gossamer_swan_deck = create_object(Room, key='The Fey-Barge "The Gossamer Swan" - Weather Deck', tags=[TAG_WORLD])
        gossamer_swan_deck.tags.add("gossamer_swan_deck", category="room_key")
        gossamer_swan_deck.tags.add("summer_court", category="zone")
        gossamer_swan_deck.db.room_key = "gossamer_swan_deck"
        gossamer_swan_deck.db.desc = (
            "You stand upon the pearlescent swan-carved deck of the fey barge. "
            "Giant wings of iridescent silver-white feather glide silently over starlight currents, "
            "leaving ripples of glowing cyan light across the waters."
        )
        gossamer_swan_deck.db.zone = "Fey Enchanted Waters"
        gossamer_swan_deck.db.terrain = "water_swim"
        gossamer_swan_deck.db.coords = (80, 150, 10)
        report["rooms_created"] += 1

    register_gossamer_swan_ferry_routes()
    report["ferry_routes_added"].append('The Fey-Barge "The Gossamer Swan" (south_docks <-> whispering_silt_islet <-> summer_court_emerald_gateway)')

    return report

