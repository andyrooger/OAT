#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

import cmd
import os

class CommandUI(cmd.Cmd):
    """Command UI class, use self.cmdloop() to run."""

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "--) "
        self.intro = ("Welcome to this little obfuscation tool.\n"
                      "If you're confused, type help!")


    def do_quit(self, line):
        """Exit the program."""

        return True


    def do_EOF(self, line):
        """Exit the program. Use CTRL^D."""

        print()
        return True


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

        pass

    def complete_parse(self, text, line, begidx, endidx):
        return self.path_completer(line.rpartition(" ")[2], len(text))
