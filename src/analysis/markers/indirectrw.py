"""
Keeps track of indirect accesses of names, those accessed in an enclosed scope.

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

class IndirectRWMarker(basic.BasicMarker):
    """Marks and shows markings for node's indirect accesses."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "indirectrw", node)

    def get_default(self):
        """Get the default value for this marking."""

        return {}

    def duplicate(self):
        return self.get_mark().copy()

    def getVariable(self, name, scope):
        """Get a tuple (read, write) containing whether the given variable it read or written. None is used if we don't know."""

        m = self.get_mark()
        try:
            return m[(name, scope)]
        except KeyError:
            return (False, False)

    def _add_variable(self, name, scope, *, read=None, write=None):
        """Add variable ref to our node. Return whether we were successful."""
        
        marks = self.get_mark()
        p_r, p_w = self.getVariable(name, scope)
        if read != None:
            p_r = read
        if write != None:
            p_w = write
        marks[(name, scope)] = (p_r, p_w)
        return self.set_mark(marks)

    def addFree(self, name, **kwargs):
        """Add a free variable."""

        return self._add_variable(name, "free", **kwargs)

    def addNonlocal(self, name, **kwargs):
        """Add a non-local variable."""

        return self._add_variable(name, "nonlocal", **kwargs)

    def addGlobal(self, name, **kwargs):
        """Add a global variable."""

        return self._add_variable(name, "global", **kwargs)
