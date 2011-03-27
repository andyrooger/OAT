"""
Keeps track of scopes of variables this ast node accesses.

"""

from . import basic

class ScopeMarker(basic.BasicMarker):
    """Marks and shows markings for node's variable scope."""

    def __init__(self, node):
        basic.BasicMarker.__init__(self, "scope", node)

    def scopes(self):
        """Get a dictionary of the scope of variables the node accesses. Use safe default if unsure."""

        return self._get_mark({})

    def _add_variable(self, variable, type):
        """Add variable scope to our node. Return whether we were successful."""
        
        marks = self.scopes()
        marks[variable] = type
        return self._set_mark(marks)

    def clear(self):
        """Clear the known variables."""

        self._set_mark({})

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

        marks = self.scopes()
        try:
            del marks[variable]
        except KeyError:
            pass

        return self._set_mark(marks)

    def getScope(self, variable):
        """Get the scope for a variable."""

        return self.scopes().get(variable, "unknown")
