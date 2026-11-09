"""
Nightmare LPmud Sailing, Ferry & Municipal Taxation System for Evennia
Features:
1. Multi-Route Ferry Vessels & Nautical Transit
2. Nightmare LPmud Currency Fare Collection (Copper/Silver/Gold with auto-change)
3. Municipal Tax Deduction into Royal City Coffers
4. Atmospheric Voyage Sequences to Remote Islands and Islets
"""

import time
from evennia.utils import delay
from evennia.objects.models import ObjectDB
from world.nightmare_core import init_nightmare_character

# =============================================================================
# MUNICIPAL COFFERS & TARIFF SYSTEM
# =============================================================================

DEFAULT_COFFERS = {
    "copper": 250,
    "silver": 120,
    "gold": 45,
    "tariffs_collected_copper": 0
}

def get_bank_object():
    """Finds the Royal Bank of Eldoria room or object to anchor coffers."""
    return ObjectDB.objects.filter(db_key__icontains="Royal Bank of Eldoria").first()


def get_city_coffers():
    """Retrieves the current municipal coffer balance."""
    bank = get_bank_object()
    if bank:
        if not bank.db.city_coffers:
            bank.db.city_coffers = dict(DEFAULT_COFFERS)
        return bank.db.city_coffers
    return dict(DEFAULT_COFFERS)


def deposit_municipal_tax(tax_copper):
    """Deposits ferry tariff tax into Eldoria's royal treasury."""
    bank = get_bank_object()
    coffers = get_city_coffers()
    coffers["copper"] += tax_copper
    coffers["tariffs_collected_copper"] = coffers.get("tariffs_collected_copper", 0) + tax_copper

    # Convert copper to silver/gold in coffers
    if coffers["copper"] >= 100:
        added_gold = coffers["copper"] // 100
        coffers["gold"] += added_gold
        coffers["copper"] %= 100
    if coffers["copper"] >= 10:
        added_silver = coffers["copper"] // 10
        coffers["silver"] += added_silver
        coffers["copper"] %= 10

    if bank:
        bank.db.city_coffers = coffers
    return coffers


def format_copper_as_currency(copper_amt):
    """Formats an amount in copper into gold, silver, and copper."""
    gold = copper_amt // 100
    rem = copper_amt % 100
    silver = rem // 10
    copper = rem % 10
    parts = []
    if gold > 0:
        parts.append(f"|y{gold} Gold|n")
    if silver > 0:
        parts.append(f"|w{silver} Silver|n")
    if copper > 0 or not parts:
        parts.append(f"|r{copper} Copper|n")
    return ", ".join(parts)


def total_player_copper(char):
    """Calculates total copper wealth on hand for character."""
    coins = char.db.coins or {"copper": 0, "silver": 0, "gold": 0}
    return coins.get("copper", 0) + (coins.get("silver", 0) * 10) + (coins.get("gold", 0) * 100)


def deduct_fare(char, cost_copper):
    """
    Deducts cost_copper from character's coins, auto-converting gold/silver
    into proper change.
    """
    total = total_player_copper(char)
    if total < cost_copper:
        return False, f"You cannot afford the fare! (Requires {format_copper_as_currency(cost_copper)}, you have {format_copper_as_currency(total)})"

    rem = total - cost_copper
    new_gold = rem // 100
    rem %= 100
    new_silver = rem // 10
    new_copper = rem % 10
    char.db.coins = {"gold": new_gold, "silver": new_silver, "copper": new_copper}
    return True, f"Paid {format_copper_as_currency(cost_copper)} (Change returned. New balance: {format_copper_as_currency(total - cost_copper)})."


# =============================================================================
# FERRY ROUTES & VESSELS DEFINITION
# =============================================================================

