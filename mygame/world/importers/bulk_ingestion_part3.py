"""
Bulk World Ingestion Engine — Part 3: The Mythic Frontiers

Expands Eldoria with an additional 120 rooms across 4 high-tier mythic zones:
1. The Sunken Metropolis of Atlantea (Lima / FluffOS Deep Sea) [Level 16-23]
2. The Underdark & Obsidian City of Ched Nasad (CircleMUD / Diku) [Level 18-25]
3. Castle Ravencrest & The Vampire Crypts (Gothic Horror / Ravenloft) [Level 14-20]
4. The Cloud Citadel of the Storm Giants (tbaMUD Elemental Air) [Level 20-27+]

Features:
- New Deep-Sea Bathysphere 'Nautilus' submersible route
- 100% GMCP Room.Info automapper telemetry
- Legendary boss encounters and mythic relics
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
# ZONE 10: ATLANTEA SUNKEN METROPOLIS [Level 16-23, 30 Rooms]
# =============================================================================

def build_zone_atlantea():
    return {
        "zone_key": "atlantea_depths",
        "zone_name": "The Sunken Metropolis of Atlantea",
        "default_terrain": "underwater",
        "base_coords": (-20, 20, -30),
        "rooms": {
            "atlantea_sea_gate": {
                "name": "The Great Pearl Barrier of Atlantea",
                "desc": "A monumental arch of iridescent mother-of-pearl rising from the ocean floor. A shimmering magical air-field seals the entrance, allowing dry air within the sunken city while holding back millions of tons of ocean water.",
                "terrain": "water_swim",
                "exits": {"down": {"dest_id": "air_dome_plaza", "alias": "d"}},
                "npcs": [{"name": "Atlantean Sea Sentry", "desc": "A gill-breathing merman warrior in coral scale mail holding a barbed trident.", "level": 16, "role": "warrior"}]
            },
            "air_dome_plaza": {
                "name": "The Grand Air-Dome Plaza",
                "desc": "Inside the colossal glass dome, breathable air allows travelers to walk freely. Streets paved with polished turquoise and abalone shell spread outward beneath the curved glass ceiling holding back schools of glowing manta rays.",
                "terrain": "city",
                "exits": {"up": {"dest_id": "atlantea_sea_gate", "alias": "u"}, "north": {"dest_id": "coral_palace_doors", "alias": "n"}, "east": {"dest_id": "pearl_market", "alias": "e"}, "west": {"dest_id": "bioluminescent_gardens", "alias": "w"}},
                "npcs": [{"name": "Atlantean Citizen", "desc": "A graceful aquatic humanoid in flowing seaweed silk robes.", "level": 14, "role": "civilian"}]
            },
            "coral_palace_doors": {
                "name": "Threshold of the Sea King's Palace",
                "desc": "Two massive bronze doors carved with reliefs of leviathans battling storm gods. Fountains of glowing blue brine burble on either side.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "air_dome_plaza", "alias": "s"}, "north": {"dest_id": "throne_room_triton", "alias": "n"}},
                "npcs": [{"name": "Royal Triton Guard", "desc": "A towering armored merman wielding a golden spear.", "level": 18, "role": "warrior"}]
            },
            "throne_room_triton": {
                "name": "The High Throne of King Triton",
                "desc": "Carved from a colossal nautilus shell, the throne rests upon a dais of solid sea jade. Banners woven from golden sea kelp hang from the vaulted crystal ceiling.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "coral_palace_doors", "alias": "s"}, "down": {"dest_id": "abyssal_treasury", "alias": "d"}},
                "npcs": [{"name": "King Triton the Sea Lord", "desc": "The sovereign monarch of the ocean deeps, his beard swirling like ocean froth, wielding the Trident of the Abyss.", "level": 23, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Trident of Ocean Depths", "desc": "A legendary three-pronged weapon that commands the tides and storms."}]
            },
            "abyssal_treasury": {
                "name": "The Sunken Vault of Galleon Plunder",
                "desc": "Sunken chests from hundreds of ancient pirate shipwrecks sit cracked open, spilling gold doubloons, emeralds, and diamond tiaras across the sand.",
                "terrain": "indoors",
                "exits": {"up": {"dest_id": "throne_room_triton", "alias": "u"}},
                "items": [{"name": "Chest of Ancient Sunken Doubloons", "desc": "A heavy iron-banded chest filled with antique Spanish gold coins."}]
            },
            "pearl_market": {
                "name": "The Luminescent Pearl Market",
                "desc": "Stalls made of giant clamshells displaying rare black pearls, dried sea herbs, electric eel oil, and sponges.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "air_dome_plaza", "alias": "w"}, "east": {"dest_id": "aquatic_forge", "alias": "e"}},
                "npcs": [{"name": "Merfolk Pearl Merchant", "desc": "A merchant with webbed fingers stringing lustrous pearls onto wire.", "level": 15, "role": "civilian"}]
            },
            "aquatic_forge": {
                "name": "The Cold-Flame Coral Forge",
                "desc": "An alchemical smithy using hydrothermal vent pressure and cold volcanic flames to forge weapons from sea-glass and coral.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "pearl_market", "alias": "w"}},
                "items": [{"name": "Sea-Glass Dagger of Atlantea", "desc": "A translucent blade sharper than obsidian that glows softly underwater."}]
            },
            "bioluminescent_gardens": {
                "name": "The Bioluminescent Sea Kelp Gardens",
                "desc": "Forests of glowing emerald and turquoise kelp rise forty feet high. Schools of translucent angel fish dart between the fronds.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "air_dome_plaza", "alias": "e"}, "west": {"dest_id": "kraken_trench_edge", "alias": "w"}},
                "npcs": [{"name": "Giant Coral Crab", "desc": "A ten-legged crustacean with pincers capable of severing anchor chains.", "level": 17, "role": "warrior"}]
            },
            "kraken_trench_edge": {
                "name": "Edge of the Abyssal Kraken Trench",
                "desc": "The protective air dome terminates here at an iron airlock. Beyond lies the pitch-black precipice plunging into the freezing midnight ocean abyss.",
                "terrain": "underwater",
                "exits": {"east": {"dest_id": "bioluminescent_gardens", "alias": "e"}, "down": {"dest_id": "kraken_lair", "alias": "d"}}
            },
            "kraken_lair": {
                "name": "Lair of the Deep Sea Kraken",
                "desc": "Crushed hulls of wooden caravels and iron anchors litter the seabed. Enormous tentacles the size of redwood trees stir in the cold currents.",
                "terrain": "underwater",
                "exits": {"up": {"dest_id": "kraken_trench_edge", "alias": "u"}},
                "npcs": [{"name": "Primordial Abyssal Kraken", "desc": "A colossal sea leviathan with crushing suckered tentacles and a serrated beak.", "level": 22, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Eye of the Kraken Relic", "desc": "A glowing basketball-sized orb granting underwater darkvision."}]
            },
            "siren_grotto_depths": {
                "name": "The Sunken Sirens' Grotto",
                "desc": "Echoing caverns where aquatic sirens sing hypnotic melodies that lure unwary sailors to the depths.",
                "terrain": "underwater",
                "exits": {"north": {"dest_id": "bioluminescent_gardens", "alias": "n"}},
                "npcs": [{"name": "Deep Ocean Siren", "desc": "A seductive aquatic nymph with shimmering azure scales and a voice like silver bells.", "level": 17, "role": "mage"}]
            },
            "shipwreck_galleon": {
                "name": "Wreck of the Imperial Armada Flagship",
                "desc": "The rotting ribs of a three-masted warship covered in barnacles and sea sponges. Cannon barrels peer through sand.",
                "terrain": "underwater",
                "exits": {"east": {"dest_id": "kraken_lair", "alias": "e"}}
            },
            "bathysphere_dock": {
                "name": "The Submersible Air-Dock",
                "desc": "An enclosed hydraulic lock where diving bells and deep-sea bathyspheres dock safely from the surface world.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "air_dome_plaza", "alias": "s"}}
            },
            "tide_observatory": {
                "name": "Observatory of Oceanic Currents",
                "desc": "Glass prisms tracking global tides and lunar phases.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "coral_palace_doors", "alias": "w"}}
            },
            "shell_mosaic_hall": {
                "name": "The Shell Mosaic Gallery",
                "desc": "Vast murals made from millions of colorful clam and conch shells.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "coral_palace_doors", "alias": "e"}},
                "items": [{"name": "Abalone Shell Crown of the Ocean Pearl", "desc": "An ornate circlet shimmering with green-blue nacre."}]
            },
            "sea_anemone_meadow": {
                "name": "Meadow of Weeping Anemones",
                "desc": "Colorful stinging tentacles waving in the simulated current.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "bioluminescent_gardens", "alias": "n"}}
            },
            "jellyfish_nursery": {
                "name": "The Translucent Medusa Nursery",
                "desc": "Thousands of tiny glowing jellyfish floating like paper lanterns.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "pearl_market", "alias": "s"}}
            },
            "hydrothermal_spire": {
                "name": "Black Smoker Mineral Spire",
                "desc": "Scalding mineral plumes gushing into the ocean deeps.",
                "terrain": "underwater",
                "exits": {"down": {"dest_id": "kraken_lair", "alias": "d"}}
            },
            "submerged_amphitheater": {
                "name": "The Amphitheater of the Waves",
                "desc": "Tiers of marble benches where aquatic concerts are performed.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "tide_observatory", "alias": "s"}}
            },
            "conch_belfry": {
                "name": "The Great Conch Belfry",
                "desc": "A colossal conch shell blown during times of submarine war.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "air_dome_plaza", "alias": "n"}}
            },
            "abalone_colonnade": {
                "name": "The Abalone Colonnade",
                "desc": "Graceful columns reflecting rainbow sheens of nacre.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "throne_room_triton", "alias": "e"}}
            },
            "sea_serpent_hatchery": {
                "name": "The Royal Sea Serpent Hatchery",
                "desc": "Nest troughs where aquatic dragonets hatch from leathery eggs.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "throne_room_triton", "alias": "w"}}
            },
            "diver_salvage_depot": {
                "name": "Deep Salvage Warehouse",
                "desc": "Heavy brass helmets, copper diving suits, and air hoses.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "bathysphere_dock", "alias": "n"}}
            },
            "sponge_aquarium": {
                "name": "The Living Sponge Wall",
                "desc": "Giant barrel sponges filtering water continuously.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "jellyfish_nursery", "alias": "s"}}
            },
            "manta_hangar": {
                "name": "The War Manta Stables",
                "desc": "Giant armored stingrays saddled with harness straps.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "atlantea_sea_gate", "alias": "e"}}
            },
            "ocean_tomb_kings": {
                "name": "Crypt of the Ancient Mer-Kings",
                "desc": "Sarcophagi carved from white coral resting in cold water.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "abyssal_treasury", "alias": "d"}}
            },
            "pearl_divers_shack": {
                "name": "The Free-Divers' Rest",
                "desc": "Benches where human pearl divers dry off between deep dives.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "pearl_market", "alias": "s"}}
            },
            "kelp_brewery": {
                "name": "The Kelp Mead Still",
                "desc": "Distilleries producing salty, invigorating green ocean spirits.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "pearl_divers_shack", "alias": "w"}}
            },
            "glass_dome_apex": {
                "name": "Pinnacle of the Great Air Dome",
                "desc": "High catwalk directly beneath the curved glass holding back the ocean.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "air_dome_plaza", "alias": "d"}}
            },
            "ocean_abyss_floor": {
                "name": "Floor of the Eternal Abyss",
                "desc": "The deepest seabed where no sunlight has ever penetrated.",
                "terrain": "underwater",
                "exits": {"up": {"dest_id": "kraken_lair", "alias": "u"}}
            }
        }
    }


# =============================================================================
# ZONE 11: THE UNDERDARK OF CHED NASAD [Level 18-25, 30 Rooms]
# =============================================================================

def build_zone_underdark():
    return {
        "zone_key": "underdark_drow",
        "zone_name": "The Underdark & Obsidian City of Ched Nasad",
        "default_terrain": "catacombs",
        "base_coords": (0, 0, -50),
        "rooms": {
            "chasm_descent": {
                "name": "Descent to the Faerzress Chasm",
                "desc": "A dizzying natural cavern glowing with eerie violet phosphorescence. Ancient stone steps carved into stalagmites spiral downward into the Underdark abyss.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "ched_nasad_gates", "alias": "d"}},
                "npcs": [{"name": "Drow Sentry Scout", "desc": "An obsidian-skinned dark elf in piwafwi cloak wielding a poisoned hand crossbow.", "level": 18, "role": "rogue"}]
            },
            "ched_nasad_gates": {
                "name": "Gates of the City of Shimmering Webs",
                "desc": "Massive gates forged from dark adamantine shaped like a predatory spider. Enormous strands of petrified calcified silk span the yawning chasm overhead.",
                "terrain": "city",
                "exits": {"up": {"dest_id": "chasm_descent", "alias": "u"}, "north": {"dest_id": "stalactite_boulevard", "alias": "n"}},
                "npcs": [{"name": "Drow Elite House Guard", "desc": "A warrior in black spider-silk armor wielding twin masterwork scimitars.", "level": 19, "role": "warrior"}]
            },
            "stalactite_boulevard": {
                "name": "Boulevard of the Stalactite Manors",
                "desc": "A monumental Underdark avenue where noble drow houses inhabit hollowed-out stalactites suspended hundreds of feet above the glowing cavern floor.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "ched_nasad_gates", "alias": "s"}, "north": {"dest_id": "temple_of_lolth", "alias": "n"}, "east": {"dest_id": "slave_bazaar", "alias": "e"}, "west": {"dest_id": "academy_sorcere", "alias": "w"}},
                "npcs": [{"name": "Drow Nobleman", "desc": "An arrogant dark elf aristocrat draped in velvet and spiderweb lace.", "level": 17, "role": "mage"}]
            },
            "slave_bazaar": {
                "name": "The Underdark Slave Market",
                "desc": "Iron cages holding captured dwarves, surface elves, and deep gnomes. Overseers crack barbed whips across the auction blocks.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "stalactite_boulevard", "alias": "w"}},
                "npcs": [{"name": "Drow Slaver Taskmaster", "desc": "A cruel dark elf cracking an electrified shock whip.", "level": 18, "role": "warrior"}]
            },
            "academy_sorcere": {
                "name": "The Arcane Spire of Sorcere",
                "desc": "The wizard academy of the drow. Glowing runes of necromancy and evocation float in the air around levitating stone lecterns.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "stalactite_boulevard", "alias": "e"}},
                "npcs": [{"name": "Drow Arch-Mage Draz", "desc": "A master of shadows holding a staff of blackened obsidian.", "level": 21, "role": "mage"}],
                "items": [{"name": "Grimoire of Underdark Shadow Magic", "desc": "A heavy tome bound in drow leather containing shadow spells."}]
            },
            "temple_of_lolth": {
                "name": "The Great Temple of the Spider Queen",
                "desc": "A nightmare temple carved into a mountain of black basalt. Eight colossal stone spider legs support a blood-stained altar before a statue of Lolth.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "stalactite_boulevard", "alias": "s"}, "north": {"dest_id": "matron_sanctum", "alias": "n"}},
                "npcs": [{"name": "Drow Priestess of Lolth", "desc": "A fanatical priestess wielding a scourge of five live vipers.", "level": 20, "role": "mage"}]
            },
            "matron_sanctum": {
                "name": "Sanctum of Matron Mother Malice",
                "desc": "Floating thrones of woven black spider silk and cushions of purple velvet. The matron mother rules the city with absolute cruelty and cunning.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "temple_of_lolth", "alias": "s"}, "down": {"dest_id": "drider_pits", "alias": "d"}},
                "npcs": [{"name": "Matron Mother Malice", "desc": "The supreme matriarch of the drow, her voice like poisoned honey, surrounded by loyal yochlol demons.", "level": 24, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Spider-Fang Rapier of Lolth", "desc": "A black adamantine rapier dripping with lethal paralytic venom."}]
            },
            "drider_pits": {
                "name": "The Pit of the Driders",
                "desc": "A filthy abyss where failed drow who offended the Spider Queen are transformed into hideous half-drow half-spider centaur abominations.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "matron_sanctum", "alias": "u"}},
                "npcs": [{"name": "Tortured Drider Chieftain", "desc": "A massive drider wielding a poisoned greataxe with blinding speed.", "level": 21, "role": "boss", "danger_tier": "boss"}]
            },
            "mushroom_forest_underdark": {
                "name": "The Great Luminous Fungal Forest",
                "desc": "Giant zurkhwood mushrooms tower sixty feet high, shedding blue and violet spores into the stagnant subterranean breeze.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "chasm_descent", "alias": "s"}, "east": {"dest_id": "deep_gnome_refuge", "alias": "e"}},
                "npcs": [{"name": "Myconid Sovereign", "desc": "A walking fungal entity communicating through telepathic spore clouds.", "level": 18, "role": "mage"}]
            },
            "deep_gnome_refuge": {
                "name": "Svirfneblin Hidden Enclave",
                "desc": "A concealed village of deep gnomes camouflaged among rough grey rocks and crystal geodes.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "mushroom_forest_underdark", "alias": "w"}},
                "npcs": [{"name": "Deep Gnome Gemcutter", "desc": "A small, earth-skinned gnome carving a glowing emerald.", "level": 16, "role": "civilian"}]
            },
            "faerzress_rift": {
                "name": "The Glowing Faerzress Rift",
                "desc": "Wild subterranean radiation crackles in sheets of magical purple lightning across raw adamantine boulders.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "mushroom_forest_underdark", "alias": "n"}}
            },
            "poisoners_laboratory": {
                "name": "The Assassin Guild Poison Lab",
                "desc": "Glass alembics distilling deadly crawler mucus, black lotus extract, and spider venoms.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "slave_bazaar", "alias": "n"}}
            },
            "noble_house_gates": {
                "name": "Gates of House Baenre",
                "desc": "Adamantine gates flanked by twin rearing black onyx spider statues.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "stalactite_boulevard", "alias": "e"}}
            },
            "lizard_stable": {
                "name": "The Subterranean Riding Lizard Stables",
                "desc": "Pens holding giant two-legged subterranean lizards that run effortlessly along walls and ceilings.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "ched_nasad_gates", "alias": "s"}}
            },
            "abyssal_well_underdark": {
                "name": "The Whispering Well of Souls",
                "desc": "A bottomless pit from which the agonized moans of sacrificed victims drift upward.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "temple_of_lolth", "alias": "w"}}
            },
            "web_bridge_high": {
                "name": "The Great High Web Bridge",
                "desc": "Thick steel-strength spider silk bridging two colossal stalactites three hundred feet in the air.",
                "terrain": "air",
                "exits": {"north": {"dest_id": "noble_house_gates", "alias": "n"}}
            },
            "drow_armory_vault": {
                "name": "Underdark Adamantine Armory",
                "desc": "Suits of mesh chainmail that dissolve if exposed to surface sunlight.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "academy_sorcere", "alias": "s"}}
            },
            "duergar_trade_depot": {
                "name": "The Grey Dwarf Smuggler Depot",
                "desc": "Grim duergar merchants trading heavy crossbows and subterranean iron.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "slave_bazaar", "alias": "n"}}
            },
            "chitin_craftsman": {
                "name": "The Chitin Weaver Studio",
                "desc": "Artisans carving breastplates from the polished shells of giant beetles.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "slave_bazaar", "alias": "e"}}
            },
            "torture_chamber_drow": {
                "name": "Inquisition Hall of Lolth",
                "desc": "Racks, thumbscrews, and iron maidens lined with adamantine spikes.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "matron_sanctum", "alias": "s"}}
            },
            "blind_cavern": {
                "name": "The Cavern of the Blind Fish",
                "desc": "An underground river flowing with cold, mineral-rich water.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "lizard_stable", "alias": "n"}}
            },
            "cloaker_roost": {
                "name": "The Howling Cloaker Roost",
                "desc": "Stalactites where flying, cloak-like leather predators hang waiting for prey.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "web_bridge_high", "alias": "d"}}
            },
            "hook_horror_den": {
                "name": "Den of the Hook Horrors",
                "desc": "A cavern echoing with strange clicking noises made by vulture-headed monstrosities with bone hooks.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "faerzress_rift", "alias": "e"}}
            },
            "beholder_tunnel": {
                "name": "The Spherical Eye Tunnel",
                "desc": "A perfectly smooth circular tunnel bored through solid granite by disintegration rays.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "faerzress_rift", "alias": "w"}}
            },
            "silent_library_drow": {
                "name": "The Black Archive of Curses",
                "desc": "Tomes written in Drow sign language and secret runes.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "academy_sorcere", "alias": "n"}}
            },
            "sacrificial_font": {
                "name": "The Font of Black Blood",
                "desc": "A stone basin where the lifeblood of surface elves is offered to the Spider Queen.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "temple_of_lolth", "alias": "e"}}
            },
            "stalagmite_spire": {
                "name": "Sentry Spire of the Vanguard",
                "desc": "A hollowed stalagmite fortress guarding the eastern approach.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "ched_nasad_gates", "alias": "w"}}
            },
            "underdark_sinkhole": {
                "name": "The Great Bottomless Sinkhole",
                "desc": "A sheer drop plummeting into the mantle of the world.",
                "terrain": "air",
                "exits": {"up": {"dest_id": "chasm_descent", "alias": "u"}}
            },
            "crystal_geode_vault": {
                "name": "The Imperial Amethyst Geode",
                "desc": "A cavern inside a single colossal hollow geode of violet quartz.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "deep_gnome_refuge", "alias": "s"}}
            },
            "yochlol_portal": {
                "name": "The Abyssal Demon Gate",
                "desc": "A swirling portal of boiling yellow slime connecting to the Demonweb Pits.",
                "terrain": "catacombs",
                "exits": {"down": {"dest_id": "matron_sanctum", "alias": "d"}}
            }
        }
    }


# =============================================================================
# ZONE 12: CASTLE RAVENCREST & VAMPIRE CRYPTS [Level 14-20, 30 Rooms]
# =============================================================================

def build_zone_ravenloft():
    return {
        "zone_key": "ravenloft_castle",
        "zone_name": "Castle Ravencrest & The Vampire Crypts",
        "default_terrain": "city",
        "base_coords": (20, 25, 15),
        "rooms": {
            "drawbridge_chasm": {
                "name": "The Drawbridge over Howling Mist",
                "desc": "A creaking wooden drawbridge spanning a thousand-foot gorge of swirling grey fog. Lightning flashes illuminate the black spires of Castle Ravencrest towering ahead against a blood-red moon.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "courtyard_gargoyles", "alias": "n"}},
                "npcs": [{"name": "Gargoyle Sentry", "desc": "A stone gargoyle that awakens with red burning eyes and outstretched bat wings.", "level": 14, "role": "warrior"}]
            },
            "courtyard_gargoyles": {
                "name": "The Courtyard of Weeping Statues",
                "desc": "Dead rose bushes and tangled briars choke cracked cobblestones. Rain drips from demonic stone gargoyles perched along the roofline.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "drawbridge_chasm", "alias": "s"}, "north": {"dest_id": "great_entry_hall", "alias": "n"}, "east": {"dest_id": "abandoned_carriage_house", "alias": "e"}},
                "npcs": [{"name": "Dire Wolf of Ravencrest", "desc": "A massive, mangy wolf with glowing eyes snarling from the shadows.", "level": 14, "role": "warrior"}]
            },
            "abandoned_carriage_house": {
                "name": "The Ghostly Carriage House",
                "desc": "A black velvet-lined horse-drawn carriage sits in silence, its four spectral black stallions stamping non-existent hooves.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "courtyard_gargoyles", "alias": "w"}}
            },
            "great_entry_hall": {
                "name": "The Grand Hall of Ravencrest",
                "desc": "A sweeping marble staircase ascends to the upper galleries. Massive iron chandeliers holding unlit black tapers hang from the timber ceiling. A huge roaring fireplace warms nothing.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "courtyard_gargoyles", "alias": "s"}, "north": {"dest_id": "grand_ballroom", "alias": "n"}, "up": {"dest_id": "upper_portrait_gallery", "alias": "u"}, "down": {"dest_id": "castle_dungeon_cells", "alias": "d"}},
                "npcs": [{"name": "Spectral Butler", "desc": "A translucent phantom in powdered wig bowing formally.", "level": 14, "role": "civilian"}]
            },
            "grand_ballroom": {
                "name": "The Ballroom of the Damned",
                "desc": "An opulent ballroom where a phantom pipe organ plays a haunting waltz by itself. Spectral lords and ladies in antique velvet dance without touching the floor.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "great_entry_hall", "alias": "s"}, "east": {"dest_id": "dining_hall_crimson", "alias": "e"}},
                "npcs": [{"name": "Vampiric Bride", "desc": "A pale, breathtaking noblewoman in a bloodstained wedding gown, revealing razor fangs.", "level": 17, "role": "rogue"}]
            },
            "dining_hall_crimson": {
                "name": "The Banquet Hall of Chalices",
                "desc": "A fifty-foot long mahogany banquet table laden with silver trenchers and crystal goblets filled with dark crimson blood-wine.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "grand_ballroom", "alias": "w"}},
                "items": [{"name": "Crimson Chalice of Blood", "desc": "A silver goblet inscribed with bat motifs, filled with vampire blood-wine."}]
            },
            "upper_portrait_gallery": {
                "name": "The Ancestral Portrait Gallery",
                "desc": "Paintings of the Von Ravencrest dynasty through the centuries. Every single portrait depicts the exact same man with the same pale features and dark piercing gaze.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "great_entry_hall", "alias": "d"}, "north": {"dest_id": "master_bedchamber", "alias": "n"}},
                "npcs": [{"name": "Animated Suit of Black Armor", "desc": "A towering suit of plate armor stepping forward with broadsword raised.", "level": 16, "role": "warrior"}]
            },
            "master_bedchamber": {
                "name": "The Master Bedchamber",
                "desc": "A four-poster bed draped in crimson velvet curtains. French doors open out onto a balcony overlooking the storm-tossed forest far below.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "upper_portrait_gallery", "alias": "s"}, "up": {"dest_id": "high_tower_spire", "alias": "u"}}
            },
            "high_tower_spire": {
                "name": "The High Spire of Count Vlad",
                "desc": "The highest room of the castle, surrounded by storm clouds and lightning. In the center sits an organ and a velvet-lined coffin of polished black ebony.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "master_bedchamber", "alias": "d"}},
                "npcs": [{"name": "Count Vlad von Ravencrest", "desc": "The ancient vampire lord, master of Castle Ravencrest, his fangs bared and his eyes burning with immortal hunger.", "level": 20, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Vampiric Signet Ring of the Bat", "desc": "A blood-red ruby ring that siphons vitality from struck foes."}]
            },
            "castle_dungeon_cells": {
                "name": "The Castle Dungeons",
                "desc": "Damp iron-barred cells where the Count's victims languish in madness. Water drips slowly into puddles of rust.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "great_entry_hall", "alias": "u"}, "north": {"dest_id": "torture_chamber_ravencrest", "alias": "n"}}
            },
            "torture_chamber_ravencrest": {
                "name": "The Inquisitor's Cellar",
                "desc": "Iron maidens, stretch racks, and braziers with branding irons. The air smells of old iron and dried blood.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "castle_dungeon_cells", "alias": "s"}, "down": {"dest_id": "vampire_crypt_vault", "alias": "d"}}
            },
            "vampire_crypt_vault": {
                "name": "The Ancient Crypt of Sarcophagi",
                "desc": "Rows of stone coffins packed with ancestral soil where the Count's spawn sleep during the daylight hours.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "torture_chamber_ravencrest", "alias": "u"}},
                "npcs": [{"name": "Vampire Spawn Bloodletter", "desc": "A feral, blood-hungry vampire newborn with wild eyes and clawed fingers.", "level": 16, "role": "warrior"}]
            },
            "wine_cellar_ravencrest": {
                "name": "The Vintage Wine Cellars",
                "desc": "Cobweb-covered oak casks dating back over three centuries.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "castle_dungeon_cells", "alias": "e"}}
            },
            "chapel_ravencrest": {
                "name": "The Desecrated Castle Chapel",
                "desc": "Broken stained glass and upside-down iron crosses.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "great_entry_hall", "alias": "w"}},
                "items": [{"name": "Unholy Silver Candelabra of Ravenloft", "desc": "A tarnished silver candelabra holding seven black wax tapers."}]
            },
            "library_dark_arts": {
                "name": "The Dark Occult Library",
                "desc": "Leather-bound grimoires on vampirism, blood rituals, and demonology.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "upper_portrait_gallery", "alias": "e"}}
            },
            "balcony_storm": {
                "name": "The Storm Balcony",
                "desc": "A stone balcony buffeted by rain and thunderous gale-force winds.",
                "terrain": "air",
                "exits": {"north": {"dest_id": "master_bedchamber", "alias": "n"}}
            },
            "servants_quarters_castle": {
                "name": "The Pale Servants' Quarters",
                "desc": "Tidy, unnervingly silent rooms where thralls sleep.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "great_entry_hall", "alias": "s"}}
            },
            "clock_tower_ravencrest": {
                "name": "The Castle Clock Mechanism",
                "desc": "Gigantic brass gears ticking loudly, striking midnight perpetually.",
                "terrain": "indoors",
                "exits": {"down": {"dest_id": "high_tower_spire", "alias": "d"}}
            },
            "armory_gothic": {
                "name": "The Gothic Knight Armory",
                "desc": "Fluted Maximilian plate armor and heavy zweihander swords.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "courtyard_gargoyles", "alias": "s"}}
            },
            "greenhouse_ravencrest": {
                "name": "The Conservatory of Poisonous Flora",
                "desc": "Glass greenhouse filled with black nightshade, belladonna, and ghost orchids.",
                "terrain": "forest",
                "exits": {"west": {"dest_id": "courtyard_gargoyles", "alias": "w"}}
            },
            "catwalk_rampart": {
                "name": "The North Battlements",
                "desc": "Crenellated stone walkway with iron cauldrons for boiling oil.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "courtyard_gargoyles", "alias": "s"}}
            },
            "mausoleum_grounds": {
                "name": "The Castle Graveyard",
                "desc": "Crooked gravestones of former castle servants shrouded in dense mist.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "courtyard_gargoyles", "alias": "e"}}
            },
            "sewer_drain_castle": {
                "name": "The Moat Siphon Drain",
                "desc": "An iron grating draining stagnant water into the ravine.",
                "terrain": "water_swim",
                "exits": {"down": {"dest_id": "castle_dungeon_cells", "alias": "d"}}
            },
            "parapet_view": {
                "name": "Parapet of the Howling Bats",
                "desc": "High vantage point where thousands of bats roost beneath the eaves.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "catwalk_rampart", "alias": "s"}}
            },
            "alchemical_laboratory": {
                "name": "The Count's Alchemical Laboratory",
                "desc": "Retorts and beakers bubbling with preservative fluids and embalming oils.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "library_dark_arts", "alias": "w"}}
            },
            "crypt_brides": {
                "name": "Crypt of the Three Brides",
                "desc": "Three stone sarcophagi draped in tattered lace and dead black roses.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "vampire_crypt_vault", "alias": "n"}}
            },
            "secret_passage_castle": {
                "name": "Secret Stair Behind the Tapestry",
                "desc": "A concealed spiral stone stair connecting the bedroom to the crypts.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "master_bedchamber", "alias": "u"}}
            },
            "kennel_vampiric": {
                "name": "Kennels of the Bloodhounds",
                "desc": "Iron pens where red-eyed hounds chew on bone marrow.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "courtyard_gargoyles", "alias": "s"}}
            },
            "belfry_roof": {
                "name": "The Castle Belfry Roof",
                "desc": "Slippery slate roof tiles high above the abyss under pouring rain.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "clock_tower_ravencrest", "alias": "d"}}
            },
            "abyssal_pit_castle": {
                "name": "The Oubliette",
                "desc": "A circular stone pit with no door and no escape, save for flight.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "castle_dungeon_cells", "alias": "u"}}
            }
        }
    }


# =============================================================================
# ZONE 13: THE CELESTIAL CLOUD CITADEL [Level 20-27+, 30 Rooms]
# =============================================================================

def build_zone_cloud_citadel():
    return {
        "zone_key": "cloud_citadel",
        "zone_name": "The Cloud Citadel of the Storm Giants",
        "default_terrain": "air",
        "base_coords": (0, 0, 60),
        "rooms": {
            "cumulus_gateway": {
                "name": "The Cloudbank Gateway",
                "desc": "You step onto a cloud bank that feels as solid as marble beneath your boots. Billowing white fog forms giant arches, framing a castle of blue crystal and white marble floating in the stratosphere.",
                "terrain": "air",
                "exits": {"north": {"dest_id": "thunder_bridge", "alias": "n"}},
                "npcs": [{"name": "Storm Roc Sentry", "desc": "A colossal golden eagle with a ninety-foot wingspan crackling with static electricity.", "level": 20, "role": "warrior"}]
            },
            "thunder_bridge": {
                "name": "The Bridge of Solid Lightning",
                "desc": "A translucent bridge formed of petrified electrical lightning connecting the outer clouds to the main gate of the citadel. Sparks dance beneath your soles.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "cumulus_gateway", "alias": "s"}, "north": {"dest_id": "giant_portcullis", "alias": "n"}},
                "npcs": [{"name": "Cloud Giant Halberdier", "desc": "An eighteen-foot tall giant with skin of storm-grey and hair of windblown clouds.", "level": 21, "role": "warrior"}]
            },
            "giant_portcullis": {
                "name": "The Great Gates of the Cloud Citadel",
                "desc": "A portcullis made from solid bars of cold-forged meteoric iron forty feet tall. Banners of storm clouds flutter from soaring parapets.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "thunder_bridge", "alias": "s"}, "north": {"dest_id": "hall_of_the_tempest", "alias": "n"}}
            },
            "hall_of_the_tempest": {
                "name": "Great Feast Hall of the Tempest",
                "desc": "A hall of colossal proportions. Giant oak tables are laden with roast mammoths and barrels of thunder-mead. High arched windows look out over the curved horizon of the world below.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "giant_portcullis", "alias": "s"}, "north": {"dest_id": "storm_throne_room", "alias": "n"}, "east": {"dest_id": "lightning_forge", "alias": "e"}, "west": {"dest_id": "roc_aerie", "alias": "w"}},
                "npcs": [{"name": "Storm Giant Thane", "desc": "A mighty giant in a mantle of polar bear fur drinking from an iron horn.", "level": 22, "role": "warrior"}]
            },
            "roc_aerie": {
                "name": "The High Roc Aerie",
                "desc": "Giant open-air nests made of whole pine trees perched on the cloud ledge. Rocs and storm griffins preen their feathers in the wind.",
                "terrain": "air",
                "exits": {"east": {"dest_id": "hall_of_the_tempest", "alias": "e"}},
                "items": [{"name": "Storm Roc Feather", "desc": "A six-foot golden quill feather that floats effortlessly on the air."}]
            },
            "lightning_forge": {
                "name": "The Forge of Thunderbolts",
                "desc": "Giant anvils where storm giant smiths harness raw lightning bolts directly from storm clouds, hammering them into javelins of electrical fury.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "hall_of_the_tempest", "alias": "w"}},
                "npcs": [{"name": "Master Stormsmith Thorik", "desc": "A one-eyed giant blacksmith catching lightning in bare hands.", "level": 23, "role": "warrior"}],
                "items": [{"name": "Javelin of Living Lightning", "desc": "A spear of crackling electricity that discharges on impact."}]
            },
            "storm_throne_room": {
                "name": "The Throne of the Sky King",
                "desc": "Carved from solid blue sapphire, the throne overlooks the stratosphere. In the seat rests King Hekaton, ruler of the giants, surrounded by storm cloud elementals.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "hall_of_the_tempest", "alias": "s"}, "up": {"dest_id": "stratosphere_pinnacle", "alias": "u"}},
                "npcs": [{"name": "Storm King Hekaton", "desc": "The colossal twenty-four foot sovereign of the storm giants, his eyes flashing with thunder, clutching the Thunderbolt Scepter.", "level": 27, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Thunderbolt Scepter of the Colossus", "desc": "A legendary relic that commands the winds, thunder, and lightning of the heavens."}]
            },
            "stratosphere_pinnacle": {
                "name": "The Stratosphere Observation Spire",
                "desc": "The highest pinnacle of the citadel, where the curvature of the world is plainly visible. The stars shine brightly even during the daytime.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "storm_throne_room", "alias": "d"}},
                "items": [{"name": "Crown of Cloud Sovereignty", "desc": "A diadem of frozen starlight and condensed cloud vapor."}]
            },
            "cloud_catwalk_east": {
                "name": "Eastern Cloud Rampart",
                "desc": "A parapet of hardened cumulus vapor overlooking thunderheads below.",
                "terrain": "air",
                "exits": {"west": {"dest_id": "giant_portcullis", "alias": "w"}}
            },
            "cloud_catwalk_west": {
                "name": "Western Cloud Rampart",
                "desc": "Where storm ballistas are mounted on solid cloud foundations.",
                "terrain": "air",
                "exits": {"east": {"dest_id": "giant_portcullis", "alias": "e"}}
            },
            "storm_giant_barracks": {
                "name": "Barracks of the Sky Guard",
                "desc": "Immense stone bunks with wool blankets as large as ship sails.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "cloud_catwalk_west", "alias": "s"}}
            },
            "mead_cellar_clouds": {
                "name": "Cellar of the Cloud Nectar",
                "desc": "Giant barrels of honey mead brewed from alpine wildflower nectar.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "hall_of_the_tempest", "alias": "n"}}
            },
            "cirrus_garden": {
                "name": "Garden of the Frost Flowers",
                "desc": "Delicate crystalline ice flowers growing out of frozen cloud vapor.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "roc_aerie", "alias": "e"}}
            },
            "wind_shrine": {
                "name": "Altar of the Four Winds",
                "desc": "A circular pavilion where the North, South, East, and West winds whisper.",
                "terrain": "air",
                "exits": {"north": {"dest_id": "cirrus_garden", "alias": "n"}},
                "items": [{"name": "Whistle of the North Wind", "desc": "A carved crystal whistle that summons a whirlwind when blown."}]
            },
            "griffin_stables": {
                "name": "The Storm Griffin Perch",
                "desc": "Giant eagle-lion hybrids resting on cloud ledges.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "roc_aerie", "alias": "s"}}
            },
            "armory_storm": {
                "name": "Armory of the Giants",
                "desc": "Shields as broad as barn doors and halberds twenty feet in length.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "lightning_forge", "alias": "n"}}
            },
            "astronomical_globe": {
                "name": "The Great Floating Orrery",
                "desc": "A giant mechanical model of the cosmos spinning in midair.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "storm_throne_room", "alias": "s"}}
            },
            "hailstone_magazine": {
                "name": "The Hailstone Ammunition Bin",
                "desc": "Boulders of solid blue ice ready to be loaded into giant catapults.",
                "terrain": "air",
                "exits": {"east": {"dest_id": "cloud_catwalk_east", "alias": "e"}}
            },
            "cloud_bridge_north": {
                "name": "The Misty Span",
                "desc": "A quiet cloud path leading toward the outer floating towers.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "storm_throne_room", "alias": "s"}}
            },
            "aurora_balcony": {
                "name": "Balcony of the Borealis",
                "desc": "Emerald and violet aurora ribbons wave right above your head.",
                "terrain": "air",
                "exits": {"west": {"dest_id": "cloud_bridge_north", "alias": "w"}}
            },
            "thunder_chamber": {
                "name": "The Acoustic Thunder Chamber",
                "desc": "A vaulted dome where giant drums resonate with rolling thunder.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "hall_of_the_tempest", "alias": "e"}}
            },
            "cloud_wharf": {
                "name": "The Sky Skiff Wharf",
                "desc": "Wooden mooring masts where flying skiffs anchor to cloud docks.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "cumulus_gateway", "alias": "n"}}
            },
            "ice_crystal_gallery": {
                "name": "The Frost Prism Gallery",
                "desc": "Sculptures of ice that never melt in the freezing stratosphere air.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "astronomical_globe", "alias": "w"}}
            },
            "cumulus_archway": {
                "name": "The Arch of the West Wind",
                "desc": "Natural cloud formations arching across the azure sky.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "wind_shrine", "alias": "s"}}
            },
            "skylight_colonnade": {
                "name": "The Solar Colonnade",
                "desc": "Pillars of white stone that absorb pure sunlight during the day.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "cloud_catwalk_west", "alias": "n"}}
            },
            "flying_bridge_spire": {
                "name": "Spire Bridge of the Heavens",
                "desc": "A dizzying walkway connecting two soaring towers in mid-air.",
                "terrain": "air",
                "exits": {"up": {"dest_id": "stratosphere_pinnacle", "alias": "u"}}
            },
            "cloud_abyss_drop": {
                "name": "The Edge of the World Drop",
                "desc": "Look straight down through gaps in the clouds at the miniature towns below.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "cloud_catwalk_east", "alias": "s"}}
            },
            "cyclone_well": {
                "name": "The Vortex Cyclone Well",
                "desc": "A captive spinning whirlwind used to power the citadel's elevators.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "hall_of_the_tempest", "alias": "d"}}
            },
            "sky_garden": {
                "name": "The Hanging Gardens of the Stratosphere",
                "desc": "Terraces of cloud soil growing radiant fruit that tastes of ozone and honey.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "cirrus_garden", "alias": "n"}}
            },
            "lightning_rod_apex": {
                "name": "The Primary Lightning Conductor",
                "desc": "A copper spire fifty feet high attracting continuous lightning strikes.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "lightning_forge", "alias": "d"}}
            }
        }
    }


# =============================================================================
# MARITIME ROUTE: DEEP BATHYSPHERE 'NAUTILUS'
# =============================================================================

def register_atlantea_ferry_routes():
    """
    Registers the 6th major maritime route:
    'The Bathysphere Nautilus' connecting Eldoria South Docks,
    Dead Man's Cove, and Atlantea Pearl Barrier.
    """
    bathysphere_route = {
        "key": "nautilus_sub",
        "name": "The Bathysphere 'Nautilus'",
        "operator": "Chief Engineer Aronnax",
        "operator_title": "Grand Master of Deep Oceanic Submersibles",
        "ports": ["south_docks", "dead_mans_cove", "atlantea_depths_atlantea_sea_gate", "atlantea_sea_gate"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "dead_mans_cove": "Dead Man's Cove (Smuggler's Coast)",
            "atlantea_depths_atlantea_sea_gate": "The Great Pearl Barrier of Atlantea",
            "atlantea_sea_gate": "The Great Pearl Barrier of Atlantea"
        },
        "fares": {
            ("south_docks", "atlantea_depths_atlantea_sea_gate"): 90,   # 9 silver
            ("atlantea_depths_atlantea_sea_gate", "south_docks"): 90,
            ("dead_mans_cove", "atlantea_depths_atlantea_sea_gate"): 60, # 6 silver
            ("atlantea_depths_atlantea_sea_gate", "dead_mans_cove"): 60,
            ("south_docks", "atlantea_sea_gate"): 90,
            ("atlantea_sea_gate", "south_docks"): 90,
            ("dead_mans_cove", "atlantea_sea_gate"): 60,
            ("atlantea_sea_gate", "dead_mans_cove"): 60
        },
        "desc": "A reinforced brass-plated submarine sphere with thick quartz viewports, air compressors, and searchlights.",
        "deck_key": "nautilus_deck"
    }
    sailing.FERRY_ROUTES["nautilus_sub"] = bathysphere_route
    return bathysphere_route


# =============================================================================
# MAIN EXPANSION PART 3 RUNNER
# =============================================================================

def run_bulk_ingestion_part3(clean_existing=True):
    """
    Executes bulk ingestion of Part 3 mythic zones (120 rooms) with:
    - Atlantea Sunken Metropolis
    - Underdark of Ched Nasad
    - Castle Ravencrest
    - Cloud Citadel of Storm Giants
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
        build_zone_atlantea,
        build_zone_underdark,
        build_zone_ravenloft,
        build_zone_cloud_citadel
    ]

    # Overland / Dungeon Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("underdark_drow", "chasm_descent", "ossuary", "down", "up"),
        ("ravenloft_castle", "drawbridge_chasm", "watchtower", "northeast", "southwest"),
        ("cloud_citadel", "cumulus_gateway", "summit", "climb into clouds", "descend to summit")
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

    # 4. Register Bathysphere Nautilus Submersible Route & Cabin Deck
    sub_deck = find_room_by_key("nautilus_deck")
    if not sub_deck:
        sub_deck = create_object(Room, key="The Bathysphere 'Nautilus' - Pressure Cabin", tags=[TAG_WORLD])
        sub_deck.tags.add("nautilus_deck", category="room_key")
        sub_deck.tags.add("atlantea_depths", category="zone")
        sub_deck.db.room_key = "nautilus_deck"
        sub_deck.db.desc = (
            "You stand inside the heavy riveted brass pressure cabin of the Bathysphere 'Nautilus'. "
            "Brass pressure dials hiss softly with compressed air, and heavy quartz portholes offer "
            "a breathtaking view of the dark ocean depths and glowing deep-sea leviathans."
        )
        sub_deck.db.zone = "Abyssal Trench"
        sub_deck.db.terrain = "indoors"
        sub_deck.db.coords = (-10, 10, -25)
        report["rooms_created"] += 1

    register_atlantea_ferry_routes()
    report["ferry_routes_added"].append("The Bathysphere 'Nautilus' (south_docks <-> dead_mans_cove <-> atlantea_sea_gate)")

    return report
