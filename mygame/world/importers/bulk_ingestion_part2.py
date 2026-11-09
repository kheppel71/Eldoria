"""
Bulk World Ingestion Engine — Part 2: The Extended Realms

Expands Eldoria with an additional 120 rooms across 4 legendary open-source inspired zones:
1. The Emerald Canopy & Elven Glades of Silvanesti (CircleMUD / Lothlorien) [Level 7-13]
2. The Great Halls of Khazad-Dum & Deep Magma Forges (tbaMUD Dwarven Kingdom) [Level 14-20]
3. The Shifting Dunes of Kalim Desert & Pyramid of the Sun (CoffeeMUD / CircleMUD) [Level 12-17]
4. The Realm of Honshu & Monasteries of the Jade Mountain (Nightmare IV Heritage) [Level 15-22+]

Features:
- Dual Overland and Maritime access (New 'Jade Dragon Junk' sailing route)
- 100% GMCP Room.Info automapper telemetry
- Fixed danger level combat sheets and boss loot tables
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
    OPPOSITE_DIR,
    TAG_WORLD
)
from world.importers.bulk_ingestion import init_mob_combat
import world.sailing as sailing

# =============================================================================
# ZONE 6: SILVANESTI ELVEN GLADES [Level 7-13, 30 Rooms]
# =============================================================================

def build_zone_silvanesti():
    return {
        "zone_key": "silvanesti_canopy",
        "zone_name": "The Emerald Canopy of Silvanesti",
        "default_terrain": "forest",
        "base_coords": (25, 0, 10),
        "rooms": {
            "canopy_ascent": {
                "name": "Ascent to the Emerald Canopy",
                "desc": "Massive spiral wooden staircases wrap around the colossal trunk of an ancient mallorn tree. The green forest floor falls away below as you ascend toward the sun-dappled canopy.",
                "terrain": "forest",
                "exits": {"up": {"dest_id": "village_flet", "alias": "u"}},
                "npcs": [{"name": "Silvanesti Boundary Scout", "desc": "An agile elven archer clad in leaf-patterned green leathers.", "level": 7, "role": "rogue"}]
            },
            "village_flet": {
                "name": "Central Flet of the Elven Haven",
                "desc": "A wide wooden platform suspended high among the great branches of the canopy. Graceful elven dwellings woven from living birch boughs surround a central communal hearth.",
                "terrain": "city",
                "exits": {"down": {"dest_id": "canopy_ascent", "alias": "d"}, "north": {"dest_id": "bowyer_loft", "alias": "n"}, "east": {"dest_id": "suspension_bridge_1", "alias": "e"}, "west": {"dest_id": "druid_moon_well", "alias": "w"}},
                "npcs": [{"name": "Silvanesti Citizen", "desc": "A graceful high elf with golden hair humming an ancient melody.", "level": 6, "role": "civilian"}]
            },
            "bowyer_loft": {
                "name": "The Master Bowyer's Loft",
                "desc": "Staves of seasoned yew, ash, and heartwood dry upon overhead racks. Beautiful recurve longbows strung with silver sinew hang on display.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "village_flet", "alias": "s"}},
                "npcs": [{"name": "Master Bowyer Aeldir", "desc": "An elder elf shaving a yew branch with a curved drawknife.", "level": 9, "role": "warrior"}],
                "items": [{"name": "Silvanesti Elven Longbow", "desc": "A flexible, beautifully crafted longbow of ancient yew."}]
            },
            "druid_moon_well": {
                "name": "The Shimmering Moon Well",
                "desc": "A circular basin of carved white marble cradles water that glows with soft lunar luminescence. Droplets of dew ripple across the surface like liquid silver.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "village_flet", "alias": "e"}, "north": {"dest_id": "starlight_observatory", "alias": "n"}},
                "npcs": [{"name": "Arch-Druid Faelyn", "desc": "A serene elven mystic holding an oaken staff crowned with a glowing acorn.", "level": 13, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Phial of Moon Well Tears", "desc": "A crystal phial of rejuvenating lunar spring water."}]
            },
            "starlight_observatory": {
                "name": "Observatory of the Silver Leaf",
                "desc": "Open to the night sky, this high perch among the leaves offers an unobstructed view of the constellations. Intricate celestial globes of brass spin silently.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "druid_moon_well", "alias": "s"}}
            },
            "suspension_bridge_1": {
                "name": "The Swaying Vine Bridge",
                "desc": "Thick braided creepers and flexible cedar slats form a bridge spanning between two immense forest patriarchs. The wind gently rocks the walkway.",
                "terrain": "air",
                "exits": {"west": {"dest_id": "village_flet", "alias": "w"}, "east": {"dest_id": "elder_oak_heart", "alias": "e"}}
            },
            "elder_oak_heart": {
                "name": "Heart of the Elder Oak",
                "desc": "A hollow chamber inside the living trunk of a tree older than recorded history. Carved wooden benches follow the natural contours of the wood.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "suspension_bridge_1", "alias": "w"}, "down": {"dest_id": "lower_root_glade", "alias": "d"}}
            },
            "lower_root_glade": {
                "name": "The Sunken Root Glade",
                "desc": "Gargantuan gnarled tree roots curl into natural tunnels on the forest floor. Patches of luminous blue moss illuminate the soft loam.",
                "terrain": "forest",
                "exits": {"up": {"dest_id": "elder_oak_heart", "alias": "u"}, "north": {"dest_id": "dryad_grove", "alias": "n"}, "south": {"dest_id": "spider_hollow_entrance", "alias": "s"}},
                "npcs": [{"name": "Mossback Treant", "desc": "A walking sentinel of living bark and leafy boughs.", "level": 11, "role": "warrior"}]
            },
            "dryad_grove": {
                "name": "Sacred Grove of the Dryads",
                "desc": "White blossoms drift down from cherry and almond boughs. The air smells sweet as honey, and melodic laughter echoes from unseen figures.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "lower_root_glade", "alias": "s"}},
                "npcs": [{"name": "Sylvan Dryad", "desc": "A breathtaking nature spirit whose hair flows like weeping willow leaves.", "level": 10, "role": "mage"}]
            },
            "spider_hollow_entrance": {
                "name": "Threshold to the Gloomy Weave",
                "desc": "The vibrant green forest darkens abruptly here. Thick grey cobwebs blanket the bushes and hang in sticky curtains from the lower branches.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "lower_root_glade", "alias": "n"}, "south": {"dest_id": "spider_lair", "alias": "s"}},
                "npcs": [{"name": "Silvanesti Webspinner", "desc": "A chitinous arachnid the size of a war horse with venom-dripping fangs.", "level": 10, "role": "warrior"}]
            },
            "spider_lair": {
                "name": "Lair of the Broodmother",
                "desc": "Skeletons of deer and unwary orcs hang cocooned in silk. In the center sits a pulsating egg sac surrounded by scurrying hatchlings.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "spider_hollow_entrance", "alias": "n"}},
                "npcs": [{"name": "Broodmother Queen", "desc": "A monstrous obsidian spider with eight burning red eyes.", "level": 12, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Spun Silk Cloak of Stealth", "desc": "A lightweight cloak woven from spider silk that blends into shadows."}]
            },
            "canopy_walk_north": {
                "name": "Northern Canopy Way",
                "desc": "Wooden catwalks hugging the outer branches overlooking the rolling canopy of green.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "bowyer_loft", "alias": "s"}, "east": {"dest_id": "flet_scouts", "alias": "e"}}
            },
            "flet_scouts": {
                "name": "Flet of the Frontier Rangers",
                "desc": "Barracks platform where wilderness rangers sharpen broadhead hunting arrows.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "canopy_walk_north", "alias": "w"}}
            },
            "canopy_walk_south": {
                "name": "Southern Canopy Walkway",
                "desc": "A scenic timber walkway flanked by blooming orchids and climbing jasmine.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "village_flet", "alias": "n"}}
            },
            "weaving_loft": {
                "name": "The Elven Loom Loft",
                "desc": "Looms of polished rosewood weaving gossamer cloaks and banners.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "village_flet", "alias": "e"}}
            },
            "herbalist_perch": {
                "name": "The Sylvan Herbalist",
                "desc": "Clay jars filled with dried silverleaf, kingsblood, and wild clover.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "canopy_walk_south", "alias": "w"}}
            },
            "blossom_bridge": {
                "name": "The Blossom Bridge",
                "desc": "A suspension bridge covered in fragrant violet wisteria vines.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "canopy_ascent", "alias": "s"}}
            },
            "whispering_glade": {
                "name": "The Whispering Glade",
                "desc": "A clearing where the leaves rustle with secret prophecies in the forest wind.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "lower_root_glade", "alias": "n"}}
            },
            "river_branch": {
                "name": "Canopy Overlook of the Silver Stream",
                "desc": "A high viewpoint gazing down upon the shimmering blue waters of the forest river.",
                "terrain": "air",
                "exits": {"west": {"dest_id": "flet_scouts", "alias": "w"}}
            },
            "glade_falls": {
                "name": "Misty Falls of Silvanesti",
                "desc": "A gentle cascade of mountain water spilling over mossy boulders into a crystal basin.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "whispering_glade", "alias": "e"}}
            },
            "moon_shrine": {
                "name": "Altar of the Pale Lady",
                "desc": "A silver crescent altar surrounded by blooming white nightshade.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "druid_moon_well", "alias": "s"}}
            },
            "canopy_east_watch": {
                "name": "Eastern Canopy Sentry Post",
                "desc": "A camouflaged watch post scanning the eastern horizon for orc raiders.",
                "terrain": "forest",
                "exits": {"west": {"dest_id": "elder_oak_heart", "alias": "w"}}
            },
            "songbird_roost": {
                "name": "The Songbird Roost",
                "desc": "Hundreds of brightly plumaged forest finches and nightingales nesting peacefully.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "canopy_east_watch", "alias": "n"}}
            },
            "ancient_barrow_woods": {
                "name": "The Overgrown Barrow Mound",
                "desc": "A moss-covered earth barrow surrounded by ancient standing stones.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "whispering_glade", "alias": "e"}}
            },
            "fern_gully": {
                "name": "The Deep Fern Gully",
                "desc": "Ferns as tall as men carpet this sheltered ravine.",
                "terrain": "forest",
                "exits": {"west": {"dest_id": "ancient_barrow_woods", "alias": "w"}}
            },
            "beast_master_den": {
                "name": "Lair of the Beast Wardens",
                "desc": "Trained timber wolves and hunting falcons resting beside their elven handlers.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "fern_gully", "alias": "s"}}
            },
            "canopy_pinnacle": {
                "name": "The King's Branch Pinnacle",
                "desc": "The highest branch in Silvanesti, touching the clouds above.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "starlight_observatory", "alias": "d"}}
            },
            "mushroom_circle": {
                "name": "The Fairy Ring Circle",
                "desc": "A perfect ring of red-capped toadstools where playful sprites dance under the moon.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "dryad_grove", "alias": "n"}}
            },
            "silent_pool": {
                "name": "The Mirror Pool",
                "desc": "Completely still water that mirrors the starry sky with pristine clarity.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "mushroom_circle", "alias": "w"}}
            },
            "canopy_west_edge": {
                "name": "Western Forest Threshold",
                "desc": "Where the dense canopy begins to thin toward the outer pine woods.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "blossom_bridge", "alias": "e"}}
            }
        }
    }


# =============================================================================
# ZONE 7: KHAZAD-DUM DWARVEN DEEPS [Level 14-20, 30 Rooms]
# =============================================================================

def build_zone_khazad():
    return {
        "zone_key": "khazad_deeps",
        "zone_name": "The Great Halls of Khazad-Dum",
        "default_terrain": "mountain",
        "base_coords": (0, 30, -10),
        "rooms": {
            "great_gates": {
                "name": "The Adamantine Doors of Durin",
                "desc": "Two colossal stone slabs inlaid with glowing veins of silver ithildin stand set into the mountain wall. Ancient dwarven runes proclaim the realm of Khazad-Dum.",
                "terrain": "mountain",
                "exits": {"north": {"dest_id": "vestibule", "alias": "n"}},
                "npcs": [{"name": "Khazad Gate Warden", "desc": "A dwarven defender in full adamantine plate wielding a heavy war mattock.", "level": 14, "role": "warrior"}]
            },
            "vestibule": {
                "name": "The Grand Vestibule of Kings",
                "desc": "Towering statues of the ancient Dwarven Thanes line this monumental gateway hall, their stone hands resting upon massive two-handed greataxes.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "great_gates", "alias": "s"}, "north": {"dest_id": "pillared_colonnade", "alias": "n"}, "east": {"dest_id": "guard_bastion", "alias": "e"}}
            },
            "guard_bastion": {
                "name": "The Iron Vanguard Bastion",
                "desc": "Murder holes and arrow slits overlook the entrance vestibule. Heavy stone ballistas stand aimed down the main corridor.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "vestibule", "alias": "w"}}
            },
            "pillared_colonnade": {
                "name": "The Thousand-Pillar Colonnade",
                "desc": "A breathtaking cavern of impossible scale. Vast octagonal stone pillars soar into the black heights above, supporting the weight of the entire mountain peak.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "vestibule", "alias": "s"}, "north": {"dest_id": "thane_throne_room", "alias": "n"}, "east": {"dest_id": "dwarven_brewery", "alias": "e"}, "west": {"dest_id": "mithril_mines_entrance", "alias": "w"}},
                "npcs": [{"name": "Khazad Stone Mason", "desc": "A beard-braided artisan checking the stone joins with plumb line and hammer.", "level": 12, "role": "civilian"}]
            },
            "dwarven_brewery": {
                "name": "The Great Vat Brewery of Khazad",
                "desc": "Gigantic copper brewing kettles and oak barrels three times the height of a dwarf. The air is thick with roasted barley, hops, and yeast.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "pillared_colonnade", "alias": "w"}},
                "npcs": [{"name": "Brewmaster Brokk", "desc": "A rotund dwarf with a red foam-stained beard sampling dark stout.", "level": 14, "role": "warrior"}],
                "items": [{"name": "Cask of Khazad Iron Stout", "desc": "A potent, pitch-black dwarven ale renowned for restoring stamina."}]
            },
            "thane_throne_room": {
                "name": "Throne Room of the High Thane",
                "desc": "Raised on seven tiers of basalt stands the Throne of Durin, carved from a single block of raw ruby and obsidian. Banners of hammer and anvil hang from high vaults.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "pillared_colonnade", "alias": "s"}, "north": {"dest_id": "royal_treasury", "alias": "n"}, "down": {"dest_id": "magma_depths", "alias": "d"}},
                "npcs": [{"name": "High Thane Thorgar Stoneheart", "desc": "The sovereign lord of the deeps, clad in runed mithril plate and wielding a thunderous warhammer.", "level": 18, "role": "boss", "danger_tier": "boss"}]
            },
            "royal_treasury": {
                "name": "The Vault of the Star-Stone",
                "desc": "Mounds of cut diamonds, golden chalices, and ingots of pure mithril glisten in warded alcoves behind heavy iron grates.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "thane_throne_room", "alias": "s"}},
                "items": [{"name": "Mithril Bar of Khazad", "desc": "A featherlight bar of gleaming silvery-blue mithril metal."}]
            },
            "mithril_mines_entrance": {
                "name": "Upper Shaft of the Mithril Deeps",
                "desc": "Narrow mine rails curve downward into the richest mineral veins in the known world. Tiny flakes of silver dust glitter in the rock walls.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "pillared_colonnade", "alias": "e"}, "down": {"dest_id": "deep_mine_face", "alias": "d"}},
                "npcs": [{"name": "Mithril Prospector", "desc": "A soot-caked dwarf with a lantern strapped to his iron helm.", "level": 13, "role": "civilian"}]
            },
            "deep_mine_face": {
                "name": "The Deep Excavation Face",
                "desc": "The mine breaks into natural geological fissures where raw mithril crystal clusters protrude from the dark bedrock.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "mithril_mines_entrance", "alias": "u"}, "south": {"dest_id": "mine_flooded_sump", "alias": "s"}},
                "npcs": [{"name": "Cave Troll Excavator", "desc": "A massive, stone-skinned brute enslaved to haul heavy ore blocks.", "level": 15, "role": "warrior"}]
            },
            "mine_flooded_sump": {
                "name": "Subterranean Mine Sump",
                "desc": "Freezing black water pools at the bottom of the deepest shaft.",
                "terrain": "underwater",
                "exits": {"north": {"dest_id": "deep_mine_face", "alias": "n"}}
            },
            "magma_depths": {
                "name": "The Great Core Magma Falls",
                "desc": "A staggering subterranean chasm where rivers of bright orange molten rock cascade hundreds of feet down sheer volcanic basalt.",
                "terrain": "mountain",
                "exits": {"up": {"dest_id": "thane_throne_room", "alias": "u"}, "north": {"dest_id": "magma_bridge", "alias": "n"}},
                "items": [{"name": "Chunk of Volcanic Obsidian", "desc": "Razor-sharp black volcanic glass."}]
            },
            "magma_bridge": {
                "name": "The Narrow Arch of Fire",
                "desc": "A slender stone bridge without railings spanning the boiling lake of magma. Waves of intense thermal heat distort the air.",
                "terrain": "air",
                "exits": {"south": {"dest_id": "magma_depths", "alias": "s"}, "north": {"dest_id": "ancient_forge", "alias": "n"}},
                "npcs": [{"name": "Magma Fiend of the Deep", "desc": "A towering entity composed of hardened slag and roaring magma.", "level": 17, "role": "warrior"}]
            },
            "ancient_forge": {
                "name": "The Core Anvil of Durin",
                "desc": "Harnessing the raw geothermal heat of the mountain's core, this monumental anvil was used to forge the great rings and weapons of legend.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "magma_bridge", "alias": "s"}, "down": {"dest_id": "balrog_lair", "alias": "d"}},
                "npcs": [{"name": "Master Runesmith Balar", "desc": "An ancient runesmith striking white-hot steel with a runed hammer.", "level": 16, "role": "warrior"}],
                "items": [{"name": "Runed Greathammer of Khazad", "desc": "A colossal two-handed hammer engraved with glowing runes of striking."}]
            },
            "balrog_lair": {
                "name": "The Pit of Shadow and Flame",
                "desc": "A scorched abyss of brimstone and eternal darkness where a primordial terror from the first age of the world slumbers.",
                "terrain": "catacombs",
                "exits": {"up": {"dest_id": "ancient_forge", "alias": "u"}},
                "npcs": [{"name": "The Shadow Demon of the Abyss", "desc": "A colossal monstrosity of shadow and living fire wielding a flaming whip.", "level": 20, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Whip of Abyssal Cinders", "desc": "A legendary weapon woven from barbed hellfire."}]
            },
            "hall_ancestors": {
                "name": "The Hall of Ancestral Tombs",
                "desc": "Deep crypts where dwarven warlords are entombed with their weapons and shields.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "pillared_colonnade", "alias": "e"}}
            },
            "armory_iron": {
                "name": "The Ironbreaker Armory",
                "desc": "Heavy dwarven shields, battleaxes, and scale mail hauberks.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "guard_bastion", "alias": "s"}}
            },
            "granite_quarry": {
                "name": "The Subterranean Granite Quarry",
                "desc": "Enormous blocks of grey granite carved with precision geometry.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "mithril_mines_entrance", "alias": "n"}}
            },
            "water_wheel_hub": {
                "name": "The Geothermal Waterwheel Hub",
                "desc": "Huge wooden cogs driving the air ventilation bellows for the deeps.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "dwarven_brewery", "alias": "w"}}
            },
            "sculptors_studio": {
                "name": "The Royal Stonemasons' Studio",
                "desc": "Half-finished marble statues and bas-relief carvings of historic sieges.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "pillared_colonnade", "alias": "s"}}
            },
            "cart_hub_east": {
                "name": "Eastern Mining Depot",
                "desc": "Siding tracks where empty ore carts are serviced and greased.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "mithril_mines_entrance", "alias": "w"}}
            },
            "fungus_pantry": {
                "name": "Deep Fungus Pantries",
                "desc": "Cool caves lined with edible underground truffles and cave mushrooms.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "dwarven_brewery", "alias": "n"}}
            },
            "powder_magazine_khazad": {
                "name": "Mithril Powder Magazine",
                "desc": "Carefully guarded storage for blasting charges.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "mithril_mines_entrance", "alias": "s"}}
            },
            "great_cistern": {
                "name": "The Mountain Core Cistern",
                "desc": "An underground freshwater reservoir filled by alpine glacier runoff.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "water_wheel_hub", "alias": "e"}}
            },
            "crystal_chasm": {
                "name": "Chasm of Gypsum Crystals",
                "desc": "Giant white selenite crystals protruding like sword blades from the walls.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "deep_mine_face", "alias": "w"}}
            },
            "barracks_dwarven": {
                "name": "Iron Vanguard Quarters",
                "desc": "Double-deck stone bunks with fur blankets and weapon racks.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "guard_bastion", "alias": "n"}}
            },
            "council_chamber": {
                "name": "Council of the Seven Clans",
                "desc": "A circular stone table engraved with the map of the mountain range.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "thane_throne_room", "alias": "e"}}
            },
            "smelter_vent": {
                "name": "Upper Smoke Chimney",
                "desc": "Vertical flue exhausting heat toward the mountain summit.",
                "terrain": "mountain",
                "exits": {"down": {"dest_id": "ancient_forge", "alias": "d"}}
            },
            "lower_gallery": {
                "name": "The Forgotten Deep Gallery",
                "desc": "Dark corridors abandoned centuries ago during the Goblin Wars.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "hall_ancestors", "alias": "n"}}
            },
            "obsidian_altar": {
                "name": "Altar of the Stone Father",
                "desc": "A block of black obsidian dedicated to the creator of the dwarven race.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "council_chamber", "alias": "w"}}
            },
            "vault_runes": {
                "name": "The Runic Archive Vault",
                "desc": "Engraved copper tablets preserving the language and genealogy of Khazad.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "royal_treasury", "alias": "s"}}
            }
        }
    }


# =============================================================================
# ZONE 8: KALIM DESERT & PYRAMID OF THE SUN [Level 12-17, 30 Rooms]
# =============================================================================

def build_zone_kalim():
    return {
        "zone_key": "kalim_desert",
        "zone_name": "The Shifting Dunes of Kalim Desert",
        "default_terrain": "field",
        "base_coords": (0, -35, 0),
        "rooms": {
            "caravan_post": {
                "name": "The Silk Road Caravanserai",
                "desc": "A walled sandstone compound with arched gates. Camels resting by drinking troughs, spice merchants haggling under canvas awnings, and water jars sweating in the dry heat.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "desert_gateway", "alias": "s"}},
                "npcs": [{"name": "Caravan Merchant Tariq", "desc": "A turbanned nomad merchant with keen eyes and bags of saffron.", "level": 11, "role": "civilian"}]
            },
            "desert_gateway": {
                "name": "Gateway to the Golden Dunes",
                "desc": "The cobbled road ends abruptly, disappearing into the rolling sea of golden sand that stretches toward the burning southern horizon.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "caravan_post", "alias": "n"}, "south": {"dest_id": "great_dune_sea", "alias": "s"}, "east": {"dest_id": "oasis_emerald", "alias": "e"}},
                "npcs": [{"name": "Nomad Bedouin Scout", "desc": "A desert tracker veiled in dark blue linen mounted on a swift camel.", "level": 12, "role": "rogue"}]
            },
            "oasis_emerald": {
                "name": "The Mirage Oasis of Kalim",
                "desc": "A tranquil haven in the desert. Date palms sway around a pool of crystal-clear spring water reflecting the azure sky.",
                "terrain": "water_swim",
                "exits": {"west": {"dest_id": "desert_gateway", "alias": "w"}},
                "items": [{"name": "Flask of Sweet Oasis Water", "desc": "Refreshing cold spring water that quenches desert thirst."}]
            },
            "great_dune_sea": {
                "name": "The Crest of the Great Sand Dune",
                "desc": "Fine, scorching golden sand shifts under your boots. The desert wind sculpts ripples across towering dunes that look like ocean waves frozen in stone.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "desert_gateway", "alias": "n"}, "south": {"dest_id": "sphinx_avenue", "alias": "s"}, "west": {"dest_id": "sandstorm_ridge", "alias": "w"}},
                "npcs": [{"name": "Desert Sandstalker", "desc": "A predatory reptilian quadruped with scales that match the dune sands.", "level": 13, "role": "warrior"}]
            },
            "sandstorm_ridge": {
                "name": "The Howling Dust Ridge",
                "desc": "Blinding sand grains whip in howling gusts that obscure vision and strip paint from pack saddles.",
                "terrain": "field",
                "exits": {"east": {"dest_id": "great_dune_sea", "alias": "e"}}
            },
            "sphinx_avenue": {
                "name": "Avenue of the Jackal Sphinxes",
                "desc": "Weathered sandstone statues of jackal-headed guardians line a forgotten processional road leading toward a massive step pyramid.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "great_dune_sea", "alias": "n"}, "south": {"dest_id": "pyramid_threshold", "alias": "s"}},
                "npcs": [{"name": "Sand Golem Guardian", "desc": "A hulking construct formed of compacted sand held together by ancient solar magic.", "level": 14, "role": "warrior"}]
            },
            "pyramid_threshold": {
                "name": "Threshold of the Sunken Pyramid",
                "desc": "Two colossal statues of a seated Pharaoh flank the entrance to the pyramid. The air shifts from blazing desert heat to chilled tomb stone.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "sphinx_avenue", "alias": "n"}, "south": {"dest_id": "pyramid_grand_hall", "alias": "s"}}
            },
            "pyramid_grand_hall": {
                "name": "Grand Hall of the Sun God",
                "desc": "Walls covered in colorful hieroglyphics depict the soul's journey across the underworld. Golden sun disks reflect light down long corridors.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "pyramid_threshold", "alias": "n"}, "south": {"dest_id": "burial_chamber", "alias": "s"}, "east": {"dest_id": "chamber_anubis", "alias": "e"}, "west": {"dest_id": "labyrinth_bronze", "alias": "w"}},
                "npcs": [{"name": "Tomb Guardian Mummy", "desc": "An embalmed corpse wrapped in linen shrouds, moving with dreadful tireless purpose.", "level": 15, "role": "warrior"}]
            },
            "chamber_anubis": {
                "name": "Sanctuary of the Jackal Lord",
                "desc": "A black granite statue of the jackal deity holding the scales of judgment. A golden feather rests on one balance pan.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "pyramid_grand_hall", "alias": "w"}},
                "items": [{"name": "Golden Ankh of the Sun", "desc": "A heavy golden talisman radiating warm abjuration energy."}]
            },
            "labyrinth_bronze": {
                "name": "Labyrinth of the Polished Mirrors",
                "desc": "Sheets of polished bronze line the walls, designed to channel sunlight deep into the subterranean passages.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "pyramid_grand_hall", "alias": "e"}, "south": {"dest_id": "canopic_treasury", "alias": "s"}}
            },
            "canopic_treasury": {
                "name": "The Royal Canopic Treasury",
                "desc": "Gold-plated alabaster jars containing royal viscera sit surrounded by lapis lazuli beads, ebony chests, and ceremonial daggers.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "labyrinth_bronze", "alias": "n"}}
            },
            "burial_chamber": {
                "name": "The Golden Tomb of Pharaoh Akhen-Ra",
                "desc": "In the center of this domed chamber rests a massive sarcophagus of solid beaten gold, surrounded by golden chariots, royal scepters, and offerings of honey.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "pyramid_grand_hall", "alias": "n"}},
                "npcs": [{"name": "Pharaoh Akhen-Ra", "desc": "The resurrected solar monarch, clutching the crook and flail, his eyes burning with golden solar fire.", "level": 17, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Solar Flail of the Pharaoh", "desc": "A golden ceremonial weapon that strikes with the searing brilliance of the noon sun."}]
            },
            "desert_canyon": {
                "name": "The Sun-Bleached Canyon",
                "desc": "Towering red sandstone walls carved by ancient flash floods.",
                "terrain": "mountain",
                "exits": {"east": {"dest_id": "great_dune_sea", "alias": "e"}}
            },
            "bedouin_encampment": {
                "name": "Nomad Goat-Hair Tents",
                "desc": "Low black tents woven from goat hair pitched in the lee of a rocky bluff.",
                "terrain": "field",
                "exits": {"south": {"dest_id": "desert_canyon", "alias": "s"}}
            },
            "quicksand_sink": {
                "name": "The Deceptive Silt Sink",
                "desc": "Dry powdery silt that swallows boots like water.",
                "terrain": "marsh",
                "exits": {"west": {"dest_id": "great_dune_sea", "alias": "w"}}
            },
            "sandworm_hollow": {
                "name": "Territory of the Burrower",
                "desc": "Massive circular craters where the sand shifts and trembles from movements deep below.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "quicksand_sink", "alias": "n"}},
                "npcs": [{"name": "Great Sand Dune Worm", "desc": "A segmented leviathan with concentric rows of triangular teeth.", "level": 16, "role": "boss", "danger_tier": "boss"}]
            },
            "ruined_watchtower_desert": {
                "name": "Crumbling Adobe Watchtower",
                "desc": "A sun-dried adobe tower overlooking the ancient caravan route.",
                "terrain": "city",
                "exits": {"east": {"dest_id": "desert_gateway", "alias": "e"}}
            },
            "desert_spring": {
                "name": "Hidden Rocky Spring",
                "desc": "A cool trickle of water emerging from a crack in red sandstone.",
                "terrain": "water_swim",
                "exits": {"south": {"dest_id": "bedouin_encampment", "alias": "s"}}
            },
            "salt_flats": {
                "name": "The Blinding Salt Basin",
                "desc": "A dry lake bed encrusted with brilliant white salt crusts.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "great_dune_sea", "alias": "n"}}
            },
            "pyramid_false_crypt": {
                "name": "The False Sarcophagus Vault",
                "desc": "A decoy tomb rigged with falling stone block traps to fool grave robbers.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "pyramid_grand_hall", "alias": "w"}}
            },
            "sun_priest_sanctuary": {
                "name": "Sanctuary of the Sun Priests",
                "desc": "Stone beds where priests of the solar cult slept before rituals.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "chamber_anubis", "alias": "e"}}
            },
            "shrine_bast": {
                "name": "Shrine of the Cat Goddess",
                "desc": "Bronze cat statuettes and offering dishes filled with sweet milk.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "pyramid_grand_hall", "alias": "s"}}
            },
            "dune_ridge_south": {
                "name": "Southern Dune Escarpment",
                "desc": "A sheer drop where the desert drops hundreds of feet into scrublands.",
                "terrain": "field",
                "exits": {"north": {"dest_id": "great_dune_sea", "alias": "n"}}
            },
            "buried_temple_gate": {
                "name": "Sand-Choked Temple Arch",
                "desc": "Columns buried up to their capitals in drifting sand.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "sphinx_avenue", "alias": "s"}}
            },
            "scorpion_pit": {
                "name": "The Sunken Scorpion Den",
                "desc": "A sandy pit crawling with golden emperor scorpions.",
                "terrain": "field",
                "exits": {"west": {"dest_id": "sandstorm_ridge", "alias": "w"}}
            },
            "hieroglyph_scriptorium": {
                "name": "The Royal Scribe's Archive",
                "desc": "Papyrus scrolls preserved in terracotta jars.",
                "terrain": "catacombs",
                "exits": {"north": {"dest_id": "pyramid_grand_hall", "alias": "n"}}
            },
            "sun_boat_chamber": {
                "name": "The Solar Barge Hall",
                "desc": "A full-sized wooden ceremonial river barge intended to sail the stars with the pharaoh.",
                "terrain": "catacombs",
                "exits": {"east": {"dest_id": "burial_chamber", "alias": "e"}}
            },
            "tomb_weighing_hall": {
                "name": "Hall of the Heart's Weighing",
                "desc": "Stone murals of the underworld deities judging mortal souls.",
                "terrain": "catacombs",
                "exits": {"west": {"dest_id": "chamber_anubis", "alias": "w"}}
            },
            "dune_crest_west": {
                "name": "Western Horizon Dunes",
                "desc": "The sun sets in blood-red splendor over the desert expanse.",
                "terrain": "field",
                "exits": {"east": {"dest_id": "sandstorm_ridge", "alias": "e"}}
            },
            "desert_well": {
                "name": "The Deep Caravan Well",
                "desc": "A circular stone well with a creaking wooden bucket windlass.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "caravan_post", "alias": "n"}}
            }
        }
    }


# =============================================================================
# ZONE 9: HONSHU & JADE MOUNTAIN [Level 15-22+, 30 Rooms]
# =============================================================================

def build_zone_honshu():
    return {
        "zone_key": "honshu_realm",
        "zone_name": "The Realm of Honshu & Jade Mountain",
        "default_terrain": "city",
        "base_coords": (-35, -20, 0),
        "rooms": {
            "jade_harbor": {
                "name": "Honshu Harbor of the Thousand Lanterns",
                "desc": "An ornate harbor where red-lacquered wooden piers extend into peaceful turquoise waters. Stone lanterns line the seawall, casting warm amber reflections across the bay.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "bamboo_path", "alias": "n"}, "east": {"dest_id": "tea_house", "alias": "e"}},
                "npcs": [{"name": "Honshu Harbor Guard", "desc": "A disciplined warrior in black and gold lamellar armor wielding a naginata.", "level": 15, "role": "warrior"}]
            },
            "tea_house": {
                "name": "The Cherry Blossom Tea House",
                "desc": "Tatami mats, low lacquered tables, and shoji screens overlooking a koi pond. The aroma of freshly whisked matcha tea and incense fills the air.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "jade_harbor", "alias": "w"}},
                "items": [{"name": "Ceramic Bowl of Green Matcha", "desc": "Frothy green tea served in a fine ceramic bowl."}]
            },
            "bamboo_path": {
                "name": "The Whispering Bamboo Grove",
                "desc": "Towering stalks of emerald bamboo rustle gently in the sea breeze. A mossy flagstone path leads toward the mist-shrouded Jade Mountain.",
                "terrain": "forest",
                "exits": {"south": {"dest_id": "jade_harbor", "alias": "s"}, "north": {"dest_id": "torii_gate", "alias": "n"}, "west": {"dest_id": "waterfall_bridge", "alias": "w"}},
                "npcs": [{"name": "Shadow Shinobi", "desc": "A masked ninja armed with dual kunai and shuriken.", "level": 16, "role": "rogue"}]
            },
            "waterfall_bridge": {
                "name": "Arched Red Bridge over the Rapids",
                "desc": "A graceful arched wooden bridge painted vermilion spanning a roaring mountain waterfall.",
                "terrain": "mountain",
                "exits": {"east": {"dest_id": "bamboo_path", "alias": "e"}}
            },
            "torii_gate": {
                "name": "The Great Vermilion Torii Gate",
                "desc": "A towering ceremonial wooden gate marking the boundary between the mortal realm and the sacred grounds of the Jade Mountain.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "bamboo_path", "alias": "s"}, "north": {"dest_id": "monastery_courtyard", "alias": "n"}},
                "npcs": [{"name": "Sohei War Monk", "desc": "A monk in white robes and straw sandals wielding an iron-ringed staff.", "level": 17, "role": "warrior"}]
            },
            "monastery_courtyard": {
                "name": "Courtyard of the Five Tigers",
                "desc": "A peaceful Zen gravel garden raked in concentric wave patterns around ancient moss-covered boulders. Monks practice empty-hand katas in silence.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "torii_gate", "alias": "s"}, "north": {"dest_id": "dojo_iron_palm", "alias": "n"}, "east": {"dest_id": "seven_tier_pagoda", "alias": "e"}},
                "npcs": [{"name": "Tiger Style Initiate", "desc": "A martial artist striking wooden practice dummies with blistering speed.", "level": 16, "role": "warrior"}]
            },
            "dojo_iron_palm": {
                "name": "The Grand Dojo of the Iron Palm",
                "desc": "Polished cedar floorboards where the masters of Honshu train in lethal unarmed strikes and ki manipulation.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "monastery_courtyard", "alias": "s"}, "north": {"dest_id": "grandmaster_hall", "alias": "n"}},
                "npcs": [{"name": "Dojo Sensei Ryu", "desc": "A battle-hardened master of martial arts with calloused hands of stone.", "level": 18, "role": "warrior"}]
            },
            "grandmaster_hall": {
                "name": "Sanctum of Grand Master Kenshin",
                "desc": "A tranquil chamber with paper lanterns and painted silk scrolls of soaring dragons. Incense burns upon an altar of dark cedar.",
                "terrain": "indoors",
                "exits": {"south": {"dest_id": "dojo_iron_palm", "alias": "s"}},
                "npcs": [{"name": "Grand Master Kenshin", "desc": "A legendary martial artist whose strikes channel the thunderous fury of the storm.", "level": 21, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Ki-Infused Silk Wraps", "desc": "Hand wraps embroidered with golden dragon runes that augment unarmed ripostes."}]
            },
            "seven_tier_pagoda": {
                "name": "Base of the Seven-Tier Pagoda",
                "desc": "Curved tile roofs and carved wooden dragons jutting from the eaves. A steep spiral staircase ascends into the heights.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "monastery_courtyard", "alias": "w"}, "up": {"dest_id": "pagoda_apex", "alias": "u"}}
            },
            "pagoda_apex": {
                "name": "Pagoda of the Storms Apex",
                "desc": "The highest balcony of the pagoda, open to the mountain winds. Below lies the entire archipelago of Honshu.",
                "terrain": "air",
                "exits": {"down": {"dest_id": "seven_tier_pagoda", "alias": "d"}, "north": {"dest_id": "dragon_sanctuary", "alias": "n"}}
            },
            "dragon_sanctuary": {
                "name": "Sanctuary of the Celestial Jade Dragon",
                "desc": "Perched upon the highest mist-shrouded peak of the mountain sits an open-air circular altar of pure green jade overlooking the endless ocean.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "pagoda_apex", "alias": "s"}},
                "npcs": [{"name": "The Celestial Jade Dragon", "desc": "An ancient, serpentine dragon with scales of shimmering emerald jade and whiskers of lightning.", "level": 25, "role": "boss", "danger_tier": "boss"}],
                "items": [{"name": "Orb of the Jade Dragon", "desc": "A flawless sphere of celestial jade radiating boundless arcane vitality."}]
            },
            "koi_pond_garden": {
                "name": "The Lotus & Koi Garden",
                "desc": "Red and gold carp glide peacefully under broad green lily pads.",
                "terrain": "water_swim",
                "exits": {"north": {"dest_id": "tea_house", "alias": "n"}}
            },
            "pottery_workshop": {
                "name": "Honshu Ceramic Kiln",
                "desc": "Potter's wheels and wood-fired kilns crafting fine porcelain.",
                "terrain": "indoors",
                "exits": {"west": {"dest_id": "tea_house", "alias": "w"}}
            },
            "samurai_barracks": {
                "name": "The Guard Guard Barracks of Honshu",
                "desc": "Suits of lacquered armor mounted on wooden display stands.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "jade_harbor", "alias": "e"}}
            },
            "weaponsmith_forge_honshu": {
                "name": "Master Swordsmith's Hearth",
                "desc": "Folded steel katanas quenching in water troughs.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "samurai_barracks", "alias": "n"}},
                "items": [{"name": "Folded Steel Katana of Honshu", "desc": "A curved, razor-sharp blade with a wave-pattern hamon line."}]
            },
            "stone_lantern_walk": {
                "name": "The Path of Mossy Lanterns",
                "desc": "A stone stair through cedar woods lit by moss-covered lanterns.",
                "terrain": "mountain",
                "exits": {"west": {"dest_id": "bamboo_path", "alias": "w"}}
            },
            "hot_springs": {
                "name": "The Mountain Onsen",
                "desc": "Geothermal natural hot springs steaming gently in the mountain air.",
                "terrain": "water_swim",
                "exits": {"east": {"dest_id": "stone_lantern_walk", "alias": "e"}}
            },
            "pine_ridge": {
                "name": "The Windy Pine Ridge",
                "desc": "Twisted black pines clinging tenaciously to the cliff faces.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "torii_gate", "alias": "s"}}
            },
            "shrine_kitsune": {
                "name": "Shrine of the White Fox",
                "desc": "Statues of foxes holding golden keys in their mouths.",
                "terrain": "forest",
                "exits": {"north": {"dest_id": "pine_ridge", "alias": "n"}}
            },
            "bell_pavilion": {
                "name": "The Bronze Peace Bell Pavilion",
                "desc": "A huge bronze temple bell struck with a swinging cedar log.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "monastery_courtyard", "alias": "w"}}
            },
            "meditation_cave": {
                "name": "The Hermit's Meditation Cave",
                "desc": "A quiet natural grotto with a single woven straw meditation cushion.",
                "terrain": "catacombs",
                "exits": {"south": {"dest_id": "bell_pavilion", "alias": "s"}}
            },
            "library_scrolls": {
                "name": "The Library of Ancient Katas",
                "desc": "Scroll cabinets containing secret techniques of sword and staff.",
                "terrain": "indoors",
                "exits": {"east": {"dest_id": "dojo_iron_palm", "alias": "e"}}
            },
            "clifftop_archery_range": {
                "name": "The Kyudo Archery Range",
                "desc": "Long straw targets set against a backdrop of rolling ocean fog.",
                "terrain": "city",
                "exits": {"west": {"dest_id": "monastery_courtyard", "alias": "w"}}
            },
            "monastery_kitchen": {
                "name": "The Temple Kitchens",
                "desc": "Steaming bamboo steamers of rice and pots of vegetable broth.",
                "terrain": "indoors",
                "exits": {"north": {"dest_id": "monastery_courtyard", "alias": "n"}}
            },
            "bamboo_hollow": {
                "name": "Deep Bamboo Clearing",
                "desc": "Sunlight dapples the forest floor where wild pheasants forage.",
                "terrain": "forest",
                "exits": {"east": {"dest_id": "bamboo_path", "alias": "e"}}
            },
            "coastal_cliffs_honshu": {
                "name": "The Dragon's Tooth Sea Cliffs",
                "desc": "Jagged basalt spires rising out of the foaming surf.",
                "terrain": "mountain",
                "exits": {"south": {"dest_id": "jade_harbor", "alias": "s"}}
            },
            "fisherman_dock_honshu": {
                "name": "The Cormorant Fishing Docks",
                "desc": "Small wooden skiffs where fishermen train cormorant birds to catch river fish.",
                "terrain": "city",
                "exits": {"north": {"dest_id": "jade_harbor", "alias": "n"}}
            },
            "mountain_pass_mist": {
                "name": "The Misty Mountain Pass",
                "desc": "Cloud banks drift across the stone path leading to the high shrine.",
                "terrain": "mountain",
                "exits": {"down": {"dest_id": "seven_tier_pagoda", "alias": "d"}}
            },
            "zen_rock_garden": {
                "name": "The Inner Garden of Stillness",
                "desc": "Seven standing stones placed in silent contemplation.",
                "terrain": "city",
                "exits": {"south": {"dest_id": "grandmaster_hall", "alias": "s"}}
            },
            "dragon_pool": {
                "name": "The Dragon's Eye Pool",
                "desc": "Deep green water beneath the summit altar reflecting the clouds.",
                "terrain": "water_swim",
                "exits": {"down": {"dest_id": "dragon_sanctuary", "alias": "d"}}
            }
        }
    }


# =============================================================================
# MARITIME ROUTE: JADE DRAGON JUNK
# =============================================================================

def register_honshu_ferry_routes():
    """
    Registers the 5th major maritime ferry route:
    'The Jade Dragon Junk' connecting Eldoria South Docks,
    Old Praxis Imperial Pier, and Honshu Jade Harbor.
    """
    junk_route = {
        "key": "jade_junk",
        "name": "The Jade Dragon Junk",
        "operator": "Captain Toshiro Jin",
        "operator_title": "Grand Navigator of the Eastern Sea",
        "ports": ["south_docks", "praxis_province_praxis_harbor", "honshu_realm_jade_harbor", "jade_harbor"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
            "honshu_realm_jade_harbor": "Honshu Harbor of the Thousand Lanterns",
            "jade_harbor": "Honshu Harbor of the Thousand Lanterns"
        },
        "fares": {
            ("south_docks", "honshu_realm_jade_harbor"): 80,   # 8 silver
            ("honshu_realm_jade_harbor", "south_docks"): 80,
            ("praxis_province_praxis_harbor", "honshu_realm_jade_harbor"): 50, # 5 silver
            ("honshu_realm_jade_harbor", "praxis_province_praxis_harbor"): 50,
            ("south_docks", "jade_harbor"): 80,
            ("jade_harbor", "south_docks"): 80,
            ("praxis_province_praxis_harbor", "jade_harbor"): 50,
            ("jade_harbor", "praxis_province_praxis_harbor"): 50
        },
        "desc": "A traditional Eastern junk with three crimson battened sails, carved dragon prow, and lacquered ironwood hull.",
        "deck_key": "jade_junk_deck"
    }
    sailing.FERRY_ROUTES["jade_junk"] = junk_route
    return junk_route


# =============================================================================
# MAIN EXPANSION PART 2 RUNNER
# =============================================================================

def run_bulk_ingestion_part2(clean_existing=True):
    """
    Executes bulk ingestion of Part 2 zones (120 rooms) with:
    - Silvanesti Elven Canopy
    - Khazad-Dum Dwarven Deeps
    - Kalim Desert & Sun Pyramid
    - Honshu & Jade Mountain
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
        build_zone_silvanesti,
        build_zone_khazad,
        build_zone_kalim,
        build_zone_honshu
    ]

    # Overland Anchor Mapping: (zone_key, zone_room_id, world_room_key, dir_to_zone, dir_to_world)
    ANCHOR_MAPPINGS = [
        ("silvanesti_canopy", "canopy_ascent", "deep_woods", "east", "west"),
        ("khazad_deeps", "great_gates", "frostfang_pass", "north", "south"),
        ("kalim_desert", "caravan_post", "bazaar", "south", "north")
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

    # 3. Create Overland Anchors
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

    # 4. Register Jade Dragon Junk Maritime Route & Weather Deck
    junk_deck = find_room_by_key("jade_junk_deck")
    if not junk_deck:
        junk_deck = create_object(Room, key="The Jade Dragon Junk - Weather Deck", tags=[TAG_WORLD])
        junk_deck.tags.add("jade_junk_deck", category="room_key")
        junk_deck.tags.add("honshu_realm", category="zone")
        junk_deck.db.room_key = "jade_junk_deck"
        junk_deck.db.desc = (
            "You stand upon the broad lacquered ironwood weather deck of the imperial junk. "
            "Three soaring red-battened canvas sails billow in the ocean gale. A fierce golden dragon "
            "figurehead looks out from the bow over the surging waves."
        )
        junk_deck.db.zone = "Eastern Ocean"
        junk_deck.db.terrain = "city"
        junk_deck.db.coords = (-20, -30, 0)
        report["rooms_created"] += 1

    register_honshu_ferry_routes()
    report["ferry_routes_added"].append("The Jade Dragon Junk (south_docks <-> praxis_harbor <-> honshu_jade_harbor)")

    return report

