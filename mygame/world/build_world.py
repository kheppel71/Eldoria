"""
World Builder for Evennia
Creates an expansive, interconnected 49-room multi-zone adventure realm across 8 distinct regions:
1. The City of Eldoria (Hub City)
2. The Whispering Wilds (Forest & Overland)
3. The Crypt of the Hollow King (Underground Dungeon)
4. The Smuggler Sewers (Underground Urban / Rogue Guild)
5. Smuggler's Bay & The Siren Reefs (Maritime & Coast)
6. The Moonlit Glade & Feywild Verge (Fey / Enchanted Glade)
7. The Abandoned Deep Dwarf Foundry (Subterranean Industrial / Magma)
8. The Frozen Peaks & Hermit's Ridge (Alpine / Boreal Mountain)

Featuring all 25 Interactive Mini-Quests, custom NPCs, puzzle locks, usable items, and commands!
"""

import os
import sys

# Ensure Evennia environment is loaded
os.chdir(r"c:\Evennia\mygame")
sys.path.insert(0, r"c:\Evennia\mygame")
os.environ["DJANGO_SETTINGS_MODULE"] = "server.conf.settings"

import django
django.setup()

import evennia
evennia._init()

from evennia.utils.create import create_object, create_script
from evennia.objects.models import ObjectDB
from evennia.scripts.models import ScriptDB
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.objects import Object
from typeclasses.characters import Character


def create_exit(location, destination, key, aliases=None):
    """Helper to create a one-way exit."""
    if aliases is None:
        aliases = []
    for ex in location.exits:
        if ex.key.lower() == key.lower():
            ex.destination = destination
            return ex
    return create_object(
        Exit,
        key=key,
        location=location,
        destination=destination,
        aliases=aliases,
        tags=["eldoria_world"]
    )


def create_two_way_exit(room_a, room_b, dir_a_to_b, dir_b_to_a, alias_a=None, alias_b=None):
    """Creates reciprocal exits between two rooms."""
    aliases_a = [alias_a] if alias_a else []
    aliases_b = [alias_b] if alias_b else []
    ex_ab = create_exit(room_a, room_b, dir_a_to_b, aliases_a)
    ex_ba = create_exit(room_b, room_a, dir_b_to_a, aliases_b)
    return ex_ab, ex_ba


