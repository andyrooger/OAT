"""
Marker plugin for read variables.

"""

from analysis.markers import read
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Choose all the variables this node reads. Use a(g|n|l|u)-variable to add or r-variable to remove a global, nonlocal, local, or unknown variable."""

    def parameters(self):
        return {
            "nargs": "+",
            "metavar": "VAR"
        }

    def update(self, node, arg):
        marker = self._get_marker(node)
        return self._alter_vars(marker, arg)

    def show(self, node, title):
        marker = self._get_marker(node)

        if marker.is_marked():
            vars = self._get_dict(marker)
            print(title + ":" + ("" if vars else " Empty"))

            for var in vars:
                print("   - " + var + " (" + vars[var] + ")")

    def _get_marker(self, node):
        """Get the marker for this type of mark."""
        return read.ReadMarker(node)

    def _get_dict(self, marker):
        return marker.reads()

    def _alter_vars(self, marker, changes):
        """
        Parse the function references from the command line and alter the current node.

        Returns whether the alteration was successful.

        Uses format (a(g|n|l|u)|r)-variable.

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
                    "au": marker.addUnknown,
                    "al": marker.addLocal,
                    "an": marker.addNonlocal,
                    "ag": marker.addGlobal,
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
