"""
Reincarnation and soul shard commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_reincarnation import perform_reincarnation, HERITAGE_TRAITS


class CmdReincarnate(default_cmds.MuxCommand):
    """
    Perform the ancient reincarnation ritual to rebirth with eternal soul shard blessings

    Usage:
      reincarnate
      reincarnate <blade_prowess/arcane_mind/colossus_vitality/shadow_step>
    """
    key = "reincarnate"
    aliases = ["rebirth"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        lvl = caller.db.level or 1

        if not self.args:
            caller.msg(f"\n|w=================== ANCESTRAL REINCARNATION ===================|n")
            caller.msg(f"Current Level: |c{lvl}|n (Requires Level 10+)")
            caller.msg("Transcending resets your character to Level 1 while permanently imbuing a Soul Shard.\n")
            caller.msg("|yAvailable Heritage Blessings:|n")
            for t_k, data in HERITAGE_TRAITS.items():
                caller.msg(f"  |c{t_k:<20}|n {data['name']}: |g{data['desc']}|n")
            caller.msg("|w" + "=" * 65 + "|n")
            caller.msg("To transcend: |wreincarnate <trait_name>|n\n")
            return

        ok, msg = perform_reincarnation(caller, self.args.strip())
        if not ok:
            caller.msg(msg)


class CmdSoulShards(default_cmds.MuxCommand):
    """
    Inspect your accumulated ancestral soul shards and permanent heritage traits

    Usage:
      soulshards
      heritage
    """
    key = "soulshards"
    aliases = ["heritage", "shards"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        shards = getattr(caller.db, "soul_shards", 0) or 0
        traits = getattr(caller.db, "heritage_traits", []) or []

        caller.msg(f"\n|w=== Ancestral Soul Shards: {caller.key} ===|n")
        caller.msg(f"Reincarnations Completed: |Y{shards} Soul Shards|n")
        if traits:
            caller.msg("\n|GActive Heritage Blessings:|n")
            for t in traits:
                caller.msg(f"  |Y[*] {t}|n")
        else:
            caller.msg("\n|xNo ancestral soul shards earned yet. (Achieved at Level 10+)|n")
        caller.msg("|w" + "=" * 42 + "|n\n")

