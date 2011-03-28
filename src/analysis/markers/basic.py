"""
Basic functions that a marker should do.

"""

import ast
import abc

class BasicMarker(metaclass=abc.ABCMeta):
    def __init__(self,
                 mark : "Name of the marking",
                 node : "Node to mark" = None):
        self.mark = mark
        if node == None:
            self.node = DummyAST() # Dummy
        else:
            self.node = node

    def supports_markings(self):
        """Check if our node supports markings."""

        return isinstance(self.node, ast.AST)

    def has_markings(self):
        """Check if our node has markings."""

        return hasattr(self.node, "_markings")

    def _get_markings(self, create : "Should we add markings if possible?" = False):
        """Get markings if the node has them, or None."""

        if not self.supports_markings():
            return None

        if self.has_markings():
            return self.node._markings
        elif create:
            self.node._markings = {}
            return self.node._markings
        else:
            return None

    def is_marked(self):
        """Check if the node contains this type of marking."""

        marks = self._get_markings()
        return marks != None and self.mark in marks

    def get_mark(self):
        """Get the value of our marking, or the default."""

        marks = self._get_markings()
        if marks == None:
            return self.get_default()

        return marks.get(self.mark, self.get_default())

    def set_mark(self, val):
        """Set the value of our marking."""

        if self.supports_markings():
            self._get_markings(True)[self.mark] = val
            return True
        else:
            return False

    @abc.abstractmethod
    def get_default(self):
        """Get the default value for this marking."""

    def detach(self):
        """Detach the current marker from its node, duplicating necessary data."""

        data = self.duplicate()
        self.node = DummyAST()
        self.set_mark(data)

    @abc.abstractmethod
    def duplicate(self):
        """Returns identical to get_mark() but separate objects."""

class DummyAST(ast.AST): pass
