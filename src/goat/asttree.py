"""
Display a tree view of the current abstract syntax tree.

"""

import tkinter
from tkinter import ttk

class ScrolledASTTreeview(ttk.Frame):
    """Scrolling version on ASTTreeview."""

    def __init__(self, parent, fulltree, currenttree=None):
        ttk.Frame.__init__(self, parent)

        xscroll = ttk.Scrollbar(self, orient="horizontal")
        xscroll.grid(column=0, row=1, sticky="ew")
        yscroll = ttk.Scrollbar(self)
        yscroll.grid(column=1, row=0, sticky="ns")

        tv = ASTTreeview(self, fulltree, currenttree,
                         xscrollcommand=xscroll.set,
                         yscrollcommand=yscroll.set)
        tv.grid(column=0, row=0, sticky="nsew")
        xscroll.config(command=tv.xview)
        yscroll.config(command=tv.yview)

class ASTTreeview(ttk.Treeview):
    """Create treeview to display an AST."""

    def __init__(self, parent, fulltree, currenttree=None, **kwargs):
        # Setup
        ttk.Treeview.__init__(self, parent,
                              columns=["type", "value"],
                              selectmode="none")
        self.heading("type", text="Type")
        self.heading("value", text="Value")

        # Tags
        self.tag_configure("empty", background="#222")

        # Content
        self._fill_tree(fulltree)
        self.selection_set(id(currenttree))
        self.see(id(currenttree))
        self.item(id(currenttree), open=True)

    def _fill_tree(self, tree, parent='', link='Root', index=0):
        """Fill tree with given nodes."""

        # Insert item
        self.insert(parent, index, iid=id(tree), text=link)

        # Tag item
        if tree.is_empty():
            self.item(id(tree), tags=["empty"])

        # Fill columns
        self.set(id(tree), "type", tree.type())
        if tree.is_basic():
            self.set(id(tree), "value", str(tree.node()))

        # Add children
        idx = 0
        for child in tree.ordered_children():
            self._fill_tree(tree.children[child],
                            parent=id(tree),
                            link=child,
                            index=idx)
            idx += 1
