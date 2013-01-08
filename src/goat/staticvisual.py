"""
Provides a non-interactive graphical representation of state.

"""

# OAT - Obfuscation and Analysis Tool
# Copyright (C) 2011  Andy Gurden
# 
#     This file is part of OAT.
# 
#     OAT is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     OAT is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with OAT.  If not, see <http://www.gnu.org/licenses/>.

import tkinter
from tkinter import ttk

from . import asttree
from . import markpane
from . import codedisplay

class StaticVisual(ttk.Frame):
    """
    Create frame with all the widgets we need to understand the
    state of the program.

    """

    def __init__(self, master, fulltree=None, currenttree=None, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        if fulltree == None:
            self.grid_rowconfigure(0, weight=1)
            self.grid_rowconfigure(1, weight=1)
            ttk.Label(self, text="No tree loaded.").grid(sticky="s")
            ttk.Label(self, text="Please use parse to create one.").grid(sticky="n")
        else:
            self.grid_rowconfigure(0, weight=1)
            StaticVisualPanes(self, fulltree, currenttree).grid(sticky="nsew")

        self.button = ttk.Button(self, text="Close", command=master.quit)
        self.button.grid(sticky="e", pady=5, padx=5)


class StaticVisualPanes(ttk.PanedWindow):
    """
    PanedWindow containing everything we want to view a node.

    """

    def __init__(self, master, node, currentnode=None, **kwargs):
        ttk.PanedWindow.__init__(self, master, orient="horizontal", **kwargs)

        self._top_node = node
        self._selected_node = currentnode
        self._current_node = currentnode

        self.inner = ttk.PanedWindow(self, **kwargs)
        self.add(self.inner)

        tree = asttree.ScrolledASTTreeview(
            self.inner, node, currentnode, select_handler=self._update_node)
        self.inner.add(tree)

        self.marks = markpane.MarkPane(self.inner, currentnode)
        self.inner.add(self.marks)

        self.codebox = codedisplay.CodeDisplay(self)
        self.add(self.codebox)
        self.codebox.fill(node, currentnode, currentnode)

    def _update_node(self, node):
        """Callback for tree view when node is changed."""

        if self._selected_node == node:
            return
        else:
            self._selected_node = node

        self.inner.remove(self.marks)
        self.marks.destroy()
        self.marks = markpane.MarkPane(self.inner, node)
        self.inner.add(self.marks)

        self.codebox.fill(self._top_node, self._selected_node, self._current_node)
