"""
Provides a non-interactive graphical representation of state.

"""

import tkinter
from tkinter import ttk

from . import asttree

class StaticVisual:
    """
    Create frame with all the widgets we need to understand the
    state of the program.

    """

    def __init__(self, master, fulltree=None, currenttree=None):
        frame = ttk.Frame(master)

        if fulltree == None:
            ttk.Label(frame, text="No tree loaded.").pack()
            ttk.Label(frame, text="Please use parse to create one.").pack()
        else:
            self.tree = asttree.ScrolledASTTreeview(frame, fulltree, currenttree)
            self.tree.pack()

        self.button = ttk.Button(frame, text="QUIT", command=frame.quit)
        self.button.pack(side=tkinter.LEFT)

        self.hi_there = tkinter.Button(frame, text="Hello", command=None)
        self.hi_there.pack(side=tkinter.LEFT)

        frame.pack()
