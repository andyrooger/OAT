"""
Keeps track of flow breakers on an ast node.

"""

from . import basic

class BreakMarker(basic.BasicMarker):
    """Marks and shows markings for flow breaking nodes."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "breaks", node)

    def get_default(self):
        """Get the default value for this marking."""

        return set()

    def duplicate(self):
        return self.get_mark().copy()

    def canBreak(self):
        """Check if the node can break from normal flow. Use safe default if unsure."""

        if not self.is_marked():
            return True

        return bool(self.get_mark()) # True if there are some

    def addBreak(self, type):
        """Add a possible break from normal flow. Return whether we were successful."""

        if type not in ["except", "return", "break", "continue", "yield"]:
            return False

        breakers = self.get_mark()
        breakers.add(type)
        return self.set_mark(breakers)

    def removeBreak(self, type):
        """Remove a break type from the possibilities. Return whether we were successful."""

        if type not in ["except", "return", "break", "continue", "yield"]:
            return False

        breakers = self.get_mark()
        try:
            breakers.remove(type)
        except KeyError:
            pass
        return self.set_mark(breakers)
