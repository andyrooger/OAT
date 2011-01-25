#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

import cmd


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
