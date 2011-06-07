"""
Display a tree view of the current abstract syntax tree.

"""

import tkinter
from tkinter import ttk

class ScrolledASTTreeview(ttk.Frame):
    """Scrolling version on ASTTreeview."""

    def __init__(self, parent, fulltree, currenttree=None, select_handler=None):
        ttk.Frame.__init__(self, parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        xscroll = ttk.Scrollbar(self, orient="horizontal")
        xscroll.grid(column=0, row=1, sticky="ew")
        yscroll = ttk.Scrollbar(self)
        yscroll.grid(column=1, row=0, sticky="ns")

        tv = ASTTreeview(self, fulltree, currenttree, select_handler,
                         xscrollcommand=xscroll.set,
                         yscrollcommand=yscroll.set)
        tv.grid(column=0, row=0, sticky="nsew")
        xscroll.config(command=tv.xview)
        yscroll.config(command=tv.yview)


class ASTTreeview(ttk.Treeview):
    """Create treeview to display an AST."""

    def __init__(self, parent, fulltree, currenttree=None, select_handler=None, **kwargs):
        # Setup
        ttk.Treeview.__init__(self, parent,
                              columns=["type", "value"],
                              selectmode="browse")
        self.heading("type", text="Type")
        self.column("type", width=100)
        self.heading("value", text="Value")

        # Tags
        self.tag_configure("empty", background="#222")
        self.tag_configure("current", background="#b2ff00")

        # Content
        self._fill_tree(fulltree)
        self.selection_set(id(currenttree))
        self.see(id(currenttree))
        self.item(id(currenttree), tags=["current"], open=True)

        # Selection
        self.selection_handler = select_handler
        self.bind("<<TreeviewSelect>>", func=self._selected)

    def _selected(self, info):
        """Called on selection event to dispatch an actual node to our handler."""

        if self.selection_handler == None:
            return # No point dealing with this

        try:
            nid, *_ = self.selection() # Take first
        except ValueError:
            return

        try:
            node = self._node_lookup[nid]
        except KeyError:
            # Either we didn't create the lookup table in _fill_tree
            # Or we haven't seen it
            return
        self.selection_handler(node)

    def _fill_tree(self, tree, parent='', link='Root', index=0):
        """Fill tree with given nodes."""

        # Add node to lookup table
        if not hasattr(self, "_node_lookup"):
            self._node_lookup = {}

        self._node_lookup[str(id(tree))] = tree

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
        for child in tree:
            self._fill_tree(tree[child],
                            parent=id(tree),
                            link=child,
                            index=idx)
            idx += 1
