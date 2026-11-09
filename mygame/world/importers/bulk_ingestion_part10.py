"""
Bulk World Ingestion Engine — Part 10: The "2,000+ Rooms Milestone" Epochal Expansion

Expands Eldoria beyond the legendary 2,000-room frontier with 241 rooms across 4 high-tier realms:
1. The Tomb of Horrors & Acererak's Demilich Crypt [Level 20-28 Endgame, 60 Rooms]
2. The City of Brass & Elemental Plane of Fire [Level 18-26 Planar, 60 Rooms]
3. The Dwarven Citadel of Mithral Hall [Level 12-20 Underdark & Mountain, 60 Rooms]
4. The Sunken Trench of the Kraken & Triton Coral Citadel [Level 18-26 Abyssal Ocean, 60 Rooms]

Total Rooms Created in Part 10: 241 Rooms (including Planar Skiff 'Sultana' weather deck)
Cumulative World Total: 1,802 + 241 = 2,043 Rooms!

Features:
- New 'The Planar Brass Skiff Sultana' elemental fire transit route in sailing.py
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
# ZONE 38: THE TOMB OF HORRORS & ACERERAK'S DEMILICH CRYPT [Level 20-28, 60 Rooms]
# =============================================================================

def build_zone_tomb_of_horrors():
    zone_key = "tomb_of_horrors"
    zone_name = "The Tomb of Horrors & Acererak's Demilich Crypt"
    rooms = {}

    rooms["tomb_entrance_false_portal"] = {
        "name": "The False Entrance of the Tomb of Horrors",
        "desc": "A sinister portal carved directly into a grim cliff face of bleached stone. Crumbling bas-reliefs depict anguished souls tumbling into bottomless abysses.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "mosaic_path_of_spheres", "alias": "n"}},
        "npcs": [{"name": "Crypt Ghoul Stalker", "desc": "A ravenous undead fiend with elongated gray claws, hunched over a pile of petrified bones.", "level": 20, "role": "rogue"}]
    }

    rooms["mosaic_path_of_spheres"] = {
        "name": "The Mosaic Path of Floating Spheres",
        "desc": "Intricate floor tiles of colored glass and glazed stone form a serpentine winding path. Symbols of death and planar traps decorate the polished stone archways.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "tomb_entrance_false_portal", "alias": "s"}, "north": {"dest_id": "tomb_corridor_01", "alias": "n"}, "east": {"dest_id": "great_green_devil_face", "alias": "e"}},
        "items": [{"name": "Ancient Jeweled Scarab of Protection", "desc": "A gold-plated scarab amulet that wards against necrotic decay."}]
    }

    rooms["great_green_devil_face"] = {
        "name": "The Maw of the Great Green Devil",
        "desc": "A terrifying mosaic depicting a horned green devil with its wide mouth agape in an eternal scream. The mouth opens into impenetrable, absolute magical blackness.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "mosaic_path_of_spheres", "alias": "w"}, "north": {"dest_id": "tomb_corridor_15", "alias": "n"}},
        "npcs": [{"name": "Iron Golem Tomb Sentinel", "desc": "A towering automaton forged of black iron, radiating a suffocating cloud of toxic poison vapors.", "level": 23, "role": "warrior"}]
    }

    rooms["false_crypt_of_the_lich"] = {
        "name": "The False Crypt of the Gilded Lich",
        "desc": "A grand burial vault flanked by alabaster urns. In the center rests an opulent sarcophagus covered in faux-gold foil and deceptive protective runes.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "tomb_corridor_25", "alias": "s"}},
        "npcs": [{"name": "Mummy Lord Crypt Guardian", "desc": "An ancient embalmed sovereign wrapped in moldering linen, eyes blazing with malevolent scarlet flame.", "level": 24, "role": "cleric"}],
        "items": [{"name": "Cursed Gilded Phylon Torc", "desc": "An ornate golden torque that glitters with deceitful enchantment."}]
    }

    rooms["hall_of_floating_spheres"] = {
        "name": "The Chamber of Shifting Gravity",
        "desc": "A bizarre spherical chamber where gravitational forces churn unpredictably. Stone platforms drift in mid-air above glowing chasms of arcane energy.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "tomb_corridor_40", "alias": "s"}},
        "items": [{"name": "Amulet of Stable Gravitation", "desc": "A heavy leaden talisman that pins the wearer securely to the ground against levitation spells."}]
    }

    rooms["mithral_vault_sanctum"] = {
        "name": "The Crypt of Acererak the Demilich",
        "desc": "The true resting sanctuary of the supreme arch-lich. A dais of obsidian pillars elevates a small velvet altar upon which rests a jewel-encrusted human skull with gleaming soul gems set into its eye sockets and teeth.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "tomb_corridor_54", "alias": "s"}},
        "npcs": [{"name": "Acererak the Demilich", "desc": "A floating human skull covered in golden runes and sparkling emerald teeth. Its eye sockets burn with the abyssal soulfire of a thousand consumed archmages.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Acererak's Jeweled Demilich Skull", "desc": "A legendary relic imbued with catastrophic necromantic magic capable of devouring living souls."},
            {"name": "Staff of the Archmage's Ruin", "desc": "An ancient ebon staff capped with a pulsating void crystal."}
        ]
    }

    # 54 Crypt corridors, trap gauntlets, and tomb vaults to reach 60 rooms
    for i in range(1, 55):
        r_key = f"tomb_corridor_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Cold flagstones inscribed with warding hexes and ancient hieroglyphs. "
            f"The scent of dry rot and embalming spices clings to the stagnant air. [Tomb Sector #{i}]"
        )
        r_name = f"Tomb Catacomb Hall #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"tomb_corridor_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"tomb_corridor_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"tomb_corridor_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"tomb_corridor_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "mosaic_path_of_spheres", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "great_green_devil_face", "alias": "s"}
        if i == 25:
            exits["north"] = {"dest_id": "false_crypt_of_the_lich", "alias": "n"}
        if i == 40:
            exits["north"] = {"dest_id": "hall_of_floating_spheres", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "mithral_vault_sanctum", "alias": "n"}

        npcs = []
        items = []
        if i % 6 == 0:
            npcs.append({"name": "Tomb Spectre Wraith", "desc": "A howling apparition of chilling cold that drains vitality with a mere touch.", "level": 21, "role": "mage"})
        elif i % 9 == 0:
            npcs.append({"name": "Crypt Trap Automaton", "desc": "A mechanical bronze spider that fires poisoned dart volleys.", "level": 22, "role": "rogue"})

        if i == 18:
            items.append({"name": "Flask of Preserved Alchemical Embalming Salve", "desc": "A vial of golden salve that cures necrosis and disease."})

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
        "base_coords": (-40, -40, -30),
        "rooms": rooms
    }


# =============================================================================
# ZONE 39: THE CITY OF BRASS & ELEMENTAL PLANE OF FIRE [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_city_of_brass():
    zone_key = "city_of_brass"
    zone_name = "The City of Brass & Elemental Plane of Fire"
    rooms = {}

    rooms["city_of_brass_obsidian_pier"] = {
        "name": "The Obsidian Pier of the Sea of Fire",
        "desc": "A monumental quay of glassy black volcanic obsidian jutting into an infinite sea of boiling orange magma. Planar skiffs moor along brass pylons.",
        "terrain": "city",
        "exits": {"north": {"dest_id": "gate_of_molten_bronze", "alias": "n"}},
        "npcs": [{"name": "Efreet Harbor Sentinel", "desc": "A muscular crimson-skinned genie in gilded scale mail holding a curved flaming halberd.", "level": 19, "role": "warrior"}]
    }

    rooms["gate_of_molten_bronze"] = {
        "name": "The Grand Gate of Molten Bronze",
        "desc": "Colossal gates of solid bronze glowing with dull thermal incandescence. Beyond, the towers and minarets of the legendary City of Brass pierce the fiery sky.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "city_of_brass_obsidian_pier", "alias": "s"}, "north": {"dest_id": "brass_avenue_01", "alias": "n"}, "east": {"dest_id": "bazaar_of_smoldering_spices", "alias": "e"}}
    }

    rooms["bazaar_of_smoldering_spices"] = {
        "name": "The Efreet Grand Souk & Spicemarket",
        "desc": "Silken awnings of flame-resistant salamander hide shade open stalls heaped with smoking saffron, crystallized cinnamon, glowing rubies, and bottled fire elementals.",
        "terrain": "city",
        "exits": {"west": {"dest_id": "gate_of_molten_bronze", "alias": "w"}, "north": {"dest_id": "brass_avenue_15", "alias": "n"}},
        "npcs": [{"name": "Marid Merchant Merchant Prince", "desc": "A wealthy merchant wearing layered robes of woven cinder-silk and smoking hookah pipes.", "level": 20, "role": "rogue"}],
        "items": [{"name": "Pouch of Crystallized Fire Spices", "desc": "Pungent planar spices that warm the spirit and restore stamina."}]
    }

    rooms["foundry_of_salamander_smiths"] = {
        "name": "The Hellfire Crucible & Salamander Foundry",
        "desc": "Great rivers of molten copper and brass cascade into casting vats. Serpent-tailed salamanders hammer glowing broadswords with bare, fire-forged fists.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "brass_avenue_30", "alias": "s"}},
        "npcs": [{"name": "Master Salamander Armorsmith", "desc": "A reptilian forge master whose scales crackle with yellow lightning and white heat.", "level": 22, "role": "warrior"}],
        "items": [{"name": "Ingot of Pyrite-Forged Brass", "desc": "A heavy bar of supernatural brass that never tarnishes nor yields to mortal cold."}]
    }

    rooms["avenue_of_the_burning_spires"] = {
        "name": "The Royal Avenue of Burning Spires",
        "desc": "A broad thoroughfare paved in polished red granite. Towers crowned with braziers of unquenchable elemental fire loom on either flank.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "brass_avenue_45", "alias": "s"}, "north": {"dest_id": "sultan_throne_of_flames", "alias": "n"}}
    }

    rooms["sultan_throne_of_flames"] = {
        "name": "The Smoldering Throne of Grand Sultan Al-Malik",
        "desc": "The imperial throne hall of the Efreet Empire. A colossal throne carved from a single slab of smoldering basalt sits beneath a dome of swirling firestorms.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "avenue_of_the_burning_spires", "alias": "s"}},
        "npcs": [{"name": "Grand Sultan Al-Malik of the Smoldering Throne", "desc": "A towering twelve-foot efreet warlord crowned in horns of white fire, clad in armor of hammered brass, brandishing a flaming scimitar.", "level": 25, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Scimitar of the Efreet Sultan", "desc": "A legendary curved blade of glowing brass that slashes with incandescent planar fire."},
            {"name": "Smoldering Brass Censer of Flame Control", "desc": "A ceremonial brazier that allows the bearer to command open flames and fiery spirits."}
        ]
    }

    # 54 Brass avenues, plazas, and ember districts to reach 60 rooms
    for i in range(1, 55):
        r_key = f"brass_avenue_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"The air shimmers with dry thermal waves above brass paving stones. "
            f"Fountains of liquid crimson flame illuminate towering minarets. [City of Brass Sector #{i}]"
        )
        r_name = f"City of Brass Grand Boulevard #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"brass_avenue_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"brass_avenue_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"brass_avenue_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"brass_avenue_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "gate_of_molten_bronze", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "bazaar_of_smoldering_spices", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "foundry_of_salamander_smiths", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "avenue_of_the_burning_spires", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Fire Mephit Courier", "desc": "A small winged imp made of living smoke and red embers.", "level": 18, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Efreet Royal Legionnaire", "desc": "A disciplined genie warrior wielding a curved scimitar and tower shield.", "level": 21, "role": "warrior"})

        if i == 20:
            items.append({"name": "Flask of Refined Liquid Magma", "desc": "Alchemical liquid fire used to enchant weapons or brew destructive flame bombs."})

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
        "base_coords": (70, 70, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 40: THE DWARVEN CITADEL OF MITHRAL HALL [Level 12-20, 60 Rooms]
# =============================================================================

def build_zone_mithral_hall():
    zone_key = "mithral_hall"
    zone_name = "The Dwarven Citadel of Mithral Hall"
    rooms = {}

    rooms["mithral_hall_valley_gates"] = {
        "name": "The Secret Valley Gates of Clan Battlehammer",
        "desc": "Concealed within a hidden glacial cirque between sheer mountain peaks, two massive stone portals carved with the foaming mug and warhammer crest stand proud.",
        "terrain": "mountain",
        "exits": {"north": {"dest_id": "great_hall_of_battlehammer_kings", "alias": "n"}},
        "npcs": [{"name": "Battlehammer Veteran Crossbowman", "desc": "A bearded shield dwarf in heavy chainmail peering down from an iron crenel.", "level": 13, "role": "warrior"}]
    }

    rooms["great_hall_of_battlehammer_kings"] = {
        "name": "The Great Pillar Hall of Dwarven Kings",
        "desc": "Colossal octagonal columns of gray granite rise eighty feet to support a vaulted mountain roof. Banners of ancient dwarven thanes hang between stone braziers.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "mithral_hall_valley_gates", "alias": "s"}, "north": {"dest_id": "mithral_hall_passage_01", "alias": "n"}, "east": {"dest_id": "garumn_gorge_catwalk", "alias": "e"}},
        "items": [{"name": "Flagon of Battlehammer Mountain Mead", "desc": "Strong, dark dwarven mead brewed from honey and mountain herbs."}]
    }

    rooms["garumn_gorge_catwalk"] = {
        "name": "Garumn's Gorge & The Dizzying Catwalk Spans",
        "desc": "A seemingly bottomless subterranean rift crossed by slender arching stone catwalks lacking railings. Far below, the subterranean River Surbrin rumbles.",
        "terrain": "underground",
        "exits": {"west": {"dest_id": "great_hall_of_battlehammer_kings", "alias": "w"}, "north": {"dest_id": "mithral_hall_passage_15", "alias": "n"}},
        "npcs": [{"name": "Deep Cave Troll", "desc": "A hulking gray-skinned troll with long rubbery arms and razor claws that regenerate instantly.", "level": 16, "role": "warrior"}]
    }

    rooms["mithral_deep_vein_mines"] = {
        "name": "The Deep Lodes of Radiant Mithral",
        "desc": "The beating heart of the stronghold's wealth. Thick veins of lustrous, silvery-blue mithral ore snake through the exposed gneiss bedrock.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "mithral_hall_passage_30", "alias": "s"}},
        "npcs": [{"name": "Master Dwarven Prospector", "desc": "A grizzled miner with a silver-tipped pickaxe and an eye for pure ore veins.", "level": 15, "role": "rogue"}],
        "items": [{"name": "Raw Chunk of Pure Mithral Ore", "desc": "A heavy nugget of shimmering mithral that is as light as silver but hard as dragon scales."}]
    }

    rooms["undercity_forge_of_dumathoin"] = {
        "name": "The Undercity Forges of Dumathoin",
        "desc": "Great waterwheels drive massive mechanical trip-hammers against iron anvils. Runes of the Silent Keeper glow with blue warmth upon the forge chimneys.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "mithral_hall_passage_45", "alias": "s"}}
    }

    rooms["shimmergloom_shadow_chasm"] = {
        "name": "The Abyssal Lair of Shimmergloom",
        "desc": "The deepest subterranean cavern beneath Mithral Hall. Whispering shadows coil like living smoke around a vast nest of calcified bones and dwarven armor.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "mithral_hall_passage_54", "alias": "s"}},
        "npcs": [{"name": "Shimmergloom the Shadow Dragon", "desc": "A colossal serpent of undulating obsidian scales and smoky shadow wings. Its eyes burn with hateful violet flame as darkness pools beneath its talons.", "level": 22, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Mithral Warhammer of the Battlehammer Thane", "desc": "A superbly balanced two-handed warhammer forged from pure folded mithral, devastating against giants and dragons."},
            {"name": "Aegis-fang of the North", "desc": "A heavy runic warhammer inscribed with thunderous protective glyphs."}
        ]
    }

    # 54 Passages, armories, and tunnels to reach 60 rooms
    for i in range(1, 55):
        r_key = f"mithral_hall_passage_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Solid granite corridors hewn with masterful dwarven stonework. "
            f"Iron sconces hold everburning oil torches illuminating geometric masonry. [Mithral Hall Sector #{i}]"
        )
        r_name = f"Mithral Hall Stone Gallery #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"mithral_hall_passage_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"mithral_hall_passage_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"mithral_hall_passage_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"mithral_hall_passage_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "great_hall_of_battlehammer_kings", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "garumn_gorge_catwalk", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "mithral_deep_vein_mines", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "undercity_forge_of_dumathoin", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "shimmergloom_shadow_chasm", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Clan Battlehammer Shieldbearer", "desc": "A resolute dwarven warrior with an iron-banded oak shield.", "level": 14, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Duergar Shadow Infiltrator", "desc": "A gray dwarf rogue cloaked in magical invisibility and carrying poisoned daggers.", "level": 15, "role": "rogue"})

        if i == 25:
            items.append({"name": "Bar of Refined Mithral Ingot", "desc": "A gleaming ingot of feather-light, indestructible mithral metal."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "underground",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "underground",
        "base_coords": (-10, -80, -15),
        "rooms": rooms
    }


# =============================================================================
# ZONE 41: THE SUNKEN TRENCH OF THE KRAKEN [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_kraken_trench():
    zone_key = "kraken_trench"
    zone_name = "The Sunken Trench of the Kraken & Triton Coral Citadel"
    rooms = {}

    rooms["kraken_trench_abyssal_rim"] = {
        "name": "The Abyssal Rim of the Midnight Trench",
        "desc": "The continental shelf drops away into a sheer, plunging marine precipice. Water pressure increases exponentially, and darkness swallows all sunlight.",
        "terrain": "water_swim",
        "exits": {"north": {"dest_id": "hydrothermal_black_smokers", "alias": "n"}},
        "npcs": [{"name": "Abyssal Anglerfish Predator", "desc": "A monstrous anglerfish with needle-like fangs and a hypnotic bioluminescent lure.", "level": 19, "role": "warrior"}]
    }

    rooms["hydrothermal_black_smokers"] = {
        "name": "The Hydrothermal Black Smoker Spires",
        "desc": "Towering chimneys of volcanic mineral deposits venting superheated black water into the icy deep. Blind tube worms and ghost crabs thrive in the sulfur warmth.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "kraken_trench_abyssal_rim", "alias": "s"}, "north": {"dest_id": "abyssal_waters_01", "alias": "n"}, "east": {"dest_id": "triton_coral_throne_room", "alias": "e"}}
    }

    rooms["triton_coral_throne_room"] = {
        "name": "The Luminescent Throne of Triton High Kings",
        "desc": "A breathtaking palace carved from living deep-sea coral that glows in phosphorescent green and blue hues. Triton honor guards hover with silver tridents.",
        "terrain": "water_swim",
        "exits": {"west": {"dest_id": "hydrothermal_black_smokers", "alias": "w"}, "north": {"dest_id": "abyssal_waters_15", "alias": "n"}},
        "npcs": [{"name": "Triton Royal Champion", "desc": "An aristocratic aquatic noble clad in polished pearl scale armor wielding a heavy trident.", "level": 21, "role": "warrior"}],
        "items": [{"name": "Luminescent Sea-Lily Crown", "desc": "A living coral circlet that grants underwater breathing and darkvision."}]
    }

    rooms["sunken_corsair_graveyard"] = {
        "name": "The Abyssal Graveyard of Sunken Galleons",
        "desc": "Dozens of ancient sailing vessels rest crushed upon the ocean floor, their hulls covered in barnacles and ghostly sea anemones.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "abyssal_waters_30", "alias": "s"}},
        "npcs": [{"name": "Drowned Galleon Bosun", "desc": "A barnacle-encrusted zombie clutching an ancient rusted boarding axe.", "level": 20, "role": "warrior"}],
        "items": [{"name": "Barnacle-Encrusted Doubloon Chest", "desc": "A waterlogged oak strongbox containing forgotten gold coins."}]
    }

    rooms["bioluminescent_jellyfish_forest"] = {
        "name": "The Forest of Giant Bioluminescent Siphonophores",
        "desc": "Curtains of floating, translucent jellyfish tentacles trail hundreds of feet through the deep water, pulsing with rhythmic waves of electric blue.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "abyssal_waters_45", "alias": "s"}}
    }

    rooms["kraken_deep_trench_abyss"] = {
        "name": "The Leviathan Abyss of the Ancient Kraken",
        "desc": "At the bottom of the world, miles below the surface, lies the cavernous trench where the mythical leviathan rests. Cyclopean tentacles as thick as towers stir in the silt.",
        "terrain": "water_swim",
        "exits": {"south": {"dest_id": "abyssal_waters_54", "alias": "s"}},
        "npcs": [{"name": "The Ancient Kraken Leviathan", "desc": "A colossal sea titan with ten barbed tentacles, a beak of serrated black chitin that can shear battleships, and eyes as large as galleons.", "level": 24, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Trident of the Abyssal Leviathan", "desc": "A mythical trident forged from deep-trench black pearl and kraken bone, capable of summoning tidal whirlpools."},
            {"name": "Black Pearl of Tidal Mastery", "desc": "A flawless fist-sized black pearl radiating immense oceanic magic."}
        ]
    }

    # 54 Abyssal trench waters, vents, and rifts to reach 60 rooms
    for i in range(1, 55):
        r_key = f"abyssal_waters_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Freezing, high-pressure oceanic abyss where alien sea creatures drift silently. "
            f"Phosphorescent plankton trails behind every movement. [Kraken Trench Sector #{i}]"
        )
        r_name = f"Abyssal Trench Water Column #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"abyssal_waters_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"abyssal_waters_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"abyssal_waters_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"abyssal_waters_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "hydrothermal_black_smokers", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "triton_coral_throne_room", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "sunken_corsair_graveyard", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "bioluminescent_jellyfish_forest", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "kraken_deep_trench_abyss", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Abyssal Sea Viper", "desc": "A long, venomous eel with glowing spinal fins and paralytic venom.", "level": 19, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Deep-Trench Triton Sentry", "desc": "A vigilant aquatic soldier patrolling the abyssal depths.", "level": 20, "role": "warrior"})

        if i == 28:
            items.append({"name": "Gleaming Black Trench Pearl", "desc": "A rare gem harvested from crushing ocean depths."})

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
        "base_coords": (0, 110, -50),
        "rooms": rooms
    }


# =============================================================================
# MARITIME ROUTE HELPER
# =============================================================================

def register_sultana_ferry_routes():
    """Ensures The Planar Brass Skiff 'Sultana' is registered in sailing.FERRY_ROUTES."""
    if "sultana_skiff" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["sultana_skiff"] = {
            "key": "sultana_skiff",
            "name": 'The Planar Brass Skiff "Sultana"',
            "operator": "Efreet Helmsman Malik",
            "operator_title": "Navigator of the Sea of Fire & Planar Rifts",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "city_of_brass_obsidian_pier", "brass_pier"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "city_of_brass_obsidian_pier": "The Obsidian Pier of the Sea of Fire",
                "brass_pier": "The Obsidian Pier of the Sea of Fire"
            },
            "fares": {
                ("south_docks", "city_of_brass_obsidian_pier"): 95,
                ("city_of_brass_obsidian_pier", "south_docks"): 95,
                ("praxis_province_praxis_harbor", "city_of_brass_obsidian_pier"): 80,
                ("city_of_brass_obsidian_pier", "praxis_province_praxis_harbor"): 80,
                ("south_docks", "brass_pier"): 95,
                ("brass_pier", "south_docks"): 95,
                ("praxis_province_praxis_harbor", "brass_pier"): 80,
                ("brass_pier", "praxis_province_praxis_harbor"): 80
            },
            "desc": "A gleaming skiff constructed of enchanted burnished brass, insulated against planar infernos with cooling elemental runes and steered with a volcanic obsidian tiller.",
            "deck_key": "sultana_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 10
# =============================================================================

def run_bulk_ingestion_part10(clean_existing=False):
    """
    Executes Part 10 of the bulk world expansion ("2,000+ Rooms Milestone"):
    - The Tomb of Horrors & Acererak's Demilich Crypt (60 rooms)
    - The City of Brass & Elemental Plane of Fire (60 rooms)
    - The Dwarven Citadel of Mithral Hall (60 rooms)
    - The Sunken Trench of the Kraken & Triton Coral Citadel (60 rooms)
    Plus The Planar Brass Skiff 'Sultana' weather deck (1 room).
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
        build_zone_tomb_of_horrors,
        build_zone_city_of_brass,
        build_zone_mithral_hall,
        build_zone_kraken_trench
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("tomb_of_horrors", "tomb_entrance_false_portal", "catacombs", "descend into the tomb of horrors", "ascend from the tomb of horrors"),
        ("city_of_brass", "city_of_brass_obsidian_pier", "chasm_bridge", "step through planar fire portal", "step through planar portal to mortal realm"),
        ("mithral_hall", "mithral_hall_valley_gates", "frostfang_pass", "enter secret dwarf passage to mithral hall", "exit mithral hall to frostfang pass"),
        ("kraken_trench", "kraken_trench_abyssal_rim", "dead_mans_cove", "dive into the midnight abyss trench", "surface from the deep abyssal trench")
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

    # 4. Register Sultana Planar Ferry Route & Weather Deck
    sultana_deck = find_room_by_key("sultana_deck")
    if not sultana_deck:
        sultana_deck = create_object(Room, key='The Planar Brass Skiff "Sultana" - Weather Deck', tags=[TAG_WORLD])
        sultana_deck.tags.add("sultana_deck", category="room_key")
        sultana_deck.tags.add("city_of_brass", category="zone")
        sultana_deck.db.room_key = "sultana_deck"
        sultana_deck.db.desc = (
            "You stand upon the burnished brass deck of the planar skiff. "
            "A shimmering heat-warding aura surrounds the vessel, insulating passengers from "
            "the roaring magma waves of the Sea of Fire and the icy drafts of mortal seas."
        )
        sultana_deck.db.zone = "Planar Transit"
        sultana_deck.db.terrain = "water_swim"
        sultana_deck.db.coords = (70, 70, 0)
        report["rooms_created"] += 1

    register_sultana_ferry_routes()
    report["ferry_routes_added"].append('The Planar Brass Skiff "Sultana" (south_docks <-> praxis_harbor <-> city_of_brass_pier)')

    return report
