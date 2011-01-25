#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

import cmd
import os
import ast

from writer import sourcewriter
from writer import basicwriter

class CommandUI(cmd.Cmd):
    """Command UI class, use self.cmdloop() to run."""

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "--) "
        self.intro = ("Welcome to this little obfuscation tool.\n"
                      "If you're confused, type help!")

        self._parsed_tree = None
        self._parsed_file = None


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
        print(self._parsed_tree, end="")
        if self._parsed_file != None:
            print(" : " + self._parsed_file)
        else:
            print()

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
        self._parsed_file = path

    def complete_parse(self, text, line, begidx, endidx):
        return self.path_completer(line.rpartition(" ")[2], len(text))


    def format(self, line : "As given to do_*", force : "Do we perform sanity checks or forget them?"):
        """Output formatted source from the current AST."""

        args = line.split()

        if not self._parsed_tree:
            print("You do not have an AST to format!")
            print("Use the parse command to create one.")
            return False

        if len(args) > 1:
            print("Too many arguments, I don't know what you mean!")
            return False

        if args:
            path = args[0]

            if not force and os.path.lexists(path):
                print("The specified file already exists. Use fformat overwrite.")
                return False

            try:
                with open(path, "w") as file:
                    basicwriter.BasicWriter(self._parsed_tree, file).write()
                print("Written.")
            except IOError:
                print("The file could not be written to.")
        else:
            if not force:
                print("Are you sure you wish to print to stout?..This could be big!")
                print("Use fformat to confirm, otherwise add a filename argument.")
                return False
            sourcewriter.printSource(self._parsed_tree, basicwriter.BasicWriter)


    def do_format(self, line):
        """Output formatted source from the current AST without causing harm."""

        self.format(line, False)

    def do_fformat(self, line):
        """Like format but with force."""

        self.format(line, True)
