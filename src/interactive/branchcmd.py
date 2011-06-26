"""
Branch statement lists from the console.

"""

import ast

from . import commandui

from analysis.brancher import Brancher
from analysis.customast import CustomAST

class BranchCommand(commandui.Command):
    """Branch statement blocks from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "branch")

        self._opts.add_argument("name", default=None, nargs="?", type=str,
                                help="Name of a brancher collection.")
        self._opts.add_argument("-c", "--create", action="store_true", default=False,
                                help="Create brancher if it does not exist.")
        self._opts.add_argument("--remove", action="store_true", default=False,
                                help="Remove a given brancher or item.")
#        self._opts.add_argument("-d", "--display", choices=["index", "type", "code"], default="type",
#                                help="How to display statements, either by index, type or the full code.")
        actions = self._opts.add_mutually_exclusive_group()
        actions.add_argument("-p", "--predicate", action="store", type=int, nargs="?", default=None, const=True,
                             help="Display, add or alter a predicate in this brancher.")
        actions.add_argument("-e", "--exception", action="store", type=int, nargs="?", default=None, const=True,
                             help="Display, add or alter an exception causing expression in this brancher.")
        actions.add_argument("-i", "--initial", action="store", type=int, nargs="?", default=None, const=True,
                             help="Display, add or alter an initial statement for this brancher.")
        actions.add_argument("-v", "--preserves", action="store", type=int, nargs="?", default=None, const=True,
                             help="Display, add or alter a predicate preserving statement for this brancher.")
        actions.add_argument("-d", "--destroys", action="store", type=int, nargs="?", default=None, const=True,
                             help="Display, add or alter a predicate unstabilising statement for this brancher.")
        actions.add_argument("-r", "--randomises", action="store", type=int, nargs="?", default=None, const=True,
                             help="Display, add or alter a predicate randomising statement for this brancher.")
        actions.add_argument("-s", "--save", action="store_true", default=False,
                             help="Save a brancher object.")
        actions.add_argument("-l", "--load", action="store_true", default=False,
                             help="Load a brancher object.")


        self._related_parsecmd = parsecmd
        self._related_explorecmd = explorecmd

        self._branchers = {}

    def run(self, args):
        """Extract part of the current block of statements into a separate branch."""

        if args.name == None:
            if not self._branchers:
                print("There are no branchers available yet. You must create some.")
                return
            else:
                print("Available branchers are:")
                for brancher in self._branchers:
                    print("  " + brancher)
                return

        if args.name not in self._branchers:
            if args.create:
                self._branchers[args.name] = Brancher(args.name)
                print("Brancher created: " + args.name)
            else:
                print("The brancher requested does not exist: " + args.name)
                return

        brancher = self._branchers[args.name]

        # Are we editing the brancher?
        for arg in {"predicate", "exception", "initial", "preserves", "destroys", "randomises"}:
            val = getattr(args, arg)
            if val != None:
                self._brancher_edit(brancher, arg, val, args)
                return # updating the branch

        for arg in {"load", "save"}:
            if getattr(args, arg):
                return # Loading or saving

        # Must be asking about the brancher

        print(brancher)

        if args.remove:
            if self._confirm("remove this brancher", False):
                del self._branchers[args.name]
                print("Brancher deleted: " + args.name)
            else:
                print("Deletion cancelled.")

        return

#        # Get action
#        do = "best" if args.do == None else args.do
#
#        self._related_explorecmd._ensure_node_sync()
#
#        if self._related_explorecmd.ast_current == None:
#            print("There is no AST to reorder. Have you create one with the parse command?")
#            return False
#
#        block = self._get_block()
#
#        if block == None:
#            print("This node is not reorderable.")
#            return False
#
#        try:
#            orderer = (reorder.RandomReorderer(block, safe=args.safe, limit=args.limit) if args.random
#                      else reorder.Reorderer(block, safe=args.safe, limit=args.limit))
#        except TypeError:
#            print("The node's body was of unexpected type, I don't know what do do with this.")
#            return False
#
#        try:
#            self._perform_action(do, block, orderer, args)
#        except AssertionError:
#            if not args.safe: # Then we shouldn't have got this
#                raise
#            print("Safety check failed.")
#
#    def _get_block(self):
#        cur = self._related_explorecmd.ast_current
#        if not cur.is_list():
#            return None
#        for stmt in cur:
#            if not issubclass(cur[stmt].type(asclass=True), ast.stmt):
#                return None
#        return cur
#
#    def _set_block(self, block):
#        cur = self._related_explorecmd.ast_current
#        if cur.is_list():
#            cur.become(block) # Throws TypeError if not a list, but could change in future
#            self._related_parsecmd.ast.modified = True
#        else:
#            raise TypeError
#
#    def _print_block(self, statements, perm, disp, markings=False):
#        """Print a block of statements in a particular permutation."""
#
#        if disp == "index":
#            for i in perm:
#                print(str(i) + " - ", end="")
#            print()
#
#        else:
#            ord_stat = list(statements.ordered_children())
#            for i in perm:
#                child = statements[ord_stat[i]]
#                if disp == "type":
#                     print(str(i) + ": " + child.type(), end="")
#                elif disp == "code":
#                     print()
#                     sourcewriter.printSource(child, prettywriter.PrettyWriter)
#
#                if markings:
#                    complete_markings = reorder.Reorderer(CustomAST([child])).check_markings()
#
#                    if complete_markings:
#                        print(" - Completely marked")
#                    else:
#                        print(" - Not marked")
#                if disp == "type" or markings:
#                    print()
#
#        self._related_parsecmd.ast.augmented = True

    def _brancher_edit(self, brancher, category, info, args):
        """Deal with a request for part of a specific brancher."""

        if info is True: # because 1 == True
            self._brancher_add(brancher, category)
            return
        else:
            attrib = {
                "predicate": "predicates",
                "exception": "exceptions",
                "initial": "initial",
                "preserves": "preserving",
                "destroys": "destroying",
                "randomises": "randomising"
            }[category]
            col = getattr(brancher, attrib)
            try:
                item = col.stringify(info)
                print(attrib.title() + " " + str(info) + ":")
                print("  " + item)
            except KeyError:
                print("Could not find ID: " + str(info))
                return

            if args.remove:
                if self._confirm("remove this item", False):
                    del col[info]
                    print("Item deleted: " + attrib.title() + " " + str(info))
                else:
                    print("Deletion cancelled.")

            return

    def _brancher_add(self, brancher, category):
        """Add a new item to the brancher of the given category."""

        if category == "predicate":
            print("Please input a predicate along with its expected value.")
            node = self._code_input("Predicate: ", True)
            if node == None:
                return
            expected = self._choice("Value (True or False): ", ["True", "False"])
            brancher.predicates.add(CustomAST(node), expected)
        else:
            raise ValueError("Cannot create a new item in category: " + category)


    def _code_input(self, prompt, expr):
        try:
            source = input(prompt)
        except EOFError:
            print()
            return None

        if expr:
            try:
                parsed = ast.parse(source, mode="eval")
            except SyntaxError as exc:
                print("Expression could not be parsed: " + str(exc))
                return None
            return parsed.body
        else: # we want a statement
            try:
                parsed = ast.parse(source, mode="exec")
            except SyntaxError as exc:
                print("Statement could not be parsed: " + str(exc))
                return None
            if len(parsed.body) != 1:
                print("Source does not represent a single statement.")
                return None
            return parsed.body[0]

    def _confirm(self, prompt, default=False):
        """Confirm a request."""

        try:
            r = input("Are you sure you wish to " + prompt + " (y/n)? ")
        except EOFError:
            return default

        if r == "y":
            return True
        if r == "n":
            return False
        return default
        

    def _choice(self, prompt, choices):
        """Ask the user to make a choice."""

        answer = None

        while answer == None:
            try:
                answer = input(prompt)
            except EOFError:
                print()
                answer = None
            if answer not in choices:
                print("You must choose one of " + ", ".join(choices) + ".")
                answer = None

        return answer

    def autocomplete(self, before, arg, after):
        if not arg.startswith("-"):
            return [f for f in self._branchers if f.startswith(arg)]
        return []
