"""
Keeps track of flow breakers on an ast node.

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

class BreakMarker(basic.BasicMarker):
    """Marks and shows markings for flow breaking nodes."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "breaks", node)

    def get_default(self):
        """Get the default value for this marking."""

        return set()

    def duplicate(self):
        return self.get_mark().copy()

    def canBreak(self):
        """Check if the node can break from normal flow. Use safe default if unsure."""

        if not self.is_marked():
            return True

        return bool(self.get_mark()) # True if there are some

    def addBreak(self, type):
        """Add a possible break from normal flow. Return whether we were successful."""

        if type not in ["except", "return", "break", "continue", "yield"]:
            return False

        breakers = self.get_mark()
        breakers.add(type)
        return self.set_mark(breakers)

    def removeBreak(self, type):
        """Remove a break type from the possibilities. Return whether we were successful."""

        if type not in ["except", "return", "break", "continue", "yield"]:
            return False

        breakers = self.get_mark()
        try:
            breakers.remove(type)
        except KeyError:
            pass
        return self.set_mark(breakers)
