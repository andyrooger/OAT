"""
Command based UI for the obfuscator.

"""

# OAT - Obfuscation and Analysis Tool
# Copyright (C) 2011  Andy Gurden
# 
#     This file is part of OAT.
# 
#     OAT is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     OAT is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with OAT.  If not, see <http://www.gnu.org/licenses/>.

from . import commandui

from . import parsecmd
from . import formatcmd
from . import explorecmd
from . import reordercmd
from . import markcmd
from . import visualisecmd
from . import branchcmd

class SolidConsole(commandui.CommandUI):
    """Solid command class."""

    def __init__(self):
        commandui.CommandUI.__init__(self)

        parse = parsecmd.ParseCommand()
        explore = explorecmd.ExploreCommand(parse)
        format = formatcmd.FormatCommand(parse, explore)
        reorder = reordercmd.ReorderCommand(parse, explore)
        mark = markcmd.MarkCommand(parse, explore)
        visualise = visualisecmd.VisualiseCommand(parse, explore)
        branch = branchcmd.BranchCommand(parse, explore)
        self.add_command(parse)
        self.add_command(format)
        self.add_command(explore)
        self.add_command(reorder)
        self.add_command(mark)
        self.add_command(visualise)
        self.add_command(branch)
