"""
Alchemy brewing and cooking commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_alchemy_cooking import brew_potion, cook_meat, eat_ration, RECIPES


class CmdBrew(default_cmds.MuxCommand):
    """
    Brew an alchemical potion or elixir from harvested herbs

    Usage:
      brew
      brew <healing/mana/antidote/stoneskin>
    """
    key = "brew"
    aliases = ["alchemy"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("\n|w====================== ALCHEMY RECIPES ======================|n")
            caller.msg(f"{'Recipe':<14} {'Herb Reagents':<22} {'Result'}")
            caller.msg("|b" + "-" * 65 + "|n")
            for r_k, data in RECIPES.items():
                reqs = ", ".join(data["req"])
                caller.msg(f"|y{r_k:<14}|n |c{reqs:<22}|n |w{data['name']}|n")
                caller.msg(f"   |xEffect:|n {data['desc']}")
            caller.msg("|w" + "=" * 65 + "|n\n")
            caller.msg("To brew a potion: |wbrew <recipe_name>|n\n")
            return

        ok, msg = brew_potion(caller, self.args.strip())
        if not ok:
            caller.msg(msg)


class CmdCookFood(default_cmds.MuxCommand):
    """
    Cook raw butchered monster meat over a campfire

    Usage:
      cook <meat_item>
    """
    key = "cookfood"
    aliases = ["roast"]
    locks = "cmd:all()"
    help_category = "Crafting"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("What meat do you want to cook?")
            return

        meat = caller.search(self.args.strip(), location=caller)
        if not meat:
            return

        ok, msg = cook_meat(caller, meat)
        if not ok:
            caller.msg(msg)


class CmdEat(default_cmds.MuxCommand):
    """
    Eat cooked rations to restore Stamina, HP, and gain a nourishment buff

    Usage:
      eat <food_item>
    """
    key = "eat"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Eat what?")
            return

        food = caller.search(self.args.strip(), location=caller)
        if not food:
            return

        ok, msg = eat_ration(caller, food)
        if not ok:
            caller.msg(msg)

