#!/usr/bin/env python3

"""
Explore ASTs from the console.

"""

import ast

from . import commandui

class ExploreCommand(commandui.Command):
    """Explore ASTs from the console."""

    def __init__(self, parsecmd):
        commandui.Command.__init__(self, "explore")

        self._opts.add_argument("-f", "--fields", action="store_true", default=False,
                                help="Show fields contained in the current node.")
        self._opts.add_argument("-a", "--attributes", action="store_true", default=False,
                                help="Show attributes of the current node.")
        self._opts.add_argument("-e", "--enter", metavar="FIELD",
                                nargs="?", const=False, default=None,
                                help="Drop through the AST into the given field or move up to the parent if no field is given.")

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
            print("There is no AST to explore. Have you create one with the parse command?")
            return

        if args.enter != None:
            if args.enter:
                if not self.enter_field(args.enter):
                    return
            else:
                if not self.level_up():
                    return

        current = self.ast_current

        print("Now at: " + self.describe_node(current))

        if args.attributes:
            print()
            print("Attributes:")
            if isinstance(current, ast.AST):
                for attr in current._attributes:
                    print("  " + attr + " - " + str(getattr(current, attr)))
            else:
                print("  Attributes are not valid on this type of node.")

        if args.fields:
            print()
            print("Fields:")
            if isinstance(current, ast.AST):
                for field in current._fields:
                    print("  " + field + " - " + self.describe_node(getattr(current, field)))
            elif isinstance(current, list):
                for i in range(len(current)):
                    print("  " + str(i) + " - " + self.describe_node(current[i]))
            else:
                print("  Fields are not valid on this type of node.")

    def status(self):
        self._ensure_node_sync()
        print("Viewing node: " + self.describe_node())

    def describe_node(self, node=None):
        """Get basic details for the current node."""

        if node == None:
            node = self.ast_current

        if node == None:
                return "No node"
        elif isinstance(node, ast.AST):
            text = node.__class__.__name__
            location = None
            try:
                location = "line " + str(node.lineno)
                location += ", col " + str(node.col_offset)
            except AttributeError:
                pass
            if location != None:
                text += " (" + location + ")"
            return text
        elif isinstance(node, list):
            return "Block of statements"
        else:
            return "Unknown (" + str(node) + ")"

    def enter_field(self, field):
        current = self.ast_current
        child = None

        if isinstance(current, ast.AST) and field in current._fields:
                child = getattr(current, field)
        elif isinstance(current, list):
            try:
                child = current[int(field)]
            except ValueError:
                pass
            except IndexError:
                pass

        if child == None:
            print("Field does not exist.")
            return False
        elif not isinstance(child, ast.AST) and not isinstance(child, list):
            print("Field is not a valid node.")
            return False

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

        if self._related_parsecmd.parsed_tree == None:
            self.ast_parents = []
        elif not hasattr(self, "ast_parents") or self.ast_top != self._related_parsecmd.parsed_tree:
            self.ast_parents = [self._related_parsecmd.parsed_tree]
