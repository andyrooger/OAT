#!/usr/bin/env python3

"""
Command based UI for the obfuscator.

"""

import cmd
import os
import optparse

class CommandUI(cmd.Cmd):
    """Command UI base class, use self.cmdloop() to run."""

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "--) "
        self.intro = ("Welcome to this little obfuscation tool.\n"
                      "If you're confused, type help!")

        self._commands = {}

    def postcmd(self, stop, line):
        print()
        return stop

    def emptyline(self):
        pass

    def _split_line(self, line):
        command, ignore, params = line.partition(" ")
        params = params.lstrip()
        return (command, params)

    def default(self, line):
        # Should look through added commands and call the correct one
        command, params = self._split_line(line)
        try:
            todo = self._commands[command]
        except KeyError:
            return cmd.Cmd.default(self, line)
        else:
            return todo.do(params)

    def do_quit(self, line):
        """Exit the program."""

        return True

    def do_EOF(self, line):
        """Exit the program. Use CTRL^D."""

        print()
        return True

    def completedefault(self, text, line, begidx, endidx):
        # Should look through added commands and call the correct one
        command, params = self._split_line(line)
        try:
            todo = self._commands[command]
        except KeyError:
            return cmd.Cmd.completedefault(self, text, line, begidx, endidx)
        else:
            return todo.complete(text, params, begidx, endidx)

    def do_help(self, line):
        """Get help on a given subject."""

        if not line:
            return self.help_topics()

        # Should check for help in our added commands or fall back
        try:
            todo = self._commands[line]
        except KeyError:
            return cmd.Cmd.do_help(self, line)
        else:
            return todo.help()

    def help_topics(self):
        """Print topics for help. This uses the code from Cmd's implementation."""

        cmds_doc = ["help", "quit", "status"] + list(self._commands.keys())

        self.stdout.write("%s\n"%str(self.doc_leader))
        self.print_topics(self.doc_header,   cmds_doc,   15,80)

    def completenames(self, text, *ignored):
        return cmd.Cmd.completenames(self, text, ignored) + [name for name in self._commands.keys() if name.startswith(text)]

    def add_command(self, command : "interactive.Command to add to the console."):
        """Add a command to the console."""

        self._commands[command.id] = command

    def do_status(self, line):
        """Show status for the current session."""

        for command in self._commands:
            self._commands[command].status()


class CommandOptions(optparse.OptionParser):
    """Child of OptionParser tailored to be used in the command interface."""

    def __init__(self, command):
        optparse.OptionParser.__init__(self,
                                       add_help_option = False,
                                       prog = command)

    def error(self, msg):
        raise OptionError(msg)


class OptionError(ValueError):
    pass


class Command:
    """Base class for any commands to add to the console."""

    def __init__(self, id : "Name of the command"):
        self.id = id

    def do(self, line): pass
    def complete(self, text, params, begidx, endidx): pass
    def status(self): pass

    def help(self):
        if self.do.__doc__:
            print(self.do.__doc__)

    
def path_completer(path : "Full path",
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
