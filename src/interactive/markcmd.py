"""
Mark AST nodes with extra information from the console.

"""

# OAT - Obfuscation and Analysis Tool
# Copyright (C) 2011  Andy Gurden
# 
#     This file is part of OAT.
# 
#     OAT is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     OAT is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with OAT.  If not, see <http://www.gnu.org/licenses/>.

import ast
import abc

from util import pluginfinder
from analysis import automarker

from . import markers
from . import commandui

from writer import sourcewriter
from writer import prettywriter

from analysis.customast import CustomAST

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

        self._opts.add_argument("-a", "--auto", choices=["mark", "calc", "user"], nargs="*", metavar="METHOD",
                                help="Auto-mark this node and those needed to resolve its markings. It will use the given resolution order.")
        self._opts.add_argument("--review", action="store_true", default=False,
                                help="Review each set of markings before they are made permanent on a node. This is only valid for auto-marking.")

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

        return node        

    def run(self, args):
        """Mark the current AST node with extra information."""

        node = self._get_node()
        if node == None:
            return False

        params = vars(args)
        trans = {}
        for p in params:
            if params[p] != None and p in self.marks: # Has to be valid
                trans[p] = (lambda n=node, a=params[p], m=self.marks[p]: m.translate(n, a))

        if params["auto"] != None:
            self._auto_update(node, params["auto"], params["review"], trans)
        elif trans:
            self._manual_update(node, trans)
        else:
            self._show_markings(node)

    def _manual_update(self, node, trans):
        # From our setup we shouldn't cause exceptions
        to_mark = set(trans.keys())
        marker = automarker.AutoMarker([], mark=True, defaults=trans)
        m = marker.resolve_marks(node, needed=to_mark)
        self._show_dummy_markings(m)
        self._related_parsecmd.ast.augmented = True

    def _auto_update(self, node, res, review, trans):
        self._related_parsecmd.ast.augmented = True
        try:
            if review:
                marker = automarker.AutoMarker(res, mark=True, user=self._ask_specific, review=self._review_marks, defaults=trans)
            else:
                marker = automarker.AutoMarker(res, mark=True, user=self._ask_specific, defaults=trans)
        except ValueError as exc:
            print(str(exc))
        else:
            try:
                m = marker.resolve_marks(node) # By default all markings
                self._show_dummy_markings(m)
            except automarker.UserStop:
                print("The auto-marking process was interrupted.")

    def _show_markings(self, node):
        """Print out the markings for the given node."""

        print("Markings for current node:")

        for marker in self.marks:
            self.marks[marker].show(node, "  " + marker.title() + " - ")

    def _show_dummy_markings(self, markings):
        # Create a dummy node with the markings already set to show
        d_node = CustomAST([])
        d_node._markings = markings
        self._show_markings(d_node)


    def _ask_specific(self, node, needed):
        """Ask the user about specific markings for a specific node."""

        for n in needed:
            self._ask_user("We are missing the marking: " + n, node)

        return {}

    def _ask_user(self, question, node):
        """Print a problem and ask the user to fix it, print it or ignore it."""

        while True:
            print()
            print(question)
            print()
            print("Would you like to:")
            print("p) Print more information.")
            print("s) Print source for the node in question. This could be large.") 
            print("i) Ignore the problem. Allow other methods of mark resolution.")
            print("f) Stop and fix the problem.")

            ans = ""
            while ans not in ["p", "s", "i", "f"]:
                ans = input("Choose an option: ")

            print()

            if ans == "p":
                self._node_information(node)
            elif ans == "s":
                sourcewriter.printSource(node, prettywriter.PrettyWriter)
            elif ans == "i":
                return
            elif ans == "f":
                raise automarker.UserStop

    def _node_information(self, node):
        """Display information about a node."""

        print("Type: " + node.desc())
        loc = node.locstr()
        if loc:
            print("Location: " + loc)


    def _review_marks(self, node, markings):
        """Let the user review the markings and approve or disapprove them."""

        print()
        print("Current node:")
        self._node_information(node)
        print()
        print("Generated markings: ")

        self._show_dummy_markings(markings)
        print()

        print("Are these markings acceptable?")
        ans = input("Press enter for yes or type anything else for no: ")

        return not ans

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
