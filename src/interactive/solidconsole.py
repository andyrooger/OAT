#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

from . import commandui

from . import parsecmd
from . import formatcmd
from . import explorecmd

class SolidConsole(commandui.CommandUI):
    """Solid command class."""

    def __init__(self):
        commandui.CommandUI.__init__(self)

        parse = parsecmd.ParseCommand()
        explore = explorecmd.ExploreCommand(parse)
        format = formatcmd.FormatCommand(explore)
        self.add_command(parse)
        self.add_command(format)
        self.add_command(explore)

