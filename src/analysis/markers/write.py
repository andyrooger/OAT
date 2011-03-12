"""
Keeps track of names this ast node writes to.

"""

from . import basic

class WriteMarker(basic.BasicMarker):
    """Marks and shows markings for node writes."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "writes", node)

    def get_default(self):
        """Get the default value for this marking."""

        return set()

    def duplicate(self):
        return self.get_mark().copy()

    def addVariable(self, variable):
        """Add written variable to our node. Return whether we were successful."""
        
        marks = self.get_mark()
        marks.add(variable)
        return self.set_mark(marks)

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.get_mark()
        try:
            marks.remove(variable)
        except KeyError:
            pass

        return self.set_mark(marks)
