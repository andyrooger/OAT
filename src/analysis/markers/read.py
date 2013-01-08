"""
Keeps track of names this ast node reads.

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

from . import basic

class ReadMarker(basic.BasicMarker):
    """Marks and shows markings for node reads."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "reads", node)

    def get_default(self):
        """Get the default value for this marking."""

        return set()

    def duplicate(self):
        return self.get_mark().copy()

    def addVariable(self, variable):
        """Add read variable to our node. Return whether we were successful."""
        
        marks = self.get_mark()
        marks.add(variable)
        return self.set_mark(marks)

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.get_mark()
        try:
            marks.remove(variable)
        except KeyError:
            pass

        return self.set_mark(marks)
