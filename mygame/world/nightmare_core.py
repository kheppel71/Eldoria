"""
Nightmare LPmud Core Systems for Evennia
Complete Multi-Phase Architecture:
Phase 1: True Spellbooks, Scribing, High Arcane Incantations & Reagents
Phase 2: Use-Based Skill Ticks, Proficiencies & Riposte Synergies
Phase 3: Prestige Guild Subclasses, Ranks & Signature Abilities
Phase 4: Exotic Races (Dragonkin, Centaur), Morphologies & Racial Actives
"""

import random
from evennia.utils.create import create_object
from evennia.objects.models import ObjectDB
from typeclasses.objects import Object


# =============================================================================
# GUILDS & CLASSES
# =============================================================================

GUILDS = {
    "Fighter": {
        "desc": "Masters of heavy armor, martial weapons, shields, and tactical melee combat.",
        "leader": "Ser Gareth",
        "location": "High Tower Barracks"
    },
    "Mage": {
        "desc": "Scholars of the arcane arts, wielding evocation, abjuration, and teleportation spells.",
        "leader": "Archmage Vaelin",
        "location": "Arcane Library"
    },
    "Cleric": {
        "desc": "Devoted servants of the celestial heavens, blessed with miraculous healing and divine smites.",
        "leader": "High Priestess Meredith",
        "location": "Cathedral of Light"
    },
    "Rogue": {
        "desc": "Masters of stealth, lockpicking, backstabbing, poisons, and shadows.",
        "leader": "Master Kael",
        "location": "The Velvet Dagger"
    },
    "Ranger": {
        "desc": "Wilderness trackers and lethal archers accompanied by bonded beasts.",
        "leader": "Huntress Sylva",
        "location": "Whispering Grove"
    }
}


# =============================================================================
# PHASE 1: SPELL ENGINE, INCANTATIONS & REAGENTS
# =============================================================================

SPELLS = {
    "firebolt": {
        "name": "Firebolt",
        "school": "Evocation",
        "mana": 15,
        "chant": "Pyros Ignis!",
        "reagent": None,
        "desc": "A crackling dart of elemental flame.",
        "min_dmg": 25, "max_dmg": 45, "stat": "int",
        "skill": "magic attack"
    },
    "fireball": {
        "name": "Fireball",
        "school": "Evocation",
        "mana": 35,
        "chant": "Pyros Ignis Calamitas!",
        "reagent": "sulfur",
        "desc": "A roaring sphere of fire that engulfs the target in an inferno.",
        "min_dmg": 55, "max_dmg": 95, "stat": "int",
        "skill": "magic attack"
    },
    "lightning": {
        "name": "Lightning Bolt",
        "school": "Evocation",
        "mana": 30,
        "chant": "Fulgur Mortis!",
        "reagent": None,
        "desc": "A searing fork of lightning that arcs through armor.",
        "min_dmg": 40, "max_dmg": 80, "stat": "int",
        "skill": "magic attack"
    },
    "stoneskin": {
        "name": "Stone Skin",
        "school": "Abjuration",
        "mana": 25,
        "chant": "Petra Duritas!",
        "reagent": "dust",
        "desc": "Hardens flesh to absorb 80 points of incoming physical damage.",
        "absorb": 80,
        "skill": "magic defense"
    },
    "blink": {
        "name": "Blink",
        "school": "Transmutation",
        "mana": 20,
        "chant": "Spatium Evanesco!",
        "reagent": None,
        "desc": "Blinks the caster through the ether, evading melee engagement.",
        "skill": "magic defense"
    },
    "heal": {
        "name": "Heal",
        "school": "Restoration",
        "mana": 20,
        "chant": "Sanatio Vitae!",
        "reagent": None,
        "desc": "Channels celestial light to mend wounded limbs and restore HP.",
        "min_heal": 35, "max_heal": 65, "stat": "wis",
        "skill": "healing"
    },
    "smite": {
        "name": "Divine Smite",
        "school": "Divinity",
        "mana": 25,
        "chant": "Lux Aeterna!",
        "reagent": "holy water",
        "desc": "Channels radiant solar wrath to scorch heretics and undead.",
        "min_dmg": 45, "max_dmg": 75, "stat": "wis",
        "skill": "faith"
    },
    "animate": {
        "name": "Animate Dead",
        "school": "Necromancy",
        "mana": 45,
        "chant": "Mors Resurget!",
        "reagent": "grave dust",
        "desc": "Binds a restless soul into a fallen corpse, creating a skeletal thrall.",
        "skill": "magic attack"
    }
}


# =============================================================================
# PHASE 2: USE-BASED SKILL TICKS & SYNERGIES
# =============================================================================

