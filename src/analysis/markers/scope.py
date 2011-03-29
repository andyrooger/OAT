"""
Keeps track of scopes markings inside this node.

"""

from . import basic

class ScopeMarker(basic.BasicMarker):
    """Marks and shows markings for node's scope modifiers."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "scope", node)

    def get_default(self):
        """Get the default value for this marking."""

        return {}

    def duplicate(self):
        return self.get_mark().copy()

    def _add_variable(self, variable, type):
        """Add variable scope to our node. Return whether we were successful."""
        
        marks = self.get_mark()
        marks[variable] = type
        return self.set_mark(marks)

    def addNonlocal(self, variable):
        """Add a non-local variable."""

        return self._add_variable(variable, "nonlocal")

    def addGlobal(self, variable):
        """Add a global variable."""

        return self._add_variable(variable, "global")

    def remove(self, variable):
        """Remove a variable from the set."""

        marks = self.get_mark()
        try:
            del marks[variable]
        except KeyError:
            pass

        return self.set_mark(marks)

    def getScope(self, variable):
        """Get the scope for a variable."""

        return self.get_mark().get(variable, None)
