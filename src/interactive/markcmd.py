"""
Mark AST nodes with extra information from the console.

"""

import ast

from . import commandui

class MarkCommand(commandui.Command):
    """Mark AST nodes with extra information from the console."""

    def __init__(self, explorecmd):
        commandui.Command.__init__(self, "mark")

        self._opts.add_argument("-v", "--visible", choices=["invisible", "visible"],
                                help="Is this a visible or invisible statement?")

        self._related_explorecmd = explorecmd

    def run(self, args):
        """Mark the current AST node with extra information."""

        self._related_explorecmd._ensure_node_sync()

        node = self._related_explorecmd.ast_current

        if node == None:
            print("There is no AST to mark. Have you create one with the parse command?")
            return False

        newmarkings = vars(args)
        newmarkings = {
            mark: newmarkings[mark]
            for mark in newmarkings
            if newmarkings[mark] != None
        }

        if newmarkings:
            self._update_markings(newmarkings)
        else:
            self._show_markings()

    def _get_markings(self):
        """Get the markings set on the current node."""

        node = self._related_explorecmd.ast_current
        return node._markings if hasattr(node, "_markings") else {}

    def _show_markings(self):
        """Print out the markings for the current node."""

        markings = self._get_markings()

        print("Markings for current node:")

        for mark in markings:
            print(mark.title() + ": " + str(markings[mark]))

    def _update_markings(self, marks):
        """Update the current node's markings with the values in the marks dict."""


        node = self._related_explorecmd.ast_current

        if isinstance(node, list):
            print("This node does not support markings.")
            return False

        if not hasattr(node, "_markings"):
            node._markings = {}
        
        node._markings.update(marks)
