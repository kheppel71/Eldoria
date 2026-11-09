"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 11):
1. Siege Warfare, Battering Rams & Gate Breaching
2. Wild Horse Taming, Mustang Breaking & Breeding
3. Leatherworking, Tanning Vats & Beast Hide Curing
4. Traveling Carnival of Oddities & Games of Skill
5. Barber-Surgeon Leeching, Bloodletting & Humoral Medicine
6. Lapidary Gemcutting, Faceting & Jeweled Filigree
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_siege import (
    create_fortified_gate, create_battering_ram, assault_gate_with_ram, repair_siege_gate, format_gate_status
)
from world.nightmare_horse_taming import (
    spawn_wild_horse, lasso_wild_horse, break_wild_horse, breed_tamed_horses, format_stable_info
)
from world.nightmare_leatherworking import (
    skin_beast_carcass, cure_leather_in_vat, craft_leather_armor
)
from world.nightmare_carnival import (
    format_carnival_directory, play_high_striker, play_balloon_target
)
from world.nightmare_apothecary_leeching import (
    inspect_humors, gather_medicinal_leeches, apply_medicinal_leeches, perform_lancet_bloodletting
)
from world.nightmare_lapidary import (
    create_rough_gem, facet_rough_gemstone, craft_jeweled_filigree
)


class TestNightmareSystemsPart11(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 11)."""

    def setUp(self):
        super().setUp()
        self.courtyard = create_object(Room, key="Praxis Fortress Outer Courtyard")

        self.char1 = create_object(Character, key="Warlord_Kael", location=self.courtyard)
        self.char2 = create_object(Character, key="Apothecary_Finn", location=self.courtyard)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 80
        self.char1.db.max_hp = 100
        self.char1.db.stamina = 80
        self.char1.db.max_stamina = 100
        self.char1.db.str = 16
        self.char1.db.coins = 500

        self.char2.db.hp = 70
        self.char2.db.max_hp = 100
        self.char2.db.stamina = 90
        self.char2.db.max_stamina = 100
        self.char2.db.coins = 200

        self.c1_msgs = []
        self.c2_msgs = []

        def capture_c1(msg=None, *args, **kwargs):
            if msg is not None:
                self.c1_msgs.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.c1_msgs.append(str(t[0] if isinstance(t, tuple) else t))

        def capture_c2(msg=None, *args, **kwargs):
            if msg is not None:
                self.c2_msgs.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.c2_msgs.append(str(t[0] if isinstance(t, tuple) else t))

        self.char1.msg = capture_c1
        self.char2.msg = capture_c2

    def tearDown(self):
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.courtyard.pk:
            self.courtyard.delete()
        super().tearDown()

    # 1. SIEGE WARFARE & GATE BREACHING
    def test_siege_warfare(self):
        gate = create_fortified_gate(self.courtyard, "Iron Fortress Gate", hp=100)
        ram = create_battering_ram(self.courtyard)

        # Assault gate
        ok, msg = assault_gate_with_ram(self.char1, "Iron Fortress Gate")
        self.assertTrue(ok)
        self.assertLess(gate.db.gate_hp, 100)

        # Repair gate
        ok, msg = repair_siege_gate(self.char1, "Iron Fortress Gate")
        self.assertTrue(ok)

        status_text = format_gate_status(self.char1, "Iron Fortress Gate")
        self.assertIn("FORTIFIED GATE STATUS", status_text)

    # 2. HORSE TAMING & BREEDING
    def test_horse_taming_and_breeding(self):
        horse = spawn_wild_horse(self.courtyard, "mustang")
        self.assertFalse(horse.db.is_tamed)

        # Lasso horse
        ok, msg = lasso_wild_horse(self.char1, "mustang")
        self.assertTrue(ok)
        self.assertTrue(horse.db.is_snared)

        # Break horse
        ok, msg = break_wild_horse(self.char1, "mustang")
        self.assertTrue(ok)
        self.assertTrue(horse.db.is_tamed)

        # Spawn second tamed horse to test breeding
        horse2 = spawn_wild_horse(self.courtyard, "courser")
        horse2.db.is_tamed = True

        ok, msg = breed_tamed_horses(self.char1)
        self.assertTrue(ok)

        info = format_stable_info(self.char1, "mustang")
        self.assertIn("EQUESTRIAN STABLE PROFILE", info)

    # 3. LEATHERWORKING & TANNING
    def test_leatherworking(self):
        ok, msg = skin_beast_carcass(self.char1)
        self.assertTrue(ok)
        has_hide = any(getattr(obj.db, "is_raw_hide", False) for obj in self.char1.contents)
        self.assertTrue(has_hide)

        # Tan leather
        ok, msg = cure_leather_in_vat(self.char1)
        self.assertTrue(ok)
        has_cured = any(getattr(obj.db, "is_cured_leather", False) for obj in self.char1.contents)
        self.assertTrue(has_cured)

        # Craft boots (costs 1 roll)
        ok, msg = craft_leather_armor(self.char1, "boots")
        self.assertTrue(ok)
        has_boots = any("Boots" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_boots)

    # 4. CARNIVAL GAMES
    def test_carnival_attractions(self):
        disp = format_carnival_directory()
        self.assertIn("CARNIVAL OF ODDITIES", disp)

        # High striker
        old_coins = self.char1.db.coins
        ok, msg = play_high_striker(self.char1)
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.coins, old_coins - 5)

        # Balloon target
        ok, msg = play_balloon_target(self.char1)
        self.assertTrue(ok)

    # 5. APOTHECARY LEECHING & BLOODLETTING
    def test_apothecary_leeching(self):
        diag = inspect_humors(self.char1, self.char2)
        self.assertIn("HUMORAL MEDICAL DIAGNOSIS", diag)

        # Gather leeches
        ok, msg = gather_medicinal_leeches(self.char1)
        self.assertTrue(ok)

        # Apply leeches to char2
        old_hp = self.char2.db.hp
        ok, msg = apply_medicinal_leeches(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertGreater(self.char2.db.hp, old_hp)

        # Bloodletting
        old_hp2 = self.char2.db.hp
        ok, msg = perform_lancet_bloodletting(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertGreater(self.char2.db.hp, old_hp2)

    # 6. LAPIDARY & JEWELRY
    def test_lapidary_and_jewelry(self):
        gem = create_rough_gem(self.char1, "ruby")
        self.assertFalse(gem.db.is_faceted)

        # Facet gem
        ok, msg = facet_rough_gemstone(self.char1, "ruby")
        self.assertTrue(ok)
        self.assertTrue(gem.db.is_faceted)

        # Craft jewelry ring
        ok, msg = craft_jeweled_filigree(self.char1, "ring")
        self.assertTrue(ok)
        has_ring = any("Ring" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_ring)

