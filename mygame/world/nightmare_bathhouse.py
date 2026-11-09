"""
Nightmare LPmud Thermal Bathhouse, Steam Vapor & Mineral Soaking Engine.

Implements:
1. Praxis Civic Bathhouse Facilities:
   - Caldarium Sulfur Thermal Pool (Deep muscle recovery & toxin purge)
   - Eucalyptus Steam Vault (Respiratory clearing & mana surge)
   - Frigidarium Cold Plunge (Nervous system shock & stamina invigoration)
2. Bathhouse directory and soaking mechanics ('bathhouse', 'soak <pool>').
3. Combat gore and grime washing ('washgrime').
4. 'Rejuvenated Spirit' long-lasting vitality buff.
"""

BATHHOUSE_POOLS = {
    "caldarium": {
        "name": "Caldarium Sulfur Thermal Pool",
        "temp": "104°F (Scalding Hot)",
        "mineral": "Volcanic Sulfur & Epsom Salts",
        "effect": "Purges poisons, soothes fractured limbs, restores +30 HP",
        "desc": "A sunken marble pool fed by subterranean geothermal aqueducts, thick with therapeutic sulfur steam."
    },
    "steam": {
        "name": "Eucalyptus Steam Vault",
        "temp": "115°F (Dense Vapor)",
        "mineral": "Distilled Eucalyptus & Cedar Oils",
        "effect": "Clears lungs, expands awareness, restores +35 Mana",
        "desc": "A domed stone chamber billowing with hot, aromatic herbal mist that condenses on cool tiles."
    },
    "frigidarium": {
        "name": "Frigidarium Cold Plunge",
        "temp": "45°F (Glacial Cold)",
        "mineral": "Chilled Mountain Spring Water",
        "effect": "Shocks circulation, restores +35 Stamina & invigoration",
        "desc": "A crystalline plunge basin filled with snowmelt water, ringed by mosaic dolphins and sea nymphs."
    }
}


def format_bathhouse_directory():
    """Formats bathhouse menu and facilities."""
    lines = [
        "|c" + "=" * 70 + "|n",
        "|w               PRAXIS CIVIC BATHHOUSE & GEOTHERMAL SPRINGS        |n",
        "|c" + "=" * 70 + "|n"
    ]

    for key, data in BATHHOUSE_POOLS.items():
        lines.append(f"\n|Y[{key.upper()}]|n |w{data['name']}|n [Temp: |c{data['temp']}|n]")
        lines.append(f"  |yMinerals & Aromatics:|n {data['mineral']}")
        lines.append(f"  |gTherapeutic Boon:|n {data['effect']}")
        lines.append(f"  |x{data['desc']}|n")

    lines.append("\n|c" + "=" * 70 + "|n")
    lines.append("|xTo immerse yourself: 'soak <caldarium|steam|frigidarium>' or 'washgrime'|n")
    return "\n".join(lines)


def soak_in_pool(caller, pool_key="caldarium"):
    """Immerses caller in a therapeutic mineral bath or steam room."""
    key = pool_key.strip().lower()
    matched = next((k for k in BATHHOUSE_POOLS if key in k), None)

    if not matched:
        opts = ", ".join(BATHHOUSE_POOLS.keys())
        return False, f"Unknown bathhouse pool '{pool_key}'. Options: {opts}"

    pool = BATHHOUSE_POOLS[matched]

    if matched == "caldarium":
        curr_hp = getattr(caller.db, "hp", 100) or 100
        max_hp = getattr(caller.db, "max_hp", 100) or 100
        caller.db.hp = min(max_hp, curr_hp + 30)
    elif matched == "steam":
        curr_mana = getattr(caller.db, "mana", 100) or 100
        max_mana = getattr(caller.db, "max_mana", 100) or 100
        caller.db.mana = min(max_mana, curr_mana + 35)
    elif matched == "frigidarium":
        curr_stam = getattr(caller.db, "stamina", 100) or 100
        max_stam = getattr(caller.db, "max_stamina", 100) or 100
        caller.db.stamina = min(max_stam, curr_stam + 35)

    caller.db.rejuvenated_buff = True

    caller.msg(
        f"\n|C[BATHHOUSE IMMERSION]|n You sink deeply into the {pool['name']}.\n"
        f"The {pool['mineral']} envelopes your skin as tension and grime dissolve away!\n"
        f"|gTherapeutic effect applied! You gain the |W'Rejuvenated Spirit'|g buff!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} immerses themselves into the soothing waters of the {pool['name']}.",
            exclude=[caller]
        )
    return True, "Soaked in pool."


def wash_battle_grime(caller):
    """Washes away dried gore, soot, and dungeon grime."""
    caller.msg(
        "\n|YYou lather scented olive-oil soap and rinse thoroughly under a stream of warm spring water.\n"
        "|wEvery trace of blood, grave dust, and dungeon grime is washed clean away!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} washes clean their skin and gear under a warm water stream.",
            exclude=[caller]
        )
    return True, "Cleaned grime."

