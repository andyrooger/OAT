"""
Write out source for the console.

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

import os

try:
    import argparse
except ImportError:
    from thirdparty import argparse

from . import commandui

from writer import sourcewriter
from writer import basicwriter
from writer import prettywriter

class FormatCommand(commandui.Command):
    """Format and write commands for the console."""

    def __init__(self, parsecmd, explorecmd):
        commandui.Command.__init__(self, "format")

        self._opts.add_argument("-w", "--write", dest="filename",
                                help="Filename to write to. If this is not specified we write to stdout.")
        self._opts.add_argument("-f", action="store_true", default=False, dest="force",
                                help="Force - to overwrite files or do something we may want to check first.")
        group = self._opts.add_mutually_exclusive_group()
        group.add_argument("-c", "--current", action="store_false", dest="top_node", default=False,
                                help="Write the current node (view with explore)")
        group.add_argument("-t", "--top", action="store_true", dest="top_node",
                                help="Write the top node (parsed with parse)")
        self._opts.add_argument("-s", "--style", choices=["basic", "pretty"],
                                help="Style to write source code with. Defaults to pretty.", default="pretty")

        self._related_parsecmd = parsecmd
        self._related_explorecmd = explorecmd

    def run(self, args):
        """Output formatted source from the current AST."""

        self._related_explorecmd._ensure_node_sync()
        towrite = self._related_explorecmd.ast_top if args.top_node else self._related_explorecmd.ast_current

        if not towrite:
            print("You do not have an AST to format!")
            print("Use the parse command to create one.")
            return False

        writer = {
            "basic" : basicwriter.BasicWriter,
            "pretty" : prettywriter.PrettyWriter
        }.get(args.style)

        if args.filename:
            return self.write_to_file(towrite, writer, args.filename, args.force)
        else:
            return self.write_to_stdout(towrite, writer, args.force)


    def write_to_file(self, tree, writer, filename, force):
        if not force and os.path.lexists(filename):
            print("The specified file already exists. Use -f to overwrite.")
            return False

        try:
            with open(filename, "w") as file:
                writer(tree, file).write()
        except IOError:
            print("The file could not be written to.")
        else:
            self._related_parsecmd.ast.file = filename
            self._related_parsecmd.ast.modified = False
            print("Written to: " + filename)


    def write_to_stdout(self, tree, writer, force):
        if not force:
            print("Are you sure you wish to print to stdout?..This could be big!")
            print("Use -f to confirm, otherwise add a filename argument.")
            return False
        sourcewriter.printSource(tree, writer)

