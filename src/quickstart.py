#!/usr/bin/env python3

"""
Just starts my preferred UI from a
sensible place.

"""

from interactive.solidconsole import SolidConsole

def go(intro = None):
    try:
        SolidConsole().cmdloop(intro)
    except KeyboardInterrupt:
        print()
        go("")


if __name__ == "__main__":
    go()
