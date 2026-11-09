"""
Mounts and pack animal commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_mounts import mount_beast, dismount_beast, mounted_charge


class CmdMount(default_cmds.MuxCommand):
    """
    Mount a warhorse, pack mule, or riding beast

    Usage:
      mount <beast>
    """
    key = "mount"
    locks = "cmd:all()"
    help_category = "Mounts"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Mount what beast?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        ok, msg = mount_beast(caller, target)
        if not ok:
            caller.msg(msg)


class CmdDismount(default_cmds.MuxCommand):
    """
    Dismount from your current steed

    Usage:
      dismount
    """
    key = "dismount"
    locks = "cmd:all()"
    help_category = "Mounts"

    def func(self):
        caller = self.caller
        ok, msg = dismount_beast(caller)
        if not ok:
            caller.msg(msg)


class CmdCharge(default_cmds.MuxCommand):
    """
    Spur your steed into a thundering mounted cavalry charge

    Usage:
      charge <target>
    """
    key = "charge"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args:
            target = getattr(caller.ndb, "combat_target", None)
            if not target:
                caller.msg("Charge who?")
                return
        else:
            target = caller.search(self.args.strip(), location=caller.location)
            if not target:
                return

        ok, msg = mounted_charge(caller, target)
        if not ok:
            caller.msg(msg)


class CmdSaddlebags(default_cmds.MuxCommand):
    """
    Access saddlebags on your mount to store or retrieve gear

    Usage:
      saddlebags
      saddlebags put <item>
      saddlebags get <item>
    """
    key = "saddlebags"
    aliases = ["packs"]
    locks = "cmd:all()"
    help_category = "Mounts"

    def func(self):
        caller = self.caller
        mount = getattr(caller.db, "current_mount", None)
        if not mount:
            # Check if mount is in the room
            if caller.location:
                for obj in caller.location.contents:
                    if getattr(obj.db, "is_mount", False) and obj.db.owner_id == caller.id:
                        mount = obj
                        break

        if not mount:
            caller.msg("You do not have a mount nearby to access saddlebags.")
            return

        bags = getattr(mount.db, "saddlebags", []) or []

        if not self.args:
            caller.msg(f"\n|w=== Saddlebags: {mount.key} ===|n")
            if not bags:
                caller.msg("The saddlebags are currently empty.")
            else:
                caller.msg("Contents:")
                for item in bags:
                    caller.msg(f"  - |c{item.key}|n ({getattr(item.db, 'weight', 1)} stone)")
            caller.msg(f"Capacity: {len(bags)}/{mount.db.capacity or 100} items.")
            caller.msg("|w" + "=" * 32 + "|n\n")
            return

        parts = self.args.strip().split(None, 1)
        subcmd = parts[0].lower()
        item_name = parts[1].strip() if len(parts) > 1 else ""

        if subcmd == "put":
            if not item_name:
                caller.msg("Put what item into the saddlebags?")
                return
            item = caller.search(item_name, location=caller)
            if not item:
                return

            item.move_to(mount, quiet=True)
            bags.append(item)
            mount.db.saddlebags = bags
            caller.msg(f"You stow {item.key} safely into {mount.key}'s saddlebags.")

        elif subcmd == "get":
            if not item_name:
                caller.msg("Get what item from the saddlebags?")
                return
            found = next((it for it in bags if item_name.lower() in it.key.lower()), None)
            if not found:
                caller.msg(f"Could not find '{item_name}' in the saddlebags.")
                return

            bags.remove(found)
            mount.db.saddlebags = bags
            found.move_to(caller, quiet=True)
            caller.msg(f"You retrieve {found.key} from {mount.key}'s saddlebags.")

        else:
            caller.msg("Usage: saddlebags [put <item> | get <item>]")

