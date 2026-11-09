"""
Nightmare LPmud Deities, Shrines & Divine Favor System.

Implements:
1. Pantheon of Gods (Solaris, Moradin, Nocturna, Khorne).
2. Swearing devotion ('worship <deity>').
3. Prayer at shrines ('pray') and Altar Sacrifices ('sacrifice <item/gold>').
4. Divine Favor progression and miraculous blessings.
"""

DEITIES = {
    "solaris": {
        "name": "Solaris the Sun Lord",
        "domain": "Light, Healing, Radiant Wrath",
        "blessing": "Aura of Radiant Healing (+20% healing received)",
        "desc": "The blazing solar deity who purifies heresy and watches over healers and righteous paladins."
    },
    "moradin": {
        "name": "Moradin the Forge Father",
        "domain": "Earth, Smithing, Stone, Endurance",
        "blessing": "Adamantine Skin (+15 Physical Damage Absorption)",
        "desc": "The rugged patron of dwarven blacksmiths and subterranean tunnel wardens."
    },
    "nocturna": {
        "name": "Nocturna the Night Mother",
        "domain": "Shadows, Secrets, Lunar Magic",
        "blessing": "Shroud of Erebos (+20% Stealth & +5 Mana Regen)",
        "desc": "The enigmatic mistress of midnight, rogues, assassins, and twilight sorcerers."
    },
    "khorne": {
        "name": "Khorne the War Bringer",
        "domain": "Battle, Martial Fury, Slaughter",
        "blessing": "Blood Rage (+8 Melee Damage, +10% Crit Chance)",
        "desc": "The ferocious god of unrelenting combat, testing martial warriors in trial by blade."
    }
}


def worship_deity(caller, deity_key):
    """Pledges soul and faith to a specific deity."""
    key = deity_key.lower().strip()
    data = DEITIES.get(key)
    if not data:
        for d_k, d_val in DEITIES.items():
            if key in d_k or key in d_val["name"].lower():
                data = d_val
                key = d_k
                break

    if not data:
        caller.msg(f"Unknown deity '{deity_key}'. Available: {', '.join(DEITIES.keys())}")
        return False, "Unknown deity."

    caller.db.deity = data["name"]
    caller.db.deity_key = key
    caller.db.divine_favor = 10

    caller.msg(f"\n|Y[DEVOTION PLEDGED]|n You kneel and swear your solemn faith to |w{data['name']}|n!")
    caller.msg(f"|xDomain:|n {data['domain']}")
    caller.msg(f"|GBlessing Granted:|n {data['blessing']}\n")
    if caller.location:
        caller.location.msg_contents(
            f"|Y{caller.key} kneels and swears holy devotion to {data['name']}.|n",
            exclude=[caller]
        )
    return True, "Devotion pledged."


def pray_at_altar(caller):
    """Prays at a sacred altar to receive divine restoration."""
    loc = caller.location
    if not loc:
        return False, "You cannot pray in the void."

    deity = getattr(caller.db, "deity", None)
    if not deity:
        caller.msg("You do not worship any deity! Choose a patron with: |wworship <deity>|n")
        return False, "No deity."

    favor = getattr(caller.db, "divine_favor", 0) or 0
    heal_amount = 25 + (favor // 2)

    caller.db.hp = min(caller.db.max_hp or 100, (caller.db.hp or 0) + heal_amount)
    caller.db.mana = min(caller.db.max_mana or 100, (caller.db.mana or 0) + 20)

    caller.msg(f"\n|Y*** DIVINE COMMUNION ***|n")
    caller.msg(f"You bow your head in humble prayer to {deity}.")
    caller.msg(f"|gA warm beam of celestial light washes over you, restoring {heal_amount} HP and 20 Mana!|n\n")

    if loc:
        loc.msg_contents(
            f"|yA shaft of divine light descends from above, enveloping {caller.key} in holy radiance as they pray.|n",
            exclude=[caller]
        )
    return True, "Prayed."


def sacrifice_to_deity(caller, gold_or_item):
    """Offers a sacrifice to the altar to build Divine Favor."""
    deity = getattr(caller.db, "deity", None)
    if not deity:
        return False, "You must choose a patron deity first with: |wworship <deity>|n"

    # Check if sacrifice is gold amount
    if isinstance(gold_or_item, int) or gold_or_item.isdigit():
        gold = int(gold_or_item)
        coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        if coins.get("gold", 0) < gold:
            return False, f"You do not have {gold} Gold to sacrifice."

        coins["gold"] -= gold
        caller.db.coins = coins

        favor_gain = max(1, gold // 5)
        caller.db.divine_favor = (caller.db.divine_favor or 0) + favor_gain

        caller.msg(f"\n|Y[ALTAR SACRIFICE]|n You place {gold} Gold upon the altar. Sacred flames consume the offering!")
        caller.msg(f"|G{deity} smiles upon your devotion! (+{favor_gain} Divine Favor, Total: {caller.db.divine_favor})|n\n")
        return True, "Sacrificed gold."
    else:
        # Item sacrifice
        item = caller.search(gold_or_item, location=caller)
        if not item:
            return False, f"Could not find '{gold_or_item}' in your inventory."

        val = getattr(item.db, "value", 10) or 10
        item_name = item.key
        item.delete()

        favor_gain = max(2, val // 10)
        caller.db.divine_favor = (caller.db.divine_favor or 0) + favor_gain

        caller.msg(f"\n|Y[ALTAR SACRIFICE]|n You lay {item_name} upon the sacred altar. Holy fire engulfs the relic!")
        caller.msg(f"|G{deity} accepts your offering! (+{favor_gain} Divine Favor, Total: {caller.db.divine_favor})|n\n")
        return True, "Sacrificed item."

