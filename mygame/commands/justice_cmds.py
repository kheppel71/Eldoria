"""
Justice, Bounty & Law Enforcement Commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_justice import (
    BOUNTIES, init_justice_character, place_bounty, pay_bail,
    release_prisoner, arrest_criminal
)


class CmdBounties(default_cmds.MuxCommand):
    """
    View the realm's active wanted list and bounties

    Usage:
      bounties
    """
    key = "bounties"
    aliases = ["wanted"]
    locks = "cmd:all()"
    help_category = "Justice"

    def func(self):
        caller = self.caller

        if not BOUNTIES:
            caller.msg("\n|gThere are currently no active bounties on record in Sigil. Peace reigns.|n\n")
            return

        caller.msg("\n|r=========================== REALM WANTED LIST ===========================|n")
        caller.msg(f"{'Outlaw Name':<20} {'Bounty (Gold)':<16} {'Recent Infractions'}")
        caller.msg("|r" + "-" * 74 + "|n")

        for char_id, data in sorted(BOUNTIES.items(), key=lambda x: x[1]["bounty"], reverse=True):
            crimes_str = ", ".join(data.get("crimes", [])) or "Disturbing the Peace"
            caller.msg(f"|w{data['name']:<20}|n |y{data['bounty']:<16}|n |r{crimes_str}|n")

        caller.msg("|r" + "-" * 74 + "|n")
        caller.msg("Bring outlaws to justice to collect rewards at the Courthouse.\n")


class CmdBounty(default_cmds.MuxCommand):
    """
    Place a bounty on a wanted criminal

    Usage:
      bounty <target> <gold_amount>
    """
    key = "bounty"
    locks = "cmd:all()"
    help_category = "Justice"

    def func(self):
        caller = self.caller
        if not self.args or len(self.args.split()) < 2:
            caller.msg("Usage: bounty <target> <gold_amount>")
            return

        parts = self.args.split()
        target_name = parts[0]
        try:
            amount = int(parts[1])
            if amount <= 0:
                caller.msg("Bounty amount must be greater than 0.")
                return
        except ValueError:
            caller.msg("Gold amount must be a number.")
            return

        target = caller.search(target_name)
        if not target:
            return

        ok, msg = place_bounty(caller, target, amount)
        caller.msg(msg)


class CmdSurrender(default_cmds.MuxCommand):
    """
    Surrender peacefully to the City Watch or authorities

    Usage:
      surrender
    """
    key = "surrender"
    locks = "cmd:all()"
    help_category = "Justice"

    def func(self):
        caller = self.caller
        init_justice_character(caller)

        if not caller.db.is_outlaw:
            caller.msg("You are a law-abiding citizen with no criminal charges. There is nothing to surrender to.")
            return

        if getattr(caller.db, "is_jailed", False):
            caller.msg("You are already locked in the stockades.")
            return

        caller.msg("|yYou drop your weapons, raise your hands, and surrender to the City Watch.|n")
        if caller.location:
            caller.location.msg_contents(
                f"{caller.key} raises their hands and yields unconditionally to the authorities.",
                exclude=[caller]
            )

        # Incarcerate with reduced sentence for cooperating (30 seconds)
        arrest_criminal(None, caller, sentence_seconds=30)


class CmdBail(default_cmds.MuxCommand):
    """
    Pay bail to release an imprisoned criminal from the stockades

    Usage:
      bail <prisoner>
    """
    key = "bail"
    locks = "cmd:all()"
    help_category = "Justice"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Usage: bail <prisoner>")
            return

        target = caller.search(self.args.strip())
        if not target:
            return

        ok, msg = pay_bail(caller, target)
        caller.msg(msg)


class CmdServeTime(default_cmds.MuxCommand):
    """
    Serve time on your jail sentence or inspect remaining imprisonment

    Usage:
      serve
    """
    key = "serve"
    locks = "cmd:all()"
    help_category = "Justice"

    def func(self):
        caller = self.caller
        init_justice_character(caller)

        if not getattr(caller.db, "is_jailed", False):
            caller.msg("You are not imprisoned.")
            return

        rem = caller.db.jail_time or 0
        if rem <= 0:
            caller.msg("|gYour sentence has been served! The stockade keeper unlocks your cell.|n")
            release_prisoner(caller, pardon=True)
            return

        # Advance time by 10s upon deliberate reflection
        rem = max(0, rem - 10)
        caller.db.jail_time = rem

        if rem == 0:
            caller.msg("|gYou reflect solemnly on your crimes as the final minutes pass. Time served!|n")
            release_prisoner(caller, pardon=True)
        else:
            caller.msg(f"|yYou sit on the cold stone floor of the stockade. Remaining sentence: {rem} seconds.|n")


class CmdCriminalRecord(default_cmds.MuxCommand):
    """
    Inspect your criminal record and outlaw standing

    Usage:
      record
      crimes
    """
    key = "record"
    aliases = ["crimes"]
    locks = "cmd:all()"
    help_category = "Justice"

    def func(self):
        caller = self.caller
        init_justice_character(caller)

        status = "|r[OUTLAW - WANTED]|n" if caller.db.is_outlaw else "|g[LAW-ABIDING CITIZEN]|n"
        bounty = caller.db.bounty or 0
        crimes = caller.db.crimes or []

        caller.msg(f"\n|w=== Criminal Record for {caller.key} ===|n")
        caller.msg(f"Status: {status}    Active Bounty: |y{bounty} Gold|n")
        caller.msg(f"Incarcerated: {'|rYES|n' if caller.db.is_jailed else '|gNO|n'}\n")

        if crimes:
            caller.msg("|wPast Recorded Infractions:|n")
            for c in crimes[-5:]:
                caller.msg(f"  - |r{c['crime']}|n against |w{c['victim']}|n (+{c['bounty']} Gold)")
        else:
            caller.msg("No infractions on record.")
        caller.msg("|w" + "=" * 40 + "|n\n")

