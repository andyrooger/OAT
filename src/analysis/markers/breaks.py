"""
Keeps track of flow breakers on an ast node.

"""

from . import basic

class BreakMarker(basic.BasicMarker):
    """Marks and shows markings for flow breaking nodes."""

    def __init__(self, node):
        basic.BasicMarker.__init__(self, "breaks", node)

    def breakers(self):
        """Grab a list of the types of breakers."""

        return self._get_mark(set())

    def canBreak(self):
        """Check if the node can break from normal flow. Use safe default if unsure."""

        breakers = self._get_mark(None)
        if breakers == None:
            return True

        return bool(breakers) # True if there are some

    def clearBreaks(self):
        """Clear all types of break."""

        self._set_mark(set())
        return True

    def addBreak(self, type):
        """Add a possible break from normal flow. Return whether we were successful."""

        if type not in ["except", "return", "break", "continue", "yield"]:
            return False

        if not self.supports_markings():
            return False

        breakers = self.breakers()
        breakers.add(type)
        self._set_mark(breakers)
        return True

    def removeBreak(self, type):
        """Remove a break type from the possibilities. Return whether we were successful."""

        if type not in ["except", "return", "break", "continue", "yield"]:
            return False

        if not self.supports_markings():
            return False

        breakers = self.breakers()
        try:
            breakers.remove(type)
        except KeyError:
            pass
        self._set_mark(breakers)
        return True
