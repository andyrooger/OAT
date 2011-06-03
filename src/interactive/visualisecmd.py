"""
Allow the user to visualise the current state of the program from the console.

"""

import ast

from . import commandui

class VisualiseCommand(commandui.Command):
    """Visualise the state of the program from the console."""

    def __init__(self, explorecmd):
        commandui.Command.__init__(self, "visualise")

        self._related_explorecmd = explorecmd

    def run(self, args):
        """Pop up our GUI."""
