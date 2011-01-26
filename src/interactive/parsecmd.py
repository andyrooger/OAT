#!/usr/bin/env python3

"""
Parses ASTs for the console.

"""

import ast

from . import commandui

class ParseCommand(commandui.Command):
    """Command to deal with parsing ASTs."""

    def __init__(self):
        commandui.Command.__init__(self, "parse")

        self._parsed_tree = None
        self._parsed_file = None

    def do(self, info, line):
        """Parse a source file to an AST."""

        paths = line.split()
        if not paths:
            print("You need to specify a path to parse.")
            return False
        if len(paths) != 1:
            print("Currently only one file may be parsed at a time.")
            return False

        path = paths[0]

        source = None
        try:
            with open(path, "r") as file:
                source = file.read()
        except:
            print("Could not read the specified file.")
            return False

        theast = None

        try:
            theast = ast.parse(source, filename=path)
        except SyntaxError:
            print("Could not parse the specified file. Are you sure it's Python?")
            return False
        except TypeError:
            print("Could not use the data in the specified file.")
            return False

        info["parsed_tree"] = theast
        info["parsed_file"] = path


    def complete(self, info, text, line, begidx, endidx):
        return commandui.path_completer(line.rpartition(" ")[2], len(text))

    def status(self, info):
        """Show status for the current session."""

        print("Parsed tree: ", end="")
        print(info["parsed_tree"], end="")
        if info["parsed_file"] != None:
            print(" : " + info["parsed_file"])
        else:
            print()
