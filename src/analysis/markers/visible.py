"""
Keeps track of visible markings on an ast node.

"""

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
