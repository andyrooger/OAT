"""
Provides a non-interactive graphical representation of state.

"""

import tkinter
from tkinter import ttk

from . import asttree

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
            self.tree = asttree.ScrolledASTTreeview(self, fulltree, currenttree)
            self.tree.grid(sticky="nsew")

        self.button = ttk.Button(self, text="Close", command=master.quit)
        self.button.grid(sticky="e")
