"""
Nightmare LPmud Quest Engine & Quest Point (QP) Advancement System.

Implements:
1. Quest Registry with multi-stage objectives, lore, and rewards.
2. Quest Points (QP) economy gating guild tier advancements and prestige titles.
3. Automated milestone completion upon slaying bosses, discovering secret artifacts,
   or speaking with guildmasters.
4. Player Quest Journal and inquiry tools.
"""

QUESTS = {
    "hermit_ring": {
        "name": "The Hermit's Ring",
        "qp": 10,
        "xp": 500,
        "gold": 25,
        "min_level": 1,
        "desc": "An elderly hermit living on the fringes of the city lost his silver signet ring in the overgrown brush. Retrieve it to earn his blessing.",
        "objective": "Search the wilderness brush and return the Silver Ring to the Hermit."
    },
    "goblin_shaman": {
        "name": "The Goblin Shaman's Totem",
        "qp": 15,
        "xp": 1000,
        "gold": 50,
        "min_level": 3,
        "desc": "A wicked goblin shaman has been terrorizing local supply caravans. Slay the shaman in his lair and claim his cursed totem.",
        "objective": "Defeat the Goblin Shaman and seize his tribal totem."
    },
    "cathedral_relic": {
        "name": "The Cathedral's Stolen Chalice",
        "qp": 20,
        "xp": 2000,
        "gold": 100,
        "min_level": 5,
        "desc": "A sacred gold chalice was stolen from the Cathedral altar by desecrators. Recover the relic and return it to the High Priestess.",
        "objective": "Locate the thieves in the catacombs and recover the holy chalice."
    },
    "hive_smugglers": {
        "name": "The Hive Ward Smugglers",
        "qp": 15,
        "xp": 1200,
        "gold": 75,
        "min_level": 4,
        "desc": "Contraband weapons and forbidden alchemical venoms are moving through the Hive Ward alleyways. Break up the ring.",
        "objective": "Investigate the suspicious crates and defeat the Smuggler Boss."
    },
    "dragons_eye": {
        "name": "The Dragon's Eye Gem",
        "qp": 35,
        "xp": 5000,
        "gold": 300,
        "min_level": 8,
        "desc": "An ancient ruby pulsating with draconic fire rests at the peak of the volcanic spire. Only seasoned heroes may claim it.",
        "objective": "Scale the spire and survive the dragon's elemental trial."
    }
}


def init_quest_character(char):
    """Initializes quest storage on character."""
    if not hasattr(char, "db"):
        return
    if char.db.qp is None:
        char.db.qp = 0
    if char.db.quest_log is None:
        char.db.quest_log = {}


def start_quest(char, quest_key):
    """Accepts or begins tracking a quest."""
    init_quest_character(char)
    q = QUESTS.get(quest_key)
    if not q:
        return False, f"Unknown quest '{quest_key}'."

    log = char.db.quest_log or {}
    if quest_key in log and log[quest_key].get("status") == "completed":
        return False, f"You have already completed {q['name']}!"

    if (char.db.level or 1) < q["min_level"]:
        return False, f"You must be at least Level {q['min_level']} to undertake {q['name']}."

    log[quest_key] = {"status": "in_progress", "started_at": char.db.level}
    char.db.quest_log = log
    char.msg(f"\n|G[QUEST STARTED] You have begun: {q['name']}!|n")
    char.msg(f"|xObjective:|n {q['objective']}\n")
    return True, f"Quest '{q['name']}' started!"


def complete_quest(char, quest_key):
    """Marks a quest as successfully completed, distributing QP, XP, and Gold."""
    init_quest_character(char)
    q = QUESTS.get(quest_key)
    if not q:
        return False, f"Unknown quest '{quest_key}'."

    log = char.db.quest_log or {}
    if log.get(quest_key, {}).get("status") == "completed":
        return False, f"You have already received rewards for {q['name']}."

    log[quest_key] = {"status": "completed"}
    char.db.quest_log = log

    qp_gain = q["qp"]
    xp_gain = q["xp"]
    gold_gain = q["gold"]

    char.db.qp = (char.db.qp or 0) + qp_gain
    char.db.xp = (char.db.xp or 0) + xp_gain
    coins = char.db.coins or {"gold": 0, "silver": 0, "copper": 0}
    coins["gold"] = coins.get("gold", 0) + gold_gain
    char.db.coins = coins

    char.msg(f"""
|Y========================== QUEST COMPLETED ==========================|n
|wCongratulations! You have completed: |g{q['name']}|n!
  Rewards Granted:
    - |m+{qp_gain} Quest Points (Total: {char.db.qp} QP)|n
    - |g+{xp_gain} Experience Points|n
    - |y+{gold_gain} Gold Coins|n
|Y=====================================================================|n
""")
    if char.location:
        char.location.msg_contents(
            f"|y{char.key} has completed the heroic quest '{q['name']}'!|n",
            exclude=[char]
        )
    return True, f"Quest '{q['name']}' completed!"


def get_quest_rank(qp):
    """Calculates classic Nightmare quest rank title from total QP."""
    if qp >= 80:
        return "|YGrand Paragon of the Realm|n"
    elif qp >= 50:
        return "|cMaster Adventurer|n"
    elif qp >= 30:
        return "|gRenowned Explorer|n"
    elif qp >= 15:
        return "|ySeasoned Pathfinder|n"
    elif qp >= 5:
        return "|wNovice Questor|n"
    return "|xUnproven Wayfarer|n"

