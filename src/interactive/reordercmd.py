"""
Reorder statement blocks from the console.

"""

import ast

from . import commandui

from analysis import reorder

from writer import sourcewriter
from writer import prettywriter

from analysis.markers import breaks
from analysis.markers import visible
from analysis.markers import read
from analysis.markers import write
from analysis.markers import scope

class ReorderCommand(commandui.Command):
    """Reorder statement blocks from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "reorder")

        self._opts.add_argument("-d", "--display", choices=["index", "type", "code"], default="type",
                                help="How to display statements, either by index, type or the full code.")
        self._opts.add_argument("-v", "--valuer", choices=["random", "first"], default="random",
                                help="Choose the valuer function.")
        self._opts.add_argument("-e", "--edit", action="store_true", default=False,
                                help="Allow editing of the tree. This is disallowed by default.")
        actions = self._opts.add_mutually_exclusive_group()
        actions.add_argument("-c", "--current", action="store_const", const="current", dest="do",
                             help="Check if this node can be reordered and print it's current state if so.")
        actions.add_argument("-s", "--split", action="store_const", const="split", dest="do",
                             help="Show statement list partitions. Used for debugging.")
        actions.add_argument("-n", "--number", action="store_const", const="number", dest="do",
                             help="Calculate the total number of permutations we can retrieve for this node.")
        actions.add_argument("-p", "--permutations", action="store_const", const="permutations", dest="do",
                             help="Show all possible permutations for the arguments. Used for debugging.")
        actions.add_argument("-b", "--best", action="store_const", const="best", dest="do",
                             help="Find the best permutation of these instructions according to the given valuer function. This is the default action.")

        self._related_parsecmd = parsecmd
        self._related_explorecmd = explorecmd

    def run(self, args):
        """Reorder the body of statements for the current node."""

        # Get action
        do = "best" if args.do == None else args.do

        self._related_explorecmd._ensure_node_sync()

        if self._related_explorecmd.ast_current == None:
            print("There is no AST to reorder. Have you create one with the parse command?")
            return False

        block = self._get_block()

        if block == None:
            print("This node is not reorderable.")
            return False

        try:
            orderer = reorder.Reorderer(block)
        except TypeError:
            print("The node's body was of unexpected type, I don't know what do do with this.")
            return False

        if do == "current":
            self._print_block(block, range(len(block)), args.display, True)
            if orderer.check_markings():
                print("The statements can be reordered.")
            else:
                print("The statements are not fully marked up, so cannot be reordered.")
            return

        if not orderer.check_markings():
            print("The statements are not fully marked up, so cannot be reordered.")
            return False

        if do == "split":
            for part in orderer.partition():
                self._print_block(block, part, args.display)
                print("---")
            return

        if do == "number":
            # No len for generators
            total = 0
            for p in orderer.permutations():
                total += 1
            print("The total number of permutations for this node is " + str(total))
            return

        if do == "permutations":
            for perm in orderer.permutations():
                self._print_block(block, perm, args.display)
                try:
                    print()
                    input('Press enter to continue...')
                except EOFError: pass
                print()

            print("There are no other permutations.")
            return

        if do == "best":
            valuer = {
                "random" : reorder.RandomValuer,
                "first" : reorder.FirstValuer,
            }[args.valuer]
            perm = orderer.best_permutation(valuer)

            self._print_block(block, perm, args.display)

            print()
            if args.edit:
                self._set_block(orderer.permute(perm))
                print("The node has been reordered.")
            else:
                print("This is the optimal chosen rearrangement. To write to the node see --edit.")
            return

        print("The action, " + do + ", has not been implemented yet.") # Shouldn't get here


    def _get_block(self):
        cur = self._related_explorecmd.ast_current
        if not isinstance(cur, list):
            return None
        for stmt in cur:
            if not isinstance(stmt, ast.stmt):
                return None
        return cur

    def _set_block(self, block):
        cur = self._related_explorecmd.ast_current
        if isinstance(cur, list):
            cur[:] = block
            self._related_parsecmd.ast.modified = True
        else:
            raise TypeError

    def _print_block(self, statements, perm, disp, markings=False):
        """Print a block of statements in a particular permutation."""

        if disp == "index":
            for i in perm:
                print(str(i) + " - ", end="")
            print()

        else:
            for i in perm:
                if disp == "type":
                     print(str(i) + ": " + statements[i].__class__.__name__, end="")
                elif disp == "code":
                     print()
                     sourcewriter.printSource(statements[i], prettywriter.PrettyWriter)

                if markings:
                    complete_markings = reorder.Reorderer([statements[i]]).check_markings()

                    if complete_markings:
                        print(" - Completely marked")
                    else:
                        print(" - Not marked")
                if disp == "type" or markings:
                    print()

        self._related_parsecmd.ast.augmented = True
