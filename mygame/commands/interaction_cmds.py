"""
Interactive gameplay commands:
- talk: Engage in branching dialogue with NPCs
- drink: Drink potions, beverages, and elixirs
- read: Read books, tomes, and scrolls
- light: Light torches, pyres, and watchtower beacons
- catch: Catch will-o'-the-wisps, familiars, or moonbeams
- turn: Turn sewer valves, pressure wheels, and mechanisms
- mine: Mine ore veins with a pickaxe
- cleanse: Cleanse diseased roots or holy altars
- insert: Insert steam cores into automatons
"""

from evennia import default_cmds
from evennia.utils.evmenu import EvMenu
from evennia.utils.create import create_object
from typeclasses.objects import Object


class CmdTalk(default_cmds.MuxCommand):
    """
    Talk to a non-player character (NPC)

    Usage:
      talk <target>
      talk

    Initiates an interactive dialogue menu with an NPC in the room.
    If only one talkative NPC is present, 'talk' will speak with them automatically.
    """

    key = "talk"
    aliases = ["speak", "chat"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        location = caller.location
        if not location:
            caller.msg("You cannot talk to anyone here.")
            return

        npcs = [
            obj for obj in location.contents
            if obj != caller and (obj.db.dialog_menu or (not obj.has_account and getattr(obj, 'is_character', False)))
        ]

        if not self.args:
            if not npcs:
                caller.msg("There is no one here to talk to.")
                return
            if len(npcs) == 1:
                target = npcs[0]
            else:
                names = ", ".join([npc.key for npc in npcs])
                caller.msg(f"Who do you want to talk to? Present here: {names}. Use: talk <name>")
                return
        else:
            target = caller.search(self.args.strip(), location=location)
            if not target:
                return

        menu_path = target.db.dialog_menu
        start_node = target.db.dialog_startnode or "menu_start_node"

        if not menu_path:
            caller.msg(f"{target.key} glances your way, but has nothing to say right now.")
            return

        caller.msg(f"|y(You approach {target.key} and strike up a conversation...)|n")
        EvMenu(
            caller,
            menu_path,
            startnode=start_node,
            auto_quit=True,
            auto_look=False
        )


class CmdDrink(default_cmds.MuxCommand):
    """
    Drink a potion, beverage, or elixir

    Usage:
      drink <item>
      quaff <item>
      sip <item>

    Consumes a potion or beverage from your inventory.
    """

    key = "drink"
    aliases = ["quaff", "sip"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to drink?")
            return

        item = caller.search(self.args.strip(), location=caller)
        if not item:
            return

        is_drinkable = item.db.is_drinkable
        drink_type = item.db.drink_type or "beverage"

        if not is_drinkable and not any(k in item.key.lower() for k in ["potion", "elixir", "stout", "beer", "drink", "flask", "ale", "salve", "tea"]):
            caller.msg(f"You cannot drink {item.key}!")
            return

        if drink_type in ["elixir", "salve"] or any(k in item.key.lower() for k in ["elixir", "potion", "salve"]):
            heal_hp = getattr(item.db, "heal_amount", None) or 45
            heal_stm = getattr(item.db, "stamina_amount", None) or 25
            max_hp = getattr(caller.db, "max_hp", 100) or 100
            max_stm = getattr(caller.db, "max_stamina", 80) or 80
            caller.db.hp = min(max_hp, (getattr(caller.db, "hp", 50) or 50) + heal_hp)
            caller.db.stamina = min(max_stm, (getattr(caller.db, "stamina", 50) or 50) + heal_stm)

            # Heal damaged limbs
            if caller.db.limbs:
                for l_data in caller.db.limbs.values():
                    l_data["hp"] = min(l_data.get("max_hp", 30), l_data.get("hp", 30) + (heal_hp // 2))

            caller.msg(
                f"|gYou consume the {item.key}! A soothing, radiant warmth washes "
                f"through your veins, healing {heal_hp} HP! ({caller.db.hp}/{max_hp} HP)|n"
            )
            caller.location.msg_contents(
                f"{caller.key} drinks a {item.key}. Soft light sparkles around them!",
                exclude=[caller]
            )
            item.delete()
        elif drink_type in ["stout", "beer", "ale"] or any(k in item.key.lower() for k in ["stout", "beer", "ale"]):
            heal_hp = 12
            heal_stm = 30
            max_hp = getattr(caller.db, "max_hp", 100) or 100
            max_stm = getattr(caller.db, "max_stamina", 80) or 80
            caller.db.hp = min(max_hp, (getattr(caller.db, "hp", 50) or 50) + heal_hp)
            caller.db.stamina = min(max_stm, (getattr(caller.db, "stamina", 50) or 50) + heal_stm)

            caller.msg(
                f"|yYou take a hearty, deep swig of the {item.key}! Ahhh... rich, malty, and delicious! "
                f"Restores {heal_hp} HP and {heal_stm} Stamina! ({caller.db.hp}/{max_hp} HP)|n"
            )
            caller.location.msg_contents(
                f"{caller.key} takes a deep draught from a {item.key} and wipes their mouth with satisfaction.",
                exclude=[caller]
            )
            item.delete()
        else:
            heal_hp = 8
            heal_stm = 15
            max_hp = getattr(caller.db, "max_hp", 100) or 100
            max_stm = getattr(caller.db, "max_stamina", 80) or 80
            caller.db.hp = min(max_hp, (getattr(caller.db, "hp", 50) or 50) + heal_hp)
            caller.db.stamina = min(max_stm, (getattr(caller.db, "stamina", 50) or 50) + heal_stm)
            caller.msg(f"|cYou take a refreshing drink from {item.key}. Restores {heal_hp} HP and {heal_stm} Stamina! ({caller.db.hp}/{max_hp} HP)|n")
            item.delete()


class CmdRead(default_cmds.MuxCommand):
    """
    Read an ancient tome, scroll, book, or sign

    Usage:
      read <item>

    Reads the contents or inscribed lore of an item in your hands or in the room.
    """

    key = "read"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to read?")
            return

        item = caller.search(self.args.strip())
        if not item:
            return

        readable_text = item.db.readable_text
        if readable_text:
            caller.msg(f"|w=== {item.key} ===|n\n{readable_text}")
        else:
            caller.msg(f"|w=== {item.key} ===|n\n{item.db.desc}")


class CmdLight(default_cmds.MuxCommand):
    """
    Light a pyre, beacon, or torch

    Usage:
      light <target>

    Ignites a signal beacon, pyre, or torch.
    """

    key = "light"
    aliases = ["ignite", "kindle"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to light?")
            return

        target_name = self.args.strip().lower()

        if any(w in target_name for w in ["beacon", "pyre", "fire", "signal"]):
            if "watchtower" not in caller.location.key.lower():
                caller.msg("There is no signal pyre here to light.")
                return

            caller.db.pyre_is_lit = True
            caller.msg(
                "|yYou strike sparks into the dry pine kindling inside the watchtower signal pyre! "
                "With a hearty *WHOOSH*, a roaring golden blaze bursts to life, sending a towering "
                "column of brilliant white smoke into the northern sky! Eldoria can now see the pass!|n"
            )
            caller.location.msg_contents(
                f"{caller.key} ignites the Watchtower Signal Pyre! Roaring flames illuminate the mountain peaks!",
                exclude=[caller]
            )
            return

        item = caller.search(self.args.strip())
        if not item:
            return

        if "torch" in item.key.lower():
            caller.msg(f"|yYou ignite the {item.key}. It flickers with warm yellow torchlight.|n")
            caller.location.msg_contents(f"{caller.key} lights a torch.", exclude=[caller])
        else:
            caller.msg(f"You cannot light {item.key}.")


class CmdCatch(default_cmds.MuxCommand):
    """
    Catch will-o'-the-wisps, familiars, or moonbeams

    Usage:
      catch <target>

    Catches wild creatures, spirits, or celestial phenomena.
    """

    key = "catch"
    aliases = ["capture", "trap"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to catch?")
            return

        target = self.args.strip().lower()

        # Capture will-o'-the-wisp
        if "wisp" in target:
            if "mire" not in caller.location.key.lower() and "marsh" not in caller.location.key.lower():
                caller.msg("There are no will-o'-the-wisps here to catch.")
                return

            lantern = next((i for i in caller.contents if "ghost-iron" in i.key.lower()), None)
            if not lantern:
                caller.msg("The dancing blue spirit fire slips through your fingers! You need a ghost-iron lantern to trap it.")
                return

            lantern.delete()
            blazing = create_object(
                Object,
                key="Blazing Wisp Lantern",
                location=caller,
                aliases=["lantern", "wisp lantern", "blazing lantern"],
                tags=["eldoria_world"]
            )
            blazing.db.desc = "A filigreed lantern glowing with an eternal, captured blue spirit fire. It cuts through dark fog and illusions."

            caller.msg(
                "|cYou sweep the Empty Ghost-Iron Lantern through the air, scooping up the dancing will-o'-the-wisp! "
                "The door snaps shut, and the lantern blazes with an unearthly sapphire radiance!|n"
            )
            caller.location.msg_contents(
                f"{caller.key} traps a dancing will-o'-the-wisp inside a ghost-iron lantern!",
                exclude=[caller]
            )
            return

        # Capture moonbeam in twilight glade
        if "moonbeam" in target or "moonlight" in target:
            if "glade" not in caller.location.key.lower():
                caller.msg("There are no pooled moonbeams here to capture.")
                return

            phial = create_object(
                Object,
                key="Crystal Phial of Liquid Moonlight",
                location=caller,
                aliases=["phial", "moonlight", "liquid moonlight"],
                tags=["eldoria_world"]
            )
            phial.db.desc = "A shimmering crystal phial swirling with captured silver moonlight. Dispels dark illusions."
            caller.db.captured_moonbeam = True

            caller.msg(
                "|wYou uncork an empty crystal phial and hold it up beneath the silver canopy. "
                "A pool of liquid moonlight swirls into the vessel, bathing your hands in cool, celestial light!|n"
            )
            caller.location.msg_contents(
                f"{caller.key} bottles a swirl of pure liquid moonlight into a crystal phial!",
                exclude=[caller]
            )
            return

        caller.msg(f"You cannot catch {self.args.strip()}.")


class CmdTurn(default_cmds.MuxCommand):
    """
    Turn a valve wheel or mechanism

    Usage:
      turn <wheel/valve>
    """

    key = "turn"
    aliases = ["rotate", "spin"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to turn?")
            return

        target = self.args.strip().lower()

        # Sewer valve in ancient cistern / sluice
        if any(w in target for w in ["valve", "wheel", "sluice"]):
            if "cistern" in caller.location.key.lower() or "sluice" in caller.location.key.lower():
                caller.db.turned_sewer_valve = True
                caller.msg(
                    "|yYou grip the heavy iron wheel and heave with all your might! With a deafening groan of rusted gears, "
                    "the sluice gate lifts, draining the foul wastewater and revealing the ancient cistern floor!|n"
                )
                caller.location.msg_contents(
                    f"{caller.key} turns the massive iron sluice wheel! Rushing water drains away into the deep!",
                    exclude=[caller]
                )
                return
            elif "valve" in caller.location.key.lower() or "steam" in caller.location.key.lower() or "forge" in caller.location.key.lower():
                caller.db.vented_steam = True
                caller.msg(
                    "|rYou wrench the brass geothermal pressure valve open! A deafening *HISSSS* of white steam vents into "
                    "the molten cavern, cooling the foundry boilers to safe operating levels!|n"
                )
                caller.location.msg_contents(
                    f"{caller.key} vents the geothermal steam pressure valve! Hissing vapor billows upward!",
                    exclude=[caller]
                )
                return

        caller.msg(f"You cannot turn {self.args.strip()}.")


class CmdMine(default_cmds.MuxCommand):
    """
    Mine ore veins in caves and mines

    Usage:
      mine <ore/vein>
    """

    key = "mine"
    aliases = ["dig", "excavate"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        has_pick = any("pick" in i.key.lower() for i in caller.contents)

        if not has_pick:
            caller.msg("You need a heavy mining pickaxe to mine mineral veins!")
            return

        if "forge" not in caller.location.key.lower() and "hub" not in caller.location.key.lower() and "chasm" not in caller.location.key.lower():
            caller.msg("There are no rich mineral veins to mine here.")
            return

        caller.db.mined_mithril = True
        ore = create_object(
            Object,
            key="Chunk of Pure Mithril Ore",
            location=caller,
            aliases=["mithril", "ore", "mithril ore"],
            tags=["eldoria_world"]
        )
        ore.db.desc = "A brilliant fist-sized chunk of glowing silver-blue mithril ore, lightweight yet stronger than steel."

        caller.msg(
            "|c*CLANG! CLANG!* You swing the pickaxe into the glittering rock face! A dazzling chunk of "
            "Pure Mithril Ore fractures free and falls into your hands!|n"
        )
        caller.location.msg_contents(
            f"{caller.key} strikes the rock face with a pickaxe and frees a glowing chunk of Mithril Ore!",
            exclude=[caller]
        )


class CmdCleanse(default_cmds.MuxCommand):
    """
    Cleanse diseased roots or ancient altars

    Usage:
      cleanse <target>
    """

    key = "cleanse"
    aliases = ["purify", "heal"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to cleanse?")
            return

        target = self.args.strip().lower()

        if any(w in target for w in ["tree", "roots", "oakhaven", "treant"]):
            if "elder" not in caller.location.key.lower() and "willow" not in caller.location.key.lower() and "glade" not in caller.location.key.lower():
                caller.msg("There is no blighted tree here to cleanse.")
                return

            caller.db.cleansed_treant = True
            caller.msg(
                "|gYou pour consecrated dawn water over the weeping willow's twisted roots! The black fungal rot hisses and dissolves "
                "into harmless dew. Fresh green leaves burst along the branches as Oakhaven groans in deep gratitude!|n"
            )
            caller.location.msg_contents(
                f"{caller.key} cleanses the roots of the ancient tree with consecrated water! Fresh emerald blossoms erupt!",
                exclude=[caller]
            )
            return

        caller.msg(f"You cannot cleanse {self.args.strip()}.")


class CmdInsert(default_cmds.MuxCommand):
    """
    Insert fuel cores or key components into machines

    Usage:
      insert <item> into <target>
      reboot <target>
    """

    key = "insert"
    aliases = ["reboot", "install"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        has_core = any("core" in i.key.lower() for i in caller.contents)

        if not has_core:
            caller.msg("You do not have a Pneumatic Steam Core to insert!")
            return

        if "assembly" not in caller.location.key.lower() and "automaton" not in caller.location.key.lower():
            caller.msg("There is no dormant machinery here to power up.")
            return

        core = next((i for i in caller.contents if "core" in i.key.lower()), None)
        if core:
            core.delete()

        caller.db.awakened_cog = True
        caller.msg(
            "|yYou slide the glowing Pneumatic Steam Core into Unit 7-B's brass chest compartment! "
            "Pneumatic pistons hiss to life, brass gears spin rapidly, and two warm amber optic lenses flicker awake! "
            "Cog is online!|n"
        )
        caller.location.msg_contents(
            f"{caller.key} inserts a steam core into Unit 7-B! The brass automaton whirs to life!",
            exclude=[caller]
        )



class CmdFish(default_cmds.MuxCommand):
    """
    Cast your fishing rod into a body of water

    Usage:
      fish
      cast
    """

    key = "fish"
    aliases = ["cast"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        location = caller.location

        rod = next((i for i in caller.contents if any(k in i.key.lower() for k in ["rod", "pole"])), None)
        if not rod:
            caller.msg("You need a fishing rod in your inventory to fish! (Look around the harbor docks)")
            return

        from world.fishing import get_room_biome
        biome = get_room_biome(location)
        if not biome:
            caller.msg("There is no body of water here to cast your line into!")
            return

        bait = next((i for i in caller.contents if any(k in i.key.lower() for k in ["worm", "beetle", "grub", "squid", "breadcrumb"])), None)
        bait_str = f" baited with {bait.key}" if bait else " (unbaited)"

        caller.ndb.fishing_active = True
        caller.ndb.fishing_rod = rod
        caller.ndb.fishing_bait = bait

        caller.msg(
            f"|cYou whip back your {rod.key}{bait_str} and cast your line out into the {biome} waters! "
            "Your painted float bobs peacefully on the ripples...|n"
        )
        location.msg_contents(
            f"{caller.key} casts a fishing line out into the water.",
            exclude=[caller]
        )

        caller.msg(
            "|y*SPLASH!* The float violently dips beneath the surface! Something is tugging on the line! "
            "Quick, use: |wreel|n!|n"
        )


class CmdReel(default_cmds.MuxCommand):
    """
    Reel in your fishing line to catch fish

    Usage:
      reel
    """

    key = "reel"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        location = caller.location

        if not caller.ndb.fishing_active:
            caller.msg("You haven't cast your line yet! Use: fish or cast")
            return

        rod = caller.ndb.fishing_rod
        bait = caller.ndb.fishing_bait
        caller.ndb.fishing_active = False

        from world.fishing import catch_fish
        item, tier = catch_fish(caller, location, rod=rod, bait=bait)

        if bait and bait.location == caller:
            bait.delete()
            caller.msg("|x(Your bait was consumed in the catch.)|n")

        if not item:
            caller.msg("You reel in your empty hook with a splash.")
            return

        if tier == "rare":
            color = "|Y"
            caller.msg(f"{color}*** TROPHY CATCH! *** You strain against your rod and haul up a magnificent {item.key}!|n")
        elif tier == "uncommon":
            color = "|g"
            caller.msg(f"{color}You reel in with steady hands! With a bright splash, you land a {item.key}!|n")
        elif tier == "junk":
            color = "|w"
            caller.msg(f"{color}You tug the line and haul up a waterlogged {item.key}!|n")
        else:
            color = "|c"
            caller.msg(f"{color}You reel in smoothly, landing a fresh {item.key}!|n")

        location.msg_contents(
            f"{caller.key} reels in a splashing catch from the water: {item.key}!",
            exclude=[caller]
        )


class CmdCook(default_cmds.MuxCommand):
    """
    Cook freshly caught fish over a hearth or fire

    Usage:
      cook <fish>
      fry <fish>
      grill <fish>
    """

    key = "cook"
    aliases = ["fry", "grill"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What do you want to cook?")
            return

        location = caller.location
        loc_key = location.key.lower()
        has_fire = any(w in loc_key for w in ["tavern", "forge", "hearth", "fire", "camp", "cave", "marshland"])
        has_torch = any("torch" in i.key.lower() for i in caller.contents)

        if not has_fire and not has_torch:
            caller.msg("You need to be near a cooking fire, hearth, forge, or hold a torch to cook!")
            return

        fish_item = caller.search(self.args.strip(), location=caller)
        if not fish_item:
            return

        if not fish_item.db.cookable and "fish" not in fish_item.key.lower():
            caller.msg(f"You cannot cook {fish_item.key}!")
            return

        raw_name = fish_item.db.raw_fish_name or fish_item.key.split("(")[0].strip()
        fish_item.delete()

        cooked = create_object(
            Object,
            key=f"Crispy Pan-Fried {raw_name}",
            location=caller,
            aliases=["fish", "cooked fish", "food", raw_name.lower()],
            tags=["eldoria_world"]
        )
        cooked.db.desc = f"A golden-brown, crispy grilled {raw_name} seasoned with wild herbs. Smells delicious! Use: drink (or eat)"
        cooked.db.is_drinkable = True
        cooked.db.drink_type = "food"

        caller.msg(
            f"|yYou sizzle the fresh {raw_name} over the hot coals! The skin crisps to a mouthwatering golden brown! "
            f"You now have a {cooked.key}!|n"
        )
        location.msg_contents(
            f"{caller.key} cooks a fresh fish over the fire, filling the air with a savory aroma!",
            exclude=[caller]
        )


class CmdMapper(default_cmds.MuxCommand):
    """
    Toggle automapper assistance mode (Room IDs, strict exits, telemetry)

    Usage:
      mapper
      mapper on
      mapper off
      roomid [on|off]
    """
    key = "mapper"
    aliases = ["roomid", "automap"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        curr_state = bool(caller.db.mapper_mode)

        if not self.args:
            status = "|gENABLED|n" if curr_state else "|rDISABLED|n"
            caller.msg(f"\nAutomapper Mode is currently {status}.")
            caller.msg("GMCP Room.Info out-of-band telemetry is |gALWAYS ACTIVE|n for modern clients (Mudlet/TinTin++).")
            caller.msg("To toggle on-screen Room IDs and telemetry: |wmapper on|n or |wmapper off|n\n")
            return

        arg = self.args.strip().lower()
        if arg in ["on", "enable", "yes", "true"]:
            caller.db.mapper_mode = True
            caller.msg("\n|gAutomapper Mode ENABLED!|n")
            caller.msg("Room IDs, machine-parseable exits, and telemetry headers are now active on your display.")
            caller.msg("Your MUD client's automapper will now be able to distinguish every room uniquely.\n")
            if caller.location:
                caller.msg(caller.location.return_appearance(caller))
        elif arg in ["off", "disable", "no", "false"]:
            caller.db.mapper_mode = False
            caller.msg("\n|yAutomapper Mode DISABLED.|n Default immersive text view restored.\n")
            if caller.location:
                caller.msg(caller.location.return_appearance(caller))
        else:
            caller.msg("Usage: mapper on | mapper off")
