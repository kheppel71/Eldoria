"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 9):
1. Shipwright Naval Crafting, Dinghies & Oceanic Voyages
2. Runecarving, Protective Wards & Explosive Sigils
3. Wilderness Survival Camps, Canvas Tents & Hearth Warmth
4. Street Urchin Begging, Busking & Town Square Performances
5. Paleontological Fossils, Bone Restoration & Museum Curations
6. Eldritch Tarot Divination, Fate Cards & Omen Readings
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object
from typeclasses.exits import Exit

from world.nightmare_shipwright import (
    build_vessel, board_vessel, sail_vessel, toggle_anchor
)
from world.nightmare_wards import (
    carve_ward, trigger_ward_check, disarm_ward
)
from world.nightmare_survival_camp import (
    create_portable_tent, pitch_camp_tent, strike_camp_tent, kindle_campfire, rest_in_camp
)
from world.nightmare_busking import (
    beg_for_alms, perform_busking
)
from world.nightmare_fossils import (
    create_raw_fossil, clean_fossil_specimen, donate_fossil_to_museum, format_museum_display, MUSEUM_EXHIBITS
)
from world.nightmare_tarot import (
    create_tarot_deck, draw_single_fate_card, perform_three_card_spread
)


class TestNightmareSystemsPart9(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 9)."""

    def setUp(self):
        super().setUp()
        self.harbor = create_object(Room, key="Praxis Harbor Wharf")
        self.ocean = create_object(Room, key="Open Ocean Waters")

        # Create exit between harbor and ocean
        self.exit_sea = create_object(Exit, key="ocean", location=self.harbor, destination=self.ocean)

        self.char1 = create_object(Character, key="Captain_Jack", location=self.harbor)
        self.char2 = create_object(Character, key="Intruder_Dan", location=self.harbor)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 80
        self.char1.db.max_hp = 100
        self.char1.db.stamina = 70
        self.char1.db.max_stamina = 100
        self.char1.db.coins = 500

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.stamina = 100
        self.char2.db.max_stamina = 100

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
        MUSEUM_EXHIBITS.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.exit_sea.pk:
            self.exit_sea.delete()
        if self.harbor.pk:
            self.harbor.delete()
        if self.ocean.pk:
            self.ocean.delete()
        super().tearDown()

    # 1. SHIPWRIGHT & VOYAGES
    def test_shipwright_and_sailing(self):
        # Build dinghy
        ok, msg = build_vessel(self.char1, "dinghy")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.coins, 450)

        # Board vessel
        ok, msg = board_vessel(self.char1)
        self.assertTrue(ok)
        vessel = self.char1.db.boarded_vessel
        self.assertIsNotNone(vessel)

        # Raise anchor
        ok, msg = toggle_anchor(self.char1)
        self.assertTrue(ok)
        self.assertFalse(vessel.db.is_anchored)

        # Sail vessel to ocean
        ok, msg = sail_vessel(self.char1, "ocean")
        self.assertTrue(ok)
        self.assertEqual(self.char1.location, self.ocean)
        self.assertEqual(vessel.location, self.ocean)

    # 2. RUNECARVING & WARDS
    def test_runecarving_and_wards(self):
        chest = create_object(Object, key="Iron Strongbox", location=self.harbor)

        # Carve explosive rune
        ok, msg = carve_ward(self.char1, "explosive", target_obj=chest)
        self.assertTrue(ok)
        self.assertIsNotNone(chest.db.active_ward)

        # Intruder triggers ward
        old_hp = self.char2.db.hp
        tripped = trigger_ward_check(chest, self.char2)
        self.assertTrue(tripped)
        self.assertLess(self.char2.db.hp, old_hp)

        # Re-carve alarm rune and disarm it
        ok, msg = carve_ward(self.char1, "alarm", target_obj=chest)
        self.assertTrue(ok)
        ok, msg = disarm_ward(self.char1, chest)
        self.assertTrue(ok)
        self.assertIsNone(chest.db.active_ward)

    # 3. SURVIVAL CAMPS & TENTS
    def test_survival_camping(self):
        tent_item = create_portable_tent(self.char1)
        self.assertIn(tent_item, self.char1.contents)

        # Pitch tent
        ok, msg = pitch_camp_tent(self.char1)
        self.assertTrue(ok)
        has_tent = any(getattr(obj.db, "is_pitched_tent", False) for obj in self.harbor.contents)
        self.assertTrue(has_tent)

        # Kindle fire
        ok, msg = kindle_campfire(self.char1)
        self.assertTrue(ok)

        # Rest in camp
        old_hp = self.char1.db.hp
        ok, msg = rest_in_camp(self.char1)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, old_hp)

        # Strike tent
        ok, msg = strike_camp_tent(self.char1)
        self.assertTrue(ok)

    # 4. BEGGING & BUSKING
    def test_begging_and_busking(self):
        # Beg alms
        beg_for_alms(self.char1)

        # Perform busking
        old_coins = self.char1.db.coins
        ok, msg = perform_busking(self.char1, "juggle")
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.coins, old_coins)

    # 5. FOSSILS & MUSEUM
    def test_fossils_and_museum(self):
        fossil = create_raw_fossil(self.char1, "mammoth_tusk")
        self.assertFalse(fossil.db.is_cleaned)

        # Clean fossil
        ok, msg = clean_fossil_specimen(self.char1, "mammoth")
        self.assertTrue(ok)
        self.assertTrue(fossil.db.is_cleaned)

        # Donate to museum
        ok, msg = donate_fossil_to_museum(self.char1, "mammoth")
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.curator_points, 0)

        disp = format_museum_display()
        self.assertIn("Ancient Mammoth Tusk", disp)

    # 6. TAROT DIVINATION
    def test_tarot_divination(self):
        deck = create_tarot_deck(self.char1)
        self.assertTrue(deck.db.is_tarot_deck)

        # Draw card
        ok, card_name = draw_single_fate_card(self.char1)
        self.assertTrue(ok)
        self.assertTrue(len(card_name) > 0)

        # 3-card spread
        ok, msg = perform_three_card_spread(self.char1, self.char2)
        self.assertTrue(ok)

