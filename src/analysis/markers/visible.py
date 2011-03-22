"""
Keeps track of visible markings on an ast node.

"""

from . import basic

class VisibleMarker(BasicMarker):
    """Marks and shows markings for node visibility."""

    def __init__(self, node):
        BasicMarker.__init__(self, "visible", node)

    def isVisible(self):
        """Check if the node is visible. Use safe default if unsure."""

        return self._get_mark(True)

    def setVisible(self, visible):
        """Set visibility on our node. Return whether we were successful."""

        if self.supports_markings():
            self._set_mark(visible)
            return True

        return False