FERRY_ROUTES = {
    "salt_spit": {
        "key": "salt_spit",
        "name": "The Salt-Spit Sea Ferry",
        "operator": "Ferrywoman Maeve",
        "operator_title": "Master Harbor Pilot",
        "ports": ["south_docks", "isle_harbor", "dead_mans_cove"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "isle_harbor": "Corsair's Anchorage (Isle of Serpents)",
            "dead_mans_cove": "Dead Man's Cove (Smuggler's Coast)"
        },
        "fares": {
            ("south_docks", "isle_harbor"): 50,  # 5 silver
            ("isle_harbor", "south_docks"): 50,
            ("south_docks", "dead_mans_cove"): 20, # 2 silver
            ("dead_mans_cove", "south_docks"): 20,
            ("dead_mans_cove", "isle_harbor"): 35,
            ("isle_harbor", "dead_mans_cove"): 35
        },
        "desc": "A rugged two-masted caravel with salt-stained oak planks and billowing canvas.",
        "deck_key": "salt_spit_deck"
    },
    "misty_skiff": {
        "key": "misty_skiff",
        "name": "The Misty Flatboat",
        "operator": "Old Riverman Jacques",
        "operator_title": "Misty River Ferryman",
        "ports": ["misty_river", "silt_islet"],
        "port_names": {
            "misty_river": "Misty River Crossing",
            "silt_islet": "Whispering Silt Islet"
        },
        "fares": {
            ("misty_river", "silt_islet"): 15, # 1 silver 5 copper
            ("silt_islet", "misty_river"): 15
        },
        "desc": "A sturdy flat-bottomed cedar punt ferry steered with an iron-shod push pole.",
        "deck_key": "misty_skiff_deck"
    },
    "corsair_longboat": {
        "key": "corsair_longboat",
        "name": "The Corsair's Longboat",
        "operator": "Helmsman Joshua",
        "operator_title": "Island Coast Pilot",
        "ports": ["isle_harbor", "isle_cove", "isle_wreck"],
        "port_names": {
            "isle_harbor": "Corsair's Anchorage",
            "isle_cove": "Smuggler's Lagoon",
            "isle_wreck": "The Leviathan's Graveyard"
        },
        "fares": {
            ("isle_harbor", "isle_cove"): 25,
            ("isle_cove", "isle_harbor"): 25,
            ("isle_harbor", "isle_wreck"): 30,
            ("isle_wreck", "isle_harbor"): 30,
            ("isle_cove", "isle_wreck"): 20,
            ("isle_wreck", "isle_cove"): 20
        },
        "desc": "A swift, nimble rowed longboat fitted with muffled oarlocks and dark waterproof canvas.",
        "deck_key": "corsair_longboat_deck"
    },
    "praxis_galleon": {
        "key": "praxis_galleon",
        "name": "The Royal Galleon 'Sea Phantom'",
        "operator": "Commodore Ethan Hawke",
        "operator_title": "Grand Admiral of the Royal Fleet",
        "ports": ["south_docks", "praxis_province_praxis_harbor", "midgaard_district_midgaard_port"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
            "midgaard_district_midgaard_port": "Midgaard Royal Wharf"
        },
        "fares": {
            ("south_docks", "praxis_province_praxis_harbor"): 60,
            ("praxis_province_praxis_harbor", "south_docks"): 60,
            ("south_docks", "midgaard_district_midgaard_port"): 40,
            ("midgaard_district_midgaard_port", "south_docks"): 40,
            ("praxis_province_praxis_harbor", "midgaard_district_midgaard_port"): 50,
            ("midgaard_district_midgaard_port", "praxis_province_praxis_harbor"): 50
        },
        "desc": "A magnificent three-deck imperial galleon with gilded figurehead, black oak hull, and triple rows of bronze cannons.",
        "deck_key": "praxis_galleon_deck"
    },
    "jade_junk": {
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
            ("south_docks", "honshu_realm_jade_harbor"): 80,
            ("honshu_realm_jade_harbor", "south_docks"): 80,
            ("praxis_province_praxis_harbor", "honshu_realm_jade_harbor"): 50,
            ("honshu_realm_jade_harbor", "praxis_province_praxis_harbor"): 50,
            ("south_docks", "jade_harbor"): 80,
            ("jade_harbor", "south_docks"): 80,
            ("praxis_province_praxis_harbor", "jade_harbor"): 50,
            ("jade_harbor", "praxis_province_praxis_harbor"): 50
        },
        "desc": "A traditional Eastern junk with three crimson battened sails, carved dragon prow, and lacquered ironwood hull.",
        "deck_key": "jade_junk_deck"
    },
    "nautilus_sub": {
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
            ("south_docks", "atlantea_depths_atlantea_sea_gate"): 90,
            ("atlantea_depths_atlantea_sea_gate", "south_docks"): 90,
            ("dead_mans_cove", "atlantea_depths_atlantea_sea_gate"): 60,
            ("atlantea_depths_atlantea_sea_gate", "dead_mans_cove"): 60,
            ("south_docks", "atlantea_sea_gate"): 90,
            ("atlantea_sea_gate", "south_docks"): 90,
            ("dead_mans_cove", "atlantea_sea_gate"): 60,
            ("atlantea_sea_gate", "dead_mans_cove"): 60
        },
        "desc": "A reinforced brass-plated submarine sphere with thick quartz viewports, air compressors, and searchlights.",
        "deck_key": "nautilus_deck"
    },
    "black_skull_ship": {
        "key": "black_skull_ship",
        "name": "The Black Skull Corsair Frigate",
        "operator": "Quartermaster Flint",
        "operator_title": "First Mate of the Brotherhood",
        "ports": ["dead_mans_cove", "isle_cove", "tortuga_haven_tortuga_docks", "tortuga_docks"],
        "port_names": {
            "dead_mans_cove": "Dead Man's Cove (Smuggler's Coast)",
            "isle_cove": "Smuggler's Lagoon (Isle of Serpents)",
            "tortuga_haven_tortuga_docks": "The Weathered Wharves of Tortuga",
            "tortuga_docks": "The Weathered Wharves of Tortuga"
        },
        "fares": {
            ("dead_mans_cove", "tortuga_haven_tortuga_docks"): 45,
            ("tortuga_haven_tortuga_docks", "dead_mans_cove"): 45,
            ("isle_cove", "tortuga_haven_tortuga_docks"): 35,
            ("tortuga_haven_tortuga_docks", "isle_cove"): 35,
            ("dead_mans_cove", "tortuga_docks"): 45,
            ("tortuga_docks", "dead_mans_cove"): 45,
            ("isle_cove", "tortuga_docks"): 35,
            ("tortuga_docks", "isle_cove"): 35
        },
        "desc": "A menacing black-hulled 24-gun frigate flying a tattered black flag with crimson skull and crossed cutlasses.",
        "deck_key": "black_skull_deck"
    },
    "zephyr_skyship": {
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
            ("south_docks", "cloud_gateway"): 110,
            ("cloud_gateway", "south_docks"): 110,
            ("praxis_province_praxis_harbor", "cloud_gateway"): 95,
            ("cloud_gateway", "praxis_province_praxis_harbor"): 95,
            ("south_docks", "praxis_province_praxis_harbor"): 40,
            ("praxis_province_praxis_harbor", "south_docks"): 40
        },
        "desc": "A majestic dual-envelope dirigible with brass rudders, glowing arcane aether-turbines, and varnished mahogany flying decks.",
        "deck_key": "zephyr_skyship_deck"
    },
    "avalon_barge": {
        "key": "avalon_barge",
        "name": 'The Avalon Mist-Barge "Nimue\'s Blessing"',
        "operator": "Nimue the Lake Maiden",
        "operator_title": "Enchantress of the Sacred Waters",
        "ports": ["south_docks", "praxis_province_praxis_harbor", "camelot_realm_avalon_ferry_dock", "avalon_dock"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
            "camelot_realm_avalon_ferry_dock": "The Shrouded Pier of Avalon",
            "avalon_dock": "The Shrouded Pier of Avalon"
        },
        "fares": {
            ("south_docks", "camelot_realm_avalon_ferry_dock"): 65,
            ("camelot_realm_avalon_ferry_dock", "south_docks"): 65,
            ("praxis_province_praxis_harbor", "camelot_realm_avalon_ferry_dock"): 55,
            ("camelot_realm_avalon_ferry_dock", "praxis_province_praxis_harbor"): 55,
            ("south_docks", "avalon_dock"): 65,
            ("avalon_dock", "south_docks"): 65,
            ("praxis_province_praxis_harbor", "avalon_dock"): 55,
            ("avalon_dock", "praxis_province_praxis_harbor"): 55
        },
        "desc": "A graceful white-wood barge propelled silently through enchanted lake mists by silver oars.",
        "deck_key": "avalon_barge_deck"
    },
    "ankh_barge": {
        "key": "ankh_barge",
        "name": 'The Cargo-Barge "Pride of the Ankh"',
        "operator": "Bargemaster C.M.O.T. Dibbler",
        "operator_title": "Purveyor of Fine River Cruises & Hot Meat Pies",
        "ports": ["south_docks", "praxis_province_praxis_harbor", "ankh_morpork_brass_bridge_wharf", "ankh_wharf"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
            "ankh_morpork_brass_bridge_wharf": "The Brass Bridge Wharf of Ankh-Morpork",
            "ankh_wharf": "The Brass Bridge Wharf of Ankh-Morpork"
        },
        "fares": {
            ("south_docks", "ankh_morpork_brass_bridge_wharf"): 50,
            ("ankh_morpork_brass_bridge_wharf", "south_docks"): 50,
            ("praxis_province_praxis_harbor", "ankh_morpork_brass_bridge_wharf"): 40,
            ("ankh_morpork_brass_bridge_wharf", "praxis_province_praxis_harbor"): 40,
            ("south_docks", "ankh_wharf"): 50,
            ("ankh_wharf", "south_docks"): 50,
            ("praxis_province_praxis_harbor", "ankh_wharf"): 40,
            ("ankh_wharf", "praxis_province_praxis_harbor"): 40
        },
        "desc": "A flat-bottomed wooden cargo barge smelling faintly of fried onions, stagnant river mud, and mystery meat sausages.",
        "deck_key": "ankh_barge_deck"
    },
    "sultana_skiff": {
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
    },
    "icebreaker_ship": {
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
    },
    "nightfall_skyship": {
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
    },
    "iron_drake_ship": {
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
    },
    "voidstrider_skiff": {
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
    },
    "gossamer_swan_barge": {
        "key": "gossamer_swan_barge",
        "name": 'The Fey-Barge "The Gossamer Swan"',
        "operator": "Eladrin Swan-Keeper Liriel",
        "operator_title": "Navigator of the Enchanted Waterways",
        "ports": ["south_docks", "whispering_silt_islet", "summer_court_emerald_gateway", "summer_court_gateway"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "whispering_silt_islet": "Whispering Silt Islet",
            "summer_court_emerald_gateway": "The Emerald Gateway of the Summer Court",
            "summer_court_gateway": "The Emerald Gateway of the Summer Court"
        },
        "fares": {
            ("south_docks", "summer_court_emerald_gateway"): 75,
            ("summer_court_emerald_gateway", "south_docks"): 75,
            ("whispering_silt_islet", "summer_court_emerald_gateway"): 50,
            ("summer_court_emerald_gateway", "whispering_silt_islet"): 50,
            ("south_docks", "summer_court_gateway"): 75,
            ("summer_court_gateway", "south_docks"): 75,
            ("whispering_silt_islet", "summer_court_gateway"): 50,
            ("summer_court_gateway", "whispering_silt_islet"): 50
        },
        "desc": "A magnificent barge sculpted of pearlescent white wood in the likeness of a crowned swan, propelled silently over starlight waters by giant iridescent wings.",
        "deck_key": "gossamer_swan_deck"
    },
    "wind_dancer_ship": {
        "key": "wind_dancer_ship",
        "name": 'The Djinn Zephyr Skyship "The Wind Dancer"',
        "operator": "Djinn Navigator Rashid",
        "operator_title": "Grand Aeronaut of the Trade Winds",
        "ports": ["south_docks", "praxis_province_praxis_harbor", "djinn_caliphate_cloud_docks", "mount_qaf_docks"],
        "port_names": {
            "south_docks": "Harbor Promenade (Eldoria South Docks)",
            "praxis_province_praxis_harbor": "Old Praxis Imperial Pier",
            "djinn_caliphate_cloud_docks": "The Cloud Docks of Mount Qaf",
            "mount_qaf_docks": "The Cloud Docks of Mount Qaf"
        },
        "fares": {
            ("south_docks", "djinn_caliphate_cloud_docks"): 120,
            ("djinn_caliphate_cloud_docks", "south_docks"): 120,
            ("praxis_province_praxis_harbor", "djinn_caliphate_cloud_docks"): 105,
            ("djinn_caliphate_cloud_docks", "praxis_province_praxis_harbor"): 105,
            ("south_docks", "mount_qaf_docks"): 120,
            ("mount_qaf_docks", "south_docks"): 120,
            ("praxis_province_praxis_harbor", "mount_qaf_docks"): 105,
            ("mount_qaf_docks", "praxis_province_praxis_harbor"): 105
        },
        "desc": "A flying skyship fitted with giant outriggers of woven cloud-silk and sails that billow with perpetual warm trade winds, steered with a golden astrolabe.",
        "deck_key": "wind_dancer_deck"
    },
    "royal_coach_line": {
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
}


