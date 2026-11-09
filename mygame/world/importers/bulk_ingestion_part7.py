"""
Bulk World Ingestion Engine — Part 7: The Sunken Citadel, High Sorcery, Camelot & Duergar Deeps

Expands Eldoria with an additional 251 rooms across 4 legendary adventure realms:
1. The Sunken Citadel & Twilight Grove (Classic low-level dungeon crawler) [Level 2-6, 60 Rooms]
2. The High Tower of High Sorcery & Astral Observatory (Arcane apex of wizards) [Level 16-25, 60 Rooms]
3. The Arthurian Realm of Camelot & Mystical Avalon (Knights of the Round Table) [Level 12-20, 65 Rooms]
4. The Sunken Duergar Deep City & Magma Forges (Dark Dwarven underground empire) [Level 15-23, 65 Rooms]

Total Rooms Created in Part 7: 251 Rooms
Cumulative World Total: 1,002 + 251 = 1,253 Rooms!

Features:
- New 'The Avalon Mist-Barge Nimue's Blessing' maritime ferry route
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
# ZONE 26: THE SUNKEN CITADEL & TWILIGHT GROVE [Level 2-6, 60 Rooms]
# =============================================================================

def build_zone_sunken_citadel():
    zone_key = "sunken_citadel"
    zone_name = "The Sunken Citadel & Twilight Grove"
    rooms = {}

    rooms["sunken_citadel_chasm_ledge"] = {
        "name": "The Ravine Ledge of the Sunken Citadel",
        "desc": "A vast fissure in the earth drops into darkness. A cracked stone stairway leads down to the submerged towers of a forgotten fortress buried by an ancient cataclysm.",
        "terrain": "mountain",
        "exits": {"down": {"dest_id": "citadel_courtyard", "alias": "d"}},
        "npcs": [{"name": "Giant Fire Beetle", "desc": "A two-foot beetle whose luminous glands glow with steady orange light.", "level": 2, "role": "warrior"}]
    }

    rooms["citadel_courtyard"] = {
        "name": "The Cracked Fortress Courtyard",
        "desc": "Piles of collapsed masonry and rubble litter a cavernous underground courtyard. Faint sounds of yipping kobolds echo from the western tunnels.",
        "terrain": "catacombs",
        "exits": {"up": {"dest_id": "sunken_citadel_chasm_ledge", "alias": "u"}, "west": {"dest_id": "kobold_throne_room", "alias": "w"}, "east": {"dest_id": "goblin_chief_hall", "alias": "e"}, "down": {"dest_id": "twilight_grove_chasm", "alias": "d"}}
    }

    rooms["kobold_throne_room"] = {
        "name": "The Throne of Yusdrayl the Kobold Queen",
        "desc": "A dilapidated stone altar serves as a throne for the reptilian kobold queen. Offering bowls of rat tails and copper coins surround her dais.",
        "terrain": "catacombs",
        "exits": {"east": {"dest_id": "citadel_courtyard", "alias": "e"}, "south": {"dest_id": "citadel_room_01", "alias": "s"}},
        "npcs": [{"name": "Yusdrayl the Kobold Queen", "desc": "A cunning red-scaled kobold sorceress wielding a tiny dragon-fang wand.", "level": 4, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Dragon-Fang Wand of Sparking", "desc": "A wand carved from a juvenile red dragon tooth that casts sparks."}]
    }

    rooms["goblin_chief_hall"] = {
        "name": "The Hall of Chieftain Durnn",
        "desc": "Durnn the hobgoblin has conquered this wing of the fortress, setting up barricades and cages for prisoners.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "citadel_courtyard", "alias": "w"}, "north": {"dest_id": "citadel_room_15", "alias": "n"}},
        "npcs": [{"name": "Chieftain Durnn the Hobgoblin", "desc": "A burly hobgoblin in chainmail clutching a spiked iron morningstar.", "level": 5, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Durnn's Spiked Morningstar", "desc": "A brutal steel morningstar that fractures bone."}]
    }

    rooms["twilight_grove_chasm"] = {
        "name": "The Descent to the Twilight Grove",
        "desc": "A humid subterranean cavern filled with bioluminescent fungi and pale, twisted root networks.",
        "terrain": "forest",
        "exits": {"up": {"dest_id": "citadel_courtyard", "alias": "u"}, "south": {"dest_id": "gulthias_tree_heart", "alias": "s"}},
        "npcs": [{"name": "Twig Blight Pack", "desc": "Thorny, ambulatory wooden humanoids with needle-sharp claws.", "level": 3, "role": "rogue"}]
    }

    rooms["gulthias_tree_heart"] = {
        "name": "The Heart of the Gulthias Tree",
        "desc": "In the center of the subterranean grove rises the Gulthias Tree, a horrific twisted monstrosity with blood-red sap and writhing roots.",
        "terrain": "forest",
        "exits": {"north": {"dest_id": "twilight_grove_chasm", "alias": "n"}},
        "npcs": [{"name": "Belak the Outcast Druid", "desc": "A fallen druid with madness in his eyes, tending the vampire tree.", "level": 6, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Wand of Entangling Briars", "desc": "A staff crafted from the Gulthias Tree that causes grasping roots to erupt."}]
    }

    # 54 Citadel chambers and catacombs to reach 60 rooms
    for i in range(1, 55):
        r_key = f"citadel_room_{i:02d}"
        if r_key in rooms:
            continue
        
        terrain = "forest" if i > 35 else "catacombs"
        desc = (
            f"Ancient masonry arches cracked by geological tremors. "
            f"Fungi sprout in the crevices of damp flagstones. [Room #{i}]"
        )
        r_name = f"Sunken Citadel Chamber #{i}"
        
        exits = {}
        if i > 1:
            exits["west"] = {"dest_id": f"citadel_room_{i-1:02d}", "alias": "w"}
        if i < 54:
            exits["east"] = {"dest_id": f"citadel_room_{i+1:02d}", "alias": "e"}
        if i + 6 <= 54:
            exits["north"] = {"dest_id": f"citadel_room_{i+6:02d}", "alias": "n"}
        if i - 6 >= 1:
            exits["south"] = {"dest_id": f"citadel_room_{i-6:02d}", "alias": "s"}

        if i == 1:
            exits["north"] = {"dest_id": "kobold_throne_room", "alias": "n"}
        if i == 15:
            exits["south"] = {"dest_id": "goblin_chief_hall", "alias": "s"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Kobold Slinger", "desc": "A scaly skirmisher hurling clay pots of burning pitch.", "level": 3, "role": "rogue"})
        elif i % 8 == 0:
            npcs.append({"name": "Goblin Warrior", "desc": "A snarling goblin with a wooden shield and shortspear.", "level": 3, "role": "warrior"})

        if i == 10:
            items.append({"name": "Silver Dragon Key of the Citadel", "desc": "A key shaped like a rearing dragon."})

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
        "base_coords": (30, -20, -15),
        "rooms": rooms
    }


# =============================================================================
# ZONE 27: THE HIGH TOWER OF HIGH SORCERY [Level 16-25, 60 Rooms]
# =============================================================================

def build_zone_tower_sorcery():
    zone_key = "tower_sorcery"
    zone_name = "The High Tower of High Sorcery"
    rooms = {}

    rooms["tower_sorcery_shoikan_grove"] = {
        "name": "The Shrouded Shoikan Grove",
        "desc": "A chilling grove of spectral black aspens that instills paralyzing dread in mortal hearts. Ethereal mists dance between the dark trunks.",
        "terrain": "forest",
        "exits": {"north": {"dest_id": "tower_silver_gates", "alias": "n"}},
        "npcs": [{"name": "Grove Shadow Guardian", "desc": "An incorporeal apparition born of ancient protective curses.", "level": 16, "role": "warrior"}]
    }

    rooms["tower_silver_gates"] = {
        "name": "The Gates of Silver and Obsidian",
        "desc": "Two colossal doors carved of single blocks of obsidian inlaid with shimmering silver runes of warding. The tower walls soar thousands of feet into the sky.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "tower_sorcery_shoikan_grove", "alias": "s"}, "north": {"dest_id": "grand_library_scrolls", "alias": "n"}}
    }

    rooms["grand_library_scrolls"] = {
        "name": "The Infinite Library of Lost Arcanum",
        "desc": "Spiral galleries ascending into vaulted heights, holding millions of leather-bound grimoires, illuminated spellbooks, and glowing astral scrolls.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "tower_silver_gates", "alias": "s"}, "up": {"dest_id": "elemental_summoning_ring", "alias": "u"}, "east": {"dest_id": "tower_chamber_01", "alias": "e"}},
        "npcs": [{"name": "Archmage Lector", "desc": "A venerable mage floating three feet off the ground reading three scrolls at once.", "level": 18, "role": "mage"}],
        "items": [{"name": "Tome of Masterful Transmutation", "desc": "A heavy leather grimoire filled with complex alchemical formulas."}]
    }

    rooms["elemental_summoning_ring"] = {
        "name": "The Planar Crucible of Elements",
        "desc": "A brass ring set into white marble floor tiles, burning with controlled plumes of elemental fire, water, earth, and air.",
        "terrain": "indoors",
        "exits": {"down": {"dest_id": "grand_library_scrolls", "alias": "d"}, "up": {"dest_id": "astral_orrery_chamber", "alias": "u"}},
        "npcs": [{"name": "Bound Fire Elemental", "desc": "A swirling vortex of white-hot magical flame bound by runic chains.", "level": 20, "role": "mage"}]
    }

    rooms["astral_orrery_chamber"] = {
        "name": "The Great Astral Orrery",
        "desc": "Gleaming brass spheres representing planes and stars spin in complex clockwork orbits beneath a dome of magical starlight.",
        "terrain": "air",
        "exits": {"down": {"dest_id": "elemental_summoning_ring", "alias": "d"}, "up": {"dest_id": "apex_archmage_sanctum", "alias": "u"}},
        "items": [{"name": "Brass Astral Astrolabe", "desc": "A navigational device that measures planar alignments and celestial currents."}]
    }

    rooms["apex_archmage_sanctum"] = {
        "name": "The High Apex of the Master of Sorcery",
        "desc": "The highest sanctuary in the tower, commanding panoramic vistas of the heavens. In the center stands the legendary Master of Past and Present.",
        "terrain": "indoors",
        "exits": {"down": {"dest_id": "astral_orrery_chamber", "alias": "d"}},
        "npcs": [{"name": "Archmage Raistlin Majere", "desc": "The master of the tower, wearing robes of black velvet, golden hourglass eyes gleaming with ancient sorrow and terrifying ambition.", "level": 25, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Staff of Magius", "desc": "A gnarled wooden staff crowned with a golden dragon claw clutching a crystal orb of pure arcane light."}]
    }

    # 54 Tower laboratory, spire and hall rooms to reach 60 rooms
    for i in range(1, 55):
        r_key = f"tower_chamber_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Polished marble walls reflecting the soft magical luminescence of floating lanterns. "
            f"Shelves of glowing alchemical vials line the walls. [Tower Room #{i}]"
        )
        r_name = f"Tower of Sorcery Alcove #{i}"
        
        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"tower_chamber_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"tower_chamber_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["up"] = {"dest_id": f"tower_chamber_{i+5:02d}", "alias": "u"}
        if i - 5 >= 1:
            exits["down"] = {"dest_id": f"tower_chamber_{i-5:02d}", "alias": "d"}

        if i == 1:
            exits["west"] = {"dest_id": "grand_library_scrolls", "alias": "w"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Arcane Homunculus", "desc": "A winged clay creature carrying delicate potion vials.", "level": 17, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Spectral Battlemage", "desc": "A spectral warrior casting incandescent lightning spears.", "level": 19, "role": "mage"})

        if i == 25:
            items.append({"name": "Scroll of Time Manipulation", "desc": "An ancient parchment inscribed in gold ink."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "indoors",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "indoors",
        "base_coords": (-10, 45, 30),
        "rooms": rooms
    }


# =============================================================================
# ZONE 28: THE ARTHURIAN REALM OF CAMELOT [Level 12-20, 65 Rooms]
# =============================================================================

def build_zone_camelot():
    zone_key = "camelot_realm"
    zone_name = "The Arthurian Realm of Camelot"
    rooms = {}

    rooms["camelot_realm_tournament_meadow"] = {
        "name": "The Grand Tournament Meadow of Camelot",
        "desc": "Brightly colored pavilions of silk and heraldic pennants flutter in the summer breeze. Knightly lists and wooden jousting barriers stretch across lush turf.",
        "terrain": "field",
        "exits": {"north": {"dest_id": "camelot_outer_barbican", "alias": "n"}},
        "npcs": [{"name": "Knight Errant of Camelot", "desc": "A noble knight in polished plate mail bearing a red lion crest upon his shield.", "level": 12, "role": "warrior"}]
    }

    rooms["camelot_outer_barbican"] = {
        "name": "The Great Barbican of King Arthur",
        "desc": "Soaring white stone ramparts and portcullises protect the approach to the legendary citadel. Guard banners snap in the wind.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "camelot_realm_tournament_meadow", "alias": "s"}, "north": {"dest_id": "round_table_hall", "alias": "n"}, "west": {"dest_id": "merlin_crystal_cave", "alias": "w"}}
    }

    rooms["round_table_hall"] = {
        "name": "The Great Hall of the Round Table",
        "desc": "In the center of this majestic hall of white marble stands the legendary Round Table, encircled by fifty chairs of carved oak bearing the gold names of the realm's greatest knights.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "camelot_outer_barbican", "alias": "s"}, "east": {"dest_id": "camelot_room_01", "alias": "e"}, "north": {"dest_id": "camelot_realm_avalon_ferry_dock", "alias": "n"}},
        "npcs": [{"name": "King Arthur Pendragon", "desc": "The High King of Britain, crowned in gold and wearing royal crimson, with sovereign authority in his eyes.", "level": 20, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "The Excalibur Blade of King Arthur", "desc": "The mythical sword of the rightful king, its blade shining with blinding solar brilliance."}]
    }

    rooms["merlin_crystal_cave"] = {
        "name": "The Crystal Grotto of Merlin the Enchanter",
        "desc": "Gleaming amethyst stalactites and glowing pools of prophecy illuminate the subterranean workshop of the master enchanter.",
        "terrain": "catacombs",
        "exits": {"east": {"dest_id": "camelot_outer_barbican", "alias": "e"}},
        "npcs": [{"name": "Merlin the Enchanter", "desc": "The legendary druidic archmage holding an oak wand and reading ancient dragon prophecies.", "level": 20, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Oak Wand of Merlin", "desc": "A wand carved from sacred Glastonbury oak that channels prophetic visions."}]
    }

    rooms["camelot_realm_avalon_ferry_dock"] = {
        "name": "The Shrouded Pier of Avalon",
        "desc": "A white timber pier extending into a calm enchanted lake shrouded in perpetual silver mist. The water is smooth as glass.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "round_table_hall", "alias": "s"}, "north": {"dest_id": "isle_of_avalon_shrine", "alias": "n"}}
    }

    rooms["isle_of_avalon_shrine"] = {
        "name": "The Sacred Apple Blossom Isle of Avalon",
        "desc": "A paradise of eternal spring where golden apple trees blossom perpetually and wounds are healed by sacred lake maidens.",
        "terrain": "field",
        "exits": {"south": {"dest_id": "camelot_realm_avalon_ferry_dock", "alias": "s"}},
        "items": [{"name": "Golden Apple of Avalon", "desc": "An apple that restores health and removes all mortal afflictions."}]
    }

    # 59 Camelot castle, garden, and lake rooms to reach 65 rooms
    for i in range(1, 60):
        r_key = f"camelot_room_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"White limestone corridors hung with tapestries of knighthood and the Holy Grail. "
            f"Tall arched lancet windows look out over green meadows. [Castle Room #{i}]"
        )
        r_name = f"Camelot Chamber #{i}"
        
        exits = {}
        if i > 1:
            exits["west"] = {"dest_id": f"camelot_room_{i-1:02d}", "alias": "w"}
        if i < 59:
            exits["east"] = {"dest_id": f"camelot_room_{i+1:02d}", "alias": "e"}
        if i + 5 <= 59:
            exits["north"] = {"dest_id": f"camelot_room_{i+5:02d}", "alias": "n"}
        if i - 5 >= 1:
            exits["south"] = {"dest_id": f"camelot_room_{i-5:02d}", "alias": "s"}

        if i == 1:
            exits["west"] = {"dest_id": "round_table_hall", "alias": "w"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Camelot Royal Guard", "desc": "A disciplined man-at-arms in polished steel.", "level": 14, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Court Minstrel", "desc": "A musician playing a silver lute.", "level": 12, "role": "bard"})

        if i == 15:
            items.append({"name": "Shield of the White Hart", "desc": "A heater shield decorated with the legendary white hart."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "indoors",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "city",
        "base_coords": (25, 30, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 29: SUNKEN DUERGAR DEEP CITY & MAGMA FORGES [Level 15-23, 65 Rooms]
# =============================================================================

def build_zone_duergar():
    zone_key = "duergar_deep_city"
    zone_name = "The Sunken Duergar Deep City & Magma Forges"
    rooms = {}

    rooms["duergar_deep_city_obsidian_gate"] = {
        "name": "The Obsidian Sentry Bastion",
        "desc": "A terrifying fortress gate carved directly out of natural black obsidian. Spikes of grey steel and steam vents bristle along the battlements.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "duergar_slave_quarry", "alias": "s"}},
        "npcs": [{"name": "Duergar Ironclad Sentry", "desc": "A gray-skinned dwarf warrior in spiked black iron armor with a heavy crossbow.", "level": 15, "role": "warrior"}]
    }

    rooms["duergar_slave_quarry"] = {
        "name": "The Deep Slave Quarry of Duergar",
        "desc": "A tiered cavern where chained miners hack at veins of black iron under the cruel whips of gray dwarf taskmasters.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "duergar_deep_city_obsidian_gate", "alias": "n"}, "east": {"dest_id": "magma_furnace_crucible", "alias": "e"}},
        "npcs": [{"name": "Duergar Taskmaster", "desc": "A cruel gray dwarf wielding a barbed leather whip.", "level": 16, "role": "warrior"}]
    }

    rooms["magma_furnace_crucible"] = {
        "name": "The Great Magma Forge Crucible",
        "desc": "Rivers of liquid magma are channeled through stone sluices to heat gargantuan blast furnaces. Automated trip-hammers strike hot steel with deafening thunder.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "duergar_slave_quarry", "alias": "w"}, "south": {"dest_id": "throne_deep_king_horgar", "alias": "s"}, "east": {"dest_id": "illithid_embassy_chamber", "alias": "e"}},
        "npcs": [{"name": "Magma Forge Golem", "desc": "An animated iron automaton fueled by an internal furnace of liquid magma.", "level": 18, "role": "warrior"}]
    }

    rooms["throne_deep_king_horgar"] = {
        "name": "The Iron Throne of Deep King Horgar",
        "desc": "Carved of blackened meteoric iron, the throne of King Horgar rises above a platform of skulls. Gray dwarf nobles in spiked plate kneel in fearful obedience.",
        "terrain": "indoors",
        "exits": {"north": {"dest_id": "magma_furnace_crucible", "alias": "n"}, "south": {"dest_id": "duergar_room_01", "alias": "s"}},
        "npcs": [{"name": "Deep King Horgar Steelshadow", "desc": "The supreme tyrant of the Duergar empire, an invisible psionic powerhouse clad in adamantine plate.", "level": 23, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "War-Pick of Deep Earthquakes", "desc": "A heavy mattock that triggers miniature tectonic shockwaves upon impact."}]
    }

    rooms["illithid_embassy_chamber"] = {
        "name": "The Psionic Enclave of the Mind Flayers",
        "desc": "A strange alien chamber of slick purple architecture. Illithid ambassadors with purple tentacles hover above pools of brain brine.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "magma_furnace_crucible", "alias": "w"}},
        "npcs": [{"name": "Elder Brain Ambassador", "desc": "A tentacled mind flayer clad in rubbery alien robes, radiating crushing telepathic waves.", "level": 21, "role": "boss", "danger_tier": "boss"}],
        "items": [{"name": "Psionic Mind-Shielding Circlet", "desc": "A circlet of silver wire that repels psychic shocks and mind control."}]
    }

    # 60 Duergar tunnels, barracks, and smelters to reach 65 rooms
    for i in range(1, 61):
        r_key = f"duergar_room_{i:02d}"
        if r_key in rooms:
            continue
        
        desc = (
            f"Black stone streets carved into the subterranean deeps. "
            f"Vents of sulfuric smoke vent from ceiling grates. [Duergar Sector #{i}]"
        )
        r_name = f"Duergar Deep Vault #{i}"
        
        exits = {}
        if i > 1:
            exits["north"] = {"dest_id": f"duergar_room_{i-1:02d}", "alias": "n"}
        if i < 60:
            exits["south"] = {"dest_id": f"duergar_room_{i+1:02d}", "alias": "s"}
        if i + 5 <= 60:
            exits["east"] = {"dest_id": f"duergar_room_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"duergar_room_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["north"] = {"dest_id": "throne_deep_king_horgar", "alias": "n"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Duergar Crossbow Sniper", "desc": "An invisible sniper waiting in ceiling shadows.", "level": 16, "role": "rogue"})
        elif i % 9 == 0:
            npcs.append({"name": "Subterranean Steeder Spider", "desc": "A giant hunting spider used by the duergar as war mounts.", "level": 17, "role": "warrior"})

        if i == 20:
            items.append({"name": "Ingot of Dark Smelted Iron", "desc": "Heavy ore refined in the magma crucibles."})

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
        "base_coords": (40, 70, -45),
        "rooms": rooms
    }


# =============================================================================
# INGESTION RUNNER & REGISTRATION
# =============================================================================

def register_avalon_ferry_routes():
    """Register the Avalon Mist-Barge transit route."""
    if "avalon_barge" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["avalon_barge"] = {
            "key": "avalon_barge",
            "name": 'The Avalon Mist-Barge "Nimue\'s Blessing"',
            "operator": "Nimue the Lake Maiden",
            "operator_title": "Enchantress of the Sacred Waters",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "camelot_realm_avalon_ferry_dock", "avalon_dock"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "camelot_realm_avalon_ferry_dock": "The Shrouded Pier of Avalon",
                "avalon_dock": "The Shrouded Pier of Avalon"
            },
            "fares": {
                ("south_docks", "camelot_realm_avalon_ferry_dock"): 65,
                ("camelot_realm_avalon_ferry_dock", "south_docks"): 65,
                ("praxis_province_praxis_harbor", "camelot_realm_avalon_ferry_dock"): 55,
                ("camelot_realm_avalon_ferry_dock", "praxis_province_praxis_harbor"): 55,
                ("south_docks", "avalon_dock"): 65,
                ("avalon_dock", "south_docks"): 65,
                ("praxis_province_praxis_harbor", "avalon_dock"): 55,
                ("avalon_dock", "praxis_province_praxis_harbor"): 55
            },
            "desc": "A graceful white-wood barge propelled silently through enchanted lake mists by silver oars.",
            "deck_key": "avalon_barge_deck"
        }


def run_bulk_ingestion_part7(clean_existing=False):
    """
    Executes Part 7 of the bulk world expansion:
    - The Sunken Citadel & Twilight Grove (60 rooms)
    - The High Tower of High Sorcery (60 rooms)
    - The Arthurian Realm of Camelot (65 rooms)
    - The Sunken Duergar Deep City (65 rooms)
    Total: 251 rooms (including the Avalon Mist-Barge weather deck)!
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
        build_zone_sunken_citadel,
        build_zone_tower_sorcery,
        build_zone_camelot,
        build_zone_duergar
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("sunken_citadel", "sunken_citadel_chasm_ledge", "foothills", "descend into cracked ravine", "climb out of cracked ravine"),
        ("tower_sorcery", "tower_sorcery_shoikan_grove", "watchtower", "enter grove of shadows", "exit grove of shadows"),
        ("camelot_realm", "camelot_realm_tournament_meadow", "north_gate", "ride toward camelot", "ride toward eldoria gate"),
        ("duergar_deep_city", "duergar_deep_city_obsidian_gate", "khazad_deeps_great_gates", "descend into duergar chasm", "ascend toward dwarven gates")
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

    # 4. Register Avalon Mist-Barge Route & Weather Deck
    avalon_deck = find_room_by_key("avalon_barge_deck")
    if not avalon_deck:
        avalon_deck = create_object(Room, key='The Avalon Mist-Barge "Nimue\'s Blessing" - Weather Deck', tags=[TAG_WORLD])
        avalon_deck.tags.add("avalon_barge_deck", category="room_key")
        avalon_deck.tags.add("camelot_realm", category="zone")
        avalon_deck.db.room_key = "avalon_barge_deck"
        avalon_deck.db.desc = (
            "You stand upon the silver-inlaid deck of the enchanted Avalon barge. "
            "Wisps of fragrant white mist curl over the smooth water as invisible oarsmen "
            "row silently toward the sacred isle."
        )
        avalon_deck.db.zone = "Lake of Avalon"
        avalon_deck.db.terrain = "water_swim"
        avalon_deck.db.coords = (25, 35, 0)
        report["rooms_created"] += 1

    register_avalon_ferry_routes()
    report["ferry_routes_added"].append('The Avalon Mist-Barge "Nimue\'s Blessing" (south_docks <-> praxis_harbor <-> avalon_dock)')

    return report

