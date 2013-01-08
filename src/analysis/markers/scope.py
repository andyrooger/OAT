"""
Keeps track of scopes markings inside this node.

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

class ScopeMarker(basic.BasicMarker):
    """Marks and shows markings for node's scope modifiers."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "scope", node)

    def get_default(self):
        """Get the default value for this marking."""

        return {}

    def duplicate(self):
        return self.get_mark().copy()

    def _add_variable(self, variable, type):
        """Add variable scope to our node. Return whether we were successful."""
        
        marks = self.get_mark()
        marks[variable] = type
        return self.set_mark(marks)

    def addNonlocal(self, variable):
        """Add a non-local variable."""

        return self._add_variable(variable, "nonlocal")

    def addGlobal(self, variable):
        """Add a global variable."""

        return self._add_variable(variable, "global")

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.get_mark()
        try:
            del marks[variable]
        except KeyError:
            pass

        return self.set_mark(marks)

    def getScope(self, variable):
        """Get the scope for a variable."""

        return self.get_mark().get(variable, None)
