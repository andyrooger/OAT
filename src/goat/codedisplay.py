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

        if hasattr(self, "_node") and hasattr(self, "_selected") and hasattr(self, "_current"):
            self.fill(self._node, self._selected, self._current)

    def fill(self, node, selected=None, current=None):
        """Print the actual code in our box."""

        self._node = node
        self._selected = selected
        self._current = current

        try:
            writer = {
                "pretty": prettywriter.PrettyWriter,
                "basic": basicwriter.BasicWriter
            }[self.disp_type.get()]
        except KeyError:
            raise ValueError("Writer radio button has incorrect value.")
        else:
            self.codebox.fill(writer, node, selected, current)

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

    def fill(self, writer, node, selected=None, current=None):
        """Write the code."""

        self.codebox.fill(writer, node, selected, current)

class CodeBox(tkinter.Text):
    """
    Text box to display and format our code.

    """

    def __init__(self, master, **kwargs):
        tkinter.Text.__init__(self, master, state="disabled", **kwargs)
        self.tag_config("currentnode", background="#b2ff00")
        self.tag_config("selectednode", background="#8B98C6", foreground="white")

    def fill(self, writer, node, selected=None, current=None):
        """Write the code."""

        self.config(state="normal")

        self.delete("1.0", "end") # clear
        TaggingWriter = tagging_writer(writer, self, selectednode=selected, currentnode=current)
        TaggingWriter(node).write()

        self.config(state="disabled")


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


    class DisplayIO:
        def write(self, data):
            display.insert("end", data)

    class TaggingWriter(writer):

        def __init__(self, node, *varargs, **kwargs):
            writer.__init__(self, node, DisplayIO(), *varargs, **kwargs)

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
