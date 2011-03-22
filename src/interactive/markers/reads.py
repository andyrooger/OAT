"""
Marker plugin for read variables.

"""

from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Choose all the variables this node reads. Use a(g|n|l|u)-variable to add or r-variable to remove a global, nonlocal, local, or unknown variable."""

    def parameters(self):
        return {
            "nargs": "+",
            "metavar": "VAR"
        }

    def addCommand(self, args):
        """Add a command to the argument parser given for this marking."""

    def marked(self, node):
        """Returns whether or not a node has been marked."""

    def update(self, node, opts):
        """Update the markings based on the given options."""

    def show(self, node):
        """Print information about this type of marking."""