# =============================================================================
# VOYAGE ATMOSPHERE & EMBARKATION LOGIC
# =============================================================================

def execute_voyage(char, route_key, origin_room, dest_room, cost_copper, tax_copper):
    """
    Executes an atmospheric real-time ferry voyage with soundscapes and arrival.
    """
    route = FERRY_ROUTES[route_key]
    dest_name = route["port_names"].get(dest_room.tags.get(category="room_key") or dest_room.key, dest_room.key)

    char.msg(
        f"\n|c{route['operator']} collects your fare of {format_copper_as_currency(cost_copper)}.|n\n"
        f"|x[{format_copper_as_currency(tax_copper)} Crown Maritime Tax deposited to Eldoria Municipal Coffers]|n\n"
        f"|w\"{route['operator']} unties the heavy hawser line and signals the crew: 'All hands cast off for {dest_name}!'\"|n\n"
    )

    origin_room.msg_contents(
        f"{char.key} pays the fare and boards {route['name']}. The vessel casts off and slips into the waves!",
        exclude=[char]
    )

    # Move passenger to vessel deck
    deck_key = route.get("deck_key")
    deck = ObjectDB.objects.filter(db_tags__db_key=deck_key, db_tags__db_category="room_key").first() if deck_key else None
    if not deck:
        deck = ObjectDB.objects.filter(db_key=route["name"] + " - Weather Deck").first()
    if deck:
        char.move_to(deck, quiet=True)
    else:
        # Fallback if deck room not yet created
        deck = origin_room

    char.msg(f"|y=== {route['name']} - Underway ===|n")
    char.msg("|wSalt spray foams across the bow as the ship gathers speed under full sail...|n\n")

    # Timed atmospheric stages
    def stage_midway():
        char.msg(
            f"|cSea spray whips against your face as {route['name']} cuts through the rolling swells.\n"
            f"Gulls wheel in the sea breeze, and coastal headlands give way to open waters...|n\n"
        )

    def stage_approach():
        char.msg(
            f"|yThe lookout calls from the bowsprit: 'Land ho! Approaching {dest_name}!'\n"
            f"The crew trims the sails as the vessel maneuvers alongside the timber pier.|n\n"
        )

    def stage_docking():
        char.msg(
            f"|g*** ARRIVAL AT {dest_name.upper()} ***\n"
            f"Mooring lines are lashed tight to the barnacled pilings. The gangplank thuds down.\n"
            f"\"{route['operator']} announces: 'Safe arrival at {dest_name}! Watch your step, travelers.'\"|n\n"
        )
        char.move_to(dest_room, quiet=True)
        dest_room.msg_contents(
            f"{route['name']} docks at the pier, and {char.key} disembarks onto the boards.",
            exclude=[char]
        )

    # Queue delays for interactive voyage progression
    delay(2, stage_midway)
    delay(4, stage_approach)
    delay(6, stage_docking)

