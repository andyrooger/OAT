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
            if params[param] != None and param in self.marks: # Has to be valid
                emptyargs = False
                trans = self.marks[param].translate(node, params[param])
                if self.marks[param].update(node, trans):
                    self._related_parsecmd.ast.augmented = True

        if emptyargs:
            self._show_markings()

    def _show_markings(self): #, markings=None, indent=""):
        """Print out the markings for the current node."""

        node = self._get_node()

        if node == None:
            return False

        print("Markings for current node:")
        for marker in self.marks:
            self.marks[marker].show(node, "  " + marker.title() + " - ")


class AbstractMarker(metaclass=abc.ABCMeta):
    """Base class for creating markers."""

    @abc.abstractmethod
    def parameters(self):
        """Get the necessary parameters for the argument parser."""

    @abc.abstractmethod
    def translate(self, node, arg):
        """Translate the argument into a representation of the new markings."""

    @abc.abstractmethod
    def update(self, node, trans):
        """Update the markings based on the given translation. Return whether successful."""

    @abc.abstractmethod
    def show(self, node, title):
        """Print information about this type of marking, beginning with title."""
