"""
Marker plugin for flow breaking statements.

"""

from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Can this statement break from a linear flow?"""

    def parameters(self):
        return {
            "choices": ["yes", "no"]
        }

    def addCommand(self, args):
        """Add a command to the argument parser given for this marking."""

    def marked(self, node):
        """Returns whether or not a node has been marked."""

    def update(self, node, opts):
        """Update the markings based on the given options."""

    def show(self, node):
        """Print information about this type of marking."""

