"""
Display a tree view of the current abstract syntax tree.

"""

import tkinter
from tkinter import ttk

class ASTTreeview(ttk.Treeview):
    """Create treeview to display an AST."""

    def __init__(self, parent, fulltree, currenttree=None):
        ttk.Treeview.__init__(self, parent)
        self._fill_tree(fulltree)

    def _fill_tree(self, tree, parent='', index=0):
        """Fill tree with given nodes."""

        if isinstance(tree, list):
            pass
        else:
            self.insert(parent, index, id(tree))
