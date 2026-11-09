"""
Nightmare LPmud Soul Shards & Reincarnation Heritage Engine.

Implements:
1. Ancestral Reincarnation ritual resetting level with permanent soul shard blessings.
2. Heritage Traits (Blade Prowess, Arcane Mind, Colossus Vitality, Shadow Step).
3. Inspection of soul shards and ancestral lineage ('soulshards').
"""

HERITAGE_TRAITS = {
    "blade_prowess": {
        "name": "Blade Prowess",
        "desc": "+10% Physical Damage permanently",
        "effect": "damage_boost"
    },
    "arcane_mind": {
        "name": "Arcane Mind",
        "desc": "+40 Max Mana permanently",
        "effect": "mana_boost"
    },
    "colossus_vitality": {
        "name": "Colossus Vitality",
        "desc": "+50 Max HP permanently",
        "effect": "hp_boost"
    },
    "shadow_step": {
        "name": "Shadow Step",
        "desc": "+15 Stealth & Dodge agility permanently",
        "effect": "stealth_boost"
    }
}


def perform_reincarnation(caller, trait_key):
    """Executes the soul reincarnation ritual for veteran adventurers."""
    key = trait_key.lower().strip()
    trait = HERITAGE_TRAITS.get(key)
    if not trait:
        for t_k, data in HERITAGE_TRAITS.items():
            if key in t_k or key in data["name"].lower():
                trait = data
                key = t_k
                break

    if not trait:
        caller.msg(f"Unknown heritage trait '{trait_key}'. Available: {', '.join(HERITAGE_TRAITS.keys())}")
        return False, "Unknown trait."

    lvl = caller.db.level or 1
    if lvl < 10:
        return False, f"You must be at least Level 10 to undergo ancestral reincarnation! (Currently Level {lvl})"

    # Increment soul shards
    shards = (caller.db.soul_shards or 0) + 1
    caller.db.soul_shards = shards

    # Apply trait
    traits = getattr(caller.db, "heritage_traits", []) or []
    traits.append(trait["name"])
    caller.db.heritage_traits = traits

    # Reset level to 1, preserve XP baseline
    caller.db.level = 1
    caller.db.xp = 0

    if trait["effect"] == "hp_boost":
        caller.db.max_hp = (caller.db.max_hp or 100) + 50
    elif trait["effect"] == "mana_boost":
        caller.db.max_mana = (caller.db.max_mana or 100) + 40

    caller.msg(f"\n|Y====================== ANCESTRAL REINCARNATION ======================|n")
    caller.msg(f"|WYour mortal shell dissolves into golden starlight as your soul transcends!|n")
    caller.msg(f"|YYou are reborn anew as a Level 1 Adventurer, carrying Soul Shard #{shards}!|n")
    caller.msg(f"|GBlessing Bestowed:|n |w{trait['name']}|n ({trait['desc']})\n")
    caller.msg("|Y====================================================================|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"|YBlinding celestial starlight bursts from {caller.key} as their soul undergoes sacred reincarnation!|n",
            exclude=[caller]
        )
    return True, "Reincarnated."

