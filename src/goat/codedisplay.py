"""
Provides a display of the current code, possibly with highlighting.

"""

import tkinter
from tkinter import ttk

from writer import prettywriter
from writer import basicwriter

class CodeDisplay(ttk.Frame):
    """
    Create frame containing all the widgets we need for displaying the code.

    """

    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.codebox = ScrolledCodeBox(self, **kwargs)
        self.codebox.grid(column=0, row=0, columnspan=3, sticky="nsew")

        ttk.Label(self, text="Code displayed using").grid(
            column=0, row=1, sticky="nsw")

        self.disp_type = tkinter.StringVar(value="pretty")
        def_btn = ttk.Radiobutton(
            self, text="Pretty", variable=self.disp_type, value="pretty", command=self.refresh)
        def_btn.grid(column=1, row=1, sticky="ns")
        ttk.Radiobutton(
            self, text="Basic", variable=self.disp_type, value="basic", command=self.refresh).grid(
            column=2, row=1, sticky="ns")

    def refresh(self):
        """Refill code with previous node values."""

        if hasattr(self, "_node") and hasattr(self, "_highlight"):
            self.fill(self._node, self._highlight)

    def fill(self, node, highlight=None):
        """Print the actual code in our box."""

        self._node = node
        self._highlight = highlight

        try:
            writer = {
                "pretty": prettywriter.PrettyWriter,
                "basic": basicwriter.BasicWriter
            }[self.disp_type.get()]
        except KeyError:
            raise ValueError("Writer radio button has incorrect value.")
        else:
            self.codebox.fill(writer, node, highlight)

class ScrolledCodeBox(ttk.Frame):
    """
    Box for the actual code, but with scrollbars.

    """

    def __init__(self, master, **kwargs):
        ttk.Frame.__init__(self, master, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        xscroll = ttk.Scrollbar(self, orient="horizontal")
        xscroll.grid(column=0, row=1, sticky="ew")
        yscroll = ttk.Scrollbar(self)
        yscroll.grid(column=1, row=0, sticky="ns")

        self.codebox = CodeBox(self,
                               xscrollcommand=xscroll.set,
                               yscrollcommand=yscroll.set)
        self.codebox.grid(column=0, row=0, sticky="nsew")

        xscroll.config(command=self.codebox.xview)
        yscroll.config(command=self.codebox.yview)

    def fill(self, writer, node, highlight=None):
        """Write the code."""

        self.codebox.fill(writer, node, highlight)

class CodeBox(tkinter.Text):
    """
    Text box to display and format our code.

    """

    def __init__(self, master, **kwargs):
        tkinter.Text.__init__(self, master, state="disabled", **kwargs)

    def fill(self, writer, node, highlight=None):
        """Write the code."""

        self.config(state="normal")

        self.delete("1.0", "end") # clear
        self._display_writer(writer, node, highlight).write()

        self.config(state="disabled")

    def _display_writer(self, writer, node, highlight=None):
        """Take a writer class and return an instance prepared to write to our display."""

        class TaggingWriter(writer):
            def _write(self, node):
                if node is highlight:
                    # Tag here and after
                    super()._write(node)
                else:
                    super()._write(node)

        return TaggingWriter(node, self._display_file())

    def _display_file(self):
        """Get a file-like object to write to the display."""

        class DisplayIO:
            def write(innerself, data):
                self.insert("end", data)

        return DisplayIO()
