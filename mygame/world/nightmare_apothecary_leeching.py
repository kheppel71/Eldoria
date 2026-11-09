"""
Nightmare LPmud Barber-Surgeon Leeching, Bloodletting & Humors Engine.

Implements:
1. Four Bodily Humors Inspection ('humors'):
   - Sanguine (Blood & vitality)
   - Choleric (Yellow bile & fever)
   - Phlegmatic (Mucus & chills)
   - Melancholic (Black bile & gloom)
2. Medicinal Leech Therapy ('applyleeches') to purge venom, sepsis, and rot.
3. Lancet Bloodletting ('bloodlet') to break burning fevers.
4. Fresh Leech Jar Gathering ('jarleeches').
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object


def inspect_humors(caller, target_char=None):
    """Diagnoses the balance of the four bodily humors."""
    target = target_char if target_char else caller
    hp = getattr(target.db, "hp", 100) or 100
    max_hp = getattr(target.db, "max_hp", 100) or 100
    hp_pct = int((hp / max_hp) * 100)

    sanguine = "Balanced & Warm" if hp_pct > 70 else "Depleted & Pale"
    choleric = "Excessive & Feverish" if hp_pct < 50 else "Temperate"
    phlegmatic = "Calm"
    melancholic = "Clear"

    lines = [
        "|c" + "=" * 65 + "|n",
        f"|w               HUMORAL MEDICAL DIAGNOSIS: {target.key.upper()} |n",
        "|c" + "=" * 65 + "|n",
        f" |rSanguine (Blood):|n        {sanguine}",
        f" |yCholeric (Yellow Bile):|n  {choleric}",
        f" |wPhlegmatic (Lymph):|n      {phlegmatic}",
        f" |bMelancholic (Black Bile):|n {melancholic}",
        "|c" + "-" * 65 + "|n",
        "|xPrescription: Apply medicinal leeches ('applyleeches') or lancet ('bloodlet').|n",
        "|c" + "=" * 65 + "|n"
    ]
    return "\n".join(lines)


def gather_medicinal_leeches(caller):
    """Collects a jar of hungry medicinal swamp leeches."""
    jar = create_object(Object, key="Glass Jar of Medicinal Leeches", location=caller)
    jar.db.is_leech_jar = True
    jar.db.leech_count = 5
    jar.db.desc = "A sealed glass jar filled with brackish pond water and squirming, black medicinal leeches."

    caller.msg("\n|G[LEECH GATHERING]|n You skim the reed shallows, collecting a |wGlass Jar of Medicinal Leeches|G!|n\n")
    return True, "Leeches gathered."


def apply_medicinal_leeches(caller, target_char=None):
    """Places medicinal leeches on the target to suck out corrupt toxins and venom."""
    target = target_char if target_char else caller

    # Look for leech jar
    jar = None
    for obj in caller.contents:
        if getattr(obj.db, "is_leech_jar", False) or "leeches" in obj.key.lower():
            jar = obj
            break

    if not jar:
        return False, "You need a Glass Jar of Medicinal Leeches in your pack! Gather one with 'jarleeches'."

    target.db.is_poisoned = False

    curr_hp = getattr(target.db, "hp", 100) or 100
    max_hp = getattr(target.db, "max_hp", 100) or 100
    target.db.hp = min(max_hp, curr_hp + 15)

    caller.msg(
        f"\n|Y[BARBER-SURGEON THERAPY]|n You uncap the jar and place fat, hungry leeches along {target.key}'s forearm.\n"
        f"The leeches swell, drawing out dark foul blood and neutralizing circulating venom (+15 HP, Poison Cleansed)!|n\n"
    )
    if target != caller:
        target.msg(
            f"\n|g{caller.key} applies therapeutic freshwater leeches to your arm, drawing out necrotic blood and fever!|n\n"
        )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} performs medicinal leeching on {target.key}, drawing out dark toxins.",
            exclude=[caller, target]
        )
    return True, "Leeches applied."


def perform_lancet_bloodletting(caller, target_char=None):
    """Uses a sharp lancet to perform controlled bloodletting, breaking burning fevers."""
    target = target_char if target_char else caller

    curr_hp = getattr(target.db, "hp", 100) or 100
    max_hp = getattr(target.db, "max_hp", 100) or 100
    target.db.hp = min(max_hp, curr_hp + 20)

    caller.msg(
        f"\n|Y[LANCET BLOODLETTING]|n With steady surgeon's hand, you make a swift nick into {target.key}'s median vein.\n"
        f"Foul choleric humors escape into a pewter basin. {target.key}'s fever breaks instantly (+20 HP)!|n\n"
    )
    if target != caller:
        target.msg(
            f"\n|w{caller.key} makes a precise lancet incision. The hot pressure behind your temples subsides as your fever breaks!|n\n"
        )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} performs a swift lancet incision on {target.key}, relieving internal fever pressure.",
            exclude=[caller, target]
        )
    return True, "Bloodletting performed."

