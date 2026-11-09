"""
Bulk World Ingestion Engine — Part 11: The "2,300+ Rooms Milestone" Grand Astral & Planar Expansion

Expands Eldoria to 2,313 rooms across 4 high-challenge realms:
1. The Astral Dreadnought & Githyanki Sky-Citadel [Level 20-28 Planar, 60 Rooms]
2. The Sunken City of Omu & Fane of the Night Serpent [Level 16-24 Jungle & Catacombs, 60 Rooms]
3. The Frozen Glacier Spire of Svardborg [Level 16-25 Arctic Mountain, 60 Rooms]
4. The Cursed Shadowfell Necropolis of Moil [Level 22-30 Endgame Void, 60 Rooms]

Total Rooms Created in Part 11: 241 Rooms (including 'Winter's Fang' Icebreaker weather deck)
Cumulative World Total: 2,072 + 241 = 2,313 Rooms!

Features:
- New 'The Frost-Cutter Icebreaker Winter\'s Fang' arctic transit route in sailing.py
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
# ZONE 42: THE ASTRAL DREADNOUGHT & GITHYANKI SKY-CITADEL [Level 20-28, 60 Rooms]
# =============================================================================

def build_zone_astral_dreadnought():
    zone_key = "astral_dreadnought"
    zone_name = "The Astral Dreadnought & Githyanki Sky-Citadel"
    rooms = {}

    rooms["astral_silver_wharf"] = {
        "name": "The Silver Void Wharf of Tu'narath",
        "desc": "A dock constructed of petrified thought-matter jutting into the silvery expanse of the Astral Plane. Wisps of psychic mist drift around astral skiffs moored to psychic anchor chains.",
        "terrain": "air",
        "exits": {"north": {"dest_id": "dead_god_ribcage_hall", "alias": "n"}},
        "npcs": [{"name": "Githyanki Astral Sentry", "desc": "A gaunt, yellow-skinned warrior with ornate plate armor holding a glowing silver greatsword.", "level": 20, "role": "warrior"}]
    }

    rooms["dead_god_ribcage_hall"] = {
        "name": "The Ribcage Colonnade of the Dead God",
        "desc": "Massive ossified rib bones of an ancient petrified deity arch hundreds of feet overhead, forming the vaulted ceiling of a colossal astral fortress.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "astral_silver_wharf", "alias": "s"}, "north": {"dest_id": "astral_passage_01", "alias": "n"}, "east": {"dest_id": "tu_narath_barracks", "alias": "e"}}
    }

    rooms["tu_narath_barracks"] = {
        "name": "The Red Dragon Knights' Quarters",
        "desc": "Polished silver weapon racks line the walls, and the pungent smell of dragon-smoke fills the air. Elite githyanki knights practice deadly telekinetic katas.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "dead_god_ribcage_hall", "alias": "w"}, "north": {"dest_id": "astral_passage_15", "alias": "n"}},
        "npcs": [{"name": "Githyanki Dragon Knight", "desc": "A decorated warrior bonded to an astral red dragon, wielding a psychic lance.", "level": 23, "role": "warrior"}],
        "items": [{"name": "Talisman of Pure Thought", "desc": "A crystal medallion that allows the wearer to move by thought-power alone in gravity-free voids."}]
    }

    rooms["inquisitor_judgment_hall"] = {
        "name": "The Hall of Telepathic Inquisition",
        "desc": "A circular platform suspended over a bottomless silver abyss. Psychic runes pulse across the floor, stripping secrets from the minds of mortal prisoners.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "astral_passage_30", "alias": "s"}},
        "npcs": [{"name": "Lich-Queen Mind Cleaver", "desc": "A psionic zealot in crimson silks whose gaze severs mental consciousness.", "level": 24, "role": "mage"}],
        "items": [{"name": "Psionic Focus Crystal", "desc": "A pulsating amethyst that amplifies spellcasting and telepathic precision."}]
    }

    rooms["dreadnought_silver_eye"] = {
        "name": "The Chasm of the Astral Dreadnought",
        "desc": "An enormous abyssal hollow where a titanic, serpentine beast of spiked obsidian hide and a single colossal cyclopean eye floats slumbering, radiating terrifying antimagic.",
        "terrain": "air",
        "exits": {"south": {"dest_id": "astral_passage_45", "alias": "s"}}
    }

    rooms["astral_void_apex"] = {
        "name": "The Astral Dais of Inquisitor Val'keth",
        "desc": "A throne carved from the solidified psychic skull of an elder brain. Lord Val'keth commands the astral fleet from this supreme elevation, surrounded by red dragon guards.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "astral_passage_54", "alias": "s"}},
        "npcs": [{"name": "Vlaakith's Inquisitor-General Val'keth", "desc": "A seven-foot githyanki warmaster clad in midnight-black astral plate. In his hands rests a silver greatsword that crackles with soul-rending psionic energy.", "level": 27, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Githyanki Silver Greatsword of Astral Severance", "desc": "A legendary two-handed greatsword capable of cleaving both physical armor and astral silver cords."},
            {"name": "Crown of the Dead God", "desc": "An ancient circlet carved from divine petrified bone, radiating absolute psionic mastery."}
        ]
    }

    # 54 Astral halls, psychic rifts, and silver corridors to reach 60 rooms
    for i in range(1, 55):
        r_key = f"astral_passage_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Weightless corridors of shimmering mother-of-pearl stone adrift in the silver void. "
            f"Sensations of time and gravity are mere suggestions here. [Astral Sector #{i}]"
        )
        r_name = f"Astral Void Gallery #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"astral_passage_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"astral_passage_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"astral_passage_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"astral_passage_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "dead_god_ribcage_hall", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "tu_narath_barracks", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "inquisitor_judgment_hall", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "dreadnought_silver_eye", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "astral_void_apex", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Astral Void Drake", "desc": "A sleek silver-scaled reptile that hunts on the ethereal currents.", "level": 21, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Githyanki Gish Spellblade", "desc": "A battlemage weaving force magic and swordplay with lethal grace.", "level": 22, "role": "mage"})

        if i == 22:
            items.append({"name": "Flask of Condensed Astral Ether", "desc": "A shimmering potion that restores mana and clears mind-affecting hexes."})

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
        "base_coords": (120, -50, 100),
        "rooms": rooms
    }


# =============================================================================
# ZONE 43: THE SUNKEN CITY OF OMU & FANE OF THE NIGHT SERPENT [Level 16-24, 60 Rooms]
# =============================================================================

def build_zone_fane_night_serpent():
    zone_key = "fane_night_serpent"
    zone_name = "The Sunken City of Omu & Fane of the Night Serpent"
    rooms = {}

    rooms["omu_ruined_gateway"] = {
        "name": "The Sunken Gateway of Ancient Omu",
        "desc": "A crumbling sandstone gateway choked with trailing jungle vines and swamp water. Bas-reliefs of coiled vipers and hooded cobras stare down with unblinking ruby eyes.",
        "terrain": "swamp",
        "exits": {"north": {"dest_id": "serpent_sacrificial_pit", "alias": "n"}},
        "npcs": [{"name": "Yuan-ti Pureblood Scout", "desc": "A slender jungle infiltrator with scaly skin and slit pupils, holding a poisoned recurve bow.", "level": 16, "role": "rogue"}]
    }

    rooms["serpent_sacrificial_pit"] = {
        "name": "The Sacrificial Pit of the Green Viper",
        "desc": "A flooded limestone pit writhing with thousands of venomous water moccasins and pit vipers. Stone altars stained with ancient sacrifices overlook the pit.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "omu_ruined_gateway", "alias": "s"}, "north": {"dest_id": "fane_corridor_01", "alias": "n"}, "east": {"dest_id": "yuan_ti_malison_brood", "alias": "e"}}
    }

    rooms["yuan_ti_malison_brood"] = {
        "name": "The Brood Chambers of the Malisons",
        "desc": "Warm, humid caverns where giant leathery serpent eggs rest in beds of decomposing jungle rot. Serpent-bodied warriors stand guard with curved scimitars.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "serpent_sacrificial_pit", "alias": "w"}, "north": {"dest_id": "fane_corridor_15", "alias": "n"}},
        "npcs": [{"name": "Yuan-ti Malison Abomination", "desc": "A horrifying monstrosity with the muscular torso of a human and the head and coiling tail of a king cobra.", "level": 19, "role": "warrior"}],
        "items": [{"name": "Phial of Concentrated Wyrm Venom", "desc": "A deadly toxin that coats piercing weapons with paralytic venom."}]
    }

    rooms["fane_blood_fountain"] = {
        "name": "The Blood Fountain of Dendar",
        "desc": "A massive marble fountain where enchanted scarlet water flows endlessly from the fangs of a colossal basalt serpent statue.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "fane_corridor_30", "alias": "s"}},
        "npcs": [{"name": "Serpent Priestess of the Night", "desc": "A hooded cleric chanting unholy litanies to the world-devouring serpent.", "level": 21, "role": "cleric"}],
        "items": [{"name": "Golden Serpent Idol of Omu", "desc": "A heavy golden idol decorated with polished emeralds."}]
    }

    rooms["altar_of_dendar"] = {
        "name": "The Shrine of the World-Eater",
        "desc": "A somber subterranean temple illuminated by green phosphor braziers. Murals depict the gigantic night serpent swallowing the sun and plunging creation into darkness.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "fane_corridor_45", "alias": "s"}}
    }

    rooms["hierophant_sanctum_chamber"] = {
        "name": "The Throne Room of Ras Nsi",
        "desc": "The throne hall of the undead warlord and yuan-ti supreme leader. Ras Nsi reclines upon a serpentine couch of carved ebony, surrounded by his royal bodyguards.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "fane_corridor_54", "alias": "s"}},
        "npcs": [{"name": "Ras Nsi the Yuan-ti High Hierophant", "desc": "An ancient necromancer and warlord whose lower body has been transformed into a massive serpent. His eyes glow with cold malice as he draws his flaming blade.", "level": 24, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Flame Tongue Scimitar of Ras Nsi", "desc": "A fearsome curved scimitar that bursts into bright orange flames upon drawing."},
            {"name": "Serpent Eye Amulet of Poison Mastery", "desc": "A jade amulet granting complete immunity to all known poisons and venoms."}]
    }

    # 54 Fane chambers, flooded tunnels, and snake dens to reach 60 rooms
    for i in range(1, 55):
        r_key = f"fane_corridor_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Ancient Chultan stonework covered in thick emerald moss and damp jungle mildew. "
            f"The sound of slithering scales echoes from dark cracks. [Fane Sector #{i}]"
        )
        r_name = f"Fane Serpent Corridor #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"fane_corridor_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"fane_corridor_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"fane_corridor_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"fane_corridor_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "serpent_sacrificial_pit", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "yuan_ti_malison_brood", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "fane_blood_fountain", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "altar_of_dendar", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "hierophant_sanctum_chamber", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Giant Constrictor Python", "desc": "A twenty-foot spotted python coiled in wait above the archway.", "level": 17, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Yuan-ti Mind Whisperer", "desc": "A cunning serpent caster invoking mass suggestion and terror.", "level": 18, "role": "mage"})

        if i == 25:
            items.append({"name": "Flagon of Fermented Jungle Palm Wine", "desc": "Sweet, potent Chultan wine brewed from tropical palm sap."})

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
        "base_coords": (-60, 80, -25),
        "rooms": rooms
    }


# =============================================================================
# ZONE 44: THE FROZEN GLACIER SPIRE OF SVARDBORG [Level 16-25, 60 Rooms]
# =============================================================================

def build_zone_svardborg_glacier():
    zone_key = "svardborg_glacier"
    zone_name = "The Frozen Glacier Spire of Svardborg"
    rooms = {}

    rooms["svardborg_glacier_pier"] = {
        "name": "The Frozen Pier of Svardborg Glacier",
        "desc": "A jagged dock of solid blue permafrost jutting into an icy arctic sound choked with grinding icebergs. Heavy mooring bollards carved of mammoth tusks stand rimed in frost.",
        "terrain": "ice",
        "exits": {"north": {"dest_id": "glacier_ice_chasm_gates", "alias": "n"}},
        "npcs": [{"name": "Frost Giant Harpooner", "desc": "A fourteen-foot giant with skin like pale glacial ice, holding an iron whale harpoon.", "level": 17, "role": "warrior"}]
    }

    rooms["glacier_ice_chasm_gates"] = {
        "name": "The Chasm Gates of Svardborg",
        "desc": "Two sheer glacier walls flank a narrow, treacherous defile of hard-packed snow. The howling arctic wind carries the scent of roasting whale blubber and woodsmoke.",
        "terrain": "mountain",
        "exits": {"south": {"dest_id": "svardborg_glacier_pier", "alias": "s"}, "north": {"dest_id": "glacier_pass_01", "alias": "n"}, "east": {"dest_id": "dire_wolf_kennels", "alias": "e"}}
    }

    rooms["dire_wolf_kennels"] = {
        "name": "The Kennels of the Winter Wolves",
        "desc": "Caverns carved into the glacier ice where massive white-furred dire wolves and winter wolves gnaw on frozen seal carcasses.",
        "terrain": "ice",
        "exits": {"west": {"dest_id": "glacier_ice_chasm_gates", "alias": "w"}, "north": {"dest_id": "glacier_pass_15", "alias": "n"}},
        "npcs": [{"name": "Alpha Winter Wolf", "desc": "A monstrous canine with intelligence in its pale blue eyes, exhaling clouds of freezing frost.", "level": 18, "role": "warrior"}],
        "items": [{"name": "Pelt of the White Winter Wolf", "desc": "A thick, luxurious wolf pelt that insulates completely against freezing blizzards."}]
    }

    rooms["frozen_mammoth_stables"] = {
        "name": "The Stables of the War Mammoths",
        "desc": "Colossal stalls hewn from the glacier wall. Enormous woolly mammoths clad in spiked iron barding stamp their massive feet in the snow.",
        "terrain": "ice",
        "exits": {"south": {"dest_id": "glacier_pass_30", "alias": "s"}},
        "npcs": [{"name": "Frost Giant Mammoth Keeper", "desc": "A giant in thick walrus-hide armor carrying an iron prod and frost club.", "level": 21, "role": "warrior"}],
        "items": [{"name": "Mammoth Ivory War Horn", "desc": "A massive carved tusk horn that echoes with the roaring fury of an avalanche."}]
    }

    rooms["frost_giant_great_longhouse"] = {
        "name": "The Great Timber Longhouse of Jarl Storvald",
        "desc": "Built from the timber hulls of dozens of wrecked merchant cogs, this titanic lodge features a central fire pit the size of a tavern roaring with burning driftwood.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "glacier_pass_45", "alias": "s"}}
    }

    rooms["jarl_storvald_ice_throne"] = {
        "name": "The Permafrost Throne of Jarl Storvald",
        "desc": "A monumental high seat carved from a single iceberg of unbreakable true-ice. Jarl Storvald presides over the frost giant tribes, his greataxe resting against his knee.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "glacier_pass_54", "alias": "s"}},
        "npcs": [{"name": "Jarl Storvald the Frost Giant King", "desc": "A titanic frost giant chieftain crowned in silver walrus tusks and clad in rune-inscribed white iron armor. His cold blue eyes promise merciless winter.", "level": 25, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Greataxe of Permafrost", "desc": "A colossal two-handed battleaxe forged of rimed steel that freezes mortal flesh solid upon contact."},
            {"name": "Horn of the Blinding Blizzard", "desc": "A legendary horn capable of summoning a howling arctic blizzard that blinds all foes."}
        ]
    }

    # 54 Glacier tunnels, ice ridges, and snow hollows to reach 60 rooms
    for i in range(1, 55):
        r_key = f"glacier_pass_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Vast blue ice tunnels carved deep inside the Svardborg ice shelf. "
            f"Icicles as large as lances hang from the frozen vaulted ceiling. [Glacier Sector #{i}]"
        )
        r_name = f"Glacier Ice Tunnel #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"glacier_pass_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"glacier_pass_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"glacier_pass_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"glacier_pass_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "glacier_ice_chasm_gates", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "dire_wolf_kennels", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "frozen_mammoth_stables", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "frost_giant_great_longhouse", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "jarl_storvald_ice_throne", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Glacial Ice Troll", "desc": "A translucent blue troll whose severed limbs reform from freezing ice shards.", "level": 18, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Frost Giant Skald", "desc": "A giant bard chanting ancient sagas of the Thousand Year War.", "level": 20, "role": "mage"})

        if i == 20:
            items.append({"name": "Cask of Strong Nord Dwarf Ale", "desc": "Hardy frozen ale that must be chipped with a dagger before drinking."})

        rooms[r_key] = {
            "name": r_name,
            "desc": desc,
            "terrain": "ice",
            "exits": exits,
            "npcs": npcs,
            "items": items
        }

    return {
        "zone_key": zone_key,
        "zone_name": zone_name,
        "default_terrain": "ice",
        "base_coords": (-80, -90, 40),
        "rooms": rooms
    }


# =============================================================================
# ZONE 45: THE CURSED SHADOWFELL NECROPOLIS OF MOIL [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_shadowfell_moil():
    zone_key = "shadowfell_moil"
    zone_name = "The Cursed Shadowfell Necropolis of Moil"
    rooms = {}

    rooms["moil_chain_bridge_entry"] = {
        "name": "The Chained Span of Moil",
        "desc": "A monumental bridge of rusted iron chains suspended over the infinite necrotic void of the Shadowfell. In the distance rise the inverted obsidian spires of the city that faces sundering.",
        "terrain": "catacombs",
        "exits": {"north": {"dest_id": "black_ice_colonnade", "alias": "n"}},
        "npcs": [{"name": "Shadowfell Void Stalker", "desc": "A spectral entity composed of pure shadow and cold malice.", "level": 22, "role": "rogue"}]
    }

    rooms["black_ice_colonnade"] = {
        "name": "The Colonnade of Black Ice",
        "desc": "Pillars of supernatural black ice support crumbling vaults. The air is so frigid that it drains the warmth from living blood and extinguishes all natural torches.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "moil_chain_bridge_entry", "alias": "s"}, "north": {"dest_id": "moil_spire_bridge_01", "alias": "n"}, "east": {"dest_id": "spire_of_sundered_skies", "alias": "e"}}
    }

    rooms["spire_of_sundered_skies"] = {
        "name": "The Spire of Sundered Skies",
        "desc": "A hollow obsidian tower extending downward into the void. Spectral bridges criss-cross between open balconies where vampire spawn and necromantic liches congregate.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "black_ice_colonnade", "alias": "w"}, "north": {"dest_id": "moil_spire_bridge_15", "alias": "n"}},
        "npcs": [{"name": "Moilian Vampire Lord", "desc": "An aristocratic undead aristocrat clad in dusty velvet robes, with long needle-sharp fangs.", "level": 24, "role": "warrior"}],
        "items": [{"name": "Ring of the Shadowfell Shroud", "desc": "A platinum ring set with a star sapphire that conceals the wearer from undead detection."}]
    }

    rooms["void_wraith_hollow"] = {
        "name": "The Hollow of Mourning Wraiths",
        "desc": "A sunken plaza where the wailing cries of damned Moilian souls echo eternally. Shadows writhe against the black ice walls with lifelike sentience.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "moil_spire_bridge_30", "alias": "s"}},
        "npcs": [{"name": "Dread Wraith of Moil", "desc": "A swirling cyclone of black mist and screaming spectral faces.", "level": 25, "role": "mage"}],
        "items": [{"name": "Soul-Vial of Preserved Life-Force", "desc": "A glowing crystal vial containing stolen vitality that can restore dying mortals to full health."}]
    }

    rooms["hall_of_weeping_vestiges"] = {
        "name": "The Chamber of Sundered Vestiges",
        "desc": "Ancient alcoves containing the sealed sarcophagi of forgotten dark gods and primordial vestiges. The stones weep dark, unholy tears.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "moil_spire_bridge_45", "alias": "s"}}
    }

    rooms["throne_of_the_void_sovereign"] = {
        "name": "The Obsidian Throne of Malchor the Sovereign",
        "desc": "The supreme throne hall of the City of Moil. Suspended directly over the roaring heart of the Shadowfell void, a throne of jagged black ice floats in perpetual levitation.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "moil_spire_bridge_54", "alias": "s"}},
        "npcs": [{"name": "Malchor the Sovereign of Moil", "desc": "A terrifying arch-lich sovereign clad in robes of woven void matter, crowned in black ice, wielding a scythe that siphons the life from entire realms.", "level": 29, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Black Ice Scythe of Moil", "desc": "A mythic scythe crafted from unbreakable Moilian black ice that inflicts catastrophic necrotic and cold damage."},
            {"name": "Vestige of the Sundered Void", "desc": "A sphere of captured void-light that absorbs incoming hostile spells and curses."}
        ]
    }

    # 54 Suspended bridges, obsidian chambers, and void corridors to reach 60 rooms
    for i in range(1, 55):
        r_key = f"moil_spire_bridge_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"A dizzying bridge of black stone suspended by colossal iron chains over the dark abyss. "
            f"The silence of the grave weighs heavy upon mortal souls. [Moil Spire Sector #{i}]"
        )
        r_name = f"Moil Suspended Bridge #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"moil_spire_bridge_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"moil_spire_bridge_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"moil_spire_bridge_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"moil_spire_bridge_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "black_ice_colonnade", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "spire_of_sundered_skies", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "void_wraith_hollow", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "hall_of_weeping_vestiges", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "throne_of_the_void_sovereign", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Moilian Crypt Wight", "desc": "A frozen corpse with glowing crimson pinpoints for eyes, carrying a notched broadsword.", "level": 23, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Shadowfell Necromancer", "desc": "A dark cultist in tattered black silks weaving forbidden curses.", "level": 24, "role": "mage"})

        if i == 18:
            items.append({"name": "Shard of Moilian Black Ice", "desc": "A sharp sliver of eternal black ice that never melts."})

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
        "base_coords": (-100, 30, -50),
        "rooms": rooms
    }


# =============================================================================
# MARITIME ROUTE HELPER
# =============================================================================

def register_icebreaker_ferry_routes():
    """Ensures The Frost-Cutter Icebreaker 'Winter's Fang' is registered in sailing.FERRY_ROUTES."""
    if "icebreaker_ship" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["icebreaker_ship"] = {
            "key": "icebreaker_ship",
            "name": 'The Frost-Cutter Icebreaker "Winter\'s Fang"',
            "operator": "First Mate Torvald",
            "operator_title": "Glacial Navigator of the Frozen Seas",
            "ports": ["south_docks", "dead_mans_cove", "svardborg_glacier_pier", "glacier_pier"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "dead_mans_cove": "Dead Man's Cove (Smuggler's Coast)",
                "svardborg_glacier_pier": "The Frozen Pier of Svardborg Glacier",
                "glacier_pier": "The Frozen Pier of Svardborg Glacier"
            },
            "fares": {
                ("south_docks", "svardborg_glacier_pier"): 85,
                ("svardborg_glacier_pier", "south_docks"): 85,
                ("dead_mans_cove", "svardborg_glacier_pier"): 65,
                ("svardborg_glacier_pier", "dead_mans_cove"): 65,
                ("south_docks", "glacier_pier"): 85,
                ("glacier_pier", "south_docks"): 85,
                ("dead_mans_cove", "glacier_pier"): 65,
                ("glacier_pier", "dead_mans_cove"): 65
            },
            "desc": "A heavy iron-reinforced cog fitted with an armored reinforced ram capable of sundering towering pack ice in arctic waters.",
            "deck_key": "icebreaker_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 11
# =============================================================================

def run_bulk_ingestion_part11(clean_existing=False):
    """
    Executes Part 11 of the bulk world expansion ("2,300+ Rooms Milestone"):
    - The Astral Dreadnought & Githyanki Sky-Citadel (60 rooms)
    - The Sunken City of Omu & Fane of the Night Serpent (60 rooms)
    - The Frozen Glacier Spire of Svardborg (60 rooms)
    - The Cursed Shadowfell Necropolis of Moil (60 rooms)
    Plus The Frost-Cutter Icebreaker 'Winter's Fang' weather deck (1 room).
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
        build_zone_astral_dreadnought,
        build_zone_fane_night_serpent,
        build_zone_svardborg_glacier,
        build_zone_shadowfell_moil
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("astral_dreadnought", "astral_silver_wharf", "summit", "step into astral silver void", "return through astral portal to summit"),
        ("fane_night_serpent", "omu_ruined_gateway", "marshland", "descend into sunken serpent fane", "surface from serpent fane to sunken mire"),
        ("svardborg_glacier", "svardborg_glacier_pier", "watchtower", "ascend frozen glacial crest to svardborg", "descend glacier to ruined watchtower"),
        ("shadowfell_moil", "moil_chain_bridge_entry", "ossuary", "cross chained void bridge into moil", "return across void bridge to sunken ossuary")
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

    # 4. Register Winter's Fang Icebreaker Ferry Route & Weather Deck
    icebreaker_deck = find_room_by_key("icebreaker_deck")
    if not icebreaker_deck:
        icebreaker_deck = create_object(Room, key='The Frost-Cutter Icebreaker "Winter\'s Fang" - Weather Deck', tags=[TAG_WORLD])
        icebreaker_deck.tags.add("icebreaker_deck", category="room_key")
        icebreaker_deck.tags.add("svardborg_glacier", category="zone")
        icebreaker_deck.db.room_key = "icebreaker_deck"
        icebreaker_deck.db.desc = (
            "You stand upon the iron-plated timber deck of the icebreaker. "
            "Rime and thick sea salt crust the railings, while an armored ram crushes through "
            "towering ice floes on the freezing polar voyage."
        )
        icebreaker_deck.db.zone = "Arctic Seas"
        icebreaker_deck.db.terrain = "water_swim"
        icebreaker_deck.db.coords = (-80, -90, 40)
        report["rooms_created"] += 1

    register_icebreaker_ferry_routes()
    report["ferry_routes_added"].append('The Frost-Cutter Icebreaker "Winter\'s Fang" (south_docks <-> dead_mans_cove <-> svardborg_glacier_pier)')

    return report

