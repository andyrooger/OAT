"""
Keeps track of names this ast node reads.

"""

from . import basic

class ReadMarker(basic.BasicMarker):
    """Marks and shows markings for node reads."""

    def __init__(self, node):
        basic.BasicMarker.__init__(self, "reads", node)

    def reads(self):
        """Get a dictionary of the variables the node reads. Use safe default if unsure."""

        return self._get_mark(set())

    def addVariable(self, variable):
        """Add read variable to our node. Return whether we were successful."""
        
        marks = self.reads()
        marks.add(variable)
        return self._set_mark(marks)

    def clear(self):
        """Clear the known variables."""

        self._set_mark(set())

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.reads()
        try:
            marks.remove(variable)
        except KeyError:
            pass

        return self._set_mark(marks)
