"""
Bulk World Ingestion Engine — Part 17: The "3,750+ Rooms Grand Empire Expansion"

Expands Eldoria beyond 3,750 rooms (reaching 3,759 rooms) across 4 legendary mythic, planar, subterranean, and classical adventure realms:
1. The Sunken Vaults of the Sunless Citadel & Gulthias Tree [Level 10-18 Subterranean Classic, 60 Rooms]
2. The Astral Githyanki War-Ship "The Void Dragon" & Creche Kliir [Level 20-28 Astral Combat, 60 Rooms]
3. The Enchanted Cloud Spire of Mount Olympus & The Pantheon Hall [Level 22-30 Divine Cloud, 60 Rooms]
4. The Buried Under-City of Old Skullport (Port of Shadows) [Level 15-24 Pirate Underdark, 60 Rooms]

Total Rooms Created in Part 17: 241 Rooms (including 'The Imperial Royal Stagecoach Crown & Clover' carriage interior)
Cumulative World Total: 3,518 + 241 = 3,759 Rooms!

Features:
- New 'The Imperial Royal Stagecoach Crown & Clover' overland post-road transit route in sailing.py
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
# ZONE 66: THE SUNLESS CITADEL & GULTHIAS TREE [Level 10-18, 60 Rooms]
# =============================================================================

def build_zone_sunless_citadel():
    zone_key = "sunless_citadel"
    zone_name = "The Sunken Vaults of the Sunless Citadel & Gulthias Tree"
    rooms = {}

    rooms["sunless_citadel_chasm_stairs"] = {
        "name": "The Old Stone Steps of the Sunless Citadel",
        "desc": "Weathered stone steps switchbacking down a yawning 200-foot chasm in the earth. Looming below in the subterranean darkness is the sunken fortress of an ancient dragon cult.",
        "terrain": "stone_dungeon",
        "exits": {"north": {"dest_id": "sunless_citadel_fortress_parapet", "alias": "n"}},
        "npcs": [{"name": "Citadel Kobold Guard", "desc": "A scaly red kobold with a sling and a rusted iron spear, defending the citadel stairs.", "level": 10, "role": "warrior"}]
    }

    rooms["sunless_citadel_fortress_parapet"] = {
        "name": "The Sunken Fortress Parapet",
        "desc": "A fortified battle terrace carved into the limestone cavern. Ruined ballistas and dragon-headed gargoyles overlook dry moats overgrown with briars.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "sunless_citadel_chasm_stairs", "alias": "s"},
            "east": {"dest_id": "sunless_citadel_kobold_shrine_meepo", "alias": "e"},
            "west": {"dest_id": "sunless_citadel_goblin_barricade", "alias": "w"},
            "north": {"dest_id": "sunless_citadel_hallway_01", "alias": "n"}
        },
        "npcs": [{"name": "Kobold Slinger", "desc": "A nimble kobold darting between arrow slits with pots of alchemical fire.", "level": 11, "role": "rogue"}]
    }

    rooms["sunless_citadel_kobold_shrine_meepo"] = {
        "name": "The Dragon Shrine of Meepo",
        "desc": "A small temple alcove where kobolds venerate a carved stone dragon altar with offerings of cave fungus, dried rats, and shiny copper coins.",
        "terrain": "stone_dungeon",
        "exits": {"west": {"dest_id": "sunless_citadel_fortress_parapet", "alias": "w"}},
        "npcs": [{"name": "Meepo the Dragon-Keeper", "desc": "A distraught kobold keeper sobbing over an empty dragon-cage.", "level": 10, "role": "civilian"}],
        "items": [{"name": "Draconic Kobold Token", "desc": "A polished brass token stamped with the profile of an ancient red dragon."}]
    }

    rooms["sunless_citadel_goblin_barricade"] = {
        "name": "The Spiked Goblin Barricade",
        "desc": "A reinforced wall of sharpened timber and rubble held by the Durbuluk goblin tribe, separating the upper ruins from the lower grove.",
        "terrain": "stone_dungeon",
        "exits": {"east": {"dest_id": "sunless_citadel_fortress_parapet", "alias": "e"}},
        "npcs": [{"name": "Durbuluk Goblin Champion", "desc": "A heavily armored goblin warrior carrying a spiked morningstar.", "level": 12, "role": "warrior"}]
    }

    rooms["sunless_citadel_twilight_grove_verge"] = {
        "name": "The Verge of the Twilight Grove",
        "desc": "The ruined stone gives way to a bizarre subterranean forest. The air is damp, smelling of fertile compost and bitter sap. Corrupted needle blights scuttle in the underbrush.",
        "terrain": "caves",
        "exits": {
            "south": {"dest_id": "sunless_citadel_hallway_18", "alias": "s"},
            "north": {"dest_id": "sunless_citadel_gulthias_roots", "alias": "n"}
        },
        "npcs": [{"name": "Corrupted Needle Blight", "desc": "A plant monstrosity made of animated briars and pine needles, shooting thorny spines.", "level": 14, "role": "warrior"}]
    }

    rooms["sunless_citadel_gulthias_roots"] = {
        "name": "The Roots of the Gulthias Tree",
        "desc": "Massive black roots the size of pythons twist across the cavern floor, pulsating with dark vampiric sap that weeps from fissures in the bark.",
        "terrain": "caves",
        "exits": {
            "south": {"dest_id": "sunless_citadel_twilight_grove_verge", "alias": "s"},
            "north": {"dest_id": "sunless_citadel_gulthias_tree_heart", "alias": "n"}
        },
        "npcs": [{"name": "Entangled Berserker", "desc": "A thrall of the Gulthias tree whose flesh is intertwined with woody vines.", "level": 16, "role": "warrior"}]
    }

    rooms["sunless_citadel_gulthias_tree_heart"] = {
        "name": "The Heart of the Gulthias Tree",
        "desc": "A colossal, gnarled tree growing in the sunless cavern, sprouting from a stake driven through an ancient vampire lord. Belak the Outcast tends to its bloody ruby fruit.",
        "terrain": "caves",
        "exits": {"south": {"dest_id": "sunless_citadel_gulthias_roots", "alias": "s"}},
        "npcs": [{"name": "Belak the Outcast & The Gulthias Tree", "desc": "A crazed druid wielding a staff of black vampiric wood, bound in unholy symbiosis with the corrupted Gulthias Tree.", "level": 20, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Gulthias Vampire Wood Staff", "desc": "A staff carved of dark briar wood that drains the life of struck enemies and commands plant blights."},
            {"name": "Red Fruit of the Gulthias Tree", "desc": "A crimson apple pulsating with dark vitality that restores health to the user at a shadowy cost."}
        ]
    }

    # 53 connected citadel chambers, tomb halls, and twilight grove pathways
    for i in range(1, 54):
        r_key = f"sunless_citadel_hallway_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Ancient carved limestone halls and overgrown root tunnels of the sunken citadel. "
            f"Faded dragon frescoes line the walls, crumbling under centuries of subterranean dampness. [Citadel Sector #{i}]"
        )
        r_name = f"Sunless Citadel Chamber #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"sunless_citadel_hallway_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"sunless_citadel_hallway_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"sunless_citadel_hallway_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"sunless_citadel_hallway_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "sunless_citadel_fortress_parapet", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "sunless_citadel_twilight_grove_verge", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "sunless_citadel_gulthias_roots", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Twig Blight Pack", "desc": "A skittering bundle of dried thorns and twigs with sharp wooden teeth.", "level": 12, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Giant Skeleton Guardian", "desc": "A skeletal warrior of an ancient draconic champion wielding a rusted broadsword.", "level": 14, "role": "warrior"})

        if i == 21:
            items.append({"name": "Ancient Sunless Citadel Key", "desc": "A rusted iron skeleton key shaped like a curled dragon wyrmling."})

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
        "base_coords": (-140, 180, -90),
        "rooms": rooms
    }


# =============================================================================
# ZONE 67: THE GITHYANKI ASTRAL WAR-SHIP & CRECHE KLIIR [Level 20-28, 60 Rooms]
# =============================================================================

def build_zone_githyanki_warship():
    zone_key = "githyanki_warship"
    zone_name = "The Githyanki Astral War-Ship 'The Void Dragon' & Creche Kliir"
    rooms = {}

    rooms["githyanki_warship_stern_flight_deck"] = {
        "name": "The Stern Flight Deck of 'The Void Dragon'",
        "desc": "A colossal landing deck carved from the petrified bone of an astral leviathan, suspended in the silvery twilight of the Astral Plane. Red dragons perch along the bulwarks, waiting for command.",
        "terrain": "planar",
        "exits": {"north": {"dest_id": "githyanki_warship_main_catwalk", "alias": "n"}},
        "npcs": [{"name": "Githyanki Warrior Vanguard", "desc": "A gaunt, yellow-skinned warrior clad in ornate spiked silver plate, wielding a greatsword with telekinetic precision.", "level": 20, "role": "warrior"}]
    }

    rooms["githyanki_warship_main_catwalk"] = {
        "name": "The Central Bone Catwalk",
        "desc": "A wide gangway spanning the vessel's cavernous hollow ribcage. Astral mists drift between the bone beams, and psionic runes pulse with violet light.",
        "terrain": "planar",
        "exits": {
            "south": {"dest_id": "githyanki_warship_stern_flight_deck", "alias": "s"},
            "east": {"dest_id": "githyanki_warship_red_dragon_roost", "alias": "e"},
            "west": {"dest_id": "githyanki_warship_silver_sword_forge", "alias": "w"},
            "north": {"dest_id": "githyanki_warship_corridor_01", "alias": "n"}
        },
        "npcs": [{"name": "Githyanki Psion", "desc": "A bald githyanki mystic with glowing purple eyes hovering inches above the deck.", "level": 22, "role": "mage"}]
    }

    rooms["githyanki_warship_red_dragon_roost"] = {
        "name": "The Red Dragon Roosting Deck",
        "desc": "Massive chains of enchanted adamantine hold platforms where adult red dragons, sworn by pact to Vlaakith, feed on astral prey and roar with furnace heat.",
        "terrain": "planar",
        "exits": {"west": {"dest_id": "githyanki_warship_main_catwalk", "alias": "w"}},
        "npcs": [{"name": "Pact-Bound Red Dragon", "desc": "A massive crimson dragon with leathery wings spanning sixty feet, exhaling plumes of brimstone.", "level": 25, "role": "warrior"}],
        "items": [{"name": "Astral Dragon Saddle", "desc": "An ornate war-saddle fitted with silver stirrups for fighting in zero-gravity space."}]
    }

    rooms["githyanki_warship_silver_sword_forge"] = {
        "name": "The Silver Sword Mind-Forge",
        "desc": "A psionic forge where silver blades are hammered not with heat, but with pure concentrated psychic will, embedding mental disruptor fields into each weapon.",
        "terrain": "stone",
        "exits": {"east": {"dest_id": "githyanki_warship_main_catwalk", "alias": "e"}},
        "npcs": [{"name": "Githyanki Weapon-Smith", "desc": "A master armorer channeling psionic energy through an adamantine anvil.", "level": 23, "role": "warrior"}]
    }

    rooms["githyanki_warship_creche_hatchery"] = {
        "name": "The Hatchery of Creche Kliir",
        "desc": "A warm chamber lined with translucent amber pods where githyanki young are trained from birth in psionics, swordplay, and hatred of the mind flayers.",
        "terrain": "stone",
        "exits": {
            "south": {"dest_id": "githyanki_warship_corridor_18", "alias": "s"},
            "north": {"dest_id": "githyanki_warship_bridge_antechamber", "alias": "n"}
        },
        "npcs": [{"name": "Creche Master Varsh", "desc": "A stern taskmaster drilling cadets with ruthless efficiency.", "level": 24, "role": "mage"}]
    }

    rooms["githyanki_warship_bridge_antechamber"] = {
        "name": "The Bridge Antechamber of Vlaakith",
        "desc": "A solemn gallery dominated by a colossal portrait of Lich-Queen Vlaakith CLVII. Incense burns in bronze braziers, and the air crackles with psychic tension.",
        "terrain": "planar",
        "exits": {
            "south": {"dest_id": "githyanki_warship_creche_hatchery", "alias": "s"},
            "north": {"dest_id": "githyanki_warship_kithrak_command_bridge", "alias": "n"}
        },
        "npcs": [{"name": "Githyanki Knight Justiciar", "desc": "An elite knight carrying a silver greatsword that shimmers with razor psionic power.", "level": 26, "role": "warrior"}]
    }

    rooms["githyanki_warship_kithrak_command_bridge"] = {
        "name": "The Helm of Kith'rak Voss",
        "desc": "The apex bridge of the void warship. Huge crystal viewports look out over the silvery depths of the Astral Plane. Seated at the helm is Supreme Kith'rak Voss, commanding the vanguard.",
        "terrain": "planar",
        "exits": {"south": {"dest_id": "githyanki_warship_bridge_antechamber", "alias": "s"}},
        "npcs": [{"name": "Kith'rak Voss, Supreme Dragon-Rider", "desc": "The supreme warlord of the githyanki astral fleet, wielding the legendary Silver Greatsword of Psionics and commanding legions of dragon-riders.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Githyanki Silver Greatsword of Psionics", "desc": "A silver greatsword that severs the astral silver cords of planar travelers and delivers massive psychic shockwaves."},
            {"name": "Plate of the Astral Vanguard", "desc": "Spiked full plate armor of polished silver that deflects mind-control spells."}
        ]
    }

    # 53 connected bone decks, psionic corridors, and barracks
    for i in range(1, 54):
        r_key = f"githyanki_warship_corridor_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Bone corridors and silver-plated bulkheads aboard the colossal astral war-ship. "
            f"Psionic glyphs along the ribcage illuminate the zero-gravity passages. [Void Warship Sector #{i}]"
        )
        r_name = f"Githyanki Warship Deck #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"githyanki_warship_corridor_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"githyanki_warship_corridor_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"githyanki_warship_corridor_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"githyanki_warship_corridor_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "githyanki_warship_main_catwalk", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "githyanki_warship_creche_hatchery", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "githyanki_warship_bridge_antechamber", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Githyanki Raider", "desc": "A swift fighter leaping between platforms with telekinetic agility.", "level": 21, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Astral Hound Scout", "desc": "A two-headed quadruped tracking psionic traces across the silver void.", "level": 22, "role": "warrior"})

        if i == 23:
            items.append({"name": "Phial of Astral Starlight", "desc": "A vial of silver astral light that cures mental exhaustion and restores mana."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "planar",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "planar",
        "base_coords": (180, 260, 200),
        "rooms": rooms
    }


# =============================================================================
# ZONE 68: THE CLOUD SPIRE OF MOUNT OLYMPUS [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_olympus_spire():
    zone_key = "olympus_spire"
    zone_name = "The Enchanted Cloud Spire of Mount Olympus & The Pantheon Hall"
    rooms = {}

    rooms["olympus_spire_golden_cloud_stair"] = {
        "name": "The Golden Cloud Stair of Olympus",
        "desc": "A monumental staircase carved of glowing golden cloud-stuff ascending above the mortal atmosphere. Above, the snow-capped peak of Mount Olympus glitters under an eternal Greek sun.",
        "terrain": "marble",
        "exits": {"north": {"dest_id": "olympus_spire_colonnade_of_heroes", "alias": "n"}},
        "npcs": [{"name": "Myrmidon Golden Sentry", "desc": "A bronze-armored hoplite carrying an eight-foot ash spear and a polished round shield.", "level": 22, "role": "warrior"}]
    }

    rooms["olympus_spire_colonnade_of_heroes"] = {
        "name": "The Great Colonnade of Heroes",
        "desc": "A majestic avenue of fluted white marble pillars draped with flowering purple wisteria. Statues of Hercules, Perseus, and Achilles stand in eternal honor along the walkway.",
        "terrain": "marble",
        "exits": {
            "south": {"dest_id": "olympus_spire_golden_cloud_stair", "alias": "s"},
            "east": {"dest_id": "olympus_spire_ambrosia_orchard", "alias": "e"},
            "west": {"dest_id": "olympus_spire_nectar_fountain", "alias": "w"},
            "north": {"dest_id": "olympus_spire_terrace_01", "alias": "n"}
        },
        "npcs": [{"name": "Olympian Herald", "desc": "A winged youth wearing golden sandals and carrying the caduceus of the gods.", "level": 23, "role": "rogue"}]
    }

    rooms["olympus_spire_ambrosia_orchard"] = {
        "name": "The Golden Ambrosia Orchard",
        "desc": "Orchards of golden apple trees cultivated by the Hesperides. The fruit glows with divine immortality, and nymphs sing gentle hymns in the shade.",
        "terrain": "marble",
        "exits": {"west": {"dest_id": "olympus_spire_colonnade_of_heroes", "alias": "w"}},
        "npcs": [{"name": "Hesperide Maiden", "desc": "A radiant nymph with flowers in her hair guarding the golden fruit.", "level": 24, "role": "mage"}],
        "items": [{"name": "Golden Apple of Mount Olympus", "desc": "A divine apple of solid gold that grants supreme health and cures all mortal afflictions."}]
    }

    rooms["olympus_spire_nectar_fountain"] = {
        "name": "The Nectar Fountain of the Gods",
        "desc": "A fountain carved of pure crystal where sweet golden nectar bubbles forth into basins of alabaster. Drinking from the stream warms the spirit with celestial fire.",
        "terrain": "marble",
        "exits": {"east": {"dest_id": "olympus_spire_colonnade_of_heroes", "alias": "e"}},
        "npcs": [{"name": "Cupbearer of Olympus", "desc": "A graceful youth ladling sparkling nectar into golden goblets.", "level": 23, "role": "civilian"}]
    }

    rooms["olympus_spire_pantheon_portal"] = {
        "name": "The Grand Portico of the Twelve Olympians",
        "desc": "Twelve colossal bronze braziers burn with eternal holy fire before double doors of gold and ivory. The scent of frankincense and roasted sacrifices hangs in the mountain air.",
        "terrain": "marble",
        "exits": {
            "south": {"dest_id": "olympus_spire_terrace_18", "alias": "s"},
            "north": {"dest_id": "olympus_spire_pantheon_high_council", "alias": "n"}
        },
        "npcs": [{"name": "Olympian Centaur Vanguard", "desc": "A proud centaur armed with a composite bow of horn and sinew.", "level": 26, "role": "warrior"}]
    }

    rooms["olympus_spire_pantheon_high_council"] = {
        "name": "The High Council Chamber of Mount Olympus",
        "desc": "A circular amphitheater of white marble looking out over the entire mortal cosmos below. Twelve thrones carved of ivory and gold form a circle beneath an open sky of pure lightning.",
        "terrain": "marble",
        "exits": {
            "south": {"dest_id": "olympus_spire_pantheon_portal", "alias": "s"},
            "north": {"dest_id": "olympus_spire_throne_of_thunder", "alias": "n"}
        },
        "npcs": [{"name": "Athena's Sacred Owl Construct", "desc": "A mechanical owl of gold and sapphire that speaks with the voice of strategic wisdom.", "level": 27, "role": "mage"}]
    }

    rooms["olympus_spire_throne_of_thunder"] = {
        "name": "The Cloud Throne of Olympian Thunder",
        "desc": "The highest pinnacle of Mount Olympus. Seated upon a throne of solid thunderclouds and crackling golden lightning is the Avatar of Olympian Thunder, holding the master bolt.",
        "terrain": "marble",
        "exits": {"south": {"dest_id": "olympus_spire_pantheon_high_council", "alias": "s"}},
        "npcs": [{"name": "Avatar of Olympian Thunder", "desc": "The supreme ruler of Olympus, with a beard of swirling storm clouds and eyes of blinding lightning, holding the master thunderbolt.", "level": 30, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Javelin of Crackling Thunderbolts", "desc": "A spear of pure solid lightning that can be hurled to smite foes with catastrophic thunderclaps."},
            {"name": "Aegis of Olympus", "desc": "A legendary shield forged of bronze and Gorgon skin that strikes terror into all enemies who behold it."}
        ]
    }

    # 53 connected terrace steps, marble temples, and cloud gardens
    for i in range(1, 54):
        r_key = f"olympus_spire_terrace_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Alabaster colonnades and fragrant olive groves overlooking the clouds. "
            f"White marble steps lead upward toward the shimmering halls of the gods. [Olympus Terrace #{i}]"
        )
        r_name = f"Mount Olympus Cloud Terrace #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"olympus_spire_terrace_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"olympus_spire_terrace_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"olympus_spire_terrace_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"olympus_spire_terrace_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "olympus_spire_colonnade_of_heroes", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "olympus_spire_pantheon_portal", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "olympus_spire_pantheon_high_council", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Spartan Ghost Warrior", "desc": "A phantom phalanx soldier marching with unwavering discipline.", "level": 24, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Olympian Griffin", "desc": "A regal beast with the forequarters of an eagle and the hindquarters of a lion.", "level": 25, "role": "warrior"})

        if i == 25:
            items.append({"name": "Phial of Olympian Nectar", "desc": "A golden elixir that grants temporary invulnerability to mortal blows."})

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
        "base_coords": (20, 260, 250),
        "rooms": rooms
    }


# =============================================================================
# ZONE 69: OLD SKULLPORT (PORT OF SHADOWS) [Level 15-24, 60 Rooms]
# =============================================================================

def build_zone_skullport_shadows():
    zone_key = "skullport_shadows"
    zone_name = "The Buried Under-City of Old Skullport (Port of Shadows)"
    rooms = {}

    rooms["skullport_shadows_subterranean_wharf"] = {
        "name": "The Lower Flotsam Wharf of Skullport",
        "desc": "A damp underground port carved into the limestone cavern beneath Waterdeep. Derelict barges and smuggler sloops creak against rotting timber pilings in the black, sluggish waters.",
        "terrain": "underdark",
        "exits": {"north": {"dest_id": "skullport_shadows_keelhaul_avenue", "alias": "n"}},
        "npcs": [{"name": "Skullport Smuggler", "desc": "A scarred pirate in leather armor unloading crates of contraband under the dim light of skull-lanterns.", "level": 16, "role": "rogue"}]
    }

    rooms["skullport_shadows_keelhaul_avenue"] = {
        "name": "Keelhaul Avenue",
        "desc": "A muddy, slanting street lined with leaning wooden shacks, crooked taverns, and pawnshops. Green sulfur flares flicker in iron baskets suspended from stalactites.",
        "terrain": "city",
        "exits": {
            "south": {"dest_id": "skullport_shadows_subterranean_wharf", "alias": "s"},
            "east": {"dest_id": "skullport_shadows_black_flotsam_tavern", "alias": "e"},
            "west": {"dest_id": "skullport_shadows_slavers_market", "alias": "w"},
            "north": {"dest_id": "skullport_shadows_flotsam_lane_01", "alias": "n"}
        },
        "npcs": [{"name": "Duergar Contrabandist", "desc": "A grey dwarf trading illicit poison vials in the shadow of an alleyway.", "level": 18, "role": "rogue"}]
    }

    rooms["skullport_shadows_black_flotsam_tavern"] = {
        "name": "The Black Flotsam Tavern",
        "desc": "A notorious drinking dive smelling of sour ale, rotting kelp, and pipe smoke. Sahuagin corsairs and drow mercenaries arm-wrestle across tables made of driftwood.",
        "terrain": "city",
        "exits": {"west": {"dest_id": "skullport_shadows_keelhaul_avenue", "alias": "w"}},
        "npcs": [{"name": "One-Eyed Grog-Master", "desc": "A burly half-orc barkeep sliding mugs of foul dwarven rotgut down the stained bar.", "level": 17, "role": "civilian"}],
        "items": [{"name": "Bottle of Skullport Gut-Rot Rum", "desc": "Vile, fiery liquor distilled from subterranean cave fungus."}]
    }

    rooms["skullport_shadows_slavers_market"] = {
        "name": "The Slavers' Iron Market",
        "desc": "A grim stone square dominated by an iron auction block. Chains rattle as duergar and drow slavers examine captive surface dwellers.",
        "terrain": "underdark",
        "exits": {"east": {"dest_id": "skullport_shadows_keelhaul_avenue", "alias": "e"}},
        "npcs": [{"name": "Drow Slaver Captain", "desc": "A ruthless dark elf carrying an electrified whip and iron manacles.", "level": 20, "role": "warrior"}]
    }

    rooms["skullport_shadows_skulls_plaza"] = {
        "name": "The Plaza of the Floating Skulls",
        "desc": "A wide square where thirteen flaming, disembodied human skulls drift silently in the air. These Netherese entities enforce the minimal, bloody laws of the Shadow Port.",
        "terrain": "city",
        "exits": {
            "south": {"dest_id": "skullport_shadows_flotsam_lane_18", "alias": "s"},
            "north": {"dest_id": "skullport_shadows_skum_lord_manor_gate", "alias": "n"}
        },
        "npcs": [{"name": "Flaming Skull Sentinel", "desc": "A floating human skull surrounded by green magical fire that speaks with ancient Netherese telepathy.", "level": 22, "role": "mage"}]
    }

    rooms["skullport_shadows_skum_lord_manor_gate"] = {
        "name": "The Gates of the Shadow Keep",
        "desc": "A fortress built of waterlogged ship timbers and iron armor plates, guarded by hulking aboleth-corrupted mutants and aquatic mercenaries.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "skullport_shadows_skulls_plaza", "alias": "s"},
            "north": {"dest_id": "skullport_shadows_throne_of_the_skum_lord", "alias": "n"}
        },
        "npcs": [{"name": "Skum Enforcer", "desc": "A mutated amphibious brute with slimy webbed fingers and needle-like teeth.", "level": 24, "role": "warrior"}]
    }

    rooms["skullport_shadows_throne_of_the_skum_lord"] = {
        "name": "The Throne of the Skum-Lord",
        "desc": "The damp inner sanctum of the ruler of Skullport. High upon a throne of rusted cannons and skull-carved timbers sits the Skum-Lord, controlling the underworld smuggling empire.",
        "terrain": "underdark",
        "exits": {"south": {"dest_id": "skullport_shadows_skum_lord_manor_gate", "alias": "s"}},
        "npcs": [{"name": "The Skum-Lord of the Shadow Port", "desc": "The sinister aquatic tyrant who controls all smuggling, slaving, and piracy beneath Waterdeep, wielding a cutlass of black flotsam and dark psychic magic.", "level": 26, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Cutlass of Black Flotsam", "desc": "A cursed cutlass carved from shipwreck timber that blinds struck targets with magical black slime."},
            {"name": "Ring of Shadow Skulls", "desc": "A brass ring that summons a floating green-flame skull to scout ahead of the wearer."}
        ]
    }

    # 53 connected flotsam alleys, canal bridges, and smuggler catwalks
    for i in range(1, 54):
        r_key = f"skullport_shadows_flotsam_lane_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Twisting flotsam catwalks and slippery stone docks suspended over black underground canals. "
            f"Smugglers, tieflings, and pirate cutthroats slip through the shadows. [Skullport Lane #{i}]"
        )
        r_name = f"Skullport Flotsam Lane #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"skullport_shadows_flotsam_lane_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"skullport_shadows_flotsam_lane_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"skullport_shadows_flotsam_lane_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"skullport_shadows_flotsam_lane_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "skullport_shadows_keelhaul_avenue", "alias": "s"}
        if i == 18:
            exits["north"] = {"dest_id": "skullport_shadows_skulls_plaza", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "skullport_shadows_skum_lord_manor_gate", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Skullport Cutpurse", "desc": "A stealthy rogue lurking behind a stack of contraband fish barrels.", "level": 17, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Wererat Scavenger", "desc": "A diseased rat-human hybrid gnawing on bone flotsam in the gutter.", "level": 19, "role": "warrior"})

        if i == 24:
            items.append({"name": "Pouch of Smuggler's Black Pearls", "desc": "A velvet pouch containing rare black pearls dredged from subterranean lakes."})

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
        "base_coords": (140, -180, -70),
        "rooms": rooms
    }


# =============================================================================
# OVERLAND CARRIAGE ROUTE HELPER
# =============================================================================

def register_royal_coach_ferry_routes():
    """Ensures The Imperial Royal Stagecoach 'Crown & Clover' is registered in sailing.FERRY_ROUTES."""
    if "royal_coach_line" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["royal_coach_line"] = {
            "key": "royal_coach_line",
            "name": 'The Imperial Royal Stagecoach "Crown & Clover"',
            "operator": "Coachman Barnaby",
            "operator_title": "Master of the Imperial Post Roads",
            "ports": ["north_gate", "midgaard_district_midgaard_port", "foothills", "midgaard_port"],
            "port_names": {
                "north_gate": "Eldoria North Gate Post Depot",
                "midgaard_district_midgaard_port": "Midgaard South Coach Terminal",
                "midgaard_port": "Midgaard South Coach Terminal",
                "foothills": "Craggy Foothills Stage Post"
            },
            "fares": {
                ("north_gate", "midgaard_district_midgaard_port"): 35,
                ("midgaard_district_midgaard_port", "north_gate"): 35,
                ("north_gate", "foothills"): 40,
                ("foothills", "north_gate"): 40,
                ("midgaard_district_midgaard_port", "foothills"): 45,
                ("foothills", "midgaard_district_midgaard_port"): 45,
                ("north_gate", "midgaard_port"): 35,
                ("midgaard_port", "north_gate"): 35,
                ("midgaard_port", "foothills"): 45,
                ("foothills", "midgaard_port"): 45
            },
            "desc": "A gilded four-horse imperial stagecoach with sprung steel chassis, plush velvet passenger seating, and leather luggage boot.",
            "deck_key": "royal_coach_interior"
        }


# =============================================================================
# MASTER RUNNER FOR PART 17
# =============================================================================

def run_bulk_ingestion_part17(clean_existing=False):
    """
    Executes Part 17 of the bulk world expansion ("3,750+ Rooms Grand Empire Expansion"):
    - The Sunken Vaults of the Sunless Citadel & Gulthias Tree (60 rooms)
    - The Astral Githyanki War-Ship "The Void Dragon" & Creche Kliir (60 rooms)
    - The Enchanted Cloud Spire of Mount Olympus & The Pantheon Hall (60 rooms)
    - The Buried Under-City of Old Skullport (60 rooms)
    Plus The Imperial Royal Stagecoach 'Crown & Clover' carriage interior (1 room).
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
        build_zone_sunless_citadel,
        build_zone_githyanki_warship,
        build_zone_olympus_spire,
        build_zone_skullport_shadows
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("sunless_citadel", "sunless_citadel_chasm_stairs", "catacombs", "descend stone steps into sunless citadel", "ascend chasm stairs back to catacombs"),
        ("githyanki_warship", "githyanki_warship_stern_flight_deck", "astral_nexus", "board githyanki warship in astral space", "disembark warship to astral nexus platform"),
        ("olympus_spire", "olympus_spire_golden_cloud_stair", "summit", "ascend golden cloud stair to mount olympus", "descend golden stair back to summit"),
        ("skullport_shadows", "skullport_shadows_subterranean_wharf", "dead_mans_cove", "enter submerged canal tunnel to skullport", "sail out of shadow canal to dead mans cove")
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

    # 4. Register Imperial Royal Stagecoach Route & Carriage Room
    royal_coach_interior = find_room_by_key("royal_coach_interior")
    if not royal_coach_interior:
        royal_coach_interior = create_object(Room, key='The Imperial Royal Stagecoach "Crown & Clover" - Interior Carriage', tags=[TAG_WORLD])
        royal_coach_interior.tags.add("royal_coach_interior", category="room_key")
        royal_coach_interior.tags.add("sunless_citadel", category="zone")
        royal_coach_interior.db.room_key = "royal_coach_interior"
        royal_coach_interior.db.desc = (
            "You sit within the luxurious interior of the Imperial Stagecoach. "
            "Padded crimson velvet cushions line the mahogany benches, while glass lanterns "
            "sway gently from brass ceiling brackets as iron-shod wheels clatter across the highway."
        )
        royal_coach_interior.db.zone = "Imperial Post Roads"
        royal_coach_interior.db.terrain = "indoors"
        royal_coach_interior.db.coords = (0, 40, 5)
        report["rooms_created"] += 1

    register_royal_coach_ferry_routes()
    report["ferry_routes_added"].append('The Imperial Royal Stagecoach "Crown & Clover" (north_gate <-> midgaard_port <-> foothills)')

    return report

