# pylint: disable=no-member
"""This file will shows the game."""

import curses
from curses import wrapper

try: # We all know why
    from . import prepare, displayer
except ImportError:
    import prepare
    import displayer

def main(stdscr: curses.window):
    """The main function, this will shows the game."""
    assert curses.LINES >= 24 and curses.COLS >= 80, "The terminal size is unvalid."

    # Prepare scene
    prepare.prepare_i18n()
    displayer.init_screen(stdscr)

    displayer.end_screen()

wrapper(main)
