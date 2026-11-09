"""
Nightmare LPmud Illusionism, Mirror Images & Phantasms Engine.

Implements:
1. Shimmering Mirror Image conjuration ('mirrorimage'):
   - Conjures 3 illusory duplicate images that absorb incoming physical strikes.
2. Phantasmal Horror casting ('phantasm <target>'):
   - Wreathes enemy minds in nightmarish apparitions, draining morale and inflicting terror.
3. Dispel Illusion perception rites ('dispelillusion'):
   - Shatters visual glamours and duplicate phantoms.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def cast_mirror_images(caller):
    """Conjures 3 shimmering mirror duplicates of the caster."""
    mana = getattr(caller.db, "mana", 100) or 100
    if mana < 20:
        return False, "You lack sufficient mana to weave mirror duplicates! (Requires 20 Mana)"

    caller.db.mana = mana - 20
    caller.db.mirror_images = 3

    caller.msg(
        "\n|C[ILLUSION - MIRROR IMAGE]|n You weave refractive light and arcane glamours!\n"
        "|wThree identical shimmering doppelgangers step forth from your silhouette,\n"
        "circling around you in perfect synchronization! (3 Images Active)|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"|C{caller.key}'s form blurs as three identical shimmering mirror duplicates split outward from them!|n",
            exclude=[caller]
        )
    return True, "Mirror images conjured."


def absorb_strike_with_mirror(target_char):
    """Checks if an incoming attack is absorbed by an active mirror image."""
    images = getattr(target_char.db, "mirror_images", 0) or 0
    if images <= 0:
        return False

    target_char.db.mirror_images = images - 1
    remaining = images - 1

    target_char.msg(
        f"\n|C*SHATTER!* The enemy's blow strikes an illusory duplicate!|n\n"
        f"The mirror image shatters into harmless sparkling light crystals! ({remaining} images remain)\n"
    )
    if target_char.location:
        target_char.location.msg_contents(
            f"|CThe strike passes harmlessly through a mirror image of {target_char.key}, popping it into crystal dust!|n",
            exclude=[target_char]
        )
    return True


def cast_phantasmal_terror(caller, target_char):
    """Projects waking nightmarish horrors into a victim's mind."""
    if not target_char:
        return False, "Who do you wish to afflict with phantasmal terror?"

    mana = getattr(caller.db, "mana", 100) or 100
    if mana < 25:
        return False, "You need 25 Mana to project phantasms into enemy consciousness."

    caller.db.mana = mana - 25
    target_char.db.is_terrified = True

    caller.msg(
        f"\n|M[PHANTASMAL TERROR]|n You pierce the veil of {target_char.key}'s subconscious!\n"
        f"Unspeakable chittering shadows and eldritch horrors swarm their vision!\n"
    )
    target_char.msg(
        f"\n|R[MIND INVASION]|n {caller.key}'s eyes glow with hypnotic violet flame!\n"
        "|rMonstrous slithering tentacles and weeping faces erupt from the shadows around you! You recoil in terror!|n\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"|mViolet psionic embers drift from {caller.key}'s brow as {target_char.key} recoils in waking terror!|n",
            exclude=[caller, target_char]
        )
    return True, f"Afflicted {target_char.key} with phantasms."


def dispel_illusions(caller, target_char=None):
    """Pierces and cleanses active visual glamours and duplicate images."""
    target = target_char if target_char else caller
    had_images = (getattr(target.db, "mirror_images", 0) or 0) > 0
    had_terror = bool(getattr(target.db, "is_terrified", False))

    if not had_images and not had_terror:
        return False, f"There are no active illusions or phantasms enveloping {target.key}."

    target.db.mirror_images = 0
    target.db.is_terrified = False

    caller.msg(
        f"\n|W[DISPEL ILLUSION]|n You invoke the cleansing truth of pure perception!\n"
        f"All false glamours, mirror duplicates, and waking horrors around {target.key} dissolve into clear air!|n\n"
    )
    if target != caller:
        target.msg(f"\n|W{caller.key} dispels the mental falsehoods and false images shrouding your vision!|n\n")

    if caller.location:
        caller.location.msg_contents(
            f"|WA wave of translucent light washes out from {caller.key}, banishing all active optical illusions!|n",
            exclude=[caller, target]
        )
    return True, "Illusions dispelled."
