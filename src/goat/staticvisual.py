"""
Provides a non-interactive graphical representation of state.

"""

import tkinter

class StaticVisual:
    """
    Create frame with all the widgets we need to understand the
    state of the program.

    """

    def __init__(self, master):
        frame = tkinter.Frame(master)
        frame.pack()

        self.button = tkinter.Button(frame, text="QUIT", fg="red", command=frame.quit)
        self.button.pack(side=tkinter.LEFT)

        self.hi_there = tkinter.Button(frame, text="Hello", command=None)
        self.hi_there.pack(side=tkinter.LEFT)
