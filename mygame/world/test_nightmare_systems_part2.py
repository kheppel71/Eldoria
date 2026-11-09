"""
Unit & Integration Test Suite for Nightmare LPmud Systems (Part 2):
1. Rogue Thievery & Shoplifting
2. Player Housing, Keys & Lockpicking
3. Alchemy Cauldron & Campfire Cooking
4. Merchant Haggling & Peddlers
5. Holy Turning & Necromancy
6. Guild Territory Control
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_thievery import peek_target, pickpocket_target, fence_item
from world.nightmare_housing import (
    create_lockable_chest, create_physical_key, lock_target, unlock_target,
    pick_lock, claim_player_house
)
from world.nightmare_alchemy_cooking import brew_potion, cook_meat, eat_ration
from world.nightmare_economy import create_wandering_peddler, haggle_price, peddler_buy_item
from world.nightmare_necromancy import turn_undead, animate_dead, order_thrall
from world.nightmare_territory import claim_territory, get_regional_guild_buff, TERRITORIES
from world.nightmare_justice import BOUNTIES


class TestNightmareSystemsPart2(EvenniaTest):
    """Test suite covering the 6 new Nightmare LPmud systems."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Sigil Hive Ward Crossroads")
        self.room.db.terrain = "city"

        self.char1 = create_object(Character, key="Rogue_Lia", location=self.room)
        self.char2 = create_object(Character, key="Priest_Kael", location=self.room)
        self.victim = create_object(Character, key="Merchant_Tom", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True
        self.victim.db.is_character = True

        self.char1.db.guild = "Rogue"
        self.char2.db.guild = "Cleric"

        self.char1.db.dex = 50
        self.char1.db.wis = 20
        self.char1.db.str = 20
        self.char1.db.hp = 100
        self.char1.db.max_hp = 100
        self.char1.db.stamina = 100
        self.char1.db.max_stamina = 100
        self.char1.db.coins = {"gold": 500, "silver": 50, "copper": 20}

        self.victim.db.coins = {"gold": 50, "silver": 20, "copper": 10}
        self.victim.db.wis = 10
        self.victim.db.dex = 10

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

        BOUNTIES.clear()

    def tearDown(self):
        BOUNTIES.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.victim.pk:
            self.victim.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    # 1. THIEVERY & FENCES
    def test_thievery_system(self):
        # Peek
        ok, msg = peek_target(self.char1, self.victim)
        self.assertTrue(ok)

        # Successful pickpocketing of coins
        ok, msg = pickpocket_target(self.char1, self.victim, target_type="coins")
        self.assertTrue(ok)
        self.assertLess(self.victim.db.coins["gold"], 50)
        self.assertGreater(self.char1.db.coins["gold"], 500)

        # Fence contraband item
        contraband = create_object(Object, key="Stolen Jeweled Goblet", location=self.char1)
        contraband.db.value = 100
        ok, msg = fence_item(self.char1, contraband)
        self.assertTrue(ok)

    # 2. HOUSING, KEYS & LOCKPICKING
    def test_housing_and_lockpicking(self):
        key_code = "vault_99"
        chest = create_lockable_chest(key_code, location=self.room)
        key = create_physical_key(key_code, location=self.char1)

        # Unlock with key
        self.assertTrue(chest.db.is_locked)
        ok, msg = unlock_target(self.char1, chest, key)
        self.assertTrue(ok)
        self.assertFalse(chest.db.is_locked)

        # Relock with key
        ok, msg = lock_target(self.char1, chest, key)
        self.assertTrue(ok)
        self.assertTrue(chest.db.is_locked)

        # Rogue lockpick
        lockpick = create_object(Object, key="Steel Lockpick", location=self.char1)
        ok, msg = pick_lock(self.char1, chest, lockpick)
        self.assertTrue(ok)
        self.assertFalse(chest.db.is_locked)

        # Buy house
        ok, msg = claim_player_house(self.char1, "Lia's Hideout")
        self.assertTrue(ok)
        self.assertIsNotNone(self.char1.db.home_room_id)

    # 3. ALCHEMY & COOKING
    def test_alchemy_and_cooking(self):
        # Brew Healing Potion
        herb = create_object(Object, key="Kingsfoil", location=self.char1)
        ok, msg = brew_potion(self.char1, "healing")
        self.assertTrue(ok)
        potion = next((o for o in self.char1.contents if "Healing" in o.key), None)
        self.assertIsNotNone(potion)

        # Cook Raw Meat
        meat = create_object(Object, key="Chunk of Fresh Wolf Meat", location=self.char1)
        ok, msg = cook_meat(self.char1, meat)
        self.assertTrue(ok)
        ration = next((o for o in self.char1.contents if "Steak" in o.key), None)
        self.assertIsNotNone(ration)

        # Eat cooked food
        self.char1.db.hp = 50
        self.char1.db.stamina = 50
        ok, msg = eat_ration(self.char1, ration)
        self.assertTrue(ok)
        self.assertGreater(self.char1.db.hp, 50)
        self.assertTrue(self.char1.db.well_fed)

    # 4. PEDDLERS & HAGGLING
    def test_peddlers_and_haggling(self):
        peddler = create_wandering_peddler(location=self.room)
        self.assertTrue(peddler.db.is_peddler)

        # Haggle calculation
        price = haggle_price(self.char1, 20, is_buying=True)
        self.assertLessEqual(price, 20)

        # Buy from peddler
        ok, msg = peddler_buy_item(self.char1, peddler, "Iron Lockpick")
        self.assertTrue(ok)
        item = next((o for o in self.char1.contents if "Lockpick" in o.key), None)
        self.assertIsNotNone(item)

    # 5. HOLY TURNING & NECROMANCY
    def test_holy_turning_and_necromancy(self):
        # Create undead skeleton
        skeleton = create_object(Character, key="Rattling Skeleton", location=self.room)
        skeleton.db.is_undead = True
        skeleton.db.hp = 40

        # Turn undead
        self.char2.db.mana = 50
        self.char2.db.wis = 30
        ok, msg = turn_undead(self.char2, skeleton)
        self.assertTrue(ok)

        # Animate dead from corpse
        corpse = create_object(Object, key="Corpse of Orc Berserker", location=self.room)
        self.char1.db.mana = 60
        ok, msg = animate_dead(self.char1, corpse)
        self.assertTrue(ok)
        thrall = self.char1.db.active_thrall
        self.assertIsNotNone(thrall)

        # Order thrall
        ok, msg = order_thrall(self.char1, "guard")
        self.assertTrue(ok)
        ok, msg = order_thrall(self.char1, "dismiss")
        self.assertTrue(ok)
        self.assertIsNone(self.char1.db.active_thrall)

    # 6. GUILD TERRITORY CONTROL
    def test_guild_territory_control(self):
        # Reset and claim territory
        TERRITORIES["hive_crossroads"]["controlling_guild"] = "Fighter"
        ok, msg = claim_territory(self.char1, "hive_crossroads")
        self.assertTrue(ok)
        self.assertEqual(TERRITORIES["hive_crossroads"]["controlling_guild"], "Rogue")

        # Regional buff
        buff = get_regional_guild_buff(self.char1, self.room)
        self.assertIsNotNone(buff)
        self.assertIn("Stealth", buff)

