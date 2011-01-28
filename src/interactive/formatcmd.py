#!/usr/bin/env python3

"""
Write out source for the console.

"""

import os

try:
    import argparse
except ImportError:
    from thirdparty import argparse

from . import commandui

from writer import sourcewriter
from writer import basicwriter

class FormatCommand(commandui.Command):
    """Format and write commands for the console."""

    def __init__(self, parsecmd):
        commandui.Command.__init__(self, "format")

        self._opts.add_argument("-w", "--write", dest="filename",
                                help="Filename to write to. If this is not specified we write to stdout.")
        self._opts.add_argument("-f", action="store_true", default=False, dest="force",
                                help="Force - to overwrite files or do something we may want to check first.")

        self._related_parsecmd = parsecmd
        self.source_writer = basicwriter.BasicWriter

    def run(self, args):
        """Output formatted source from the current AST."""

        if not self._related_parsecmd.parsed_tree:
            print("You do not have an AST to format!")
            print("Use the parse command to create one.")
            return False

        if args.filename:
            return self.write_to_file(self._related_parsecmd.parsed_tree, args.filename, args.force)
        else:
            return self.write_to_stdout(self._related_parsecmd.parsed_tree, args.force)


    def write_to_file(self, tree, filename, force):
        if not force and os.path.lexists(filename):
            print("The specified file already exists. Use -f to overwrite.")
            return False

        try:
            with open(filename, "w") as file:
                self.source_writer(tree, file).write()
            print("Written to: " + filename)
        except IOError:
            print("The file could not be written to.")

    def write_to_stdout(self, tree, force):
        if not force:
            print("Are you sure you wish to print to stout?..This could be big!")
            print("Use -f to confirm, otherwise add a filename argument.")
            return False
        sourcewriter.printSource(tree, self.source_writer)

