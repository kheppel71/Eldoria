"""
Bulk World Ingestion Engine — Part 12: The "2,500+ Rooms Milestone" Quarter-Myriad Expansion

Expands Eldoria beyond 2,500 rooms with 241 rooms across 4 legendary realms:
1. The Drow Metropolis of Menzoberranzan [Level 16-25 Underdark, 60 Rooms]
2. The Floating Cloud Castle of Skyreach [Level 18-26 High Altitude, 60 Rooms]
3. The Sunken Elven Ruins of Myth Drannor [Level 15-24 Ancient Magic, 60 Rooms]
4. The Nine Hells — City of Dis & The Iron Tower [Level 22-30 Endgame Infernal, 60 Rooms]

Total Rooms Created in Part 12: 241 Rooms (including 'Nightfall' Skyship weather deck)
Cumulative World Total: 2,313 + 241 = 2,554 Rooms!

Features:
- New 'The Shadow-Weave Skyship Nightfall' aerial transit route in sailing.py
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
# ZONE 46: THE DROW METROPOLIS OF MENZOBERRANZAN [Level 16-25, 60 Rooms]
# =============================================================================

def build_zone_menzoberranzan():
    zone_key = "menzoberranzan"
    zone_name = "The Drow Metropolis of Menzoberranzan"
    rooms = {}

    rooms["menzo_tier_breche_gates"] = {
        "name": "The Warded Gates of Tier Breche",
        "desc": "A vast cavern ramp guarded by sculpted spider stone gates and glowing amethyst faerie fire. Beyond, the great subterranean stalactite city of the dark elves spreads out in the darkness.",
        "terrain": "underground",
        "exits": {"north": {"dest_id": "arach_tinilith_academy", "alias": "n"}},
        "npcs": [{"name": "Drow Elite Guard", "desc": "A slender dark elf clad in silent piwafwi cloak and blackened chainmail, holding a hand crossbow loaded with sleep poison.", "level": 17, "role": "warrior"}]
    }

    rooms["arach_tinilith_academy"] = {
        "name": "The High Academy of Arach-Tinilith",
        "desc": "A grand cavern temple carved in the likeness of a colossal obsidian spider. Novice priestesses chant dark devotionals to Lolth amid webs of sticky spun shadow.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "menzo_tier_breche_gates", "alias": "s"}, "north": {"dest_id": "menzo_avenue_01", "alias": "n"}, "east": {"dest_id": "house_baenre_compound", "alias": "e"}}
    }

    rooms["house_baenre_compound"] = {
        "name": "The Grand Compound of House Baenre",
        "desc": "The ancestral fortress of the First House of Menzoberranzan. Towering dome-shaped stalagmites carved into opulent palaces are protected by pulsating magical barriers.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "arach_tinilith_academy", "alias": "w"}, "north": {"dest_id": "menzo_avenue_15", "alias": "n"}},
        "npcs": [{"name": "Baenre Spellwarrior Champion", "desc": "An elite drow swordmaster whose twin scimitars glow with lethal dark venom.", "level": 22, "role": "warrior"}],
        "items": [{"name": "Piwafwi Cloak of the Dark Elves", "desc": "A magical spider-silk cloak that renders the wearer virtually invisible in subterranean gloom."}]
    }

    rooms["narbondel_heat_pillar"] = {
        "name": "The Great Pillar of Narbondel",
        "desc": "A colossal natural stone pillar that serves as the city's clock. The Archmage of Menzoberranzan enchants it daily with a band of rising thermal heat.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "menzo_avenue_30", "alias": "s"}},
        "npcs": [{"name": "Drow Archmage Adept", "desc": "A robed drow sorcerer studying the thermal currents of the pillar.", "level": 21, "role": "mage"}],
        "items": [{"name": "Wand of Faerie Fire Illumination", "desc": "A slender silver wand that outlines hidden enemies in glowing violet light."}]
    }

    rooms["donigarten_fungal_shores"] = {
        "name": "The Fungal Shores of Lake Donigarten",
        "desc": "The food basin of the city. Stinking moss beds and giant phosphorescent fungi surround a subterranean lake where goblin and orc slaves tend rothe herds.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "menzo_avenue_45", "alias": "s"}}
    }

    rooms["quenthel_baenre_throne"] = {
        "name": "The Throne Room of Matron Mother Quenthel",
        "desc": "The inner sanctum of the supreme ruler of Menzoberranzan. A throne of woven living spiders elevates the Matron Mother beneath statues of the Demon Queen of Spiders.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "menzo_avenue_54", "alias": "s"}},
        "npcs": [{"name": "Matron Mother Quenthel Baenre", "desc": "The supreme Matron Mother of House Baenre and High Priestess of Lolth. In her hand is a five-headed viper scourge that strikes with paralyzing fury.", "level": 26, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Scourge of the Spider Queen", "desc": "A fearsome five-headed scourge of living serpents that injects deadly necrotic venom."},
            {"name": "Insignia of House Baenre", "desc": "A noble insignia granting levitation and command over lesser underdark beings."}
        ]
    }

    # 54 Avenues, stalagmite alleys, and fungal passages to reach 60 rooms
    for i in range(1, 55):
        r_key = f"menzo_avenue_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Carved obsidian avenues illuminated by eerie patches of blue and violet faerie fire. "
            f"Drow patrols move silently across the dark flagstones. [Menzoberranzan Sector #{i}]"
        )
        r_name = f"Menzoberranzan Dark Avenue #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"menzo_avenue_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"menzo_avenue_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"menzo_avenue_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"menzo_avenue_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "arach_tinilith_academy", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "house_baenre_compound", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "narbondel_heat_pillar", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "donigarten_fungal_shores", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "quenthel_baenre_throne", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Cave Drider Hunter", "desc": "A terrifying centauric monstrosity with the body of a giant spider and the torso of a drow warrior.", "level": 19, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Lolth Inquisitrix Priestess", "desc": "A fanatical priestess wielding a mace shaped like a coiled arachnid.", "level": 20, "role": "cleric"})

        if i == 19:
            items.append({"name": "Flask of Deep-Mushroom Wine", "desc": "A sweet, heady wine brewed from bioluminescent underdark fungi."})

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
        "base_coords": (-120, -70, -60),
        "rooms": rooms
    }


# =============================================================================
# ZONE 47: THE FLOATING CLOUD CASTLE OF SKYREACH [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_skyreach_castle():
    zone_key = "skyreach_castle"
    zone_name = "The Floating Cloud Castle of Skyreach"
    rooms = {}

    rooms["skyreach_castle_cloud_gate"] = {
        "name": "The Floating Cloud Dock of Skyreach Castle",
        "desc": "A breathtaking open-air dock carved of solidified cloudstone and shimmering glacier ice, hovering thousands of feet above the jagged mountain peaks.",
        "terrain": "air",
        "exits": {"north": {"dest_id": "cloud_giant_great_hall", "alias": "n"}},
        "npcs": [{"name": "Cloud Castle Sky-Guard", "desc": "A towering cloud giant clad in white linen and silver cuirass, holding a giant morningstar.", "level": 19, "role": "warrior"}]
    }

    rooms["cloud_giant_great_hall"] = {
        "name": "The Great Vaulted Hall of Skyreach",
        "desc": "Monumental fifty-foot high arches of carved white marble open to the boundless blue sky. Fine mist swirls around giant-sized furniture and tapestries.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "skyreach_castle_cloud_gate", "alias": "s"}, "north": {"dest_id": "skyreach_corridor_01", "alias": "n"}, "east": {"dest_id": "white_dragon_glazhael_cavern", "alias": "e"}}
    }

    rooms["white_dragon_glazhael_cavern"] = {
        "name": "The Glacial Vault of Glazhael the Cloudchaser",
        "desc": "A vast cavern within the true-ice foundation of the floating fortress. Walls of crystal frost house the frozen gold hoard of an ancient white dragon.",
        "terrain": "ice",
        "exits": {"west": {"dest_id": "cloud_giant_great_hall", "alias": "w"}, "north": {"dest_id": "skyreach_corridor_15", "alias": "n"}},
        "npcs": [{"name": "Glazhael the Cloudchaser", "desc": "A terrifying adult white dragon with jagged horns of ice and a breath weapon of pure arctic death.", "level": 23, "role": "warrior"}],
        "items": [{"name": "Frost-Wreathed White Dragon Scale", "desc": "A thick dragon scale that confers resistance against cold and ice magic."}]
    }

    rooms["vampire_guest_sanctum"] = {
        "name": "The Shrouded Crypt of the Vampire Guest",
        "desc": "A darkened chamber protected by heavy velvet drapes where aristocratic vampire emissaries rest during daylight hours in silk-lined sarcophagi.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "skyreach_corridor_30", "alias": "s"}},
        "npcs": [{"name": "Lord Sandesyl the Vampire Noble", "desc": "An undead sorcerer clad in crimson velvet whose red eyes hypnotize all mortals.", "level": 22, "role": "mage"}],
        "items": [{"name": "Ring of Cloud Mist Levitation", "desc": "A ring that allows the wearer to drift gently down from great heights like a feather."}]
    }

    rooms["control_tower_steering_orb"] = {
        "name": "The Steering Chamber of the Esoteric Orb",
        "desc": "The highest pinnacle of Skyreach Castle. In the center floats a glowing sphere of churning storm clouds and lightning used to pilot the floating citadel across the sky.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "skyreach_corridor_45", "alias": "s"}}
    }

    rooms["blagothkus_throne_hall"] = {
        "name": "The Cloudstone Throne of Count Blagothkus",
        "desc": "The grand audience chamber of Count Blagothkus. Columns of solid ice support a vaulted dome through which sunlight streams in dazzling prismatic refractions.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "skyreach_corridor_54", "alias": "s"}},
        "npcs": [{"name": "Blagothkus the Cloud Giant Count", "desc": "An imposing eighteen-foot cloud giant noble with sky-blue skin and braided platinum hair, wielding a massive spiked morningstar of thunder.", "level": 25, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Morningstar of the Cloud Giant", "desc": "A titanic morningstar that deals thunderous cleaving damage on every blow."},
            {"name": "Control Orb of Skyreach Castle", "desc": "A miniature orb of churning clouds that commands winds and floating citadels."}
        ]
    }

    # 54 Corridors, balconies, and ice battlements to reach 60 rooms
    for i in range(1, 55):
        r_key = f"skyreach_corridor_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Vast open-air walkways carved of pale cloudstone and permanent ice. "
            f"Winds buffet the railings, revealing dizzying views of the world far below. [Skyreach Sector #{i}]"
        )
        r_name = f"Skyreach Cloud Walkway #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"skyreach_corridor_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"skyreach_corridor_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"skyreach_corridor_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"skyreach_corridor_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "cloud_giant_great_hall", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "white_dragon_glazhael_cavern", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "vampire_guest_sanctum", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "control_tower_steering_orb", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "blagothkus_throne_hall", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Skyreach Air Elemental", "desc": "A whistling vortex of living wind and gale-force currents.", "level": 19, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Ogre Sky-Mercenary", "desc": "A hulking brute in thick winter furs carrying an iron-shod war club.", "level": 18, "role": "warrior"})

        if i == 25:
            items.append({"name": "Flagon of Giant Spiced Cloud-Wine", "desc": "Heady wine that makes the drinker feel as light as air."})

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
        "base_coords": (150, 40, 120),
        "rooms": rooms
    }


# =============================================================================
# ZONE 48: THE SUNKEN ELVEN RUINS OF MYTH DRANNOR [Level 15-24, 60 Rooms]
# =============================================================================

def build_zone_myth_drannor():
    zone_key = "myth_drannor"
    zone_name = "The Sunken Elven Ruins of Myth Drannor"
    rooms = {}

    rooms["myth_drannor_ancient_mythal_gate"] = {
        "name": "The Shattered Mythal Gate of Myth Drannor",
        "desc": "A monumental archway of weeping white marble entwined with ancient ironwood roots. Wisps of cracked, unstable elven high magic crackle softly around the perimeter.",
        "terrain": "forest",
        "exits": {"north": {"dest_id": "speculum_of_divination", "alias": "n"}},
        "npcs": [{"name": "Corrupted Mythal Treant", "desc": "A colossal oak guardian infected by wild planar magic, branches thrashing in grief.", "level": 16, "role": "warrior"}]
    }

    rooms["speculum_of_divination"] = {
        "name": "The Speculum of Elven Divination",
        "desc": "A circular pavilion surrounding a flawless pool of liquid silver. Ancient reflections of the City of Song shimmer across the water's surface.",
        "terrain": "forest",
        "exits": {"south": {"dest_id": "myth_drannor_ancient_mythal_gate", "alias": "s"}, "north": {"dest_id": "mythal_grove_01", "alias": "n"}, "east": {"dest_id": "coronal_high_palace", "alias": "e"}}
    }

    rooms["coronal_high_palace"] = {
        "name": "The High Palace of the Coronal",
        "desc": "Once the seat of the Elven Emperors, now overgrown with phosphorescent briars and silver ferns. Broken marble thrones sit beneath shattered glass domes.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "speculum_of_divination", "alias": "w"}, "north": {"dest_id": "mythal_grove_15", "alias": "n"}},
        "npcs": [{"name": "Elven Baelnorn Guardian", "desc": "An ancient undead elven archmage in golden funerary robes, bound to guard the realm forever.", "level": 21, "role": "mage"}],
        "items": [{"name": "Shard of the Shattered Mythal", "desc": "A fragment of crystallized elven magic that pulses with restorative healing aura."}]
    }

    rooms["baelnorn_guardian_vault"] = {
        "name": "The Crypt of the Moonblade Weavers",
        "desc": "A solemn underground vault lined with ancestral elven sarcophagi. Spectral swords float horizontally in mid-air above each grave.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "mythal_grove_30", "alias": "s"}},
        "npcs": [{"name": "Spectral Bladesinger Shade", "desc": "A ghost executing intricate sword katas with blinding elven speed.", "level": 22, "role": "warrior"}],
        "items": [{"name": "Moonblade of the Coronal", "desc": "A legendary elven longsword that glows with pale silver moonlight, attuned to royal elven blood."}]
    }

    rooms["phaerimm_subterranean_breach"] = {
        "name": "The Subterranean Breach of the Phaerimm",
        "desc": "A deep sinkhole where the magic-devouring horrors breached the subterranean foundations of the city. Magic drains away like water through a sieve.",
        "terrain": "underground",
        "exits": {"south": {"dest_id": "mythal_grove_45", "alias": "s"}}
    }

    rooms["despoiler_spire_sanctum"] = {
        "name": "The Spire of the Phaerimm Despoiler",
        "desc": "The lair of the ancient conical aberration responsible for the destruction of the elven empire. Leathery tentacles and glowing multi-faceted eyes hover in the magical vortex.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "mythal_grove_54", "alias": "s"}},
        "npcs": [{"name": "The Eldritch Phaerimm Despoiler", "desc": "A floating conical monstrosity with a maw of needle teeth, clutching multiple magical staves in its four powerful arms while weaving chaotic spells.", "level": 24, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Staff of Myth Drannor Mythal", "desc": "An ancient staff woven of weirwood and silver, commanding the remnant spells of the fallen empire."},
            {"name": "Ring of the Seldarine High Council", "desc": "An ancient ring granting profound resistance to mental enchantment and magical decay."}
        ]
    }

    # 54 Overgrown groves, crystal colonnades, and sunken arches to reach 60 rooms
    for i in range(1, 55):
        r_key = f"mythal_grove_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Ancient elven colonnades entwined with wild roses and towering oaks. "
            f"The air hums with residual harmonic vibrations from the broken mythal. [Myth Drannor Sector #{i}]"
        )
        r_name = f"Myth Drannor Overgrown Colonnade #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"mythal_grove_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"mythal_grove_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"mythal_grove_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"mythal_grove_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "speculum_of_divination", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "coronal_high_palace", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "baelnorn_guardian_vault", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "phaerimm_subterranean_breach", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "despoiler_spire_sanctum", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Wild Magic Will-o'-Wisp", "desc": "A bobbing orb of unstable arcane luminescence that shocks living flesh.", "level": 17, "role": "mage"})
        elif i % 10 == 0:
            npcs.append({"name": "Corrupted Elven Shadow Archer", "desc": "An undead marksman firing arrows that phase through physical shields.", "level": 18, "role": "rogue"})

        if i == 20:
            items.append({"name": "Flask of Ancient Elven Sun-Nectar", "desc": "Golden cordial that restores vigor and shields against necromancy."})

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
        "base_coords": (90, -110, -20),
        "rooms": rooms
    }


# =============================================================================
# ZONE 49: THE NINE HELLS — DIS & THE IRON TOWER [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_hells_dis():
    zone_key = "hells_dis_iron_tower"
    zone_name = "The Nine Hells — City of Dis & The Iron Tower"
    rooms = {}

    rooms["dis_iron_gate_of_chains"] = {
        "name": "The Scorched Iron Gate of Dis",
        "desc": "Monumental iron gates glowing red-hot from the perpetual hellfire beneath the Second Layer of Baator. Countless damned souls strain in chains along the parapets.",
        "terrain": "city",
        "exits": {"north": {"dest_id": "avenue_of_burning_slag", "alias": "n"}},
        "npcs": [{"name": "Barbed Devil Sentinel", "desc": "A muscular fiend covered in vicious serrated spikes, holding an iron flail.", "level": 22, "role": "warrior"}]
    }

    rooms["avenue_of_burning_slag"] = {
        "name": "The Avenue of Boiling Slag",
        "desc": "Streets paved with black iron cobblestones that radiate searing heat. Buildings of hammered iron twist upward into the sulfurous green smog of the sky.",
        "terrain": "city",
        "exits": {"south": {"dest_id": "dis_iron_gate_of_chains", "alias": "s"}, "north": {"dest_id": "dis_iron_street_01", "alias": "n"}, "east": {"dest_id": "erinyes_iron_spire_aerie", "alias": "e"}}
    }

    rooms["erinyes_iron_spire_aerie"] = {
        "name": "The Aerie of the Erinyes Executioners",
        "desc": "High iron perches where winged fiends sharpen poisoned composite bows and ropes of entanglement, surveying the city for unpermitted rebellion.",
        "terrain": "city",
        "exits": {"west": {"dest_id": "avenue_of_burning_slag", "alias": "w"}, "north": {"dest_id": "dis_iron_street_15", "alias": "n"}},
        "npcs": [{"name": "Erinyes Inquisitor", "desc": "A fierce winged devil in gleaming red armor wielding a fiery broadsword and rope of entrapment.", "level": 24, "role": "warrior"}],
        "items": [{"name": "Rope of Baatorian Entanglement", "desc": "A whip woven of red hell-iron that binds and burns trapped victims."}]
    }

    rooms["dispater_prison_dungeon"] = {
        "name": "The Vaults of Eternal Confinement",
        "desc": "Iron cells that shrink and expand unpredictably to torment their prisoners. Dispater's paranoid decrees are etched into every iron door.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "dis_iron_street_30", "alias": "s"}},
        "npcs": [{"name": "Chain Devil Warden", "desc": "A tormentor wrapped in animated spiked chains that obey its mental command.", "level": 25, "role": "warrior"}],
        "items": [{"name": "Chain of Infernal Torment", "desc": "A heavy barbed chain that strikes with supernatural hellfire."}]
    }

    rooms["great_hall_of_paranoia"] = {
        "name": "The Great Hall of Shifting Reflections",
        "desc": "Mirrors of polished brass and iron line the walls, reflecting a thousand paranoid projections of potential assassins and usurpers.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "dis_iron_street_45", "alias": "s"}}
    }

    rooms["dispater_iron_tower_apex"] = {
        "name": "The Throne of Archduke Dispater",
        "desc": "The apex of the Iron Tower, a structure that shifts its geometry at the Archduke's whim. Dispater sits upon a throne of impenetrable lead and iron, watching all layers of Baator.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "dis_iron_street_54", "alias": "s"}},
        "npcs": [{"name": "Archduke Dispater of the Iron Tower", "desc": "The supreme Lord of the Second Layer of Hell. A regal devil in iron-studded robes with horns of dark bronze, carrying a heavy iron rod of absolute authority.", "level": 29, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Iron Rod of Archduke Dispater", "desc": "A mythical scepter of solid Baatorian iron that paralyzes mortals and shatters incoming planar attacks."},
            {"name": "Signet Ring of the Nine Hells", "desc": "An ancient infernal signet ring granting mastery over fire and immunity to fear."}
        ]
    }

    # 54 Iron streets, foundries, and slag alleys to reach 60 rooms
    for i in range(1, 55):
        r_key = f"dis_iron_street_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Streets of glowing red-hot iron where sulfur smoke swirls in blinding drafts. "
            f"The sound of distant hammer blows upon iron anvils reverberates endlessly. [Dis Sector #{i}]"
        )
        r_name = f"City of Dis Iron Thoroughfare #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"dis_iron_street_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"dis_iron_street_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"dis_iron_street_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"dis_iron_street_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "avenue_of_burning_slag", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "erinyes_iron_spire_aerie", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "dispater_prison_dungeon", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "great_hall_of_paranoia", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "dispater_iron_tower_apex", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Spined Devil Scout", "desc": "A small winged imp firing flaming spines from its tail.", "level": 21, "role": "rogue"})
        elif i % 10 == 0:
            npcs.append({"name": "Bone Devil Taskmaster", "desc": "A terrifying skeletal devil with a scorpion stinger and bone club.", "level": 23, "role": "warrior"})

        if i == 21:
            items.append({"name": "Phial of Smoldering Hell-Tar", "desc": "Liquid unquenchable fire extracted from the foundries of Dis."})

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
        "base_coords": (-150, 60, -80),
        "rooms": rooms
    }


# =============================================================================
# MARITIME & AETHER ROUTE HELPER
# =============================================================================

def register_nightfall_ferry_routes():
    """Ensures The Shadow-Weave Skyship 'Nightfall' is registered in sailing.FERRY_ROUTES."""
    if "nightfall_skyship" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["nightfall_skyship"] = {
            "key": "nightfall_skyship",
            "name": 'The Shadow-Weave Skyship "Nightfall"',
            "operator": "Netherese Arcanist Kaelen",
            "operator_title": "Navigator of the Shadow-Weave Skies",
            "ports": ["south_docks", "praxis_province_praxis_harbor", "skyreach_castle_cloud_gate", "skyreach_gate"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
                "skyreach_castle_cloud_gate": "The Floating Cloud Dock of Skyreach Castle",
                "skyreach_gate": "The Floating Cloud Dock of Skyreach Castle"
            },
            "fares": {
                ("south_docks", "skyreach_castle_cloud_gate"): 105,
                ("skyreach_castle_cloud_gate", "south_docks"): 105,
                ("praxis_province_praxis_harbor", "skyreach_castle_cloud_gate"): 90,
                ("skyreach_castle_cloud_gate", "praxis_province_praxis_harbor"): 90,
                ("south_docks", "skyreach_gate"): 105,
                ("skyreach_gate", "south_docks"): 105,
                ("praxis_province_praxis_harbor", "skyreach_gate"): 90,
                ("skyreach_gate", "praxis_province_praxis_harbor"): 90
            },
            "desc": "An elegant skyship crafted of midnight shadow-silk sails, darkwood hull, and suspended gravity-defying Netherese mythallar crystals.",
            "deck_key": "nightfall_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 12
# =============================================================================

def run_bulk_ingestion_part12(clean_existing=False):
    """
    Executes Part 12 of the bulk world expansion ("2,500+ Rooms Milestone"):
    - The Drow Metropolis of Menzoberranzan (60 rooms)
    - The Floating Cloud Castle of Skyreach (60 rooms)
    - The Sunken Elven Ruins of Myth Drannor (60 rooms)
    - The Nine Hells — City of Dis & The Iron Tower (60 rooms)
    Plus The Shadow-Weave Skyship 'Nightfall' weather deck (1 room).
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
        build_zone_menzoberranzan,
        build_zone_skyreach_castle,
        build_zone_myth_drannor,
        build_zone_hells_dis
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("menzoberranzan", "menzo_tier_breche_gates", "rail_hub", "descend underdark rift to menzoberranzan", "ascend subterranean rift to rail hub"),
        ("skyreach_castle", "skyreach_castle_cloud_gate", "summit", "board floating cloud dock of skyreach", "descend cloud stairway to mountain summit"),
        ("myth_drannor", "myth_drannor_ancient_mythal_gate", "deep_woods", "pass through elven mythal portal", "return through mythal portal to deep woods"),
        ("hells_dis_iron_tower", "dis_iron_gate_of_chains", "bazaar", "step through infernal gate into dis", "escape burning iron city to sunken bazaar")
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

    # 4. Register Nightfall Skyship Ferry Route & Weather Deck
    nightfall_deck = find_room_by_key("nightfall_deck")
    if not nightfall_deck:
        nightfall_deck = create_object(Room, key='The Shadow-Weave Skyship "Nightfall" - Weather Deck', tags=[TAG_WORLD])
        nightfall_deck.tags.add("nightfall_deck", category="room_key")
        nightfall_deck.tags.add("skyreach_castle", category="zone")
        nightfall_deck.db.room_key = "nightfall_deck"
        nightfall_deck.db.desc = (
            "You stand upon the varnished darkwood deck of the Netherese skyship. "
            "Sails woven from shadowy dark matter billow without sound, while a floating mythallar "
            "core hums with ancient anti-gravitational enchantments."
        )
        nightfall_deck.db.zone = "Netherese Sky"
        nightfall_deck.db.terrain = "air"
        nightfall_deck.db.coords = (150, 40, 120)
        report["rooms_created"] += 1

    register_nightfall_ferry_routes()
    report["ferry_routes_added"].append('The Shadow-Weave Skyship "Nightfall" (south_docks <-> praxis_harbor <-> skyreach_cloud_gate)')

    return report

