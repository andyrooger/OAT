"""
Command based UI for the obfuscator.

"""

from . import commandui

from . import parsecmd
from . import formatcmd
from . import explorecmd
from . import reordercmd
from . import markcmd
from . import visualisecmd

class SolidConsole(commandui.CommandUI):
    """Solid command class."""

    def __init__(self):
        commandui.CommandUI.__init__(self)

        parse = parsecmd.ParseCommand()
        explore = explorecmd.ExploreCommand(parse)
        format = formatcmd.FormatCommand(parse, explore)
        reorder = reordercmd.ReorderCommand(parse, explore)
        mark = markcmd.MarkCommand(parse, explore)
        visualise = visualisecmd.VisualiseCommand(explore)
        self.add_command(parse)
        self.add_command(format)
        self.add_command(explore)
        self.add_command(reorder)
        self.add_command(mark)
        self.add_command(visualise)
