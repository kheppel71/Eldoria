"""
Bardic performance and singing commands for Nightmare LPmud.
"""

from evennia import default_cmds
from world.nightmare_bard import play_instrument, sing_bardic_song, SONGS


class CmdPlayInstrument(default_cmds.MuxCommand):
    """
    Play a musical instrument in your hands or pack

    Usage:
      play <instrument>
    """
    key = "play"
    locks = "cmd:all()"
    help_category = "General"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("Play what instrument?")
            return

        instrument = caller.search(self.args.strip(), location=caller)
        if not instrument:
            return

        ok, msg = play_instrument(caller, instrument)


class CmdSingSong(default_cmds.MuxCommand):
    """
    Sing an enchanting bardic melody to bolster allies or soothe beasts

    Usage:
      sing
      sing <vitality/valor/lullaby>
    """
    key = "sing"
    aliases = ["ballad", "chant"]
    locks = "cmd:all()"
    help_category = "Magic"

    def func(self):
        caller = self.caller
        if not self.args:
            caller.msg("\n|w====================== BARDIC REPERTOIRE ======================|n")
            caller.msg(f"{'Song':<16} {'Cost':<14} {'Description'}")
            caller.msg("|b" + "-" * 65 + "|n")
            for s_k, data in SONGS.items():
                caller.msg(f"|y{s_k:<16}|n |w{data['stamina_cost']} Stamina|n   {data['desc']}")
            caller.msg("|w" + "=" * 65 + "|n")
            caller.msg("To sing: |wsing <song_name>|n\n")
            return

        ok, msg = sing_bardic_song(caller, self.args.strip())
        if not ok:
            caller.msg(msg)

