"""
Keeps track of visible markings on an ast node.

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

class VisibleMarker(basic.BasicMarker):
    """Marks and shows markings for node visibility."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "visible", node)

    def get_default(self):
        """Get the default value for this marking."""

        return True

    def duplicate(self):
        return self.get_mark()

    def isVisible(self):
        """Check if the node is visible. Use safe default if unsure."""

        return self.get_mark()

    def setVisible(self, visible):
        """Set visibility on our node. Return whether we were successful."""

        return self.set_mark(visible)
