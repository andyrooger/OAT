"""
Explore ASTs from the console.

"""

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
            print("There is no AST to explore. Have you create one with the parse command?")
            return

        if args.field != None:
            if self.enter_field(args.field):
                print("Looking at: " + self.describe_node(self.ast_current))
            return
        elif args.parent:
            if self.level_up():
                print("Looking at: " + self.describe_node(self.ast_current))
            return

        current = self.ast_current
        print("Looking at: " + self.describe_node(current))

        if args.attributes:
            print()
            print("Attributes:")
            if isinstance(current, ast.AST):
                if current._attributes:
                    for attr in current._attributes:
                        print("  " + attr + " - " + str(getattr(current, attr)))
                else:
                    print("  There are no attributes for this node.")
            else:
                print("  Attributes are not valid on this type of node.")

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
        print("Viewing node: " + self.describe_node(self.ast_current))

    def describe_node(self, node):
        """Get basic details for the current node."""

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
            return "Unknown node (" + str(node) + ")"

    def enter_field(self, field):
        current = self.ast_current
        child = None

        if isinstance(current, ast.AST) and field in current._fields:
            child = getattr(current, field)
        elif isinstance(current, list) and field.isdigit() and int(field) < len(current):
            child = current[int(field)]
        else:
            print("Field does not exist.")
            return False

        if not isinstance(child, ast.AST) and not isinstance(child, list):
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

    def autocomplete(self, before, arg, after):
        if not arg.startswith("-"):
            self._ensure_node_sync()
            current = self.ast_current
            if current != None:
                fields = []
                if isinstance(current, ast.AST):
                    fields = list(current._fields)
                if isinstance(current, list):
                    fields = [str(index) for index in range(len(current))]
                return [field for field in fields if field.startswith(arg)]
        return []
