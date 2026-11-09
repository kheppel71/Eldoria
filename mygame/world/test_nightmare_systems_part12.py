"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 12):
1. Illusionism, Mirror Images & Phantasmal Doppelgangers
2. Wilderness Spelunking, Rappelling Ropes & Chasm Crossing
3. Artisan Cheesemaking, Dairy Churning & Cellar Aging
4. Toll Bridges, Municipal River Crossings & Customs Inspection
5. Dungeon Chalk Markings, Wayfinding Glyphs & Wall Scrawls
6. Cathedral Confessionals, Penance & Divine Absolution
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object
from typeclasses.exits import Exit

from world.nightmare_illusionism import (
    cast_mirror_images, absorb_strike_with_mirror, cast_phantasmal_terror, dispel_illusions
)
from world.nightmare_spelunking import (
    create_climbing_rope, tie_rappelling_rope, execute_rappel, anchor_chasm_bridge
)
from world.nightmare_cheesemaking import (
    milk_farm_livestock, churn_dairy_butter, press_artisan_cheese, age_cheese_in_cellar
)
from world.nightmare_tolls import (
    create_toll_gate, pay_bridge_toll, perform_customs_inspection
)
from world.nightmare_chalkmarks import (
    create_chalk_stick, inscribe_chalk_mark, read_room_chalk_marks, wipe_chalk_marks
)
from world.nightmare_confession import (
    enter_confession, perform_holy_penance, receive_divine_absolution
)


class TestNightmareSystemsPart12(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems (Part 12)."""

    def setUp(self):
        super().setUp()
        self.upper_ledge = create_object(Room, key="Cavern Upper Precipice")
        self.abyss_floor = create_object(Room, key="Sunken Abyss Floor")

        # Vertical exit
        self.exit_down = create_object(Exit, key="down", location=self.upper_ledge, destination=self.abyss_floor)

        self.char1 = create_object(Character, key="Illusionist_Vex", location=self.upper_ledge)
        self.char2 = create_object(Character, key="Penitent_Bram", location=self.upper_ledge)

        self.char1.db.is_character = True
        self.char2.db.is_character = True

        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.mana = 100
        self.char1.db.max_mana = 100
        self.char1.db.coins = 500

        self.char2.db.hp = 100
        self.char2.db.max_hp = 100
        self.char2.db.mana = 100
        self.char2.db.max_mana = 100
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
        if self.exit_down.pk:
            self.exit_down.delete()
        if self.upper_ledge.pk:
            self.upper_ledge.delete()
        if self.abyss_floor.pk:
            self.abyss_floor.delete()
        super().tearDown()

    # 1. ILLUSIONISM & MIRROR IMAGES
    def test_illusionism(self):
        ok, msg = cast_mirror_images(self.char1)
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.mirror_images, 3)

        # Absorb strike
        absorbed = absorb_strike_with_mirror(self.char1)
        self.assertTrue(absorbed)
        self.assertEqual(self.char1.db.mirror_images, 2)

        # Phantasmal terror
        ok, msg = cast_phantasmal_terror(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertTrue(self.char2.db.is_terrified)

        # Dispel illusions
        ok, msg = dispel_illusions(self.char1, self.char2)
        self.assertTrue(ok)
        self.assertFalse(self.char2.db.is_terrified)

    # 2. SPELUNKING & RAPPELLING
    def test_spelunking_and_rappelling(self):
        rope = create_climbing_rope(self.char1)
        self.assertIn(rope, self.char1.contents)

        # Tie rope
        ok, msg = tie_rappelling_rope(self.char1)
        self.assertTrue(ok)
        self.assertTrue(self.upper_ledge.db.has_rope_line)

        # Rappel down
        ok, msg = execute_rappel(self.char1, "down")
        self.assertTrue(ok)
        self.assertEqual(self.char1.location, self.abyss_floor)

        # Anchor bridge
        ok, msg = anchor_chasm_bridge(self.char1)
        self.assertTrue(ok)

    # 3. CHEESEMAKING & DAIRY
    def test_cheesemaking_and_aging(self):
        ok, msg = milk_farm_livestock(self.char1)
        self.assertTrue(ok)
        has_milk = any(getattr(obj.db, "is_milk", False) for obj in self.char1.contents)
        self.assertTrue(has_milk)

        # Churn butter
        ok, msg = churn_dairy_butter(self.char1)
        self.assertTrue(ok)

        # Milk again for cheese
        milk_farm_livestock(self.char1)
        ok, msg = press_artisan_cheese(self.char1, "cheddar")
        self.assertTrue(ok)
        has_cheese = any(getattr(obj.db, "is_cheese", False) for obj in self.char1.contents)
        self.assertTrue(has_cheese)

        # Age cheese
        ok, msg = age_cheese_in_cellar(self.char1)
        self.assertTrue(ok)

    # 4. TOLL BRIDGES & CUSTOMS
    def test_toll_bridges_and_customs(self):
        gate = create_toll_gate(self.upper_ledge, fee=10)
        old_coins = self.char1.db.coins

        # Pay toll
        ok, msg = pay_bridge_toll(self.char1)
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.coins, old_coins - 10)
        self.assertTrue(gate.db.is_open)

        # Customs inspect
        report = perform_customs_inspection(self.char1, self.char2)
        self.assertIn("MUNICIPAL CUSTOMS INSPECTION", report)

    # 5. CHALK MARKS
    def test_chalk_marks(self):
        chalk = create_chalk_stick(self.char1, "Crimson")
        self.assertIn(chalk, self.char1.contents)

        # Inscribe mark
        ok, msg = inscribe_chalk_mark(self.char1, "skull", "Beware pit traps!")
        self.assertTrue(ok)

        # Read marks
        marks_disp = read_room_chalk_marks(self.char1)
        self.assertIn("Beware pit traps!", marks_disp)

        # Clear marks
        ok, msg = wipe_chalk_marks(self.char1)
        self.assertTrue(ok)

    # 6. CONFESSION & PENANCE
    def test_confession_and_absolution(self):
        ok, msg = enter_confession(self.char2, "I stole silver goblets from the tavern.")
        self.assertTrue(ok)
        self.assertIsNotNone(self.char2.db.active_penance)

        # Perform penance
        old_coins = self.char2.db.coins
        ok, msg = perform_holy_penance(self.char2)
        self.assertTrue(ok)
        self.assertEqual(self.char2.db.coins, old_coins - 25)

        # Absolve
        ok, msg = receive_divine_absolution(self.char2)
        self.assertTrue(ok)
        self.assertTrue(self.char2.db.holy_absolution_buff)

