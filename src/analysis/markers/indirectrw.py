"""
Keeps track of indirect accesses of names, those accessed in an enclosed scope.

"""

from . import basic

class IndirectRWMarker(basic.BasicMarker):
    """Marks and shows markings for node's indirect accesses."""

    def __init__(self, node = None):
        basic.BasicMarker.__init__(self, "indirectrw", node)

    def get_default(self):
        """Get the default value for this marking."""

        return {}

    def duplicate(self):
        return self.get_mark().copy()

    def getVariable(self, name, scope):
        """Get a tuple (read, write) containing whether the given variable it read or written. None is used if we don't know."""

        m = self.get_mark()
        try:
            return m[(name, scope)]
        except KeyError:
            return (None, None)

    def _add_variable(self, name, scope, *, read=None, write=None):
        """Add variable ref to our node. Return whether we were successful."""
        
        marks = self.get_mark()
        p_r, p_w = self.getVariable(name, scope)
        if read != None:
            p_r = read
        if write != None:
            p_w = write
        marks[(name, scope)] = (p_r, p_w)
        return self.set_mark(marks)

    def removeName(self, name, scope):
        marks = self.get_mark()
        try:
            del marks[(name, scope)]
        except KeyError:
            pass
        return self.set_mark(marks)

    def addFree(self, name, **kwargs):
        """Add a free variable."""

        return self._add_variable(name, "free", **kwargs)

    def addNonlocal(self, name, **kwargs):
        """Add a non-local variable."""

        return self._add_variable(name, "nonlocal", **kwargs)

    def addGlobal(self, name, **kwargs):
        """Add a global variable."""

        return self._add_variable(name, "global", **kwargs)
