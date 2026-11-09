"""
Unit & Integration Tests for Nightmare LPmud Command Suite.
Tests:
1. CmdHp (vitals prompt)
2. CmdWimpy (wimpy threshold configuration)
3. CmdConsider (threat evaluation & target condition)
4. CmdKick (martial strike & stamina cost)
5. CmdDisarm (tactical weapon disarm)
6. CmdParty & CmdPartySay (party formation, invite, join, status, say, leave, disband)
7. CmdAssist (ally assistance in combat)
8. CmdSpells (spell directory listing)
9. CmdSearch, CmdListen, CmdSmell (sensory exploration)
10. CmdAppraise (item valuation and properties)
"""

from evennia.utils.test_resources import EvenniaTest
from evennia.utils.create import create_object
from typeclasses.characters import Character
from typeclasses.rooms import Room
from typeclasses.objects import Object
from world.nightmare_core import (
    init_nightmare_character, start_combat, disengage_combat,
    is_in_combat, PARTIES, get_party
)
from commands.nightmare_cmds import (
    CmdHp, CmdWimpy, CmdConsider, CmdKick, CmdDisarm,
    CmdParty, CmdPartySay, CmdAssist, CmdSpells,
    CmdSearch, CmdListen, CmdSmell, CmdAppraise
)


