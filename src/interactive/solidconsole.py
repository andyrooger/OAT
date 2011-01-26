#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

from . import commandui

from . import parsecmd
from . import formatcmd

class SolidConsole(commandui.CommandUI):
    """Solid command class."""

    def __init__(self):
        commandui.CommandUI.__init__(self)

        self.add_command(parsecmd.ParseCommand())
        self.add_command(formatcmd.FormatCommand())

