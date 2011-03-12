"""
Marker plugin for variable scope.

"""

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
