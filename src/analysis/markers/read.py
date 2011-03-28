"""
Keeps track of names this ast node reads.

"""

from . import basic

class ReadMarker(basic.BasicMarker):
    """Marks and shows markings for node reads."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "reads", node)

    def get_default(self):
        """Get the default value for this marking."""

        return set()

    def duplicate(self):
        return self.get_mark().copy()

    def addVariable(self, variable):
        """Add read variable to our node. Return whether we were successful."""
        
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
