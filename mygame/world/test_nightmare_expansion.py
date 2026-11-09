"""
Comprehensive Unit & Integration Test Suite for the 7 Nightmare LPmud Expansion Systems:
1. Justice & Bounty System
2. Quest Engine & QP Progression
3. Equipment Durability & Blacksmithing
4. Wilderness Harvesting, Skinning & Envenoming
5. Celestial Cycle & Weather Engine
6. Bulletin Boards & Courier Postal System
7. Mounts & Cavalry Combat
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object

from world.nightmare_justice import (
    record_crime, arrest_criminal, release_prisoner, pay_bail,
    place_bounty, BOUNTIES, init_justice_character
)
from world.nightmare_quests import (
    start_quest, complete_quest, get_quest_rank, QUESTS, init_quest_character
)
from world.nightmare_durability import (
    init_item_durability, get_item_condition, apply_wear, repair_item, sharpen_weapon
)
from world.nightmare_harvest import (
    skin_corpse, forage_herbs, apply_poison_to_weapon
)
from world.nightmare_weather import (
    get_game_time, get_moon_phase, get_current_weather, set_weather
)
from world.nightmare_boards_mail import (
    post_to_board, read_board_note, remove_board_note, send_mail
)
from world.nightmare_mounts import (
    create_mount, mount_beast, dismount_beast, mounted_charge
)

from commands.justice_cmds import CmdBounties, CmdSurrender, CmdServeTime, CmdCriminalRecord
from commands.quest_cmds import CmdQuests, CmdQuestInfo
from commands.durability_cmds import CmdCondition, CmdSharpen
from commands.harvest_cmds import CmdSkin
from commands.weather_cmds import CmdTime, CmdWeather
from commands.board_mail_cmds import CmdBulletinBoard, CmdMailbox
from commands.mount_cmds import CmdMount, CmdDismount, CmdCharge, CmdSaddlebags


class TestNightmareExpansion(EvenniaTest):
    """Test suite covering the 7 Nightmare LPmud expansion phases."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Sigil Grand Bazaar")
        self.room.db.terrain = "forest"

        self.char1 = create_object(Character, key="Valerius", location=self.room)
        self.char2 = create_object(Character, key="Morrigan", location=self.room)
        self.target = create_object(Character, key="Rogue Thief", location=self.room)

        self.char1.db.is_character = True
        self.char2.db.is_character = True
        self.target.db.is_character = True

        self.char1.db.coins = {"gold": 100, "silver": 50, "copper": 20}
        self.char2.db.coins = {"gold": 100, "silver": 50, "copper": 20}

        self.msgs1 = []
        self.msgs2 = []

        def capture_c1(msg=None, *args, **kwargs):
            if msg is not None:
                self.msgs1.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.msgs1.append(str(t[0] if isinstance(t, tuple) else t))

        def capture_c2(msg=None, *args, **kwargs):
            if msg is not None:
                self.msgs2.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.msgs2.append(str(t[0] if isinstance(t, tuple) else t))

        self.char1.msg = capture_c1
        self.char2.msg = capture_c2

        BOUNTIES.clear()

    def tearDown(self):
        BOUNTIES.clear()
        if self.char1.pk:
            self.char1.delete()
        if self.char2.pk:
            self.char2.delete()
        if self.target.pk:
            self.target.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    def text1(self):
        return "\n".join(self.msgs1)

    def text2(self):
        return "\n".join(self.msgs2)

    # 1. JUSTICE & BOUNTY
    def test_justice_system(self):
        record_crime(self.target, "Assault", victim=self.char1, bounty_add=75)
        self.assertTrue(self.target.db.is_outlaw)
        self.assertEqual(self.target.db.bounty, 75)
        self.assertIn(self.target.id, BOUNTIES)

        # Place additional bounty
        ok, msg = place_bounty(self.char1, self.target, 25)
        self.assertTrue(ok)
        self.assertEqual(self.target.db.bounty, 100)

        # Arrest and incarceration
        arrest_criminal(None, self.target, sentence_seconds=30)
        self.assertTrue(self.target.db.is_jailed)

        # Pay bail
        ok, msg = pay_bail(self.char1, self.target)
        self.assertTrue(ok)
        self.assertFalse(self.target.db.is_jailed)
        self.assertFalse(self.target.db.is_outlaw)

    # 2. QUEST ENGINE & QP
    def test_quest_system(self):
        self.char1.db.level = 5
        ok, msg = start_quest(self.char1, "hermit_ring")
        self.assertTrue(ok)

        # Complete quest
        ok, msg = complete_quest(self.char1, "hermit_ring")
        self.assertTrue(ok)
        self.assertEqual(self.char1.db.qp, 10)
        self.assertIn("Novice Questor", get_quest_rank(self.char1.db.qp))

        # Check command output
        cmd = CmdQuests()
        cmd.caller = self.char1
        cmd.args = ""
        cmd.func()
        self.assertIn("The Hermit's Ring", self.text1())

    # 3. DURABILITY & BLACKSMITHING
    def test_durability_and_blacksmith(self):
        sword = create_object(Object, key="Iron Longsword", location=self.char1)
        init_item_durability(sword, max_dur=100)

        # Apply wear
        apply_wear(sword, amount=40)
        self.assertEqual(sword.db.durability, 60)
        pct, label, desc = get_item_condition(sword)
        self.assertEqual(pct, 60)
        self.assertIn("Worn", label)

        # Repair item
        ok, msg = repair_item(self.char1, sword)
        self.assertTrue(ok)
        self.assertEqual(sword.db.durability, 100)

        # Sharpen weapon
        ok, msg = sharpen_weapon(self.char1, sword)
        self.assertTrue(ok)
        self.assertEqual(sword.db.hone_bonus, 2)

    # 4. WILDERNESS HARVESTING, SKINNING & ENVENOMING
    def test_harvest_and_envenom(self):
        # Skin corpse
        corpse = create_object(Object, key="Corpse of Dire Wolf", location=self.room)
        ok, msg = skin_corpse(self.char1, corpse)
        self.assertTrue(ok)
        self.assertTrue(corpse.db.is_skinned)

        # Forage herbs
        self.char1.db.wis = 50
        ok, msg = forage_herbs(self.char1)
        self.assertTrue(ok)

        # Envenom blade
        poison_herb = create_object(Object, key="Nightshade", location=self.char1)
        poison_herb.db.herb_effect = "poison"
        dagger = create_object(Object, key="Steel Dagger", location=self.char1)
        dagger.db.slot = "right_hand"

        ok, msg = apply_poison_to_weapon(self.char1, poison_herb, dagger)
        self.assertTrue(ok)
        self.assertGreater(dagger.db.poison_charges, 0)

    # 5. CELESTIAL CYCLE & WEATHER
    def test_celestial_and_weather(self):
        hour, period, desc, is_night = get_game_time()
        self.assertGreaterEqual(hour, 0)
        self.assertLessEqual(hour, 23)

        moon_name, moon_desc, mana_bonus = get_moon_phase()
        self.assertIsNotNone(moon_name)

        ok, msg = set_weather("thunderstorm")
        self.assertTrue(ok)
        w = get_current_weather()
        self.assertEqual(w["name"], "Crackling Thunderstorm")
        self.assertIn("Lightning spells empowered", w["modifier"])

    # 6. BULLETIN BOARDS & COURIER MAIL
    def test_boards_and_courier_mail(self):
        # Board posting & reading
        ok, msg = post_to_board(self.room, "Valerius", "Dragon Sighting", "Beware the fiery peak.")
        self.assertTrue(ok)
        note = read_board_note(self.room, 1)
        self.assertIsNotNone(note)
        self.assertEqual(note["subject"], "Dragon Sighting")

        # Courier mail with enclosed gold
        ok, msg = send_mail(self.char1, self.char2, "Secret Plans", "Meet me at midnight.", gold=15)
        self.assertTrue(ok)
        self.assertEqual(len(self.char2.db.mailbox), 1)
        self.assertEqual(self.char2.db.mailbox[0]["enclosed_gold"], 15)

    # 7. MOUNTS & CAVALRY
    def test_mounts_and_cavalry(self):
        steed = create_mount("warhorse", location=self.room, owner=self.char1)
        self.assertTrue(steed.db.is_mount)

        # Mount beast
        ok, msg = mount_beast(self.char1, steed)
        self.assertTrue(ok)
        self.assertTrue(self.char1.db.is_mounted)

        # Charge target
        self.char1.db.stamina = 100
        self.target.db.hp = 100
        self.target.db.max_hp = 100
        ok, msg = mounted_charge(self.char1, self.target)
        self.assertTrue(ok)
        self.assertLess(self.target.db.hp, 100)

        # Dismount
        ok, msg = dismount_beast(self.char1)
        self.assertTrue(ok)
        self.assertFalse(self.char1.db.is_mounted)

