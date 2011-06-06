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
        self.tag_config("selectednode", background="blue")

    def fill(self, writer, node, highlight=None):
        """Write the code."""

        self.config(state="normal")

        self.delete("1.0", "end") # clear
        self._display_writer(writer, node, highlight).write()

        self.config(state="disabled")

    def _display_writer(self, writer, node, highlight=None):
        """Take a writer class and return an instance prepared to write to our display."""

        TaggingWriter = tagging_writer(writer, self, selectednode=highlight)
        return TaggingWriter(node, self._display_file())

    def _display_file(self):
        """Get a file-like object to write to the display."""

        class DisplayIO:
            def write(innerself, data):
                self.insert("end", data)

        return DisplayIO()


def tagging_writer(writer, display, **highlight):
    """
    Create a tagging writer class from a writer class.

    highlight is a dict from tag name to nodes.

    """

    in_progress = set()

    def _highlight(name, state):
        """Start or stop tagging name."""

        if state == (name in in_progress):
            return
        else:
            if state:
                in_progress.add(name)
            else:
                in_progress.remove(name)
        if state:
            display.mark_set("starthighlight"+name, "current")
            display.mark_gravity("starthighlight"+name, "left")
        else:
            display.tag_add(name, "starthighlight"+name, "current")


    def _highlighter(f):
        """Can highlight innards of methods."""

        def f2(self, node, *varargs, **kwargs):
            for h in highlight:
                if node is highlight[h]:
                    _highlight(h, True)
            f(self, node, *varargs, **kwargs)
            for h in highlight:
                if node is highlight[h]:
                    _highlight(h, False)
        return f2


    class TaggingWriter(writer):

        @_highlighter
        def _write(self, *varargs, **kwargs):
            super()._write(*varargs, **kwargs)

        @_highlighter
        def _interleave_write(self, *varargs, **kwargs):
            super()._interleave_write(*varargs, **kwargs)

        @_highlighter
        def _write_block(self, *varargs, **kwargs):
            super()._write_block(*varargs, **kwargs)

    return TaggingWriter
