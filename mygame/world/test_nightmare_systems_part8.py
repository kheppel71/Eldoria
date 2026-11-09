"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 8):
1. Astrological Constellations & Zodiac Alignments
2. Wilderness Herbalism, Medicinal Poultices & Blade Poisons
3. Cursed Relics, Haunted Idols & Exorcism Rites
4. Mercenary Hirelings & Traveling Companions
5. Merchant Trade Caravans & Highwayman Ambushes
6. Grand Library Archives, Lore Tomes & Archaeological Research
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_astrology import (
    init_character_zodiac, set_character_zodiac, get_character_zodiac, format_constellations_display
)
from world.nightmare_herbalism import (
    forage_herbs, craft_poultice, apply_poultice, craft_poison, coat_weapon_with_poison
)
from world.nightmare_exorcism import (
    create_cursed_relic, is_cursed, inspect_curse, perform_exorcism
)
from world.nightmare_hirelings import (
    format_hirelings_display, hire_mercenary, order_mercenary, dismiss_mercenary
)
from world.nightmare_caravans import (
    format_caravans_display, join_caravan_escort, trigger_caravan_defense, ACTIVE_ESCORT_GUARDS
)
from world.nightmare_library import (
    create_lore_tome, read_lore_tome, transcribe_lore_tome, format_lore_profile
)


class TestNightmareSystemsPart8(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 8)."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Praxis High Commons")

        self.char1 = create_object(Character, key="Aurelius", location=self.room)
        self.char2 = create_object(Character, key="Sariel", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 80
        self.char1.db.max_hp = 100
        self.char1.db.coins = 500

        self.char2.db.hp = 70
        self.char2.db.max_hp = 100
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
        ACTIVE_ESCORT_GUARDS.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. ASTROLOGY & ZODIAC ALIGNMENT
    def test_astrology_zodiac(self):
        init_character_zodiac(self.char1)
        self.assertIsNotNone(self.char1.db.zodiac_sign)

        # Set specific sign
        ok, msg = set_character_zodiac(self.char1, "The Dragon")
        self.assertTrue(ok)
        zdata = get_character_zodiac(self.char1)
        self.assertEqual(zdata["name"], "The Dragon")

        disp = format_constellations_display(self.char1)
        self.assertIn("ASTRAL CONSTELLATIONS", disp)
        self.assertIn("The Dragon", disp)

    # 2. HERBALISM, POULTICES & POISONS
    def test_herbalism_and_poisons(self):
        # Forage herbs
        ok, msg = forage_herbs(self.char1)
        self.assertTrue(ok)
        has_herb = any(getattr(obj.db, "is_herb", False) for obj in self.char1.contents)
        self.assertTrue(has_herb)

        # Craft and apply healing poultice
        herb = create_object(Object, key="Kingsbloom Flower", location=self.char1)
        herb.db.is_herb = True
        herb.db.herb_type = "healing"
        herb.db.cure_amount = 35

        ok, msg = craft_poultice(self.char1)
        self.assertTrue(ok)

        old_hp = self.char1.db.hp
        ok, msg = apply_poultice(self.char1)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, old_hp)

        # Craft poison and coat weapon
        nightshade = create_object(Object, key="Nightshade Belladonna", location=self.char1)
        nightshade.db.is_herb = True
        nightshade.db.herb_type = "poison"

        ok, msg = craft_poison(self.char1)
        self.assertTrue(ok)

        dagger = create_object(Object, key="Steel Dagger", location=self.char1)
        ok, msg = coat_weapon_with_poison(self.char1, "Steel Dagger")
        self.assertTrue(ok)
        self.assertTrue(dagger.db.poison_coated)
        self.assertEqual(dagger.db.poison_charges, 5)

    # 3. CURSED RELICS & EXORCISM
    def test_cursed_relics_and_exorcism(self):
        ring = create_cursed_relic(self.char1, "whispering_ring")
        self.assertTrue(is_cursed(ring))

        info = inspect_curse(self.char1, ring)
        self.assertIn("CURSED ARTIFACT", info)

        # Perform holy exorcism
        ok, msg = perform_exorcism(self.char1, ring.key)
        self.assertTrue(ok)
        self.assertFalse(is_cursed(ring))
        self.assertIn("Cleansed", ring.key)

    # 4. MERCENARY HIRELINGS & ORDERS
    def test_mercenary_hirelings(self):
        disp = format_hirelings_display()
        self.assertIn("MERCENARY & ADVENTURER GUILD", disp)

        # Hire Duran
        ok, msg = hire_mercenary(self.char1, "duran")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.coins, 450)

        # Order hireling
        ok, msg = order_mercenary(self.char1, "Duran", "follow")
        self.assertTrue(ok)

        # Dismiss hireling
        ok, msg = dismiss_mercenary(self.char1, "Duran")
        self.assertTrue(ok)

    # 5. MERCHANT CARAVANS & HIGHWAYMAN AMBUSHES
    def test_caravans_and_ambushes(self):
        disp = format_caravans_display()
        self.assertIn("PRAXIS MERCHANT TRADE CARAVANS", disp)

        # Enlist in caravan
        ok, msg = join_caravan_escort(self.char1, "praxis_desert")
        self.assertTrue(ok)
        self.assertIn(self.char1.id, ACTIVE_ESCORT_GUARDS)

        # Trigger ambush defense
        ok, msg = trigger_caravan_defense(self.char1)
        self.assertTrue(ok)
        self.assertEqual(msg, "Ambush triggered.")

        # Deliver caravan safely
        ok, msg = trigger_caravan_defense(self.char1)
        self.assertTrue(ok)
        self.assertEqual(msg, "Caravan escorted successfully.")
        self.assertNotIn(self.char1.id, ACTIVE_ESCORT_GUARDS)

    # 6. GRAND LIBRARY & LORE TOMES
    def test_library_and_lore(self):
        tome = create_lore_tome(self.char1, "goblin_wars")
        self.assertTrue(tome.db.is_lore_tome)

        # Read tome
        ok, msg = read_lore_tome(self.char1, tome)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.lore_points, 0)
        self.assertIn("goblin_wars", self.char1.db.studied_tomes)

        # Transcribe tome
        ok, msg = transcribe_lore_tome(self.char1, tome)
        self.assertTrue(ok)
        has_notes = any("Notes" in obj.key for obj in self.char1.contents)
        self.assertTrue(has_notes)

        # Format scholar profile
        prof = format_lore_profile(self.char1)
        self.assertIn("ARCHAEOLOGICAL LORE", prof)
        self.assertIn("Chronicles of the Goblin Wars", prof)

