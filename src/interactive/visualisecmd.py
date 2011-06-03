"""
Allow the user to visualise the current state of the program from the console.

"""

import ast
import tkinter

from . import commandui

from goat.staticvisual import StaticVisual

class VisualiseCommand(commandui.Command):
    """Visualise the state of the program from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "visualise")

        self._related_parsecmd = parsecmd
        self._related_explorecmd = explorecmd

    def run(self, args):
        """Pop up our GUI."""

        self._related_explorecmd._ensure_node_sync()

        root = tkinter.Tk()
        root.title("OAT Visualiser <" + str(self._related_parsecmd.ast) + ">")
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(0, weight=1)
        StaticVisual(root,
                     fulltree=self._related_explorecmd.ast_top,
                     currenttree=self._related_explorecmd.ast_current
                     ).grid(sticky="nsew")

        print("OAT Visualisation is being displayed.")
        print("To return to the command console, please quit the "
              "visualisation from its own window.")

        root.mainloop()
        try:
            root.destroy()
        except tkinter.TclError:
            pass # Probably already destroyed by closing from window.
