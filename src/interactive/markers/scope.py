"""
Marker plugin for variable scope.

"""

from analysis.markers import scope
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Choose all the variables this node reads. Use (g|n|l|r)-varname to add a global, nonlocal or local or remove a variable."""

    def parameters(self):
        return {
            "nargs": "+",
            "metavar": "VAR"
        }

    def update(self, node, arg):
        marker = scope.ScopeMarker(node)
        return self._alter_vars(marker, arg)

    def show(self, node, title):
        marker = scope.ScopeMarker(node)

        if marker.is_marked():
            vars = marker.scopes()
            print(title + ":" + ("" if vars else " Empty"))

            for var in vars:
                print("   - " + var + " (" + vars[var] + ")")

    def _alter_vars(self, marker, changes):
        """
        Parse the function references from the command line and alter the current node.

        Returns whether the alteration was successful.

        Uses format (g|n|l|r)-varname.

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
                    "l": marker.addLocal,
                    "n": marker.addNonlocal,
                    "g": marker.addGlobal,
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
