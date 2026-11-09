"""
Nightmare LPmud Command Suite for Evennia
Implements commands for:
1. Limbs, Equipment & Score
2. Guilds, Classes & Skills
3. Death, Ghost & Corpse Looting
4. Lighting & Perception
5. Banking & Vaults
6. Tactical Combat, Spells & Abilities
7. Races & Racial Traits
"""

import random
from evennia import default_cmds
from evennia.utils.create import create_object
from typeclasses.objects import Object
from world.nightmare_core import (
    init_nightmare_character, GUILDS, RACES, EQUIPMENT_SLOTS,
    PRESTIGE_SUBCLASSES, SPELLS, trigger_skill_tick,
    perform_combat_round, resurrect_player, room_is_illuminated,
    handle_player_death, start_combat, disengage_combat, is_in_combat,
    rest_tick, AMBIENT_SENSORY, PARTIES, get_party, create_party,
    invite_to_party, join_party, leave_party, disband_party, msg_party,
    distribute_party_xp
)


# =============================================================================
# 1. SCORE, LIMBS & EQUIPMENT COMMANDS
# =============================================================================

class CmdScore(default_cmds.MuxCommand):
    """
    View your character score sheet, vitals, and stats

    Usage:
      score
      sc
    """

    key = "score"
    aliases = ["sc"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        coins = caller.db.coins or {"copper": 0, "silver": 0, "gold": 0}
        b_coins = caller.db.bank_coins or {"copper": 0, "silver": 0, "gold": 0}

        status = "|r[GHOST]|n" if caller.db.is_ghost else "|g[ALIVE]|n"

        text = f"""
|w========================= NIGHTMARE STATUS =========================|n
Name: |c{caller.key}|n {status}    Race: |y{caller.db.race}|n    Guild: |m{caller.db.guild}|n
Level: |w{caller.db.level}|n    Experience: |g{caller.db.xp}|n XP

|wVitals:|n
  HP:      |g{caller.db.hp}/{caller.db.max_hp}|n
  Mana:    |c{caller.db.mana}/{caller.db.max_mana}|n
  Stamina: |y{caller.db.stamina}/{caller.db.max_stamina}|n

|wAttributes:|n
  Strength:     |w{caller.db.str:<3}|n   Intelligence: |w{caller.db.int:<3}|n
  Dexterity:    |w{caller.db.dex:<3}|n   Wisdom:       |w{caller.db.wis:<3}|n
  Constitution: |w{caller.db.con:<3}|n   Charisma:     |w{caller.db.cha:<3}|n

|wWealth (On Hand):|n
  |y{coins.get('gold', 0)} Gold|n  |w{coins.get('silver', 0)} Silver|n  |r{coins.get('copper', 0)} Copper|n
|wWealth (Banked):|n
  |y{b_coins.get('gold', 0)} Gold|n  |w{b_coins.get('silver', 0)} Silver|n  |r{b_coins.get('copper', 0)} Copper|n
|w===================================================================|n
"""
        caller.msg(text.strip())


class CmdLimbs(default_cmds.MuxCommand):
    """
    Inspect the health condition of your individual limbs

    Usage:
      limbs
    """

    key = "limbs"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        limbs = caller.db.limbs or {}
        caller.msg(f"\n|w=== {caller.key}'s Body Condition ===|n")
        for limb_name, data in limbs.items():
            hp = data.get("hp", 0)
            max_hp = data.get("max_hp", 1)
            pct = int((hp / max_hp) * 100)

            if pct > 75:
                color = "|g"
                desc = "Healthy"
            elif pct > 40:
                color = "|y"
                desc = "Battered"
            elif pct > 0:
                color = "|r"
                desc = "Crippled"
            else:
                color = "|R"
                desc = "SEVERED/USELESS"

            caller.msg(f"  {limb_name.title():<12}: {color}{hp}/{max_hp} ({pct}%) [{desc}]|n")
        caller.msg("|w====================================|n\n")


class CmdEquipment(default_cmds.MuxCommand):
    """
    View currently equipped weapons and armor

    Usage:
      equipment
      eq
    """

    key = "equipment"
    aliases = ["eq"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        slots = caller.db.slots or {}
        caller.msg(f"\n|w=== {caller.key}'s Equipped Gear ===|n")
        for slot in EQUIPMENT_SLOTS:
            item = slots.get(slot)
            item_name = item.key if (item and item in caller.contents) else "|x<empty>|n"
            caller.msg(f"  {slot.replace('_', ' ').title():<12}: {item_name}")
        caller.msg("|w=================================|n\n")


class CmdWield(default_cmds.MuxCommand):
    """
    Wield a weapon in your main hand or off hand

    Usage:
      wield <weapon>
      wield <weapon> in off hand
    """

    key = "wield"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if caller.db.is_ghost:
            caller.msg("Ghosts have no physical hands to wield weapons!")
            return

        if not self.args:
            caller.msg("What do you want to wield?")
            return

        args = self.args.lower()
        target_slot = "off_hand" if "off" in args else "main_hand"
        clean_name = args.replace("in off hand", "").replace("in off", "").strip()

        item = caller.search(clean_name, location=caller)
        if not item:
            return

        slots = caller.db.slots
        slots[target_slot] = item

        slot_name = target_slot.replace("_", " ")
        caller.msg(f"|yYou wield {item.key} in your {slot_name}.|n")
        caller.location.msg_contents(f"{caller.key} wields {item.key}.", exclude=[caller])


class CmdWear(default_cmds.MuxCommand):
    """
    Wear a piece of armor on your body

    Usage:
      wear <item>
      wear <item> on <slot>
    """

    key = "wear"
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if caller.db.is_ghost:
            caller.msg("Armor slips right through your ghostly form!")
            return

        if not self.args:
            caller.msg("What do you want to wear?")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        key = item.key.lower()
        slot = "torso"
        if any(w in key for w in ["helm", "crown", "cap", "hat", "goggles"]):
            slot = "head"
        elif any(w in key for w in ["ring", "band"]):
            slot = "ring"
        elif any(w in key for w in ["amulet", "talisman", "rosary", "beads", "crest"]):
            slot = "amulet"
        elif any(w in key for w in ["boots", "shoes"]):
            slot = "feet"
        elif any(w in key for w in ["greaves", "leggings"]):
            slot = "legs"
        elif any(w in key for w in ["shield", "buckler"]):
            slot = "off_hand"

        caller.db.slots[slot] = item
        caller.msg(f"|gYou wear {item.key} on your {slot}.|n")
        caller.location.msg_contents(f"{caller.key} wears {item.key}.", exclude=[caller])


class CmdRemove(default_cmds.MuxCommand):
    """
    Remove or unwield a piece of equipment

    Usage:
      remove <item>
      unwield <item>
    """

    key = "remove"
    aliases = ["unwield", "take off"]
    locks = "cmd:all()"
    help_category = "Equipment"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("What do you want to remove?")
            return

        slots = caller.db.slots
        target_name = self.args.strip().lower()

        found_slot = None
        for slot, item in slots.items():
            if item and target_name in item.key.lower():
                found_slot = slot
                break

        if not found_slot:
            caller.msg(f"You do not have {self.args.strip()} equipped.")
            return

        removed_item = slots[found_slot]
        slots[found_slot] = None
        caller.msg(f"You remove {removed_item.key} from your {found_slot.replace('_', ' ')}.")


# =============================================================================
# 2. GUILDS & SKILLS COMMANDS
# =============================================================================

class CmdGuilds(default_cmds.MuxCommand):
    """
    List all adventurer guilds and their Guildmasters

    Usage:
      guilds
    """

    key = "guilds"
    locks = "cmd:all()"
    help_category = "Guilds"

    def func(self):
        caller = self.caller
        caller.msg("\n|w=== Guilds of Eldoria ===|n")
        for g_name, g_data in GUILDS.items():
            caller.msg(f"|c{g_name:<8}|n: {g_data['desc']}")
            caller.msg(f"          Guildmaster: |y{g_data['leader']}|n ({g_data['location']})\n")
        caller.msg("|w===========================|n\n")


class CmdJoinGuild(default_cmds.MuxCommand):
    """
    Join an adventurer guild at their guildmaster's location

    Usage:
      join <guild>
    """

    key = "join"
    locks = "cmd:all()"
    help_category = "Guilds"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Which guild do you want to join? Type: guilds")
            return

        target_guild = self.args.strip().title()
        if target_guild not in GUILDS:
            caller.msg(f"Unknown guild: {target_guild}. Available: {', '.join(GUILDS.keys())}")
            return

        caller.db.guild = target_guild
        from world.languages import get_innate_languages
        new_langs = get_innate_languages(caller.db.race or "Human", target_guild)
        curr_langs = caller.db.languages or {}
        for l_k, l_v in new_langs.items():
            curr_langs[l_k] = max(curr_langs.get(l_k, 0), l_v)
        caller.db.languages = curr_langs

        caller.msg(f"\n|g*** CONGRATULATIONS! ***|n\nYou have joined the |c{target_guild} Guild|n!")
        caller.location.msg_contents(f"{caller.key} has sworn allegiance to the {target_guild} Guild!", exclude=[caller])


class CmdSkills(default_cmds.MuxCommand):
    """
    View your current skill proficiencies

    Usage:
      skills
    """

    key = "skills"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        skills = caller.db.skills or {}
        caller.msg(f"\n|w=== {caller.key}'s Skills (XP Available: {caller.db.xp}) ===|n")
        for sk_name, val in skills.items():
            bar = "=" * (val // 10) + "-" * (10 - (val // 10))
            caller.msg(f"  {sk_name.title():<15}: |c{val:>3}%|n [{bar}]")
        caller.msg("|w================================================|n\n")


class CmdTrain(default_cmds.MuxCommand):
    """
    Train a skill using earned experience points

    Usage:
      train <skill>
    """

    key = "train"
    locks = "cmd:all()"
    help_category = "Skills"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Which skill do you want to train? Type: skills")
            return

        sk_target = self.args.strip().lower()

        # Check if training a language
        from world.languages import LANGUAGES
        matched_lang = None
        for l_key, l_data in LANGUAGES.items():
            if sk_target == l_key or sk_target in l_data["name"].lower():
                matched_lang = l_key
                break

        if matched_lang:
            langs = caller.db.languages or {}
            curr_val = langs.get(matched_lang, 0)
            if curr_val >= 100:
                caller.msg(f"You are already completely fluent in {LANGUAGES[matched_lang]['name']} (100%)!")
                return
            cost = max(50, curr_val * 6)
            if (caller.db.xp or 0) < cost:
                caller.msg(f"Studying {LANGUAGES[matched_lang]['name']} requires {cost} XP! (You have: {caller.db.xp} XP)")
                return
            caller.db.xp -= cost
            langs[matched_lang] = min(100, curr_val + 10)
            caller.db.languages = langs
            caller.msg(f"|gYou study ancient grammar and phonetics! Your fluency in {LANGUAGES[matched_lang]['name']} rises to {langs[matched_lang]}%! ({cost} XP spent)|n")
            return

        skills = caller.db.skills

        matched_skill = next((sk for sk in skills.keys() if sk_target in sk), None)
        if not matched_skill:
            caller.msg(f"Unknown skill '{sk_target}'. Check your skills list.")
            return

        curr_val = skills[matched_skill]
        if curr_val >= 100:
            caller.msg(f"You have already mastered {matched_skill.title()} (100%)!")
            return

        cost = curr_val * 5
        if (caller.db.xp or 0) < cost:
            caller.msg(f"Training {matched_skill.title()} requires {cost} XP! (You have: {caller.db.xp} XP)")
            return

        caller.db.xp -= cost
        skills[matched_skill] += 5
        caller.msg(f"|gYou train rigorously in {matched_skill.title()}! Your skill rises to {skills[matched_skill]}%! ({cost} XP spent)|n")


# =============================================================================
# 3. DEATH, RESURRECTION & GHOST COMMANDS
# =============================================================================

class CmdResurrect(default_cmds.MuxCommand):
    """
    Return to the world of the living at a holy shrine or cathedral

    Usage:
      resurrect
    """

    key = "resurrect"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        loc = caller.location
        is_holy = "cathedral" in loc.key.lower() or "altar" in loc.key.lower() or "temple" in loc.key.lower()

        if not is_holy:
            caller.msg("You can only be resurrected before the holy altar in the Cathedral of Light!")
            return

        ok, msg = resurrect_player(caller)
        if not ok:
            caller.msg(msg)


class CmdLootCorpse(default_cmds.MuxCommand):
    """
    Loot your belongings from your fallen corpse

    Usage:
      loot corpse
    """

    key = "loot"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to loot?")
            return

        corpse = caller.search(self.args.strip(), location=caller.location)
        if not corpse:
            return

        items = list(corpse.contents)
        if not items:
            caller.msg(f"{corpse.key} is completely empty.")
            return

        for item in items:
            item.move_to(caller, quiet=True)

        caller.msg(f"|gYou reclaim all {len(items)} items from {corpse.key}!|n")
        caller.location.msg_contents(f"{caller.key} loots {corpse.key}.", exclude=[caller])


# =============================================================================
# 5. BANKING & VAULT COMMANDS
# =============================================================================

class CmdBalance(default_cmds.MuxCommand):
    """
    Check your wallet and bank account balances

    Usage:
      balance
    """

    key = "balance"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        c = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
        b = caller.db.bank_coins or {"gold": 0, "silver": 0, "copper": 0}

        text = f"""
|w=== Eldoria Financial Summary ===|n
  Wallet: |y{c.get('gold', 0)} Gold|n, |w{c.get('silver', 0)} Silver|n, |r{c.get('copper', 0)} Copper|n
  Bank:   |y{b.get('gold', 0)} Gold|n, |w{b.get('silver', 0)} Silver|n, |r{b.get('copper', 0)} Copper|n
|w==================================|n
"""
        caller.msg(text.strip())


class CmdDeposit(default_cmds.MuxCommand):
    """
    Deposit coins into your bank account

    Usage:
      deposit <amount> [currency]
      Example: deposit 50 gold
    """

    key = "deposit"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if "bank" not in caller.location.key.lower() and "vault" not in caller.location.key.lower():
            caller.msg("You can only deposit coins at the Royal Bank of Eldoria!")
            return

        if not self.args:
            caller.msg("Usage: deposit <amount> [gold/silver/copper]")
            return

        parts = self.args.strip().split()
        try:
            amt = int(parts[0])
        except ValueError:
            caller.msg("Amount must be a positive number.")
            return

        curr = parts[1].lower() if len(parts) > 1 else "gold"
        if curr not in ["gold", "silver", "copper"]:
            curr = "gold"

        c = caller.db.coins
        b = caller.db.bank_coins

        if c.get(curr, 0) < amt:
            caller.msg(f"You do not have {amt} {curr} on hand! (You have: {c.get(curr, 0)})")
            return

        c[curr] -= amt
        b[curr] = b.get(curr, 0) + amt
        caller.msg(f"|yYou deposit {amt} {curr} into your bank vault.|n Bank total: {b[curr]} {curr}.")


class CmdWithdraw(default_cmds.MuxCommand):
    """
    Withdraw coins from your bank account

    Usage:
      withdraw <amount> [currency]
      Example: withdraw 25 gold
    """

    key = "withdraw"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if "bank" not in caller.location.key.lower() and "vault" not in caller.location.key.lower():
            caller.msg("You can only withdraw coins at the Royal Bank of Eldoria!")
            return

        if not self.args:
            caller.msg("Usage: withdraw <amount> [gold/silver/copper]")
            return

        parts = self.args.strip().split()
        try:
            amt = int(parts[0])
        except ValueError:
            caller.msg("Amount must be a positive number.")
            return

        curr = parts[1].lower() if len(parts) > 1 else "gold"
        if curr not in ["gold", "silver", "copper"]:
            curr = "gold"

        c = caller.db.coins
        b = caller.db.bank_coins

        if b.get(curr, 0) < amt:
            caller.msg(f"You do not have {amt} {curr} in your bank account! (Bank has: {b.get(curr, 0)})")
            return

        b[curr] -= amt
        c[curr] = c.get(curr, 0) + amt
        caller.msg(f"|yYou withdraw {amt} {curr} from your account.|n Wallet: {c[curr]} {curr}.")


class CmdVault(default_cmds.MuxCommand):
    """
    Store or retrieve items in your private bank safety deposit locker

    Usage:
      vault store <item>
      vault retrieve <item>
      vault list
    """

    key = "vault"
    locks = "cmd:all()"
    help_category = "Economy"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if "bank" not in caller.location.key.lower() and "vault" not in caller.location.key.lower():
            caller.msg("You must be at the Royal Bank & Vault to access safety lockers!")
            return

        if not self.args:
            caller.msg("Usage: vault store <item> | vault retrieve <item> | vault list")
            return

        cmd = self.args.strip().split()[0].lower()
        rest = " ".join(self.args.strip().split()[1:])

        vault = caller.db.bank_vault or []

        if cmd == "list":
            if not vault:
                caller.msg("Your safety deposit vault is currently empty.")
            else:
                caller.msg(f"\n|w=== Your Bank Vault Items ({len(vault)}) ===|n")
                for itm in vault:
                    caller.msg(f"  - {itm.key}")
                caller.msg("|w========================================|n\n")

        elif cmd == "store":
            item = caller.search(rest, location=caller)
            if not item:
                return

            item.move_to(None, quiet=True)  # Store in limbo/vault
            vault.append(item)
            caller.db.bank_vault = vault
            caller.msg(f"|yYou place {item.key} into your locked bank vault locker.|n")

        elif cmd in ["retrieve", "get"]:
            target_name = rest.lower()
            found = next((i for i in vault if target_name in i.key.lower()), None)
            if not found:
                caller.msg(f"Item '{rest}' not found in your bank vault.")
                return

            vault.remove(found)
            caller.db.bank_vault = vault
            found.move_to(caller, quiet=True)
            caller.msg(f"|gYou retrieve {found.key} from your bank vault locker.|n")


# =============================================================================
# 6. TACTICAL COMBAT COMMANDS
# =============================================================================

class CmdKill(default_cmds.MuxCommand):
    """
    Engage a target in combat. Real-time auto-combat rounds will continue
    automatically every 2.4 seconds until a combatant dies, flees, or disengages.

    Usage:
      kill <target>
      attack <target>
    """

    key = "kill"
    aliases = ["attack"]
    priority = 10
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Who do you want to attack?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        if target == caller:
            caller.msg("You cannot attack yourself!")
            return

        init_nightmare_character(target)
        start_combat(caller, target)


class CmdDisengage(default_cmds.MuxCommand):
    """
    Disengage from active combat.

    Usage:
      disengage
      stop
    """
    key = "disengage"
    aliases = ["stop"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        target = getattr(caller.ndb, "combat_target", None)
        if not target:
            caller.msg("You are not currently fighting anyone.")
            return

        disengage_combat(caller, target)
        caller.msg(f"|yYou lower your weapon and disengage from combat with {target.key}.|n")
        if hasattr(target, "msg"):
            target.msg(f"|y{caller.key} backs away and lowers their weapon. Combat ceases.|n")
        if caller.location:
            caller.location.msg_contents(
                f"|y{caller.key} disengages from combat with {target.key}.|n",
                exclude=[caller, target]
            )


class CmdBash(default_cmds.MuxCommand):
    """
    Slam your shield or shoulder into the opponent to stun them

    Usage:
      bash <target>
    """

    key = "bash"
    priority = 10
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Who do you want to bash?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        if (caller.db.stamina or 0) < 15:
            caller.msg("You are too exhausted to perform a shield bash!")
            return

        caller.db.stamina -= 15
        init_nightmare_character(target)

        dmg = random.randint(15, 28) + (caller.db.str // 2)
        target.db.hp = max(0, (target.db.hp or 50) - dmg)

        caller.msg(f"|YYou lower your shoulder and BASH into {target.key} for {dmg} bludgeoning damage!|n")
        target.msg(f"|R{caller.key} BASHEES into you, knocking the wind from your lungs for {dmg} damage!|n")
        caller.location.msg_contents(f"{caller.key} executes a powerful bash against {target.key}!", exclude=[caller, target])


class CmdBackstab(default_cmds.MuxCommand):
    """
    Stealthily backstab an opponent from behind for massive critical damage

    Usage:
      backstab <target>
    """

    key = "backstab"
    aliases = ["stab"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Who do you want to backstab?")
            return

        target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        init_nightmare_character(target)
        dmg = random.randint(35, 60) + (caller.db.dex * 2)
        target.db.hp = max(0, (target.db.hp or 50) - dmg)

        caller.msg(f"|R*** CRITICAL STRIKE! *** You slip behind {target.key} and drive your blade into their back for {dmg} damage!|n")
        target.msg(f"|R{caller.key} plunges a blade into your back for {dmg} critical damage!|n")
        caller.location.msg_contents(f"{caller.key} ambushes {target.key} with a lethal backstab!", exclude=[caller, target])


class CmdSpellbook(default_cmds.MuxCommand):
    """
    Inspect your arcane spellbook and studied incantations

    Usage:
      spellbook
      spells
      spellbook <spell>
    """
    key = "spellbook"
    aliases = ["spells"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        spellbook = caller.db.spellbook or []

        if not self.args:
            caller.msg("\n|w============================= ARCANE SPELLBOOK =============================|n")
            caller.msg(f"{'Spell Name':<16} {'School':<14} {'Mana':<6} {'Reagent':<12} {'Chant (High Arcane)':<22}")
            caller.msg("-" * 75)
            for s_key, s_data in SPELLS.items():
                learned = s_key in spellbook
                name_col = f"|g{s_data['name']:<16}|n" if learned else f"|x{s_data['name']:<16} [Unlearned]|n"
                reagent = s_data['reagent'].title() if s_data['reagent'] else "None"
                caller.msg(f"{name_col} {s_data['school']:<14} {s_data['mana']:<6} {reagent:<12} |c{s_data['chant']:<22}|n")
            caller.msg("|w=============================================================================|n")
            caller.msg("To inspect a specific spell, type: |wspellbook <spell>|n\n")
            return

        query = self.args.strip().lower()
        matched_key = None
        for s_key, s_data in SPELLS.items():
            if query in s_key or query in s_data["name"].lower():
                matched_key = s_key
                break

        if not matched_key:
            caller.msg(f"Spell '{query}' not found in the grand arcane archives.")
            return

        s = SPELLS[matched_key]
        status = "|gLearned|n" if matched_key in spellbook else "|rNot Learned (Requires study)|n"
        reagent = s['reagent'].title() if s['reagent'] else "None required"
        caller.msg(f"\n|c=== Spell: {s['name']} ===|n")
        caller.msg(f"Status:      {status}")
        caller.msg(f"School:      |m{s['school']}|n")
        caller.msg(f"Mana Cost:   |c{s['mana']} Mana|n")
        caller.msg(f"Incantation: |C\"{s['chant']}\"|n")
        caller.msg(f"Reagent:     |y{reagent}|n")
        caller.msg(f"Skill:       |w{s['skill'].title()}|n")
        caller.msg(f"Description: {s['desc']}\n")


class CmdStudy(default_cmds.MuxCommand):
    """
    Study an arcane scroll to scribe its formula into your spellbook

    Usage:
      study <scroll>
      scribe <scroll>
    """
    key = "study"
    aliases = ["scribe"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("Which scroll do you want to study? (e.g. study scroll of fireball)")
            return

        scroll = caller.search(self.args.strip(), location=caller)
        if not scroll:
            return

        spell_key = getattr(scroll.db, "spell", None)
        if not spell_key:
            for k in SPELLS.keys():
                if k in scroll.key.lower():
                    spell_key = k
                    break

        if not spell_key or spell_key not in SPELLS:
            caller.msg(f"You examine {scroll.key}, but it does not contain an arcane formula you can scribe.")
            return

        spell_data = SPELLS[spell_key]
        spellbook = caller.db.spellbook or []
        if spell_key in spellbook:
            caller.msg(f"You already have {spell_data['name']} inscribed in your spellbook!")
            return

        spellbook.append(spell_key)
        caller.db.spellbook = spellbook
        trigger_skill_tick(caller, "magic attack", 30)

        caller.msg(
            f"\n|gYou carefully unfurl {scroll.key} and trace the glowing silver runes...|n\n"
            f"|YThe parchment dissolves into sparkling golden motes as the incantation sears into your memory!|n\n"
            f"|cYou have learned the spell: |w{spell_data['name']}|c!|n\n"
            f"Incantation Chant: |C\"{spell_data['chant']}\"|n\n"
        )
        caller.location.msg_contents(
            f"{caller.key} studies an arcane scroll; it turns to radiant dust as magical energy washes over them!",
            exclude=[caller]
        )
        scroll.delete()


class CmdCast(default_cmds.MuxCommand):
    """
    Cast a magical spell from your spellbook

    Usage:
      cast <spell> [at <target>]
    """
    key = "cast"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if getattr(caller.db, "is_ghost", False):
            caller.msg("You are a ghost! You cannot channel magical forces!")
            return

        if not self.args:
            caller.msg("Usage: cast <spell> [at <target>]\nType |wspellbook|n to see your learned spells.")
            return

        parts = self.args.strip().split()
        spell_name = parts[0].lower()
        target_name = parts[2] if len(parts) > 2 and parts[1].lower() == "at" else (parts[1] if len(parts) > 1 else None)

        matched_key = None
        for s_key in SPELLS.keys():
            if spell_name == s_key or spell_name in s_key:
                matched_key = s_key
                break

        if not matched_key:
            caller.msg(f"Unknown spell '{spell_name}'. Type |wspellbook|n to view your spells.")
            return

        spellbook = caller.db.spellbook or []
        if matched_key not in spellbook:
            caller.msg(f"You have not learned the spell '{spell_name}'! You must find and study its scroll.")
            return

        spell_data = SPELLS[matched_key]

        # Mana check
        mana_cost = spell_data["mana"]
        if (caller.db.mana or 0) < mana_cost:
            caller.msg(f"Not enough mana! (Requires {mana_cost} Mana, you have {caller.db.mana})")
            return

        # Reagent check
        req_reagent = spell_data["reagent"]
        reagent_item = None
        if req_reagent:
            for item in caller.contents:
                if req_reagent in item.key.lower():
                    reagent_item = item
                    break
            if not reagent_item:
                caller.msg(f"|rSpell failed! You lack the required reagent: {req_reagent.title()}!|n")
                return

        # Deduct resources
        caller.db.mana -= mana_cost
        if reagent_item:
            caller.msg(f"|x[You consume {reagent_item.key}]|n")
            reagent_item.delete()

        # Incantation broadcast
        caller.location.msg_contents(
            f"|C{caller.key} raises both hands, incanting High Arcane words: '{spell_data['chant']}'!|n"
        )

        # Spell Effects
        if matched_key == "heal":
            target = caller
            if target_name:
                t = caller.search(target_name, location=caller.location)
                if t:
                    target = t
            init_nightmare_character(target)
            wis_mod = max(1, (caller.db.wis or 10) // 2)
            heal_amt = random.randint(spell_data["min_heal"], spell_data["max_heal"]) + wis_mod
            target.db.hp = min(target.db.max_hp, (target.db.hp or 50) + heal_amt)
            if target.db.limbs:
                for l_data in target.db.limbs.values():
                    l_data["hp"] = min(l_data["max_hp"], l_data["hp"] + (heal_amt // 2))
            target.msg(f"|gA warm celestial light envelops you, healing {heal_amt} HP! ({target.db.hp}/{target.db.max_hp} HP)|n")
            if target != caller:
                caller.msg(f"|gYou heal {target.key} for {heal_amt} HP!|n")
            caller.location.msg_contents(f"|gSoft golden radiance shines upon {target.key}.|n", exclude=[caller, target])
            trigger_skill_tick(caller, "healing", 40)
            return

        if matched_key == "stoneskin":
            caller.db.stoneskin_absorb = (caller.db.stoneskin_absorb or 0) + spell_data["absorb"]
            caller.msg(f"|yYour flesh hardens like solid granite! (+{spell_data['absorb']} Stone Skin absorption)|n")
            caller.location.msg_contents(f"{caller.key}'s skin takes on the dull, impenetrable texture of gray granite.", exclude=[caller])
            trigger_skill_tick(caller, "magic defense", 40)
            return

        if matched_key == "blink":
            exits = caller.location.exits
            if exits:
                dest_exit = random.choice(exits)
                caller.msg(f"|c*** BLINK! *** You fold the fabric of space and reappear at the {dest_exit.key}!|n")
                caller.location.msg_contents(f"|c{caller.key} vanishes in a bright azure flash!|n", exclude=[caller])
                dest_exit.at_traverse(caller, dest_exit.destination)
            else:
                caller.msg("|c*** BLINK! *** You phase through the ether and reposition instantaneously!|n")
            trigger_skill_tick(caller, "magic defense", 40)
            return

        if matched_key == "animate":
            corpse = None
            for obj in caller.location.contents:
                if "corpse" in obj.key.lower():
                    corpse = obj
                    break
            if not corpse:
                caller.msg("There is no fallen corpse here to reanimate!")
                return
            c_name = corpse.key
            corpse.delete()
            thrall = create_object(
                Object,
                key=f"Skeletal Thrall of {caller.key}",
                location=caller.location,
                aliases=["skeletal thrall", "thrall", "skeleton"],
                tags=["eldoria_world", "undead", "pet"]
            )
            thrall.db.desc = f"A clattering skeleton raised by {caller.key}'s dark necromancy. Glowing blue light burns in its hollow eye sockets."
            thrall.db.owner_id = caller.id
            thrall.db.hp = 60
            thrall.db.max_hp = 60
            caller.msg(f"|m*** ANIMATE DEAD *** Flesh dissolves into grave dust as {thrall.key} rises from the remains!|n")
            caller.location.msg_contents(f"|mCold mist swirls as {thrall.key} claws its way up from {c_name}!|n", exclude=[caller])
            trigger_skill_tick(caller, "magic attack", 45)
            return

        # Offensive Spells: require target
        if not target_name:
            caller.msg(f"Who do you want to cast {spell_data['name']} at?")
            return

        target = caller.search(target_name, location=caller.location)
        if not target:
            return

        init_nightmare_character(target)
        stat_val = getattr(caller.db, spell_data["stat"], 10)
        stat_mod = max(1, stat_val // 2)
        base_dmg = random.randint(spell_data["min_dmg"], spell_data["max_dmg"]) + stat_mod

        # Pyromancer Combustion synergy
        if matched_key in ["firebolt", "fireball"] and getattr(caller.db, "combustion_active", False):
            base_dmg = int(base_dmg * 1.5)
            caller.db.combustion_active = False
            caller.msg("|r*** COMBUSTION DETONATION! *** Thermal shockwave multiplies your fire damage by +50%!|n")

        # Inquisitor Smite synergy vs undead
        if matched_key == "smite":
            is_undead = "undead" in target.tags.all() or "skeleton" in target.key.lower() or "ghoul" in target.key.lower() or "spectre" in target.key.lower()
            if is_undead:
                base_dmg *= 2
                caller.msg("|Y*** HOLY SMITE PURGE! *** Radiant light vaporizes the foul undead (+100% damage)!|n")

        dmg = base_dmg
        target.db.hp = max(0, (target.db.hp or 50) - dmg)

        # Limb damage
        if target.db.limbs:
            limb_choice = random.choice(list(target.db.limbs.keys()))
            target.db.limbs[limb_choice]["hp"] = max(0, target.db.limbs[limb_choice]["hp"] - dmg)

        if matched_key in ["firebolt", "fireball"]:
            caller.msg(f"|rYour {spell_data['name']} explodes against {target.key} for {dmg} FIRE damage!|n")
            target.msg(f"|r{caller.key}'s {spell_data['name']} engulfs you in searing fire for {dmg} damage!|n")
            caller.location.msg_contents(f"|rA blast of fire erupts around {target.key}!|n", exclude=[caller, target])
        elif matched_key == "lightning":
            caller.msg(f"|cCrackling lightning leaps from your fingertips and shocks {target.key} for {dmg} LIGHTNING damage!|n")
            target.msg(f"|c{caller.key}'s lightning bolt jolts through your body for {dmg} damage!|n")
            caller.location.msg_contents(f"|cBlue arcs of electricity fork across the room into {target.key}!|n", exclude=[caller, target])
        elif matched_key == "smite":
            caller.msg(f"|YYou smite {target.key} with celestial fury for {dmg} DIVINE damage!|n")
            target.msg(f"|YHoly wrath sears your flesh for {dmg} damage!|n")
            caller.location.msg_contents(f"|YA pillar of celestial sunlight descends upon {target.key}!|n", exclude=[caller, target])

        trigger_skill_tick(caller, spell_data["skill"], 40)

        # Death check
        if target.db.hp <= 0:
            if getattr(target, "has_account", False) or target.db.is_character:
                handle_player_death(target)
                caller.msg(f"|Y*** YOU HAVE SLAIN {target.key.upper()}! ***|n")
            else:
                target.location.msg_contents(f"|r{target.key} collapses dead from arcane destruction!|n")
                corpse = create_object(
                    Object,
                    key=f"Corpse of {target.key}",
                    location=target.location,
                    aliases=["corpse"],
                    tags=["eldoria_world"]
                )
                corpse.db.desc = f"The charred remains of {target.key}."
                target.delete()


class CmdFlee(default_cmds.MuxCommand):
    """
    Attempt to flee from combat in panic

    Usage:
      flee
    """
    key = "flee"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        exits = caller.location.exits
        if not exits:
            caller.msg("There is nowhere to flee to!")
            return

        target = getattr(caller.ndb, "combat_target", None)
        if target:
            disengage_combat(caller, target)
            if hasattr(target, "msg"):
                target.msg(f"|y{caller.key} flees frantically from combat!|n")

        dest_exit = random.choice(exits)
        caller.msg(f"|yIn sheer terror, you scramble frantically toward the {dest_exit.key}!|n")
        dest_exit.at_traverse(caller, dest_exit.destination)


class CmdRest(default_cmds.MuxCommand):
    """
    Sit down and rest to recover Health, Mana, and Stamina.

    Usage:
      rest
      sleep
      stand
      wake

    Resting accelerates natural regeneration over time (+14 HP, +10 Mana, +18 Stamina per tick).
    Moving, standing, or engaging in combat will automatically end your rest.
    """
    key = "rest"
    aliases = ["sleep", "stand", "wake"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if self.cmdstring in ["stand", "wake"] or getattr(caller.db, "is_resting", False):
            caller.db.is_resting = False
            caller.msg("|yYou stand up and stretch, ready for action.|n")
            if caller.location:
                caller.location.msg_contents(f"{caller.key} stands up.", exclude=[caller])
            return

        if getattr(caller.ndb, "combat_target", None):
            caller.msg("|rYou cannot rest while locked in combat!|n")
            return

        if getattr(caller.db, "is_ghost", False):
            caller.msg("Ghosts have no mortal fatigue to rest.")
            return

        caller.db.is_resting = True
        caller.msg("|cYou sit down comfortably to rest. Healing energy begins knitting your wounds.|n")
        if caller.location:
            caller.location.msg_contents(f"{caller.key} sits down and begins to rest.", exclude=[caller])

        rest_tick(caller)


# =============================================================================
# 7. PRESTIGE SUBCLASSES, ABILITIES & RACES
# =============================================================================

class CmdSubclass(default_cmds.MuxCommand):
    """
    View or choose a Prestige Guild Subclass specialization

    Usage:
      subclass
      specialize <subclass>
    """
    key = "subclass"
    aliases = ["specialize"]
    locks = "cmd:all()"
    help_category = "Guilds"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("\n|w===================== PRESTIGE GUILD SUBCLASSES =====================|n")
            for sub_name, data in PRESTIGE_SUBCLASSES.items():
                is_curr = caller.db.subclass == sub_name
                mark = "|g[CURRENT]|n " if is_curr else ""
                caller.msg(f"{mark}|c{sub_name:<12}|n (Guild: |y{data['parent']:<8}|n) - {data['desc']}")
                caller.msg(f"    Active Ability: |w{data['ability']}|n - {data['ability_desc']}")
                stat_str = ", ".join([f"+{v} {k.upper()}" for k, v in data['stat_bonus'].items()])
                caller.msg(f"    Stat Bonuses:   |g{stat_str}|n\n")
            caller.msg("|w======================================================================|n")
            if caller.db.subclass:
                caller.msg(f"You are currently specialized as a |g{caller.db.subclass}|n.")
            else:
                caller.msg("To specialize, use: |wspecialize <subclass>|n")
            return

        choice = self.args.strip().title()
        if choice not in PRESTIGE_SUBCLASSES:
            caller.msg(f"Unknown subclass '{choice}'. Available: {', '.join(PRESTIGE_SUBCLASSES.keys())}")
            return

        sub_data = PRESTIGE_SUBCLASSES[choice]
        if caller.db.guild != sub_data["parent"]:
            caller.msg(f"You cannot specialize as a {choice}! You must be a member of the {sub_data['parent']} Guild (Your guild: {caller.db.guild}).")
            return

        if caller.db.subclass == choice:
            caller.msg(f"You are already specialized as a {choice}!")
            return

        # Apply specialization
        caller.db.subclass = choice
        for stat, val in sub_data["stat_bonus"].items():
            curr = getattr(caller.db, stat, 10)
            setattr(caller.db, stat, curr + val)

        # Update vitals
        caller.db.max_hp = caller.db.con * 10
        caller.db.hp = caller.db.max_hp
        caller.db.max_mana = caller.db.int * 8
        caller.db.mana = caller.db.max_mana
        caller.db.max_stamina = (caller.db.con + caller.db.dex) * 5
        caller.db.stamina = caller.db.max_stamina

        caller.msg(
            f"\n|Y======================================================================\n"
            f"*** PRESTIGE SPECIALIZATION ACHIEVED! ***\n"
            f"You have attained the rank of |w{choice}|Y in the {caller.db.guild} Guild!\n"
            f"Granted Signature Ability: |w{sub_data['ability']}|Y (Use: |wability|Y)\n"
            f"======================================================================|n\n"
        )
        caller.location.msg_contents(
            f"|Y{caller.key} has specialized as a {choice}! An aura of martial and arcane mastery settles upon them.|n",
            exclude=[caller]
        )


class CmdAbility(default_cmds.MuxCommand):
    """
    Trigger your subclass's signature active combat ability

    Usage:
      ability
      special [at <target>]
    """
    key = "ability"
    aliases = ["special"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not caller.db.subclass:
            caller.msg("You have not specialized in a subclass yet! Type |wsubclass|n or |wspecialize <name>|n.")
            return

        sub = caller.db.subclass
        data = PRESTIGE_SUBCLASSES.get(sub)
        if not data:
            caller.msg("Unknown subclass ability.")
            return

        ab = data["ability"]

        # 1. Knight: shieldwall
        if ab == "shieldwall":
            if (caller.db.stamina or 0) < 20:
                caller.msg("Not enough stamina! (Requires 20 Stamina)")
                return
            caller.db.stamina -= 20
            caller.db.shieldwall = True
            caller.msg("|c*** SHIELDWALL RAISED! *** You brace behind an impenetrable fortress of steel, halving incoming physical damage!|n")
            caller.location.msg_contents(f"{caller.key} raises a massive defensive shieldwall!", exclude=[caller])

        # 2. Berserker: rage
        elif ab == "rage":
            if (caller.db.stamina or 0) < 20:
                caller.msg("Not enough stamina! (Requires 20 Stamina)")
                return
            caller.db.stamina -= 20
            caller.db.is_raging = True
            caller.msg("|r*** BLOOD RAGE! *** Red veins burst in your eyes as an uncontrollable battle frenzy grants +15 Weapon Damage!|n")
            caller.location.msg_contents(f"{caller.key} roars in uncontrollable blood frenzy!", exclude=[caller])

        # 3. Pyromancer: combustion
        elif ab == "combustion":
            if (caller.db.mana or 0) < 20:
                caller.msg("Not enough mana! (Requires 20 Mana)")
                return
            caller.db.mana -= 20
            caller.db.combustion_active = True
            caller.msg("|r*** COMBUSTION CHARGED! *** Superheated thermal energy coats your hands! Your next Fireball or Firebolt deals +50% explosive damage!|n")
            caller.location.msg_contents(f"Waves of intense heat shimmer and warp the air around {caller.key}.", exclude=[caller])

        # 4. Conjurer: elemental
        elif ab == "elemental":
            if (caller.db.mana or 0) < 30:
                caller.msg("Not enough mana! (Requires 30 Mana)")
                return
            caller.db.mana -= 30
            elem = create_object(
                Object,
                key=f"Lesser Elemental of {caller.key}",
                location=caller.location,
                aliases=["elemental", "fire elemental"],
                tags=["eldoria_world", "elemental", "pet"]
            )
            elem.db.desc = f"A swirling vortex of living primordial fire bound to {caller.key}'s command."
            elem.db.owner_id = caller.id
            elem.db.hp = 70
            elem.db.max_hp = 70
            caller.msg(f"|y*** PLANAR CONJURATION *** You tear the ether open, summoning {elem.key}!|n")
            caller.location.msg_contents(f"A rift tears in reality and {elem.key} emerges in a crackle of sparks!", exclude=[caller])

        # 5. Healer: blessing
        elif ab == "blessing":
            if (caller.db.mana or 0) < 25:
                caller.msg("Not enough mana! (Requires 25 Mana)")
                return
            caller.db.mana -= 25
            caller.db.hp = min(caller.db.max_hp, (caller.db.hp or 50) + 40)
            caller.msg("|g*** CELESTIAL BLESSING! *** Divine radiance mends your flesh, restoring 40 HP!|n")
            caller.location.msg_contents(f"Pillars of soothing light cascade over {caller.key}.", exclude=[caller])

        # 6. Inquisitor: exorcism
        elif ab == "exorcism":
            if (caller.db.mana or 0) < 25:
                caller.msg("Not enough mana! (Requires 25 Mana)")
                return
            target_name = self.args.strip()
            if not target_name:
                caller.msg("Who do you want to target with Exorcism?")
                return
            target = caller.search(target_name, location=caller.location)
            if not target:
                return
            init_nightmare_character(target)
            caller.db.mana -= 25
            dmg = random.randint(35, 65) + (caller.db.wis or 10)
            is_undead = "undead" in target.tags.all() or "skeleton" in target.key.lower() or "zombie" in target.key.lower()
            if is_undead:
                dmg *= 2
                caller.msg("|Y*** EXORCISM: UNDEAD PURGE! *** The foul undead is wracked with agony from pure holy fire! (Double Damage)|n")
            target.db.hp = max(0, target.db.hp - dmg)
            caller.msg(f"|YYou unleash an EXORCISM upon {target.key} for {dmg} holy damage!|n")
            target.msg(f"|Y{caller.key} brands you with searing exorcism fire for {dmg} damage!|n")
            caller.location.msg_contents(f"|YBlinding golden fire consumes {target.key}!|n", exclude=[caller, target])

        # 7. Assassin: poison
        elif ab == "poison":
            if (caller.db.stamina or 0) < 15:
                caller.msg("Not enough stamina! (Requires 15 Stamina)")
                return
            caller.db.stamina -= 15
            caller.db.poison_blade = 5
            caller.msg("|g*** WYVERN POISON APPLIED! *** You coat your blade with lethal green toxin (5 strikes active).|n")

        # 8. Shadowthief: shadowstep
        elif ab == "shadowstep":
            if (caller.db.stamina or 0) < 20:
                caller.msg("Not enough stamina! (Requires 20 Stamina)")
                return
            caller.db.stamina -= 20
            caller.msg("|x*** SHADOWSTEP! *** You dissolve into the ambient shadows, becoming untargetable!|n")
            caller.location.msg_contents(f"{caller.key} steps backward into the gloom and vanishes without a whisper.", exclude=[caller])

        # 9. Beastmaster: callpet
        elif ab == "callpet":
            if (caller.db.stamina or 0) < 25:
                caller.msg("Not enough stamina! (Requires 25 Stamina)")
                return
            caller.db.stamina -= 25
            wolf = create_object(
                Object,
                key=f"Mountain Dire Wolf of {caller.key}",
                location=caller.location,
                aliases=["dire wolf", "wolf", "pet"],
                tags=["eldoria_world", "beast", "pet"]
            )
            wolf.db.desc = f"A massive silver dire wolf with razor fangs, loyally guarding {caller.key}."
            wolf.db.owner_id = caller.id
            wolf.db.hp = 65
            wolf.db.max_hp = 65
            caller.msg(f"|w*** BEAST CALL *** You whistle into the wind, and {wolf.key} bounds to your side!|n")
            caller.location.msg_contents(f"A savage dire wolf leaps out of the shadows to join {caller.key}!", exclude=[caller])

        # 10. Sniper: aimedshot
        elif ab == "aimedshot":
            if (caller.db.stamina or 0) < 25:
                caller.msg("Not enough stamina! (Requires 25 Stamina)")
                return
            target_name = self.args.strip()
            if not target_name:
                caller.msg("Who do you want to target with Aimed Shot?")
                return
            target = caller.search(target_name, location=caller.location)
            if not target:
                return
            init_nightmare_character(target)
            caller.db.stamina -= 25
            dmg = random.randint(45, 75) + (caller.db.dex or 10)
            target.db.hp = max(0, target.db.hp - dmg)
            caller.msg(f"|R*** AIMED SNIPER SHOT! *** You release an arrow straight through {target.key}'s weak point for {dmg} piercing damage!|n")
            target.msg(f"|R{caller.key}'s arrow pierces cleanly through your armor for {dmg} damage!|n")
            caller.location.msg_contents(f"{caller.key} fires an armor-piercing shot into {target.key}!", exclude=[caller, target])


class CmdRacial(default_cmds.MuxCommand):
    """
    Activate your innate racial active ability

    Usage:
      racial
      racepower [at <target>]
    """
    key = "racial"
    aliases = ["racepower"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        race = caller.db.race or "Human"
        r_data = RACES.get(race)
        if not r_data:
            caller.msg("No racial data found.")
            return

        ab = r_data["ability"]

        if ab == "rally":  # Human
            caller.db.stamina = min(caller.db.max_stamina, (caller.db.stamina or 0) + 40)
            caller.msg("|Y*** HUMAN RALLY! *** You take a deep breath and rally your willpower, recovering 40 Stamina!|n")
            caller.location.msg_contents(f"{caller.key} rallies their spirits with renewed determination.", exclude=[caller])

        elif ab == "feystep":  # Elf
            exits = caller.location.exits
            if exits:
                dest_exit = random.choice(exits)
                caller.msg(f"|g*** FEYSTEP! *** You slip between the dimensions of the Feywild, stepping instantly to the {dest_exit.key}!|n")
                caller.location.msg_contents(f"{caller.key} glides through a shimmering green portal and disappears.", exclude=[caller])
                dest_exit.at_traverse(caller, dest_exit.destination)
            else:
                caller.msg("|g*** FEYSTEP! *** Shimmering emerald light wraps around you, confusing your foes!|n")

        elif ab == "stoneform":  # Dwarf
            caller.db.stoneskin_absorb = (caller.db.stoneskin_absorb or 0) + 40
            caller.msg("|y*** DWARVEN STONEFORM! *** Your skin turns to rugged mountain granite, granting 40 damage absorption!|n")
            caller.location.msg_contents(f"{caller.key}'s skin turns to hard, chiseled stone!", exclude=[caller])

        elif ab == "luckydodge":  # Halfling
            caller.db.lucky_dodge = True
            caller.msg("|g*** HALFLING LUCK! *** You brace yourself with supernatural agility — the next incoming attack will miss you completely!|n")

        elif ab == "darkness":  # Drow
            caller.location.db.is_dark = True
            caller.msg("|m*** DROW GLOBE OF DARKNESS! *** You summon an orb of pitch-black subterranean darkness!|n")
            caller.location.msg_contents(f"|m{caller.key} raises a hand and an impenetrable globe of pitch-black darkness engulfs the room!|n", exclude=[caller])

        elif ab == "breathefire":  # Dragonkin
            if (caller.db.stamina or 0) < 20:
                caller.msg("Not enough stamina! (Requires 20 Stamina)")
                return
            caller.db.stamina -= 20
            caller.msg("|r*** DRAGON BREATH! *** You exhale a roaring torrent of blistering dragonfire across the area!|n")
            caller.location.msg_contents(f"|r{caller.key} opens their draconic jaws, spewing a cone of roaring flame!|n", exclude=[caller])
            for obj in caller.location.contents:
                if obj != caller and hasattr(obj, "db") and obj.db.hp is not None and not getattr(obj.db, "is_ghost", False):
                    f_dmg = random.randint(30, 55)
                    obj.db.hp = max(0, obj.db.hp - f_dmg)
                    obj.msg(f"|rBlistering dragonfire scorches you for {f_dmg} fire damage!|n")
                    caller.msg(f"|rDragon breath roasts {obj.key} for {f_dmg} damage!|n")

        elif ab == "trample":  # Centaur
            if (caller.db.stamina or 0) < 20:
                caller.msg("Not enough stamina! (Requires 20 Stamina)")
                return
            target_name = self.args.strip()
            if not target_name:
                caller.msg("Who do you want to trample?")
                return
            target = caller.search(target_name, location=caller.location)
            if not target:
                return
            init_nightmare_character(target)
            caller.db.stamina -= 20
            t_dmg = random.randint(30, 50) + (caller.db.str or 10)
            target.db.hp = max(0, target.db.hp - t_dmg)
            caller.msg(f"|y*** CENTAUR TRAMPLE! *** You gallop thunderously forward and crush {target.key} beneath your iron hooves for {t_dmg} bludgeoning damage!|n")
            target.msg(f"|r{caller.key} charges you down, trampling you beneath heavy hooves for {t_dmg} damage!|n")
            caller.location.msg_contents(f"{caller.key} charges down {target.key} with a thunderous trampling kick!", exclude=[caller, target])


class CmdRace(default_cmds.MuxCommand):
    """
    View or select your player race

    Usage:
      race
      race <Human/Elf/Dwarf/Halfling/Drow/Dragonkin/Centaur>
    """
    key = "race"
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg(f"\n|wYour current race:|n |y{caller.db.race}|n\n")
            caller.msg("|w=========================== PLAYABLE RACES & TRAITS ===========================|n")
            for r_name, r_data in RACES.items():
                nv = "|c[Nightvision]|n " if r_data.get("nightvision") else ""
                caller.msg(f"|c{r_name:<10}|n: {r_data['desc']} {nv}")
                caller.msg(f"            Racial Power: |w{r_data['ability']}|n - {r_data['ability_desc']}\n")
            caller.msg("|w==============================================================================|n\n")
            caller.msg("To change race, use: |wrace <name>|n")
            return

        choice = self.args.strip().title()
        if choice not in RACES:
            caller.msg(f"Unknown race '{choice}'. Available: {', '.join(RACES.keys())}")
            return

        caller.db.race = choice
        from world.languages import get_innate_languages
        new_langs = get_innate_languages(choice, caller.db.guild or "Fighter")
        curr_langs = caller.db.languages or {}
        for l_k, l_v in new_langs.items():
            curr_langs[l_k] = max(curr_langs.get(l_k, 0), l_v)
        caller.db.languages = curr_langs

        limbs = caller.db.limbs or {
            "head": {"hp": 50, "max_hp": 50},
            "torso": {"hp": 100, "max_hp": 100},
            "right arm": {"hp": 60, "max_hp": 60},
            "left arm": {"hp": 60, "max_hp": 60},
            "right leg": {"hp": 70, "max_hp": 70},
            "left leg": {"hp": 70, "max_hp": 70},
        }
        if choice == "Dragonkin":
            limbs["tail"] = {"hp": 50, "max_hp": 50}
        elif choice == "Centaur":
            limbs["forelegs"] = {"hp": 80, "max_hp": 80}
            limbs["hindlegs"] = {"hp": 90, "max_hp": 90}
        caller.db.limbs = limbs

        caller.msg(f"|gYou have chosen the |y{choice}|g race! Your innate racial traits and morphology are active.|n")
        caller.msg(f"Granted Racial Power: |w{RACES[choice]['ability']}|n (Use: |wracial|n or |wracepower|n)")


# =============================================================================
# 8. NIGHTMARE VITALS, PARTY & SENSORY EXPLORATION COMMANDS
# =============================================================================

class CmdHp(default_cmds.MuxCommand):
    """
    Display a fast, single-line vitals prompt

    Usage:
      hp
      gauge
    """
    key = "hp"
    aliases = ["gauge"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        if getattr(caller.db, "is_ghost", False):
            caller.msg("|r[GHOST] You have no physical vitals.|n")
            return

        hp = caller.db.hp or 0
        max_hp = caller.db.max_hp or 1
        pct = int((hp / max_hp) * 100)
        if pct > 60:
            hp_str = f"|g{hp}/{max_hp}|n"
        elif pct > 25:
            hp_str = f"|y{hp}/{max_hp}|n"
        else:
            hp_str = f"|r{hp}/{max_hp}|n"

        mana = caller.db.mana or 0
        max_mana = caller.db.max_mana or 1
        stamina = caller.db.stamina or 0
        max_stamina = caller.db.max_stamina or 1

        wimpy_val = getattr(caller.db, "wimpy", 0) or 0
        wimpy_str = f"|m{wimpy_val}%|n" if wimpy_val > 0 else "|xOFF|n"

        coins = caller.db.coins or {"copper": 0, "silver": 0, "gold": 0}
        g = coins.get("gold", 0)
        s = coins.get("silver", 0)
        c = coins.get("copper", 0)

        caller.msg(f"|w[|n HP: {hp_str} |w| Mana: |c{mana}/{max_mana}|n |w| Stm: |y{stamina}/{max_stamina}|n |w| Wimpy: {wimpy_str} |w| Coins: |y{g}g |w{s}s |r{c}c |w]|n")


class CmdWimpy(default_cmds.MuxCommand):
    """
    Configure automatic fleeing when health falls below a given percentage

    Usage:
      wimpy
      wimpy <percentage>
      wimpy off
    """
    key = "wimpy"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        if not self.args:
            curr = getattr(caller.db, "wimpy", 0) or 0
            if curr > 0:
                max_hp = caller.db.max_hp or 100
                thresh = int(max_hp * (curr / 100.0))
                caller.msg(f"Wimpy is currently set to |m{curr}%|n (fleeing at or below {thresh} HP).")
            else:
                caller.msg("Wimpy auto-flee is currently |xOFF|n. Use: |wwimpy <percentage>|n (e.g. wimpy 20)")
            return

        arg = self.args.strip().lower()
        if arg in ["off", "0", "disable"]:
            caller.db.wimpy = 0
            caller.msg("Wimpy auto-flee disabled.")
            return

        try:
            val = int(arg)
            if val < 1 or val > 99:
                caller.msg("Wimpy percentage must be between 1 and 99.")
                return
            caller.db.wimpy = val
            max_hp = caller.db.max_hp or 100
            thresh = int(max_hp * (val / 100.0))
            caller.msg(f"Wimpy set to |m{val}%|n. You will automatically flee combat when your HP drops below {thresh} HP.")
        except ValueError:
            caller.msg("Invalid wimpy value. Use a number between 1 and 99, or 'off'.")


class CmdConsider(default_cmds.MuxCommand):
    """
    Evaluate the combat danger and health of a potential target

    Usage:
      consider <target>
      con <target>
    """
    key = "consider"
    aliases = ["con"]
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Consider who?")
            return

        target_name = self.args.strip()
        target = caller.search(target_name, location=caller.location)
        if not target:
            return

        init_nightmare_character(caller)
        init_nightmare_character(target)

        c_lvl = caller.db.level or 1
        t_lvl = target.db.level or 1
        diff = t_lvl - c_lvl

        if diff <= -5:
            assessment = f"|gYou would stomp {target.key} into a bloody pulp!|n"
        elif diff <= -2:
            assessment = f"|g{target.key} looks like an easy kill.|n"
        elif diff <= 1:
            assessment = f"|yThe fight with {target.key} would be fairly even.|n"
        elif diff <= 4:
            assessment = f"|r{target.key} looks tough. You might want some help!|n"
        else:
            assessment = f"|RAttacking {target.key} would be suicidal! Flee while you can!|n"

        t_hp = target.db.hp if target.db.hp is not None else 100
        t_max = target.db.max_hp or 100
        pct = int((t_hp / t_max) * 100) if t_max > 0 else 100

        if pct >= 100:
            condition = f"{target.key} is in pristine physical condition."
        elif pct >= 75:
            condition = f"{target.key} has a few superficial scratches."
        elif pct >= 50:
            condition = f"{target.key} is wounded and bleeding."
        elif pct >= 25:
            condition = f"{target.key} is badly battered and staggering."
        else:
            condition = f"{target.key} is near death!"

        caller.msg(f"\n|wEvaluating {target.key} (Level {t_lvl}):|n")
        caller.msg(f"  {assessment}")
        caller.msg(f"  {condition}\n")


class CmdKick(default_cmds.MuxCommand):
    """
    Deliver a fierce martial kick to an opponent

    Usage:
      kick <target>
    """
    key = "kick"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        if getattr(caller.db, "is_ghost", False):
            caller.msg("You are a ghost! You cannot kick.")
            return

        stamina = caller.db.stamina or 0
        if stamina < 12:
            caller.msg("You are too exhausted to kick! (Requires 12 Stamina)")
            return

        target = None
        if self.args:
            target = caller.search(self.args.strip(), location=caller.location)
        else:
            target = getattr(caller.ndb, "combat_target", None)

        if not target:
            caller.msg("Kick who?")
            return

        if target == caller:
            caller.msg("You cannot kick yourself!")
            return

        if getattr(target.db, "is_ghost", False):
            caller.msg(f"{target.key} is an incorporeal spirit!")
            return

        caller.db.stamina = max(0, stamina - 12)
        caller.db.is_resting = False

        str_bonus = (caller.db.str or 10) // 3
        guild_bonus = 4 if caller.db.guild == "Fighter" else 0
        dmg = random.randint(8, 16) + str_bonus + guild_bonus

        trigger_skill_tick(caller, "melee", True)

        caller.msg(f"|yYou deliver a powerful, sweeping kick right into {target.key} for |r{dmg}|y damage!|n")
        target.msg(f"|r{caller.key} delivers a fierce kick into your ribs for {dmg} damage!|n")
        caller.location.msg_contents(f"{caller.key} kicks {target.key} hard!", exclude=[caller, target])

        target.db.hp = max(0, (target.db.hp or 0) - dmg)
        if target.db.hp <= 0:
            handle_player_death(target, caller)
        else:
            if not is_in_combat(caller):
                start_combat(caller, target)


class CmdDisarm(default_cmds.MuxCommand):
    """
    Attempt to disarm your opponent, knocking their weapon to the ground

    Usage:
      disarm <target>
    """
    key = "disarm"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        if getattr(caller.db, "is_ghost", False):
            caller.msg("You are a ghost! You cannot disarm anyone.")
            return

        stamina = caller.db.stamina or 0
        if stamina < 15:
            caller.msg("You are too tired to attempt a disarm! (Requires 15 Stamina)")
            return

        target = None
        if self.args:
            target = caller.search(self.args.strip(), location=caller.location)
        else:
            target = getattr(caller.ndb, "combat_target", None)

        if not target:
            caller.msg("Disarm who?")
            return

        if target == caller:
            caller.msg("You cannot disarm yourself!")
            return

        if getattr(target.db, "is_ghost", False):
            caller.msg(f"{target.key} is an incorporeal spirit!")
            return

        caller.db.stamina = max(0, stamina - 15)
        caller.db.is_resting = False

        # Look for target's equipped weapon
        equipped = getattr(target.db, "equipped_slots", {}) or {}
        weapon = None
        weapon_slot = None
        for slot in ["right_hand", "left_hand"]:
            wp_candidate = equipped.get(slot)
            if wp_candidate:
                weapon = wp_candidate
                weapon_slot = slot
                break

        # Contested roll: caller Dex vs target Dex + Str/2
        c_roll = (caller.db.dex or 10) + random.randint(1, 20)
        t_roll = (target.db.dex or 10) + ((target.db.str or 10) // 2) + random.randint(1, 20)

        trigger_skill_tick(caller, "melee", True)

        if not weapon:
            caller.msg(f"{target.key} is fighting unarmed and cannot be disarmed!")
            if not is_in_combat(caller):
                start_combat(caller, target)
            return

        if c_roll > t_roll:
            # Success! Unequip and move weapon to floor
            equipped.pop(weapon_slot, None)
            target.db.equipped_slots = equipped
            weapon.location = target.location

            caller.msg(f"|GWith a lightning-fast twist of your weapon, you flick {weapon.key} straight out of {target.key}'s hands onto the floor!|n")
            target.msg(f"|R{caller.key} expertly twists their blade and disarms you! Your {weapon.key} clatters to the ground!|n")
            caller.location.msg_contents(f"{caller.key} disarms {target.key}, knocking {weapon.key} clattering to the floor!", exclude=[caller, target])
        else:
            caller.msg(f"|yYou try to hook {target.key}'s weapon, but they nimbly parry your attempt!|n")
            target.msg(f"|y{caller.key} tries to disarm you, but you keep a firm grip on your weapon!|n")

        if not is_in_combat(caller):
            start_combat(caller, target)


class CmdParty(default_cmds.MuxCommand):
    """
    Manage an adventuring party

    Usage:
      party form <party name>
      party invite <player>
      party join <party name>
      party leave
      party disband
      party status
      party say <message>
      p <message>
    """
    key = "party"
    locks = "cmd:all()"
    help_category = "Party"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        if not self.args:
            caller.msg("""|wParty Commands:|n
  |wparty form <name>|n     - Form a new adventuring party
  |wparty invite <player>|n - Invite a player to your party
  |wparty join <name>|n     - Accept an invitation and join
  |wparty leave|n           - Leave your current party
  |wparty disband|n         - Disband your party (leader only)
  |wparty status|n          - View party members and health
  |wparty say <msg>|n       - Speak to party members (or |wp <msg>|n)""")
            return

        parts = self.args.strip().split(None, 1)
        subcmd = parts[0].lower()
        subarg = parts[1].strip() if len(parts) > 1 else ""

        if subcmd == "form":
            if not subarg:
                caller.msg("Usage: party form <party name>")
                return
            ok, msg = create_party(caller, subarg)
            caller.msg(msg)

        elif subcmd == "invite":
            if not subarg:
                caller.msg("Usage: party invite <player>")
                return
            target = caller.search(subarg, location=caller.location)
            if not target:
                return
            ok, msg = invite_to_party(caller, target)
            caller.msg(msg)
            if ok:
                target.msg(f"|y{caller.key} has invited you to join their party! Type: |wparty join {caller.db.party}|n")

        elif subcmd == "join":
            if not subarg:
                caller.msg("Usage: party join <party name>")
                return
            ok, msg = join_party(caller, subarg)
            caller.msg(msg)

        elif subcmd == "leave":
            ok, msg = leave_party(caller)
            caller.msg(msg)

        elif subcmd == "disband":
            ok, msg = disband_party(caller)
            caller.msg(msg)

        elif subcmd in ["say", "chat"]:
            if not subarg:
                caller.msg("What do you want to say to your party?")
                return
            party = get_party(caller)
            if not party:
                caller.msg("You are not in a party.")
                return
            msg_party(party["name"], f"|c[Party: {party['name']}] {caller.key}: {subarg}|n")

        elif subcmd in ["status", "stat", "list"]:
            party = get_party(caller)
            if not party:
                caller.msg("You are not currently in an adventuring party.")
                return

            from evennia.objects.models import ObjectDB
            leader = ObjectDB.objects.filter(id=party["leader_id"]).first()
            l_name = leader.key if leader else "None"

            text = [
                f"\n|c=== Party: {party['name']} (Leader: {l_name}) ===|n",
                f"{'Name':<18} {'Lvl':<5} {'HP':<15} {'Mana':<15} {'Location'}",
                "-" * 65
            ]

            for m_id in party["members"]:
                m = ObjectDB.objects.filter(id=m_id).first()
                if not m:
                    continue
                hp_str = f"{m.db.hp or 0}/{m.db.max_hp or 1}"
                mana_str = f"{m.db.mana or 0}/{m.db.max_mana or 1}"
                loc_str = m.location.key if m.location else "Unknown"
                star = "*" if m_id == party["leader_id"] else " "
                text.append(f"{star}{m.key:<17} {m.db.level or 1:<5} {hp_str:<15} {mana_str:<15} {loc_str}")

            text.append("-" * 65)
            text.append("|y* Party members in the same room earn +10% bonus teamwork XP!|n\n")
            caller.msg("\n".join(text))

        else:
            caller.msg(f"Unknown party command '{subcmd}'. Type 'party' for help.")


class CmdPartySay(default_cmds.MuxCommand):
    """
    Send a message to your adventuring party

    Usage:
      p <message>
    """
    key = "p"
    locks = "cmd:all()"
    help_category = "Party"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to say to your party?")
            return
        party = get_party(caller)
        if not party:
            caller.msg("You are not in an adventuring party. Form one with: party form <name>")
            return
        msg_party(party["name"], f"|c[Party: {party['name']}] {caller.key}: {self.args.strip()}|n")


class CmdAssist(default_cmds.MuxCommand):
    """
    Join the fight to assist an ally in combat

    Usage:
      assist <player>
    """
    key = "assist"
    locks = "cmd:all()"
    help_category = "Combat"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        if getattr(caller.db, "is_ghost", False):
            caller.msg("You are a ghost! You cannot assist in battle.")
            return

        if not self.args:
            caller.msg("Assist who?")
            return

        ally = caller.search(self.args.strip(), location=caller.location)
        if not ally:
            return

        if ally == caller:
            caller.msg("You cannot assist yourself!")
            return

        target = getattr(ally.ndb, "combat_target", None)
        if not target:
            caller.msg(f"{ally.key} is not currently engaged in combat.")
            return

        if target == caller:
            caller.msg(f"{ally.key} is fighting YOU!")
            return

        if getattr(target.db, "is_ghost", False):
            caller.msg(f"{target.key} is already dead or an incorporeal spirit.")
            return

        caller.msg(f"|yYou charge into the fray to assist {ally.key} against {target.key}!|n")
        ally.msg(f"|g{caller.key} leaps to your side to assist in your battle against {target.key}!|n")
        caller.location.msg_contents(f"{caller.key} joins {ally.key} in attacking {target.key}!", exclude=[caller, ally, target])
        start_combat(caller, target)


class CmdSpells(default_cmds.MuxCommand):
    """
    Inspect the directory of magical incantations and circles

    Usage:
      spells
      spells <circle_number>
    """
    key = "spells"
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)

        filter_circle = None
        if self.args:
            try:
                filter_circle = int(self.args.strip())
            except ValueError:
                caller.msg("Specify a circle number from 1 to 5 (e.g. spells 1).")
                return

        caller.msg("\n|w============================= SPELL DIRECTORY =============================|n")
        caller.msg(f"{'Spell Name':<16} {'Circle':<8} {'Mana':<8} {'Chant / Incantation':<25}")
        caller.msg("|b" + "-" * 76 + "|n")

        for s_name, s_data in SPELLS.items():
            circle = s_data.get("circle", 1)
            if filter_circle is not None and circle != filter_circle:
                continue
            mana = s_data.get("mana", 10)
            chant = s_data.get("chant", "")
            caller.msg(f"|c{s_name:<16}|n |wCircle {circle:<3}|n |y{mana:<6} MP|n |m\"{chant}\"|n")
            caller.msg(f"   |xDescription:|n {s_data.get('desc', '')}")

        caller.msg("|b" + "-" * 76 + "|n")
        caller.msg("To cast a spell: |wcast <spell> [at <target>]|n")
        caller.msg("|w===========================================================================|n\n")


class CmdSearch(default_cmds.MuxCommand):
    """
    Search your surroundings thoroughly for hidden items, coins, or secrets

    Usage:
      search
    """
    key = "search"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        loc = caller.location
        if not loc:
            caller.msg("You are floating in nothingness; there is nothing to search.")
            return

        caller.msg(f"|yYou carefully search the area around {loc.key}...|n")
        loc.msg_contents(f"{caller.key} kneels down and carefully searches the surroundings.", exclude=[caller])

        # Check if caller finds small coins dropped in nooks
        searched_key = f"_searched_{loc.id}"
        if not getattr(caller.ndb, searched_key, False):
            setattr(caller.ndb, searched_key, True)
            roll = random.randint(1, 100) + (caller.db.wis or 10)
            if roll > 60:
                found_copper = random.randint(3, 8)
                caller.db.coins["copper"] = caller.db.coins.get("copper", 0) + found_copper
                caller.msg(f"|gAha! You discover {found_copper} copper coins hidden in a crevice!|n")
                return

        # Check room contents for hidden items or general details
        contents = [o for o in loc.contents if o != caller and not o.destination]
        if contents:
            item_names = ", ".join(o.key for o in contents[:5])
            caller.msg(f"Your inspection reveals items and features nearby: |w{item_names}|n.")
        else:
            caller.msg("After a thorough search, you find nothing unusual here.")


class CmdListen(default_cmds.MuxCommand):
    """
    Listen to ambient environmental sounds or listen closely to a target

    Usage:
      listen
      listen <target>
    """
    key = "listen"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        loc = caller.location
        if not loc:
            caller.msg("Silence echoes in the void.")
            return

        if self.args:
            target = caller.search(self.args.strip(), location=loc)
            if not target:
                return
            caller.msg(f"You lean in and listen closely to {target.key}...")
            if getattr(target.db, "is_ghost", False):
                caller.msg(f"|cYou hear only a chilling, ethereal hum emanating from {target.key}.|n")
            elif hasattr(target.db, "hp"):
                hp = target.db.hp or 0
                max_hp = target.db.max_hp or 100
                if hp < (max_hp // 3):
                    caller.msg(f"|rYou hear {target.key}'s ragged, labored breathing and faint gasps of pain.|n")
                else:
                    caller.msg(f"|gYou hear {target.key}'s steady, rhythmic breathing and the soft rustle of their gear.|n")
            else:
                caller.msg(f"{target.key} emits no sound.")
            return

        # Ambient listening
        terrain = getattr(loc.db, "terrain", "city") or "city"
        terrain_key = terrain.lower()
        sound = AMBIENT_SENSORY.get("sounds", {}).get(terrain_key)
        if not sound:
            sound = AMBIENT_SENSORY["sounds"].get("city", "You hear the faint murmur of the surroundings.")

        caller.msg(f"\n|c[Ambient Acoustics - {loc.key}]|n\n{sound}\n")


class CmdSmell(default_cmds.MuxCommand):
    """
    Sample the ambient aromas of the area or sniff a specific target

    Usage:
      smell
      smell <target>
    """
    key = "smell"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        loc = caller.location
        if not loc:
            caller.msg("The void smells of pure vacuum.")
            return

        if self.args:
            target = caller.search(self.args.strip(), location=loc)
            if not target:
                return
            caller.msg(f"You take a deep sniff of {target.key}...")
            if getattr(target.db, "is_ghost", False):
                caller.msg(f"|m{target.key} smells of ozone, cold spectral dust, and ancient crypts.|n")
            elif getattr(target.db, "race", None) == "Dwarf":
                caller.msg(f"|y{target.key} smells of dark stout ale, forge soot, and underground granite.|n")
            elif getattr(target.db, "race", None) == "Elf":
                caller.msg(f"|g{target.key} smells of fresh pine boughs, wild berries, and morning dew.|n")
            elif getattr(target.db, "race", None) == "Dragonkin":
                caller.msg(f"|r{target.key} smells of sulfur, heated basalt, and scorching embers.|n")
            else:
                caller.msg(f"|w{target.key} smells of leather armor, iron, and travel dust.|n")
            return

        # Ambient scent
        terrain = getattr(loc.db, "terrain", "city") or "city"
        terrain_key = terrain.lower()
        scent = AMBIENT_SENSORY.get("scents", {}).get(terrain_key)
        if not scent:
            scent = AMBIENT_SENSORY["scents"].get("city", "You smell the air of the area.")

        caller.msg(f"\n|y[Ambient Scents - {loc.key}]|n\n{scent}\n")


class CmdAppraise(default_cmds.MuxCommand):
    """
    Appraise an item's condition, weight, market value, and combat properties

    Usage:
      appraise <item>
      value <item>
    """
    key = "appraise"
    aliases = ["value"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        init_nightmare_character(caller)
        if not self.args:
            caller.msg("Appraise what item?")
            return

        target = caller.search(self.args.strip(), location=caller)
        if not target:
            target = caller.search(self.args.strip(), location=caller.location)
        if not target:
            return

        weight = getattr(target.db, "weight", 1) or 1
        base_val = getattr(target.db, "value", 10) or 10

        # Wisdom check modifies valuation accuracy
        wis = caller.db.wis or 10
        val_est = max(1, int(base_val * (0.8 + (wis / 50.0))))
        gold = val_est // 100
        silver = (val_est % 100) // 10
        copper = val_est % 10

        caller.msg(f"\n|w=== Appraisal: {target.key} ===|n")
        caller.msg(f"  |xDescription:|n {target.db.desc or 'A nondescript item.'}")
        caller.msg(f"  |xWeight:|n {weight} stone")
        caller.msg(f"  |xEstimated Market Value:|n |y{gold} Gold|n |w{silver} Silver|n |r{copper} Copper|n")

        # Weapon / Armor inspection
        slot = getattr(target.db, "slot", None)
        dmg_bonus = getattr(target.db, "damage_bonus", None)
        armor_val = getattr(target.db, "armor_value", None)

        if dmg_bonus is not None or slot in ["right_hand", "left_hand"]:
            caller.msg(f"  |xType:|n Weapon (Damage Bonus: |r+{dmg_bonus or 0}|n)")
        elif armor_val is not None or slot in ["head", "torso", "legs", "shield"]:
            caller.msg(f"  |xType:|n Armor (Slot: |c{slot or 'body'}|n, Protection: |g+{armor_val or 0}|n)")

        caller.msg("|w" + "=" * 32 + "|n\n")


class CmdWhoNightmare(default_cmds.MuxCommand):
    """
    List all connected players in classic Nightmare LPMud format

    Usage:
      who
      lwho
    """
    key = "who"
    aliases = ["lwho"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        from evennia.server.sessionhandler import SESSIONS

        connected_chars = []
        for session in SESSIONS.get_sessions():
            char = session.get_puppet()
            if char and char not in connected_chars:
                connected_chars.append(char)

        if not connected_chars:
            caller.msg("No players are currently connected.")
            return

        caller.msg("\n|b==============================================================================|n")
        caller.msg("|w                    N I G H T M A R E   A D V E N T U R E R S               |n")
        caller.msg("|b==============================================================================|n")
        caller.msg(f"|w {'[Lvl  Race        Guild / Class      ]':<36} Player Name (Title)|n")
        caller.msg("|b" + "-" * 78 + "|n")

        for char in connected_chars:
            init_nightmare_character(char)
            lvl = char.db.level or 1
            race = char.db.race or "Human"
            guild = char.db.guild or "Adventurer"
            subclass = getattr(char.db, "subclass", None)
            if subclass:
                class_str = f"{guild}/{subclass}"
            else:
                class_str = guild

            bracket = f"[{lvl:<3} {race:<11} {class_str:<18}]"
            ghost_tag = " |r(GHOST)|n" if getattr(char.db, "is_ghost", False) else ""
            caller.msg(f" |c{bracket:<35}|n {char.key}{ghost_tag}")

        caller.msg("|b==============================================================================|n")
        caller.msg(f"|w Total Connected Adventurers: {len(connected_chars):<47}|n")
        caller.msg("|b==============================================================================|n\n")


