#!/usr/bin/env python3

"""
Parses ASTs for the console.

"""

import ast

try:
    import argparse
except ImportError:
    from thirdparty import argparse

from . import commandui

class ParseCommand(commandui.Command):
    """Command to deal with parsing ASTs."""

    def __init__(self):
        commandui.Command.__init__(self, "parse")

        self._opts.add_argument("file", type=argparse.FileType("r"),
                                help="File to parse.")

        self.parsed_tree = None
        self.parsed_file = None

    def run(self, args):
        """Parse a source file to an AST."""
        
        source = args.file.read()
        args.file.close()

        theast = None
        try:
            theast = ast.parse(source, filename=args.file.name)
        except SyntaxError:
            print("Could not parse the specified file. Are you sure it's Python?")
            return False
        except TypeError:
            print("Could not use the data in the specified file.")
            return False

        self.parsed_tree = theast
        self.parsed_file = args.file.name

    def complete(self, text, line, begidx, endidx):
        return commandui.path_completer(line.rpartition(" ")[2], len(text))

    def status(self):
        """Show status for the current session."""

        print("Parsed tree: ", end="")
        print(self.parsed_tree, end="")
        if self.parsed_file != None:
            print(" : " + self.parsed_file)
        else:
            print()
