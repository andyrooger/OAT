"""
Reorder statement blocks from the console.

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

from analysis import reorder
from analysis import valuers

from writer import sourcewriter
from writer import prettywriter

from analysis.markers import breaks
from analysis.markers import visible
from analysis.markers import read
from analysis.markers import write
from analysis.markers import scope

from analysis.customast import CustomAST

class ReorderCommand(commandui.Command):
    """Reorder statement blocks from the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "reorder")

        self._opts.add_argument("-d", "--display", choices=["index", "type", "code"], default="type",
                                help="How to display statements, either by index, type or the full code.")
        self._opts.add_argument("-v", "--valuer", choices=["random", "first", "wrange", "rwrange", "rwlogrange", "knots"], default="random",
                                help="Choose the valuer function.")
        self._opts.add_argument("-i", "--invert", action="store_true", default=False,
                                help="Invert the output of the given valuer function.")
        self._opts.add_argument("-e", "--edit", action="store_true", default=False,
                                help="Allow editing of the tree. This is disallowed by default.")
        self._opts.add_argument("-t", "--safetytests", dest="safe", action="store_true", default=False,
                                help="Perform safety tests on the reorderer during calculations. Warning: This could cause significant slow-down.")
        self._opts.add_argument("-r", "--random", action="store_true", default=False,
                                help="Randomise order of output permutations.")
        self._opts.add_argument("-l", "--limit", type=int, default=None,
                                help="Take only the first LIMIT permutations. Combine with --random for a very fast random permutation.")
        actions = self._opts.add_mutually_exclusive_group()
        actions.add_argument("-c", "--current", action="store_const", const="current", dest="do",
                             help="Check if this node can be reordered and print it's current state if so.")
        actions.add_argument("-s", "--split", action="store_const", const="split", dest="do",
                             help="Show statement list partitions. Used for debugging.")
        actions.add_argument("-n", "--number", action="store_const", const="number", dest="do",
                             help="Calculate the total number of permutations we can retrieve for this node.")
        actions.add_argument("-u", "--unique", action="store_const", const="unique", dest="do",
                             help="Calculate the total number of unique permutations we have generated. Used for debugging. Expect MASSIVE memory usage.")
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
            orderer = (reorder.RandomReorderer(block, safe=args.safe, limit=args.limit) if args.random
                      else reorder.Reorderer(block, safe=args.safe, limit=args.limit))
        except TypeError:
            print("The node's body was of unexpected type, I don't know what do do with this.")
            return False

        try:
            self._perform_action(do, block, orderer, args)
        except AssertionError:
            if not args.safe: # Then we shouldn't have got this
                raise
            print("Safety check failed.")

    def _perform_action(self, do, block, orderer, args):
        """Perform the chosen action."""

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
            total = sum(1 for _ in orderer.permutations())
            print("The total number of permutations for this node is " + str(total))
            return

        if do == "unique":
            perms = {
                tuple(perm) for perm in orderer.permutations()
            }
            total = len(perms)
            print("The total number of unique permutations for this node is " + str(total))
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
                "random" : valuers.RandomValuer,
                "first" : valuers.FirstValuer,
                "wrange" : valuers.WriteRangeValuer,
                "rwrange" : valuers.WriteUseValuer,
                "rwlogrange" : valuers.WriteUseLogValuer,
                "knots" : valuers.WriteUseLogValuer,
            }[args.valuer]
            if args.invert:
                valuer = valuers.InvertValuer(valuer)
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
        if not cur.is_list():
            return None
        for stmt in cur:
            if not issubclass(cur[stmt].type(asclass=True), ast.stmt):
                return None
        return cur

    def _set_block(self, block):
        cur = self._related_explorecmd.ast_current
        if cur.is_list():
            cur.become(block) # Throws TypeError if not a list, but could change in future
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
            ord_stat = list(statements.ordered_children())
            for i in perm:
                child = statements[ord_stat[i]]
                if disp == "type":
                     print(str(i) + ": " + child.type(), end="")
                elif disp == "code":
                     print()
                     sourcewriter.printSource(child, prettywriter.PrettyWriter)

                if markings:
                    complete_markings = reorder.Reorderer(CustomAST([child])).check_markings()

                    if complete_markings:
                        print(" - Completely marked")
                    else:
                        print(" - Not marked")
                if disp == "type" or markings:
                    print()

        self._related_parsecmd.ast.augmented = True
