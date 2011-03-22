"""
Mark AST nodes with extra information from the console.

"""

import ast
import abc
from util import pluginfinder
from . import markers

from . import commandui

class MarkCommand(commandui.Command):
    """Mark AST nodes with extra information from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "mark")

        plugins = pluginfinder.PluginFinder(markers).getPlugins()
        self.marks = {}

        for plugin in plugins:
            try:
                marker = plugin.Marker()
                if isinstance(marker, AbstractMarker):
                    name = plugin.__name__.rsplit(".", 1)[-1]
                    self.marks[name] = marker
            except AttributeError:
                pass # Not a valid plugin

        for marker in self.marks:
            self._opts.add_argument("-"+marker[0], "--"+marker,
                                    help=self.marks[marker].__doc__,
                                    **self.marks[marker].parameters())

        self._related_parsecmd = parsecmd
        self._related_explorecmd = explorecmd

    def _get_node(self):
        """Get current node, print errors and return the node or None."""

        self._related_explorecmd._ensure_node_sync()
        node = self._related_explorecmd.ast_current

        if node == None:
            print("There is no AST to mark. Have you create one with the parse command?")
            return None

        if not isinstance(node, ast.AST):
            print("This node does not support markings.")
            return None

        return node        

    def run(self, args):
        """Mark the current AST node with extra information."""

        node = self._get_node()
        if node == None:
            return False

        params = vars(args)
        emptyargs = True
        for param in params:
            if params[param] != None:
                try:
                    if self.marks[param].update(node, params[param]):
                        emptyargs = False
                        self._related_parsecmd.ast.augmented = True
                except KeyError:
                    pass # Unrecognised argument, don't expect this to happen

        if emptyargs:
            self._show_markings()

#        newmarkings = {
#            mark: newmarkings[mark]
#            for mark in newmarkings
#            if newmarkings[mark] != None
#        }

#        if "reads" in newmarkings:
#            newmarkings["reads"] = self.parseRefs(newmarkings["reads"], "reads")
#        if "writes" in newmarkings:
#            newmarkings["writes"] = self.parseRefs(newmarkings["writes"], "writes")
#
#        if newmarkings:
#            self._update_markings(newmarkings)
#        else:
#            self._show_markings()

    def _show_markings(self): #, markings=None, indent=""):
        """Print out the markings for the current node."""

        node = self._get_node()

        if node == None:
            return False

        print("Markings for current node:")
        for marker in self.marks:
            self.marks[marker].show(node, "  " + marker.title() + " - ")

#        if markings == None:
#            print("Markings for current node:")
#            return self._show_markings(self._get_markings(), "    ")

#        for mark in markings:
#            print(indent + mark + ": ", end="")
#            if isinstance(markings[mark], dict):
#                print()
#                self._show_markings(markings[mark], indent+"    ")
#            else:
#                print(markings[mark])

    def parseRefs(self, changes, mark):
        """
        Parse the function references from the command line.

        Uses format (a(g|n|l|u)|r)-variable.

        """

        self._related_explorecmd._ensure_node_sync()
        try:
            refs = self._get_markings()[mark].copy()
        except KeyError:
            refs = {}

        for change in changes:
            try:
                action, var = change.split("-", 1)
            except ValueError:
                # Not enough parts (no '-')
                print("Missing action: " + change)
                continue

            if not action:
                raise ValueError("Change should not start with '-', EVER!")

            if action[0] not in "ar":
                print("Unrecognised action: " + action + " in " + change)
                continue

            if action[0] == "a":
                if len(action) != 2:
                    print("Missing type: " + action + " in " + change)
                    continue

                try:
                    category = {
                        "g": "global",
                        "n": "nonlocal",
                        "l": "local",
                        "u": "unknown",
                    }[action[1]]
                except KeyError:
                    print("Unknown type: " + action[1] + " in " + change)
                    continue

                refs[var] = category

            if action[0] == "r":
                if len(action) != 1:
                    print("Unrecognised action: " + action + " in " + change)
                    continue

                try:
                    del refs[var]
                except KeyError:
                    print("Cannot remove non-existent variable: " + var + " in " + change)
                    continue

        return refs


class AbstractMarker(metaclass=abc.ABCMeta):
    """Base class for creating markers."""

    @abc.abstractmethod
    def parameters(self):
        """Get the necessary parameters for the argument parser."""

    @abc.abstractmethod
    def update(self, node, arg):
        """Update the markings based on the given arguments. Return whether successful."""

    @abc.abstractmethod
    def show(self, node, title):
        """Print information about this type of marking, beginning with title."""
