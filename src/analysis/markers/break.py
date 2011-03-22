"""
Keeps track of flow breakers on an ast node.

"""

from . import basic

class BreakMarker(BasicMarker):
    """Marks and shows markings for flow breaking nodes."""

    def __init__(self, node):
        BasicMarker.__init__(self, "breaks", node)

    def canBreak(self):
        """Check if the node can break from normal flow. Use safe default if unsure."""

        return self._get_mark(True)

    def setBreaks(self, breaks):
        """Set whether this node can break from normal flow. Return whether we were successful."""

        if self.supports_markings():
            self._set_mark(breaks)
            return True

        return False
