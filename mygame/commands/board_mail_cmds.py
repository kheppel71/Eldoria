"""
Bulletin board and courier mail commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_boards_mail import (
    get_room_board, post_to_board, read_board_note, remove_board_note,
    init_mailbox, send_mail
)


class CmdBulletinBoard(default_cmds.MuxCommand):
    """
    Interact with the room's persistent bulletin board

    Usage:
      board
      board read <note_id>
      board post <subject>=<message>
      board remove <note_id>
    """
    key = "board"
    aliases = ["notes", "bulletin"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller
        loc = caller.location
        if not loc:
            return

        if not self.args:
            board = get_room_board(loc)
            caller.msg(f"\n|w===================== BULLETIN BOARD: {loc.key} =====================|n")
            if not board:
                caller.msg("The board is currently empty. Pin a notice with: |wboard post <subject>=<msg>|n")
            else:
                caller.msg(f"{'#':<4} {'Date':<18} {'Author':<16} {'Subject'}")
                caller.msg("|b" + "-" * 72 + "|n")
                for n in board:
                    caller.msg(f"|y{n['id']:<4}|n {n['date']:<18} |c{n['author']:<16}|n |w{n['subject']}|n")
            caller.msg("|w" + "=" * 72 + "|n\n")
            return

        parts = self.args.strip().split(None, 1)
        subcmd = parts[0].lower()
        subarg = parts[1].strip() if len(parts) > 1 else ""

        if subcmd == "read":
            try:
                n_id = int(subarg)
            except ValueError:
                caller.msg("Specify note number (e.g. board read 1).")
                return

            note = read_board_note(loc, n_id)
            if not note:
                caller.msg(f"Notice #{n_id} not found.")
                return

            caller.msg(f"\n|w=== Notice #{note['id']}: {note['subject']} ===|n")
            caller.msg(f"Author: |c{note['author']}|n    Date: |y{note['date']}|n\n")
            caller.msg(note["message"])
            caller.msg("\n|w" + "=" * 40 + "|n\n")

        elif subcmd == "post":
            if "=" not in subarg:
                caller.msg("Usage: board post <subject>=<message>")
                return
            subj, msg = subarg.split("=", 1)
            ok, feedback = post_to_board(loc, caller.key, subj, msg)
            caller.msg(feedback)

        elif subcmd == "remove":
            try:
                n_id = int(subarg)
            except ValueError:
                caller.msg("Specify note number (e.g. board remove 1).")
                return
            ok, feedback = remove_board_note(loc, n_id, caller)
            caller.msg(feedback)

        else:
            caller.msg(f"Unknown board option '{subcmd}'. Type 'board' for notice list.")


class CmdMail(default_cmds.MuxCommand):
    """
    Dispatch a letter via city courier to another player

    Usage:
      mail <recipient>=<subject>/<message>
      mail <recipient>=<subject>/<message>/<gold_coins>
    """
    key = "mail"
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller
        if not self.args or "=" not in self.args:
            caller.msg("Usage: mail <recipient>=<subject>/<message>[/<gold>]")
            return

        recip_name, rest = self.args.split("=", 1)
        target = caller.search(recip_name.strip())
        if not target:
            return

        parts = rest.split("/")
        if len(parts) < 2:
            caller.msg("Usage: mail <recipient>=<subject>/<message>[/<gold>]")
            return

        subj = parts[0].strip()
        body = parts[1].strip()
        gold = 0
        if len(parts) >= 3:
            try:
                gold = int(parts[2].strip())
            except ValueError:
                gold = 0

        ok, msg = send_mail(caller, target, subj, body, gold)
        caller.msg(msg)


class CmdMailbox(default_cmds.MuxCommand):
    """
    Inspect your personal mailbox and read delivered courier letters

    Usage:
      mailbox
      mailbox read <letter_id>
      mailbox claim <letter_id>
    """
    key = "mailbox"
    aliases = ["inbox"]
    locks = "cmd:all()"
    help_category = "Communication"

    def func(self):
        caller = self.caller
        init_mailbox(caller)
        mbox = caller.db.mailbox or []

        if not self.args:
            caller.msg(f"\n|w========================= COURIER MAILBOX =========================|n")
            if not mbox:
                caller.msg("Your mailbox is empty.")
            else:
                caller.msg(f"{'#':<4} {'Status':<10} {'Date':<18} {'From':<16} {'Subject'}")
                caller.msg("|b" + "-" * 70 + "|n")
                for m in mbox:
                    st = "|gNEW|n" if not m.get("read") else "|xRead|n"
                    gold_tag = f" |y(+{m['enclosed_gold']}g)|n" if m.get("enclosed_gold") else ""
                    caller.msg(f"|y{m['id']:<4}|n {st:<10} {m['date']:<18} |c{m['from']:<16}|n |w{m['subject']}|n{gold_tag}")
            caller.msg("|w" + "=" * 70 + "|n\n")
            return

        parts = self.args.strip().split(None, 1)
        subcmd = parts[0].lower()
        subarg = parts[1].strip() if len(parts) > 1 else ""

        if subcmd == "read":
            try:
                m_id = int(subarg)
            except ValueError:
                caller.msg("Specify letter number (e.g. mailbox read 1).")
                return

            letter = next((l for l in mbox if l["id"] == m_id), None)
            if not letter:
                caller.msg(f"Letter #{m_id} not found.")
                return

            letter["read"] = True
            caller.msg(f"\n|w=== Letter #{letter['id']}: {letter['subject']} ===|n")
            caller.msg(f"From: |c{letter['from']}|n    Date: |y{letter['date']}|n")
            if letter.get("enclosed_gold", 0) > 0:
                caller.msg(f"Enclosed Coins: |y{letter['enclosed_gold']} Gold|n (Use: |wmailbox claim {m_id}|n)")
            caller.msg(f"\n{letter['body']}\n")
            caller.msg("|w" + "=" * 40 + "|n\n")

        elif subcmd == "claim":
            try:
                m_id = int(subarg)
            except ValueError:
                caller.msg("Specify letter number to claim coins from.")
                return

            letter = next((l for l in mbox if l["id"] == m_id), None)
            if not letter:
                caller.msg(f"Letter #{m_id} not found.")
                return

            gold = letter.get("enclosed_gold", 0)
            if gold <= 0:
                caller.msg("There are no enclosed coins in this letter.")
                return

            coins = caller.db.coins or {"gold": 0, "silver": 0, "copper": 0}
            coins["gold"] = coins.get("gold", 0) + gold
            caller.db.coins = coins
            letter["enclosed_gold"] = 0

            caller.msg(f"|yYou open the wax seal and claim {gold} enclosed Gold coins! (Pocket: {coins['gold']}g)|n")
