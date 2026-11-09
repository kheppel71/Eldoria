"""
Tavern drinking and intoxication commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_intoxication import consume_tavern_drink, DRINKS


class CmdOrderDrink(default_cmds.MuxCommand):
    """
    Order a drink from the tavern barkeep

    Usage:
      drink
      drink menu
      order <stout/whiskey/mead/wine/coffee>
    """
    key = "order"
    aliases = ["orderdrink", "quaff"]
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args or self.args.strip() in ["menu", "drinks"]:
            caller.msg("\n|w===================== TAVERN DRINK MENU =====================|n")
            caller.msg(f"{'Drink':<18} {'Cost (Silver)':<16} {'Proof':<10} {'Description'}")
            caller.msg("|b" + "-" * 72 + "|n")
            for d_k, data in DRINKS.items():
                p_str = f"+{data['proof']}%" if data['proof'] > 0 else f"{data['proof']}%"
                caller.msg(f"|y{data['name']:<18}|n |w{data['cost']} Silver|n        |c{p_str:<10}|n {data['desc']}")
            caller.msg("|w" + "=" * 72 + "|n")
            caller.msg("To purchase: |worder <drink_name>|n\n")
            return

        ok, msg = consume_tavern_drink(caller, self.args.strip())
        if not ok:
            caller.msg(msg)


class CmdIntoxication(default_cmds.MuxCommand):
    """
    Check your current state of sobriety and drunkenness

    Usage:
      intoxication
      sobriety
    """
    key = "intoxication"
    aliases = ["sobriety"]
    locks = "cmd:all()"
    help_category = "Character"

    def func(self):
        caller = self.caller
        intox = getattr(caller.db, "intoxication", 0) or 0

        if intox >= 90:
            stage = "|RDead Drunk / Passing Out|n"
            desc = "You can barely keep your eyes open. The floor is looking very comfortable."
        elif intox >= 60:
            stage = "|rHeavily Intoxicated (Wasted)|n"
            desc = "Liquid courage pulses through you (+15% Damage Absorption). You sway and slur your speech."
        elif intox >= 30:
            stage = "|yBuzzed & Tipsy|n"
            desc = "A pleasant, warm numbness buzzes in your limbs. Speech is slightly slurred."
        else:
            stage = "|gStone Cold Sober|n"
            desc = "Your thoughts are clear and your reflexes sharp."

        caller.msg(f"\n|w=== Sobriety Assessment ===|n")
        caller.msg(f"Level: |c{intox}%|n - Status: {stage}")
        caller.msg(f"{desc}\n|w" + "=" * 28 + "|n\n")


class CmdSober(default_cmds.MuxCommand):
    """
    Drink bitter black coffee to quickly sober up

    Usage:
      sober
    """
    key = "sober"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        consume_tavern_drink(caller, "coffee")

