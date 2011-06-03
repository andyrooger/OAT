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

    def temp_list(self, *vargs):
        """
        Create a temporary list node starting with this node.

        If this node is a list then we duplicate it to begin our list.
        Otherwise we use it as the first item in the new list. All other
        arguments are kept in order and added to the temporary list.

        Lists are always flattened.

        """

        n_list = []
        idx = 0
        items = [self] + list(vargs)
        for item in items:
            if item.is_list():
                n_list += [item.children[k] for k in item.ordered_children()]
            else:
                n_list.append(item)
        return CustomAST(n_list)

        return n_list

    def ordered_children(self):
        """Order child names if this is a list."""

        if self.is_list():
            return (str(i) for i in range(len(self._node)))

        return self.children.keys()

    def become(self, node):
        """Replace ast node with the innards of the new node and update children."""

        if not self.is_list() or not node.is_list():
            raise TypeError("become() operation is only supported between lists currently.")

        self._node[:] = node._node
        self.children = node.children.copy()

    def _gen_children(self):
        """
        Generate children from current node.

        This takes children, assigns labels to them and fills our child dict.
        This converts any non-CustomAST children to CustomASTs in our children
        dict, but converts any CustomASTs in the simple node to other simple
        nodes.

        """

        self.children = dict()
        if self.is_ast():
            # Then we have an AST node
            self.children = {
                field: getattr(self._node, field)
                for field in self._node._fields
            }

        elif self.is_list():
            # We have a list of nodes
            self.children = {
                str(idx): self._node[idx]
                for idx in range(len(self._node))
            }

        elif not self.is_empty() and not self.is_basic():
            # We have not met this guy before
            raise TypeError("Not a recognised node type ("+self.type()+").")

        for key in self.children:
            if isinstance(self.children[key], CustomAST):
                # Convert CustomAST node-children to normal nodes
                if self.is_list():
                    self._node[int(key)] = self.children[key]._node
                else:
                    setattr(self._node, key, self.children[key]._node)
            else:
                # And our normal ast children to CustomAST
                self.children[key] = CustomAST(self.children[key])


    def location(self):
        """Get the node's location in a file if it exists."""

        try:
            return (self._node.lineno, self._node.col_offset)
        except AttributeError:
            return None

    def desc(self):
        """Provide a text description of the node."""

        if self.is_empty():
            if self.is_list():
                return "Empty list"
            else:
                return "No node"

        if self.is_list():
            return "Block of statements"

        if self.is_ast():
            return self.type()

        return "Unknown node (" + str(self.node()) + " : " + self.type() + ")"

    def locstr(self):
        """Provide a text description of the location."""

        loc = self.location()
        if loc:
            return "line " + str(loc[0]) + " column " + str(loc[1])
        else:
            return None

    def __str__(self):
        d = self.desc()
        l = self.locstr()
        
        return d + " (" + l + ")" if l else d


