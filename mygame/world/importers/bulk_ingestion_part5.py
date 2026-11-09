"""
Bulk World Ingestion Engine — Part 5: The Primordial Jungles, Lost Pharaohs & Abyssal Rift

Expands Eldoria with an additional 121 rooms across 4 high-tier adventure realms:
1. The Primeval Jungle of Chult & Forbidden Ruins of Omu (Dino-infested canopy & trickster shrines) [Level 12-18]
2. The Necropolis of Anubis & Valley of the Pharaohs (Ancient tomb pyramids & golden sarcophagi) [Level 15-22]
3. The Feywild: Moonlit Court of the Summer Queen (Enchanted crystalline glades & Seelie nobles) [Level 16-24]
4. The Abyssal Rift of the Demonweb Pits (Endgame 66th Layer of the Abyss & Web Throne) [Level 24-30]

Features:
- New 'Aether-Skyship Zephyr's Pride' high-altitude dirigible transit route
- 100% GMCP Room.Info automapper telemetry
- Fixed danger ratings, full Nightmare LPmud combat sheets, mythic artifacts
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
# ZONE 18: PRIMEVAL JUNGLE OF CHULT & RUINS OF OMU [Level 12-18, 30 Rooms]
# =============================================================================

def build_zone_chult():
    return {
        "zone_key": "chult_jungle",
        "zone_name": "The Primeval Jungle of Chult & Ruins of Omu",
        "default_terrain": "forest",
        "base_coords": (45, -35, 0),
        "rooms": {
            "river_mouth": {
                "name": "The River Olung Estuary",
                "desc": "Muddy river water churns into the ocean foam beneath dense jungle foliage. Mangrove roots arch like dragon ribs out of the swampy shallows, and exotic birds shriek overhead.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "dinosaur_basin", "alias": "n"}, "east": {"dest_id": "chult_waterfall_mist", "alias": "e"}},
                "npcs": [{"name": "River Crocodile", "desc": "A twenty-foot reptile basking on a mudbank with teeth like daggers.", "level": 12, "role": "warrior"}]
            },
            "dinosaur_basin": {
                "name": "The Raptor Basin",
                "desc": "Lush ferns and towering cycad trees surround a muddy watering hole. Deep clawed three-toed footprints crisscross the moist earth.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "river_mouth", "alias": "s"}, "north": {"dest_id": "canopy_rope_bridge", "alias": "n"}, "east": {"dest_id": "tar_pits_chult", "alias": "e"}},
                "npcs": [{"name": "Deinonychus Pack-Hunter", "desc": "A feathered predatory dinosaur with a sickle claw cocked and ready to strike.", "level": 13, "role": "rogue"}]
            },
            "tar_pits_chult": {
                "name": "The Bubbling Petroleum Tar Pits",
                "desc": "Vast pools of noxious black pitch bubble and belch choking gas. Prehistoric beast skeletons protrude from the sticky tar.",
                "terrain": "field",
                "exits": {"west": {"dest_id": "dinosaur_basin", "alias": "w"}, "north": {"dest_id": "firenewt_cavern", "alias": "n"}},
                "items": [{"name": "Chunk of Hardened Amber Pitch", "desc": "A fossilized resin containing ancient primeval insects."}]
            },
            "canopy_rope_bridge": {
                "name": "The Moss-Draped Rope Bridge",
                "desc": "Swaying vine cables and teak planks stretch across a four-hundred-foot jungle chasm. Mist swirls through giant banyan branches.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "dinosaur_basin", "alias": "s"}, "north": {"dest_id": "ziggurat_approach", "alias": "n"}, "west": {"dest_id": "witch_tree_grove", "alias": "w"}},
                "npcs": [{"name": "Pteranodon Stalker", "desc": "A winged reptile gliding silently along the updrafts searching for prey.", "level": 13, "role": "warrior"}]
            },
            "witch_tree_grove": {
                "name": "Heart of Ubtao Hollow",
                "desc": "A massive hollow ironwood tree draped in crimson orchids and hanging skulls. Green incense billows from a bronze cauldron.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "canopy_rope_bridge", "alias": "e"}},
                "npcs": [{"name": "Chultan Jungle Witchdoctor", "desc": "A masked shaman rattling snake vertebrae and chanting to primeval spirits.", "level": 14, "role": "mage"}]
            },
            "ziggurat_approach": {
                "name": "The Avenue of Nine Gods",
                "desc": "Cracked flagstones line a grand jungle boulevard choked with strangler figs. Bas-relief stone statues of animal gods stare with obsidian eyes.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "canopy_rope_bridge", "alias": "s"}, "north": {"dest_id": "royal_palace_omu", "alias": "n"}, "east": {"dest_id": "shrine_wongo", "alias": "e"}, "west": {"dest_id": "shrine_papazotl", "alias": "w"}}
            },
            "shrine_wongo": {
                "name": "The Shrine of Wongo the Su-Monster",
                "desc": "A stone sanctuary dedicated to the violent monkey god. Carvings of prehensile tails and psychic blasts cover the altar.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "ziggurat_approach", "alias": "w"}},
                "npcs": [{"name": "Frenzied Su-Monster", "desc": "A four-pawed simian monstrosity hanging from ceiling iron hooks.", "level": 14, "role": "warrior"}]
            },
            "shrine_papazotl": {
                "name": "The Shrine of Papazotl the Eblis",
                "desc": "A courtyard where statues of giant storks glare downward. Riddles carved into bronze plaques challenge the traveler's mind.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "ziggurat_approach", "alias": "e"}},
                "items": [{"name": "Papazotl's Plumed Feather Quill", "desc": "An iridescent heron feather that enhances mystical focus."}]
            },
            "royal_palace_omu": {
                "name": "The Overgrown Palace of Queen Napaka",
                "desc": "Collapsed stone columns, mosaic floors split by tree roots, and faded murals depicting the golden age of the fallen city of Omu.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "ziggurat_approach", "alias": "s"}, "north": {"dest_id": "gargoyle_colonnade", "alias": "n"}, "east": {"dest_id": "shrine_nangnang", "alias": "e"}, "west": {"dest_id": "shrine_kubazan", "alias": "w"}},
                "npcs": [{"name": "Omuan Skeletal Royal Guard", "desc": "An armored skeleton gripping an ancient bronze khopesh sword.", "level": 15, "role": "warrior"}]
            },
            "shrine_nangnang": {
                "name": "The Shrine of Nangnang the Grung",
                "desc": "A flooded mud shrine covered in slippery algae and lily pads, reeking of toxic amphibian secretions.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "royal_palace_omu", "alias": "w"}},
                "npcs": [{"name": "Grung Poison Dart Elite", "desc": "A bright orange treefrog warrior with a blowgun loaded with lethal venom.", "level": 14, "role": "rogue"}]
            },
            "shrine_kubazan": {
                "name": "The Shrine of Kubazan the Froghemoth",
                "desc": "A deep circular pool of scummy water surrounded by eight stone pillars. Bubbles rise from the muddy depths.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "royal_palace_omu", "alias": "e"}},
                "npcs": [{"name": "The Behemoth Froghemoth", "desc": "A titanic amphibious horror with tentacles, three stalk eyes, and a yawning maw.", "level": 16, "role": "boss", "danger_tier": "boss"}]
            },
            "gargoyle_colonnade": {
                "name": "Colonnade of Weeping Chultan Gargoyles",
                "desc": "Fourteen winged gargoyles crouch atop basalt pedestals. Rainwater weeps from their hollowed stone eye sockets.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "royal_palace_omu", "alias": "s"}, "north": {"dest_id": "fane_night_serpent", "alias": "n"}, "east": {"dest_id": "amphitheater_chult", "alias": "e"}},
                "npcs": [{"name": "Granite Jungle Gargoyle", "desc": "A living stone gargoyle swooping down with razor talons.", "level": 15, "role": "warrior"}]
            },
            "amphitheater_chult": {
                "name": "The Flooded Royal Amphitheater",
                "desc": "Tiered stone seating looks down upon a half-submerged stage where carnivorous plants now bloom.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "gargoyle_colonnade", "alias": "w"}}
            },
            "fane_night_serpent": {
                "name": "The Fane of the Night Serpent",
                "desc": "A sprawling subterranean temple complex of serpent carvings. Torches burn green in iron serpent wall sconces.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "gargoyle_colonnade", "alias": "s"}, "north": {"dest_id": "fane_sacrifice_altar", "alias": "n"}, "west": {"dest_id": "fane_hatchery", "alias": "w"}},
                "npcs": [{"name": "Yuan-ti Pureblood Infiltrator", "desc": "A scaly-skinned serpentine rogue wielding envenomed stilettos.", "level": 15, "role": "rogue"}]
            },
            "fane_hatchery": {
                "name": "The Serpent Brood Hatchery",
                "desc": "Warm sand pits littered with hundreds of leathery snake eggs and coiled venomous vipers.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "fane_night_serpent", "alias": "e"}},
                "npcs": [{"name": "Giant Constrictor Python", "desc": "A forty-foot serpent ready to crush steel plate.", "level": 14, "role": "warrior"}]
            },
            "fane_sacrifice_altar": {
                "name": "The Blood Altar of Dendar",
                "desc": "A colossal stepped altar carved to resemble the gaping jaws of Dendar the Night Serpent. Blood channels drain into a dark well.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "fane_night_serpent", "alias": "s"}, "down": {"dest_id": "tomb_entrance_skull", "alias": "d"}},
                "npcs": [{"name": "Ras Nsi the Yuan-ti Champion", "desc": "A towering serpentine warlord with a hood like a cobra, wielding a flame-tongue blade.", "level": 17, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Flame-Tongue Scimitar of Ras Nsi", "desc": "A bronze blade wreathed in undying serpent flames."}]
            },
            "chult_waterfall_mist": {
                "name": "The Rainbow Cataract",
                "desc": "A three-hundred foot waterfall crashing into a pool shrouded in perpetual rainbow mists.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "river_mouth", "alias": "w"}, "up": {"dest_id": "pterafolk_nest", "alias": "u"}}
            },
            "pterafolk_nest": {
                "name": "The High Pterafolk Crag",
                "desc": "A precipitous rocky plateau overlooking the entire primeval rainforest canopy.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "chult_waterfall_mist", "alias": "d"}},
                "npcs": [{"name": "Pterafolk Sky-Hunter", "desc": "A cruel winged reptilian humanoid clutching a jagged bone spear.", "level": 14, "role": "warrior"}]
            },
            "firenewt_cavern": {
                "name": "The Firenewt Sulfur Caverns",
                "desc": "Vents of scalding steam and pools of molten sulfur hiss in subterranean darkness.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "tar_pits_chult", "alias": "s"}, "north": {"dest_id": "dwarf_mine_chult", "alias": "n"}}
            },
            "dwarf_mine_chult": {
                "name": "The Smoldering Forge of Hrakhamar",
                "desc": "An ancient dwarven iron mine conquered by salamanders and magma beasts. Smelting crucibles overflow with liquid iron.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "firenewt_cavern", "alias": "s"}},
                "npcs": [{"name": "Magma Salamander", "desc": "A fiery reptilian monster slithering through pools of slag.", "level": 15, "role": "warrior"}]
            },
            "goblin_stack_village": {
                "name": "Yellyark Bungee Village",
                "desc": "A rickety village of bamboo huts lashed with thick vines, designed to be catapulted away during predator attacks.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "witch_tree_grove", "alias": "s"}},
                "npcs": [{"name": "Batiri Goblin Battle-Stack", "desc": "Five goblins balanced on each other's shoulders wielding spears and flaming torches.", "level": 13, "role": "warrior"}]
            },
            "tomb_entrance_skull": {
                "name": "The Great Gargoyle Mouth of the Tomb",
                "desc": "A grinning devil face carved into the sheer rock face. Its open jaws form the black entrance to the Tomb of the Nine Gods.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "fane_sacrifice_altar", "alias": "u"}, "north": {"dest_id": "chult_lost_vault", "alias": "n"}}
            },
            "dinosaur_nesting_grounds": {
                "name": "Tyrannosaurus Nesting Grounds",
                "desc": "Uprooted trees and massive smashed boulders surround an egg clutch guarded by the ultimate apex predator of Chult.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "canopy_rope_bridge", "alias": "s"}},
                "npcs": [{"name": "Tyrannosaurus Zombie", "desc": "A rot-infested zombie T-Rex regurgitating crawling undead skeletons.", "level": 17, "role": "boss", "danger_tier": "boss"}]
            },
            "chult_lost_vault": {
                "name": "Vault of the Nine Trickster Gods",
                "desc": "Nine stone sarcophagi are arranged in a circle around an inlaid gold mosaic floor depicting the fallen glory of Chult.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "tomb_entrance_skull", "alias": "s"}, "north": {"dest_id": "apex_spire_omu", "alias": "n"}},
                "items": [{"name": "Amulet of the Nine Trickster Spirits", "desc": "A talisman pulsing with the capricious power of the primeval gods."}]
            },
            "apex_spire_omu": {
                "name": "The Obsidian Sanctum of Acererak",
                "desc": "Hovering above a sphere of annihilation, the eternal lich Acererak conducts unholy experiments on trapped mortal souls.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "chult_lost_vault", "alias": "s"}},
                "npcs": [{"name": "Arch-Lich Acererak", "desc": "The supreme master of the Tomb, eyes burning with twin points of emerald fire, draped in silken funeral shrouds.", "level": 18, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Staff of the Forgotten Gods", "desc": "A black iron staff crowned with a grinning golden skull that commands necromantic ruin."}]
            },
            "chult_ruined_bazaar": {
                "name": "The Sunken Bazaar of Omu",
                "desc": "Flooded market stalls covered in green water lilies.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "amphitheater_chult", "alias": "e"}}
            },
            "monkey_totem_shrine": {
                "name": "Totem Circle of the Su-Monkeys",
                "desc": "Carved wooden posts adorned with monkey pelts and silver charms.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "shrine_wongo", "alias": "n"}}
            },
            "chult_cenote_sinkhole": {
                "name": "The Great Cenote Sinkhole",
                "desc": "A collapsed limestone cavern filled with crystal-clear turquoise groundwater.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "shrine_nangnang", "alias": "s"}}
            },
            "quetzalcoatlus_perch": {
                "name": "The High Mesa Perch",
                "desc": "A soaring rock needle where giant flying pterosaurs rest.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "pterafolk_nest", "alias": "d"}}
            },
            "strangler_fig_tomb": {
                "name": "The Strangler Fig Sepulcher",
                "desc": "A stone crypt enveloped entirely within the wooden coils of a gargantuan fig tree.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "witch_tree_grove", "alias": "n"}}
            }
        }
    }


# =============================================================================
# ZONE 19: NECROPOLIS OF ANUBIS & VALLEY OF PHARAOHS [Level 15-22, 30 Rooms]
# =============================================================================

def build_zone_pharaohs():
    return {
        "zone_key": "valley_pharaohs",
        "zone_name": "The Necropolis of Anubis & Valley of the Pharaohs",
        "default_terrain": "catacombs",
        "base_coords": (60, 40, -15),
        "rooms": {
            "avenue_sphinxes": {
                "name": "The Avenue of Criosphinxes",
                "desc": "A long sandstone concourse flanked by twin rows of ram-headed sphinx statues. The desert wind whistles through ancient eroded hieroglyphic inscriptions.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "pylon_gate_anubis", "alias": "n"}, "east": {"dest_id": "obelisk_plaza", "alias": "e"}},
                "npcs": [{"name": "Mummified Tomb Sentinel", "desc": "A linen-wrapped guardian clutching a bronze spear imbued with the curse of the sands.", "level": 15, "role": "warrior"}]
            },
            "pylon_gate_anubis": {
                "name": "The Black Basalt Pylon of Anubis",
                "desc": "Two towering pylons of polished black basalt frame the grand portal. Colossal statues of the jackal-god Anubis flank the stone entryway.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "avenue_sphinxes", "alias": "s"}, "north": {"dest_id": "hypostyle_hall", "alias": "n"}},
                "npcs": [{"name": "Jackal-Headed Priest of Anubis", "desc": "An embalmer priest wearing a gilded jackal mask and holding an obsidian canopic knife.", "level": 16, "role": "cleric"}]
            },
            "hypostyle_hall": {
                "name": "The Great Hypostyle Column Hall",
                "desc": "A forest of forty papyrus-shaped sandstone columns soaring into shadowy vaulted ceilings. Painted reliefs depict the weighing of the heart against the feather of Ma'at.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "pylon_gate_anubis", "alias": "s"}, "north": {"dest_id": "hall_of_maat", "alias": "n"}, "east": {"dest_id": "embalming_chamber", "alias": "e"}, "west": {"dest_id": "scribe_scriptorium", "alias": "w"}}
            },
            "embalming_chamber": {
                "name": "The Chamber of Mummification",
                "desc": "Stone tables stained with cedar oil, natron salt, and bitumen. Jars of unguents and linen wraps lie beside surgical embalming tools.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "hypostyle_hall", "alias": "w"}, "north": {"dest_id": "canopic_urn_vault", "alias": "n"}},
                "items": [{"name": "Jar of Consecrated Natron Salt", "desc": "Purifying alchemical salt used by Egyptian embalmers to ward against decay."}]
            },
            "canopic_urn_vault": {
                "name": "The Vault of the Four Canopic Guardians",
                "desc": "Four alabaster shrines hold the preserved organs of ancient pharaohs, guarded by the spirits of the Sons of Horus.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "embalming_chamber", "alias": "s"}},
                "npcs": [{"name": "Canopic Urn Golem", "desc": "An alabaster construct animated by guardian spirits that spits caustic embalming bile.", "level": 17, "role": "warrior"}]
            },
            "hall_of_maat": {
                "name": "The Hall of the Two Truths",
                "desc": "In the center of the hall stands a gargantuan set of golden scales. A blood-stained granite basin waits beneath the feather of truth.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "hypostyle_hall", "alias": "s"}, "north": {"dest_id": "descending_gallery", "alias": "n"}, "east": {"dest_id": "shaft_of_scarabs", "alias": "e"}},
                "npcs": [{"name": "Spectral Judge of the Dead", "desc": "A terrifying ghostly magistrate with radiant silver eyes evaluating mortal sins.", "level": 18, "role": "mage"}]
            },
            "shaft_of_scarabs": {
                "name": "The Chasm of Flesh-Eating Scarabs",
                "desc": "The floor hums and ripples with millions of iridescent black and golden scarab beetles. Chitin clicks rhythmically in the pitch blackness.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "hall_of_maat", "alias": "w"}},
                "npcs": [{"name": "Swarm of Golden Scarabs", "desc": "A ravenous insect swarm that strips flesh from bone in seconds.", "level": 16, "role": "rogue"}]
            },
            "descending_gallery": {
                "name": "The Sloping Granite Gallery of Ra",
                "desc": "A steep ramp lined with red granite blocks angled downwards into the heart of the pyramid bedrock. Gold leaf captures torchlight.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "hall_of_maat", "alias": "s"}, "north": {"dest_id": "grand_gallery_pharaoh", "alias": "n"}, "west": {"dest_id": "corridor_of_false_doors", "alias": "w"}}
            },
            "corridor_of_false_doors": {
                "name": "The Maze of Granite False Doors",
                "desc": "Blind stone niches carved with intricate curses intended to confuse tomb robbers and evil spirits.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "descending_gallery", "alias": "e"}},
                "items": [{"name": "Scarab Amulet of Ward-Breaching", "desc": "A carved turquoise beetle that vibrates when near hidden stone mechanisms."}]
            },
            "grand_gallery_pharaoh": {
                "name": "The Grand Ascending Gallery",
                "desc": "A soaring corbelled stone vault twenty-eight feet high, polished to mirror smoothness. Massive granite portcullis blocks hang from counterweights.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "descending_gallery", "alias": "s"}, "north": {"dest_id": "kings_burial_chamber", "alias": "n"}, "east": {"dest_id": "queens_sepulcher", "alias": "e"}},
                "npcs": [{"name": "Pharaonic Anubite Warrior", "desc": "A fierce jackal-faced warrior with gold-inlaid leather armor and an iron khopesh.", "level": 18, "role": "warrior"}]
            },
            "queens_sepulcher": {
                "name": "Sepulcher of the Sun Queen Nefertiti",
                "desc": "A chamber adorned with delicate plaster frescoes of lotus flowers, lapis lazuli beads, and a painted limestone sarcophagus.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "grand_gallery_pharaoh", "alias": "w"}},
                "npcs": [{"name": "High Queen Mummy", "desc": "A gilded royal mummy adorned with a cobra headdress and gold bracelets.", "level": 19, "role": "cleric"}],
                "items": [{"name": "Lapis Lazuli Scarab Pendant", "desc": "A radiant blue amulet imbued with sacred preservation wards."}]
            },
            "kings_burial_chamber": {
                "name": "The Gold Sarcophagus Chamber of Akhenaten",
                "desc": "Lined in solid red granite blocks, this vault holds the golden nested sarcophagi of the Heretic King. Gold foil and jewels cover every surface.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "grand_gallery_pharaoh", "alias": "s"}, "north": {"dest_id": "treasury_of_horus", "alias": "n"}},
                "npcs": [{"name": "Pharaoh Akhenaten the Sun King", "desc": "The resurrected solar monarch clad in pure gold armor, brandishing the Crook and Flail of supreme dominion.", "level": 22, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Golden Crook & Flail of Osiris", "desc": "The mythic regalia of Egypt, radiating blinding solar radiance and unyielding royal authority."}]
            },
            "treasury_of_horus": {
                "name": "The Treasury of Horus the Sun Eagle",
                "desc": "Chests overflowing with alabaster vases, gold ceremonial daggers, ebony thrones, and ivory gaming boards.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "kings_burial_chamber", "alias": "s"}},
                "items": [{"name": "Alabaster Chest of Royal Gold Coinage", "desc": "Hefty gold talents stamped with the solar disc of Aten."}]
            },
            "scribe_scriptorium": {
                "name": "The Royal Hieroglyphic Papyrus Archives",
                "desc": "Stone pigeonholes crammed with thousands of papyrus scrolls containing astronomical charts, incantations, and tomb blueprints.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "hypostyle_hall", "alias": "e"}},
                "npcs": [{"name": "Mummified High Scribe", "desc": "An ancient scribe holding a reed stylus that writes fiery hieroglyphs in the air.", "level": 17, "role": "mage"}]
            },
            "sunken_well_ammit": {
                "name": "The Devourer Ammit's Well",
                "desc": "A pitch-black pit where unweighted souls are tossed to the demon Ammit, part crocodile, part lion, part hippopotamus.",
                "terrain": "water_noswim",
                "exits": {"north": {"dest_id": "shaft_of_scarabs", "alias": "n"}},
                "npcs": [{"name": "Ammit the Soul Devourer", "desc": "A terrifying chimera with jaws that crush ghost and mortal alike.", "level": 20, "role": "boss", "danger_tier": "boss"}]
            },
            "obelisk_plaza": {
                "name": "Plaza of the Twin Rose Granite Obelisks",
                "desc": "Two hundred-foot obelisks of pink Aswan granite capped with electrum pyramidions pierce the blue desert sky.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "avenue_sphinxes", "alias": "w"}, "north": {"dest_id": "court_of_bastet", "alias": "n"}}
            },
            "court_of_bastet": {
                "name": "Sanctuary of the Cat Goddess Bastet",
                "desc": "Bronze statues of sleek feline guardians, bronze sistrum rattles, and bowls of scented cream.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "obelisk_plaza", "alias": "s"}, "east": {"dest_id": "hall_of_sobek", "alias": "e"}},
                "npcs": [{"name": "Priestess of Bastet", "desc": "An agile priestess armed with curved silver claws and blessing amulets.", "level": 17, "role": "rogue"}]
            },
            "hall_of_sobek": {
                "name": "The Sacred Crocodile Pools of Sobek",
                "desc": "Deep stone basins fed by subterranean Nile aqueducts where sacred mummified crocodiles swim.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "court_of_bastet", "alias": "w"}},
                "npcs": [{"name": "Sacred Nile Behemoth", "desc": "A gigantic armored crocodile adorned with golden ear rings.", "level": 18, "role": "warrior"}]
            },
            "crypt_of_ushabti": {
                "name": "The Hall of Ten Thousand Ushabti",
                "desc": "Wall recesses filled with thousands of blue-glazed faience figurine workers awaiting their master's resurrection.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "corridor_of_false_doors", "alias": "n"}}
            },
            "chariot_armory_pharaoh": {
                "name": "Armory of the Royal Charioteers",
                "desc": "Gilded war chariots with spiked bronze wheels and composite horn bows resting on cedar racks.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "scribe_scriptorium", "alias": "s"}},
                "items": [{"name": "Composite Recurve Bow of the Pharaoh", "desc": "A masterwork bow bound in gold wire with incredible range."}]
            },
            "curse_corridor": {
                "name": "The Corridor of Crimson Hieroglyphs",
                "desc": "Hieroglyphic inscriptions glowing with malevolent crimson sorcery, promising death on swift wings to interlopers.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "crypt_of_ushabti", "alias": "e"}}
            },
            "serpopard_menagerie": {
                "name": "The Courtyard of the Serpopards",
                "desc": "An enclosed desert courtyard where carvings depict leopards with long serpentine necks.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "obelisk_plaza", "alias": "n"}}
            },
            "papyrus_marsh_nile": {
                "name": "The Sacred Papyrus Reed Shallows",
                "desc": "Tall papyrus reeds sway in the calm waters of an ancient irrigation reservoir.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "serpopard_menagerie", "alias": "s"}}
            },
            "high_priest_sanctuary": {
                "name": "Sanctuary of High Priest Imhotep",
                "desc": "An ornate private chapel filled with astronomical astrolabes, astrological tablets, and incense burners.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "embalming_chamber", "alias": "n"}},
                "npcs": [{"name": "High Priest Imhotep", "desc": "The legendary architect and sorcerer draped in leopard skin, eyes flashing with arcane sand magic.", "level": 20, "role": "mage"}]
            },
            "secret_stair_sun": {
                "name": "The Stairway of the Solar Barque",
                "desc": "A hidden stairway of white limestone ascending toward the pyramid peak.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "kings_burial_chamber", "alias": "d"}, "up": {"dest_id": "solar_barque_dock", "alias": "u"}}
            },
            "solar_barque_dock": {
                "name": "The Dock of the Golden Solar Barque",
                "desc": "A full-sized wooden ship overlaid with sheets of hammered gold, designed to ferry the pharaoh's soul through the underworld.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "secret_stair_sun", "alias": "d"}},
                "items": [{"name": "Golden Oar of the Solar Barque", "desc": "A ritual oar plated in pure electrum that repels undead shadows."}]
            },
            "chamber_of_resurrection": {
                "name": "The Chamber of the Scarab Rebirth",
                "desc": "A stone rotunda with an opening aligned with the constellation of Orion.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "canopic_urn_vault", "alias": "s"}}
            },
            "vault_of_lapis_lazuli": {
                "name": "The Lapis Lazuli Gem Vault",
                "desc": "Raw blocks and polished beads of royal blue lapis lazuli flecked with golden pyrite.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "treasury_of_horus", "alias": "e"}}
            },
            "watchtower_of_osiris": {
                "name": "The High Sun-Dial Pylon",
                "desc": "The summit of the pylon overlooking the vast dunes of the Sahara.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "pylon_gate_anubis", "alias": "d"}}
            },
            "underground_desert_trench": {
                "name": "The Sunken Trench of Khonsu",
                "desc": "A dry, sandy gorge carved through sandstone bedrock.",
                "terrain": "field",
                "exits": {"west": {"dest_id": "avenue_sphinxes", "alias": "w"}}
            }
        }
    }


# =============================================================================
# ZONE 20: THE FEYWILD: MOONLIT COURT OF SUMMER QUEEN [Level 16-24, 30 Rooms]
# =============================================================================

def build_zone_feywild():
    return {
        "zone_key": "feywild_court",
        "zone_name": "The Feywild: Moonlit Court of the Summer Queen",
        "default_terrain": "forest",
        "base_coords": (-40, -50, 15),
        "rooms": {
            "faerie_ring_crossing": {
                "name": "The Gossamer Faerie Ring Crossing",
                "desc": "A circle of glowing violet mushrooms situated upon vibrant emerald turf. Fireflies pulse with starlight, and the sweet scent of honeysuckle and wild violets hangs in the air.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "twilight_willow_path", "alias": "n"}, "east": {"dest_id": "crystalline_brook", "alias": "e"}},
                "npcs": [{"name": "Pixie Trickster", "desc": "A tiny winged fae carrying a pouch of glowing glittery dust.", "level": 16, "role": "rogue"}]
            },
            "twilight_willow_path": {
                "name": "The Luminescent Willow Promenade",
                "desc": "Weeping willow boughs glow with soft blue luminescence, trailing delicate leaves like curtains of silk over a mossy path.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "faerie_ring_crossing", "alias": "s"}, "north": {"dest_id": "mushroom_circle_ballroom", "alias": "n"}, "west": {"dest_id": "prismatic_hedge_maze", "alias": "w"}}
            },
            "crystalline_brook": {
                "name": "The Brook of Laughing Quartz",
                "desc": "Pebbles of amethyst, rose quartz, and tourmaline sparkle beneath crystal-clear water that hums a melodious tune as it ripples.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "faerie_ring_crossing", "alias": "w"}, "north": {"dest_id": "nymph_cascade_grotto", "alias": "n"}},
                "items": [{"name": "Vial of Laughing Brook Water", "desc": "Luminescent water that inspires joy and removes fear."}]
            },
            "mushroom_circle_ballroom": {
                "name": "The Bioluminescent Cap Pavilion",
                "desc": "Giant mushrooms the size of pavilions form an outdoor ballroom. Satyrs play panpipes while eladrin nobles dance in eternal revelry.",
                "terrain": "field",
                "exits": {"south": {"dest_id": "twilight_willow_path", "alias": "s"}, "north": {"dest_id": "gossamer_silk_bridge", "alias": "n"}, "east": {"dest_id": "unicorn_glade", "alias": "e"}},
                "npcs": [{"name": "Satyr Panpipe Virtuoso", "desc": "A laughing goat-legged minstrel playing tunes that compel listeners to dance.", "level": 17, "role": "bard"}]
            },
            "prismatic_hedge_maze": {
                "name": "The Maze of Living Briar Roses",
                "desc": "Vibrant rose hedges bloom in shifting rainbow hues. The thorns seem to reach out and rearrange the paths when travelers turn their backs.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "twilight_willow_path", "alias": "e"}, "west": {"dest_id": "heart_of_briars", "alias": "w"}},
                "npcs": [{"name": "Briarthorn Dryad", "desc": "A wood spirit clad in living thorn vines wielding a bow of yew.", "level": 17, "role": "warrior"}]
            },
            "heart_of_briars": {
                "name": "The Center of the Thorn Labyrinth",
                "desc": "A secluded arbor where a massive black rose pulses with fey sorcery.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "prismatic_hedge_maze", "alias": "e"}},
                "items": [{"name": "Ever-Blooming Black Briar Rose", "desc": "A mystical flower whose fragrance confers deep magical warding."}]
            },
            "gossamer_silk_bridge": {
                "name": "The Gossamer Bridge of Spun Starlight",
                "desc": "A translucent suspension bridge woven of moonbeams and astral silk spanning a gorge of glowing mist.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "mushroom_circle_ballroom", "alias": "s"}, "north": {"dest_id": "summer_court_gates", "alias": "n"}}
            },
            "summer_court_gates": {
                "name": "The Emerald & Topaz Court Gates",
                "desc": "Two living intertwined elder trees form an archway inlaid with emeralds and sun-warmed topaz.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "gossamer_silk_bridge", "alias": "s"}, "north": {"dest_id": "grand_courtyard_seelie", "alias": "n"}},
                "npcs": [{"name": "Eladrin Gilded Knight", "desc": "A tall fey knight in shimmering leaf-mail plate clutching a golden lance.", "level": 18, "role": "warrior"}]
            },
            "grand_courtyard_seelie": {
                "name": "The Grand Seelie Court of Flowers",
                "desc": "A vast terrace where flowers chime like crystal bells in the gentle breeze. Eladrin courtiers sip nectar from carved flower goblets.",
                "terrain": "field",
                "exits": {"south": {"dest_id": "summer_court_gates", "alias": "s"}, "north": {"dest_id": "summer_throne_room", "alias": "n"}, "east": {"dest_id": "hall_of_masquerade", "alias": "e"}, "west": {"dest_id": "king_oberon_hunt_lodge", "alias": "w"}}
            },
            "hall_of_masquerade": {
                "name": "The Pavilion of Whispering Masks",
                "desc": "Fey nobles in bird masks and moth capes exchange court intrigue and dangerous romantic promises.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "grand_courtyard_seelie", "alias": "w"}},
                "npcs": [{"name": "Eladrin Countess of Whispers", "desc": "A glamorous noblewoman with butterfly wings wielding subtle illusion magic.", "level": 19, "role": "mage"}]
            },
            "summer_throne_room": {
                "name": "The Living Oak Throne of Queen Titania",
                "desc": "In the center of the hall, carved into a titanic living white oak tree, sits Queen Titania. Sunlight beams through leaves of emerald and gold, illuminating her breathtaking, radiant majesty.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "grand_courtyard_seelie", "alias": "s"}},
                "npcs": [{"name": "Queen Titania the Summer Monarch", "desc": "The supreme sovereign of the Seelie Court, radiating endless summer warmth, eyes shining with boundless starlight.", "level": 24, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Mantle of Eternal Midsummer", "desc": "A gossamer cloak woven of living blossoms that radiates summer aura and shields against cold."}]
            },
            "king_oberon_hunt_lodge": {
                "name": "The Wild Hunt Pavilions of King Oberon",
                "desc": "Banners of stag antlers and hunting horns decorate this pavilion of rough-hewn oak and crimson silk.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "grand_courtyard_seelie", "alias": "e"}},
                "npcs": [{"name": "King Oberon the Shadow Huntsman", "desc": "The consort of Titania, master of the Wild Hunt, flanked by loyal blink hounds.", "level": 23, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Horn of the Wild Hunt", "desc": "A curved stag horn whose blast strikes terror into the hearts of all beasts."}]
            },
            "unicorn_glade": {
                "name": "The Sacred Silver Unicorn Meadow",
                "desc": "Pristine white clover and silver lilies carpet a sunlit clearing where celestial unicorns graze in peace.",
                "terrain": "field",
                "exits": {"west": {"dest_id": "mushroom_circle_ballroom", "alias": "w"}, "north": {"dest_id": "moonwell_of_sehanine", "alias": "n"}},
                "npcs": [{"name": "Celestial Silver Unicorn", "desc": "A majestic silver-maned stallion with an iridescent spiraling horn.", "level": 20, "role": "paladin"}]
            },
            "moonwell_of_sehanine": {
                "name": "The Mirror Pool of the Moonwell",
                "desc": "A perfectly circular pool of silver water that mirrors constellations that do not exist in the mortal sky.",
                "terrain": "water_noswim",
                "exits": {"south": {"dest_id": "unicorn_glade", "alias": "s"}}
            },
            "nymph_cascade_grotto": {
                "name": "The Grotto of Laughing Naiads",
                "desc": "A secluded mossy cavern behind a curtain of warm falling water where water nymphs weave garlands of water lilies.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "crystalline_brook", "alias": "s"}},
                "npcs": [{"name": "Luminescent Naiad", "desc": "A graceful water spirit with hair of flowing liquid aquamarine.", "level": 18, "role": "mage"}]
            },
            "treant_council_grove": {
                "name": "Grove of the Ancient Ironwood Treants",
                "desc": "Gargantuan walking trees with faces in their bark slumber in quiet communion.",
                "terrain": "forest",
                "exits": {"west": {"dest_id": "unicorn_glade", "alias": "w"}}
            },
            "faerie_dragon_roost": {
                "name": "The Roost of the Sugar-Bramble Pseudodragons",
                "desc": "Tiny iridescent dragons with butterfly wings roost among honey-sweet berries.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "grand_courtyard_seelie", "alias": "d"}}
            },
            "bramble_cage_glade": {
                "name": "The Thorns of the Unruly Fae",
                "desc": "Living thorn cages holding tricksters who broke their solemn fairy oaths.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "prismatic_hedge_maze", "alias": "n"}}
            },
            "cellar_of_honey_mead": {
                "name": "The Cellar of Honeysuckle Nectar",
                "desc": "Casks of enchanted fairy wine that grant dreams of eternal beauty.",
                "terrain": "indoors",
                "exits": {"up": {"dest_id": "hall_of_masquerade", "alias": "u"}},
                "items": [{"name": "Flagon of Faerie Honeysuckle Nectar", "desc": "A golden beverage that restores vitality and balances the mind."}]
            },
            "weaver_of_dreams_arbor": {
                "name": "The Bower of the Starlight Weaver",
                "desc": "Spiders of silver thread weaving tapestries of mortal destinies.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "summer_throne_room", "alias": "e"}}
            },
            "puck_jester_court": {
                "name": "The Jester's Court of Mischief",
                "desc": "Tumbling sprites juggling glowing orbs and mocking dignified eladrin.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "grand_courtyard_seelie", "alias": "n"}}
            },
            "will_o_wisp_marsh": {
                "name": "The Iridescent Mist Bog",
                "desc": "Bobbing pale lanterns leading foolish mortals astray.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "crystalline_brook", "alias": "s"}}
            },
            "amber_butterfly_hollow": {
                "name": "The Hollow of Golden Monarchs",
                "desc": "Clouds of golden butterflies so thick the sun shines amber.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "twilight_willow_path", "alias": "e"}}
            },
            "starlight_observatory_fae": {
                "name": "The Dewdrop Moon Observatory",
                "desc": "Telescopes made of crystalline dew peering into celestial dimensions.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "summer_court_gates", "alias": "d"}}
            },
            "petrified_elder_ring": {
                "name": "The Megalithic Ring of Ancient Oaths",
                "desc": "Prehistoric standing stones inscribed with the primordial laws of the Fae.",
                "terrain": "field",
                "exits": {"west": {"dest_id": "faerie_ring_crossing", "alias": "w"}}
            },
            "fey_armory_silver": {
                "name": "The Silverbark Armory of the Eladrin",
                "desc": "Bows carved from petrified moonbeams and rapiers light as thistledown.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "summer_throne_room", "alias": "s"}},
                "items": [{"name": "Silverbark Rapier of the Summer Court", "desc": "A foil as light as a feather that strikes with lightning grace."}]
            },
            "pixie_blossom_canopy": {
                "name": "The High Wisteria Blossom Canopy",
                "desc": "Cascades of lavender wisteria blossoms high in the forest canopy.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "mushroom_circle_ballroom", "alias": "d"}}
            },
            "nightingale_alcove": {
                "name": "The Bower of the Silver Nightingale",
                "desc": "Where mechanical and living nightingales sing lullabies of peace.",
                "terrain": "forest",
                "exits": {"west": {"dest_id": "hall_of_masquerade", "alias": "w"}}
            },
            "everbloom_rose_garden": {
                "name": "The Eternal Rose Parterre",
                "desc": "Geometrical garden beds where thousands of prize roses never wilt.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "grand_courtyard_seelie", "alias": "n"}}
            },
            "portal_of_endless_twilight": {
                "name": "The Verge of the Twilight Horizon",
                "desc": "A cliff where the sun sets forever in gold and violet hues.",
                "terrain": "field",
                "exits": {"east": {"dest_id": "faerie_ring_crossing", "alias": "e"}}
            }
        }
    }


# =============================================================================
# ZONE 21: ABYSSAL RIFT OF THE DEMONWEB PITS [Level 24-30 Endgame, 30 Rooms]
# =============================================================================

def build_zone_abyssal():
    return {
        "zone_key": "abyssal_demonweb",
        "zone_name": "The Abyssal Rift of the Demonweb Pits",
        "default_terrain": "catacombs",
        "base_coords": (20, -70, -60),
        "rooms": {
            "web_chasm_verge": {
                "name": "The Verge of the Web Chasm",
                "desc": "An abyss of total darkness drops away into infinity. Gigantic cables of black gossamer web, each thick as an ironwood tree trunk, crisscross the bottomless void.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "adamantine_web_strand", "alias": "n"}, "east": {"dest_id": "chrysalis_cavern", "alias": "e"}},
                "npcs": [{"name": "Abyssal Web-Stalker", "desc": "An eight-legged demon of razor chitin skittering across vibrating web strands.", "level": 24, "role": "rogue"}]
            },
            "adamantine_web_strand": {
                "name": "The Adamantine Web Suspension Strand",
                "desc": "Walking upon this taut, vibrating black web strand suspended thousands of feet above the abyssal abyss requires nerves of steel. Screams of damned souls echo from below.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "web_chasm_verge", "alias": "s"}, "north": {"dest_id": "glabrezu_gatehouse", "alias": "n"}, "west": {"dest_id": "soul_cocoon_vault", "alias": "w"}}
            },
            "chrysalis_cavern": {
                "name": "The Nursery of Abyssal Broodweavers",
                "desc": "Thousands of pulsating demon chrysalises hang from the cavern roof like rotting fruit, dripping acidic green fluids into bubbling trenches.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "web_chasm_verge", "alias": "w"}, "north": {"dest_id": "blood_funnel_web", "alias": "n"}},
                "npcs": [{"name": "Behemoth Broodweaver Demon", "desc": "A bloated spider fiend spinning cocoons of flesh and soul-stuff.", "level": 25, "role": "warrior"}]
            },
            "soul_cocoon_vault": {
                "name": "The Vault of Preserved Mortal Souls",
                "desc": "Silken cocoons containing the preserved psychic consciousness of slain mortal champions. Their eyes glow through translucent silk.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "adamantine_web_strand", "alias": "e"}},
                "items": [{"name": "Crystal Vial of Condensation Souls", "desc": "Liquid soul energy tapped from the Demonweb's endless victims."}]
            },
            "blood_funnel_web": {
                "name": "The Funnel of Liquefied Gore",
                "desc": "A spiral web drain funneling rivers of fiendish blood down to the lower incubators of the Abyss.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "chrysalis_cavern", "alias": "s"}}
            },
            "glabrezu_gatehouse": {
                "name": "The Iron Gate of the Four-Armed Glabrezu",
                "desc": "A fortress of jagged black iron clamped directly onto the central web cables. Pikes adorned with horned skulls line the battlements.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "adamantine_web_strand", "alias": "s"}, "north": {"dest_id": "marilith_parade_ground", "alias": "n"}, "east": {"dest_id": "bone_spire_descent", "alias": "e"}},
                "npcs": [{"name": "Glabrezu High Inquisitor", "desc": "A towering demon with four arms: two ending in pincers capable of snapping iron, and two with spell-casting claws.", "level": 26, "role": "boss", "danger_tier": "boss"}]
            },
            "bone_spire_descent": {
                "name": "The Hollow Spire of Compressed Bone",
                "desc": "A vertical tower formed from millions of fused demon bones spiral downwards into the abyssal core.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "glabrezu_gatehouse", "alias": "w"}, "down": {"dest_id": "spider_iron_foundry", "alias": "d"}}
            },
            "marilith_parade_ground": {
                "name": "The Blade-Drill Yard of the Mariliths",
                "desc": "A broad platform of interlocking iron plates where six-armed serpent demons practice deadly sword katas with blinding speed.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "glabrezu_gatehouse", "alias": "s"}, "north": {"dest_id": "balor_pyre_bastion", "alias": "n"}, "west": {"dest_id": "chasm_of_screaming_souls", "alias": "w"}},
                "npcs": [{"name": "Marilith Blade-Captain", "desc": "A six-armed serpent fiend brandishing six blazing scimitars in a whirlwind of slaughter.", "level": 27, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Abyssal Scimitar of the Six Blades", "desc": "A razor curved blade that hums with chaotic slaughter and bleeding wounds."}]
            },
            "spider_iron_foundry": {
                "name": "The Foundry of the Crawling Siege Juggernauts",
                "desc": "Vast cauldrons of molten abyssal iron forge mechanical spider siege-tanks to be deployed into the Blood War.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "bone_spire_descent", "alias": "u"}}
            },
            "chasm_of_screaming_souls": {
                "name": "The Bottomless Void of Chaos",
                "desc": "Ripping winds howl through sheer nothingness. Flashes of violet lightning illuminate distant floating web palaces.",
                "terrain": "air",
                "exits": {"east": {"dest_id": "marilith_parade_ground", "alias": "e"}, "west": {"dest_id": "demon_ship_wharf", "alias": "w"}}
            },
            "demon_ship_wharf": {
                "name": "The Wharf of the Abyssal Voidskiffs",
                "desc": "Long piers of petrified bone where black flying skiffs anchor before sailing the planar winds.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "chasm_of_screaming_souls", "alias": "e"}}
            },
            "balor_pyre_bastion": {
                "name": "The Bastion of Fire and Ruin",
                "desc": "Flames of black hellfire erupt from iron braziers. The ground itself is cracked obsidian glowing with molten lava.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "marilith_parade_ground", "alias": "s"}, "north": {"dest_id": "altar_of_eight_eyes", "alias": "n"}},
                "npcs": [{"name": "Balor General of the Abyss", "desc": "A winged demon of shadow and flame, brandishing a vorpal lightning sword and a whip of fire.", "level": 28, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Whip of Abyssal Firestorms", "desc": "A nine-tailed whip of braided fire that entangles and incinerates enemies."}]
            },
            "altar_of_eight_eyes": {
                "name": "The Eight-Eyed Altar of Lolth",
                "desc": "A massive onyx altar in the shape of a crawling spider, set with eight fist-sized rubies that glow with malignant divine awareness.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "balor_pyre_bastion", "alias": "s"}, "north": {"dest_id": "antechamber_demon_queen", "alias": "n"}, "east": {"dest_id": "venom_reservoir_chasm", "alias": "e"}},
                "npcs": [{"name": "High Priestess of the Spider Queen", "desc": "A drow arch-cleric surrounded by crawling venomous familiars.", "level": 28, "role": "cleric"}]
            },
            "venom_reservoir_chasm": {
                "name": "The Boiling Black Spider-Venom Reservoir",
                "desc": "A lake of concentrated neurotoxic venom that dissolves metal and bone into green slurry.",
                "terrain": "water_noswim",
                "exits": {"west": {"dest_id": "altar_of_eight_eyes", "alias": "w"}}
            },
            "antechamber_demon_queen": {
                "name": "The Antechamber of the Weaver of Lies",
                "desc": "Curtains of black silk embroidered with silver webs drape walls of carved weeping faces. Mirrors reflect terrifying futures.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "altar_of_eight_eyes", "alias": "s"}, "north": {"dest_id": "throne_spider_queen", "alias": "n"}}
            },
            "throne_spider_queen": {
                "name": "The Great Web Throne of the Demon Queen",
                "desc": "Suspended in the very heart of the 66th Layer of the Abyss, upon a titanic web of adamantine and soul-silk, sits Lolth, the Queen of the Demonweb Pits. Half beautiful dark elf goddess, half titanic black widow spider, her eight eyes gleam with absolute, eternal malice.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "antechamber_demon_queen", "alias": "s"}},
                "npcs": [{"name": "Lolth the Demon Queen of Spiders", "desc": "The supreme divine monarch of the Demonweb Pits, radiating chaotic abyssal godhood, weaving destiny and doom with eight chitinous legs.", "level": 30, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Silk-Fang Scourge of Chaos", "desc": "The supreme endgame relic of the Demonweb Pits, capable of unraveling magical wards and binding mortal wills."}]
            },
            "drow_vassal_barracks": {
                "name": "Barracks of the Damned Drow Apostates",
                "desc": "Bunks of woven spider silk where renegade dark elf warriors drill in darkness.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "glabrezu_gatehouse", "alias": "e"}}
            },
            "yochlol_slime_shrine": {
                "name": "The Stinking Slime Grotto of the Yochlol",
                "desc": "Pools of yellow sulfur and putrid demonic slime where the Handmaidens of Lolth manifest.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "drow_vassal_barracks", "alias": "n"}},
                "npcs": [{"name": "Yochlol Handmaiden Demon", "desc": "A shapeshifting demon of bubbling yellow protoplasm with a single glaring eye.", "level": 26, "role": "mage"}]
            },
            "chitin_armor_forge": {
                "name": "The Forge of Demon Carapace Plate",
                "desc": "Suits of spiked plate armor crafted from the molted exoskeletons of abyssal monstrosities.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "spider_iron_foundry", "alias": "s"}},
                "items": [{"name": "Abyssal Chitin Breastplate", "desc": "Heavy armor formed of black demon carapace that absorbs magical strikes."}]
            },
            "web_cocoon_library": {
                "name": "The Preserved Minds of Dead Archmages",
                "desc": "Mummified spellcaster heads bound in silver web strands that whisper forgotten arcane secrets.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "antechamber_demon_queen", "alias": "w"}}
            },
            "demon_gladiator_pit": {
                "name": "The Pit of Abyssal Carnage",
                "desc": "A sunken iron arena where vrocks and hezrous fight to the death for Lolth's amusement.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "marilith_parade_ground", "alias": "e"}}
            },
            "corridor_of_shattered_webs": {
                "name": "The Corridor of Razor-Edge Silk",
                "desc": "Strands of silk sharp as surgical scalpels strung across the passage.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "web_chasm_verge", "alias": "n"}}
            },
            "parapet_of_thousand_fangs": {
                "name": "Parapet of the Thousand Fangs",
                "desc": "A battlements of demon jaws snapping open and closed mechanically.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "glabrezu_gatehouse", "alias": "d"}}
            },
            "cavern_of_brood_mothers": {
                "name": "The Cavern of the Behemoth Weavers",
                "desc": "Massive spiders the size of merchant galleons weaving planetary webs.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "chrysalis_cavern", "alias": "s"}}
            },
            "sacrificial_web_spire": {
                "name": "The Spire of the Bound Angels",
                "desc": "A spire of black iron where fallen celestial messengers are drained of their divine grace.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "balor_pyre_bastion", "alias": "d"}}
            },
            "hall_of_chaotic_treachery": {
                "name": "The Hall of Whispered Betrayals",
                "desc": "Echoing whispers tempting every entrant to murder their closest companions.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "altar_of_eight_eyes", "alias": "w"}}
            },
            "abyssal_portal_maw": {
                "name": "The Maw of the 66th Abyssal Layer",
                "desc": "A swirling portal of purple chaos vomiting forth new hordes of lesser demons.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "demon_ship_wharf", "alias": "n"}}
            },
            "obsidian_egg_incubator": {
                "name": "The Obsidian Hatchery of Lolth",
                "desc": "Black obsidian eggs humming with unhatched demonic royalty.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "chrysalis_cavern", "alias": "e"}}
            },
            "dread_chitin_bridge": {
                "name": "The Bridge of Interlocking Demon Skulls",
                "desc": "A narrow archway of thousands of grinning horned fiend skulls.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "bone_spire_descent", "alias": "s"}}
            },
            "spider_engine_works": {
                "name": "The Heart of the Clockwork Spider Engine",
                "desc": "Piston-driven demonic mechanisms pumping unholy ichor into the upper web strands.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "spider_iron_foundry", "alias": "n"}}
            }
        }
    }


# =============================================================================
# INGESTION RUNNER & REGISTRATION
# =============================================================================

def register_zephyr_ferry_routes():
    """Register the Zephyr Aether-Skyship transit route."""
    if "zephyr_skyship" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["zephyr_skyship"] = {
            "key": "zephyr_skyship",
            "name": "The Aether-Skyship 'Zephyr's Pride'",
            "operator": "High Sky-Captain Aurelius",
            "operator_title": "Aeronaut of the Grand Imperial Fleet",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "cloud_citadel_cumulus_gateway", "cloud_gateway"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "cloud_citadel_cumulus_gateway": "The Cloudbank Gateway (Cloud Citadel)",
                "cloud_gateway": "The Cloudbank Gateway (Cloud Citadel)"
            },
            "fares": {
                ("south_docks", "cloud_citadel_cumulus_gateway"): 110,
                ("cloud_citadel_cumulus_gateway", "south_docks"): 110,
                ("praxis_province_praxis_harbor", "cloud_citadel_cumulus_gateway"): 95,
                ("cloud_citadel_cumulus_gateway", "praxis_province_praxis_harbor"): 95,
                ("south_docks", "praxis_province_praxis_harbor"): 40,
                ("praxis_province_praxis_harbor", "south_docks"): 40
            },
            "desc": "A majestic dual-envelope dirigible with brass rudders, glowing arcane aether-turbines, and varnished mahogany flying decks.",
            "deck_key": "zephyr_skyship_deck"
        }


def run_bulk_ingestion_part5(clean_existing=False):
    """
    Executes Part 5 of the bulk world expansion:
    - Chult Jungle & Ruins of Omu
    - Valley of the Pharaohs & Anubis Necropolis
    - Feywild Moonlit Summer Court
    - Abyssal Rift of the Demonweb Pits
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
        build_zone_chult,
        build_zone_pharaohs,
        build_zone_feywild,
        build_zone_abyssal
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("chult_jungle", "river_mouth", "foothills", "enter primeval jungle", "exit primeval jungle"),
        ("valley_pharaohs", "avenue_sphinxes", "bazaar", "venture into valley of pharaohs", "return to sunken bazaar"),
        ("feywild_court", "faerie_ring_crossing", "deep_woods", "step through twilight ring", "step into mortal woods"),
        ("abyssal_demonweb", "web_chasm_verge", "marshland", "plunge into abyssal rift", "climb out of abyssal rift")
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

    # 4. Register Zephyr Pride Aether-Skyship Route & Flying Weather Deck
    skyship_deck = find_room_by_key("zephyr_skyship_deck")
    if not skyship_deck:
        skyship_deck = create_object(Room, key="The Aether-Skyship 'Zephyr's Pride' - Flying Weather Deck", tags=[TAG_WORLD])
        skyship_deck.tags.add("zephyr_skyship_deck", category="room_key")
        skyship_deck.tags.add("cloud_citadel", category="zone")
        skyship_deck.db.room_key = "zephyr_skyship_deck"
        skyship_deck.db.desc = (
            "You stand upon the polished teak observation deck of the colossal Aether-Skyship. "
            "Twin massive silk gasbags hover overhead, bound in brass harness cables. "
            "Glow-crystal aether turbines hum rhythmically, driving the ship through ocean clouds "
            "thousands of feet above the land of Eldoria."
        )
        skyship_deck.db.zone = "Skies of Eldoria"
        skyship_deck.db.terrain = "air"
        skyship_deck.db.coords = (15, 30, 25)
        report["rooms_created"] += 1

    register_zephyr_ferry_routes()
    report["ferry_routes_added"].append("The Aether-Skyship 'Zephyr's Pride' (south_docks <-> praxis_harbor <-> cloud_gateway)")

    return report

