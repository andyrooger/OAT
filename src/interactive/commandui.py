#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

import cmd
import os
import ast

class CommandUI(cmd.Cmd):
    """Command UI class, use self.cmdloop() to run."""

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "--) "
        self.intro = ("Welcome to this little obfuscation tool.\n"
                      "If you're confused, type help!")

        self._parsed_tree = None


    def do_quit(self, line):
        """Exit the program."""

        return True


    def do_EOF(self, line):
        """Exit the program. Use CTRL^D."""

        print()
        return True

    def postcmd(self, stop, line):
        print()
        return stop

    def emptyline(self):
        pass

    def do_status(self, line):
        """Show status for the current session."""

        print("Parsed tree: ", end="")
        print(self._parsed_tree)

    def path_completer(self,
                       path : "Full path",
                       suffix : "Length of suffix to replace/extend"):
        """Completer for file paths."""

        directory, base = os.path.split(path)
        fixed = path[:-suffix] if suffix else path
        fixed_l = len(fixed)
        entries = []

        try:
            if directory:
                entries = os.listdir(directory)
            else:
                entries = os.listdir(os.getcwd())
        except OSError:
            entries = []

        suggestions = [os.path.join(directory, file) for file in entries if file.startswith(base)]

        replaceables = [file[fixed_l:] for file in suggestions if file.startswith(fixed)]

        return replaceables

    
    def do_parse(self, line):
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

        self._parsed_tree = theast

    def complete_parse(self, text, line, begidx, endidx):
        return self.path_completer(line.rpartition(" ")[2], len(text))
