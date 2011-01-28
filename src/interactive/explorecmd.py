#!/usr/bin/env python3

"""
Explore ASTs from the console.

"""

import ast

from . import commandui

class ExploreCommand(commandui.Command):
    """Explore ASTs from the console."""

    def __init__(self, parsecmd):
        commandui.Command.__init__(self, "explore")

        self._opts.add_argument("-f", "--fields", action="store_true", default=False,
                                help="Show fields contained in the current node.")
        self._opts.add_argument("-a", "--attributes", action="store_true", default=False,
                                help="Show attributes of the current node.")
        self._opts.add_argument("-e", "--enter",
                                help="Drop through the AST into the given field or move up to the parent if no field is given.")

        self._related_parsecmd = parsecmd
        self._ensure_node_sync()

    @property
    def ast_current(self):
        """The ast node we are currently looking at."""

        try:
            *ignore, last = self.ast_parents
        except ValueError:
            return None
        else:
            return last

    @property
    def ast_top(self):
        """The ast node at the top of our tree."""

        try:
            first, *ignore = self.ast_parents
        except ValueError:
            return None
        else:
            return first


    def run(self, args):
        """Explore the AST."""

        self._ensure_node_sync()
        self.print_node()

    def print_node(self):
        """Print out basic details for the current node."""

        node = self.ast_current

        if node == None:
            print("No node selected. Have you created a tree with the parse command?")
        elif isinstance(node, ast.AST):
            type = node.__class__.__name__
            print(type, end="")
            if hasattr(node, "lineno"):
                print(": line " + str(node.lineno), end="")
                if hasattr(node, "col_offset"):
                    print(", column " + str(node.col_offset))
            print()
        else:
            print("Unknown node type: ", end="")
            print(node)

    def _ensure_node_sync(self):
        """Ensure the current node stack is in sync with the main tree."""

        if self._related_parsecmd.parsed_tree == None:
            self.ast_parents = []
        elif not hasattr(self, "ast_parents") or self.ast_top != self._related_parsecmd.parsed_tree:
            self.ast_parents = [self._related_parsecmd.parsed_tree]
