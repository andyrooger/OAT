"""
Basic functions that a marker should do.

"""

import ast

class BasicMarker():
    def __init__(self, mark : "Name of the marking", node : "Node to mark"):
        self.node = node
        self.mark = mark

    def supports_markings(self):
        """Check if our node supports markings."""

        return isinstance(self.node, ast.AST)

    def has_markings(self):
        """Check if our node has markings."""

        return self._get_markings() != None

    def _get_markings(self, create : "Should we add markings if possible?" = False):
        """Get markings if the node has them, or None."""

        if not self.supports_markings():
            return None

        try:
            return self.node._markings
        except AttributeError:
            if create:
                self.node._markings = {}
                return self.node._markings
            else:
                return None

    def is_marked(self):
        """Check if the node contains this type of marking."""

        marks = self._get_markings()
        return marks != None and self.mark in marks

    def _get_mark(self, default=None):
        """Get the value of our marking, or the default."""

        marks = self._get_markings()
        if marks == None:
            return default

        return marks.get(self.mark, default)

    def _set_mark(self, val):
        """Set the value of our marking."""

        self._get_markings(True)[self.mark] = val
