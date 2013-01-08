"""
Marker plugin for variable scope.

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

from analysis.markers import indirectrw
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Choose names this node indirectly accesses. This includes reading/writing of any names in an enclosed scope that are not local. They should be labelled with their scope modifier from the enclosed scope. Use ((r|nr)|(w|nw))-(g|n|f)-varname to set read/not read or write/not write a global, nonlocal or free name."""

    def parameters(self):
        return {
            "nargs": "+",
            "metavar": "VAR"
        }


    def translate(self, node, arg):
        marker = indirectrw.IndirectRWMarker(node)
        marker.detach()
        self._alter_vars(marker, arg)
        return marker.get_mark()

    def update(self, node, trans):
        return indirectrw.IndirectRWMarker(node).set_mark(trans)

    def show(self, node, title):
        marker = indirectrw.IndirectRWMarker(node)

        if marker.is_marked():
            vars = marker.get_mark()
            print(title + ("" if vars else "Empty"))

            for (n, s) in vars:
                print("   - " + n + " (" + s + " ", end="")
                r, w = vars[(n,s)]
                if r:
                    print("r", end="")
                if w:
                    print("w", end="")
                print(")")

    def _alter_vars(self, marker, changes):
        """
        Parse the function references from the command line and alter the current marker.

        Returns whether the alteration was successful.

        Uses format ((r|nr)|(w|nw))-(g|n|f)-varname.

        """

        successful_change = False

        for change in changes:
            try:
                action, scope, var = change.split("-", 2)
            except ValueError:
                print("Missing action or scope: " + change)
                continue

            if not action:
                raise ValueError("Change should not start with '-', EVER!")

            try:
                act = {
                    "f": marker.addFree,
                    "n": marker.addNonlocal,
                    "g": marker.addGlobal,
                }[scope]
            except KeyError:
                print("Unrecognised scope: " + scope + " in " + change)
                continue

            successful_change_part = False
            if action == "r":
                if act(var, read=True):
                    successful_change_part = True
            elif action == "nr":
                if act(var, read=False):
                    successful_change_part = True
            elif action == "w":
                if act(var, write=True):
                    successful_change_part = True
            elif action == "nw":
                if act(var, write=False):
                    successful_change_part = True
            else:
                print("Unrecognised change: " + action)
                continue

            if successful_change_part:
                successful_change = True
            else:
                print("Could not perform change: " + change)

        return successful_change
