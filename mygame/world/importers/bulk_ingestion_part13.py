"""
Bulk World Ingestion Engine — Part 13: The "2,800 Rooms Milestone" Expansion

Expands Eldoria to 2,795 rooms across 4 legendary adventure realms:
1. The Chasm of the Abyss & Royal Wood of Oolacile [Level 20-28 Dark Fantasy, 60 Rooms]
2. The Gnomish Clockwork Metropolis of Lantan [Level 12-20 Steampunk / Tech, 60 Rooms]
3. The Githzerai Floating Monasteries of Limbo [Level 18-26 Planar Chaos, 60 Rooms]
4. The Buried Netherese Necropolis of Ythryn [Level 22-30 Endgame Glacier Void, 60 Rooms]

Total Rooms Created in Part 13: 241 Rooms (including 'Iron Drake' Steam Ironclad weather deck)
Cumulative World Total: 2,554 + 241 = 2,795 Rooms!

Features:
- New 'The Steam-Paddle Ironclad Iron Drake' maritime steam transit route in sailing.py
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
# ZONE 50: THE CHASM OF THE ABYSS & ROYAL WOOD OF OOLACILE [Level 20-28, 60 Rooms]
# =============================================================================

def build_zone_abyss_oolacile():
    zone_key = "abyss_oolacile"
    zone_name = "The Chasm of the Abyss & Royal Wood of Oolacile"
    rooms = {}

    rooms["oolacile_sanctuary_garden_gate"] = {
        "name": "The Sanctuary Garden Gate of Oolacile",
        "desc": "A weathered stone archway flanked by overgrown white roses. Beyond lies the primeval forest of the Royal Wood, where the sky grows progressively darker as the abyss encroaches.",
        "terrain": "forest",
        "exits": {"north": {"dest_id": "royal_wood_stone_colosseum", "alias": "n"}},
        "npcs": [{"name": "Sanctuary Stone Guardian", "desc": "A massive moss-covered stone knight wielding a giant stone greathammer.", "level": 20, "role": "warrior"}]
    }

    rooms["royal_wood_stone_colosseum"] = {
        "name": "The Sunken Colosseum of Oolacile",
        "desc": "A crumbling amphitheater of carved gray granite. The ground is scarred with the claw marks of abyssal abominations.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "oolacile_sanctuary_garden_gate", "alias": "s"}, "north": {"dest_id": "abyss_chasm_path_01", "alias": "n"}, "east": {"dest_id": "bloathead_sorcerer_hollow", "alias": "e"}}
    }

    rooms["bloathead_sorcerer_hollow"] = {
        "name": "The Hollow of the Mutated Citizens",
        "desc": "A subterranean cavern where deformed sorcerers with swollen, bulbous heads covered in glowing red eyes mutter unintelligible abyssal incantations.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "royal_wood_stone_colosseum", "alias": "w"}, "north": {"dest_id": "abyss_chasm_path_15", "alias": "n"}},
        "npcs": [{"name": "Bloathead Dark Sorcerer", "desc": "A mutated scholar firing volleys of dark bead sorceries from an ebony catalyst.", "level": 22, "role": "mage"}],
        "items": [{"name": "Silver Pendant of Deflection", "desc": "An ancient pendant that emits a repelling silver pulse, deflecting dark sorceries."}]
    }

    rooms["chasm_of_the_abyss_descent"] = {
        "name": "The Descending Precipice of the Abyss",
        "desc": "The solid ground gives way to sheer slopes of pure solidified darkness. Physical footing defies gravity as travelers step onto the dark void.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "abyss_chasm_path_30", "alias": "s"}},
        "npcs": [{"name": "Giant Abyssal Humanity Phantom", "desc": "A floating wraith shaped like a humanoid black soul with two white pinpoint eyes.", "level": 23, "role": "rogue"}],
        "items": [{"name": "Clustered Humanity Sprite", "desc": "A warm, comforting black sprite that completely restores life and cleanses curses."}]
    }

    rooms["humanity_sprite_cavern"] = {
        "name": "The Cavern of Adrift Souls",
        "desc": "A silent realm within the deep abyss where countless drifting humanity spirits gather in gentle, hypnotic swarms.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "abyss_chasm_path_45", "alias": "s"}}
    }

    rooms["manus_father_of_abyss_lair"] = {
        "name": "The Primordial Bed of Manus",
        "desc": "The absolute bottom of the Abyss. A colossal cavern of pulsating darkness where the Primeval Man rests, glowing with primordial sorrow and fury.",
        "terrain": "catacombs",
        "exits": {"south": {"dest_id": "abyss_chasm_path_54", "alias": "s"}},
        "npcs": [{"name": "Manus, Father of the Abyss", "desc": "A titanic, hulking monstrosity with a colossal demonic arm, curling horns, and glowing red eyes across his torso. His roar shakes the foundations of reality.", "level": 28, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Soul of Manus, Father of the Abyss", "desc": "A dense soul of pure primeval dark magic that grants mastery over abyssal sorceries."},
            {"name": "Manus's Craggy Sorcery Catalyst", "desc": "A colossal club-catalyst carved of abyssal stone that scales with both strength and intellect."}
        ]
    }

    # 54 Chasm paths, dark slopes, and ruined township ruins to reach 60 rooms
    for i in range(1, 55):
        r_key = f"abyss_chasm_path_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Sloping ledges of ancient black stone descending deeper into the primeval abyss. "
            f"The whispers of the dark pull gently at mortal consciousness. [Abyss Sector #{i}]"
        )
        r_name = f"Chasm of the Abyss Descent #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"abyss_chasm_path_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"abyss_chasm_path_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"abyss_chasm_path_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"abyss_chasm_path_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "royal_wood_stone_colosseum", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "bloathead_sorcerer_hollow", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "chasm_of_the_abyss_descent", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "humanity_sprite_cavern", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "manus_father_of_abyss_lair", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Abyssal Bloathead Marauder", "desc": "A crazed mutated human wielding a serrated wooden spade.", "level": 21, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Dark Orb Apparition", "desc": "A swirling vortex of dark soul energy that lashes out with tendrils of darkness.", "level": 22, "role": "mage"})

        if i == 20:
            items.append({"name": "Phial of Purifying Green Moss", "desc": "Medicinal moss that completely cures toxic buildup and poison."})

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
        "base_coords": (-140, 20, -70),
        "rooms": rooms
    }


# =============================================================================
# ZONE 51: THE GNOMISH CLOCKWORK METROPOLIS OF LANTAN [Level 12-20, 60 Rooms]
# =============================================================================

def build_zone_clockwork_lantan():
    zone_key = "clockwork_lantan"
    zone_name = "The Gnomish Clockwork Metropolis of Lantan"
    rooms = {}

    rooms["clockwork_lantan_harbor"] = {
        "name": "The Clockwork Brass Harbor of Lantan",
        "desc": "A bustling seaport constructed of interlocking brass gears, bronze hydraulic cranes, and granite quays. Steamships and ironclads chug in and out of the harbor.",
        "terrain": "city",
        "exits": {"north": {"dest_id": "lantan_pneumatic_rail_terminal", "alias": "n"}},
        "npcs": [{"name": "Gnomish Harbor Mechanist", "desc": "A clever gnome in leather goggles holding a brass pneumatic wrench and steam gauge.", "level": 13, "role": "rogue"}]
    }

    rooms["lantan_pneumatic_rail_terminal"] = {
        "name": "The Grand Pneumatic Rail Terminal",
        "desc": "Polished steel tracks converge beneath a soaring dome of riveted brass and glass. Pneumatic passenger pods hiss into stations amidst clouds of clean steam.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "clockwork_lantan_harbor", "alias": "s"}, "north": {"dest_id": "clockwork_avenue_01", "alias": "n"}, "east": {"dest_id": "gond_foundry_of_gears", "alias": "e"}}
    }

    rooms["gond_foundry_of_gears"] = {
        "name": "The Great Foundry of the Wonderbringer",
        "desc": "Massive steam-powered trip hammers forge precision cogwheels from high-tensile bronze. Priests of Gond chant mathematical formulas as molten brass flows into molds.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "lantan_pneumatic_rail_terminal", "alias": "w"}, "north": {"dest_id": "clockwork_avenue_15", "alias": "n"}},
        "npcs": [{"name": "Gondar High Forge-Priest", "desc": "A devout artificer clad in copper-plated vestments with an arcane welder.", "level": 16, "role": "cleric"}],
        "items": [{"name": "Spool of High-Tensile Copper Wire", "desc": "Conductive wire used to assemble electrical traps and clockwork contraptions."}]
    }

    rooms["smokepowder_arsenal"] = {
        "name": "The Smokepowder Munitions Depot",
        "desc": "A reinforced vault protected by spark-arresting lead floorplates. Rows of brass bombards, flintlock arquebuses, and sealed kegs of black smokepowder line the walls.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "clockwork_avenue_30", "alias": "s"}},
        "npcs": [{"name": "Lantanese Bombadier", "desc": "A sharp-eyed gnome marksman carrying a triple-barreled pepperbox gun.", "level": 17, "role": "warrior"}],
        "items": [{"name": "Flask of Refined Smokepowder", "desc": "Volatile Lantanese smokepowder that detonates with thunderous explosive force."}]
    }

    rooms["great_clockwork_astrolabe"] = {
        "name": "The Great Planetarium Astrolabe",
        "desc": "A monumental multi-ringed mechanical universe that tracks planetary orbits and planar conjunctions with absolute clockwork precision.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "clockwork_avenue_45", "alias": "s"}}
    }

    rooms["master_artificer_beldon_workshop"] = {
        "name": "The Master Workshop of Grand Artificer Beldon",
        "desc": "The apex laboratory of Lantan's supreme inventor. Blueprints cover giant drafting tables, and dozens of prototype clockwork automatons await their power crystals.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "clockwork_avenue_54", "alias": "s"}},
        "npcs": [{"name": "Grand Artificer Beldon the Gearsmith", "desc": "A brilliant master gnome artificer in a mechanical exoskeleton powered by steam pistons and lightning coils, wielding a multi-tool wrench of pure adamantine.", "level": 22, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Smokepowder Thunder-Arquebus", "desc": "A masterful rifled musket that fires armor-piercing lead shot with devastating range."},
            {"name": "Gears of the Great Clockwork Cosmos", "desc": "A pocket astrolabe of interlocking mithral gears that predicts enemy movements and grants high evasion."}
        ]
    }

    # 54 Clockwork avenues, tramways, and laboratories to reach 60 rooms
    for i in range(1, 55):
        r_key = f"clockwork_avenue_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Cobblestones fitted with recessed iron gears that turn in synchrony beneath pedestrian walkways. "
            f"Brass streetlamps hum with internal clockwork escapements. [Lantan Sector #{i}]"
        )
        r_name = f"Clockwork Boulevard #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"clockwork_avenue_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"clockwork_avenue_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"clockwork_avenue_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"clockwork_avenue_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "lantan_pneumatic_rail_terminal", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "gond_foundry_of_gears", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "smokepowder_arsenal", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "great_clockwork_astrolabe", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "master_artificer_beldon_workshop", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Clockwork Spider Sentry", "desc": "A mechanical bronze arachnid that fires taser needles at intruders.", "level": 14, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Steam-Piston Automaton", "desc": "A bipedal iron robot that releases scalding steam when struck.", "level": 15, "role": "warrior"})

        if i == 25:
            items.append({"name": "Vial of High-Grade Clockwork Lubricant", "desc": "Refined oil that eliminates mechanical friction and squeaks."})

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
        "base_coords": (60, -130, 0),
        "rooms": rooms
    }


# =============================================================================
# ZONE 52: THE GITHZERAI MONASTERIES OF LIMBO [Level 18-26, 60 Rooms]
# =============================================================================

def build_zone_limbo_monasteries():
    zone_key = "limbo_monasteries"
    zone_name = "The Githzerai Floating Monasteries of Limbo"
    rooms = {}

    rooms["limbo_chaos_island_rim"] = {
        "name": "The Stabilized Island Rim of Shra'kt'lor",
        "desc": "A floating island of solid granite suspended in the swirling elemental chaos of Limbo. Beyond the mental boundary, fire, water, stone, and air churn in boiling primal discord.",
        "terrain": "air",
        "exits": {"north": {"dest_id": "monastery_courtyard_zerthimon", "alias": "n"}},
        "npcs": [{"name": "Githzerai Anarch Monk", "desc": "A calm, yellow-skinned ascetic in simple dun robes whose focused willpower maintains the physical integrity of the stone beneath your feet.", "level": 19, "role": "warrior"}]
    }

    rooms["monastery_courtyard_zerthimon"] = {
        "name": "The Courtyard of the Unbroken Circle",
        "desc": "A serene stone garden of raked granite pebbles and bonsai ironwood trees. Novice monks sit cross-legged in meditation, unfazed by the churning chaos sky.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "limbo_chaos_island_rim", "alias": "s"}, "north": {"dest_id": "limbo_chaos_span_01", "alias": "n"}, "east": {"dest_id": "slaad_spawning_chaos_rift", "alias": "e"}}
    }

    rooms["slaad_spawning_chaos_rift"] = {
        "name": "The Slaad Incursion Crevasse",
        "desc": "A breach where the mental stabilization barrier has fractured. Primal toad-like slaad fiends crawl from the roiling chaos soup, croaking with anarchic madness.",
        "terrain": "catacombs",
        "exits": {"west": {"dest_id": "monastery_courtyard_zerthimon", "alias": "w"}, "north": {"dest_id": "limbo_chaos_span_15", "alias": "n"}},
        "npcs": [{"name": "Red Slaad Egg-Planter", "desc": "A hulking crimson bipedal toad with razor talons capable of implanting parasitic tadpoles.", "level": 20, "role": "warrior"}],
        "items": [{"name": "Slaad Control Stone", "desc": "A small pulsating sphere of green quartz that grants dominion over chaos slaad."}]
    }

    rooms["hall_of_mental_discipline"] = {
        "name": "The Hall of Mental Discipline",
        "desc": "An expansive dojo where senior Zerth monks practice telekinetic martial arts. Stone boulders float gently in rhythm with their synchronized breathing.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "limbo_chaos_span_30", "alias": "s"}},
        "npcs": [{"name": "Zerth Psionic Master", "desc": "A monk whose hands strike with concussive psychic force.", "level": 22, "role": "mage"}],
        "items": [{"name": "Chaos-Stabilizing Monastic Bracers", "desc": "Silk arm bracers that protect the wearer from unpredictable planar distortions."}]
    }

    rooms["library_of_unbroken_circles"] = {
        "name": "The Library of Zerthimon's Wisdom",
        "desc": "Stone tablets inscribed with the eight circles of Zerthimon. Monks study the ancient philosophical texts that liberated their race from illithid slavery.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "limbo_chaos_span_45", "alias": "s"}}
    }

    rooms["anarch_zaer_inner_sanctum"] = {
        "name": "The Inner Sanctum of Supreme Anarch Zaer",
        "desc": "A floating platform of absolute stillness at the monastery's vortex. Supreme Anarch Zaer sits upon a simple reed mat, radiating boundless mental focus.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "limbo_chaos_span_54", "alias": "s"}},
        "npcs": [{"name": "Supreme Zerth Anarch Zaer", "desc": "An ancient githzerai master whose eyes pierce illusions and matter alike. His serene posture conceals devastating psionic mastery capable of willing whole worlds into existence.", "level": 25, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Unbroken Circle of Zerthimon", "desc": "A sacred interlocking ring of eight stone plates that confers absolute mental invulnerability."},
            {"name": "Robes of the Supreme Anarch", "desc": "Simple homespun robes that warp incoming hostile spells into harmless elemental mist."}
        ]
    }

    # 54 Monastic bridges, floating stones, and chaos spans to reach 60 rooms
    for i in range(1, 55):
        r_key = f"limbo_chaos_span_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"A bridge of solid stone held together solely by the combined willpower of meditating monks. "
            f"Beyond the bridge railing, liquid fire and crystalline earth boil in the void. [Limbo Sector #{i}]"
        )
        r_name = f"Limbo Mental Stone Span #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"limbo_chaos_span_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"limbo_chaos_span_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"limbo_chaos_span_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"limbo_chaos_span_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "monastery_courtyard_zerthimon", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "slaad_spawning_chaos_rift", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "hall_of_mental_discipline", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "library_of_unbroken_circles", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "anarch_zaer_inner_sanctum", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Blue Slaad Speller", "desc": "A large blue amphibian casting chaotic disruption spells.", "level": 21, "role": "mage"})
        elif i % 10 == 0:
            npcs.append({"name": "Githzerai Zerth Initiate", "desc": "An athletic martial artist striking with telekinetic palm thrusts.", "level": 20, "role": "warrior"})

        if i == 18:
            items.append({"name": "Bowl of Concentrated Mind-Tea", "desc": "Calming herbal tea that clears confusion, stupor, and magical fear."})

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
        "base_coords": (180, -30, 80),
        "rooms": rooms
    }


# =============================================================================
# ZONE 53: THE BURIED NETHERESE NECROPOLIS OF YTHRYN [Level 22-30, 60 Rooms]
# =============================================================================

def build_zone_ythryn_necropolis():
    zone_key = "ythryn_necropolis"
    zone_name = "The Buried Netherese Necropolis of Ythryn"
    rooms = {}

    rooms["ythryn_glacier_shaft_entrance"] = {
        "name": "The Glacial Shaft into Ythryn",
        "desc": "A deep vertical tunnel melted through hundreds of feet of solid permafrost ice. Below, the ancient obsidian spires of a fallen Netherese floating city lie entombed in subterranean ice.",
        "terrain": "ice",
        "exits": {"north": {"dest_id": "spire_of_necromancy_library", "alias": "n"}},
        "npcs": [{"name": "Netherese Tomb Wight", "desc": "A frozen wizard's corpse with glowing blue eye sockets, clutching an ice-rimed spellbook.", "level": 22, "role": "warrior"}]
    }

    rooms["spire_of_necromancy_library"] = {
        "name": "The Spire of the Eight Arcane Schools",
        "desc": "An inverted obsidian tower preserved perfectly inside glacial ice. Shelves of black marble hold thousands of frozen scroll tubes written in the ancient Netherese script.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "ythryn_glacier_shaft_entrance", "alias": "s"}, "north": {"dest_id": "ythryn_avenue_01", "alias": "n"}, "east": {"dest_id": "chamber_of_the_ythryn_mythallar", "alias": "e"}}
    }

    rooms["chamber_of_the_ythryn_mythallar"] = {
        "name": "The Great Chamber of the Ythryn Mythallar",
        "desc": "The heart of the floating city. A colossal fifty-foot crystal sphere of spinning arcane energy floats in the center, crackling with raw, unconstrained magical power.",
        "terrain": "indoors",
        "exits": {"west": {"dest_id": "spire_of_necromancy_library", "alias": "w"}, "north": {"dest_id": "ythryn_avenue_15", "alias": "n"}},
        "npcs": [{"name": "Living Blade of Disaster", "desc": "An animate spell resembling a curved tear in reality that hovers through the air slicing everything it touches.", "level": 26, "role": "warrior"}],
        "items": [{"name": "Ythryn Mythallar Shard", "desc": "A glowing crystal fragment capable of powering flying citadels and recharging artifacts."}]
    }

    rooms["hall_of_living_spells"] = {
        "name": "The Containment Hall of Living Spells",
        "desc": "A shattered menagerie where wild magical disasters took sentience when the city crashed. Living demiplanes and animate cloudkill vapors drift hungrily.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "ythryn_avenue_30", "alias": "s"}},
        "npcs": [{"name": "Living Cloudkill Abomination", "desc": "A sentient billowing cloud of yellow-green toxic vapor that devours living lungs.", "level": 25, "role": "mage"}],
        "items": [{"name": "Netherese Wand of Teleportation", "desc": "A heavy platinum wand capable of instant tactical dimensional shifts."}]
    }

    rooms["museum_of_ancient_netheril"] = {
        "name": "The Museum of the Arcane Empire",
        "desc": "Exhibition cases of indestructible forcefield glass hold ancient relics from the golden age of Netheril, before Karsus's Folly sundered the Weave.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "ythryn_avenue_45", "alias": "s"}}
    }

    rooms["crypt_of_demilich_iriolarthas"] = {
        "name": "The Sanctum of Demilich Iriolarthas",
        "desc": "The central spire where the former master of Ythryn lingers in unlife. A gilded human skull with eight sparkling magical gems in its teeth floats above an altar of black ice.",
        "terrain": "indoors",
        "exits": {"south": {"dest_id": "ythryn_avenue_54", "alias": "s"}},
        "npcs": [{"name": "Iriolarthas the Netherese Demilich", "desc": "The supreme master of the Eight Spires. A floating skull crowned in ancient Netherese gold, eyes blazing with the devastating power of the lost empire.", "level": 29, "role": "boss", "danger_tier": "boss"}],
        "items": [
            {"name": "Nether Scroll of Absolute Magic", "desc": "An authentic golden parchment of the Nether Scrolls that permanently increases spellcasting potency."},
            {"name": "Crown of Netheril", "desc": "The golden circlet of an archwizard of high Netheril, conferring complete spell immunity."}
        ]
    }

    # 54 Glacial streets, frozen plazas, and buried arches to reach 60 rooms
    for i in range(1, 55):
        r_key = f"ythryn_avenue_{i:02d}"
        if r_key in rooms:
            continue

        desc = (
            f"Streets of polished black stone encased within translucent glacial ice. "
            f"Frozen fountains and statues of ancient Netherese nobility stand preserved in time. [Ythryn Sector #{i}]"
        )
        r_name = f"Ythryn Frozen Avenue #{i}"

        exits = {}
        if i > 1:
            exits["south"] = {"dest_id": f"ythryn_avenue_{i-1:02d}", "alias": "s"}
        if i < 54:
            exits["north"] = {"dest_id": f"ythryn_avenue_{i+1:02d}", "alias": "n"}
        if i + 5 <= 54:
            exits["east"] = {"dest_id": f"ythryn_avenue_{i+5:02d}", "alias": "e"}
        if i - 5 >= 1:
            exits["west"] = {"dest_id": f"ythryn_avenue_{i-5:02d}", "alias": "w"}

        if i == 1:
            exits["south"] = {"dest_id": "spire_of_necromancy_library", "alias": "s"}
        if i == 15:
            exits["south"] = {"dest_id": "chamber_of_the_ythryn_mythallar", "alias": "s"}
        if i == 30:
            exits["north"] = {"dest_id": "hall_of_living_spells", "alias": "n"}
        if i == 45:
            exits["north"] = {"dest_id": "museum_of_ancient_netheril", "alias": "n"}
        if i == 54:
            exits["north"] = {"dest_id": "crypt_of_demilich_iriolarthas", "alias": "n"}

        npcs = []
        items = []
        if i % 7 == 0:
            npcs.append({"name": "Netherese Shadow Sentinel", "desc": "A spectral guardian armed with a chilling necrotic glaive.", "level": 23, "role": "warrior"})
        elif i % 10 == 0:
            npcs.append({"name": "Glacial Frost Gargoyle", "desc": "A winged gargoyle carved of sharp glacial true-ice.", "level": 24, "role": "warrior"})

        if i == 22:
            items.append({"name": "Crystal Shard of True Ice", "desc": "A magical ice crystal that remains cold forever and emits an aura of frost."})

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
        "base_coords": (-110, -120, -50),
        "rooms": rooms
    }


# =============================================================================
# MARITIME ROUTE HELPER
# =============================================================================

def register_iron_drake_ferry_routes():
    """Ensures The Steam-Paddle Ironclad 'Iron Drake' is registered in sailing.FERRY_ROUTES."""
    if "iron_drake_ship" not in sailing.FERRY_ROUTES:
        sailing.FERRY_ROUTES["iron_drake_ship"] = {
            "key": "iron_drake_ship",
            "name": 'The Steam-Paddle Ironclad "Iron Drake"',
            "operator": "Chief Engineer Sparkplug",
            "operator_title": "Master Mechanist of the Lantan Steam Guild",
            "ports": ["south_docks", "dead_mans_cove", "clockwork_lantan_harbor", "lantan_harbor"],
            "port_names": {
                "south_docks": "Harbor Promenade (Eldoria South Docks)",
                "dead_mans_cove": "Dead Man's Cove (Smuggler's Coast)",
                "clockwork_lantan_harbor": "The Clockwork Brass Harbor of Lantan",
                "lantan_harbor": "The Clockwork Brass Harbor of Lantan"
            },
            "fares": {
                ("south_docks", "clockwork_lantan_harbor"): 70,
                ("clockwork_lantan_harbor", "south_docks"): 70,
                ("dead_mans_cove", "clockwork_lantan_harbor"): 55,
                ("clockwork_lantan_harbor", "dead_mans_cove"): 55,
                ("south_docks", "lantan_harbor"): 70,
                ("lantan_harbor", "south_docks"): 70,
                ("dead_mans_cove", "lantan_harbor"): 55,
                ("lantan_harbor", "dead_mans_cove"): 55
            },
            "desc": "A formidable iron-plated steam warship powered by twin churning paddlewheels, belching black soot and aromatic gear oil as its bronze pressure valves hiss.",
            "deck_key": "iron_drake_deck"
        }


# =============================================================================
# MASTER RUNNER FOR PART 13
# =============================================================================

def run_bulk_ingestion_part13(clean_existing=False):
    """
    Executes Part 13 of the bulk world expansion ("2,800 Rooms Milestone"):
    - The Chasm of the Abyss & Royal Wood of Oolacile (60 rooms)
    - The Gnomish Clockwork Metropolis of Lantan (60 rooms)
    - The Githzerai Floating Monasteries of Limbo (60 rooms)
    - The Buried Netherese Necropolis of Ythryn (60 rooms)
    Plus The Steam-Paddle Ironclad 'Iron Drake' weather deck (1 room).
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
        build_zone_abyss_oolacile,
        build_zone_clockwork_lantan,
        build_zone_limbo_monasteries,
        build_zone_ythryn_necropolis
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("abyss_oolacile", "oolacile_sanctuary_garden_gate", "catacombs", "pass into abyss rift of oolacile", "return from oolacile to catacombs"),
        ("clockwork_lantan", "lantan_pneumatic_rail_terminal", "rail_hub", "board pneumatic express to lantan", "board return train to rail hub"),
        ("limbo_monasteries", "limbo_chaos_island_rim", "summit", "step into churning chaos of limbo", "return through githzerai portal to summit"),
        ("ythryn_necropolis", "ythryn_glacier_shaft_entrance", "frostfang_pass", "descend glacial shaft into ythryn", "ascend ice shaft to frostfang pass")
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

    # 4. Register Iron Drake Ironclad Ferry Route & Weather Deck
    iron_drake_deck = find_room_by_key("iron_drake_deck")
    if not iron_drake_deck:
        iron_drake_deck = create_object(Room, key='The Steam-Paddle Ironclad "Iron Drake" - Weather Deck', tags=[TAG_WORLD])
        iron_drake_deck.tags.add("iron_drake_deck", category="room_key")
        iron_drake_deck.tags.add("clockwork_lantan", category="zone")
        iron_drake_deck.db.room_key = "iron_drake_deck"
        iron_drake_deck.db.desc = (
            "You stand upon the steel armor-plated deck of the ironclad. "
            "Twin massive steam paddlewheels churn white spray along the flanks, "
            "while brass smokestacks rumble with soot and steam."
        )
        iron_drake_deck.db.zone = "Steam Seas"
        iron_drake_deck.db.terrain = "water_swim"
        iron_drake_deck.db.coords = (60, -130, 0)
        report["rooms_created"] += 1

    register_iron_drake_ferry_routes()
    report["ferry_routes_added"].append('The Steam-Paddle Ironclad "Iron Drake" (south_docks <-> dead_mans_cove <-> clockwork_lantan_harbor)')

    return report