def build_world():
    print("Beginning massive world construction across all 8 zones and 25 quests...")

    # Locate Limbo
    try:
        limbo = ObjectDB.objects.get(id=2)
    except ObjectDB.DoesNotExist:
        limbo = ObjectDB.objects.filter(db_key__iexact="Limbo").first()

    if not limbo:
        raise RuntimeError("Could not find Limbo room (#2).")

    TAG_WORLD = "eldoria_world"

    # Clean existing world objects safely
    existing = list(ObjectDB.objects.filter(db_tags__db_key=TAG_WORLD).distinct())
    if existing:
        print(f"Cleaning up {len(existing)} previous world objects...")
        for obj in existing:
            try:
                obj.delete()
            except Exception:
                pass

    rooms = {}
    current_zone = ["The City of Eldoria"]
    current_terrain = ["city"]

    def make_room(key, title, desc, zone=None, terrain=None, coords=None):
        r = create_object(Room, key=title, tags=[TAG_WORLD])
        r.tags.add(key, category="room_key")
        r.db.room_key = key
        r.db.desc = desc.strip()
        r.db.zone = zone or current_zone[0]
        r.db.terrain = terrain or current_terrain[0]
        if coords:
            r.db.coords = coords
        rooms[key] = r
        return r

    def make_item(name, location, desc, aliases=None):
        if aliases is None:
            aliases = []
        item = create_object(Object, key=name, location=location, aliases=aliases, tags=[TAG_WORLD])
        item.db.desc = desc.strip()
        return item

    def make_npc(name, location, desc, aliases=None, dialog_start=None):
        if aliases is None:
            aliases = []
        npc = create_object(Character, key=name, location=location, aliases=aliases, tags=[TAG_WORLD])
        npc.db.desc = desc.strip()
        if dialog_start:
            npc.db.dialog_menu = "world.dialogues"
            npc.db.dialog_startnode = dialog_start
        return npc

    # =========================================================================
    # ZONE 1: THE CITY OF ELDORIA
    # =========================================================================
    make_room("plaza", "Eldoria Grand Plaza",
        "The beating heart of Eldoria, a vibrant marble-paved square surrounding "
        "a towering crystalline fountain carved in the likeness of an ancient water wyrm. "
        "Banners of azure and gold ripple gently in the breeze. Bustling streets lead north to "
        "the city gates, east to the grand bazaar, west toward the sanctuary of light, and "
        "south down toward the docks. A shimmering archway marked with the seal of Limbo stands nearby."
    )

    make_room("north_gate", "Eldoria North Gate",
        "Massive iron-reinforced portcullises hang between two stone watchtowers. Royal guards "
        "in polished chainmail watch travelers with steady vigilance. Beyond the gate lies the "
        "wild King's Road winding into the untamed wilderness. To the south, the city plaza stretches out."
    )

    make_room("bazaar", "The Sunken Bazaar",
        "A canopy of vibrant silks and colorful canvas hangs overhead, shielding the market from "
        "the weather. The air is thick with the scent of roasted nuts, cinnamon, exotic spices, and "
        "freshly baked bread. Merchants shout their wares from bustling wooden stalls."
    )

    make_room("blacksmith", "Thunderhammer Forge",
        "The ringing cadence of hammer on iron echoes against stone walls. Waves of blistering heat "
        "emanate from the roaring blast furnace. Racks of broadswords, chain shirts, battleaxes, "
        "and glowing steel ingots line the soot-stained perimeter."
    )

    make_room("alchemist", "The Silver Crucible Apothecary",
        "Shelves of glass vials, spiraling alembics, and bubbling cauldrons fill this fragrant shop. "
        "Bundles of dried lavender, wolfsbane, and glowing blue moss hang from the rafters. A soft, "
        "luminescent smoke curls gracefully through the air."
    )

    make_room("tavern_common", "The Drunken Dragon Tavern",
        "A warm, lively tavern filled with rustic oak tables, roaring hearths, and the hearty din "
        "of laughing travelers and clinking flagons of spiced mead. A bard tunes a lute by the fire, "
        "and the tantalizing smell of roasted boar wafts from the kitchen. Stairs lead upward to private "
        "chambers, while an arched wooden hatch leads down to the cellar."
    )

    make_room("tavern_rooms", "The Drunken Dragon - Second Floor Lodgings",
        "A quiet corridor of polished cedar, lined with heavy tapestries and candle sconces. "
        "Comfortable guest rooms offer soft feather beds for weary adventurers needing a good night's rest."
    )

    make_room("tavern_cellar", "Drunken Dragon Wine Cellar",
        "Cool, dim, and smelling of aged oak, cobwebs, and vintage wine. Giant casks of vintage "
        "cider and blackberry wine rest on wooden blocks. In the shadows behind a stack of crates, "
        "a cold draft seems to whisper from a cracked stone wall."
    )

    make_room("temple_way", "Temple Way",
        "A quiet avenue paved with pristine white flagstones, flanked by sculpted marble statues "
        "of saints, scholars, and legendary paladins. An iron storm drain leads down into the city cisterns."
    )

    make_room("cathedral", "Cathedral of the Radiant Dawn",
        "Vast vaulted ceilings soar into the heavens, illuminated by dazzling stained-glass windows "
        "that cast kaleidoscopic pools of amber and violet light across the polished floor. A great golden "
        "altar rests at the apse, emanating an aura of serene serenity and peace."
    )

    make_room("arcane_library", "The Arcane Library & Scriptorium",
        "Spiral staircases wrap around towering bookshelves containing thousands of leather-bound grimoires, "
        "astronomical charts, and ancient spell scrolls. Floating orbs of faint witchlight drift silently, "
        "illuminating ornate reading desks and brass astrolabes."
    )

    make_room("south_docks", "Harbor Promenade",
        "The salty smell of the sea mingles with tar, hemp rope, and fresh fish. Gulls cry overhead "
        "as merchant caravels and fishing brigs rock against the wooden piers. A sturdy wooden rowboat is "
        "moored at the dock, ready to cross toward Dead Man's Cove."
    )

    make_room("warehouse", "Old Salt Warehouse",
        "A damp warehouse stacked high with wooden shipping crates, coiled ropes, and barrels of salted herring. "
        "Shafts of grey light pierce the gloom from high water-streaked windows. An iron drainage grate leads "
        "down into the sewer sluice."
    )

    make_room("bank", "Royal Bank of Eldoria & Vault",
        "Polished white marble counters front heavy brass teller grates. Vault boxes line the reinforced "
        "granite walls, guarded by silent iron golems. Lord Aldous Sterling oversees transactions from a raised mahogany desk."
    )

    # =========================================================================
    # ZONE 2: THE WHISPERING WILDS (OVERLAND)
    # =========================================================================
    current_zone[0] = "The Whispering Wilds"
    current_terrain[0] = "forest"
    make_room("kings_road", "The King's Highway",
        "A wide stone-paved road that has seen centuries of merchant wagons and marching legions. "
        "To the south, the fortified walls of Eldoria recede into the horizon. To the north, dense "
        "woods crowd the shoulders of the road like silent sentinels."
    )

    make_room("woods_edge", "Edge of the Whispering Woods",
        "The neat stone road fades into an uneven dirt track flanked by towering ancient oaks and "
        "silver birches. A perpetual hush hangs over the trees, broken only by the rustling of "
        "fallen leaves and distant birdsong."
    )

    make_room("deep_woods", "Deep in the Whispering Woods",
        "Ancient boughs interlace high above, blocking all but stray beams of dappled sunlight. "
        "Twisted roots form natural stairways over mossy boulders. Near an overgrown clearing, a circle of "
        "luminescent violet toadstools pulses with otherworldly fey twilight."
    )

    make_room("druid_circle", "Ancient Stone Circle",
        "A ring of colossal, moss-cloaked megaliths stands in a peaceful forest clearing. "
        "Carved runes pulse with a faint emerald radiance beneath the ivy. At the center sits a smooth "
        "stone altar upon which wild blossoms never seem to wither."
    )

    make_room("misty_river", "Misty River Crossing",
        "A brisk, crystal-clear river rushes over smooth river rocks. A rickety wooden suspension bridge "
        "sways gently over the rapids. The spray from the water creates a perpetual rainbow in the sunlight."
    )

    make_room("marshland", "The Sunken Mire",
        "The ground softens into thick, black peat and murky standing water. Croaking frogs, buzzing "
        "insects, and eerie will-o'-the-wisps flicker in the dense fog. Decayed trees reach upward like "
        "skeletal fingers."
    )

    make_room("witch_hut", "Witch's Stilt Hut",
        "Perched above the swamp water on crooked wooden pilings, this crooked hut smells of boiled roots, "
        "swamp thyme, and sulfur. Dried bat wings, bundles of snake skin, and curious talismans swing "
        "from the low overhang."
    )

    make_room("foothills", "Craggy Foothills",
        "The forest yields to steep, rocky inclines dotted with hardy scrub brush and wind-bent pines. "
        "Jagged grey peaks rise menacingly against the northern sky. A deep geological fissure reveals "
        "an ancient mine shaft descending into subterranean darkness."
    )

    make_room("watchtower", "Ruined Hilltop Watchtower",
        "The shattered remains of an ancient border fortress overlook the valley below. A massive iron "
        "signal pyre sits ready atop the parapet. A steep, ice-glazed goat trail winds upward into the freezing peaks."
    )

    # =========================================================================
    # ZONE 3: THE CRYPTS OF THE HOLLOW KING (DUNGEON)
    # =========================================================================
    current_zone[0] = "Crypts of the Hollow King"
    current_terrain[0] = "dungeon"
    make_room("crypt_entrance", "Dungeon Threshold: The Hollow Gate",
        "Carved directly into the sheer face of a jagged mountain cliff, a grim archway shaped like a "
        "screaming skull yawns into blackness. Cold, stagnant air spills out, carrying the faint odor of "
        "damp stone and old dust. Worn stairs spiral steeply into the subterranean dark."
    )

    make_room("antechamber", "Dusty Antechamber",
        "A square hall of dark obsidian blocks, untouched by the sun for centuries. Cobwebs blanket the "
        "corners, and discarded stone sarcophagi lie overturned. Iron sconces hold remnants of long-burnt torches."
    )

    make_room("pillared_hall", "Great Hall of Pillars",
        "A cavernous hypostyle hall supported by two rows of fluted stone pillars carved with images of "
        "armored kings and weeping angels. The floor is cracked, and water drips rhythmically from stalactites."
    )

    make_room("ossuary", "The Sunken Ossuary",
        "Walls of neatly stacked skulls and femurs line this somber chamber. The center of the room is sunken, "
        "forming a shallow pool of black mineral water. Ripples stir across the surface without any apparent wind."
    )

    make_room("goblin_den", "Goblin Skulker Outpost",
        "A crude encampment littered with gnawed bones, stolen iron pots, and patchwork hide bedrolls. "
        "A low campfire crackles, sending acrid smoke up through a fissure in the rock ceiling."
    )

    make_room("catacombs", "Forgotten Catacombs",
        "A labyrinth of narrow burial niches carved into soft limestone. Inscriptions in an archaic tongue "
        "warn trespassers of a restless monarch sleeping beyond the veil. To the north stands a colossal, "
        "rusted iron portcullis sealing the royal sanctum."
    )

    make_room("throne_room", "Sanctum of the Hollow King",
        "A magnificent, chilling throne room carved of black granite and rimmed with eerie blue witchfire. "
        "At the far dais sits a colossal throne of fused obsidian blades. Upon the throne slumbers the armored "
        "wraith of the Hollow King, crowned with withered iron."
    )

    # =========================================================================
    # ZONE 4: THE SMUGGLER SEWERS (UNDERGROUND URBAN / ROGUES)
    # =========================================================================
    current_zone[0] = "The Smuggler Sewers"
    current_terrain[0] = "sewers"
    make_room("sluice_gate", "Sewer Sluice Gate Overlook",
        "Slime-sheathed brick archways curve over a churning canal of runoff water. Massive rusted iron "
        "cogs and sluice wheels control the flow of the city's drainage. An iron ladder leads up to the warehouse grate."
    )

    make_room("black_rat_den", "The Black Rat Hideout",
        "A secret rogue's den nestled in a dry subterranean vault. Tallow candles flicker in bottles, "
        "illuminating card tables, stolen velvet tapestries, and stacks of contraband crates."
    )

    make_room("rat_warren", "The Rat King's Warren",
        "A foul, squelching cavern formed by collapsed brickwork and garbage detritus. Squeaking eyes glint in "
        "the shadowy nooks, and the stench of decay is heavy."
    )

    make_room("ancient_cistern", "Ancient Sunken Cistern",
        "A breathtaking vaulted hall dating back to the First Empire, supported by rows of fluted marble arches "
        "partially submerged in still, dark water. A heavy iron drainage valve wheel is mounted on the wall."
    )

    # =========================================================================
    # ZONE 5: SMUGGLER'S BAY & THE SIREN REEFS (MARITIME / COAST)
    # =========================================================================
    current_zone[0] = "Smuggler's Bay"
    current_terrain[0] = "coast"
    make_room("dead_mans_cove", "Dead Man's Cove",
        "A secluded, crescent-shaped pebble beach hemmed in by towering black sea cliffs. Driftwood, broken oars, "
        "and kelp litter the high-tide line. A rowboat rests near the surf."
    )

    make_room("siren_wreck", "Wreck of the Siren's Call",
        "The barnacle-encrusted timber ribs of a shattered merchant frigate loom out of the shallow breakers. "
        "The sea rushes through the fractured hull with a deep, hollow moan."
    )

    make_room("sea_cavern", "Bioluminescent Sea Cavern",
        "A tidal sea cave bathed in the eerie cyan glow of phosphorescent algae. Stalactites drip into turquoise "
        "tide pools, and a haunting, hypnotic melody echoes off the slick cavern walls."
    )

    make_room("smuggler_grotto", "Smuggler's Hidden Grotto",
        "A dry sea cavern fitted with wooden rope hoists, kegs of imported rum, and canvas hammocks. "
        "A natural sea chimney filters daylight from high above."
    )

    # =========================================================================
    # ZONE 6: THE MOONLIT GLADE & FEYWILD VERGE (FEY / ENCHANTED)
    # =========================================================================
    current_zone[0] = "The Moonlit Glade"
    current_terrain[0] = "feywild"
    make_room("twilight_glade", "Twilight Moonlit Glade",
        "A realm of eternal silver twilight where moonlight pools across lush violet grass like liquid silk. "
        "Giant luminous mushrooms cast gentle pastels of lilac and azure through the gentle mist."
    )

    make_room("weeping_tree", "The Weeping Elder Tree",
        "A colossal weeping willow whose silver-leaved branches trail down like waterfalls into a crystal spring. "
        "The tree's ancient trunk bears the wise, sorrowful face of Oakhaven the Treant."
    )

    make_room("pixie_court", "Court of the Pixie Queen",
        "A whimsical circle of glowing bioluminescent toadstools surrounded by dancing swarms of winged sprites. "
        "Tiny crystalline bells chime in the sweet, blossom-scented breeze."
    )

    make_room("briar_maze", "The Briar Maze",
        "A labyrinth of colossal thorned briars and midnight-blue roses. The paths twist and rustle as if "
        "the garden itself were alive and watching your every step."
    )

    # =========================================================================
    # ZONE 7: THE ABANDONED DEEP DWARF FOUNDRY (MAGMA / INDUSTRIAL)
    # =========================================================================
    current_zone[0] = "Abandoned Deep Dwarf Foundry"
    current_terrain[0] = "subterranean"
    make_room("rail_hub", "Subterranean Rail Hub",
        "A vast cavern echoing with the distant hum of geothermal steam. Rusted iron rails crisscross the stone floor, "
        "and abandoned ore carts rest on sidings beneath soaring basalt arches."
    )

    make_room("magma_forge", "The Core Magma Forge",
        "A titanic forge hall suspended directly over a roiling subterranean lake of bright orange magma. "
        "Massive hydraulic trip-hammers stand silent, awaiting the return of master craftsmen."
    )

    make_room("assembly_bay", "Dormant Assembly Bay",
        "Workbenches cluttered with brass gears, hydraulic pistons, and blueprints. Along the back wall stand "
        "racks of clockwork automatons, frozen in mid-stride."
    )

    make_room("steam_valve", "Geothermal Pressure Valve",
        "A narrow iron catwalk suspended over hissing steam vents and boiling thermal springs. A massive brass "
        "pressure release valve vibrates under immense geothermal force."
    )

    # =========================================================================
    # ZONE 8: THE FROZEN PEAKS & HERMIT'S RIDGE (ALPINE / MOUNTAIN)
    # =========================================================================
    current_zone[0] = "The Frozen Peaks"
    current_terrain[0] = "mountain"
    make_room("frostfang_pass", "Frostfang Mountain Pass",
        "A treacherous trail choked with deep snowdrifts and buffeted by biting sub-zero gale winds. "
        "Sheer ice-covered cliffs plunge thousands of feet into the valley below."
    )

    make_room("chasm_bridge", "The Howling Chasm Bridge",
        "A precarious rope suspension bridge swaying violently over a bottomless glacier abyss. "
        "Clusters of rare glowing frost-lichen cling to the ice-glazed precipice."
    )

    make_room("hermit_cave", "Hermit's Ice Cavern",
        "A cozy, smoke-filled cave carved into the permafrost. A burning peat fire crackles in a stone hearth, "
        "filling the cave with the earthy aroma of mountain tea and cedar shavings."
    )

    make_room("summit", "The Cloud-Piercing Summit",
        "The highest peak in the known realm, rising above the clouds beneath a dizzying dome of stars. "
        "An ancient celestial sundial carved of white star-metal stands at the edge of the world."
    )

    # =========================================================================
    # ZONE 9: THE ISLE OF SERPENTS & REMOTE WATERS (EXPANSIVE ISLAND REGION)
    # Accessible exclusively via Maritime Ferries & Operators!
    # =========================================================================
    current_zone[0] = "The Isle of Serpents"
    current_terrain[0] = "island"
    make_room("isle_harbor", "Corsair's Anchorage",
        "A weather-beaten timber jetty extending out into crashing turquoise breakers. Lanterns flicker on "
        "rusted iron gallows, and coiled harpoon lines lie stacked beneath tarred canopies. "
        "The Salt-Spit Sea Ferry and Corsair's Longboat dock here. Trails lead north onto the coral strand, "
        "and inland into the dense tropical palm jungle."
    )

    make_room("isle_beach", "Siren's Bleached Strand",
        "A dazzling white coral beach strewn with giant whale ribs, bleached driftwood, and shimmering conch shells. "
        "To the south lies the harbor, while to the east the sands wrap toward the Smuggler's Lagoon."
    )

    make_room("isle_jungle", "The Tangled Palm Jungle",
        "A humid, shadowy tropical rainforest choked with climbing strangler figs, giant ferns, and hanging lianas. "
        "Vibrant emerald macaws shriek from the canopy as ocean breezes rustle the palm fronds. "
        "Paths wind toward the soaring sea cliffs and an ancient drowned ruin."
    )

    make_room("isle_cliffs", "Black Basalt Sea Cliffs",
        "Jagged volcanic cliffs plunging hundreds of feet into churning white foam and treacherous sea caves. "
        "Seabirds nest in thousands of rocky niches along the sheer face, riding the updrafts of warm ocean air."
    )

    make_room("isle_cove", "Smuggler's Lagoon",
        "A secluded turquoise cove concealed behind a natural sea-arch of black volcanic rock. The waters here "
        "are mirror-still, sheltered from the violent open-ocean swells. Helmsman Joshua's rowed longboat "
        "is moored at a concealed wooden floating dock."
    )

    make_room("isle_ruins", "Sunken Temple of the Sea Serpent",
        "Cyclopean basalt pillars draped in kelp and sea fans rise from the flooded flagstones. An ancient altar "
        "carved in the likeness of an open-jawed leviathan stands half-submerged in the crystal-clear tidal surge."
    )

    make_room("isle_grotto", "Glowing Coral Grotto",
        "A magical subterranean sea grotto illuminated by millions of bioluminescent anemones and azure coral polyps. "
        "Gentle waves lap against smooth quartz ledges where rare sea-glass catches the ethereal light."
    )

    make_room("isle_wreck", "The Leviathan's Graveyard",
        "The splintered, barnacle-crusted hull of the imperial war galleon H.M.S. Sovereign lies broken upon "
        "jagged black sea spires. Shattered cannon barrels, anchor chains, and lost cargo chests rest in the reef shallows."
    )

    make_room("silt_islet", "Whispering Silt Islet",
        "An isolated, teardrop-shaped islet in the middle of the rushing Misty River, reachable only by "
        "Old Jacques' flatboat ferry. Weeping river willows trail into deep pools favored by legendary golden trout."
    )

    # DEDICATED FERRY WEATHER DECKS (TRANSIT SPACES)
    make_room("salt_spit_deck", "The Salt-Spit Sea Ferry - Weather Deck",
        "The sturdy, pitch-caulked oak deck of the harbor ferry. Salt spray foams across the bulwarks, "
        "and heavy canvas sails snap in the brisk ocean wind. Ferrywoman Maeve commands the ship's wheel from the quarterdeck."
    )

    make_room("misty_skiff_deck", "The Misty Flatboat - River Deck",
        "A flat cedar deck fitted with rustic benches and an iron brazier to ward off the river chill. "
        "Old Riverman Jacques maneuvers the long iron-tipped steering pole with practiced ease."
    )

    make_room("corsair_longboat_deck", "The Corsair's Longboat - Oar Benches",
        "A sleek, black-hulled coastal craft fitted with leather-wrapped oarlocks. Salt foam slaps against the hull "
        "as the vessel navigates the treacherous coral reefs and sea chimneys of the Isle of Serpents."
    )

    # =========================================================================
    # CONNECTING EXITS ACROSS ALL 8 ZONES
    # =========================================================================
    # Limbo <-> Eldoria Plaza
    create_two_way_exit(limbo, rooms["plaza"], "world", "limbo", alias_a="eldoria", alias_b="leave")

    # City Connections
    create_two_way_exit(rooms["plaza"], rooms["north_gate"], "north", "south", "n", "s")
    create_two_way_exit(rooms["plaza"], rooms["bazaar"], "east", "west", "e", "w")
    create_two_way_exit(rooms["plaza"], rooms["temple_way"], "west", "east", "w", "e")
    create_two_way_exit(rooms["plaza"], rooms["south_docks"], "south", "north", "s", "n")
    create_two_way_exit(rooms["plaza"], rooms["bank"], "bank", "plaza", "b", "p")

    create_two_way_exit(rooms["bazaar"], rooms["blacksmith"], "north", "south", "n", "s")
    create_two_way_exit(rooms["bazaar"], rooms["alchemist"], "east", "west", "e", "w")
    create_two_way_exit(rooms["bazaar"], rooms["tavern_common"], "south", "north", "s", "n")

    create_two_way_exit(rooms["tavern_common"], rooms["tavern_rooms"], "up", "down", "u", "d")
    create_two_way_exit(rooms["tavern_common"], rooms["tavern_cellar"], "down", "up", "d", "u")

    create_two_way_exit(rooms["temple_way"], rooms["cathedral"], "west", "east", "w", "e")
    create_two_way_exit(rooms["temple_way"], rooms["arcane_library"], "north", "south", "n", "s")

    create_two_way_exit(rooms["south_docks"], rooms["warehouse"], "east", "west", "e", "w")

    # City <-> Wilderness
    create_two_way_exit(rooms["north_gate"], rooms["kings_road"], "north", "south", "n", "s")
    create_two_way_exit(rooms["kings_road"], rooms["woods_edge"], "north", "south", "n", "s")

    # Wilderness Connections
    create_two_way_exit(rooms["woods_edge"], rooms["deep_woods"], "east", "west", "e", "w")
    create_two_way_exit(rooms["woods_edge"], rooms["misty_river"], "north", "south", "n", "s")

    create_two_way_exit(rooms["deep_woods"], rooms["druid_circle"], "north", "south", "n", "s")

    create_two_way_exit(rooms["misty_river"], rooms["marshland"], "east", "west", "e", "w")
    create_two_way_exit(rooms["misty_river"], rooms["foothills"], "north", "south", "n", "s")

    create_two_way_exit(rooms["marshland"], rooms["witch_hut"], "north", "south", "n", "s")

    create_two_way_exit(rooms["foothills"], rooms["watchtower"], "up", "down", "u", "d")
    create_two_way_exit(rooms["foothills"], rooms["crypt_entrance"], "north", "south", "n", "s")

    # Dungeon Connections
    create_two_way_exit(rooms["crypt_entrance"], rooms["antechamber"], "down", "up", "d", "u")
    create_two_way_exit(rooms["antechamber"], rooms["pillared_hall"], "north", "south", "n", "s")
    create_two_way_exit(rooms["pillared_hall"], rooms["ossuary"], "east", "west", "e", "w")
    create_two_way_exit(rooms["pillared_hall"], rooms["goblin_den"], "west", "east", "w", "e")
    create_two_way_exit(rooms["pillared_hall"], rooms["catacombs"], "north", "south", "n", "s")

    # LOCKED DUNGEON GATE (Requires Rusty Iron Key)
    iron_gate = create_exit(
        location=rooms["catacombs"],
        destination=rooms["throne_room"],
        key="iron gate",
        aliases=["gate", "north", "n", "portcullis"]
    )
    iron_gate.locks.add("traverse:holds(Rusty Iron Key)")
    iron_gate.db.err_traverse = (
        "|rThe massive dwarven iron portcullis is locked fast! "
        "A large keyhole is visible, guarded by intricate locking tumblers. "
        "You need the Rusty Iron Key (stolen by the goblins in their outpost) to open it!|n"
    )
    iron_gate.tags.add(TAG_WORLD)

    return_gate = create_exit(
        location=rooms["throne_room"],
        destination=rooms["catacombs"],
        key="south",
        aliases=["s", "gate", "leave"]
    )
    return_gate.tags.add(TAG_WORLD)

    # Secret passage: Tavern Cellar <-> Warehouse
    create_two_way_exit(rooms["tavern_cellar"], rooms["warehouse"], "passage", "hatch", "p", "h")

    # ZONE 4: SEWERS CONNECTIONS
    create_two_way_exit(rooms["warehouse"], rooms["sluice_gate"], "sewer grate", "surface", "grate", "up")
    create_two_way_exit(rooms["temple_way"], rooms["ancient_cistern"], "storm drain", "surface", "drain", "up")
    create_two_way_exit(rooms["sluice_gate"], rooms["black_rat_den"], "iron ladder", "sluice", "ladder", "sluice")
    create_two_way_exit(rooms["sluice_gate"], rooms["rat_warren"], "sludge canal", "canal back", "canal", "back")
    create_two_way_exit(rooms["black_rat_den"], rooms["ancient_cistern"], "conduit", "hideout", "c", "h")

    # ZONE 5: SMUGGLER'S BAY CONNECTIONS
    create_two_way_exit(rooms["south_docks"], rooms["dead_mans_cove"], "rowboat", "docks", "boat", "docks")
    create_two_way_exit(rooms["dead_mans_cove"], rooms["siren_wreck"], "shallows", "beach", "wreck", "cove")
    create_two_way_exit(rooms["dead_mans_cove"], rooms["sea_cavern"], "sea arch", "cove", "arch", "cove")
    create_two_way_exit(rooms["sea_cavern"], rooms["smuggler_grotto"], "grotto", "cavern", "g", "c")

    # ZONE 6: MOONLIT GLADE CONNECTIONS
    create_two_way_exit(rooms["deep_woods"], rooms["twilight_glade"], "fairy ring", "woods", "ring", "woods")
    create_two_way_exit(rooms["twilight_glade"], rooms["weeping_tree"], "mossy trail", "glade", "tree", "glade")
    create_two_way_exit(rooms["twilight_glade"], rooms["pixie_court"], "shimmering pool", "glade", "pool", "glade")
    create_two_way_exit(rooms["weeping_tree"], rooms["briar_maze"], "bramble burrow", "tree", "maze", "tree")

    # ZONE 7: DEEP FOUNDRY CONNECTIONS
    create_two_way_exit(rooms["foothills"], rooms["rail_hub"], "mine fissure", "surface", "fissure", "surface")
    create_two_way_exit(rooms["rail_hub"], rooms["magma_forge"], "track north", "rail hub", "north", "south")
    create_two_way_exit(rooms["rail_hub"], rooms["assembly_bay"], "track west", "rail hub", "west", "east")
    create_two_way_exit(rooms["magma_forge"], rooms["steam_valve"], "catwalk", "forge", "valve", "forge")

    # ZONE 8: FROZEN PEAKS CONNECTIONS
    create_two_way_exit(rooms["watchtower"], rooms["frostfang_pass"], "climb trail", "watchtower", "pass", "down")
    create_two_way_exit(rooms["frostfang_pass"], rooms["chasm_bridge"], "rope bridge", "trail", "bridge", "trail")
    create_two_way_exit(rooms["chasm_bridge"], rooms["hermit_cave"], "cliff ledge", "bridge", "cave", "bridge")
    create_two_way_exit(rooms["hermit_cave"], rooms["summit"], "ascent", "cave", "summit", "cave")

    # ZONE 9: ISLE OF SERPENTS CONNECTIONS (ON-ISLAND FOOT TRAILS)
    create_two_way_exit(rooms["isle_harbor"], rooms["isle_beach"], "north", "south", "n", "s")
    create_two_way_exit(rooms["isle_harbor"], rooms["isle_jungle"], "inland", "harbor", "in", "h")
    create_two_way_exit(rooms["isle_beach"], rooms["isle_cove"], "east", "west", "e", "w")
    create_two_way_exit(rooms["isle_jungle"], rooms["isle_cliffs"], "cliffs", "jungle", "climb", "j")
    create_two_way_exit(rooms["isle_jungle"], rooms["isle_ruins"], "ruins", "jungle", "r", "j")
    create_two_way_exit(rooms["isle_cove"], rooms["isle_grotto"], "grotto", "lagoon", "g", "l")
    create_two_way_exit(rooms["isle_beach"], rooms["isle_wreck"], "shallows", "beach", "wreck", "b")

    # =========================================================================
    # NPCS WITH INTERACTIVE EVMENU DIALOGUES (ALL 25 QUESTS)
    # =========================================================================
    # Zone 1
    make_npc("Barnaby the Barkeep", rooms["tavern_common"],
        "A jovial, rotund man with a white apron, briskly wiping wooden tankards.",
        aliases=["barnaby", "barkeep"], dialog_start="barnaby_start_node")

    make_npc("Lord Commander Valerius", rooms["north_gate"],
        "A battle-hardened officer clad in plate mail engraved with griffins.",
        aliases=["valerius", "commander"], dialog_start="valerius_start_node")

    make_npc("Gorim Thunderhammer", rooms["blacksmith"],
        "A muscular dwarf with a braided red beard and a leather apron.",
        aliases=["gorim", "blacksmith"], dialog_start="gorim_start_node")

    make_npc("Tobin the Apprentice Smith", rooms["blacksmith"],
        "A soot-smudged youth frantically checking grease-stained gears.",
        aliases=["tobin", "apprentice"], dialog_start="tobin_start_node")

    make_npc("Madam Belladonna", rooms["alchemist"],
        "An eccentric herbalist with silver hair tied back with velvet ribbon.",
        aliases=["belladonna", "alchemist"], dialog_start="belladonna_start_node")

    make_npc("Sister Meredith", rooms["cathedral"],
        "A serene priestess in white linen kneeling in devout prayer.",
        aliases=["meredith", "priestess"], dialog_start="meredith_start_node")

    make_npc("Pip the Street Urchin", rooms["bazaar"],
        "A quick-footed child in oversized wool rags darting between market awnings.",
        aliases=["pip", "urchin"], dialog_start="pip_start_node")

    make_npc("Archmage Vane", rooms["arcane_library"],
        "An ancient scholar robed in celestial blue velvet, levitating thick tomes.",
        aliases=["vane", "mage"], dialog_start="vane_start_node" if "vane_start_node" in globals() else None)

    make_npc("Brother Jonathan", rooms["arcane_library"],
        "A scholarly monk with wire-rimmed spectacles, poring over ancient treatises.",
        aliases=["jonathan", "brother"], dialog_start="jonathan_start_node")

    make_npc("Master Scribe Cassian", rooms["arcane_library"],
        "The Chief Philologist of the Scriptorium, surrounded by open lexicons and quills.",
        aliases=["cassian", "scribe", "philologist", "master scribe"], dialog_start="cassian_start_node")

    make_npc("Silas 'Gull' Vane", rooms["south_docks"],
        "A nervous wharf inspector glancing suspiciously toward the old warehouse.",
        aliases=["silas", "gull"], dialog_start="silas_start_node")

    make_npc("Lord Aldous Sterling", rooms["bank"],
        "An impeccably dressed banker with gold spectacles and a velvet waistcoat, reviewing ledgers with precision.",
        aliases=["aldous", "sterling", "banker"], dialog_start="aldous_start_node")

    # Zone 2 & 3
    make_npc("Scout Heather", rooms["woods_edge"],
        "A cloaked elven ranger leaning against a pine tree, nursing a bandaged shoulder.",
        aliases=["heather", "scout"], dialog_start="heather_start_node")

    make_npc("The Whispering Sentinel", rooms["druid_circle"],
        "A colossal moss-covered stone face carved into the ancient monolith.",
        aliases=["sentinel", "stone face"], dialog_start="sentinel_start_node")

    make_npc("Mirella the Bog Witch", rooms["witch_hut"],
        "A wizened crone with sharp yellow eyes stirring a bubbling cauldron.",
        aliases=["mirella", "witch"], dialog_start="mirella_start_node")

    make_npc("Barnaby-Toad", rooms["marshland"],
        "A plump, warty green amphibian with a glowing third eye.",
        aliases=["toad", "familiar"])

    make_npc("Old Man Corvus", rooms["marshland"],
        "A toothless peat-cutter smoking a clay pipe filled with marsh weed.",
        aliases=["corvus", "old man"], dialog_start="corvus_start_node")

    make_npc("Lady Elspeth", rooms["ossuary"],
        "A translucent ghostly apparition in shredded burial silks weeping silently.",
        aliases=["elspeth", "ghost"], dialog_start="elspeth_start_node")

    make_npc("Chief Snaggletooth", rooms["goblin_den"],
        "A squat, boastful goblin wearing a dented copper kettle as a helmet.",
        aliases=["snaggletooth", "chief"], dialog_start="snaggletooth_start_node")
    rooms["goblin_den"].contents[-1].db.hp = 120
    rooms["goblin_den"].contents[-1].db.max_hp = 120

    make_npc("The Hollow King", rooms["throne_room"],
        "A towering specter clad in rusted coronation armor.",
        aliases=["king", "hollow king"])
    rooms["throne_room"].contents[-1].db.hp = 250
    rooms["throne_room"].contents[-1].db.max_hp = 250

    # Zone 4: Sewers
    make_npc("Finch the Fence", rooms["black_rat_den"],
        "A sharp-eyed dealer in stolen goods with quick fingers and gold teeth.",
        aliases=["finch", "fence"], dialog_start="finch_start_node")

    make_npc("Gribble the Rat-Catcher", rooms["sluice_gate"],
        "An old eccentric wearing a patchwork coat of rat pelts with his terrier Sniffer.",
        aliases=["gribble", "rat-catcher"], dialog_start="gribble_start_node")

    make_npc("The Sewer Patriarch", rooms["rat_warren"],
        "A mutated, giant albino rat the size of a warhound with blood-red eyes.",
        aliases=["patriarch", "giant rat", "rat"])
    rooms["rat_warren"].contents[-1].db.hp = 90
    rooms["rat_warren"].contents[-1].db.max_hp = 90

    # Zone 5: Smuggler's Bay
    make_npc("Captain 'One-Eye' Morgan", rooms["dead_mans_cove"],
        "A weathered privateer captain whittling driftwood with a silver hook.",
        aliases=["morgan", "captain"], dialog_start="morgan_start_node")

    make_npc("Deckhand Barnaby's Ghost", rooms["siren_wreck"],
        "The dripping, translucent spirit of the drowned frigate helmsman.",
        aliases=["ghost helmsman", "drowned barnaby"], dialog_start="drowned_barnaby_start_node")

    make_npc("Lorelei the Sea Siren", rooms["sea_cavern"],
        "A breathtaking aquatic enchantress resting upon an emerald tidal rock.",
        aliases=["lorelei", "siren"], dialog_start="lorelei_start_node")

    # Zone 6: Moonlit Glade
    make_npc("Queen Tatiana of the Briar", rooms["pixie_court"],
        "A thumb-sized sprite monarch hovering on gossamer dragonfly wings.",
        aliases=["tatiana", "queen", "pixie queen"], dialog_start="tatiana_start_node")

    make_npc("Oakhaven the Treant", rooms["weeping_tree"],
        "A colossal, ancient weeping willow with wise mossy bark eyes.",
        aliases=["oakhaven", "treant", "tree"], dialog_start="oakhaven_start_node")

    make_npc("Puck the Jester Sprite", rooms["twilight_glade"],
        "A mischievous fairy sitting upside down on a floating toadstool.",
        aliases=["puck", "sprite"], dialog_start="puck_start_node")

    # Zone 7: Deep Dwarf Foundry
    make_npc("Automaton Unit 7-B ('Cog')", rooms["assembly_bay"],
        "A brass clockwork servant awaiting a steam power core.",
        aliases=["cog", "unit 7-b", "automaton"], dialog_start="cog_start_node")

    make_npc("Ghost of High Artificer Dueran", rooms["magma_forge"],
        "The spectral master smith of the ancient dwarven magma crucible.",
        aliases=["dueran", "artificer"], dialog_start="dueran_start_node")

    # Zone 8: Frozen Peaks
    make_npc("Brother Kaelen", rooms["frostfang_pass"],
        "A lost pilgrim shivering violently in a snowdrift on the pass.",
        aliases=["kaelen", "pilgrim"], dialog_start="kaelen_start_node")

    make_npc("Titus the Blind Mountain Hermit", rooms["hermit_cave"],
        "A former royal astrologer warming his hands beside a peat hearth.",
        aliases=["titus", "hermit"], dialog_start="titus_start_node")

    make_npc("Skirnir the Frost Drake", rooms["summit"],
        "A colossal dragon of pure crystalline ice slumbering atop the celestial sundial.",
        aliases=["skirnir", "drake", "frost drake"], dialog_start="skirnir_start_node")
    rooms["summit"].contents[-1].db.hp = 500
    rooms["summit"].contents[-1].db.max_hp = 500

    # Zone 9: Maritime Ferry Operators & Island NPCs
    make_npc("Ferrywoman Maeve", rooms["south_docks"],
        "A weather-beaten mariner with salt-sprayed hair, leaning against the harbor mooring bollard.",
        aliases=["maeve", "ferrywoman", "ferryman"], dialog_start="maeve_start_node")

    make_npc("Old Riverman Jacques", rooms["misty_river"],
        "A weathered riverman in a patched burlap smock, poling his cedar punt through the rapids.",
        aliases=["jacques", "riverman", "ferryman"], dialog_start="jacques_start_node")

    make_npc("Helmsman Joshua", rooms["isle_harbor"],
        "A sharp-eyed island navigator testing the oars of his coastal longboat.",
        aliases=["joshua", "helmsman", "ferryman"], dialog_start="joshua_start_node")

    make_npc("Captain 'Salt-Beard' Flint", rooms["isle_beach"],
        "A marooned sea captain in a tattered bicorne hat, carving driftwood with an oyster knife.",
        aliases=["flint", "captain", "salt-beard"], dialog_start="flint_start_node")

    make_npc("Coral Hermit Shelly", rooms["isle_grotto"],
        "An eccentric hermit weaving glowing coral polyps and pearlescent sea-glass.",
        aliases=["shelly", "hermit"], dialog_start="shelly_start_node")

    # Darkness flags for subterranean rooms (Nightmare vision system)
    for dark_room in ["antechamber", "pillared_hall", "ossuary", "goblin_den", "catacombs", "rat_warren", "rail_hub"]:
        rooms[dark_room].db.is_dark = True

    # =========================================================================
    # QUEST ITEMS, REAGENTS, CONSUMABLES & TOOLS
    # =========================================================================
    # City & Wilderness Items
    make_item("Wax-Sealed Cipher Ledger", rooms["warehouse"],
        "A water-damaged leather ledger crammed with coded manifests and corrupt harbor payoffs.",
        aliases=["ledger", "cipher"])

    bun = make_item("Sweet Honey Bun", rooms["bazaar"],
        "A fresh pastry dusted with sugar and drizzled with golden wildflower honey.",
        aliases=["bun", "pastry"])
    bun.db.is_drinkable = True
    bun.db.drink_type = "pastry"

    make_item("Oiled Copper Cog", rooms["plaza"],
        "A heavy brass clockwork cog resting near the drainage grating of the Wyrm Fountain.",
        aliases=["cog", "copper cog", "gear"])

    make_item("Dry Pine Kindling", rooms["deep_woods"],
        "A dry bundle of resinous pine splinters wrapped in twine.",
        aliases=["kindling", "pine kindling"])

    make_item("Watchtower Signal Pyre", rooms["watchtower"],
        "A massive iron fire-basket filled with dry logs. Use: light pyre",
        aliases=["pyre", "signal pyre", "beacon"])

    make_item("River Pearl", rooms["misty_river"],
        "A lustrous freshwater pearl glowing with pale azure light.",
        aliases=["pearl", "river pearl"])

    make_item("Sunburst Blossom", rooms["deep_woods"],
        "A radiant golden flower that blossoms even in deep forest shade.",
        aliases=["blossom", "flower"])

    make_item("Grave Dust", rooms["crypt_entrance"],
        "A pinch of fine grey dust gathered from the ancient stone carvings of the Hollow Gate.",
        aliases=["dust", "grave dust"])

    make_item("Glow-Beetle Jar", rooms["witch_hut"],
        "A glass jar humming with trapped bioluminescent insects.",
        aliases=["beetle jar", "jar"])

    make_item("Dancing Will-O'-the-Wisp", rooms["marshland"],
        "A flickering, playful orb of sapphire spirit fire dancing over the bog. Use: catch wisp",
        aliases=["wisp", "spirit fire"])

    make_item("Silver Filigree Locket", rooms["antechamber"],
        "An antique silver locket resting inside an overturned sarcophagus.",
        aliases=["locket", "silver locket"])

    make_item("Sack of Stolen Silverware", rooms["goblin_den"],
        "A heavy burlap sack stuffed with engraved royal silver platters and goblets.",
        aliases=["silverware", "sack of silverware"])

    make_item("Rusty Iron Key", rooms["goblin_den"],
        "A heavy, notched iron key corroded with ancient green patina. Fits Great-Uncle Bror's portcullis!",
        aliases=["key", "iron key"])

    make_item("Crown of the Hollow Sovereign", rooms["throne_room"],
        "An ancient circlet of blackened wrought iron set with a pale, cold gemstone.",
        aliases=["crown", "sovereign crown"])

    make_item("Black Soul-Shard", rooms["throne_room"],
        "A jagged obsidian crystal pulsing with cold, dark malice. The phylactery of the Hollow King!",
        aliases=["shard", "soul-shard", "phylactery"])

    # Sewer Items
    make_item("Sewer Valve Wheel", rooms["ancient_cistern"],
        "A heavy iron spoked wheel mounted on the sluice pipe. Use: turn wheel",
        aliases=["valve", "wheel", "valve wheel"])

    make_item("Scent-Masking Musk Flask", rooms["sluice_gate"],
        "A flask of pungent swamp musk that masks human scent from rats.",
        aliases=["musk", "flask"])

    # Smuggler's Bay Items
    make_item("Barnacled Brass Compass", rooms["siren_wreck"],
        "A heavy brass nautical compass salvaged from the frigate's locker.",
        aliases=["compass", "brass compass"])

    make_item("Beeswax Earplugs", rooms["dead_mans_cove"],
        "Dense plugs of amber beeswax that muffle siren enchantments.",
        aliases=["earplugs", "plugs"])

    make_item("Tide-Locked Sea Chest", rooms["dead_mans_cove"],
        "An iron-bound sea chest resting in the sand, locked tight against the surf.",
        aliases=["chest", "sea chest"])

    # Fey Glade Items
    make_item("Crystal Phial of Liquid Moonlight", rooms["twilight_glade"],
        "A crystal phial swirling with captured silver moonlight.",
        aliases=["moonlight", "phial"])

    make_item("Golden Fey Flute", rooms["pixie_court"],
        "A tiny carved bone instrument that charms woodland beasts.",
        aliases=["flute", "fey flute"])

    # Deep Foundry Items
    make_item("Pneumatic Steam Core", rooms["rail_hub"],
        "A heavy brass cylinder vibrating with pressurized geothermal steam.",
        aliases=["core", "steam core"])

    make_item("Heavy Mining Pickaxe", rooms["assembly_bay"],
        "A steel-tipped dwarven pickaxe used for mining ore veins. Use: mine ore",
        aliases=["pickaxe", "pick"])

    # Frozen Peaks Items
    make_item("Bundle of Warm Furs", rooms["watchtower"],
        "Heavy bear and mountain wolf furs that insulate against sub-zero blizzards.",
        aliases=["furs", "bundle of furs"])

    make_item("Pinch of Frost-Lichen", rooms["chasm_bridge"],
        "A clump of glowing cyan lichen clinging to the icy precipice.",
        aliases=["lichen", "frost-lichen"])

    make_item("Ice Drake's Molted Scale", rooms["summit"],
        "A crystal-clear dragon scale as hard as diamond and cold as winter.",
        aliases=["scale", "drake scale"])

    make_item("Astral Lens Fragment", rooms["summit"],
        "A polished star-prism that fits into the summit celestial sundial.",
        aliases=["lens", "astral lens", "fragment"])

    # Usable Consumables & Gear
    stout = make_item("Frothing Tankard of Stout", rooms["tavern_common"],
        "A heavy wooden tankard filled to the brim with dark, malty dwarven stout.",
        aliases=["tankard", "beer", "stout"])
    stout.db.is_drinkable = True
    stout.db.drink_type = "stout"

    elixir = make_item("Glowing Health Elixir", rooms["alchemist"],
        "A crystal vial filled with shimmering crimson liquid that radiates soothing warmth.",
        aliases=["elixir", "potion", "health potion"])
    elixir.db.is_drinkable = True
    elixir.db.drink_type = "elixir"

    make_item("Luminous Swamp Moss", rooms["marshland"],
        "A cluster of rare, bioluminescent moss glowing with a vibrant emerald luster.",
        aliases=["moss", "swamp moss"])

    make_item("Steel Broadsword", rooms["blacksmith"],
        "A finely balanced broadsword forged from high-carbon steel.",
        aliases=["sword", "broadsword"])

    make_item("Ranger's Longbow", rooms["woods_edge"],
        "A supple yew bow crafted by forest scouts.",
        aliases=["bow", "longbow"])

    make_item("Pitch Torch", rooms["antechamber"],
        "A sturdy wooden club wrapped in pitch-soaked burlap. Use: light torch",
        aliases=["torch"])

    # =========================================================================
    # FISHING GEAR: RODS, REELS & BAIT
    # =========================================================================
    # 1. Basic Starter Rods
    make_item("Old Bamboo Fishing Rod", rooms["south_docks"],
        "A flexible pole of notched bamboo fitted with simple bone line guides. Great for dock fishing! Use: fish or cast",
        aliases=["rod", "fishing rod", "bamboo rod", "pole"])

    make_item("Old Bamboo Fishing Rod", rooms["misty_river"],
        "A flexible pole of notched bamboo fitted with simple bone line guides. Perfect for river banks! Use: fish or cast",
        aliases=["rod", "fishing rod", "bamboo rod", "pole"])

    # 2. Advanced Coastal / Deep Sea Rod
    make_item("Reinforced Oak & Brass Reel Rod", rooms["dead_mans_cove"],
        "A heavy sea rod carved of seasoned salt-oak with a smooth brass geared reel. Handles ocean bass and barracuda!",
        aliases=["rod", "sea rod", "brass rod", "heavy rod"])

    # 3. Enchanted Fey Rod
    make_item("Fey-Spun Silk Rod with Silver Reel", rooms["twilight_glade"],
        "An ethereal rod crafted of petrified willow strung with braided pixie silk. Attracts celestial and fey fish!",
        aliases=["rod", "fey rod", "silk rod"])

    # 4. Subterranean Dwarven Rod
    make_item("Ghost-Iron Grappling Rod", rooms["rail_hub"],
        "A heavy dwarven rod forged of dark ghost-iron with a counter-weighted crank reel. Hauls up sunken lockboxes and blind cave fish!",
        aliases=["rod", "ghost-iron rod", "dwarven rod"])

    # Baits
    make_item("Can of Earthworms", rooms["south_docks"],
        "A tin can filled with rich loam and wriggling earthworms. Good all-around freshwater and dock bait!",
        aliases=["worms", "earthworms", "bait", "can of worms"])

    make_item("Can of Earthworms", rooms["misty_river"],
        "A tin can filled with rich loam and wriggling earthworms. Trout and salmon love them!",
        aliases=["worms", "earthworms", "bait", "can of worms"])

    make_item("Salted Squid Strips", rooms["dead_mans_cove"],
        "A dried pouch of salted calamari strips that release a potent scent in saltwater.",
        aliases=["squid", "strips", "squid strips", "bait"])

    make_item("Golden Breadcrumbs", rooms["bazaar"],
        "A small cloth pouch of sweet buttered breadcrumbs. Attracts minnows, carp, and surface feeders!",
        aliases=["breadcrumbs", "crumbs", "bait"])

    make_item("Luminous Grubs", rooms["antechamber"],
        "A jar of pale subterranean grubs glowing with faint phosphorescence. Irresistible to blind cave fish!",
        aliases=["grubs", "luminous grubs", "bait"])

    make_item("Glowing Fire-Beetles", rooms["witch_hut"],
        "A small wicker jar of buzzing orange fire-beetles. Swamp catfish and lurkers snap at them eagerly!",
        aliases=["beetles", "fire-beetles", "bait"])

    # =========================================================================
    # NIGHTMARE HIGH ARCANE SPELL SCROLLS & REAGENTS
    # =========================================================================
    s_fireball = make_item("Scroll of Fireball", rooms["arcane_library"],
        "An ancient parchment scroll inscribed with fiery evocation glyphs. Use: study scroll of fireball",
        aliases=["scroll", "fireball scroll", "scroll of fireball"])
    s_fireball.db.spell = "fireball"

    s_lightning = make_item("Scroll of Lightning Bolt", rooms["watchtower"],
        "A crackling vellum scroll radiating faint static and ozone. Use: study scroll of lightning",
        aliases=["scroll", "lightning scroll", "scroll of lightning bolt"])
    s_lightning.db.spell = "lightning"

    s_stone = make_item("Scroll of Stone Skin", rooms["assembly_bay"],
        "A heavy granite-embossed parchment describing geomantic abjurations. Use: study scroll of stone skin",
        aliases=["scroll", "stoneskin scroll", "scroll of stone skin"])
    s_stone.db.spell = "stoneskin"

    s_blink = make_item("Scroll of Blink", rooms["twilight_glade"],
        "A shimmering scroll woven from ethereal planar threads. Use: study scroll of blink",
        aliases=["scroll", "blink scroll", "scroll of blink"])
    s_blink.db.spell = "blink"

    s_smite = make_item("Scroll of Divine Smite", rooms["cathedral"],
        "A consecrated golden scroll penned in sacred solar runes. Use: study scroll of divine smite",
        aliases=["scroll", "smite scroll", "scroll of divine smite"])
    s_smite.db.spell = "smite"

    s_animate = make_item("Scroll of Animate Dead", rooms["catacombs"],
        "A brittle parchment stitched from blackened vellum and charnel ink. Use: study scroll of animate dead",
        aliases=["scroll", "animate scroll", "scroll of animate dead"])
    s_animate.db.spell = "animate"

    # Spell Reagents
    make_item("Pinch of Brimstone Sulfur", rooms["witch_hut"],
        "A pungent yellow powder essential for fueling roaring fireball detonations.",
        aliases=["sulfur", "brimstone", "brimstone sulfur", "pinch of sulfur"])

    make_item("Pinch of Brimstone Sulfur", rooms["magma_forge"],
        "A pungent yellow powder mined from the subterranean magma vents.",
        aliases=["sulfur", "brimstone", "brimstone sulfur", "pinch of sulfur"])

    make_item("Flask of Consecrated Holy Water", rooms["cathedral"],
        "A crystal vial blessed by High Priestess Meredith, emitting a gentle solar warmth.",
        aliases=["holy water", "water", "flask of holy water"])

    make_item("Pouch of Grave Dust", rooms["ossuary"],
        "A pouch of spectral charnel dust gathered from ancient sarcophagi.",
        aliases=["dust", "grave dust", "pouch of grave dust"])

    # =========================================================================
    # LINGUISTIC PRIMERS & ANCIENT LEXICONS
    # =========================================================================
    make_item("Elven Grammar Primer", rooms["arcane_library"],
        "An illustrated book bound in leaf-pressed parchment detailing Elven syntax and poetic cadence. Use: studylang elven",
        aliases=["primer", "elven primer", "elven grammar primer", "lexicon"])

    make_item("Ancient Draconic Lexicon", rooms["magma_forge"],
        "A massive codex bound in black dragon scales transcribing archaic wyrm runes. Use: studylang draconic",
        aliases=["lexicon", "draconic lexicon", "draconic codex", "codex"])

    make_item("Dwarven Runic Tablet", rooms["assembly_bay"],
        "A heavy slab of polished slate carved with angular Khazalid runes. Use: studylang dwarven",
        aliases=["tablet", "runic tablet", "dwarven tablet", "primer"])

    make_item("Celestial Hymnal of Light", rooms["cathedral"],
        "A gilded hymnal containing harmonic celestial chants of the upper spheres. Use: studylang celestial",
        aliases=["hymnal", "celestial hymnal", "celestial primer", "book"])

    # =========================================================================
    # ZONE 9: ISLE OF SERPENTS & MARITIME ITEMS
    # =========================================================================
    make_item("Coral-Tipped Harpoon", rooms["isle_ruins"],
        "An ancient sea weapon carved of hardened fire-coral and wrapped in rough sharkskin.",
        aliases=["harpoon", "coral harpoon", "weapon"])

    make_item("Barnacled Captain's Strongbox", rooms["isle_wreck"],
        "A heavy iron-bound sea chest salvaged from the flooded hold of the H.M.S. Sovereign.",
        aliases=["strongbox", "chest", "sea chest"])

    make_item("Iridescent Sea-Glass", rooms["isle_grotto"],
        "A smooth, luminescent shard of sea-glass buffed by centuries of turquoise waves.",
        aliases=["sea-glass", "glass", "shard"])

    make_item("Sunken Astrolabe", rooms["isle_cove"],
        "A corroded brass navigational instrument retrieved from the calm lagoon sands.",
        aliases=["astrolabe", "instrument"])

    # Deep Sea & Island Fishing Baits
    make_item("Pouch of Squid Strips", rooms["isle_harbor"],
        "A packet of salted squid strips prized by deep-water sea fishermen.",
        aliases=["squid", "strips", "squid strips", "bait"])

    make_item("Luminescent Sea Worms", rooms["isle_grotto"],
        "Glowing subterranean marine worms that attract rare phosphorescent trench fish.",
        aliases=["worms", "sea worms", "bait"])

    # =========================================================================
    # AMBIENT WORLD SCRIPT REGISTRATION
    # =========================================================================
    for scr in ScriptDB.objects.filter(db_key="ambient_world_script"):
        scr.stop()
        scr.delete()

    create_script("world.ambient.AmbientWorldScript", key="ambient_world_script")
    print("Ambient living world script activated!")

    print(f"World construction successful!")
    print(f"Created {len(rooms)} distinct rooms across 9 regions (including Isle of Serpents and Ferry routes).")
    print("All maritime ferries, operators, municipal tax coffers, quests, and NPCs initialized.")


if __name__ == "__main__":
    build_world()
