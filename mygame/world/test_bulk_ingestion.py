"""
Unit & Integration Tests for Bulk World Ingestion

Tests:
1. Execution of run_bulk_ingestion() across all 5 zones (150+ rooms)
2. Reciprocal overland anchors (Midgaard, Goblin Stronghold, Praxis, Shadowfen, Astral Rifts)
3. Fixed danger level stats and abilities for NPCs across tiers (Level 1 to 26)
4. GMCP Room.Info automapper telemetry on newly ingested rooms
5. Royal Galleon maritime ferry registration & weather deck
"""

import os
import django
from django.conf import settings

if not settings.configured:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")
    django.setup()

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.rooms import Room, get_gmcp_room_info
from world.importers.bulk_ingestion import run_bulk_ingestion
from world.importers.bulk_ingestion_part2 import run_bulk_ingestion_part2
from world.importers.bulk_ingestion_part3 import run_bulk_ingestion_part3
from world.importers.bulk_ingestion_part4 import run_bulk_ingestion_part4
from world.importers.bulk_ingestion_part5 import run_bulk_ingestion_part5
from world.importers.bulk_ingestion_part6 import run_bulk_ingestion_part6
from world.importers.bulk_ingestion_part7 import run_bulk_ingestion_part7
from world.importers.bulk_ingestion_part8 import run_bulk_ingestion_part8
from world.importers.bulk_ingestion_part9 import run_bulk_ingestion_part9
from world.importers.bulk_ingestion_part10 import run_bulk_ingestion_part10
from world.importers.bulk_ingestion_part11 import run_bulk_ingestion_part11
from world.importers.bulk_ingestion_part12 import run_bulk_ingestion_part12
from world.importers.bulk_ingestion_part13 import run_bulk_ingestion_part13
from world.importers.bulk_ingestion_part14 import run_bulk_ingestion_part14
from world.importers.bulk_ingestion_part15 import run_bulk_ingestion_part15
from world.importers.bulk_ingestion_part16 import run_bulk_ingestion_part16
from world.importers.bulk_ingestion_part17 import run_bulk_ingestion_part17
from world.importers.zone_importer import find_room_by_key
import world.sailing as sailing


