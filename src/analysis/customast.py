"""
Creates a custom version of the built in AST.

This should provide extra functionality to make certain things simpler.

"""

import ast

class CustomAST:
    """Wrapper for the built in AST."""

    def __init__(self, node):
        self._node = node
        self._gen_children()

    def type(self, asclass=False):
        """
        Get the type of node as a string.

        This could be an AST type or list or None.
        Can return actual class instead if we set asclass to true.

        """

        cls = self._node.__class__
        return cls if asclass else asclass.__name__

    def is_ast(self):
        """Is the node a normal AST node."""

        return issubclass(self.type(asclass=True), ast.AST)

    def is_empty(self):
        """Is the node empty (None)."""

        return self.type(asclass=True) == None

    def _gen_children(self):
        """
        Generate children from current node.

        This takes children, assigns labels to them and fills our child dict.

        """

        self.children = {}
        t = self.type(asclass=True):
        if issubclass(t, ast.AST):
            # Then we have an AST node
            self.children = {
                field: CustomAST(getattr(self._node, field))
                for field in self._node._fields
            }

        elif issubclass(t, list):
            # We have a list of nodes
            self.children = {
                str(idx): self._node[idx]
                for idx in range(len(self._node))
            }

        elif self._node == None:
            pass # We have an empty node

        else:
            raise TypeError("Not a recognised node type.")
