"""
Nightmare LPmud Martial Specialization & Master Trainer System.

Implements:
1. Master Combat Specializations (Dual-Wielding, Shield Bulwark, Critical Lethality, Spellweaving).
2. Permanent passive perk bonuses.
3. Master trainer progression inquiry ('specialize').
"""

SPECIALIZATIONS = {
    "dualwield": {
        "name": "Dual-Wielding Mastery",
        "req_level": 5,
        "desc": "Master the art of wielding blades in both hands, unleashing a secondary off-hand strike (+25% Damage).",
        "perk": "Off-hand strike proc in combat"
    },
    "bulwark": {
        "name": "Shield Bulwark",
        "req_level": 5,
        "desc": "Transform your shield into an impenetrable fortress wall, gaining +20% chance to completely deflect blows.",
        "perk": "Deflect attacks and absorb damage"
    },
    "lethality": {
        "name": "Critical Lethality",
        "req_level": 5,
        "desc": "Hone anatomical precision with daggers and blades, amplifying critical sneak attacks to 3.5x damage.",
        "perk": "3.5x Critical strike multiplier"
    },
    "spellweaving": {
        "name": "Arcane Spellweaving",
        "req_level": 5,
        "desc": "Weave complex leylines with effortless efficiency, reducing all spell mana costs by 20%.",
        "perk": "-20% Mana cost on all spells"
    }
}


def choose_specialization(caller, spec_key):
    """Pledges training into a master combat specialization."""
    key = spec_key.lower().strip()
    data = SPECIALIZATIONS.get(key)
    if not data:
        for s_k, s_val in SPECIALIZATIONS.items():
            if key in s_k or key in s_val["name"].lower():
                data = s_val
                key = s_k
                break

    if not data:
        caller.msg(f"Unknown specialization '{spec_key}'. Available: {', '.join(SPECIALIZATIONS.keys())}")
        return False, "Unknown spec."

    lvl = caller.db.level or 1
    if lvl < data["req_level"]:
        return False, f"You must be at least Level {data['req_level']} to specialize into {data['name']}!"

    current = getattr(caller.db, "specialization", None)
    if current == data["name"]:
        return False, f"You are already specialized in {data['name']}."

    caller.db.specialization = data["name"]
    caller.db.specialization_key = key

    caller.msg(f"\n|Y*** SPECIALIZATION MASTERED! ***|n")
    caller.msg(f"|yThe Grandmaster approves your technique. You are now specialized in: |w{data['name']}|y!|n")
    caller.msg(f"|GPassive Mastery Active:|n {data['desc']}\n")

    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} completes their master trial, attaining specialization in {data['name']}!",
            exclude=[caller]
        )
    return True, "Specialized."

