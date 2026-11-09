"""
Administrative Zone & Area Importer Commands

Provides in-game wizard/admin commands to import, validate, anchor,
and purge zones from classic MUD world files (.wld) or structured JSON packages.
"""

import os
from evennia.commands.default.muxcommand import MuxCommand
from world.importers import (
    import_json,
    import_wld,
    purge_zone,
    find_room_by_key,
    parse_json_file,
    parse_wld_file,
    validate_zone_data,
)


class CmdImportZone(MuxCommand):
    """
    Import, inspect, or manage external zones and areas.

    Usage:
      @importzone/help
      @importzone/validate <filepath>
      @importzone/json <filepath> [anchor_room_key] [direction] [return_dir]
      @importzone/wld <filepath> [anchor_room_key] [direction] [return_dir]
      @importzone/bulk
      @importzone/purge <zone_key>

    Switches:
      /bulk      - Executes full bulk ingestion of 150+ rooms across all 5 major zones.
      /validate  - Performs a dry-run check of the file syntax and exit graphs without modifying database.
      /json      - Imports a modern JSON area definition.
      /wld       - Imports a classic CircleMUD/tbaMUD/Diku .wld world file.
      /purge     - Deletes all rooms, exits, NPCs, and objects associated with <zone_key>.
      /help      - Displays this help screen and available sample zones.

    Examples:
      @importzone/validate world/importers/data/praxis_crypts.json
      @importzone/json world/importers/data/praxis_crypts.json isle_serpent_hollow down up
      @importzone/wld world/importers/data/sample_midgaard.wld eldoria_crossroads north south
      @importzone/purge praxis_crypts
    """

    key = "@importzone"
    aliases = ["@zoneimport", "@importarea"]
    locks = "cmd:perm(Admin) or perm(Builder)"
    help_category = "Building"

    def func(self):
        caller = self.caller
        switches = self.switches

        if "help" in switches or not switches:
            caller.msg(
                "|w=== Eldoria Zone & World Importer ===|n\n"
                "  |c@importzone/validate <path>|n                         - Dry-run syntax & graph check\n"
                "  |c@importzone/json <path> [anchor] [dir] [retdir]|n     - Import structured JSON zone\n"
                "  |c@importzone/wld <path> [anchor] [dir] [retdir]|n      - Import CircleMUD/tbaMUD .wld\n"
                "  |c@importzone/purge <zone_key>|n                        - Remove all entities of a zone\n\n"
                "|wBundled Sample Datasets:|n\n"
                "  - |yworld/importers/data/praxis_crypts.json|n (6-room Nightmare IV sunken catacombs)\n"
                "  - |yworld/importers/data/sample_midgaard.wld|n (5-room classic CircleMUD temple square)"
            )
            return

        if "purge" in switches:
            if not self.args:
                caller.msg("|rUsage: @importzone/purge <zone_key>|n")
                return
            zone_key = self.args.strip()
            count = purge_zone(zone_key)
            caller.msg(f"|gPurged {count} objects belonging to zone '|w{zone_key}|g'.|n")
            return

        if "bulk" in switches:
            caller.msg("|w[*] Executing Master Bulk Ingestion (2,800+ rooms across 53 major realms)...|n")
            from world.importers.bulk_ingestion import run_bulk_ingestion
            from world.importers.bulk_ingestion_part2 import run_bulk_ingestion_part2
            from world.importers.bulk_ingestion_part3 import run_bulk_ingestion_part3
            from world.importers.bulk_ingestion_part4 import run_bulk_ingestion_part4
            from world.importers.bulk_ingestion_part5 import run_bulk_ingestion_part5
            from world.importers.bulk_ingestion_part6 import run_bulk_ingestion_part6
            from world.importers.bulk_ingestion_part7 import run_bulk_ingestion_part7
            from world.importers.bulk_ingestion_part8 import run_bulk_ingestion_part8
            from world.importers.bulk_ingestion_part9 import run_bulk_ingestion_part9
            from world.importers.bulk_ingestion_part10 import run_bulk_ingestion_part10
            from world.importers.bulk_ingestion_part11 import run_bulk_ingestion_part11
            from world.importers.bulk_ingestion_part12 import run_bulk_ingestion_part12
            from world.importers.bulk_ingestion_part13 import run_bulk_ingestion_part13
            try:
                rep1 = run_bulk_ingestion(clean_existing=True)
                rep2 = run_bulk_ingestion_part2(clean_existing=True)
                rep3 = run_bulk_ingestion_part3(clean_existing=True)
                rep4 = run_bulk_ingestion_part4(clean_existing=True)
                rep5 = run_bulk_ingestion_part5(clean_existing=True)
                rep6 = run_bulk_ingestion_part6(clean_existing=True)
                rep7 = run_bulk_ingestion_part7(clean_existing=True)
                rep8 = run_bulk_ingestion_part8(clean_existing=True)
                rep9 = run_bulk_ingestion_part9(clean_existing=True)
                rep10 = run_bulk_ingestion_part10(clean_existing=True)
                rep11 = run_bulk_ingestion_part11(clean_existing=True)
                rep12 = run_bulk_ingestion_part12(clean_existing=True)
                rep13 = run_bulk_ingestion_part13(clean_existing=True)

                total_zones = rep1['zones_processed'] + rep2['zones_processed'] + rep3['zones_processed'] + rep4['zones_processed'] + rep5['zones_processed'] + rep6['zones_processed'] + rep7['zones_processed'] + rep8['zones_processed'] + rep9['zones_processed'] + rep10['zones_processed'] + rep11['zones_processed'] + rep12['zones_processed'] + rep13['zones_processed']
                total_rooms = rep1['rooms_created'] + rep2['rooms_created'] + rep3['rooms_created'] + rep4['rooms_created'] + rep5['rooms_created'] + rep6['rooms_created'] + rep7['rooms_created'] + rep8['rooms_created'] + rep9['rooms_created'] + rep10['rooms_created'] + rep11['rooms_created'] + rep12['rooms_created'] + rep13['rooms_created']
                total_exits = rep1['exits_created'] + rep2['exits_created'] + rep3['exits_created'] + rep4['exits_created'] + rep5['exits_created'] + rep6['exits_created'] + rep7['exits_created'] + rep8['exits_created'] + rep9['exits_created'] + rep10['exits_created'] + rep11['exits_created'] + rep12['exits_created'] + rep13['exits_created']
                total_npcs = rep1['npcs_created'] + rep2['npcs_created'] + rep3['npcs_created'] + rep4['npcs_created'] + rep5['npcs_created'] + rep6['npcs_created'] + rep7['npcs_created'] + rep8['npcs_created'] + rep9['npcs_created'] + rep10['npcs_created'] + rep11['npcs_created'] + rep12['npcs_created'] + rep13['npcs_created']
                total_items = rep1['items_created'] + rep2['items_created'] + rep3['items_created'] + rep4['items_created'] + rep5['items_created'] + rep6['items_created'] + rep7['items_created'] + rep8['items_created'] + rep9['items_created'] + rep10['items_created'] + rep11['items_created'] + rep12['items_created'] + rep13['items_created']
                all_anchors = rep1['anchors_established'] + rep2['anchors_established'] + rep3['anchors_established'] + rep4['anchors_established'] + rep5['anchors_established'] + rep6['anchors_established'] + rep7['anchors_established'] + rep8['anchors_established'] + rep9['anchors_established'] + rep10['anchors_established'] + rep11['anchors_established'] + rep12['anchors_established'] + rep13['anchors_established']
                all_ferries = rep1['ferry_routes_added'] + rep2['ferry_routes_added'] + rep3['ferry_routes_added'] + rep4['ferry_routes_added'] + rep5['ferry_routes_added'] + rep6['ferry_routes_added'] + rep7['ferry_routes_added'] + rep8['ferry_routes_added'] + rep9['ferry_routes_added'] + rep10['ferry_routes_added'] + rep11['ferry_routes_added'] + rep12['ferry_routes_added'] + rep13['ferry_routes_added']

                anchors_txt = "\n".join([f"    * {a}" for a in all_anchors])
                ferries_txt = "\n".join([f"    * {f}" for f in all_ferries])
                caller.msg(
                    f"\n|g=========================================================\n"
                    f"*** GRAND MASTER BULK INGESTION COMPLETE! ***\n"
                    f"=========================================================|n\n"
                    f"  - Total Zones Ingested: |w{total_zones}|n\n"
                    f"  - Total Rooms Created:  |w{total_rooms}|n\n"
                    f"  - Total Exits Built:    |w{total_exits}|n\n"
                    f"  - Total NPCs Generated: |w{total_npcs}|n\n"
                    f"  - Total Items & Relics: |w{total_items}|n\n\n"
                    f"|wAnchors Established:|n\n{anchors_txt}\n\n"
                    f"|wMaritime Routes Added:|n\n{ferries_txt}\n\n"
                    f"|g=========================================================|n\n"
                )
            except Exception as exc:
                caller.msg(f"|rBulk Ingestion failed: {exc}|n")
            return

        # Argument parsing for file-based operations
        tokens = self.args.strip().split()
        if not tokens:
            caller.msg("|rPlease provide a file path to import or validate.|n")
            return

        raw_path = tokens[0]
        # Resolve path relative to game root if relative
        if not os.path.isabs(raw_path):
            from django.conf import settings
            base_dir = settings.GAME_DIR
            filepath = os.path.join(base_dir, raw_path)
        else:
            filepath = raw_path

        if not os.path.exists(filepath):
            caller.msg(f"|rError: File not found at '{filepath}'.|n")
            return

        anchor = tokens[1] if len(tokens) > 1 else None
        anchor_dir = tokens[2] if len(tokens) > 2 else "down"
        return_dir = tokens[3] if len(tokens) > 3 else None

        # Validation / Dry-Run
        if "validate" in switches:
            try:
                if filepath.endswith(".json"):
                    data = parse_json_file(filepath)
                else:
                    data = {"zone_key": "test_wld", "rooms": parse_wld_file(filepath)}
                is_valid, warnings, errors = validate_zone_data(data)
                
                caller.msg(f"|w[*] Validation Report for '|y{os.path.basename(filepath)}|w':|n")
                caller.msg(f"  - Total Rooms Found: |g{len(data.get('rooms', {}))}|n")
                caller.msg(f"  - Overall Status: {'|gPASS|n' if is_valid else '|rFAIL|n'}")
                if warnings:
                    caller.msg("  |yWarnings:|n")
                    for w in warnings[:5]:
                        caller.msg(f"    * {w}")
                if errors:
                    caller.msg("  |rErrors:|n")
                    for e in errors:
                        caller.msg(f"    * {e}")
            except Exception as exc:
                caller.msg(f"|rValidation exception: {exc}|n")
            return

        # Live JSON Import
        if "json" in switches:
            caller.msg(f"|w[*] Ingesting JSON zone from '|y{os.path.basename(filepath)}|w'...|n")
            try:
                report = import_json(
                    filepath,
                    anchor_room_key=anchor,
                    anchor_exit_dir=anchor_dir,
                    return_exit_dir=return_dir
                )
                if report.get("success"):
                    caller.msg(
                        f"|g[SUCCESS] Imported zone '|w{report['zone_name']}|g' (|w{report['zone_key']}|g):\n"
                        f"  - Rooms created:  |w{report['rooms_created']}|n\n"
                        f"  - Exits created:  |w{report['exits_created']}|n\n"
                        f"  - NPCs created:   |w{report['npcs_created']}|n\n"
                        f"  - Items created:  |w{report['items_created']}|n\n"
                        f"  - Anchored to:    |w{report['anchored_to'] or 'None (Isolated)'}|n"
                    )
                else:
                    caller.msg(f"|rImport failed:|n {report.get('errors')}")
            except Exception as exc:
                caller.msg(f"|rImport error: {exc}|n")
            return

        # Live WLD Import
        if "wld" in switches:
            caller.msg(f"|w[*] Ingesting CircleMUD .wld zone from '|y{os.path.basename(filepath)}|w'...|n")
            zone_key = os.path.splitext(os.path.basename(filepath))[0]
            try:
                report = import_wld(
                    filepath,
                    zone_key=zone_key,
                    zone_name=f"Zone {zone_key.title()}",
                    anchor_room_key=anchor,
                    anchor_exit_dir=anchor_dir,
                    return_exit_dir=return_dir
                )
                if report.get("success"):
                    caller.msg(
                        f"|g[SUCCESS] Imported CircleMUD zone '|w{report['zone_name']}|g' (|w{report['zone_key']}|g):\n"
                        f"  - Rooms created:  |w{report['rooms_created']}|n\n"
                        f"  - Exits created:  |w{report['exits_created']}|n\n"
                        f"  - Anchored to:    |w{report['anchored_to'] or 'None (Isolated)'}|n"
                    )
                else:
                    caller.msg(f"|rImport failed:|n {report.get('errors')}")
            except Exception as exc:
                caller.msg(f"|rImport error: {exc}|n")
            return

