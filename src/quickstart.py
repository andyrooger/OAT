#!/usr/bin/env python3

"""
Just starts my preferred UI from a
sensible place.

"""

from interactive.commandui import CommandUI

def go(intro = None):
    try:
        CommandUI().cmdloop(intro)
    except KeyboardInterrupt:
        print()
        go("")


if __name__ == "__main__":
    go()
