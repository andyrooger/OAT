"""
Parses ASTs for the console.

"""

import ast
import hashlib
import pickle

from . import commandui

class ParseCommand(commandui.Command):
    """Command to deal with parsing ASTs."""

    def __init__(self):
        commandui.Command.__init__(self, "parse")

        self._opts.add_argument("file", nargs="?", default=None,
                                help="File to parse.")
        group = self._opts.add_mutually_exclusive_group()
        group.add_argument("-l", "--load", action="store_true", default=False,
                           help="Load the AST from its stored form")
        group.add_argument("-s", "--save", action="store_true", default=False,
                           help="Save the AST with markings for later")

        self.ast = ASTStorage()

    def run(self, args):
        """Parse a source file to an AST."""

        if args.file and args.save:
            print("Cannot save to a file.")
            return false

        if args.load and not args.file:
            print("Cannot load without a file.")
            return False

        if not args.load and not args.save and not args.file:
            print("Did nothing.")
            return False

        if args.save:
            if self.ast == None:
                print("There is no AST to save, parse one first.")
                return False
            else:
                try:
                    self.ast.save()
                except AssertionError:
                    print("The AST has been modified, save the source with format and try again.")
                    return False
                except IOError:
                    print("The AST file could not be opened.")
                    return False
                except pickle.PickleError:
                    print("The AST could not be saved.")
                    return False
                else:
                    print("The current AST has been saved to: " + self.ast._ast_file())
        else:
            try:
                self.ast = ASTStorage(args.file, load=args.load)
            except IOError:
                print("The necessary files could not be read.")
                return False
            except SyntaxError:
                print("The file contains incorrect syntax, are you sure it is a Python file?")
                return False
            except (TypeError, pickle.UnpickleError):
                print("Could not use the data in the given file.")
                return False
            except AssertionError:
                print("The AST and source files do not match. You must generate a new AST.")
                return False
            else:
                print("Loaded AST for file: " + args.file)

    def autocomplete(self, before, arg, after):
        if len(before):
            return []
        else:
            return commandui.path_completer(arg)

    def status(self):
        """Show status for the current session."""

        print("Parsed tree: " + str(self.ast))
        if self.ast.filehash != None:
            print("Tree hash: " + self.ast.filehash)


class ASTStorage:
    """Holds an AST along with information about its origin."""

    def __init__(self, fname = None, load = False):
        self.tree = None
        self.file = None
        self.filehash = None
        self.modified = False # Set to true on modification of the AST
        self.augmented = False # Set to true on addition of extra data

        if fname:
            if load:
                self._load(fname)
            else:
                self._parse(fname)

    def _ast_file(self, fname=None):
        """Get the name of the potential AST storage file."""

        if fname == None:
            fname = self.file

        if fname.endswith(".py"):
            return fname[0:-3] + ".ast"
        else:
            return fname + ".ast"

    def _parse(self, fname):
        """
        Parse the filename from the given file.

        Allows IOError if the file cannot be read, SyntaxError if it cannot
        be understood, or TypeError if it is the wrong type.

        """

        source = None

        # Could raise IOError
        with open(fname, "r") as file:
            source = file.read()

        # Could raise SyntaxError or TypeError
        theast = ast.parse(source, filename=fname)

        h = hashlib.sha224()
        h.update(source.encode())

        self.tree = theast
        self.file = fname
        self.filehash = h.hexdigest()
        self.modified = False
        self.augmented = False

    def _load(self, fname):
        """
        Load the given file's AST from disk.

        Raises IOError if the ast or source files cannot be read.
        Raises TypeError or pickle.UnpickleError if the AST file is incorrect
        Raises AssertError if the file has changed.

        """

        # Could raise IOError
        stored = None
        with open(self._ast_file(fname), "rb") as file:
            stored = pickle.load(file)

        # TypeError
        if not isinstance(stored, ASTStorage):
            raise TypeError

        source = None

        # Could raise IOError
        with open(fname, "r") as file:
            source = file.read()

        h = hashlib.sha224()
        h.update(source.encode())

        assert stored.filehash == h.hexdigest()

        self.tree = stored.tree
        self.file = stored.file
        self.filehash = stored.filehash
        self.modified = False # We don't care what the file says
        self.augmented = False

    def save(self):
        """
        Save the given file's AST to disk.

        Raises AssertionError if the AST has changed since parsing the file.
        Raises IOError if the file could not be opened.
        Raises pickle.PickleError if the tree could not be pickled.

        """

        assert not self.modified

        with open(self._ast_file(), "wb") as file:
            pickle.dump(self, file, 3)

        self.augmented = False

    def __str__(self):
        if self.tree == None:
            return "None"

        rep = self.file
        mods = []
        if self.modified:
            mods.append("Modified")
        if self.augmented:
            mods.append("Augmented")
        if mods:
            rep += " ("
            rep += ", ".join(mods)
            rep += ")"

        return rep
