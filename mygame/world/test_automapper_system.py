import os
import sys

# Setup Evennia environment
os.chdir(r"c:\Evennia\mygame")
sys.path.insert(0, r"c:\Evennia\mygame")
os.environ["DJANGO_SETTINGS_MODULE"] = "server.conf.settings"

import django
django.setup()
import evennia
evennia._init()

from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.characters import Character
from typeclasses.rooms import Room, get_gmcp_room_info
from commands.interaction_cmds import CmdMapper

def run_tests():
    print("=" * 60)
    print("STARTING AUTOMAPPER & GMCP VERIFICATION SUITE")
    print("=" * 60)

    # 1. Fetch representative rooms across different zones
    plaza = ObjectDB.objects.filter(db_tags__db_key="plaza", db_tags__db_category="room_key").first()
    island = ObjectDB.objects.filter(db_tags__db_key="isle_harbor", db_tags__db_category="room_key").first()
    dungeon = ObjectDB.objects.filter(db_tags__db_key="antechamber", db_tags__db_category="room_key").first()

    assert plaza is not None, "Plaza missing!"
    assert island is not None, "Island Harbor missing!"
    assert dungeon is not None, "Dungeon Antechamber missing!"

    print(f" Plaza Room:    #{plaza.id} ({plaza.key}) Zone: {plaza.db.zone} Terrain: {plaza.db.terrain} -> PASS")
    print(f" Island Room:   #{island.id} ({island.key}) Zone: {island.db.zone} Terrain: {island.db.terrain} -> PASS")
    print(f" Dungeon Room:  #{dungeon.id} ({dungeon.key}) Zone: {dungeon.db.zone} Terrain: {dungeon.db.terrain} -> PASS")

    # 2. Test GMCP Room.Info Payload Structure
    print("\n[Test 2] Testing GMCP Room.Info Payload Generation...")
    gmcp_data = get_gmcp_room_info(plaza)
    assert gmcp_data["num"] == plaza.id
    assert gmcp_data["name"] == plaza.key
    assert gmcp_data["zone"] == "The City of Eldoria"
    assert gmcp_data["terrain"] == "city"
    assert isinstance(gmcp_data["exits"], dict)
    assert len(gmcp_data["exits"]) > 0
    print(f" GMCP Payload for #{plaza.id}:")
    print(f"   Name:    {gmcp_data['name']}")
    print(f"   Zone:    {gmcp_data['zone']}")
    print(f"   Terrain: {gmcp_data['terrain']}")
    print(f"   Exits:   {gmcp_data['exits']} -> PASS")

    # 3. Test Room Appearance with GMCP Out-of-Band delivery
    print("\n[Test 3] Testing Room Appearance & Out-of-Band Dispatch...")
    player = create_object(Character, key="Mapper_Tester", location=plaza)
    player.db.is_character = True

    # Capture GMCP messages and text messages
    received_gmcp = []
    received_text = []

    def mock_msg(*args, **kwargs):
        if "gmcp" in kwargs:
            received_gmcp.append(kwargs["gmcp"])
        if args:
            received_text.append(str(args[0]))
        elif "text" in kwargs:
            received_text.append(str(kwargs["text"]))

    player.msg = mock_msg

    # Standard look (Mapper Mode OFF)
    player.db.mapper_mode = False
    appearance_default = plaza.return_appearance(player)
    assert len(received_gmcp) > 0
    assert received_gmcp[-1][0] == "Room.Info"
    assert received_gmcp[-1][1]["num"] == plaza.id
    assert "[ Obvious exits:" in appearance_default
    print(" Default appearance emitted GMCP Room.Info and standard exits bar -> PASS")

    # 4. Test Mapper Mode Toggle (CmdMapper)
    print("\n[Test 4] Testing CmdMapper Toggle Command...")
    cmd_mapper = CmdMapper()
    cmd_mapper.caller = player

    # Turn mapper mode ON
    cmd_mapper.args = "on"
    cmd_mapper.func()
    assert player.db.mapper_mode == True
    print(" 'mapper on' enabled successfully -> PASS")

    # Test appearance with Mapper Mode ON
    appearance_mapper = plaza.return_appearance(player)
    print("\n--- SAMPLE AUTOMAPPER DISPLAY OUTPUT ---")
    print(appearance_mapper)
    print("----------------------------------------")

    assert f"[#{plaza.id}]" in appearance_mapper
    assert "[ Obvious exits:" in appearance_mapper
    assert "[ Telemetry | ID: #" in appearance_mapper
    print(" Mapper mode renders machine-parseable ID, exit targets, and telemetry line -> PASS")

    # 5. Test Room Transition GMCP Emission
    print("\n[Test 5] Testing Room Transition (Entering Room triggers GMCP)...")
    north_gate = ObjectDB.objects.filter(db_tags__db_key="north_gate", db_tags__db_category="room_key").first()
    received_gmcp.clear()

    # Move player into North Gate
    north_gate.at_object_receive(player, plaza)
    assert len(received_gmcp) > 0
    assert received_gmcp[-1][0] == "Room.Info"
    assert received_gmcp[-1][1]["num"] == north_gate.id
    print(f" Player entry into #{north_gate.id} dispatched GMCP Room.Info -> PASS")

    # Clean up test player
    player.delete()

    print("\n" + "=" * 60)
    print("ALL AUTOMAPPER & GMCP SYSTEM TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()

