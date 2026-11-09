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
from typeclasses.rooms import Room
from world.nightmare_core import init_nightmare_character
from world.sailing import (
    FERRY_ROUTES, get_city_coffers, deposit_municipal_tax,
    deduct_fare, format_copper_as_currency, total_player_copper
)
from commands.sailing_cmds import CmdFerries, CmdFare, CmdBoard, CmdCoffers

def run_tests():
    print("=" * 60)
    print("STARTING COMPREHENSIVE SAILING & ISLAND TEST SUITE")
    print("=" * 60)

    # 1. Verify Island Rooms and Docks Exist
    print("\n[Test 1] Verifying Maritime Docks and Island Regions...")
    south_docks = ObjectDB.objects.filter(db_tags__db_key="south_docks", db_tags__db_category="room_key").first()
    isle_harbor = ObjectDB.objects.filter(db_tags__db_key="isle_harbor", db_tags__db_category="room_key").first()
    isle_wreck = ObjectDB.objects.filter(db_tags__db_key="isle_wreck", db_tags__db_category="room_key").first()
    silt_islet = ObjectDB.objects.filter(db_tags__db_key="silt_islet", db_tags__db_category="room_key").first()

    assert south_docks is not None, "South Docks missing!"
    assert isle_harbor is not None, "Isle Harbor missing!"
    assert isle_wreck is not None, "Leviathan Graveyard missing!"
    assert silt_islet is not None, "Silt Islet missing!"
    print(f" South Docks:      {south_docks.key} -> PASS")
    print(f" Isle of Serpents: {isle_harbor.key} -> PASS")
    print(f" Shipwreck Reef:   {isle_wreck.key} -> PASS")
    print(f" River Islet:      {silt_islet.key} -> PASS")

    # 2. Currency Auto-Change and Fare Deduction
    print("\n[Test 2] Testing Nightmare LPmud Currency Fare & Auto-Change...")
    sailor = create_object(Character, key="Captain_Tester", location=south_docks)
    sailor.db.is_character = True
    init_nightmare_character(sailor)

    # Give sailor 1 Gold (100 Copper equivalent)
    sailor.db.coins = {"gold": 1, "silver": 0, "copper": 0}
    assert total_player_copper(sailor) == 100

    # Fare to Island is 50 Copper (5 Silver)
    fare = 50
    success, msg = deduct_fare(sailor, fare)
    assert success == True
    # Remainder should be 50 copper (5 Silver, 0 Gold, 0 Copper)
    assert sailor.db.coins["gold"] == 0
    assert sailor.db.coins["silver"] == 5
    assert sailor.db.coins["copper"] == 0
    print(f" 1 Gold paid for 50 copper fare. Change returned: {sailor.db.coins} -> PASS")

    # 3. Municipal Tax Deduction into City Coffers
    print("\n[Test 3] Testing Municipal Crown Tax to Royal Coffers...")
    initial_coffers = get_city_coffers()
    initial_tariffs = initial_coffers.get("tariffs_collected_copper", 0)

    tax_rate_20_pct = int(fare * 0.20) # 10 copper
    updated_coffers = deposit_municipal_tax(tax_rate_20_pct)
    assert updated_coffers["tariffs_collected_copper"] == initial_tariffs + 10
    print(f" Deposited {tax_rate_20_pct} copper tax. Total Tariffs: {updated_coffers['tariffs_collected_copper']} -> PASS")

    # 4. In-Game Boarding Command Execution
    print("\n[Test 4] Testing Boarding Command (South Docks -> Isle of Serpents)...")
    sailor.db.coins = {"gold": 1, "silver": 0, "copper": 0}
    cmd_board = CmdBoard()
    cmd_board.caller = sailor
    cmd_board.args = "island"

    # Capture output
    sailor_msgs = []
    def rec_sailor(*args, **kwargs):
        if args: sailor_msgs.append(str(args[0]))
        elif "text" in kwargs: sailor_msgs.append(str(kwargs["text"]))
    sailor.msg = rec_sailor

    cmd_board.func()
    assert any("collects your fare" in m for m in sailor_msgs)
    assert any("Crown Maritime Tax deposited" in m for m in sailor_msgs)
    print(" Embarkation successful with tariff receipt -> PASS")

    # 5. Check Island Internal Exploration Trails
    print("\n[Test 5] Testing Isle of Serpents Internal Foot Trails...")
    sailor.move_to(isle_harbor, quiet=True)
    # Check exits from harbor
    exit_keys = [x.key.lower() for x in isle_harbor.exits]
    assert "north" in exit_keys or "beach" in exit_keys
    assert "inland" in exit_keys or "jungle" in exit_keys
    print(f" Exits from Corsair's Anchorage: {exit_keys} -> PASS")

    # Move to Siren Beach and then Leviathan's Graveyard
    beach = ObjectDB.objects.filter(db_tags__db_key="isle_beach", db_tags__db_category="room_key").first()
    sailor.move_to(beach, quiet=True)
    b_exits = [x.key.lower() for x in beach.exits]
    assert "shallows" in b_exits or "wreck" in b_exits
    print(f" Beach leads to shipwreck shallows: {b_exits} -> PASS")

    # Move to wreck and inspect treasure
    sailor.move_to(isle_wreck, quiet=True)
    strongbox = next((o for o in isle_wreck.contents if "Strongbox" in o.key), None)
    assert strongbox is not None
    print(f" Found pirate relic: {strongbox.key} in {isle_wreck.key} -> PASS")

    # 6. River Ferry to Whispering Silt Islet
    print("\n[Test 6] Testing River Ferry (Misty River -> Silt Islet)...")
    misty_river = ObjectDB.objects.filter(db_tags__db_key="misty_river", db_tags__db_category="room_key").first()
    sailor.move_to(misty_river, quiet=True)
    sailor.db.coins = {"gold": 0, "silver": 5, "copper": 0}
    cmd_board.args = "islet"
    cmd_board.func()
    assert any("Old Riverman Jacques" in m or "collects your fare" in m for m in sailor_msgs)
    print(" River Flatboat voyage chartered successfully -> PASS")

    # 7. Check Coffers Command
    print("\n[Test 7] Testing Royal Treasury Coffers Inspection...")
    cmd_coffers = CmdCoffers()
    cmd_coffers.caller = sailor
    cmd_coffers.args = ""
    cmd_coffers.func()
    assert any("ROYAL TREASURY OF ELDORIA" in m for m in sailor_msgs)
    print(" Treasury inspection command verified -> PASS")

    # Clean up test character
    sailor.delete()

    print("\n" + "=" * 60)
    print("ALL MARITIME SAILING, FERRY & ISLAND TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
