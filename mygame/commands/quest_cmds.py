"""
Quest commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_quests import (
    QUESTS, init_quest_character, start_quest, get_quest_rank
)


class CmdQuests(default_cmds.MuxCommand):
    """
    View your quest log, progress, and accumulated Quest Points

    Usage:
      quests
      quests available
      quests completed
    """
    key = "quests"
    aliases = ["quest", "qlog"]
    locks = "cmd:all()"
    help_category = "Quests"

    def func(self):
        caller = self.caller
        init_quest_character(caller)

        qp = caller.db.qp or 0
        rank = get_quest_rank(qp)
        log = caller.db.quest_log or {}

        caller.msg(f"\n|w============================= QUEST JOURNAL =============================|n")
        caller.msg(f"Adventurer: |c{caller.key}|n   Quest Points: |m{qp} QP|n   Standing: {rank}")
        caller.msg("|b" + "-" * 74 + "|n")

        # In-Progress
        in_prog = [k for k, v in log.items() if v.get("status") == "in_progress" and k in QUESTS]
        if in_prog:
            caller.msg("|yCurrent Active Quests:|n")
            for q_k in in_prog:
                q = QUESTS[q_k]
                caller.msg(f"  |g[*] {q['name']:<30}|n (Reward: {q['qp']} QP, {q['gold']} Gold)")
                caller.msg(f"      |xObjective:|n {q['objective']}")
        else:
            caller.msg("|yCurrent Active Quests:|n None.")

        # Completed
        completed = [k for k, v in log.items() if v.get("status") == "completed" and k in QUESTS]
        if completed:
            caller.msg("\n|gCompleted Quests:|n")
            for q_k in completed:
                q = QUESTS[q_k]
                caller.msg(f"  |c[COMPLETED]|n {q['name']:<30} (+{q['qp']} QP)")

        # Available
        available = [k for k in QUESTS if k not in log and (caller.db.level or 1) >= QUESTS[k]["min_level"]]
        if available:
            caller.msg("\n|wAvailable In Realm:|n")
            for q_k in available:
                q = QUESTS[q_k]
                caller.msg(f"  |w- {q_k:<16}|n {q['name']:<30} (Lvl {q['min_level']}+ | {q['qp']} QP)")
            caller.msg("\nUse: |wquest info <quest_name>|n or |wquest start <quest_name>|n")

        caller.msg("|w" + "=" * 74 + "|n\n")


class CmdQuestInfo(default_cmds.MuxCommand):
    """
    Examine detailed lore and objectives for a quest

    Usage:
      quest info <quest_key>
      quest start <quest_key>
    """
    key = "questinfo"
    aliases = ["qinfo"]
    locks = "cmd:all()"
    help_category = "Quests"

    def func(self):
        caller = self.caller
        init_quest_character(caller)

        if not self.args:
            caller.msg("Usage: questinfo <quest_key>")
            return

        key = self.args.strip().lower().replace(" ", "_")
        q = QUESTS.get(key)
        if not q:
            # Try fuzzy search
            for k, data in QUESTS.items():
                if key in k or key in data["name"].lower():
                    q = data
                    key = k
                    break

        if not q:
            caller.msg(f"Unknown quest '{self.args.strip()}'. See |wquests|n for available quests.")
            return

        log = caller.db.quest_log or {}
        status = log.get(key, {}).get("status", "Not Started")

        caller.msg(f"\n|w=== Quest: {q['name']} ===|n")
        caller.msg(f"Status: |c{status.upper()}|n    Minimum Level: |y{q['min_level']}|n")
        caller.msg(f"Rewards: |m{q['qp']} Quest Points|n, |g{q['xp']} XP|n, |y{q['gold']} Gold|n")
        caller.msg(f"\n|wLore & Background:|n\n  {q['desc']}")
        caller.msg(f"\n|wCurrent Objective:|n\n  {q['objective']}")
        caller.msg("|w" + "=" * 36 + "|n\n")


class CmdQuestStart(default_cmds.MuxCommand):
    """
    Accept and start tracking an available quest

    Usage:
      quest start <quest_key>
    """
    key = "queststart"
    aliases = ["qstart"]
    locks = "cmd:all()"
    help_category = "Quests"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: queststart <quest_key>")
            return

        key = self.args.strip().lower().replace(" ", "_")
        if key not in QUESTS:
            for k, data in QUESTS.items():
                if key in k or key in data["name"].lower():
                    key = k
                    break

        ok, msg = start_quest(caller, key)
        caller.msg(msg)

