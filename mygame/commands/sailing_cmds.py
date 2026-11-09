"""
Nightmare LPmud Sailing & Ferry Commands for Evennia
Includes:
- CmdFerries: Inspect available ferry routes, operators, and ticket fares
- CmdFare: Check ticket price, municipal tax breakdown, and wealth
- CmdBoard: Pay fare in Nightmare LPmud currency and embark on voyage
- CmdCoffers: Inspect Eldoria City Treasury and accumulated tariff revenues
"""

from evennia import default_cmds
from evennia.objects.models import ObjectDB
from world.sailing import (
    FERRY_ROUTES, get_city_coffers, deposit_municipal_tax,
    format_copper_as_currency, total_player_copper, deduct_fare, execute_voyage
)
from world.nightmare_core import init_nightmare_character


def get_current_port_key(location):
    """Determines which port key corresponds to current room."""
    if not location:
        return None
    if getattr(location.db, "room_key", None):
        return location.db.room_key
    room_tag = location.tags.get(category="room_key")
    if room_tag:
        if isinstance(room_tag, list):
            return room_tag[0] if room_tag else None
        return room_tag

    key = location.key.lower()
    if "south dock" in key or "harbor promenade" in key or "south_docks" in key:
        return "south_docks"
    elif "corsair" in key or "isle harbor" in key or "isle_harbor" in key:
        return "isle_harbor"
    elif "dead man" in key or "dead_mans_cove" in key:
        return "dead_mans_cove"
    elif "misty river" in key or "misty_river" in key:
        return "misty_river"
    elif "silt islet" in key or "silt_islet" in key:
        return "silt_islet"
    elif "smuggler's lagoon" in key or "isle_cove" in key:
        return "isle_cove"
    elif "leviathan" in key or "isle_wreck" in key:
        return "isle_wreck"

    return None


def matches_dest(query, port_key, port_name):
    """Fuzzy matcher for player destination input."""
    q = query.strip().lower()
    p = port_key.lower()
    pn = port_name.lower()
    if q in p or q in pn:
        return True
    if "island" in q and ("isle" in p or "isle" in pn):
        return True
    if "islet" in q and ("silt" in p or "islet" in p):
        return True
    if "river" in q and "river" in p:
        return True
    if "docks" in q and "docks" in p:
        return True
    if "cove" in q and "cove" in p:
        return True
    if "wreck" in q and "wreck" in p:
        return True
    return False


