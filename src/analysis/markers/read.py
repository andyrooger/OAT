"""
Keeps track of names this ast node reads.

"""

from . import basic

class ReadMarker(BasicMarker):
    """Marks and shows markings for node reads."""

    def __init__(self, node):
        BasicMarker.__init__(self, "reads", node)

    def reads(self):
        """Get a dictionary of the variables the node reads. Use safe default if unsure."""

        return self._get_mark({})

    def _add_variable(self, variable, type):
        """Add read variable to our node. Return whether we were successful."""
        
        marks = self._get_markings(True)
        if marks == None:
            return False

        marks[variable] = type
        return self._set_mark(marks)
    

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

        marks = self._get_markings(True)
        if marks == None:
            return False

        try:
            del marks[variable]
        except KeyError:
            pass

        return self._set_mark(marks)