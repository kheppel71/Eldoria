"""
Nightmare LPmud Hall of Champions & Realm Leaderboards Engine.

Implements:
1. Multi-category Realm Rankings:
   - Arena Gladiators (Duels rating & tournament valor).
   - Grand Questors (Quest points & renown completed).
   - Wealth Tycoons (Liquid gold & bank holdings).
   - Legendary Champions (Level and total experience).
2. Plaque formatting with gold, silver, and bronze podium honors.
3. Interactive query command ('leaderboards', 'rankings', 'top').
"""

from evennia.objects.models import ObjectDB


def get_character_pool():
    """Retrieves all registered character entities in the realm."""
    seen_ids = set()
    chars = []
    for obj in ObjectDB.objects.filter(db_typeclass_path__contains="Character"):
        if obj.id not in seen_ids and getattr(obj, "has_account", False) or getattr(obj.db, "level", None) is not None:
            seen_ids.add(obj.id)
            chars.append(obj)
    return chars


def get_category_ranks(category="all", limit=5):
    """Calculates top rankings for the specified category."""
    chars = get_character_pool()
    ranks = {}

    # 1. Gladiators (Arena rating)
    if category in ("all", "gladiators", "arena"):
        sorted_glad = sorted(
            chars,
            key=lambda c: (getattr(c.db, "arena_rating", 1000) or 1000, getattr(c.db, "arena_wins", 0) or 0),
            reverse=True
        )
        ranks["gladiators"] = [(c, getattr(c.db, "arena_rating", 1000) or 1000) for c in sorted_glad[:limit]]

    # 2. Grand Questors
    if category in ("all", "questors", "quests"):
        sorted_quest = sorted(
            chars,
            key=lambda c: getattr(c.db, "quest_points", 0) or 0,
            reverse=True
        )
        ranks["questors"] = [(c, getattr(c.db, "quest_points", 0) or 0) for c in sorted_quest[:limit]]

    # 3. Wealth Tycoons
    if category in ("all", "wealth", "tycoons", "gold"):
        def calc_wealth(c):
            coins = getattr(c.db, "coins", 0) or 0
            bank = getattr(c.db, "bank_coins", 0) or 0
            return coins + bank

        sorted_wealth = sorted(chars, key=calc_wealth, reverse=True)
        ranks["wealth"] = [(c, calc_wealth(c)) for c in sorted_wealth[:limit]]

    # 4. Legendary Champions (Level & XP)
    if category in ("all", "champions", "level", "slayers"):
        def calc_power(c):
            lvl = getattr(c.db, "level", 1) or 1
            xp = getattr(c.db, "xp", 0) or 0
            return (lvl * 10000) + xp

        sorted_champ = sorted(chars, key=calc_power, reverse=True)
        ranks["champions"] = [(c, getattr(c.db, "level", 1) or 1) for c in sorted_champ[:limit]]

    return ranks


def format_podium_badge(rank_idx):
    """Returns a styled medal ribbon for top 3 positions."""
    if rank_idx == 0:
        return "|Y[ 1st - GOLD  ]|n"
    elif rank_idx == 1:
        return "|w[ 2nd - SILVER]|n"
    elif rank_idx == 2:
        return "|y[ 3rd - BRONZE]|n"
    else:
        return f"|x[ #{rank_idx + 1:<10}]|n"


def format_leaderboard_display(category="all"):
    """Renders the Hall of Champions banner display."""
    ranks = get_category_ranks(category, limit=5)
    lines = [
        "|c" + "=" * 70 + "|n",
        "|w                   HALL OF CHAMPIONS - REALM LEADERBOARDS         |n",
        "|c" + "=" * 70 + "|n"
    ]

    titles_map = {
        "gladiators": ("GRAND GLADIATORS OF THE ARENA", "Arena Rating"),
        "questors": ("HIGH QUESTORS OF PRAXIS", "Quest Points"),
        "wealth": ("MERCHANT TYCOONS & COFFER BARONS", "Gold Coins"),
        "champions": ("LEGENDARY PARAGONS & SLAYERS", "Level")
    }

    for cat_key, entries in ranks.items():
        title_str, unit_str = titles_map.get(cat_key, (cat_key.upper(), "Score"))
        lines.append(f"\n|Y>>> {title_str} <<<|n")
        lines.append("|c" + "-" * 70 + "|n")
        if not entries:
            lines.append("   |xNo entries recorded in the annals yet.|n")
        else:
            for idx, (char, val) in enumerate(entries):
                badge = format_podium_badge(idx)
                name = char.key
                lines.append(f" {badge} |w{name:<24}|n : |g{val:>8} {unit_str}|n")

    lines.append("\n|c" + "=" * 70 + "|n")
    lines.append("|xType 'leaderboards <category>' to filter: arena, quests, wealth, champions.|n")
    return "\n".join(lines)

