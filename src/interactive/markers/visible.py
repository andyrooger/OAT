"""
Marker plugin for visibility.

"""

from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Is this a visible or invisible statement? (i.e. does it perform actions visible to the outside world?"""

    def parameters(self):
        return {
            "choices": ["invisible", "visible"]
        }

    def addCommand(self, args):
        """Add a command to the argument parser given for this marking."""

    def marked(self, node):
        """Returns whether or not a node has been marked."""

    def update(self, node, opts):
        """Update the markings based on the given options."""

    def show(self, node):
        """Print information about this type of marking."""

