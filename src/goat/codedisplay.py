"""
Provides a display of the current code, possibly with highlighting.

"""

import tkinter
from tkinter import ttk

class CodeDisplay(ttk.Frame):
    """
    Create frame containing all the widgets we need for displaying the code.

    """

    def __init__(self, master, node, highlight=None, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        ScrolledCodeBox(self, node, highlight, **kwargs).grid(
            column=0, row=0, columnspan=2, sticky="nsew")

        ttk.Label(self, text="Code displayed using").grid(
            column=0, row=1, sticky="nse")

        self.disp_type = ttk.Combobox(self, values=["Basic", "Pretty"], state="readonly")
        self.disp_type.set("Pretty")
        self.disp_type.grid(column=1, row=1, sticky="ns")

class ScrolledCodeBox(ttk.Frame):
    """
    Box for the actual code, but with scrollbars.

    """

    def __init__(self, master, node, highlight=None, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        xscroll = ttk.Scrollbar(self, orient="horizontal")
        xscroll.grid(column=0, row=1, sticky="ew")
        yscroll = ttk.Scrollbar(self)
        yscroll.grid(column=1, row=0, sticky="ns")

        cb = CodeBox(self, node, highlight,
                     xscrollcommand=xscroll.set,
                     yscrollcommand=yscroll.set)
        cb.grid(column=0, row=0, sticky="nsew")

        xscroll.config(command=cb.xview)
        yscroll.config(command=cb.yview)

class CodeBox(tkinter.Text):
    """
    Text box to display and format our code.

    """

    def __init__(self, master, node, highlight=None, **kwargs):
        tkinter.Text.__init__(self, master, **kwargs)
