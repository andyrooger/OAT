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

        root = tkinter.Tk()
        root.title("OAT Visualiser <" + str(self._related_parsecmd.ast) + ">")
        StaticVisual(root, fulltree=self._related_parsecmd.ast.tree)

        print("OAT Visualisation is being displayed.")
        print("To return to the command console, please quit the "
              "visualisation from its own window.")

        root.mainloop()
        try:
            root.destroy()
        except tkinter.TclError:
            pass # Probably already destroyed by closing from window.
