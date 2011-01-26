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

        parse = parsecmd.ParseCommand()
        format = formatcmd.FormatCommand(parse)
        self.add_command(parse)
        self.add_command(format)