def trigger_skill_tick(char, skill_name, difficulty=50):
    """
    Simulates Nightmare LPmud's use-based skill advancement.
    Every successful action has a chance to raise skill proficiency by 1%.
    """
    if not hasattr(char, "db") or not char.db.skills:
        return

    skills = char.db.skills
    curr_val = skills.get(skill_name, 10)
    if curr_val >= 100:
        return

    # Roll based on int, difficulty, and current value (diminishing returns as skill nears 100)
    intel = getattr(char.db, "int", 12)
    chance = max(5, int((100 - curr_val) * 0.4) + (intel // 3))

    if random.randint(1, 100) <= chance:
        skills[skill_name] = curr_val + 1
        char.msg(f"|gYou feel your proficiency in {skill_name.title()} improve! ({curr_val}% -> {curr_val + 1}%)|n")


# =============================================================================
# PHASE 3: PRESTIGE GUILD SUBCLASSES & SPECIALIZATIONS
# =============================================================================

PRESTIGE_SUBCLASSES = {
    # Fighter Specializations
    "Knight": {
        "parent": "Fighter",
        "desc": "Chivalric defender clad in impenetrable plate mail with protective auras.",
        "ability": "shieldwall",
        "ability_desc": "Raises a massive defensive shieldwall that halves incoming damage for 30s.",
        "stat_bonus": {"con": 3, "str": 1}
    },
    "Berserker": {
        "parent": "Fighter",
        "desc": "Savage warlord who enters an adrenaline-fueled blood frenzy in battle.",
        "ability": "rage",
        "ability_desc": "Enters a blood rage (+15 weapon damage, but drains stamina).",
        "stat_bonus": {"str": 4, "dex": 1}
    },
    # Mage Specializations
    "Pyromancer": {
        "parent": "Mage",
        "desc": "Master of destructive flame and explosive thermal incantations.",
        "ability": "combustion",
        "ability_desc": "Detonates target with pure thermal fire (+50% Fireball damage).",
        "stat_bonus": {"int": 4}
    },
    "Conjurer": {
        "parent": "Mage",
        "desc": "Summoner of arcane elementals and planar familiars.",
        "ability": "elemental",
        "ability_desc": "Summons a temporary fire or earth elemental companion.",
        "stat_bonus": {"int": 2, "wis": 2}
    },
    # Cleric Specializations
    "Healer": {
        "parent": "Cleric",
        "desc": "Divine vessel dedicated to miraculous group healing and regeneration.",
        "ability": "blessing",
        "ability_desc": "Channels an aura of divine regeneration that restores health over time.",
        "stat_bonus": {"wis": 4}
    },
    "Inquisitor": {
        "parent": "Cleric",
        "desc": "Holy crusader who smites evil and purges undead with scorched solar fire.",
        "ability": "exorcism",
        "ability_desc": "Unleashes a devastating holy blast that deals 3x damage to undead.",
        "stat_bonus": {"str": 2, "wis": 2}
    },
    # Rogue Specializations
    "Assassin": {
        "parent": "Rogue",
        "desc": "Deadly shadow master specialized in venomous blades and lethal ambushes.",
        "ability": "poison",
        "ability_desc": "Coats blades with lethal wyvern venom (+20 poison damage per strike).",
        "stat_bonus": {"dex": 4}
    },
    "Shadowthief": {
        "parent": "Rogue",
        "desc": "Elusive infiltrator who slips through shadows without leaving footprints.",
        "ability": "shadowstep",
        "ability_desc": "Melds into the shadows to become completely invisible to enemies.",
        "stat_bonus": {"dex": 3, "cha": 2}
    },
    # Ranger Specializations
    "Beastmaster": {
        "parent": "Ranger",
        "desc": "Warden of the wild accompanied by fierce wolves and birds of prey.",
        "ability": "callpet",
        "ability_desc": "Calls a mountain dire wolf to attack target alongside you.",
        "stat_bonus": {"dex": 2, "wis": 2}
    },
    "Sniper": {
        "parent": "Ranger",
        "desc": "Deadly marksman capable of piercing armor from extreme distances.",
        "ability": "aimedshot",
        "ability_desc": "Executes a lethal aimed arrow strike that bypasses enemy armor.",
        "stat_bonus": {"dex": 4}
    }
}


# =============================================================================
# PHASE 4: EXOTIC RACES & MORPHOLOGIES
# =============================================================================

RACES = {
    "Human": {
        "desc": "Adaptable and ambitious with rapid learning capacity (+15% XP gain).",
        "bonus": {"xp_mult": 1.15},
        "nightvision": False,
        "ability": "rally",
        "ability_desc": "Rallies fighting spirit to restore 40 stamina and clear fatigue."
    },
    "Elf": {
        "desc": "Graceful immortals with innate infravision and heightened magical attunement.",
        "bonus": {"dex": 2, "int": 1, "con": -1},
        "nightvision": True,
        "ability": "feystep",
        "ability_desc": "Steps through the fey realm to evade incoming attacks."
    },
    "Dwarf": {
        "desc": "Stout mountain folk with stone-like resilience and subterranean darkvision.",
        "bonus": {"con": 2, "str": 1, "dex": -1},
        "nightvision": True,
        "ability": "stoneform",
        "ability_desc": "Hardens skin into solid granite, gaining +30 defense for 45 seconds."
    },
    "Halfling": {
        "desc": "Small, nimble folk with uncanny luck and natural shadows stealth.",
        "bonus": {"dex": 3, "str": -2},
        "nightvision": False,
        "ability": "luckydodge",
        "ability_desc": "Evades the next incoming lethal blow with miraculous agility."
    },
    "Drow": {
        "desc": "Subterranean shadow-elves lethal in dark dungeons with total darkvision.",
        "bonus": {"int": 2, "dex": 2, "con": -2},
        "nightvision": True,
        "ability": "darkness",
        "ability_desc": "Summons a globe of magical darkness that blinds all enemies in the room."
    },
    "Dragonkin": {
        "desc": "Towering scaled draconic humanoids with natural armored scales and a tail.",
        "bonus": {"str": 3, "con": 2, "dex": -1},
        "nightvision": True,
        "ability": "breathefire",
        "ability_desc": "Exhales a blistering cone of dragon breath dealing heavy fire damage."
    },
    "Centaur": {
        "desc": "Equine nomads with four hooves, unmatched overland speed, and devastating trampling kicks.",
        "bonus": {"str": 2, "dex": 2, "con": 1},
        "nightvision": False,
        "ability": "trample",
        "ability_desc": "Charges the enemy with iron hooves, dealing blunt damage and knocking them prone."
    }
}

EQUIPMENT_SLOTS = ["head", "torso", "legs", "feet", "main_hand", "off_hand", "amulet", "ring"]


def init_nightmare_character(char):
    """Initializes full Nightmare-style character sheets, spellbooks, and limbs."""
    if not char.db.nightmare_initialized:
        char.db.nightmare_initialized = True
        char.db.race = char.db.race or "Human"
        char.db.guild = char.db.guild or "Adventurer"
        char.db.subclass = None
        char.db.level = char.db.level or 1
        char.db.xp = char.db.xp or 500

        # Stats
        char.db.str = char.db.str or 14
        char.db.dex = char.db.dex or 13
        char.db.con = char.db.con or 14
        char.db.int = char.db.int or 12
        char.db.wis = char.db.wis or 11
        char.db.cha = char.db.cha or 12

        # Vitals
        max_hp = char.db.con * 10
        max_mana = char.db.int * 8
        max_stamina = (char.db.con + char.db.dex) * 5

        char.db.max_hp = max_hp
        char.db.hp = max_hp
        char.db.max_mana = max_mana
        char.db.mana = max_mana
        char.db.max_stamina = max_stamina
        char.db.stamina = max_stamina

        # Limbs based on race
        limbs = {
            "head": {"hp": 50, "max_hp": 50},
            "torso": {"hp": 100, "max_hp": 100},
            "right arm": {"hp": 60, "max_hp": 60},
            "left arm": {"hp": 60, "max_hp": 60},
            "right leg": {"hp": 70, "max_hp": 70},
            "left leg": {"hp": 70, "max_hp": 70},
        }
        if char.db.race == "Dragonkin":
            limbs["tail"] = {"hp": 50, "max_hp": 50}
        elif char.db.race == "Centaur":
            limbs["forelegs"] = {"hp": 80, "max_hp": 80}
            limbs["hindlegs"] = {"hp": 90, "max_hp": 90}

        char.db.limbs = limbs
        char.db.slots = {slot: None for slot in EQUIPMENT_SLOTS}

        # Currency
        char.db.coins = {"copper": 50, "silver": 25, "gold": 10}
        char.db.bank_coins = {"copper": 0, "silver": 0, "gold": 100}
        char.db.bank_vault = []

        # Skills
        char.db.skills = {
            "blade": 20,
            "blunt": 15,
            "projectile": 15,
            "brawl": 15,
            "defense": 20,
            "parry": 15,
            "stealth": 10,
            "magic attack": 15,
            "magic defense": 10,
            "healing": 10,
            "faith": 10,
            "fishing": 15
        }

        # Spellbook: Starts with basic firebolt and heal
        char.db.spellbook = ["firebolt", "heal"]
        char.db.stoneskin_absorb = 0
        char.db.is_ghost = False
        char.db.wimpy = getattr(char.db, "wimpy", 0) or 0
        char.db.party = getattr(char.db, "party", None)

        # Languages
        from world.languages import get_innate_languages
        char.db.languages = char.db.languages or get_innate_languages(char.db.race, char.db.guild)
        char.db.active_language = char.db.active_language or "common"


# =============================================================================
# DEATH, RESURRECTION & GHOSTS
# =============================================================================

def handle_player_death(char):
    """Transforms player into a ghost and leaves a lootable corpse."""
    location = char.location or ObjectDB.objects.get(id=2)

    char.db.is_ghost = True
    char.db.hp = 1

    corpse = create_object(
        Object,
        key=f"Corpse of {char.key}",
        location=location,
        aliases=["corpse", f"corpse of {char.key.lower()}"],
        tags=["eldoria_world", "player_corpse"]
    )
    corpse.db.desc = f"The slain physical body of {char.key}, lying cold upon the ground. Can be looted."
    corpse.db.owner_id = char.id

    items_to_move = [
        item for item in char.contents
        if not item.db.is_soulbound and item != corpse
    ]
    for item in items_to_move:
        item.move_to(corpse, quiet=True)

    char.msg(
        "\n|r========================================================\n"
        "*** YOU HAVE DIED! ***\n"
        "Your mortal body collapses lifeless to the floor!\n"
        "Your soul rips free of the flesh, transforming into a translucent ghost!\n"
        "Your gear remains inside your corpse here in this room.\n"
        "Seek Sister Meredith at the Cathedral of Light to be resurrected!\n"
        "========================================================|n\n"
    )

    location.msg_contents(
        f"|r{char.key} collapses to the ground, dead! A pale ghost rises from the fallen corpse!|n",
        exclude=[char]
    )


def resurrect_player(char):
    """Restores a ghost back to life."""
    if not char.db.is_ghost:
        return False, "You are already among the living!"

    char.db.is_ghost = False
    char.db.hp = char.db.max_hp
    char.db.mana = char.db.max_mana
    char.db.stamina = char.db.max_stamina

    if char.db.limbs:
        for limb in char.db.limbs.values():
            limb["hp"] = limb["max_hp"]

    char.msg(
        "\n|g========================================================\n"
        "*** RESURRECTION! ***\n"
        "Divine golden sunlight envelops your ghostly form!\n"
        "Flesh, blood, and breath knit back together as you return to the living!\n"
        "Make haste to your corpse to reclaim your worldly possessions.\n"
        "========================================================|n\n"
    )
    return True, "Resurrection complete."


def room_is_illuminated(char, room):
    """Checks if a room has sufficient light for character to see."""
    if not room.db.is_dark:
        return True

    race_info = RACES.get(char.db.race, {})
    if race_info.get("nightvision"):
        return True

    for item in char.contents:
        if "torch" in item.key.lower() and getattr(item.db, "is_lit", True):
            return True
        if "wisp lantern" in item.key.lower() or "blazing" in item.key.lower():
            return True
        if "crystal phial" in item.key.lower() and "moonlight" in item.key.lower():
            return True

    return False


# =============================================================================
# COMBAT WITH RIPOSTE SYNERGY & LIMB DAMAGE
# =============================================================================

def calculate_weapon_damage(attacker):
    """Computes weapon damage based on equipped weapon, subclass, and stats."""
    slots = attacker.db.slots or {}
    main_hand = slots.get("main_hand")

    str_mod = max(1, (attacker.db.str or 10) // 3)
    bonus = 0

    # Subclass bonuses
    if attacker.db.subclass == "Berserker" and attacker.db.is_raging:
        bonus += 15

    if main_hand and main_hand in attacker.contents:
        key = main_hand.key.lower()
        if "broadsword" in key or "sword" in key:
            dmg = random.randint(12, 22) + str_mod + bonus
            w_name = main_hand.key
            trigger_skill_tick(attacker, "blade", 40)
        elif "bow" in key:
            dex_mod = max(1, (attacker.db.dex or 10) // 3)
            dmg = random.randint(14, 24) + dex_mod + bonus
            w_name = main_hand.key
            trigger_skill_tick(attacker, "projectile", 40)
        elif "cutlass" in key:
            dmg = random.randint(10, 20) + str_mod + bonus
            w_name = main_hand.key
            trigger_skill_tick(attacker, "blade", 40)
        else:
            dmg = random.randint(8, 16) + str_mod + bonus
            w_name = main_hand.key
            trigger_skill_tick(attacker, "blunt", 40)
    else:
        dmg = random.randint(3, 8) + str_mod + bonus
        w_name = "bare fists"
        trigger_skill_tick(attacker, "brawl", 30)

    return dmg, w_name


def perform_combat_round(attacker, defender):
    """Executes combat with hit chance, limb targeting, parry, and riposte."""
    if getattr(attacker.db, "is_ghost", False):
        attacker.msg("You are a ghost! You cannot interact with the physical world!")
        return

    dmg, weapon_name = calculate_weapon_damage(attacker)

    # Halfling lucky dodge active
    if defender.db.lucky_dodge:
        defender.db.lucky_dodge = False
        defender.msg(f"|g*** LUCKY DODGE! *** You tumble underneath {attacker.key}'s {weapon_name} with uncanny halfling luck!|n")
        attacker.msg(f"|x{defender.key} miraculously dodges your strike with astonishing agility!|n")
        return

    # Defender parry check
    def_parry = defender.db.skills.get("parry", 15) if hasattr(defender, "db") and defender.db.skills else 15
    if random.randint(1, 100) <= (def_parry // 2):
        defender.msg(f"|cYou cleanly PARRY {attacker.key}'s {weapon_name}!|n")
        attacker.msg(f"|x{defender.key} expertly PARRIES your {weapon_name}!|n")
        trigger_skill_tick(defender, "parry", 45)

        # Riposte Synergy: Counter-attack!
        if def_parry >= 40:
            c_dmg = random.randint(10, 20)
            attacker.db.hp = max(0, (attacker.db.hp or 50) - c_dmg)
            defender.msg(f"|Y*** RIPOSTE! *** You counter-attack instantly, striking {attacker.key} for {c_dmg} damage!|n")
            attacker.msg(f"|R{defender.key} ripostes your parried strike, hitting you for {c_dmg} damage!|n")
        return

    # Hit / Miss roll
    hit_chance = 75 + ((attacker.db.dex or 10) - (defender.db.dex or 10)) * 2
    if random.randint(1, 100) > hit_chance:
        attacker.msg(f"|xYou swing your {weapon_name} at {defender.key}, but MISS!|n")
        defender.msg(f"|x{attacker.key} swings at you with their {weapon_name}, but MISSES!|n")
        trigger_skill_tick(defender, "defense", 40)
        return

    # Knight Shieldwall damage reduction
    if defender.db.shieldwall:
        dmg = max(1, dmg // 2)
        defender.msg("|cYour towering Shieldwall absorbs half of the incoming damage!|n")

    # Check Stone Skin absorption
    stoneskin = defender.db.stoneskin_absorb or 0
    if stoneskin > 0:
        absorbed = min(stoneskin, dmg)
        defender.db.stoneskin_absorb -= absorbed
        dmg -= absorbed
        defender.msg(f"|yYour Stone Skin absorbs {absorbed} damage! ({defender.db.stoneskin_absorb} left)|n")
        attacker.msg(f"|yYour blow rebounds off {defender.key}'s granite-like Stone Skin!|n")
        if dmg <= 0:
            return

    # Assassin Envenomed blade bonus
    poison_charges = attacker.db.poison_blade or 0
    if poison_charges > 0:
        p_dmg = 15
        dmg += p_dmg
        attacker.db.poison_blade = poison_charges - 1
        attacker.msg(f"|gYour envenomed blade burns with toxic wyvern poison! (+{p_dmg} Poison Dmg)|n")
        defender.msg(f"|gWyvern venom burns agonizingly in your bloodstream! (-{p_dmg} HP)|n")

    # Select targeted limb
    limbs = defender.db.limbs or {}
    limb_choices = list(limbs.keys()) if limbs else ["torso", "head", "legs"]
    target_limb = random.choice(limb_choices)

    # Apply damage
    def_hp = getattr(defender.db, "hp", 50)
    new_hp = max(0, def_hp - dmg)
    defender.db.hp = new_hp

    if target_limb in limbs:
        limbs[target_limb]["hp"] = max(0, limbs[target_limb]["hp"] - dmg)

    color = "|R" if dmg > 18 else "|y"
    attacker.msg(f"{color}You strike {defender.key}'s {target_limb} with your {weapon_name} for {dmg} damage!|n")
    defender.msg(f"|r{attacker.key} strikes your {target_limb} with their {weapon_name} for {dmg} damage!|n")

    # Dragonkin auxiliary tail strike!
    if attacker.db.race == "Dragonkin" and random.randint(1, 100) <= 40:
        tail_dmg = random.randint(8, 16)
        defender.db.hp = max(0, defender.db.hp - tail_dmg)
        attacker.msg(f"|Y*** TAIL LASH! *** Your spined dragon tail whips around and lashes {defender.key} for {tail_dmg} damage!|n")
        defender.msg(f"|r{attacker.key}'s dragon tail smashes into you for {tail_dmg} bludgeoning damage!|n")

    show_combat_hud(attacker, defender)

    if new_hp <= 0:
        # Clear combat engagement state
        if hasattr(attacker, "ndb"):
            attacker.ndb.combat_target = None
        if hasattr(defender, "ndb"):
            defender.ndb.combat_target = None

        is_player = bool(
            getattr(defender, "has_account", False)
            or (getattr(defender, "account", None) is not None)
            or (getattr(defender, "sessions", None) and defender.sessions.all())
        )
        if is_player:
            handle_player_death(defender)
            attacker.msg(f"|Y*** YOU HAVE SLAIN {defender.key.upper()}! ***|n")
            xp_reward = 100
            if getattr(attacker.db, "race", "") == "Human":
                xp_reward = int(xp_reward * 1.15)
            attacker.db.xp = (attacker.db.xp or 0) + xp_reward
            attacker.msg(f"|gYou gain {xp_reward} Experience Points! (Total: {attacker.db.xp})|n")
        else:
            if defender.location:
                defender.location.msg_contents(f"|r{defender.key} collapses dead from mortal wounds!|n")
            corpse = create_object(
                Object,
                key=f"Corpse of {defender.key}",
                location=defender.location,
                aliases=["corpse"],
                tags=["eldoria_world"]
            )
            corpse.db.desc = f"The remains of {defender.key}."
            mob_lvl = getattr(defender.db, "level", 1) or 1
            xp_reward = max(35, mob_lvl * 40)
            if getattr(attacker.db, "race", "") == "Human":
                xp_reward = int(xp_reward * 1.15)
            attacker.db.xp = (getattr(attacker.db, "xp", 0) or 0) + xp_reward
            attacker.msg(f"|Y*** YOU HAVE SLAIN {defender.key.upper()}! ***|n")
            if getattr(attacker.db, "party", None):
                distribute_party_xp(attacker, xp_reward)
            else:
                attacker.db.xp = (getattr(attacker.db, "xp", 0) or 0) + xp_reward
                attacker.msg(f"|gYou gain {xp_reward} Experience Points! (Total: {attacker.db.xp})|n")
            defender.delete()


def show_combat_hud(char, target):
    """Renders the classic Nightmare real-time HUD prompt."""
    hp = char.db.hp or 100
    max_hp = char.db.max_hp or 100
    mana = char.db.mana or 50
    max_mana = char.db.max_mana or 50
    stm = char.db.stamina or 80
    max_stm = char.db.max_stamina or 80

    t_hp = target.db.hp or 50
    t_max = target.db.max_hp or 50
    t_pct = int((t_hp / max(1, t_max)) * 100)

    hud = f"|w[ HP: |g{hp}/{max_hp}|w | Mana: |c{mana}/{max_mana}|w | Stm: |y{stm}/{max_stm}|w | Target: |r{target.key} ({t_pct}%)|w ]|n"
    char.msg(hud)


# =============================================================================
# REAL-TIME AUTOMATIC COMBAT LOOP ENGINE
# =============================================================================

def is_in_combat(char):
    """Returns True if the character is actively locked in combat."""
    return bool(getattr(char.ndb, "combat_target", None))


def disengage_combat(char, target=None):
    """
    Safely terminates combat between char and target (or char's active target).
    """
    if not char:
        return
    active_target = target or getattr(char.ndb, "combat_target", None)
    if hasattr(char, "ndb"):
        char.ndb.combat_target = None

    if active_target and hasattr(active_target, "ndb"):
        if getattr(active_target.ndb, "combat_target", None) == char:
            active_target.ndb.combat_target = None


def start_combat(attacker, defender):
    """
    Initiates real-time auto-combat between attacker and defender.
    Locks mutual combat targets, executes Round 1 immediately,
    and automatically cycles subsequent rounds every 2.4 seconds until a combatant dies or flees.
    """
    if getattr(attacker.db, "is_ghost", False):
        attacker.msg("You are a ghost! You cannot attack the physical world.")
        return

    if getattr(defender.db, "is_ghost", False):
        attacker.msg(f"{defender.key} is a spirit and cannot be harmed physically.")
        return

    # Check if attacker is already fighting this exact target
    current_target = getattr(attacker.ndb, "combat_target", None)
    if current_target == defender:
        attacker.msg(f"You are already fighting {defender.key}!")
        return

    # Break any resting state
    attacker.db.is_resting = False
    defender.db.is_resting = False

    # Set mutual combat engagement
    attacker.ndb.combat_target = defender
    defender.ndb.combat_target = attacker

    attacker.msg(f"\n|R[COMBAT ENGAGED] You attack {defender.key}! Auto-attack rounds will continue.|n")
    defender.msg(f"\n|R[COMBAT ENGAGED] {attacker.key} attacks you!|n")
    if attacker.location:
        attacker.location.msg_contents(
            f"|r{attacker.key} lunges into combat against {defender.key}!|n",
            exclude=[attacker, defender]
        )

    # Execute round 1 immediately
    combat_round_tick(attacker, defender)


def combat_round_tick(attacker, defender):
    """
    Executes a single combat round tick:
    1. Validates combat conditions (both present, alive, not ghosts, still targeting each other).
    2. Attacker strikes Defender.
    3. If Defender survives, Defender counter-attacks Attacker.
    4. Automatically schedules next round in 2.4 seconds.
    """
    from evennia.utils.utils import delay

    # 1. State Validation
    if not attacker or not defender:
        disengage_combat(attacker, defender)
        return

    # Database check (ensure neither was deleted from memory)
    if not getattr(attacker, "pk", None) or not getattr(defender, "pk", None):
        disengage_combat(attacker, defender)
        return

    # Location check (must be in the exact same room)
    if not attacker.location or not defender.location or attacker.location != defender.location:
        disengage_combat(attacker, defender)
        return

    # Ghost / Life check
    if getattr(attacker.db, "is_ghost", False) or getattr(defender.db, "is_ghost", False):
        disengage_combat(attacker, defender)
        return

    if (getattr(attacker.db, "hp", 0) or 0) <= 0 or (getattr(defender.db, "hp", 0) or 0) <= 0:
        disengage_combat(attacker, defender)
        return

    # Target alignment check (player may have switched target or disengaged)
    if getattr(attacker.ndb, "combat_target", None) != defender:
        return

    # 2. Phase 1: Attacker strikes Defender
    perform_combat_round(attacker, defender)

    # Check if Defender died from the blow
    if not getattr(defender, "pk", None) or (getattr(defender.db, "hp", 0) or 0) <= 0 or getattr(defender.db, "is_ghost", False):
        disengage_combat(attacker, defender)
        return

    # Check Defender Wimpy threshold (auto-flee if low on health)
    def_wimpy = getattr(defender.db, "wimpy", 0) or 0
    if def_wimpy > 0:
        def_max = getattr(defender.db, "max_hp", 100) or 100
        def_pct = int(((getattr(defender.db, "hp", 0) or 0) / max(1, def_max)) * 100)
        if def_pct <= def_wimpy:
            defender.msg(f"\n|y*** WIMPY TRIGGERED! *** Your health has fallen to {def_pct}% (below your {def_wimpy}% threshold)! Fleeing!|n")
            disengage_combat(defender, attacker)
            exits = defender.location.exits if defender.location else []
            if exits:
                import random
                flee_exit = random.choice(exits)
                flee_exit.at_traverse(defender, flee_exit.destination)
            return

    # 3. Phase 2: Defender counter-attacks Attacker
    if getattr(defender.ndb, "combat_target", None) == attacker:
        perform_combat_round(defender, attacker)

    # Check if Attacker died from the counter-attack
    if not getattr(attacker, "pk", None) or (getattr(attacker.db, "hp", 0) or 0) <= 0 or getattr(attacker.db, "is_ghost", False):
        disengage_combat(attacker, defender)
        return

    # Check Attacker Wimpy threshold (auto-flee if low on health)
    att_wimpy = getattr(attacker.db, "wimpy", 0) or 0
    if att_wimpy > 0:
        att_max = getattr(attacker.db, "max_hp", 100) or 100
        att_pct = int(((getattr(attacker.db, "hp", 0) or 0) / max(1, att_max)) * 100)
        if att_pct <= att_wimpy:
            attacker.msg(f"\n|y*** WIMPY TRIGGERED! *** Your health has fallen to {att_pct}% (below your {att_wimpy}% threshold)! Fleeing!|n")
            disengage_combat(attacker, defender)
            exits = attacker.location.exits if attacker.location else []
            if exits:
                import random
                flee_exit = random.choice(exits)
                flee_exit.at_traverse(attacker, flee_exit.destination)
            return

    # 4. Schedule next auto-combat round in 2.4 seconds
    if getattr(attacker.ndb, "combat_target", None) == defender and attacker.location == defender.location:
        delay(2.4, combat_round_tick, attacker, defender)


def rest_tick(caller):
    """
    Periodic recovery tick for resting characters.
    Restores HP, Mana, and Stamina every 3.0 seconds until full or interrupted.
    """
    from evennia.utils.utils import delay

    if not caller or not getattr(caller, "pk", None) or not getattr(caller.db, "is_resting", False):
        return

    # Check if combat started or character is dead/ghost
    if getattr(caller.ndb, "combat_target", None) or getattr(caller.db, "is_ghost", False):
        caller.db.is_resting = False
        return

    max_hp = getattr(caller.db, "max_hp", 100) or 100
    max_mana = getattr(caller.db, "max_mana", 50) or 50
    max_stm = getattr(caller.db, "max_stamina", 80) or 80

    cur_hp = getattr(caller.db, "hp", 50) or 50
    cur_mana = getattr(caller.db, "mana", 20) or 20
    cur_stm = getattr(caller.db, "stamina", 40) or 40

    is_full = (cur_hp >= max_hp and cur_mana >= max_mana and cur_stm >= max_stm)
    if is_full:
        caller.db.is_resting = False
        caller.msg("|g*** Fully Recovered! *** Your body and spirit are completely rejuvenated! You stand up.|n")
        if caller.location:
            caller.location.msg_contents(f"{caller.key} stands up, looking fully refreshed.", exclude=[caller])
        return

    # Recovery increments per 3s tick
    heal_hp = 14
    heal_mana = 10
    heal_stm = 18

    caller.db.hp = min(max_hp, cur_hp + heal_hp)
    caller.db.mana = min(max_mana, cur_mana + heal_mana)
    caller.db.stamina = min(max_stm, cur_stm + heal_stm)

    # Heal damaged limbs as well
    if caller.db.limbs:
        for l_data in caller.db.limbs.values():
            l_data["hp"] = min(l_data.get("max_hp", 30), l_data.get("hp", 30) + 7)

    caller.msg(f"|w[Resting... HP: |g{caller.db.hp}/{max_hp}|w (+{heal_hp}) | Mana: |c{caller.db.mana}/{max_mana}|w (+{heal_mana}) | Stm: |y{caller.db.stamina}/{max_stm}|w (+{heal_stm})]|n")

    # Schedule next recovery tick in 3 seconds
    delay(3.0, rest_tick, caller)


# =============================================================================
# 8. SENSORY & EXPLORATION TABLES (LISTEN, SMELL, SEARCH)
# =============================================================================

AMBIENT_SENSORY = {
    "sounds": {
        "city": "The muffled clamor of merchants, distant wagon wheels clattering across cobblestones, and the murmur of urban folk.",
        "forest": "Rustling leaves whispering in the canopy, distant bird calls, and the occasional snap of twigs in the underbrush.",
        "dungeon": "Dripping water echoing in the gloom, an icy subterranean draft, and the faint scuttle of claws across cold stone.",
        "mountain": "The howling whistle of thin alpine winds and the distant clatter of tumbling scree.",
        "coast": "The rhythmic, crashing roar of ocean breakers and the wheeling cries of salt gulls overhead.",
        "underdark": "A heavy, reverberating silence broken by the faint crackle of bioluminescent fungal colonies.",
        "astral": "A faint celestial hum vibrating through the zero-gravity void like glass chimes.",
        "planar": "Unearthly planar resonance humming softly against the edges of physical space."
    },
    "scents": {
        "city": "The aroma of woodsmoke, roasting meats from nearby taverns, baked bread, and damp cobblestones.",
        "forest": "Rich loamy soil, crushed pine needles, wild honeysuckle, and fresh rainwater moss.",
        "dungeon": "Ancient stale dust, cold granite, damp rot, and a faint hint of rusted iron.",
        "mountain": "Crisp, biting alpine frost and clean mineral air.",
        "coast": "Sharp brine, iodine, damp kelp, and ocean salt spray.",
        "underdark": "Damp earth, earthy mushroom spores, and pungent sulfur.",
        "astral": "The sterile, metallic tang of starlight and ozone.",
        "planar": "A strange aroma of burnt ozone, melted silver, and sanctified incense."
    }
}


# =============================================================================
# 9. ADVENTURING PARTY SYSTEM & SHARED XP
# =============================================================================

# In-memory registry: {party_name_lower: {"name": str, "leader_id": int, "members": [int, ...], "invited": [int, ...]}}
PARTIES = {}


def get_party(char):
    """Returns the active party dictionary for the character, if enrolled in one."""
    party_name = getattr(char.db, "party", None)
    if not party_name:
        return None
    return PARTIES.get(party_name.lower())


def create_party(leader, party_name):
    """Creates a new adventuring party led by leader."""
    key = party_name.strip().lower()
    if not key:
        return False, "Party name cannot be empty."
    if key in PARTIES:
        return False, f"A party named '{party_name}' already exists."
    if get_party(leader):
        return False, "You are already in a party! Leave your current party first."

    PARTIES[key] = {
        "name": party_name.strip(),
        "leader_id": leader.id,
        "members": [leader.id],
        "invited": []
    }
    leader.db.party = party_name.strip()
    return True, f"Party '{party_name.strip()}' has been founded with you as party leader!"


def invite_to_party(leader, target):
    """Invites a player to join leader's party."""
    party = get_party(leader)
    if not party:
        return False, "You are not in a party. Form one first with: party form <name>"
    if party["leader_id"] != leader.id:
        return False, "Only the party leader can invite new members."
    if target.id in party["members"]:
        return False, f"{target.key} is already in your party."
    if get_party(target):
        return False, f"{target.key} is already in another party."

    if target.id not in party["invited"]:
        party["invited"].append(target.id)
    return True, f"You have invited {target.key} to join {party['name']}."


def join_party(char, party_name):
    """Joins an existing party if invited."""
    key = party_name.strip().lower()
    party = PARTIES.get(key)
    if not party:
        return False, f"No party named '{party_name}' found."
    if char.id not in party["invited"] and party["leader_id"] != char.id:
        return False, f"You have not been invited to join {party['name']}."
    if get_party(char):
        return False, "You are already in a party. Leave your current party first."

    if char.id in party["invited"]:
        party["invited"].remove(char.id)
    party["members"].append(char.id)
    char.db.party = party["name"]
    msg_party(party["name"], f"|g{char.key} has joined the party!|n")
    return True, f"You have joined {party['name']}!"


def leave_party(char):
    """Leaves the current party."""
    party = get_party(char)
    if not party:
        return False, "You are not in a party."

    party_name = party["name"]
    if char.id in party["members"]:
        party["members"].remove(char.id)
    char.db.party = None

    if party["leader_id"] == char.id:
        if party["members"]:
            from evennia.objects.models import ObjectDB
            new_leader_id = party["members"][0]
            party["leader_id"] = new_leader_id
            new_leader = ObjectDB.objects.filter(id=new_leader_id).first()
            if new_leader:
                new_leader.msg(f"|y{char.key} has left. You are now the leader of {party_name}!|n")
            msg_party(party_name, f"|y{char.key} has left the party. New leader is {new_leader.key if new_leader else 'Unknown'}.|n")
        else:
            PARTIES.pop(party_name.lower(), None)
            return True, f"You left and dissolved {party_name}."
    else:
        msg_party(party_name, f"|y{char.key} has left the party.|n")
    return True, f"You have left {party_name}."


def disband_party(leader):
    """Disbands the party (leader only)."""
    party = get_party(leader)
    if not party:
        return False, "You are not in a party."
    if party["leader_id"] != leader.id:
        return False, "Only the party leader can disband the party."

    from evennia.objects.models import ObjectDB
    for m_id in party["members"]:
        m = ObjectDB.objects.filter(id=m_id).first()
        if m:
            m.db.party = None
            m.msg(f"|rParty {party['name']} has been disbanded by {leader.key}.|n")

    PARTIES.pop(party["name"].lower(), None)
    return True, f"You have disbanded {party['name']}."


def msg_party(party_name, message, exclude=None):
    """Sends a message to all online party members."""
    party = PARTIES.get(party_name.lower())
    if not party:
        return
    from evennia.objects.models import ObjectDB
    for m_id in party["members"]:
        if exclude and m_id in exclude:
            continue
        m = ObjectDB.objects.filter(id=m_id).first()
        if m and hasattr(m, "msg"):
            m.msg(message)


def distribute_party_xp(killer, total_xp):
    """
    Shares XP among party members in the same room, with a 10% teamwork bonus!
    """
    party = get_party(killer)
    if not party:
        killer.db.xp = (getattr(killer.db, "xp", 0) or 0) + total_xp
        killer.msg(f"|gYou gain {total_xp} Experience Points! (Total: {killer.db.xp})|n")
        return

    from evennia.objects.models import ObjectDB
    present_members = []
    for m_id in party["members"]:
        m = ObjectDB.objects.filter(id=m_id).first()
        if m and m.location == killer.location:
            present_members.append(m)

    if not present_members:
        present_members = [killer]

    bonus_xp = int(total_xp * (1.0 + (0.10 * (len(present_members) - 1))))
    share = max(1, bonus_xp // len(present_members))

    for m in present_members:
        m_xp = share
        if getattr(m.db, "race", "") == "Human":
            m_xp = int(m_xp * 1.15)
        m.db.xp = (getattr(m.db, "xp", 0) or 0) + m_xp
        m.msg(f"|g[Party Share] You gain {m_xp} Experience Points! (Total: {m.db.xp})|n")



