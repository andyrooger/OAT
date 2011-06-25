"""
Branch statement lists from the console.

"""

import ast

from . import commandui

from analysis import brancher

from analysis.customast import CustomAST

class BranchCommand(commandui.Command):
    """Branch statement blocks from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "branch")

        self._opts.add_argument("name", default=None, nargs="?",
                                help="Name of a brancher collection.")
#        self._opts.add_argument("-d", "--display", choices=["index", "type", "code"], default="type",
#                                help="How to display statements, either by index, type or the full code.")
        actions = self._opts.add_mutually_exclusive_group()
        actions.add_argument("-p", "--predicate", action="store", type=int, default=None,
                             help="Display, add or alter a predicate in this brancher.")
        actions.add_argument("-e", "--exception", action="store", type=int, default=None,
                             help="Display, add or alter an exception causing expression in this brancher.")
        actions.add_argument("-i", "--initial", action="store", type=int, default=None,
                             help="Display, add or alter an initial statement for this brancher.")
        actions.add_argument("--preserves", action="store", type=int, default=None,
                             help="Display, add or alter a predicate preserving statement for this brancher.")
        actions.add_argument("-d", "--destroys", action="store", type=int, default=None,
                             help="Display, add or alter a predicate unstabilising statement for this brancher.")
        actions.add_argument("-r", "--randomises", action="store", type=int, default=None,
                             help="Display, add or alter a predicate randomising statement for this brancher.")
        actions.add_argument("-s", "--save", action="store_true", default=False,
                             help="Save a brancher object.")
        actions.add_argument("-l", "--load", action="store_true", default=False,
                             help="Load a brancher object.")


        self._related_parsecmd = parsecmd
        self._related_explorecmd = explorecmd

    def run(self, args):
        """Extract part of the current block of statements into a separate branch."""

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
