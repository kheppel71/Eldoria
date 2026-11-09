"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """

    def at_post_move(self, source_location, **kwargs):
        """
        Hook called after this object has moved to a new location.
        Automatically disengages from combat if moving away.
        """
        super().at_post_move(source_location, **kwargs)
        if getattr(self.db, "is_resting", False):
            self.db.is_resting = False
            self.msg("|yYou stand up as you move.|n")

        target = getattr(self.ndb, "combat_target", None)
        if target:
            from world.nightmare_core import disengage_combat
            disengage_combat(self, target)
            self.msg("|yYou have moved away from the battle. Combat disengaged.|n")
            if hasattr(target, "msg"):
                target.msg(f"|y{self.key} has left the area. Combat disengaged.|n")