class TestBulkIngestion(EvenniaTest):
    """Test suite verifying complete bulk world ingestion."""

    def setUp(self):
        super().setUp()
        # Ensure anchor rooms exist in test environment
        self.anchor_keys = {
            "north_gate": "Eldoria North Gate",
            "foothills": "Craggy Foothills",
            "dead_mans_cove": "Dead Man's Cove",
            "marshland": "The Sunken Mire",
            "silt_islet": "Whispering Silt Islet",
            "south_docks": "Harbor Promenade",
            "deep_woods": "Deep in the Whispering Woods",
            "frostfang_pass": "Frostfang Mountain Pass",
            "bazaar": "The Sunken Bazaar",
            "ossuary": "The Sunken Ossuary",
            "watchtower": "Ruined Hilltop Watchtower",
            "summit": "The Cloud-Piercing Summit",
            "rail_hub": "Subterranean Rail Hub",
            "chasm_bridge": "The Howling Chasm Bridge",
            "catacombs": "Forgotten Catacombs",
            "cathedral": "Cathedral of the Radiant Dawn",
            "plaza": "Eldoria Grand Plaza",
            "city_of_brass_obsidian_pier": "The Obsidian Pier of the Sea of Fire",
            "astral_nexus": "The Astral Nexus Platform"
        }
        for k, name in self.anchor_keys.items():
            r = find_room_by_key(k)
            if not r:
                r = create_object(Room, key=name, tags=["eldoria_world"])
                r.tags.add(k, category="room_key")
                r.db.room_key = k

    def test_bulk_world_ingestion(self):
        """Verify ingestion of all 5 zones, 150+ rooms, exits, mobs, and anchors."""
        report = run_bulk_ingestion(clean_existing=True)

        # 1. Volume assertions
        self.assertEqual(report["zones_processed"], 5)
        self.assertGreaterEqual(report["rooms_created"], 150)
        self.assertGreaterEqual(report["exits_created"], 200)
        self.assertGreaterEqual(report["npcs_created"], 25)
        self.assertGreaterEqual(report["items_created"], 20)
        self.assertEqual(len(report["anchors_established"]), 5)

        # 2. Verify key rooms in each zone
        midgaard_temple = find_room_by_key("midgaard_district_temple_square")
        self.assertIsNotNone(midgaard_temple)
        self.assertEqual(midgaard_temple.key, "The Great Temple Square")
        self.assertEqual(midgaard_temple.db.zone, "The Grand City of Midgaard")

        goblin_mine = find_room_by_key("goblin_stronghold_mine_entrance")
        self.assertIsNotNone(goblin_mine)
        self.assertEqual(goblin_mine.key, "Mouth of the Ironcrag Mines")

        praxis_harbor = find_room_by_key("praxis_province_praxis_harbor")
        self.assertIsNotNone(praxis_harbor)
        self.assertEqual(praxis_harbor.key, "Old Praxis Imperial Pier")

        shadowfen_lich = find_room_by_key("shadowfen_necropolis_lich_sanctum")
        self.assertIsNotNone(shadowfen_lich)
        self.assertEqual(shadowfen_lich.key, "Inner Sanctum of Arch-Lich Malakor")

        astral_vault = find_room_by_key("astral_rifts_vault_stars")
        self.assertIsNotNone(astral_vault)
        self.assertEqual(astral_vault.key, "The Vault of the Sovereigns")

        # 3. Verify Overland Anchors
        # North Gate -> Midgaard South Gate
        north_gate = find_room_by_key("north_gate")
        ex_to_mid = [ex for ex in north_gate.exits if ex.key == "north"]
        self.assertTrue(len(ex_to_mid) > 0)
        self.assertEqual(ex_to_mid[0].destination.db.room_key, "midgaard_district_south_gate")

        mid_gate = find_room_by_key("midgaard_district_south_gate")
        ex_to_eldoria = [ex for ex in mid_gate.exits if ex.key == "south"]
        self.assertTrue(len(ex_to_eldoria) > 0)
        self.assertEqual(ex_to_eldoria[0].destination, north_gate)

        # Silt Islet -> Astral Nexus
        silt_islet = find_room_by_key("silt_islet")
        ex_to_astral = [ex for ex in silt_islet.exits if "portal" in ex.key]
        self.assertTrue(len(ex_to_astral) > 0)
        self.assertEqual(ex_to_astral[0].destination.db.room_key, "astral_rifts_astral_nexus")

        # 4. Verify GMCP Automapper Telemetry
        gmcp_mid = get_gmcp_room_info(midgaard_temple)
        self.assertEqual(gmcp_mid["zone"], "The Grand City of Midgaard")
        self.assertEqual(gmcp_mid["terrain"], "city")
        self.assertIn("coord", gmcp_mid)

        gmcp_astral = get_gmcp_room_info(astral_vault)
        self.assertEqual(gmcp_astral["zone"], "The Astral Rifts & Elemental Spires")
        self.assertEqual(gmcp_astral["terrain"], "air")
        self.assertEqual(gmcp_astral["coord"]["z"], 31)

        # 5. Verify Fixed Danger NPCs & Stats
        # Level 12 Boss: Chieftain Gornak
        gornak_room = find_room_by_key("goblin_stronghold_chieftain_hall")
        gornak = [c for c in gornak_room.contents if c.key == "Chieftain Gornak Ironfang"][0]
        self.assertEqual(gornak.db.level, 12)
        self.assertGreaterEqual(gornak.db.hp, 250)
        self.assertGreaterEqual(gornak.db.stats["str"], 25)
        self.assertIn("torso", gornak.db.limbs)

        # Level 19 Boss: Arch-Lich Malakor
        malakor = [c for c in shadowfen_lich.contents if c.key == "Arch-Lich Malakor"][0]
        self.assertEqual(malakor.db.level, 19)
        self.assertGreaterEqual(malakor.db.hp, 600)
        self.assertIn("fireball", malakor.db.spellbook)

        # Level 26 Endgame Boss: The Astral Overseer
        overseer = [c for c in astral_vault.contents if c.key == "The Astral Overseer"][0]
        self.assertEqual(overseer.db.level, 26)
        self.assertGreaterEqual(overseer.db.hp, 1500)

        # 6. Verify Maritime Royal Galleon Route
        self.assertIn("praxis_galleon", sailing.FERRY_ROUTES)
        galleon = sailing.FERRY_ROUTES["praxis_galleon"]
        self.assertEqual(galleon["operator"], "Commodore Ethan Hawke")
        self.assertIn("south_docks", galleon["ports"])
        self.assertIn("praxis_province_praxis_harbor", galleon["ports"])
        self.assertIn("midgaard_district_midgaard_port", galleon["ports"])

        # Weather deck room exists
        deck = find_room_by_key("praxis_galleon_deck")
        self.assertIsNotNone(deck)
        self.assertIn("Sea Phantom", deck.key)

    def test_bulk_ingestion_part2(self):
        """Verify ingestion of Part 2 zones (120+ rooms, Silvanesti, Khazad, Kalim, Honshu)."""
        report = run_bulk_ingestion_part2(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertGreaterEqual(report["rooms_created"], 120)
        self.assertGreaterEqual(report["exits_created"], 150)
        self.assertGreaterEqual(report["npcs_created"], 20)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 3)

        # 1. Verify key rooms in each zone
        flet = find_room_by_key("silvanesti_canopy_village_flet")
        self.assertIsNotNone(flet)
        self.assertEqual(flet.key, "Central Flet of the Elven Haven")

        durin = find_room_by_key("khazad_deeps_thane_throne_room")
        self.assertIsNotNone(durin)
        self.assertEqual(durin.key, "Throne Room of the High Thane")

        pyramid = find_room_by_key("kalim_desert_burial_chamber")
        self.assertIsNotNone(pyramid)
        self.assertEqual(pyramid.key, "The Golden Tomb of Pharaoh Akhen-Ra")

        honshu = find_room_by_key("honshu_realm_monastery_courtyard")
        self.assertIsNotNone(honshu)
        self.assertEqual(honshu.key, "Courtyard of the Five Tigers")

        # 2. Verify Overland Anchors
        # deep_woods -> silvanesti_canopy_canopy_ascent
        deep_woods = find_room_by_key("deep_woods")
        ex_to_silv = [ex for ex in deep_woods.exits if ex.key == "east"]
        self.assertTrue(len(ex_to_silv) > 0)
        self.assertEqual(ex_to_silv[0].destination.db.room_key, "silvanesti_canopy_canopy_ascent")

        # frostfang_pass -> khazad_deeps_great_gates
        frostfang = find_room_by_key("frostfang_pass")
        ex_to_khazad = [ex for ex in frostfang.exits if ex.key == "north"]
        self.assertTrue(len(ex_to_khazad) > 0)
        self.assertEqual(ex_to_khazad[0].destination.db.room_key, "khazad_deeps_great_gates")

        # bazaar -> kalim_desert_caravan_post
        bazaar = find_room_by_key("bazaar")
        ex_to_kalim = [ex for ex in bazaar.exits if ex.key == "south"]
        self.assertTrue(len(ex_to_kalim) > 0)
        self.assertEqual(ex_to_kalim[0].destination.db.room_key, "kalim_desert_caravan_post")

        # 3. Verify Bosses
        thorgar = [c for c in durin.contents if c.key == "High Thane Thorgar Stoneheart"][0]
        self.assertEqual(thorgar.db.level, 18)
        self.assertGreaterEqual(thorgar.db.hp, 600)

        pharaoh = [c for c in pyramid.contents if c.key == "Pharaoh Akhen-Ra"][0]
        self.assertEqual(pharaoh.db.level, 17)

        dragon_sanctuary = find_room_by_key("honshu_realm_dragon_sanctuary")
        dragon = [c for c in dragon_sanctuary.contents if c.key == "The Celestial Jade Dragon"][0]
        self.assertEqual(dragon.db.level, 25)
        self.assertGreaterEqual(dragon.db.hp, 1400)

        # 4. Verify Maritime Jade Junk Route
        self.assertIn("jade_junk", sailing.FERRY_ROUTES)
        junk = sailing.FERRY_ROUTES["jade_junk"]
        self.assertEqual(junk["operator"], "Captain Toshiro Jin")
        self.assertIn("south_docks", junk["ports"])

        junk_deck = find_room_by_key("jade_junk_deck")
        self.assertIsNotNone(junk_deck)
        self.assertIn("Jade Dragon Junk", junk_deck.key)

    def test_bulk_ingestion_part3(self):
        """Verify ingestion of Part 3 mythic zones (120+ rooms, Atlantea, Underdark, Ravenloft, Cloud Citadel)."""
        report = run_bulk_ingestion_part3(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertGreaterEqual(report["rooms_created"], 120)
        self.assertGreaterEqual(report["exits_created"], 150)
        self.assertGreaterEqual(report["npcs_created"], 20)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 3)

        # 1. Verify key rooms in each zone
        triton_throne = find_room_by_key("atlantea_depths_throne_room_triton")
        self.assertIsNotNone(triton_throne)
        self.assertEqual(triton_throne.key, "The High Throne of King Triton")

        matron_sanctum = find_room_by_key("underdark_drow_matron_sanctum")
        self.assertIsNotNone(matron_sanctum)
        self.assertEqual(matron_sanctum.key, "Sanctum of Matron Mother Malice")

        vlad_spire = find_room_by_key("ravenloft_castle_high_tower_spire")
        self.assertIsNotNone(vlad_spire)
        self.assertEqual(vlad_spire.key, "The High Spire of Count Vlad")

        storm_throne = find_room_by_key("cloud_citadel_storm_throne_room")
        self.assertIsNotNone(storm_throne)
        self.assertEqual(storm_throne.key, "The Throne of the Sky King")

        # 2. Verify Anchors
        # ossuary -> underdark_drow_chasm_descent
        ossuary = find_room_by_key("ossuary")
        ex_to_under = [ex for ex in ossuary.exits if ex.key == "down"]
        self.assertTrue(len(ex_to_under) > 0)
        self.assertEqual(ex_to_under[0].destination.db.room_key, "underdark_drow_chasm_descent")

        # watchtower -> ravenloft_castle_drawbridge_chasm
        watchtower = find_room_by_key("watchtower")
        ex_to_raven = [ex for ex in watchtower.exits if ex.key == "northeast"]
        self.assertTrue(len(ex_to_raven) > 0)
        self.assertEqual(ex_to_raven[0].destination.db.room_key, "ravenloft_castle_drawbridge_chasm")

        # summit -> cloud_citadel_cumulus_gateway
        summit = find_room_by_key("summit")
        ex_to_cloud = [ex for ex in summit.exits if "cloud" in ex.key]
        self.assertTrue(len(ex_to_cloud) > 0)
        self.assertEqual(ex_to_cloud[0].destination.db.room_key, "cloud_citadel_cumulus_gateway")

        # 3. Verify Mythic Bosses
        triton = [c for c in triton_throne.contents if c.key == "King Triton the Sea Lord"][0]
        self.assertEqual(triton.db.level, 23)
        self.assertGreaterEqual(triton.db.hp, 1000)

        malice = [c for c in matron_sanctum.contents if c.key == "Matron Mother Malice"][0]
        self.assertEqual(malice.db.level, 24)

        vlad = [c for c in vlad_spire.contents if c.key == "Count Vlad von Ravencrest"][0]
        self.assertEqual(vlad.db.level, 20)
        self.assertGreaterEqual(vlad.db.hp, 800)

        hekaton = [c for c in storm_throne.contents if c.key == "Storm King Hekaton"][0]
        self.assertEqual(hekaton.db.level, 27)
        self.assertGreaterEqual(hekaton.db.hp, 1600)

        # 4. Verify Submersible Route: The Bathysphere Nautilus
        self.assertIn("nautilus_sub", sailing.FERRY_ROUTES)
        nautilus = sailing.FERRY_ROUTES["nautilus_sub"]
        self.assertEqual(nautilus["operator"], "Chief Engineer Aronnax")
        self.assertIn("south_docks", nautilus["ports"])

        sub_deck = find_room_by_key("nautilus_deck")
        self.assertIsNotNone(sub_deck)
        self.assertIn("Nautilus", sub_deck.key)

    def test_bulk_ingestion_part4(self):
        """Verify ingestion of Part 4 outer planes & frontier zones (120+ rooms, Cogsmith, Jotunheim, Tortuga, Baator Dis)."""
        report = run_bulk_ingestion_part4(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertGreaterEqual(report["rooms_created"], 120)
        self.assertGreaterEqual(report["exits_created"], 150)
        self.assertGreaterEqual(report["npcs_created"], 20)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 3)

        # 1. Verify key rooms in each zone
        gearloose_obs = find_room_by_key("clockwork_city_chronos_observatory")
        self.assertIsNotNone(gearloose_obs)
        self.assertEqual(gearloose_obs.key, "The Chronos Clockwork Apex")

        jotun_throne = find_room_by_key("jotunheim_frost_throne_frost_king")
        self.assertIsNotNone(jotun_throne)
        self.assertEqual(jotun_throne.key, "The Throne of the Glacial King")

        tortuga_council = find_room_by_key("tortuga_haven_council_of_captains")
        self.assertIsNotNone(tortuga_council)
        self.assertEqual(tortuga_council.key, "The High Council of Captains")

        dispater_throne = find_room_by_key("baator_hells_throne_dispater")
        self.assertIsNotNone(dispater_throne)
        self.assertEqual(dispater_throne.key, "The Obsidian Throne of Lord Dispater")

        # 2. Verify Anchors
        # rail_hub -> clockwork_city_brass_tram_station
        rail_hub = find_room_by_key("rail_hub")
        ex_to_clock = [ex for ex in rail_hub.exits if "steam tram" in ex.key]
        self.assertTrue(len(ex_to_clock) > 0)
        self.assertEqual(ex_to_clock[0].destination.db.room_key, "clockwork_city_brass_tram_station")

        # chasm_bridge -> jotunheim_frost_glacial_portal_pass
        chasm_bridge = find_room_by_key("chasm_bridge")
        ex_to_jotun = [ex for ex in chasm_bridge.exits if "frozen ravine" in ex.key]
        self.assertTrue(len(ex_to_jotun) > 0)
        self.assertEqual(ex_to_jotun[0].destination.db.room_key, "jotunheim_frost_glacial_portal_pass")

        # catacombs -> baator_hells_infernal_threshold
        catacombs = find_room_by_key("catacombs")
        ex_to_baator = [ex for ex in catacombs.exits if "hellfire rift" in ex.key]
        self.assertTrue(len(ex_to_baator) > 0)
        self.assertEqual(ex_to_baator[0].destination.db.room_key, "baator_hells_infernal_threshold")

        # 3. Verify Mythic Bosses
        gearloose = [c for c in gearloose_obs.contents if c.key == "Grand Mechanist Gearloose"][0]
        self.assertEqual(gearloose.db.level, 16)
        self.assertGreaterEqual(gearloose.db.hp, 500)

        thrym = [c for c in jotun_throne.contents if c.key == "Jarl Thrym the Frost King"][0]
        self.assertEqual(thrym.db.level, 25)
        self.assertGreaterEqual(thrym.db.hp, 1400)

        morgan = [c for c in tortuga_council.contents if c.key == "Dread Captain Morgan Blood-Eye"][0]
        self.assertEqual(morgan.db.level, 14)
        self.assertGreaterEqual(morgan.db.hp, 350)

        dispater = [c for c in dispater_throne.contents if c.key == "Arch-Devil Dispater"][0]
        self.assertEqual(dispater.db.level, 28)
        self.assertGreaterEqual(dispater.db.hp, 1500)

        # 4. Verify Maritime Route: The Black Skull Corsair Frigate
        self.assertIn("black_skull_ship", sailing.FERRY_ROUTES)
        black_skull = sailing.FERRY_ROUTES["black_skull_ship"]
        self.assertEqual(black_skull["operator"], "Quartermaster Flint")
        self.assertIn("dead_mans_cove", black_skull["ports"])
        self.assertIn("tortuga_haven_tortuga_docks", black_skull["ports"])

        skull_deck = find_room_by_key("black_skull_deck")
        self.assertIsNotNone(skull_deck)
        self.assertIn("Black Skull Corsair Frigate", skull_deck.key)

    def test_bulk_ingestion_part5(self):
        """Verify ingestion of Part 5 primordial & abyssal realms (120+ rooms, Chult, Pharaohs, Feywild, Demonweb Pits)."""
        report = run_bulk_ingestion_part5(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertGreaterEqual(report["rooms_created"], 120)
        self.assertGreaterEqual(report["exits_created"], 150)
        self.assertGreaterEqual(report["npcs_created"], 30)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        chult_apex = find_room_by_key("chult_jungle_apex_spire_omu")
        self.assertIsNotNone(chult_apex)
        self.assertEqual(chult_apex.key, "The Obsidian Sanctum of Acererak")

        pharaoh_throne = find_room_by_key("valley_pharaohs_kings_burial_chamber")
        self.assertIsNotNone(pharaoh_throne)
        self.assertEqual(pharaoh_throne.key, "The Gold Sarcophagus Chamber of Akhenaten")

        titania_throne = find_room_by_key("feywild_court_summer_throne_room")
        self.assertIsNotNone(titania_throne)
        self.assertEqual(titania_throne.key, "The Living Oak Throne of Queen Titania")

        lolth_throne = find_room_by_key("abyssal_demonweb_throne_spider_queen")
        self.assertIsNotNone(lolth_throne)
        self.assertEqual(lolth_throne.key, "The Great Web Throne of the Demon Queen")

        # 2. Verify Anchors
        # foothills -> chult_jungle_river_mouth
        foothills = find_room_by_key("foothills")
        ex_to_chult = [ex for ex in foothills.exits if "primeval jungle" in ex.key]
        self.assertTrue(len(ex_to_chult) > 0)
        self.assertEqual(ex_to_chult[0].destination.db.room_key, "chult_jungle_river_mouth")

        # bazaar -> valley_pharaohs_avenue_sphinxes
        bazaar = find_room_by_key("bazaar")
        ex_to_pharaohs = [ex for ex in bazaar.exits if "valley of pharaohs" in ex.key]
        self.assertTrue(len(ex_to_pharaohs) > 0)
        self.assertEqual(ex_to_pharaohs[0].destination.db.room_key, "valley_pharaohs_avenue_sphinxes")

        # deep_woods -> feywild_court_faerie_ring_crossing
        deep_woods = find_room_by_key("deep_woods")
        ex_to_fey = [ex for ex in deep_woods.exits if "twilight ring" in ex.key]
        self.assertTrue(len(ex_to_fey) > 0)
        self.assertEqual(ex_to_fey[0].destination.db.room_key, "feywild_court_faerie_ring_crossing")

        # marshland -> abyssal_demonweb_web_chasm_verge
        marshland = find_room_by_key("marshland")
        ex_to_abyss = [ex for ex in marshland.exits if "abyssal rift" in ex.key]
        self.assertTrue(len(ex_to_abyss) > 0)
        self.assertEqual(ex_to_abyss[0].destination.db.room_key, "abyssal_demonweb_web_chasm_verge")

        # 3. Verify Mythic Bosses
        acererak = [c for c in chult_apex.contents if c.key == "Arch-Lich Acererak"][0]
        self.assertEqual(acererak.db.level, 18)
        self.assertGreaterEqual(acererak.db.hp, 500)

        akhenaten = [c for c in pharaoh_throne.contents if c.key == "Pharaoh Akhenaten the Sun King"][0]
        self.assertEqual(akhenaten.db.level, 22)
        self.assertGreaterEqual(akhenaten.db.hp, 900)

        titania = [c for c in titania_throne.contents if c.key == "Queen Titania the Summer Monarch"][0]
        self.assertEqual(titania.db.level, 24)
        self.assertGreaterEqual(titania.db.hp, 1100)

        lolth = [c for c in lolth_throne.contents if c.key == "Lolth the Demon Queen of Spiders"][0]
        self.assertEqual(lolth.db.level, 30)
        self.assertGreaterEqual(lolth.db.hp, 1800)

        # 4. Verify Aether-Skyship Route: The Zephyr's Pride
        self.assertIn("zephyr_skyship", sailing.FERRY_ROUTES)
        zephyr = sailing.FERRY_ROUTES["zephyr_skyship"]
        self.assertEqual(zephyr["operator"], "High Sky-Captain Aurelius")
        self.assertIn("south_docks", zephyr["ports"])
        self.assertIn("cloud_citadel_cumulus_gateway", zephyr["ports"])

        skyship_deck = find_room_by_key("zephyr_skyship_deck")
        self.assertIsNotNone(skyship_deck)
        self.assertIn("Zephyr's Pride", skyship_deck.key)

    def test_bulk_ingestion_part6(self):
        """Verify ingestion of Part 6 '1,000 Rooms Club' (305 rooms, Sewers, Haon-Dor, Graveyard, Moria)."""
        # Ensure Midgaard anchor rooms exist for Part 6 test isolation
        for k, name in [("midgaard_district_market_square", "Midgaard Market Square"), ("midgaard_district_temple_square", "The Great Temple Square")]:
            if not find_room_by_key(k):
                r = create_object(Room, key=name, tags=["eldoria_world"])
                r.tags.add(k, category="room_key")
                r.tags.add("midgaard_district", category="zone")
                r.db.room_key = k
                r.db.zone = "The Grand City of Midgaard"

        report = run_bulk_ingestion_part6(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 305)
        self.assertGreaterEqual(report["exits_created"], 1000)
        self.assertGreaterEqual(report["npcs_created"], 50)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        sewer_throne = find_room_by_key("midgaard_sewers_wererat_throne_room")
        self.assertIsNotNone(sewer_throne)
        self.assertEqual(sewer_throne.key, "The Filth Throne of the Rat King")

        haondor_boss = find_room_by_key("haon_dor_forest_bandit_lord_tent")
        self.assertIsNotNone(haondor_boss)
        self.assertEqual(haondor_boss.key, "Pavilion of Bandit Lord Malrik")

        graveyard_wight = find_room_by_key("midgaard_graveyard_crypt_wight_throne")
        self.assertIsNotNone(graveyard_wight)
        self.assertEqual(graveyard_wight.key, "The Sepulcher of the Crypt Wight Sovereign")

        moria_tomb = find_room_by_key("moria_mines_chamber_of_mazarbul")
        self.assertIsNotNone(moria_tomb)
        self.assertEqual(moria_tomb.key, "The Chamber of Records & Balin's Tomb")

        # 2. Verify Anchors
        # midgaard_district_market_square -> midgaard_sewers_sewer_grate_market
        market = find_room_by_key("midgaard_district_market_square")
        ex_to_sewer = [ex for ex in market.exits if "iron sewer grate" in ex.key]
        self.assertTrue(len(ex_to_sewer) > 0)
        self.assertEqual(ex_to_sewer[0].destination.db.room_key, "midgaard_sewers_sewer_grate_market")

        # deep_woods -> haon_dor_forest_haon_dor_western_verge
        deep_woods = find_room_by_key("deep_woods")
        ex_to_haondor = [ex for ex in deep_woods.exits if "ancient woods of haon-dor" in ex.key]
        self.assertTrue(len(ex_to_haondor) > 0)
        self.assertEqual(ex_to_haondor[0].destination.db.room_key, "haon_dor_forest_haon_dor_western_verge")

        # midgaard_district_temple_square -> midgaard_graveyard_graveyard_iron_gate
        temple = find_room_by_key("midgaard_district_temple_square")
        ex_to_grave = [ex for ex in temple.exits if "cemetery iron gates" in ex.key]
        self.assertTrue(len(ex_to_grave) > 0)
        self.assertEqual(ex_to_grave[0].destination.db.room_key, "midgaard_graveyard_graveyard_iron_gate")

        # frostfang_pass -> moria_mines_moria_west_gate_durin
        frostfang = find_room_by_key("frostfang_pass")
        ex_to_moria = [ex for ex in frostfang.exits if "doors of durin" in ex.key]
        self.assertTrue(len(ex_to_moria) > 0)
        self.assertEqual(ex_to_moria[0].destination.db.room_key, "moria_mines_moria_west_gate_durin")

        # 3. Verify Bosses
        rat_king = [c for c in sewer_throne.contents if c.key == "Rat King Splinterclaw"][0]
        self.assertEqual(rat_king.db.level, 8)
        self.assertGreaterEqual(rat_king.db.hp, 150)

        malrik = [c for c in haondor_boss.contents if c.key == "Bandit Lord Malrik"][0]
        self.assertEqual(malrik.db.level, 11)
        self.assertGreaterEqual(malrik.db.hp, 220)

        wight = [c for c in graveyard_wight.contents if c.key == "The Crypt Wight Sovereign"][0]
        self.assertEqual(wight.db.level, 12)
        self.assertGreaterEqual(wight.db.hp, 250)

        balin = [c for c in moria_tomb.contents if c.key == "Balin's Shadow Wraith"][0]
        self.assertEqual(balin.db.level, 17)
        self.assertGreaterEqual(balin.db.hp, 450)

    def test_bulk_ingestion_part7(self):
        """Verify ingestion of Part 7 (251 rooms, Sunken Citadel, Tower of Sorcery, Camelot, Duergar Deeps)."""
        if not find_room_by_key("khazad_deeps_great_gates"):
            r = create_object(Room, key="The Adamantine Doors of Durin", tags=["eldoria_world"])
            r.tags.add("khazad_deeps_great_gates", category="room_key")
            r.tags.add("khazad_deeps", category="zone")
            r.db.room_key = "khazad_deeps_great_gates"

        report = run_bulk_ingestion_part7(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 251)
        self.assertGreaterEqual(report["exits_created"], 800)
        self.assertGreaterEqual(report["npcs_created"], 50)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        citadel_tree = find_room_by_key("sunken_citadel_gulthias_tree_heart")
        self.assertIsNotNone(citadel_tree)
        self.assertEqual(citadel_tree.key, "The Heart of the Gulthias Tree")

        raistlin_apex = find_room_by_key("tower_sorcery_apex_archmage_sanctum")
        self.assertIsNotNone(raistlin_apex)
        self.assertEqual(raistlin_apex.key, "The High Apex of the Master of Sorcery")

        round_table = find_room_by_key("camelot_realm_round_table_hall")
        self.assertIsNotNone(round_table)
        self.assertEqual(round_table.key, "The Great Hall of the Round Table")

        duergar_throne = find_room_by_key("duergar_deep_city_throne_deep_king_horgar")
        self.assertIsNotNone(duergar_throne)
        self.assertEqual(duergar_throne.key, "The Iron Throne of Deep King Horgar")

        # 2. Verify Anchors
        # foothills -> sunken_citadel_sunken_citadel_chasm_ledge
        foothills = find_room_by_key("foothills")
        ex_to_citadel = [ex for ex in foothills.exits if "cracked ravine" in ex.key]
        self.assertTrue(len(ex_to_citadel) > 0)
        self.assertEqual(ex_to_citadel[0].destination.db.room_key, "sunken_citadel_sunken_citadel_chasm_ledge")

        # watchtower -> tower_sorcery_tower_sorcery_shoikan_grove
        watchtower = find_room_by_key("watchtower")
        ex_to_sorcery = [ex for ex in watchtower.exits if "grove of shadows" in ex.key]
        self.assertTrue(len(ex_to_sorcery) > 0)
        self.assertEqual(ex_to_sorcery[0].destination.db.room_key, "tower_sorcery_tower_sorcery_shoikan_grove")

        # north_gate -> camelot_realm_camelot_realm_tournament_meadow
        north_gate = find_room_by_key("north_gate")
        ex_to_camelot = [ex for ex in north_gate.exits if "camelot" in ex.key]
        self.assertTrue(len(ex_to_camelot) > 0)
        self.assertEqual(ex_to_camelot[0].destination.db.room_key, "camelot_realm_camelot_realm_tournament_meadow")

        # khazad_deeps_great_gates -> duergar_deep_city_duergar_deep_city_obsidian_gate
        khazad_gates = find_room_by_key("khazad_deeps_great_gates")
        ex_to_duergar = [ex for ex in khazad_gates.exits if "duergar chasm" in ex.key]
        self.assertTrue(len(ex_to_duergar) > 0)
        self.assertEqual(ex_to_duergar[0].destination.db.room_key, "duergar_deep_city_duergar_deep_city_obsidian_gate")

        # 3. Verify Bosses
        belak = [c for c in citadel_tree.contents if c.key == "Belak the Outcast Druid"][0]
        self.assertEqual(belak.db.level, 6)
        self.assertGreaterEqual(belak.db.hp, 120)

        raistlin = [c for c in raistlin_apex.contents if c.key == "Archmage Raistlin Majere"][0]
        self.assertEqual(raistlin.db.level, 25)
        self.assertGreaterEqual(raistlin.db.hp, 1200)

        arthur = [c for c in round_table.contents if c.key == "King Arthur Pendragon"][0]
        self.assertEqual(arthur.db.level, 20)
        self.assertGreaterEqual(arthur.db.hp, 750)

        horgar = [c for c in duergar_throne.contents if c.key == "Deep King Horgar Steelshadow"][0]
        self.assertEqual(horgar.db.level, 23)
        self.assertGreaterEqual(horgar.db.hp, 1000)

        # 4. Verify Avalon Mist-Barge Route
        self.assertIn("avalon_barge", sailing.FERRY_ROUTES)
        avalon = sailing.FERRY_ROUTES["avalon_barge"]
        self.assertEqual(avalon["operator"], "Nimue the Lake Maiden")
        self.assertIn("south_docks", avalon["ports"])
        self.assertIn("camelot_realm_avalon_ferry_dock", avalon["ports"])

        avalon_deck = find_room_by_key("avalon_barge_deck")
        self.assertIsNotNone(avalon_deck)
        self.assertIn("Nimue's Blessing", avalon_deck.key)

    def test_bulk_ingestion_part8(self):
        """Verify ingestion of Part 8 '1,500 Rooms Milestone' (260 rooms, Temple of Evil, Shire, Atlantis Shelf, Mount Celestia)."""
        report = run_bulk_ingestion_part8(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 260)
        self.assertGreaterEqual(report["exits_created"], 900)
        self.assertGreaterEqual(report["npcs_created"], 50)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        zuggtmoy_sanctum = find_room_by_key("temple_evil_zuggtmoy_fungal_sanctum")
        self.assertIsNotNone(zuggtmoy_sanctum)
        self.assertEqual(zuggtmoy_sanctum.key, "The Golden Spore Sanctum of Zuggtmoy")

        bag_end = find_room_by_key("halfling_shire_bag_end_smial")
        self.assertIsNotNone(bag_end)
        self.assertEqual(bag_end.key, "Bag End - The Round Green Door")

        thalassa_throne = find_room_by_key("atlantis_shelf_empress_thalassa_throne")
        self.assertIsNotNone(thalassa_throne)
        self.assertEqual(thalassa_throne.key, "The Coral Throne of Empress Thalassa")

        michael_apex = find_room_by_key("mount_celestia_solar_throne_apex")
        self.assertIsNotNone(michael_apex)
        self.assertEqual(michael_apex.key, "The Empyreal Summit of Mount Celestia")

        # 2. Verify Anchors
        # marshland -> temple_evil_temple_evil_ruined_moathouse
        marshland = find_room_by_key("marshland")
        ex_to_temple = [ex for ex in marshland.exits if "ruined moathouse" in ex.key]
        self.assertTrue(len(ex_to_temple) > 0)
        self.assertEqual(ex_to_temple[0].destination.db.room_key, "temple_evil_temple_evil_ruined_moathouse")

        # north_gate -> halfling_shire_shire_brandywine_bridge
        north_gate = find_room_by_key("north_gate")
        ex_to_shire = [ex for ex in north_gate.exits if "brandywine bridge" in ex.key]
        self.assertTrue(len(ex_to_shire) > 0)
        self.assertEqual(ex_to_shire[0].destination.db.room_key, "halfling_shire_shire_brandywine_bridge")

        # dead_mans_cove -> atlantis_shelf_coral_shelf_pearl_shallows
        cove = find_room_by_key("dead_mans_cove")
        ex_to_coral = [ex for ex in cove.exits if "coral shallows" in ex.key]
        self.assertTrue(len(ex_to_coral) > 0)
        self.assertEqual(ex_to_coral[0].destination.db.room_key, "atlantis_shelf_coral_shelf_pearl_shallows")

        # summit -> mount_celestia_celestia_silver_sea_shore
        summit = find_room_by_key("summit")
        ex_to_celestia = [ex for ex in summit.exits if "silver light" in ex.key]
        self.assertTrue(len(ex_to_celestia) > 0)
        self.assertEqual(ex_to_celestia[0].destination.db.room_key, "mount_celestia_celestia_silver_sea_shore")

        # 3. Verify Bosses
        zuggtmoy = [c for c in zuggtmoy_sanctum.contents if c.key == "Demon Queen Zuggtmoy"][0]
        self.assertEqual(zuggtmoy.db.level, 20)
        self.assertGreaterEqual(zuggtmoy.db.hp, 800)

        whitfoot = [c for c in bag_end.contents if c.key == "Mayor Will Whitfoot"][0]
        self.assertEqual(whitfoot.db.level, 4)
        self.assertGreaterEqual(whitfoot.db.hp, 70)

        thalassa = [c for c in thalassa_throne.contents if c.key == "High Sea Empress Thalassa"][0]
        self.assertEqual(thalassa.db.level, 22)
        self.assertGreaterEqual(thalassa.db.hp, 900)

        michael = [c for c in michael_apex.contents if c.key == "Archangel Michael the Solar Champion"][0]
        self.assertEqual(michael.db.level, 28)
        self.assertGreaterEqual(michael.db.hp, 1600)

    def test_bulk_ingestion_part9(self):
        """Verify ingestion of Part 9 '1,800 Rooms Milestone' (289 rooms, Labyrinth, Ankh-Morpork, Dragon Wastes, R'lyeh)."""
        report = run_bulk_ingestion_part9(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 289)
        self.assertGreaterEqual(report["exits_created"], 1000)
        self.assertGreaterEqual(report["npcs_created"], 50)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        minos_altar = find_room_by_key("labyrinth_minos_labyrinth_center_altar")
        self.assertIsNotNone(minos_altar)
        self.assertEqual(minos_altar.key, "The Blood Altar of Asterion")

        vetinari_office = find_room_by_key("ankh_morpork_patrician_oblong_office")
        self.assertIsNotNone(vetinari_office)
        self.assertEqual(vetinari_office.key, "The Oblong Office of Lord Vetinari")

        wyrm_hoard = find_room_by_key("dragon_wastes_wyrm_hoard_cavern")
        self.assertIsNotNone(wyrm_hoard)
        self.assertEqual(wyrm_hoard.key, "The Titanic Gold Hoard of Pyrothrax")

        sleeper_vault = find_room_by_key("rlyeh_trench_vault_of_the_sleeper")
        self.assertIsNotNone(sleeper_vault)
        self.assertEqual(sleeper_vault.key, "The Tomb of the Slumbering Elder God")

        # 2. Verify Anchors
        # foothills -> labyrinth_minos_labyrinth_minos_bronze_gate
        foothills = find_room_by_key("foothills")
        ex_to_maze = [ex for ex in foothills.exits if "maze of daedalus" in ex.key]
        self.assertTrue(len(ex_to_maze) > 0)
        self.assertEqual(ex_to_maze[0].destination.db.room_key, "labyrinth_minos_labyrinth_minos_bronze_gate")

        # north_gate -> ankh_morpork_ankh_morpork_brass_bridge_wharf
        north_gate = find_room_by_key("north_gate")
        ex_to_ankh = [ex for ex in north_gate.exits if "brass bridge" in ex.key]
        self.assertTrue(len(ex_to_ankh) > 0)
        self.assertEqual(ex_to_ankh[0].destination.db.room_key, "ankh_morpork_ankh_morpork_brass_bridge_wharf")

        # chasm_bridge -> dragon_wastes_dragon_wastes_cinder_pass
        chasm_bridge = find_room_by_key("chasm_bridge")
        ex_to_dragon = [ex for ex in chasm_bridge.exits if "dragon wastes" in ex.key]
        self.assertTrue(len(ex_to_dragon) > 0)
        self.assertEqual(ex_to_dragon[0].destination.db.room_key, "dragon_wastes_dragon_wastes_cinder_pass")

        # dead_mans_cove -> rlyeh_trench_rlyeh_trench_cyclopean_pylon
        cove = find_room_by_key("dead_mans_cove")
        ex_to_rlyeh = [ex for ex in cove.exits if "cyclopean trench" in ex.key]
        self.assertTrue(len(ex_to_rlyeh) > 0)
        self.assertEqual(ex_to_rlyeh[0].destination.db.room_key, "rlyeh_trench_rlyeh_trench_cyclopean_pylon")

        # 3. Verify Bosses
        asterion = [c for c in minos_altar.contents if c.key == "Asterion the Minotaur King"][0]
        self.assertEqual(asterion.db.level, 15)
        self.assertGreaterEqual(asterion.db.hp, 400)

        vetinari = [c for c in vetinari_office.contents if c.key == "Lord Havelock Vetinari"][0]
        self.assertEqual(vetinari.db.level, 14)
        self.assertGreaterEqual(vetinari.db.hp, 350)

        pyrothrax = [c for c in wyrm_hoard.contents if c.key == "Pyrothrax the Ancient Red Wyrm"][0]
        self.assertEqual(pyrothrax.db.level, 26)
        self.assertGreaterEqual(pyrothrax.db.hp, 1400)

        sleeper = [c for c in sleeper_vault.contents if c.key == "The Sleeper of R'lyeh"][0]
        self.assertEqual(sleeper.db.level, 30)
        self.assertGreaterEqual(sleeper.db.hp, 1800)

        # 4. Verify Ankh-Morpork Cargo-Barge Route
        self.assertIn("ankh_barge", sailing.FERRY_ROUTES)
        barge = sailing.FERRY_ROUTES["ankh_barge"]
        self.assertEqual(barge["operator"], "Bargemaster C.M.O.T. Dibbler")
        self.assertIn("south_docks", barge["ports"])
        self.assertIn("ankh_morpork_brass_bridge_wharf", barge["ports"])

        barge_deck = find_room_by_key("ankh_barge_deck")
        self.assertIsNotNone(barge_deck)
        self.assertIn("Pride of the Ankh", barge_deck.key)

    def test_bulk_ingestion_part10(self):
        """Verify ingestion of Part 10 '2,000+ Rooms Milestone' (241 rooms, Tomb of Horrors, City of Brass, Mithral Hall, Kraken Trench)."""
        report = run_bulk_ingestion_part10(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 800)
        self.assertGreaterEqual(report["npcs_created"], 40)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        acererak_crypt = find_room_by_key("tomb_of_horrors_mithral_vault_sanctum")
        self.assertIsNotNone(acererak_crypt)
        self.assertEqual(acererak_crypt.key, "The Crypt of Acererak the Demilich")

        sultan_throne = find_room_by_key("city_of_brass_sultan_throne_of_flames")
        self.assertIsNotNone(sultan_throne)
        self.assertEqual(sultan_throne.key, "The Smoldering Throne of Grand Sultan Al-Malik")

        shimmergloom_chasm = find_room_by_key("mithral_hall_shimmergloom_shadow_chasm")
        self.assertIsNotNone(shimmergloom_chasm)
        self.assertEqual(shimmergloom_chasm.key, "The Abyssal Lair of Shimmergloom")

        kraken_abyss = find_room_by_key("kraken_trench_kraken_deep_trench_abyss")
        self.assertIsNotNone(kraken_abyss)
        self.assertEqual(kraken_abyss.key, "The Leviathan Abyss of the Ancient Kraken")

        # 2. Verify Anchors
        # catacombs -> tomb_of_horrors_tomb_entrance_false_portal
        catacombs = find_room_by_key("catacombs")
        ex_to_tomb = [ex for ex in catacombs.exits if "tomb of horrors" in ex.key]
        self.assertTrue(len(ex_to_tomb) > 0)
        self.assertEqual(ex_to_tomb[0].destination.db.room_key, "tomb_of_horrors_tomb_entrance_false_portal")

        # chasm_bridge -> city_of_brass_city_of_brass_obsidian_pier
        chasm_bridge = find_room_by_key("chasm_bridge")
        ex_to_brass = [ex for ex in chasm_bridge.exits if "planar fire portal" in ex.key]
        self.assertTrue(len(ex_to_brass) > 0)
        self.assertEqual(ex_to_brass[0].destination.db.room_key, "city_of_brass_city_of_brass_obsidian_pier")

        # frostfang_pass -> mithral_hall_mithral_hall_valley_gates
        frostfang = find_room_by_key("frostfang_pass")
        ex_to_mithral = [ex for ex in frostfang.exits if "mithral hall" in ex.key]
        self.assertTrue(len(ex_to_mithral) > 0)
        self.assertEqual(ex_to_mithral[0].destination.db.room_key, "mithral_hall_mithral_hall_valley_gates")

        # dead_mans_cove -> kraken_trench_kraken_trench_abyssal_rim
        cove = find_room_by_key("dead_mans_cove")
        ex_to_kraken = [ex for ex in cove.exits if "midnight abyss trench" in ex.key]
        self.assertTrue(len(ex_to_kraken) > 0)
        self.assertEqual(ex_to_kraken[0].destination.db.room_key, "kraken_trench_kraken_trench_abyssal_rim")

        # 3. Verify Bosses
        acererak = [c for c in acererak_crypt.contents if c.key == "Acererak the Demilich"][0]
        self.assertEqual(acererak.db.level, 28)
        self.assertGreaterEqual(acererak.db.hp, 1400)

        sultan = [c for c in sultan_throne.contents if c.key == "Grand Sultan Al-Malik of the Smoldering Throne"][0]
        self.assertEqual(sultan.db.level, 25)
        self.assertGreaterEqual(sultan.db.hp, 1200)

        shimmergloom = [c for c in shimmergloom_chasm.contents if c.key == "Shimmergloom the Shadow Dragon"][0]
        self.assertEqual(shimmergloom.db.level, 22)
        self.assertGreaterEqual(shimmergloom.db.hp, 1000)

        kraken = [c for c in kraken_abyss.contents if c.key == "The Ancient Kraken Leviathan"][0]
        self.assertEqual(kraken.db.level, 24)
        self.assertGreaterEqual(kraken.db.hp, 1200)

        # 4. Verify Planar Skiff Route
        self.assertIn("sultana_skiff", sailing.FERRY_ROUTES)
        skiff = sailing.FERRY_ROUTES["sultana_skiff"]
        self.assertEqual(skiff["operator"], "Efreet Helmsman Malik")
        self.assertIn("south_docks", skiff["ports"])
        self.assertIn("city_of_brass_obsidian_pier", skiff["ports"])

        sultana_deck = find_room_by_key("sultana_deck")
        self.assertIsNotNone(sultana_deck)
        self.assertIn("Sultana", sultana_deck.key)

    def test_bulk_ingestion_part11(self):
        """Verify ingestion of Part 11 '2,300+ Rooms Milestone' (241 rooms, Astral Dreadnought, Fane of Night Serpent, Svardborg Glacier, Moil)."""
        report = run_bulk_ingestion_part11(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 800)
        self.assertGreaterEqual(report["npcs_created"], 40)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        valketh_dais = find_room_by_key("astral_dreadnought_astral_void_apex")
        self.assertIsNotNone(valketh_dais)
        self.assertEqual(valketh_dais.key, "The Astral Dais of Inquisitor Val'keth")

        ras_nsi_throne = find_room_by_key("fane_night_serpent_hierophant_sanctum_chamber")
        self.assertIsNotNone(ras_nsi_throne)
        self.assertEqual(ras_nsi_throne.key, "The Throne Room of Ras Nsi")

        storvald_throne = find_room_by_key("svardborg_glacier_jarl_storvald_ice_throne")
        self.assertIsNotNone(storvald_throne)
        self.assertEqual(storvald_throne.key, "The Permafrost Throne of Jarl Storvald")

        moil_throne = find_room_by_key("shadowfell_moil_throne_of_the_void_sovereign")
        self.assertIsNotNone(moil_throne)
        self.assertEqual(moil_throne.key, "The Obsidian Throne of Malchor the Sovereign")

        # 2. Verify Anchors
        # summit -> astral_dreadnought_astral_silver_wharf
        summit = find_room_by_key("summit")
        ex_to_astral = [ex for ex in summit.exits if "astral silver void" in ex.key]
        self.assertTrue(len(ex_to_astral) > 0)
        self.assertEqual(ex_to_astral[0].destination.db.room_key, "astral_dreadnought_astral_silver_wharf")

        # marshland -> fane_night_serpent_omu_ruined_gateway
        marshland = find_room_by_key("marshland")
        ex_to_fane = [ex for ex in marshland.exits if "sunken serpent fane" in ex.key]
        self.assertTrue(len(ex_to_fane) > 0)
        self.assertEqual(ex_to_fane[0].destination.db.room_key, "fane_night_serpent_omu_ruined_gateway")

        # watchtower -> svardborg_glacier_svardborg_glacier_pier
        watchtower = find_room_by_key("watchtower")
        ex_to_svardborg = [ex for ex in watchtower.exits if "svardborg" in ex.key]
        self.assertTrue(len(ex_to_svardborg) > 0)
        self.assertEqual(ex_to_svardborg[0].destination.db.room_key, "svardborg_glacier_svardborg_glacier_pier")

        # ossuary -> shadowfell_moil_moil_chain_bridge_entry
        ossuary = find_room_by_key("ossuary")
        ex_to_moil = [ex for ex in ossuary.exits if "chained void bridge" in ex.key]
        self.assertTrue(len(ex_to_moil) > 0)
        self.assertEqual(ex_to_moil[0].destination.db.room_key, "shadowfell_moil_moil_chain_bridge_entry")

        # 3. Verify Bosses
        valketh = [c for c in valketh_dais.contents if c.key == "Vlaakith's Inquisitor-General Val'keth"][0]
        self.assertEqual(valketh.db.level, 27)
        self.assertGreaterEqual(valketh.db.hp, 1400)

        ras_nsi = [c for c in ras_nsi_throne.contents if c.key == "Ras Nsi the Yuan-ti High Hierophant"][0]
        self.assertEqual(ras_nsi.db.level, 24)
        self.assertGreaterEqual(ras_nsi.db.hp, 1200)

        storvald = [c for c in storvald_throne.contents if c.key == "Jarl Storvald the Frost Giant King"][0]
        self.assertEqual(storvald.db.level, 25)
        self.assertGreaterEqual(storvald.db.hp, 1200)

        malchor = [c for c in moil_throne.contents if c.key == "Malchor the Sovereign of Moil"][0]
        self.assertEqual(malchor.db.level, 29)
        self.assertGreaterEqual(malchor.db.hp, 1500)

        # 4. Verify Icebreaker Transit Route
        self.assertIn("icebreaker_ship", sailing.FERRY_ROUTES)
        icebreaker = sailing.FERRY_ROUTES["icebreaker_ship"]
        self.assertEqual(icebreaker["operator"], "First Mate Torvald")
        self.assertIn("south_docks", icebreaker["ports"])
        self.assertIn("svardborg_glacier_pier", icebreaker["ports"])

        icebreaker_deck = find_room_by_key("icebreaker_deck")
        self.assertIsNotNone(icebreaker_deck)
        self.assertIn("Winter's Fang", icebreaker_deck.key)

    def test_bulk_ingestion_part12(self):
        """Verify ingestion of Part 12 '2,500+ Rooms Milestone' (241 rooms, Menzoberranzan, Skyreach Castle, Myth Drannor, Hells of Dis)."""
        report = run_bulk_ingestion_part12(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 800)
        self.assertGreaterEqual(report["npcs_created"], 40)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        quenthel_throne = find_room_by_key("menzoberranzan_quenthel_baenre_throne")
        self.assertIsNotNone(quenthel_throne)
        self.assertEqual(quenthel_throne.key, "The Throne Room of Matron Mother Quenthel")

        blagothkus_hall = find_room_by_key("skyreach_castle_blagothkus_throne_hall")
        self.assertIsNotNone(blagothkus_hall)
        self.assertEqual(blagothkus_hall.key, "The Cloudstone Throne of Count Blagothkus")

        despoiler_sanctum = find_room_by_key("myth_drannor_despoiler_spire_sanctum")
        self.assertIsNotNone(despoiler_sanctum)
        self.assertEqual(despoiler_sanctum.key, "The Spire of the Phaerimm Despoiler")

        dispater_apex = find_room_by_key("hells_dis_iron_tower_dispater_iron_tower_apex")
        self.assertIsNotNone(dispater_apex)
        self.assertEqual(dispater_apex.key, "The Throne of Archduke Dispater")

        # 2. Verify Anchors
        # rail_hub -> menzoberranzan_menzo_tier_breche_gates
        rail_hub = find_room_by_key("rail_hub")
        ex_to_menzo = [ex for ex in rail_hub.exits if "menzoberranzan" in ex.key]
        self.assertTrue(len(ex_to_menzo) > 0)
        self.assertEqual(ex_to_menzo[0].destination.db.room_key, "menzoberranzan_menzo_tier_breche_gates")

        # summit -> skyreach_castle_skyreach_castle_cloud_gate
        summit = find_room_by_key("summit")
        ex_to_skyreach = [ex for ex in summit.exits if "skyreach" in ex.key]
        self.assertTrue(len(ex_to_skyreach) > 0)
        self.assertEqual(ex_to_skyreach[0].destination.db.room_key, "skyreach_castle_skyreach_castle_cloud_gate")

        # deep_woods -> myth_drannor_myth_drannor_ancient_mythal_gate
        deep_woods = find_room_by_key("deep_woods")
        ex_to_mythal = [ex for ex in deep_woods.exits if "mythal portal" in ex.key]
        self.assertTrue(len(ex_to_mythal) > 0)
        self.assertEqual(ex_to_mythal[0].destination.db.room_key, "myth_drannor_myth_drannor_ancient_mythal_gate")

        # bazaar -> hells_dis_iron_tower_dis_iron_gate_of_chains
        bazaar = find_room_by_key("bazaar")
        ex_to_dis = [ex for ex in bazaar.exits if "infernal gate into dis" in ex.key]
        self.assertTrue(len(ex_to_dis) > 0)
        self.assertEqual(ex_to_dis[0].destination.db.room_key, "hells_dis_iron_tower_dis_iron_gate_of_chains")

        # 3. Verify Bosses
        quenthel = [c for c in quenthel_throne.contents if c.key == "Matron Mother Quenthel Baenre"][0]
        self.assertEqual(quenthel.db.level, 26)
        self.assertGreaterEqual(quenthel.db.hp, 1400)

        blagothkus = [c for c in blagothkus_hall.contents if c.key == "Blagothkus the Cloud Giant Count"][0]
        self.assertEqual(blagothkus.db.level, 25)
        self.assertGreaterEqual(blagothkus.db.hp, 1200)

        phaerimm = [c for c in despoiler_sanctum.contents if c.key == "The Eldritch Phaerimm Despoiler"][0]
        self.assertEqual(phaerimm.db.level, 24)
        self.assertGreaterEqual(phaerimm.db.hp, 1200)

        dispater = [c for c in dispater_apex.contents if c.key == "Archduke Dispater of the Iron Tower"][0]
        self.assertEqual(dispater.db.level, 29)
        self.assertGreaterEqual(dispater.db.hp, 1500)

        # 4. Verify Nightfall Skyship Transit Route
        self.assertIn("nightfall_skyship", sailing.FERRY_ROUTES)
        skyship = sailing.FERRY_ROUTES["nightfall_skyship"]
        self.assertEqual(skyship["operator"], "Netherese Arcanist Kaelen")
        self.assertIn("south_docks", skyship["ports"])
        self.assertIn("skyreach_castle_cloud_gate", skyship["ports"])

        nightfall_deck = find_room_by_key("nightfall_deck")
        self.assertIsNotNone(nightfall_deck)
        self.assertIn("Nightfall", nightfall_deck.key)

    def test_bulk_ingestion_part13(self):
        """Verify ingestion of Part 13 '2,800 Rooms Milestone' (241 rooms, Oolacile Abyss, Lantan, Limbo, Ythryn)."""
        report = run_bulk_ingestion_part13(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 800)
        self.assertGreaterEqual(report["npcs_created"], 40)
        self.assertGreaterEqual(report["items_created"], 15)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        manus_lair = find_room_by_key("abyss_oolacile_manus_father_of_abyss_lair")
        self.assertIsNotNone(manus_lair)
        self.assertEqual(manus_lair.key, "The Primordial Bed of Manus")

        beldon_workshop = find_room_by_key("clockwork_lantan_master_artificer_beldon_workshop")
        self.assertIsNotNone(beldon_workshop)
        self.assertEqual(beldon_workshop.key, "The Master Workshop of Grand Artificer Beldon")

        zaer_sanctum = find_room_by_key("limbo_monasteries_anarch_zaer_inner_sanctum")
        self.assertIsNotNone(zaer_sanctum)
        self.assertEqual(zaer_sanctum.key, "The Inner Sanctum of Supreme Anarch Zaer")

        iriolarthas_crypt = find_room_by_key("ythryn_necropolis_crypt_of_demilich_iriolarthas")
        self.assertIsNotNone(iriolarthas_crypt)
        self.assertEqual(iriolarthas_crypt.key, "The Sanctum of Demilich Iriolarthas")

        # 2. Verify Anchors
        # catacombs -> abyss_oolacile_oolacile_sanctuary_garden_gate
        catacombs = find_room_by_key("catacombs")
        ex_to_abyss = [ex for ex in catacombs.exits if "abyss rift of oolacile" in ex.key]
        self.assertTrue(len(ex_to_abyss) > 0)
        self.assertEqual(ex_to_abyss[0].destination.db.room_key, "abyss_oolacile_oolacile_sanctuary_garden_gate")

        # rail_hub -> clockwork_lantan_lantan_pneumatic_rail_terminal
        rail_hub = find_room_by_key("rail_hub")
        ex_to_lantan = [ex for ex in rail_hub.exits if "pneumatic express to lantan" in ex.key]
        self.assertTrue(len(ex_to_lantan) > 0)
        self.assertEqual(ex_to_lantan[0].destination.db.room_key, "clockwork_lantan_lantan_pneumatic_rail_terminal")

        # summit -> limbo_monasteries_limbo_chaos_island_rim
        summit = find_room_by_key("summit")
        ex_to_limbo = [ex for ex in summit.exits if "churning chaos of limbo" in ex.key]
        self.assertTrue(len(ex_to_limbo) > 0)
        self.assertEqual(ex_to_limbo[0].destination.db.room_key, "limbo_monasteries_limbo_chaos_island_rim")

        # frostfang_pass -> ythryn_necropolis_ythryn_glacier_shaft_entrance
        frostfang = find_room_by_key("frostfang_pass")
        ex_to_ythryn = [ex for ex in frostfang.exits if "glacial shaft into ythryn" in ex.key]
        self.assertTrue(len(ex_to_ythryn) > 0)
        self.assertEqual(ex_to_ythryn[0].destination.db.room_key, "ythryn_necropolis_ythryn_glacier_shaft_entrance")

        # 3. Verify Bosses
        manus = [c for c in manus_lair.contents if c.key == "Manus, Father of the Abyss"][0]
        self.assertEqual(manus.db.level, 28)
        self.assertGreaterEqual(manus.db.hp, 1400)

        beldon = [c for c in beldon_workshop.contents if c.key == "Grand Artificer Beldon the Gearsmith"][0]
        self.assertEqual(beldon.db.level, 22)
        self.assertGreaterEqual(beldon.db.hp, 1000)

        zaer = [c for c in zaer_sanctum.contents if c.key == "Supreme Zerth Anarch Zaer"][0]
        self.assertEqual(zaer.db.level, 25)
        self.assertGreaterEqual(zaer.db.hp, 1200)

        iriolarthas = [c for c in iriolarthas_crypt.contents if c.key == "Iriolarthas the Netherese Demilich"][0]
        self.assertEqual(iriolarthas.db.level, 29)
        self.assertGreaterEqual(iriolarthas.db.hp, 1500)

        # 4. Verify Iron Drake Transit Route
        self.assertIn("iron_drake_ship", sailing.FERRY_ROUTES)
        steamship = sailing.FERRY_ROUTES["iron_drake_ship"]
        self.assertEqual(steamship["operator"], "Chief Engineer Sparkplug")
        self.assertIn("south_docks", steamship["ports"])
        self.assertIn("clockwork_lantan_harbor", steamship["ports"])

        iron_drake_deck = find_room_by_key("iron_drake_deck")
        self.assertIsNotNone(iron_drake_deck)
        self.assertIn("Iron Drake", iron_drake_deck.key)

    def test_bulk_world_ingestion_part14(self):
        """Verify Part 14: 3,000+ Rooms Epic Milestone (Atlantis, Celestia Spire, Sigil, Muspelheim, Voidstrider)."""
        report = run_bulk_ingestion_part14(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 850)
        self.assertGreaterEqual(report["npcs_created"], 60)
        self.assertGreaterEqual(report["items_created"], 10)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        atlantis_throne = find_room_by_key("sunken_atlantis_atlantis_poseidon_throne")
        self.assertIsNotNone(atlantis_throne)
        self.assertEqual(atlantis_throne.key, "The Oceanic Throne of King Amphitrite")

        celestia_throne = find_room_by_key("celestia_spire_celestia_spire_seven_heavens_throne")
        self.assertIsNotNone(celestia_throne)
        self.assertEqual(celestia_throne.key, "The High Throne of Archon Lord Raziel")

        sigil_apex = find_room_by_key("sigil_doors_sigil_doors_spire_apex")
        self.assertIsNotNone(sigil_apex)
        self.assertEqual(sigil_apex.key, "The High Balcony of the Spire Apex")

        surtr_throne = find_room_by_key("muspelheim_forge_muspelheim_surtr_throne_of_flame")
        self.assertIsNotNone(surtr_throne)
        self.assertEqual(surtr_throne.key, "The Molten Throne of King Surtr")

        # 2. Verify Anchors
        # dead_mans_cove -> sunken_atlantis_atlantis_pearly_archway
        cove = find_room_by_key("dead_mans_cove")
        ex_to_atlantis = [ex for ex in cove.exits if "abyssal trench towards atlantis" in ex.key]
        self.assertTrue(len(ex_to_atlantis) > 0)
        self.assertEqual(ex_to_atlantis[0].destination.db.room_key, "sunken_atlantis_atlantis_pearly_archway")

        # cathedral -> celestia_spire_celestia_spire_silver_shore
        cathedral = find_room_by_key("cathedral")
        ex_to_celestia = [ex for ex in cathedral.exits if "mount celestia spire" in ex.key]
        self.assertTrue(len(ex_to_celestia) > 0)
        self.assertEqual(ex_to_celestia[0].destination.db.room_key, "celestia_spire_celestia_spire_silver_shore")

        # plaza -> sigil_doors_sigil_doors_portal_gateway
        plaza = find_room_by_key("plaza")
        ex_to_sigil = [ex for ex in plaza.exits if "into sigil" in ex.key]
        self.assertTrue(len(ex_to_sigil) > 0)
        self.assertEqual(ex_to_sigil[0].destination.db.room_key, "sigil_doors_sigil_doors_portal_gateway")

        # city_of_brass_obsidian_pier -> muspelheim_forge_muspelheim_basalt_bridge
        brass_pier = find_room_by_key("city_of_brass_obsidian_pier")
        ex_to_muspelheim = [ex for ex in brass_pier.exits if "into muspelheim" in ex.key]
        self.assertTrue(len(ex_to_muspelheim) > 0)
        self.assertEqual(ex_to_muspelheim[0].destination.db.room_key, "muspelheim_forge_muspelheim_basalt_bridge")

        # 3. Verify Bosses
        amphitrite = [c for c in atlantis_throne.contents if c.key == "King Amphitrite of the Deep Trench"][0]
        self.assertEqual(amphitrite.db.level, 28)
        self.assertGreaterEqual(amphitrite.db.hp, 1780)

        raziel = [c for c in celestia_throne.contents if c.key == "Archon Lord Raziel"][0]
        self.assertEqual(raziel.db.level, 28)
        self.assertGreaterEqual(raziel.db.hp, 1780)

        dabus = [c for c in sigil_apex.contents if c.key == "High Dabus Factotum of the Lady"][0]
        self.assertEqual(dabus.db.level, 27)
        self.assertGreaterEqual(dabus.db.hp, 1720)

        surtr = [c for c in surtr_throne.contents if c.key == "Surtr, King of Fire Giants"][0]
        self.assertEqual(surtr.db.level, 30)
        self.assertGreaterEqual(surtr.db.hp, 1900)

        # 4. Verify Voidstrider Transit Route
        self.assertIn("voidstrider_skiff", sailing.FERRY_ROUTES)
        skiff = sailing.FERRY_ROUTES["voidstrider_skiff"]
        self.assertEqual(skiff["operator"], "Void-Captain Zephyrus")
        self.assertIn("south_docks", skiff["ports"])
        self.assertIn("sigil_doors_portal_gateway", skiff["ports"])

        voidstrider_deck = find_room_by_key("voidstrider_deck")
        self.assertIsNotNone(voidstrider_deck)
        self.assertIn("Voidstrider", voidstrider_deck.key)

    def test_bulk_world_ingestion_part15(self):
        """Verify Part 15: 3,250+ Rooms Grand Expansion (Mechanus, Summer Court, Shadowfell, Ched Nasad, Gossamer Swan)."""
        report = run_bulk_ingestion_part15(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 850)
        self.assertGreaterEqual(report["npcs_created"], 60)
        self.assertGreaterEqual(report["items_created"], 10)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        primus_throne = find_room_by_key("mechanus_gears_mechanus_primus_throne_of_order")
        self.assertIsNotNone(primus_throne)
        self.assertEqual(primus_throne.key, "The Infinity Throne of Primus")

        titania_bower = find_room_by_key("summer_court_summer_court_titania_throne_bower")
        self.assertIsNotNone(titania_bower)
        self.assertEqual(titania_bower.key, "The Living Bower Throne of Queen Titania")

        raven_throne = find_room_by_key("shadowfell_raven_shadowfell_raven_throne_of_the_raven_queen")
        self.assertIsNotNone(raven_throne)
        self.assertEqual(raven_throne.key, "The Throne of Frozen Memories")

        ched_nasad_throne = find_room_by_key("ched_nasad_ched_nasad_throne_of_the_web_mother")
        self.assertIsNotNone(ched_nasad_throne)
        self.assertEqual(ched_nasad_throne.key, "The Throne of the Supreme Matron Mother")

        # 2. Verify Anchors
        # rail_hub -> mechanus_gears_mechanus_planetary_gear_platform
        rail_hub = find_room_by_key("rail_hub")
        ex_to_mechanus = [ex for ex in rail_hub.exits if "gear portal to mechanus" in ex.key]
        self.assertTrue(len(ex_to_mechanus) > 0)
        self.assertEqual(ex_to_mechanus[0].destination.db.room_key, "mechanus_gears_mechanus_planetary_gear_platform")

        # deep_woods -> summer_court_summer_court_emerald_gateway
        woods = find_room_by_key("deep_woods")
        ex_to_summer = [ex for ex in woods.exits if "into summer court" in ex.key]
        self.assertTrue(len(ex_to_summer) > 0)
        self.assertEqual(ex_to_summer[0].destination.db.room_key, "summer_court_summer_court_emerald_gateway")

        # ossuary -> shadowfell_raven_shadowfell_raven_black_gate
        ossuary = find_room_by_key("ossuary")
        ex_to_shadow = [ex for ex in ossuary.exits if "fortress of memories" in ex.key]
        self.assertTrue(len(ex_to_shadow) > 0)
        self.assertEqual(ex_to_shadow[0].destination.db.room_key, "shadowfell_raven_shadowfell_raven_black_gate")

        # chasm_bridge -> ched_nasad_ched_nasad_web_bridge_rim
        bridge = find_room_by_key("chasm_bridge")
        ex_to_ched = [ex for ex in bridge.exits if "chasm of ched nasad" in ex.key]
        self.assertTrue(len(ex_to_ched) > 0)
        self.assertEqual(ex_to_ched[0].destination.db.room_key, "ched_nasad_ched_nasad_web_bridge_rim")

        # 3. Verify Bosses
        primus = [c for c in primus_throne.contents if c.key == "Primus, Lord of the Modrons"][0]
        self.assertEqual(primus.db.level, 28)
        self.assertGreaterEqual(primus.db.hp, 1780)

        titania = [c for c in titania_bower.contents if c.key == "Queen Titania of the Summer Court"][0]
        self.assertEqual(titania.db.level, 26)
        self.assertGreaterEqual(titania.db.hp, 1660)

        sorrow_knight = [c for c in raven_throne.contents if c.key == "The Raven Queen's High Sorrow Knight"][0]
        self.assertEqual(sorrow_knight.db.level, 29)
        self.assertGreaterEqual(sorrow_knight.db.hp, 1840)

        matron = [c for c in ched_nasad_throne.contents if c.key == "Matron Mother of the Web-Sisters"][0]
        self.assertEqual(matron.db.level, 28)
        self.assertGreaterEqual(matron.db.hp, 1780)

        # 4. Verify Gossamer Swan Transit Route
        self.assertIn("gossamer_swan_barge", sailing.FERRY_ROUTES)
        swan = sailing.FERRY_ROUTES["gossamer_swan_barge"]
        self.assertEqual(swan["operator"], "Eladrin Swan-Keeper Liriel")
        self.assertIn("south_docks", swan["ports"])
        self.assertIn("summer_court_emerald_gateway", swan["ports"])

        swan_deck = find_room_by_key("gossamer_swan_deck")
        self.assertIsNotNone(swan_deck)
        self.assertIn("Gossamer Swan", swan_deck.key)

    def test_bulk_world_ingestion_part16(self):
        """Verify Part 16: 3,500+ Rooms Epic Expansion (Tiamat, Djinn, Gorgon, Sargasso, Wind Dancer)."""
        report = run_bulk_ingestion_part16(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 850)
        self.assertGreaterEqual(report["npcs_created"], 60)
        self.assertGreaterEqual(report["items_created"], 10)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        tiamat_throne = find_room_by_key("tiamat_abyss_tiamat_throne_of_the_dragon_queen")
        self.assertIsNotNone(tiamat_throne)
        self.assertEqual(tiamat_throne.key, "The Wyrmtooth Throne of Tiamat")

        djinn_throne = find_room_by_key("djinn_caliphate_djinn_caliphate_throne_of_the_caliph")
        self.assertIsNotNone(djinn_throne)
        self.assertEqual(djinn_throne.key, "The Cloud Throne of Caliph Al-Zahr")

        gorgon_throne = find_room_by_key("petrified_forest_petrified_forest_throne_of_the_gorgon")
        self.assertIsNotNone(gorgon_throne)
        self.assertEqual(gorgon_throne.key, "The Petrified Throne of Stheno")

        davy_jones_throne = find_room_by_key("sargasso_graveyard_sargasso_graveyard_throne_of_davy_jones")
        self.assertIsNotNone(davy_jones_throne)
        self.assertEqual(davy_jones_throne.key, "The Abyssal Helm of Davy Jones")

        # 2. Verify Anchors
        # chasm_bridge -> tiamat_abyss_tiamat_wyrmtooth_chasm_entrance
        chasm = find_room_by_key("chasm_bridge")
        ex_to_tiamat = [ex for ex in chasm.exits if "wyrmtooth abyss of tiamat" in ex.key]
        self.assertTrue(len(ex_to_tiamat) > 0)
        self.assertEqual(ex_to_tiamat[0].destination.db.room_key, "tiamat_abyss_tiamat_wyrmtooth_chasm_entrance")

        # summit -> djinn_caliphate_djinn_caliphate_cloud_docks
        summit = find_room_by_key("summit")
        ex_to_djinn = [ex for ex in summit.exits if "cloud docks of mount qaf" in ex.key]
        self.assertTrue(len(ex_to_djinn) > 0)
        self.assertEqual(ex_to_djinn[0].destination.db.room_key, "djinn_caliphate_djinn_caliphate_cloud_docks")

        # foothills -> petrified_forest_petrified_forest_gnarled_verge
        foothills = find_room_by_key("foothills")
        ex_to_gorgon = [ex for ex in foothills.exits if "petrified forest of the gorgon" in ex.key]
        self.assertTrue(len(ex_to_gorgon) > 0)
        self.assertEqual(ex_to_gorgon[0].destination.db.room_key, "petrified_forest_petrified_forest_gnarled_verge")

        # dead_mans_cove -> sargasso_graveyard_sargasso_graveyard_rotting_wharf
        cove = find_room_by_key("dead_mans_cove")
        ex_to_sargasso = [ex for ex in cove.exits if "sargasso galleon graveyard" in ex.key]
        self.assertTrue(len(ex_to_sargasso) > 0)
        self.assertEqual(ex_to_sargasso[0].destination.db.room_key, "sargasso_graveyard_sargasso_graveyard_rotting_wharf")

        # 3. Verify Bosses
        tiamat = [c for c in tiamat_throne.contents if c.key == "Avatar of Tiamat, the Dragon Queen"][0]
        self.assertEqual(tiamat.db.level, 30)
        self.assertGreaterEqual(tiamat.db.hp, 1900)

        caliph = [c for c in djinn_throne.contents if c.key == "Caliph Al-Zahr of the Zephyr Winds"][0]
        self.assertEqual(caliph.db.level, 28)
        self.assertGreaterEqual(caliph.db.hp, 1780)

        stheno = [c for c in gorgon_throne.contents if c.key == "Stheno, the Immortal Gorgon Matriarch"][0]
        self.assertEqual(stheno.db.level, 26)
        self.assertGreaterEqual(stheno.db.hp, 1660)

        davy = [c for c in davy_jones_throne.contents if c.key == "Captain Davy Jones, Warden of the Deep"][0]
        self.assertEqual(davy.db.level, 27)
        self.assertGreaterEqual(davy.db.hp, 1720)

        # 4. Verify Wind Dancer Transit Route
        self.assertIn("wind_dancer_ship", sailing.FERRY_ROUTES)
        skyship = sailing.FERRY_ROUTES["wind_dancer_ship"]
        self.assertEqual(skyship["operator"], "Djinn Navigator Rashid")
        self.assertIn("south_docks", skyship["ports"])
        self.assertIn("djinn_caliphate_cloud_docks", skyship["ports"])

        wind_deck = find_room_by_key("wind_dancer_deck")
        self.assertIsNotNone(wind_deck)
        self.assertIn("Wind Dancer", wind_deck.key)

    def test_bulk_world_ingestion_part17(self):
        """Verify Part 17: 3,750+ Rooms Grand Empire Expansion (Sunless Citadel, Githyanki Warship, Olympus, Skullport, Royal Coach)."""
        report = run_bulk_ingestion_part17(clean_existing=True)

        self.assertEqual(report["zones_processed"], 4)
        self.assertEqual(report["rooms_created"], 241)
        self.assertGreaterEqual(report["exits_created"], 850)
        self.assertGreaterEqual(report["npcs_created"], 60)
        self.assertGreaterEqual(report["items_created"], 10)
        self.assertEqual(len(report["anchors_established"]), 4)

        # 1. Verify key rooms in each zone
        citadel_heart = find_room_by_key("sunless_citadel_sunless_citadel_gulthias_tree_heart")
        self.assertIsNotNone(citadel_heart)
        self.assertEqual(citadel_heart.key, "The Heart of the Gulthias Tree")

        githyanki_helm = find_room_by_key("githyanki_warship_githyanki_warship_kithrak_command_bridge")
        self.assertIsNotNone(githyanki_helm)
        self.assertEqual(githyanki_helm.key, "The Helm of Kith'rak Voss")

        olympus_throne = find_room_by_key("olympus_spire_olympus_spire_throne_of_thunder")
        self.assertIsNotNone(olympus_throne)
        self.assertEqual(olympus_throne.key, "The Cloud Throne of Olympian Thunder")

        skullport_throne = find_room_by_key("skullport_shadows_skullport_shadows_throne_of_the_skum_lord")
        self.assertIsNotNone(skullport_throne)
        self.assertEqual(skullport_throne.key, "The Throne of the Skum-Lord")

        # 2. Verify Anchors
        # catacombs -> sunless_citadel_sunless_citadel_chasm_stairs
        catacombs = find_room_by_key("catacombs")
        ex_to_citadel = [ex for ex in catacombs.exits if "into sunless citadel" in ex.key]
        self.assertTrue(len(ex_to_citadel) > 0)
        self.assertEqual(ex_to_citadel[0].destination.db.room_key, "sunless_citadel_sunless_citadel_chasm_stairs")

        # astral_nexus -> githyanki_warship_githyanki_warship_stern_flight_deck
        nexus = find_room_by_key("astral_nexus")
        ex_to_warship = [ex for ex in nexus.exits if "board githyanki warship" in ex.key]
        self.assertTrue(len(ex_to_warship) > 0)
        self.assertEqual(ex_to_warship[0].destination.db.room_key, "githyanki_warship_githyanki_warship_stern_flight_deck")

        # summit -> olympus_spire_olympus_spire_golden_cloud_stair
        summit = find_room_by_key("summit")
        ex_to_olympus = [ex for ex in summit.exits if "golden cloud stair to mount olympus" in ex.key]
        self.assertTrue(len(ex_to_olympus) > 0)
        self.assertEqual(ex_to_olympus[0].destination.db.room_key, "olympus_spire_olympus_spire_golden_cloud_stair")

        # dead_mans_cove -> skullport_shadows_skullport_shadows_subterranean_wharf
        cove = find_room_by_key("dead_mans_cove")
        ex_to_skullport = [ex for ex in cove.exits if "canal tunnel to skullport" in ex.key]
        self.assertTrue(len(ex_to_skullport) > 0)
        self.assertEqual(ex_to_skullport[0].destination.db.room_key, "skullport_shadows_skullport_shadows_subterranean_wharf")

        # 3. Verify Bosses
        belak = [c for c in citadel_heart.contents if "Belak" in c.key][0]
        self.assertEqual(belak.db.level, 20)
        self.assertGreaterEqual(belak.db.hp, 1300)

        voss = [c for c in githyanki_helm.contents if "Kith'rak Voss" in c.key][0]
        self.assertEqual(voss.db.level, 28)
        self.assertGreaterEqual(voss.db.hp, 1780)

        thunder = [c for c in olympus_throne.contents if "Avatar of Olympian Thunder" in c.key][0]
        self.assertEqual(thunder.db.level, 30)
        self.assertGreaterEqual(thunder.db.hp, 1900)

        skum = [c for c in skullport_throne.contents if "Skum-Lord" in c.key][0]
        self.assertEqual(skum.db.level, 26)
        self.assertGreaterEqual(skum.db.hp, 1660)

        # 4. Verify Royal Stagecoach Route
        self.assertIn("royal_coach_line", sailing.FERRY_ROUTES)
        coach = sailing.FERRY_ROUTES["royal_coach_line"]
        self.assertEqual(coach["operator"], "Coachman Barnaby")
        self.assertIn("north_gate", coach["ports"])
        self.assertIn("foothills", coach["ports"])

        coach_room = find_room_by_key("royal_coach_interior")
        self.assertIsNotNone(coach_room)
        self.assertIn("Royal Stagecoach", coach_room.key)




