"""
Command based UI for the obfuscator.

"""

import cmd
import os

try:
    import argparse
except ImportError:
    from thirdparty import argparse

class CommandUI(cmd.Cmd):
    """Command UI base class, use self.cmdloop() to run."""

    def __init__(self):
        cmd.Cmd.__init__(self)
        self.prompt = "--) "
        self.intro = ("Welcome to this little obfuscation tool.\n"
                      "If you're confused, type help!")

        self._commands = {}

    def cmdloop(self, intro = None):
        """Un-KeyboardInterrup-able cmdloop."""
        try:
            super().cmdloop(intro)
        except KeyboardInterrupt:
            print()
            self.cmdloop("")

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


class Command:
    """Base class for any commands to add to the console."""

    def __init__(self, id : "Name of the command"):
        self._opts = Command.CommandArgs(description = self.run.__doc__,
                                         add_help = False,
                                         prog = id)
        self.id = id

    def do(self, line):
        try:
            args = self._opts.parse_args(line.split())
        except ValueError as exc:
            print("Problem: " + str(exc))
            print()
            self.help()
            return False
        except IOError as exc:
            print(exc.strerror + ": " + exc.filename)
        else:
            return self.run(args)

    def complete(self, text, line, begidx, endidx):
        beg = begidx - len(self.id) - 1
        end = endidx - len(self.id) - 1
        begarg = line.rfind(" ", None, end) + 1
        endarg = end #line.rfind(" ", beg, None)
        if begarg == -1:
            begarg = 0
        if endarg == -1:
            endarg = len(line)
        arg = line[begarg:endarg]
        before = line[:begarg].split()
        after = line[endarg:].split()
        completions = self.autocomplete(before, arg, after)
        return [completion[len(arg)-len(text):] for completion in completions]

    def run(self, args): raise NotImplementedError
    def autocomplete(self, before, arg, after): return []
    def status(self): pass

    def help(self):
        self._opts.print_help()

    class CommandArgs(argparse.ArgumentParser):
        """Child of OptionParser tailored to be used in the command interface."""

        def __init__(self, *args, **kwargs):
            argparse.ArgumentParser.__init__(self, *args, **kwargs)

        def error(self, msg):
            raise ValueError(msg)

    
def path_completer(path : "Path to complete"):
    """Completer for file paths."""

    directory, base = os.path.split(path)
    entries = []

    try:
        if directory:
            entries = os.listdir(directory)
        else:
            entries = os.listdir(os.getcwd())
    except OSError:
        entries = []

    suggestions = [os.path.join(directory, file) for file in entries if file.startswith(base)]
    return suggestions
