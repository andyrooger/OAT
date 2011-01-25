#!/usr/bin/env python3

"""
Just starts my preferred UI from a
sensible place.

"""

from interactive.commandui import CommandUI

try:
    CommandUI().cmdloop()
except KeyboardInterrupt:
    print("Please close with EOF or the quit command next time.")
