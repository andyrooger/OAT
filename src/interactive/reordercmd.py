"""
Reorder statement blocks from the console.

"""

import ast

from . import commandui

class ReorderCommand(commandui.Command):
    """Reorder statement blocks from the console."""

    def __init__(self, explorecmd):
        commandui.Command.__init__(self, "reorder")

        self._opts.add_argument("-c", "--check", action="store_true", default=False,
                                help="Only check if this node can be reordered.")
        group = self._opts.add_mutually_exclusive_group()
        group.add_argument("-r", "--random", action="store_true", default=False,
                           help="Choose a permutation randomly.")
        group.add_argument("-v", "--value", metavar="FUNC", choices=["default"], default=None,
                           help="Choose the permutation with the highest value given by FUNC.")

        self._related_explorecmd = explorecmd

    def run(self, args):
        """Reorder the body of statements for the current node."""

        self._related_explorecmd._ensure_node_sync()

        if self._related_explorecmd.ast_current == None:
            print("There is no AST to reorder. Have you create one with the parse command?")
            return False

        block = self._get_block()

        if block == None:
            print("This node has no body to reorder.")
            return False

        if args.check:
            print("This node's body can be reordered.")
            return

    def _get_block(self):
        cur = self._related_explorecmd.ast_current
        if hasattr(cur, "_fields") and "body" in cur._fields:
            return cur.body
        else:
            return None

