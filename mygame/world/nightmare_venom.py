"""
Nightmare LPmud Venom Milking, Toxic Brewing & Antidotes Engine.

Implements:
1. Subdued creature venom milking ('milkvenom <creature>'):
   - Pit Viper Neuro-Toxin
   - Shadow Spider Paralyzing Venom
   - Desert Scorpion Toxin
2. Apothecary Antidote brewing ('brewantidote') utilizing activated charcoal.
3. Antidote administration ('applyantidote [target]') purging poison debuffs.
"""

from evennia.utils.create import create_object
from typeclasses.objects import Object

VENOM_TYPES = {
    "viper": {
        "name": "Phial of Pit Viper Venom",
        "power": 20,
        "antidote_name": "Serpentine Anti-Venom Serum",
        "desc": "A clear, straw-colored liquid extracted from the fangs of a subterranean pit viper."
    },
    "spider": {
        "name": "Phial of Shadow Spider Neurotoxin",
        "power": 25,
        "antidote_name": "Arachnid Neural Tonic",
        "desc": "A thick, luminescent purple venom harvested from the pedipalps of a cave-weaver spider."
    },
    "scorpion": {
        "name": "Phial of Desert Scorpion Toxin",
        "power": 30,
        "antidote_name": "Universal Charcoal Theriac",
        "desc": "A stinging amber venom milked from the barbed stinger of a desert emperor scorpion."
    }
}


def milk_creature_venom(caller, creature_name="viper"):
    """Milks venom from a subdued serpent or arachnid into a glass phial."""
    key = creature_name.strip().lower()
    matched = next((k for k in VENOM_TYPES if key in k), "viper")
    data = VENOM_TYPES[matched]

    phial = create_object(Object, key=data["name"], location=caller)
    phial.db.is_venom = True
    phial.db.venom_type = matched
    phial.db.potency = data["power"]
    phial.db.desc = data["desc"]

    caller.msg(
        f"\n|Y[VENOM EXTRACTION]|n Pinning the venomous creature behind its jaws with wooden tongs,\n"
        f"you press its fangs over the rubber membrane of an extraction vial.\n"
        f"Viscous venom drips forth, filling a |w{phial.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} expertly milks venom from a creature into a laboratory glass phial.",
            exclude=[caller]
        )
    return True, f"Milked {phial.key}."


def brew_antidote_serum(caller):
    """Brews an effective anti-venom serum from raw venom and activated charcoal."""
    venom = None
    for obj in caller.contents:
        if getattr(obj.db, "is_venom", False) or "venom" in obj.key.lower():
            venom = obj
            break

    if not venom:
        return False, "You need a phial of raw venom to distill into an anti-venom antidote! ('milkvenom')"

    vtype = getattr(venom.db, "venom_type", "viper")
    data = VENOM_TYPES.get(vtype, VENOM_TYPES["viper"])
    venom.delete()

    antidote = create_object(Object, key=data["antidote_name"], location=caller)
    antidote.db.is_antidote = True
    antidote.db.desc = f"A carefully distilled medicinal serum that completely neutralizes {data['name']}."

    caller.msg(
        f"\n|G[APOTHECARY BREWING]|n You precipitate the venom proteins over activated charcoal and pure spring water,\n"
        f"distilling a life-saving |w{antidote.key}|n!\n"
    )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} blends reagents over a spirit burner, formulating a bottle of {antidote.key}.",
            exclude=[caller]
        )
    return True, f"Brewed {antidote.key}."


def apply_antidote(caller, target_char=None):
    """Administers an antidote to cure poison and restore health."""
    target = target_char if target_char else caller

    antidote = None
    for obj in caller.contents:
        if getattr(obj.db, "is_antidote", False) or "antidote" in obj.key.lower() or "serum" in obj.key.lower():
            antidote = obj
            break

    if not antidote:
        return False, "You do not have any antidote or serum bottles in your pack! ('brewantidote')"

    aname = antidote.key
    antidote.delete()

    target.db.is_poisoned = False
    curr_hp = getattr(target.db, "hp", 100) or 100
    max_hp = getattr(target.db, "max_hp", 100) or 100
    target.db.hp = min(max_hp, curr_hp + 25)

    caller.msg(
        f"\n|G[ANTIDOTE ADMINISTERED]|n You administer {aname} to {target.key}.\n"
        "The burning toxins in the bloodstream dissolve, restoring normal color to the skin (+25 HP, Poison Cured)!\n"
    )
    if target != caller:
        target.msg(
            f"\n|G{caller.key} administers a potent dose of {aname}! The venom burning through your veins fades completely!|n\n"
        )
    if caller.location:
        caller.location.msg_contents(
            f"{caller.key} administers a healing anti-venom serum to {target.key}, neutralizing the circulating poison.",
            exclude=[caller, target]
        )
    return True, "Antidote applied."

