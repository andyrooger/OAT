#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

import os

from . import commandui

from writer import sourcewriter
from writer import basicwriter

class FormatCommand(commandui.Command):
    """Format and write commands for the console."""

    def __init__(self):
        commandui.Command.__init__(self, "format")

        opts = commandui.CommandOptions("format")
        opts.add_option("-w", "--write", dest="filename",
                        help="Filename to write to. If this is not specified we write to stdout.")
        opts.add_option("-f", action="store_true", default=False, dest="force",
                        help="Force - to overwrite files or do something we may want to check first.")
        self._format_options = opts

        self._source_writer = basicwriter.BasicWriter

    def do(self, info, line):
        """Output formatted source from the current AST."""

        if "parsed_tree" not in info or not info["parsed_tree"]:
            print("You do not have an AST to format!")
            print("Use the parse command to create one.")
            return False

        try:
            (options, args) = self._format_options.parse_args(line.split())
        except OptionError as exc:
            print(str(exc))
            return False
        else:
            if args:
                print("Unrecognised options: " + ",".join(args))
                return False
            if options.filename:
                return self.write_to_file(info["parsed_tree"], options.filename, options.force)
            else:
                return self.write_to_stdout(info["parsed_tree"], options.force)

    def write_to_file(self, tree, filename, force):
        if not force and os.path.lexists(filename):
            print("The specified file already exists. Use -f to overwrite.")
            return False

        try:
            with open(filename, "w") as file:
                self._source_writer(tree, file).write()
            print("Written to: " + filename)
        except IOError:
            print("The file could not be written to.")

    def write_to_stdout(self, tree, force):
        if not force:
            print("Are you sure you wish to print to stout?..This could be big!")
            print("Use -f to confirm, otherwise add a filename argument.")
            return False
        sourcewriter.printSource(tree, self._source_writer)

    def help(self):
        print(self.do.__doc__)
        print()
        self._format_options.print_help()