class CmdFerries(default_cmds.MuxCommand):
    """
    List ferry vessels, scheduled routes, and maritime ticket fares

    Usage:
      ferries
      routes
      ports
    """
    key = "ferries"
    aliases = ["routes", "ports"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        curr_port = get_current_port_key(caller.location)

        caller.msg("\n|w============================= ELDORIA MARITIME LINES =============================|n")
        caller.msg(f"{'Vessel & Line':<24} {'Operator':<20} {'Ports of Call':<32}")
        caller.msg("-" * 78)

        for r_key, r_data in FERRY_ROUTES.items():
            ports_str = " <-> ".join([name.split("(")[0].strip() for name in r_data["port_names"].values()])
            caller.msg(f"|c{r_data['name']:<24}|n |y{r_data['operator']:<20}|n |w{ports_str[:32]}|n")

        caller.msg("|w==================================================================================|n")

        if curr_port:
            caller.msg(f"\n|g[You are currently docked at:|n |y{curr_port.replace('_', ' ').title()}|g]|n")
            caller.msg("|wAvailable departures from this dock:|n")
            for r_key, r_data in FERRY_ROUTES.items():
                if curr_port in r_data["ports"]:
                    for dest_port in r_data["ports"]:
                        if dest_port != curr_port:
                            fare = r_data["fares"].get((curr_port, dest_port), 20)
                            dest_name = r_data["port_names"].get(dest_port, dest_port)
                            tax = int(fare * 0.20)
                            caller.msg(f"  -> |c{dest_name}|n: {format_copper_as_currency(fare)} (includes 20% Crown Tax: {format_copper_as_currency(tax)})")
            caller.msg("\nTo board a ferry: |wboard <destination>|n (e.g. |wboard island|n or |wboard cove|n)")
        else:
            caller.msg("\n|x(You are not currently at a designated ferry pier or harbor)|n")
            caller.msg("Visit Eldoria South Docks, Misty River, or Corsair's Anchorage to embark.")


class CmdFare(default_cmds.MuxCommand):
    """
    Check the ticket fare and municipal tax for a maritime route

    Usage:
      fare <destination>
    """
    key = "fare"
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Check fare to where? Usage: fare <destination>")
            return

        curr_port = get_current_port_key(caller.location)
        if not curr_port:
            caller.msg("You are not currently at a ferry dock! Travel to a harbor or pier to check fares.")
            return

        dest_query = self.args.strip().lower()
        matched_route = None
        matched_dest = None

        for r_key, r_data in FERRY_ROUTES.items():
            if curr_port in r_data["ports"]:
                for p in r_data["ports"]:
                    if p != curr_port and matches_dest(dest_query, p, r_data["port_names"].get(p, "")):
                        matched_route = r_data
                        matched_dest = p
                        break
            if matched_dest:
                break

        if not matched_dest:
            caller.msg(f"No direct ferry departs from here for '{dest_query}'. Type |wferries|n to see routes.")
            return

        fare_copper = matched_route["fares"].get((curr_port, matched_dest), 25)
        tax_copper = int(fare_copper * 0.20)
        operator_cut = fare_copper - tax_copper
        dest_name = matched_route["port_names"].get(matched_dest, matched_dest)

        player_copper = total_player_copper(caller)

        caller.msg(f"\n|c=== Maritime Passage: {matched_route['name']} ===|n")
        caller.msg(f"Departure Port:   |y{matched_route['port_names'].get(curr_port, curr_port)}|n")
        caller.msg(f"Destination:      |g{dest_name}|n")
        caller.msg(f"Operator:         |w{matched_route['operator']} ({matched_route['operator_title']})|n")
        caller.msg(f"Total Fare:       {format_copper_as_currency(fare_copper)}")
        caller.msg(f"  - Operator Cut: {format_copper_as_currency(operator_cut)} (maintenance & crew)")
        caller.msg(f"  - Crown Tax:    {format_copper_as_currency(tax_copper)} (20% to Eldoria Municipal Coffers)")
        caller.msg(f"Wealth on Hand:   {format_copper_as_currency(player_copper)}")

        if player_copper >= fare_copper:
            caller.msg(f"|gStatus: You have sufficient funds! To embark, type:|n |wboard {dest_query}|n\n")
        else:
            caller.msg(f"|rStatus: Insufficient coin! You need {format_copper_as_currency(fare_copper - player_copper)} more.|n\n")


class CmdBoard(default_cmds.MuxCommand):
    """
    Pay fare in Nightmare LPmud currency and embark on a ferry voyage

    Usage:
      board <destination/ferry>
      embark <destination>
    """
    key = "board"
    aliases = ["embark"]
    locks = "cmd:all()"
    help_category = "Travel"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if getattr(caller.db, "is_ghost", False):
            caller.msg("You are a ghost! Ferrymen cannot take fare from spirits.")
            return

        curr_port = get_current_port_key(caller.location)
        if not curr_port:
            caller.msg("You are not at a ferry dock! Head to the South Docks, Misty River, or Corsair's Anchorage.")
            return

        if not self.args:
            caller.msg("Which destination do you wish to sail to? (Type |wferries|n to see destinations)")
            return

        dest_query = self.args.strip().lower()
        matched_route = None
        matched_dest = None

        for r_key, r_data in FERRY_ROUTES.items():
            if curr_port in r_data["ports"]:
                for p in r_data["ports"]:
                    if p != curr_port and matches_dest(dest_query, p, r_data["port_names"].get(p, "")):
                        matched_route = r_data
                        matched_dest = p
                        break
            if matched_dest:
                break

        if not matched_dest:
            caller.msg(f"No ferry departing from here sails to '{dest_query}'. Type |wferries|n to check departures.")
            return

        fare_copper = matched_route["fares"].get((curr_port, matched_dest), 25)
        tax_copper = int(fare_copper * 0.20)

        # Deduct fare
        success, err_msg = deduct_fare(caller, fare_copper)
        if not success:
            caller.msg(err_msg)
            return

        # Deposit municipal tariff into town coffers
        deposit_municipal_tax(tax_copper)

        # Find destination room in DB
        dest_room = ObjectDB.objects.filter(db_tags__db_key=matched_dest, db_tags__db_category="room_key").first()
        if not dest_room:
            for obj in ObjectDB.objects.all():
                if getattr(obj.db, "room_key", None) == matched_dest:
                    dest_room = obj
                    break
        if not dest_room:
            # Fallback search by key
            for obj in ObjectDB.objects.all():
                if obj.is_typeclass("typeclasses.rooms.Room") and matched_dest in obj.key.lower().replace(" ", "_"):
                    dest_room = obj
                    break

        if not dest_room:
            caller.msg("The ferry pilot shakes their head: 'The tide is too wild to reach that port right now.'")
            return

        # Execute voyage
        execute_voyage(caller, matched_route["key"], caller.location, dest_room, fare_copper, tax_copper)


class CmdCoffers(default_cmds.MuxCommand):
    """
    Inspect Eldoria's Royal Treasury and collected municipal maritime taxes

    Usage:
      coffers
      treasury
      citytreasury
    """
    key = "coffers"
    aliases = ["treasury", "citytreasury"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        coffers = get_city_coffers()
        tariffs = coffers.get("tariffs_collected_copper", 0)

        text = f"""
|w========================= ROYAL TREASURY OF ELDORIA =========================|n
Audited by: |yLord Aldous Sterling, Chief Royal Factor & Banker|n
Location:   |cRoyal Bank of Eldoria & Vault|n

|wMunicipal Coffer Reserves:|n
  |y{coffers.get('gold', 0)} Gold Sovereigns|n
  |w{coffers.get('silver', 0)} Silver Talents|n
  |r{coffers.get('copper', 0)} Copper Pennies|n

|wPort Authority & Maritime Tariffs:|n
  Cumulative Ferry Taxes Collected: {format_copper_as_currency(tariffs)}
  Current Municipal Ferry Tax Rate: |g20% per passenger voyage|n

|wTreasury Note:|n
  \"All maritime ferries operating within Crown waters pay twenty percent of passenger
   receipts to the municipal treasury for harbour dredging, lighthouse oil, and seawalls.\"
|w=============================================================================|n
"""
        caller.msg(text.strip())
