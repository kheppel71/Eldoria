"""
Bulk World Ingestion Engine — Part 14: The "3,000+ Rooms Epic Milestone" Expansion

Crosses the historic 3,000-room threshold (reaching 3,036 rooms) across 4 legendary planar and mythic adventure realms:
1. The Sunken City of Atlantis & Poseidon's Trench [Level 18-26 Oceanic Deep, 60 Rooms]
2. The Radiant Solar Spire of Mount Celestia & Lunia's Shore [Level 20-28 Planar Radiant, 60 Rooms]
3. Sigil, City of Doors & The Hive Ward [Level 16-25 Planar Hub, 60 Rooms]
4. The Primordial Fire Realm of Muspelheim & Surtr's Iron Smelters [Level 22-30 Primordial Flame, 60 Rooms]

Total Rooms Created in Part 14: 241 Rooms (including 'The Planar Astral Skiff Voidstrider' weather deck)
Cumulative World Total: 2,795 + 241 = 3,036 Rooms!

Features:
- New 'The Planar Astral Skiff Voidstrider' interplanar transit route in sailing.py
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
# ZONE 54: THE SUNKEN CITY OF ATLANTIS & POSEIDON'S TRENCH [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_sunken_atlantis():
    zone_key = "sunken_atlantis"
    zone_name = "The Sunken City of Atlantis & Poseidon's Trench"
    rooms = {}

    rooms["atlantis_pearly_archway"] = {
        "name": "The Pearly Archway of Sunken Atlantis",
        "desc": "A monumental triumphal arch of mother-of-pearl and white marble standing upright upon the abyssal sea floor. Iridescent schools of glowing fish drift among ancient hieroglyphs celebrating the Sea God.",
        "terrain": "water_swim",
        "exits": {"north": {"dest_id": "atlantis_coral_colonnade_north", "alias": "n"}},
        "npcs": [{"name": "Atlantean Hoplite Sentry", "desc": "A muscular aquatic warrior clad in verdigris bronze armor, brandishing a hooked coral spear.", "level": 18, "role": "warrior"}]
    }

    rooms["atlantis_coral_colonnade_north"] = {
        "name": "The Great Coral Colonnade",
        "desc": "A broad underwater avenue flanked by soaring marble pillars overgrown with vibrant branching sea-fans and luminous purple brain corals.",
        "terrain": "water_swim",
        "exits": {
            "south": {"dest_id": "atlantis_pearly_archway", "alias": "s"},
            "east": {"dest_id": "atlantis_bioluminescent_gardens", "alias": "e"},
            "west": {"dest_id": "atlantis_hydrothermal_vents", "alias": "w"},
            "north": {"dest_id": "atlantis_abyssal_trench_01", "alias": "n"}
        },
        "npcs": [{"name": "Triton Wave-Priestess", "desc": "A serene triton chanting aqueous incantations that keep currents calm.", "level": 20, "role": "mage"}]
    }

    rooms["atlantis_bioluminescent_gardens"] = {
        "name": "The Bioluminescent Algae Gardens",
        "desc": "An expansive underwater terrace terraced with phosphorescent anemones and glowing kelp forests casting an ethereal teal radiance across ancient carved statues.",
        "terrain": "water_swim",
        "exits": {"west": {"dest_id": "atlantis_coral_colonnade_north", "alias": "w"}},
        "npcs": [{"name": "Abyssal Siren", "desc": "A shimmering aquatic siren whose haunting songs echo through the deep currents.", "level": 21, "role": "rogue"}],
        "items": [{"name": "Glowing Pearl of Atlantis", "desc": "A fist-sized sea pearl pulsing with aquatic luminescence."}]
    }

    rooms["atlantis_hydrothermal_vents"] = {
        "name": "The Smoldering Hydrothermal Vents",
        "desc": "Black mineral chimneys venting superheated, mineral-rich plumes into the freezing abyssal currents. Colony crustaceans and tube worms thrive around the volcanic heat.",
        "terrain": "water_swim",
        "exits": {"east": {"dest_id": "atlantis_coral_colonnade_north", "alias": "e"}},
        "npcs": [{"name": "Hydrothermal Magma Crab", "desc": "An armored sea crustacean with volcanic rock carapace and claw blades that sizzle in the water.", "level": 22, "role": "warrior"}]
    }

    rooms["atlantis_poseidon_temple"] = {
        "name": "The High Temple of Poseidon",
        "desc": "A majestic domed basilica formed from petrified sea-glass. Water pressure is held back by an ancient divine barrier, allowing air breathing within this sacred sanctum.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "atlantis_abyssal_trench_15", "alias": "s"},
            "north": {"dest_id": "atlantis_royal_treasury", "alias": "n"}
        },
        "npcs": [{"name": "High Priest of the Deep Oceans", "desc": "An ancient Atlantean elder holding a coral staff crowned with an eye of leviathan.", "level": 24, "role": "mage"}]
    }

    rooms["atlantis_royal_treasury"] = {
        "name": "The Royal Treasury of Sunken Gold",
        "desc": "Chests of ancient doubloons, barnacled platinum ingots, and uncut aquamarines piled high in alcoves guarded by coral automaton guardians.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "atlantis_poseidon_temple", "alias": "s"},
            "north": {"dest_id": "atlantis_poseidon_throne", "alias": "n"}
        },
        "npcs": [{"name": "Coral Golem Guardian", "desc": "A hulking automaton assembled from compressed coral reef and sea-iron bindings.", "level": 25, "role": "warrior"}]
    }

    rooms["atlantis_poseidon_throne"] = {
        "name": "The Oceanic Throne of King Amphitrite",
        "desc": "The apex of the sunken empire. Carved from the skull of an ancient kraken, the throne looks out over the colossal oceanic abyss where leviathans drift like shadows.",
        "terrain": "stone_dungeon",
        "exits": {"south": {"dest_id": "atlantis_royal_treasury", "alias": "s"}},
        "npcs": [{"name": "King Amphitrite of the Deep Trench", "desc": "The sovereign of the sunken empire, adorned in shell-crown and wielding the three-pronged Trident of the Abyssal Lord.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Trident of the Ocean Lord", "desc": "A mythic three-pronged spear forged of orichalcum that commands oceanic tides and tidal waves."},
            {"name": "Crown of Atlantis", "desc": "An ancient regal diadem of polished abalone shell and sea pearls."}
        ]
    }

    # 53 connected abyssal trench and sunken ruin rooms to complete 60 rooms
    for i in range(1, 54):
        r_key = f"atlantis_abyssal_trench_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Ancient submerged stone streets, sunken amphitheatres, and deep oceanic drop-offs. "
            f"Bioluminescent jellyfish drift gracefully across the ruins. [Atlantis Sector #{i}]"
        )
        r_name = f"Sunken Atlantis Promenade #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"atlantis_abyssal_trench_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"atlantis_abyssal_trench_{i+1:02d}", "alias": "n"}
        if i + 6 <= 53:
            exits["east"] = {"dest_id": f"atlantis_abyssal_trench_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"atlantis_abyssal_trench_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "atlantis_coral_colonnade_north", "alias": "s"}
        if i == 15:
            exits["north"] = {"dest_id": "atlantis_poseidon_temple", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "atlantis_royal_treasury", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Atlantean Sea-Scout", "desc": "A swift swimmer patrolling the sunken streets with a bone crossbow.", "level": 19, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Abyssal Moray Eel", "desc": "A colossal predatory eel with needle teeth lurking inside cracked marble walls.", "level": 21, "role": "warrior"})

        if i == 25:
            items.append({"name": "Amphora of Atlantean Nectar", "desc": "An ancient sealed clay jar containing enchanted nectar that grants water breathing."})

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
        "base_coords": (150, -150, -60),
        "rooms": rooms
    }


# =============================================================================
# ZONE 55: THE RADIANT SOLAR SPIRE OF MOUNT CELESTIA & LUNIA'S SHORE [Level 20-28, 60 Rooms]
# =============================================================================

def build_zone_celestia_spire():
    zone_key = "celestia_spire"
    zone_name = "The Radiant Solar Spire of Mount Celestia & Lunia's Shore"
    rooms = {}

    rooms["celestia_spire_silver_shore"] = {
        "name": "The Silver Sea Shore of Lunia",
        "desc": "The holy surf of the Silver Sea laps against shores of pure powdered pearl. Above, the infinite golden heights of the Seven Heavens rise into crystal daylight, warm and full of divine tranquility.",
        "terrain": "planar",
        "exits": {"north": {"dest_id": "celestia_spire_platinum_bridge", "alias": "n"}},
        "npcs": [{"name": "Lunia Shore Sentinel", "desc": "A hound archon standing vigilant guard beside the holy waters, bearing a greatsword of pure silver.", "level": 20, "role": "warrior"}]
    }

    rooms["celestia_spire_platinum_bridge"] = {
        "name": "The Platinum Bridge of Archons",
        "desc": "An arched bridge forged of flawless platinum spanning a chasm of golden clouds. Flocks of white doves and singing spirits soar through the gentle updrafts.",
        "terrain": "planar",
        "exits": {
            "south": {"dest_id": "celestia_spire_silver_shore", "alias": "s"},
            "north": {"dest_id": "celestia_spire_radiant_bastion", "alias": "n"},
            "east": {"dest_id": "celestia_spire_trumpet_choir", "alias": "e"}
        },
        "npcs": [{"name": "Lantern Archon Envoy", "desc": "A luminous floating globe of celestial radiance that speaks in bell-like tones.", "level": 21, "role": "mage"}]
    }

    rooms["celestia_spire_trumpet_choir"] = {
        "name": "The Terrace of the Trumpet Choir",
        "desc": "A circular platform of carved alabaster where celestial heralds blow golden trumpets whose majestic fanfare echoes across the planar heavens.",
        "terrain": "planar",
        "exits": {"west": {"dest_id": "celestia_spire_platinum_bridge", "alias": "w"}},
        "npcs": [{"name": "Trumpet Archon Herald", "desc": "A winged celestial of breathtaking elegance holding an ornate silver horn.", "level": 23, "role": "mage"}],
        "items": [{"name": "Hymnal of Mount Celestia", "desc": "A golden-bound book of divine choral music that inspires radiant bravery."}]
    }

    rooms["celestia_spire_radiant_bastion"] = {
        "name": "The Radiant Bastion of Seven Heavens",
        "desc": "A mighty fortress citadel carved into the living crystal of the mountain. Banners of solar gold and moon-silver flutter in eternal holy winds.",
        "terrain": "planar",
        "exits": {
            "south": {"dest_id": "celestia_spire_platinum_bridge", "alias": "s"},
            "north": {"dest_id": "celestia_spire_terrace_01", "alias": "n"}
        },
        "npcs": [{"name": "Sword Archon Vanguard", "desc": "A celestial warrior whose arms transform into blades of white solar flame.", "level": 24, "role": "warrior"}]
    }

    rooms["celestia_spire_solar_hall"] = {
        "name": "The Great Hall of Solar Glory",
        "desc": "A towering throne room bathed in blinding sunlight from stained crystal glass. Celestial knights kneel in eternal vigil around a fountain of liquid starlight.",
        "terrain": "planar",
        "exits": {
            "south": {"dest_id": "celestia_spire_terrace_20", "alias": "s"},
            "north": {"dest_id": "celestia_spire_pure_radiance", "alias": "n"}
        },
        "npcs": [{"name": "Planetar Justiciar", "desc": "A towering green-skinned angelic warrior with four feathered wings and a two-handed greatsword.", "level": 26, "role": "warrior"}]
    }

    rooms["celestia_spire_pure_radiance"] = {
        "name": "The Spire of Pure Radiance",
        "desc": "A pinnacle of pure condensed light high above the clouds. Evil thoughts vanish like smoke before the overwhelming divine majesty of this holy sanctuary.",
        "terrain": "planar",
        "exits": {
            "south": {"dest_id": "celestia_spire_solar_hall", "alias": "s"},
            "north": {"dest_id": "celestia_spire_seven_heavens_throne", "alias": "n"}
        },
        "npcs": [{"name": "Solar Seraph", "desc": "A supreme angel radiating golden fire, wielding a bow of dawn-light.", "level": 27, "role": "mage"}]
    }

    rooms["celestia_spire_seven_heavens_throne"] = {
        "name": "The High Throne of Archon Lord Raziel",
        "desc": "The highest sanctum on Mount Celestia. Archon Lord Raziel sits upon a throne of diamond, watching over the multiverse with eyes of pure celestial dawn.",
        "terrain": "planar",
        "exits": {"south": {"dest_id": "celestia_spire_pure_radiance", "alias": "s"}},
        "npcs": [{"name": "Archon Lord Raziel", "desc": "The champion of the Seven Heavens, crowned with solar starlight and bearing the Platinum Blade of Truth.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Platinum Blade of Truth", "desc": "A celestial greatsword forged of pure radiant starlight that banishes fiends and cleanses curses."},
            {"name": "Halo of Solar Grace", "desc": "A floating ring of golden dawn-light that shields the wearer in divine favor."}
        ]
    }

    # 53 connected terrace and crystal ascent rooms to complete 60 rooms
    for i in range(1, 54):
        r_key = f"celestia_spire_terrace_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Alabaster stairs and crystal gardens ascending Mount Celestia. "
            f"Peaceful streams of holy water trickle over diamond stones. [Celestia Spire Tier #{i}]"
        )
        r_name = f"Mount Celestia Solar Terrace #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"celestia_spire_terrace_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"celestia_spire_terrace_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"celestia_spire_terrace_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"celestia_spire_terrace_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "celestia_spire_radiant_bastion", "alias": "s"}
        if i == 20:
            exits["north"] = {"dest_id": "celestia_spire_solar_hall", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "celestia_spire_pure_radiance", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Warden Archon", "desc": "A stalwart celestial warrior patrolling the holy terrace.", "level": 22, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Celestial Pegasus", "desc": "A magnificent winged stallion with silver hooves and eyes of sapphire.", "level": 23, "role": "warrior"})

        if i == 18:
            items.append({"name": "Phial of Holy Silver Water", "desc": "Pure holy water from the Silver Sea that fully restores mana and cleanses poison."})

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
        "base_coords": (30, 160, 50),
        "rooms": rooms
    }


# =============================================================================
# ZONE 56: SIGIL, CITY OF DOORS & THE HIVE WARD [Level 16-25, 60 Rooms]
# =============================================================================

def build_zone_sigil_doors():
    zone_key = "sigil_doors"
    zone_name = "Sigil, City of Doors & The Hive Ward"
    rooms = {}

    rooms["sigil_doors_portal_gateway"] = {
        "name": "The Torus Gateway of Sigil",
        "desc": "You step through a shimmering rift into the City of Doors. Looking up, the curved torus cityscape loops high overhead against the smoggy twilight sky, lined with spires, chimneys, and razorvine-covered roofs.",
        "terrain": "city",
        "exits": {"north": {"dest_id": "sigil_doors_smoldering_corpse_tavern", "alias": "n"}},
        "npcs": [{"name": "Harmonium Enforcer", "desc": "A stern law-enforcer clad in red-and-orange lacquered plate armor carrying a capture pole.", "level": 18, "role": "warrior"}]
    }

    rooms["sigil_doors_smoldering_corpse_tavern"] = {
        "name": "The Smoldering Corpse Bar",
        "desc": "A notorious establishment reeking of cheap rotgut, brimstone, and frying meat. Floating in the center of the bar in a sphere of magical fire is the suspended body of an immortal burning spirit.",
        "terrain": "city",
        "exits": {
            "south": {"dest_id": "sigil_doors_portal_gateway", "alias": "s"},
            "east": {"dest_id": "sigil_doors_mortuary_dustmen", "alias": "e"},
            "west": {"dest_id": "sigil_doors_great_gymnasium", "alias": "w"},
            "north": {"dest_id": "sigil_doors_hive_alley_01", "alias": "n"}
        },
        "npcs": [{"name": "Barkeeper Barkis", "desc": "A grizzled planar barkeep wiping down a beer-stained copper counter with a stained rag.", "level": 16, "role": "civilian"}],
        "items": [{"name": "Mug of Smoldering Corpse Ale", "desc": "A fiery alcoholic brew that warms the belly with planar fire."}]
    }

    rooms["sigil_doors_mortuary_dustmen"] = {
        "name": "The Great Mortuary of the Dustmen",
        "desc": "A somber black stone mausoleum where the Dustmen receive bodies from across the Multiverse. Silent zombie workers scrub marble dissecting slabs under the cold gaze of hooded morticians.",
        "terrain": "stone_dungeon",
        "exits": {"west": {"dest_id": "sigil_doors_smoldering_corpse_tavern", "alias": "w"}},
        "npcs": [{"name": "Dustman Mortician", "desc": "A gaunt figure in black robes, philosophizing about the sweet release of the True Death.", "level": 20, "role": "mage"}]
    }

    rooms["sigil_doors_great_gymnasium"] = {
        "name": "The Great Gymnasium of the Transcendent",
        "desc": "A grand bathhouse and athletic forum constructed of polished granite where Cipher philosophers practice meditation, martial arts, and instinctive reaction.",
        "terrain": "city",
        "exits": {"east": {"dest_id": "sigil_doors_smoldering_corpse_tavern", "alias": "e"}},
        "npcs": [{"name": "Transcendent Master", "desc": "A martial artist who moves with absolute fluid speed without hesitating to think.", "level": 22, "role": "rogue"}]
    }

    rooms["sigil_doors_hall_of_speakers"] = {
        "name": "The Hall of Speakers",
        "desc": "The civic center of Sigil, where representatives of every planar faction argue laws, philosophy, and multiversal politics beneath soaring stained-glass domes.",
        "terrain": "city",
        "exits": {
            "south": {"dest_id": "sigil_doors_hive_alley_20", "alias": "s"},
            "north": {"dest_id": "sigil_doors_armory_doomguard", "alias": "n"}
        },
        "npcs": [{"name": "Sign of One Orator", "desc": "A persuasive speaker arguing that the multiverse is merely an illusion of consciousness.", "level": 23, "role": "mage"}]
    }

    rooms["sigil_doors_armory_doomguard"] = {
        "name": "The Armory of the Doomguard",
        "desc": "A fortress of rusted iron and forged brass where weaponsmiths craft entropy-infused armaments, venerating the slow decay of all creation.",
        "terrain": "stone_dungeon",
        "exits": {
            "south": {"dest_id": "sigil_doors_hall_of_speakers", "alias": "s"},
            "north": {"dest_id": "sigil_doors_spire_apex", "alias": "n"}
        },
        "npcs": [{"name": "Doomguard Weaponmaster", "desc": "A heavily armored knight wielding an entropic greatsword that rusts armor on contact.", "level": 25, "role": "warrior"}]
    }

    rooms["sigil_doors_spire_apex"] = {
        "name": "The High Balcony of the Spire Apex",
        "desc": "A desolate cobblestone plaza looking directly towards the shadow of the Lady of Pain. Razorvine clings thick to the walls, and the silence of the multiverse weighs heavily upon all mortals.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "sigil_doors_armory_doomguard", "alias": "s"}},
        "npcs": [{"name": "High Dabus Factotum of the Lady", "desc": "A floating horned humanoid wearing robes of deep violet, speaking in glowing rebuses and glyphs that hover in the air.", "level": 27, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Spire Key of the Infinite Doors", "desc": "A strange brass skeleton key that can unlock dormant dimensional rifts throughout the planes."},
            {"name": "Whip of Razorvine Tendrils", "desc": "A fearsome barbed whip woven from the sharp, metallic thorns of Sigil's razorvine."}
        ]
    }

    # 53 connected Hive Ward streets, alleys, and slophouse ruins to complete 60 rooms
    for i in range(1, 54):
        r_key = f"sigil_doors_hive_alley_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Narrow, twisting alleys paved with cracked cobbles under the shadow of the Spire. "
            f"Beggars, planar scavengers, and tiefling rogues dart between leaning tenements. [Hive Ward #{i}]"
        )
        r_name = f"Sigil Hive Ward Alley #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"sigil_doors_hive_alley_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"sigil_doors_hive_alley_{i+1:02d}", "alias": "n"}
        if i + 6 <= 53:
            exits["east"] = {"dest_id": f"sigil_doors_hive_alley_{i+6:02d}", "alias": "e"}
        if i - 6 >= 1:
            exits["west"] = {"dest_id": f"sigil_doors_hive_alley_{i-6:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "sigil_doors_smoldering_corpse_tavern", "alias": "s"}
        if i == 20:
            exits["north"] = {"dest_id": "sigil_doors_hall_of_speakers", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "sigil_doors_armory_doomguard", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Hive Cutpurse", "desc": "A shifty tiefling rogue looking to liberate jink from unwary primes.", "level": 17, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Bleak Cabal Thinker", "desc": "A melancholic philosopher staring into the gutter, contemplating multiversal meaninglessness.", "level": 19, "role": "civilian"})

        if i == 15:
            items.append({"name": "Pouch of Planar Jink", "desc": "A pouch of mixed silver and brass coins minted across different planes."})

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
        "base_coords": (220, 220, 100),
        "rooms": rooms
    }


# =============================================================================
# ZONE 57: THE PRIMORDIAL FIRE REALM OF MUSPELHEIM & SURTR'S SMELTERS [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_muspelheim_forge():
    zone_key = "muspelheim_forge"
    zone_name = "The Primordial Fire Realm of Muspelheim & Surtr's Iron Smelters"
    rooms = {}

    rooms["muspelheim_basalt_bridge"] = {
        "name": "The Great Basalt Causeway of Muspelheim",
        "desc": "A broad causeway of black volcanic basalt suspended over a roaring river of liquid magma. The sky is a furnace of boiling crimson ash and volcanic lightning.",
        "terrain": "lava",
        "exits": {"north": {"dest_id": "muspelheim_molten_slag_river", "alias": "n"}},
        "npcs": [{"name": "Muspelheim Cinder Guard", "desc": "A towering fire giant warrior clad in black plate armor with a flaming broadsword.", "level": 22, "role": "warrior"}]
    }

    rooms["muspelheim_molten_slag_river"] = {
        "name": "The River of Liquid Slag",
        "desc": "A river of incandescent white-hot slag surging through deep basalt canyons. The heat is intense enough to scorch cloth and melt ordinary steel.",
        "terrain": "lava",
        "exits": {
            "south": {"dest_id": "muspelheim_basalt_bridge", "alias": "s"},
            "east": {"dest_id": "muspelheim_hellhound_kennel", "alias": "e"},
            "west": {"dest_id": "muspelheim_cinder_drake_roost", "alias": "w"},
            "north": {"dest_id": "muspelheim_forge_slag_path_01", "alias": "n"}
        },
        "npcs": [{"name": "Magma Salamander", "desc": "A serpentine elemental monster slithering effortlessly through the molten rock.", "level": 23, "role": "warrior"}]
    }

    rooms["muspelheim_hellhound_kennel"] = {
        "name": "The Ashen Hellhound Kennels",
        "desc": "Caverns glowing with red coals where massive fire-breathing canines gnaw on obsidian bones and growl with embers dripping from their jowls.",
        "terrain": "fire",
        "exits": {"west": {"dest_id": "muspelheim_molten_slag_river", "alias": "w"}},
        "npcs": [{"name": "Alpha Hellhound", "desc": "A monstrous obsidian hound the size of a warhorse, breathing jets of white napalm flame.", "level": 24, "role": "warrior"}],
        "items": [{"name": "Obsidian Hellhound Collar", "desc": "A spiky collar of volcanic glass radiating infernal heat."}]
    }

    rooms["muspelheim_cinder_drake_roost"] = {
        "name": "The Roost of the Cinder Drakes",
        "desc": "High jagged volcanic spires where winged drakes of crimson scales bask in updrafts of noxious sulfurous smoke.",
        "terrain": "fire",
        "exits": {"east": {"dest_id": "muspelheim_molten_slag_river", "alias": "e"}},
        "npcs": [{"name": "Muspelheim Cinder Drake", "desc": "A vicious four-legged drake whose breath incinerates rock into bubbling lava.", "level": 25, "role": "warrior"}]
    }

    rooms["muspelheim_great_iron_smelter"] = {
        "name": "Surtr's Great Iron Smelter",
        "desc": "A colossal industrial forge powered by primordial volcanic rifts. Giant bellows the size of galleons roar as molten iron flows into immense molds for world-sundering siege weapons.",
        "terrain": "fire",
        "exits": {
            "south": {"dest_id": "muspelheim_forge_slag_path_20", "alias": "s"},
            "north": {"dest_id": "muspelheim_obsidian_anvils", "alias": "n"}
        },
        "npcs": [{"name": "Fire Giant Master Smelter", "desc": "A bearded titan of flame holding iron tongs twenty feet long, hammering glowing plates with rhythmic thunder.", "level": 26, "role": "warrior"}]
    }

    rooms["muspelheim_obsidian_anvils"] = {
        "name": "The Hall of Obsidian Anvils",
        "desc": "A cavernous hall lined with anvils carved from single blocks of volcanic obsidian. Weapons crafted here are tempered in the blood of primordial magma beasts.",
        "terrain": "fire",
        "exits": {
            "south": {"dest_id": "muspelheim_great_iron_smelter", "alias": "s"},
            "north": {"dest_id": "muspelheim_surtr_throne_of_flame", "alias": "n"}
        },
        "npcs": [{"name": "Surtr's Flame Archon", "desc": "A winged elemental commander of primordial flame, wielding a spear of incandescent magma.", "level": 28, "role": "mage"}]
    }

    rooms["muspelheim_surtr_throne_of_flame"] = {
        "name": "The Molten Throne of King Surtr",
        "desc": "The burning heart of Muspelheim. High upon a throne carved of hardened volcanic magma sits Surtr, the Primordial Fire Giant King, waiting for the twilight of the gods with a sword brighter than the sun.",
        "terrain": "fire",
        "exits": {"south": {"dest_id": "muspelheim_obsidian_anvils", "alias": "s"}},
        "npcs": [{"name": "Surtr, King of Fire Giants", "desc": "The apocalyptic lord of fire giants, standing thirty feet tall with a beard of roaring flames and the world-cleaving Twilight Blade.", "level": 30, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Twilight Blade of Surtr", "desc": "A colossal flaming greatsword that burns with the primordial fire destined to consume the cosmos at Ragnarok."},
            {"name": "Crown of Muspelheim Cinders", "desc": "A jagged crown of black volcanic rock and burning eternal embers."}
        ]
    }

    # 53 connected slag paths, molten causeways, and lava trenches to complete 60 rooms
    for i in range(1, 54):
        r_key = f"muspelheim_forge_slag_path_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Basalt walkways winding between bubbling pools of lava and roaring sulfur vents. "
            f"The sound of distant giant hammers echoes through the fiery gloom. [Muspelheim Sector #{i}]"
        )
        r_name = f"Muspelheim Slag Pathway #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"muspelheim_forge_slag_path_{i-1:02d}", "alias": "s"}
        if i < 53:
            exits["north"] = {"dest_id": f"muspelheim_forge_slag_path_{i+1:02d}", "alias": "n"}
        if i + 5 <= 53:
            exits["east"] = {"dest_id": f"muspelheim_forge_slag_path_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"muspelheim_forge_slag_path_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "muspelheim_molten_slag_river", "alias": "s"}
        if i == 20:
            exits["north"] = {"dest_id": "muspelheim_great_iron_smelter", "alias": "n"}
        if i == 53:
            exits["east"] = {"dest_id": "muspelheim_obsidian_anvils", "alias": "e"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Muspelheim Fire Elemental", "desc": "A roaring vortex of living flame dancing through the sulfur clouds.", "level": 23, "role": "mage"})
        elif i % 10 == 0:
            npcs.append({"name": "Fire Giant Blacksmith Apprentice", "desc": "A hulking young giant hauling heavy ingots of raw pig iron.", "level": 24, "role": "warrior"})

        if i == 28:
            items.append({"name": "Chunk of Primordial Slag", "desc": "A heavy rock infused with volcanic heat that never cools down."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "fire",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "fire",
        "base_coords": (180, 90, -30),
        "rooms": rooms
    }


# =============================================================================
# MARITIME ROUTE HELPER
# =============================================================================

def register_voidstrider_ferry_routes():
    """Ensures The Planar Astral Skiff 'Voidstrider' is registered in sailing.FERRY_ROUTES."""
    if "voidstrider_skiff" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["voidstrider_skiff"] = {
            "key": "voidstrider_skiff",
            "name": 'The Planar Astral Skiff "Voidstrider"',
            "operator": "Void-Captain Zephyrus",
            "operator_title": "Astral Navigator of the Great Wheel",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "sigil_doors_portal_gateway", "sigil_portal"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "sigil_doors_portal_gateway": "The Torus Gateway of Sigil",
                "sigil_portal": "The Torus Gateway of Sigil"
            },
            "fares": {
                ("south_docks", "sigil_doors_portal_gateway"): 115,
                ("sigil_doors_portal_gateway", "south_docks"): 115,
                ("praxis_province_praxis_harbor", "sigil_doors_portal_gateway"): 100,
                ("sigil_doors_portal_gateway", "praxis_province_praxis_harbor"): 100,
                ("south_docks", "sigil_portal"): 115,
                ("sigil_portal", "south_docks"): 115,
                ("praxis_province_praxis_harbor", "sigil_portal"): 100,
                ("sigil_portal", "praxis_province_praxis_harbor"): 100
            },
            "desc": "A sleek astral vessel forged of iridescent silver-wood and propelled by sails of pure psychic energy through planar color pools.",
            "deck_key": "voidstrider_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 14
# =============================================================================

def run_bulk_ingestion_part14(clean_existing=False):
    """
    Executes Part 14 of the bulk world expansion ("3,000+ Rooms Epic Milestone"):
    - The Sunken City of Atlantis & Poseidon's Trench (60 rooms)
    - The Radiant Solar Spire of Mount Celestia & Lunia's Shore (60 rooms)
    - Sigil, City of Doors & The Hive Ward (60 rooms)
    - The Primordial Fire Realm of Muspelheim & Surtr's Iron Smelters (60 rooms)
    Plus The Planar Astral Skiff 'Voidstrider' weather deck (1 room).
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
        build_zone_sunken_atlantis,
        build_zone_celestia_spire,
        build_zone_sigil_doors,
        build_zone_muspelheim_forge
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("sunken_atlantis", "atlantis_pearly_archway", "dead_mans_cove", "dive into abyssal trench towards atlantis", "ascend ocean current back to dead mans cove"),
        ("celestia_spire", "celestia_spire_silver_shore", "cathedral", "ascend holy light beam to mount celestia spire", "descend crystal steps back to cathedral"),
        ("sigil_doors", "sigil_doors_portal_gateway", "plaza", "step through shimmering door-portal into sigil", "step through exit arch back to grand plaza"),
        ("muspelheim_forge", "muspelheim_basalt_bridge", "city_of_brass_obsidian_pier", "cross bridge of molten slag into muspelheim", "retreat across basalt bridge back to city of brass")
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

    # 4. Register Voidstrider Skiff Ferry Route & Weather Deck
    voidstrider_deck = find_room_by_key("voidstrider_deck")
    if not voidstrider_deck:
        voidstrider_deck = create_object(Room, key='The Planar Astral Skiff "Voidstrider" - Weather Deck', tags=[TAG_WORLD])
        voidstrider_deck.tags.add("voidstrider_deck", category="room_key")
        voidstrider_deck.tags.add("sigil_doors", category="zone")
        voidstrider_deck.db.room_key = "voidstrider_deck"
        voidstrider_deck.db.desc = (
            "You stand upon the polished silver-wood deck of the astral skiff. "
            "Sheets of psychic energy catch the planar winds, while color pools drift "
            "beneath the hull like vast glowing portals to other dimensions."
        )
        voidstrider_deck.db.zone = "Astral Sea"
        voidstrider_deck.db.terrain = "planar"
        voidstrider_deck.db.coords = (100, 100, 100)
        report["rooms_created"] += 1

    register_voidstrider_ferry_routes()
    report["ferry_routes_added"].append('The Planar Astral Skiff "Voidstrider" (south_docks <-> praxis_province_praxis_harbor <-> sigil_doors_portal_gateway)')

    return report
