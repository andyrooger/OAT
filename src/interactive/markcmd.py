"""
Mark AST nodes with extra information from the console.

"""

import ast

from . import commandui

class MarkCommand(commandui.Command):
    """Mark AST nodes with extra information from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "mark")

        self._opts.add_argument("-v", "--visible", choices=["invisible", "visible"],
                                help="Is this a visible or invisible statement? (i.e. does it perform actions visible to the outside world?")
        self._opts.add_argument("-b", "--breaks", choices=["yes", "no"],
                                help="Can this statement break from a linear flow?")
        self._opts.add_argument("-r", "--reads", nargs="+", metavar="var",
                                help="Choose all the variables this node reads. Use (+|-)(g|n|l|u)variable to add or remove a global, nonlocal, local, or unknown variable.")
        self._opts.add_argument("-w", "--writes", nargs="+", metavar="var",
                                help="Choose all the variables this node writes. Use (a|r)(g|n|l|u)variable to add or remove a global, nonlocal, local, or unknown variable.")

        self._related_parsecmd = parsecmd
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

        if "reads" in newmarkings:
            newmarkings["reads"] = self.parseRefs(newmarkings["reads"], "reads")
        if "writes" in newmarkings:
            newmarkings["writes"] = self.parseRefs(newmarkings["writes"], "writes")

        if newmarkings:
            self._update_markings(newmarkings)
        else:
            self._show_markings()

    def _get_markings(self):
        """Get the markings set on the current node."""

        node = self._related_explorecmd.ast_current
        return node._markings if hasattr(node, "_markings") else {}

    def _show_markings(self, markings=None, indent=""):
        """Print out the markings for the current node."""

        if markings == None:
            print("Markings for current node:")
            return self._show_markings(self._get_markings(), "    ")

        for mark in markings:
            print(indent + mark.title() + ": ", end="")
            if isinstance(markings[mark], dict):
                print()
                self._show_markings(markings[mark], indent+"    ")
            else:
                print(markings[mark])

    def _update_markings(self, marks):
        """Update the current node's markings with the values in the marks dict."""

        node = self._related_explorecmd.ast_current

        if isinstance(node, list):
            print("This node does not support markings.")
            return False

        if not hasattr(node, "_markings"):
            node._markings = {}
            self._related_parsecmd.ast.augmented = True
        
        node._markings.update(marks)

        if marks:
            self._related_parsecmd.ast.augmented = True


    def parseRefs(self, changes, mark):
        """
        Parse the function references from the command line.

        Uses format (a|r)(g|n|l|u)variable.

        """

        self._related_explorecmd._ensure_node_sync()
        try:
            refs = self._get_markings()[mark].copy()
        except KeyError:
            refs = {
                "global": set(),
                "nonlocal": set(),
                "local": set(),
                "unknown": set()
            }

        for change in changes:
            if len(change) < 3:
                print("Unrecognised argument: " + change)
                continue

            try:
                category = {
                    "g": "global",
                    "n": "nonlocal",
                    "l": "local",
                    "u": "unknown",
                }[change[1]]
            except KeyError:
                print("Unknown type: " + change[1] + " in " + change)
                continue

            try:
                do = {
                    "a" : refs[category].add,   # Categories are created with
                    "r" : refs[category].remove # the original marking
                }[change[0]]
            except KeyError:
                print("Invalid action: " + change[0] + " in " + change)
                continue


            variable = change[2:]

            try:
                do(variable)
            except KeyError:
                pass # Means we tried to remove a variable that didn't exist
            

        return refs
