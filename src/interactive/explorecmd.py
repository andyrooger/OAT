"""
Explore ASTs from the console.

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

from . import commandui

class ExploreCommand(commandui.Command):
    """Explore ASTs from the console."""

    def __init__(self, parsecmd):
        commandui.Command.__init__(self, "explore")

        group = self._opts.add_mutually_exclusive_group()
        group.add_argument("field", metavar="FIELD", default=None, nargs="?",
                           help="Field to drop through the tree into.")
        group.add_argument("-a", "--attributes", action="store_true", default=False,
                           help="Show attributes of the current node.")
        group.add_argument("-p", "--parent", action="store_true", default=False,
                           help="Head up the tree to a parent.")

        self._related_parsecmd = parsecmd
        self._ensure_node_sync()

    @property
    def ast_current(self):
        """The ast node we are currently looking at."""

        try:
            *ignore, last = self.ast_parents
        except ValueError:
            return None
        else:
            return last

    @property
    def ast_top(self):
        """The ast node at the top of our tree."""

        try:
            first, *ignore = self.ast_parents
        except ValueError:
            return None
        else:
            return first


    def run(self, args):
        """Explore the AST."""

        self._ensure_node_sync()

        if self.ast_current == None:
            print("There is no AST to explore. Have you created one with the parse command?")
            return

        if args.field != None:
            if self.enter_field(args.field):
                print("Looking at: " + str(self.ast_current))
            return
        elif args.parent:
            if self.level_up():
                print("Looking at: " + str(self.ast_current))
            return

        current = self.ast_current
        print("Looking at: " + str(current))

        if args.attributes:
            print()
            print("Attributes:")
            if current.is_ast():
                loc = current.location()
                if loc != None:
                    line, offset = loc
                    print("  Line Num   - " + str(line))
                    print("  Col Offset - " + str(offset))
                else:
                    print("  There are no attributes for this node.")
            else:
                print("  Attributes are not valid on this type of node.")

        print()
        print("Fields:")
        if current.has_children():
            for field in current:
                print("  " + field + " - " + str(current[field]))
        else:
            print("  This node has no fields.")

    def status(self):
        self._ensure_node_sync()
        print("Viewing node: " + str(self.ast_current) if self.ast_current != None else "No node")

    def enter_field(self, field):
        current = self.ast_current
        child = None

        try:
            child = current[field]
        except KeyError:
            print("Field does not exist.")
            return False
        else:
            self.ast_parents.append(child)

        return True

    def level_up(self):
        if len(self.ast_parents) > 1:
            self.ast_parents.pop()
            return True
        else:
            print("There is no parent node.")
        return False

    def _ensure_node_sync(self):
        """Ensure the current node stack is in sync with the main tree."""

        if self._related_parsecmd.ast.tree == None:
            self.ast_parents = []
        elif not hasattr(self, "ast_parents") or self.ast_top != self._related_parsecmd.ast.tree:
            self.ast_parents = [self._related_parsecmd.ast.tree]

    def autocomplete(self, before, arg, after):
        if not arg.startswith("-"):
            self._ensure_node_sync()
            current = self.ast_current
            if current != None:
                return [f for f in current.ordered_children()
                        if f.startswith(arg)]
        return []
