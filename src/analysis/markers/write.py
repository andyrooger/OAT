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

        return self._get_mark({})

    def _add_variable(self, variable, type):
        """Add written variable to our node. Return whether we were successful."""
        
        marks = self.writes()
        marks[variable] = type
        return self._set_mark(marks)

    def clear(self):
        """Clear the known variables."""

        self._set_mark({})

    def addUnknown(self, variable):
        """Add a variable of unknown scope."""

        return self._add_variable(variable, "unknown")

    def addLocal(self, variable):
        """Add a local variable."""

        return self._add_variable(variable, "local")

    def addNonlocal(self, variable):
        """Add a non-local variable."""

        return self._add_variable(variable, "nonlocal")

    def addGlobal(self, variable):
        """Add a global variable."""

        return self._add_variable(variable, "global")

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.writes()

        try:
            del marks[variable]
        except KeyError:
            pass

        return self._set_mark(marks)
