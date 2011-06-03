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
        return cls if asclass else cls.__name__

    def node(self):
        """Return the actual node."""

        return self._node

    def is_ast(self):
        """Is the node a normal AST node."""

        return issubclass(self.type(asclass=True), ast.AST)

    def is_basic(self):
        """Is the node a basic type."""

        if issubclass(self.type(asclass=True), str):
            return True
        if issubclass(self.type(asclass=True), int):
            return True
        if issubclass(self.type(asclass=True), float):
            return True
        if issubclass(self.type(asclass=True), bytes):
            return True
        return False

    def is_list(self):
        """Is this node a list."""

        return issubclass(self.type(asclass=True), list)

    def is_empty(self):
        """Is the node empty (None or [])."""

        return self._node == None or (self.is_list() and not self.node())

    def temp_list(self, *vargs, flattenlists=True):
        """
        Create a temporary list node starting with this node.

        If this node is a list and flattenlists is True then we duplicate
        it to begin our list. Otherwise we use it as the first item in
        the new list. All other arguments are kept in order and added to
        the temporary list. Added lists can be flattened into our list
        rather than added as single items if flattenlists is True.

        """

        n_list = CustomAST([])
        idx = 0
        for item in [self] + list(vargs):
            if item.is_list() and flattenlists:
                for child in item.ordered_children():
                    n_list.children[str(idx)] = item.children[child]
                    n_list._node.append(item.children[child])
                    idx += 1
            else:
                n_list.children[str(idx)] = item
                n_list._node.append(item)
                idx += 1

        return n_list

    def ordered_children(self):
        """Order child names if this is a list."""

        if self.is_list():
            return (str(i) for i in range(len(self._node)))

        return keys()

    def _gen_children(self):
        """
        Generate children from current node.

        This takes children, assigns labels to them and fills our child dict.

        """

        self.children = dict()
        if self.is_ast():
            # Then we have an AST node
            self.children = {
                field: CustomAST(getattr(self._node, field))
                for field in self._node._fields
            }

        elif self.is_list():
            # We have a list of nodes
            self.children = {
                str(idx): CustomAST(self._node[idx])
                for idx in range(len(self._node))
            }

        elif not self.is_empty() and not self.is_basic():
            # We have not met this guy before
            raise TypeError("Not a recognised node type ("+self.type()+").")
