"""
Marker plugin for read variables.

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

from analysis.markers import write
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Choose all the variables this node writes. Use (a|r)-variable to add or remove a variable."""

    def parameters(self):
        return {
            "nargs": "+",
            "metavar": "VAR"
        }

    def translate(self, node, arg):
        marker = write.WriteMarker(node)
        marker.detach()
        self._alter_vars(marker, arg)
        return marker.get_mark()

    def update(self, node, trans):
        return write.WriteMarker(node).set_mark(trans)

    def show(self, node, title):
        marker = write.WriteMarker(node)

        if marker.is_marked():
            vars = marker.get_mark()
            print(title + ("" if vars else "Empty"))

            for var in vars:
                print("   - " + var)

    def _alter_vars(self, marker, changes):
        """
        Parse the function references from the command line and alter the current marker.

        Returns whether the alteration was successful.

        Uses format (a|r)-variable.

        """

        successful_change = False

        for change in changes:
            try:
                action, var = change.split("-", 1)
            except ValueError:
                # Not enough parts (no '-')
                print("Missing action: " + change)
                continue

            if not action:
                raise ValueError("Change should not start with '-', EVER!")

            try:
                act = {
                    "a": marker.addVariable,
                    "r": marker.remove
                }[action]
            except KeyError:
                print("Unrecognised action: " + action + " in " + change)
                continue
            else:
                if act(var):
                    successful_change = True
                else:
                    print("Could not perform change: " + change)

        return successful_change