class TestNightmareCommands(EvenniaTest):
    """Test suite for Nightmare LPmud commands."""

    def setUp(self):
        super().setUp()
        self.room = create_object(Room, key="Sigil Hive Ward Alley")
        self.room.db.terrain = "city"

        self.player1 = create_object(Character, key="PlayerOne", location=self.room)
        self.player2 = create_object(Character, key="PlayerTwo", location=self.room)
        self.monster = create_object(Character, key="Foul Ogre", location=self.room)

        self.player1.db.is_character = True
        self.player2.db.is_character = True
        self.monster.db.is_character = True

        init_nightmare_character(self.player1)
        init_nightmare_character(self.player2)
        init_nightmare_character(self.monster)

        self.player1.db.hp = 100
        self.player1.db.max_hp = 100
        self.player1.db.stamina = 100
        self.player1.db.max_stamina = 100
        self.player1.db.mana = 50
        self.player1.db.max_mana = 50
        self.player1.db.level = 5

        self.player2.db.hp = 100
        self.player2.db.max_hp = 100
        self.player2.db.level = 5

        self.monster.db.hp = 120
        self.monster.db.max_hp = 120
        self.monster.db.level = 6

        # Clear active parties
        PARTIES.clear()

        # Capture messages cleanly for both direct and msg_contents calls
        self.p1_msgs = []
        self.p2_msgs = []

        def capture_p1(msg=None, *args, **kwargs):
            if msg is not None:
                self.p1_msgs.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.p1_msgs.append(str(t[0] if isinstance(t, tuple) else t))

        def capture_p2(msg=None, *args, **kwargs):
            if msg is not None:
                self.p2_msgs.append(str(msg))
            elif "text" in kwargs:
                t = kwargs["text"]
                self.p2_msgs.append(str(t[0] if isinstance(t, tuple) else t))

        self.player1.msg = capture_p1
        self.player2.msg = capture_p2

    def tearDown(self):
        disengage_combat(self.player1, self.monster)
        disengage_combat(self.player2, self.monster)
        PARTIES.clear()
        if self.player1.pk:
            self.player1.delete()
        if self.player2.pk:
            self.player2.delete()
        if self.monster.pk:
            self.monster.delete()
        if self.room.pk:
            self.room.delete()
        super().tearDown()

    def p1_text(self):
        return "\n".join(self.p1_msgs)

    def p2_text(self):
        return "\n".join(self.p2_msgs)

    def test_cmd_hp(self):
        """Test quick vitals prompt."""
        cmd = CmdHp()
        cmd.caller = self.player1
        cmd.args = ""
        cmd.func()

        out = self.p1_text()
        self.assertIn("HP:", out)
        self.assertIn("Mana:", out)
        self.assertIn("Stm:", out)
        self.assertIn("Coins:", out)

    def test_cmd_wimpy(self):
        """Test wimpy auto-flee threshold settings."""
        cmd = CmdWimpy()
        cmd.caller = self.player1

        # Check default status
        cmd.args = ""
        cmd.func()
        self.assertIn("Wimpy", self.p1_text())

        # Set to 25%
        self.p1_msgs.clear()
        cmd.args = "25"
        cmd.func()
        self.assertEqual(self.player1.db.wimpy, 25)
        self.assertIn("25%", self.p1_text())

        # Disable
        self.p1_msgs.clear()
        cmd.args = "off"
        cmd.func()
        self.assertEqual(self.player1.db.wimpy, 0)
        self.assertIn("disabled", self.p1_text())

    def test_cmd_consider(self):
        """Test tactical threat and condition evaluation."""
        cmd = CmdConsider()
        cmd.caller = self.player1
        cmd.args = "Foul Ogre"
        cmd.func()

        out = self.p1_text()
        self.assertIn("Evaluating Foul Ogre", out)
        self.assertIn("pristine physical condition", out)

    def test_cmd_kick(self):
        """Test martial kick strike and stamina consumption."""
        cmd = CmdKick()
        cmd.caller = self.player1
        cmd.args = "Foul Ogre"
        cmd.func()

        self.assertEqual(self.player1.db.stamina, 88)
        self.assertLess(self.monster.db.hp, 120)
        self.assertTrue(is_in_combat(self.player1))

    def test_cmd_disarm(self):
        """Test disarm attempt against an armed target."""
        weapon = create_object(Object, key="Iron Cleaver", location=self.monster)
        weapon.db.damage_bonus = 5
        self.monster.db.equipped_slots = {"right_hand": weapon}

        cmd = CmdDisarm()
        cmd.caller = self.player1
        cmd.args = "Foul Ogre"
        # Force high dex on player1 to ensure disarm success
        self.player1.db.dex = 50
        self.monster.db.dex = 5
        self.monster.db.str = 5
        cmd.func()

        self.assertEqual(self.player1.db.stamina, 85)
        # Weapon was disarmed to the room floor
        self.assertEqual(weapon.location, self.room)
        self.assertNotIn("right_hand", self.monster.db.equipped_slots)

    def test_cmd_party_lifecycle(self):
        """Test complete adventuring party system: form, invite, join, status, leave."""
        cmd = CmdParty()

        # 1. Form party
        cmd.caller = self.player1
        cmd.args = "form Bloodfang"
        cmd.func()
        self.assertIsNotNone(get_party(self.player1))
        self.assertEqual(self.player1.db.party, "Bloodfang")

        # 2. Invite PlayerTwo
        cmd.args = "invite PlayerTwo"
        cmd.func()
        party = get_party(self.player1)
        self.assertIn(self.player2.id, party["invited"])

        # 3. PlayerTwo joins
        cmd.caller = self.player2
        cmd.args = "join Bloodfang"
        cmd.func()
        self.assertEqual(self.player2.db.party, "Bloodfang")
        self.assertIn(self.player2.id, party["members"])

        # 4. Status check
        self.p1_msgs.clear()
        cmd.caller = self.player1
        cmd.args = "status"
        cmd.func()
        out = self.p1_text()
        self.assertIn("Party: Bloodfang", out)
        self.assertIn("PlayerOne", out)
        self.assertIn("PlayerTwo", out)

        # 5. Party chat (CmdPartySay)
        psay = CmdPartySay()
        psay.caller = self.player1
        psay.args = "For Sigil!"
        psay.func()
        self.assertIn("For Sigil!", self.p2_text())

        # 6. PlayerTwo leaves
        cmd.caller = self.player2
        cmd.args = "leave"
        cmd.func()
        self.assertIsNone(self.player2.db.party)
        self.assertNotIn(self.player2.id, party["members"])

    def test_cmd_assist(self):
        """Test assist command joining ally's combat."""
        # Start combat between PlayerOne and Foul Ogre
        start_combat(self.player1, self.monster)
        self.assertTrue(is_in_combat(self.player1))
        self.assertFalse(is_in_combat(self.player2))

        # PlayerTwo assists PlayerOne
        cmd = CmdAssist()
        cmd.caller = self.player2
        cmd.args = "PlayerOne"
        cmd.func()

        self.assertTrue(is_in_combat(self.player2))
        self.assertEqual(getattr(self.player2.ndb, "combat_target", None), self.monster)

    def test_cmd_spells(self):
        """Test spells directory listing."""
        cmd = CmdSpells()
        cmd.caller = self.player1
        cmd.args = ""
        cmd.func()

        out = self.p1_text()
        self.assertIn("SPELL DIRECTORY", out)
        self.assertIn("firebolt", out)
        self.assertIn("fireball", out)

    def test_cmd_sensory(self):
        """Test search, listen, and smell sensory commands."""
        # Listen
        c_listen = CmdListen()
        c_listen.caller = self.player1
        c_listen.args = ""
        c_listen.func()
        self.assertIn("Ambient Acoustics", self.p1_text())

        # Smell
        self.p1_msgs.clear()
        c_smell = CmdSmell()
        c_smell.caller = self.player1
        c_smell.args = ""
        c_smell.func()
        self.assertIn("Ambient Scents", self.p1_text())

        # Search
        self.p1_msgs.clear()
        c_search = CmdSearch()
        c_search.caller = self.player1
        c_search.args = ""
        c_search.func()
        self.assertIn("carefully search", self.p1_text())

    def test_cmd_appraise(self):
        """Test item appraisal."""
        dagger = create_object(Object, key="Silver Dagger", location=self.player1)
        dagger.db.weight = 2
        dagger.db.value = 150
        dagger.db.damage_bonus = 6
        dagger.db.slot = "right_hand"

        cmd = CmdAppraise()
        cmd.caller = self.player1
        cmd.args = "Silver Dagger"
        cmd.func()

        out = self.p1_text()
        self.assertIn("Appraisal: Silver Dagger", out)
        self.assertIn("2 stone", out)
        self.assertIn("Weapon", out)
        self.assertIn("Gold", out)
