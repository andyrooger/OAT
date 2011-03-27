"""
Keeps track of names this ast node writes to.

"""

from . import basic

class WriteMarker(basic.BasicMarker):
    """Marks and shows markings for node writes."""

    def __init__(self, node):
        basic.BasicMarker.__init__(self, "writes", node)

    def writes(self):
        """Get a dictionary of the variables the node writes. Use safe default if unsure."""

        return self._get_mark(set())

    def addVariable(self, variable):
        """Add written variable to our node. Return whether we were successful."""
        
        marks = self.writes()
        marks.add(variable)
        return self._set_mark(marks)

    def clear(self):
        """Clear the known variables."""

        self._set_mark(set())

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.writes()
        try:
            marks.remove(variable)
        except KeyError:
            pass

        return self._set_mark(marks)
