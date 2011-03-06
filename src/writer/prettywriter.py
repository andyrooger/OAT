"""
Tries to write the source in an attractive way. Most functionality comes
from basicwriter.

"""

import ast
import sys

from . import sourcewriter
from . basicwriter import BasicWriter

class PrettyWriter(BasicWriter):
    """
    Writes pretty source from an AST.

    Extends the basic writer's functionality to print readable code.

    >>> import ast
    >>> from . import sourcewriter
    >>> theast = None
    >>> with open("../example/stuff.py") as file:
    ...     theast = ast.parse(file.read(), "startup.py", "exec")
    >>> with open("../example/stuff.py.prettyformat") as file:
    ...         file.read() == sourcewriter.srcToStr(theast, PrettyWriter)
    True

    """

    def __init__(self,
                 top_ast : "The AST to be printed" = None,
                 out : "Output file" = sys.stdout):

        BasicWriter.__init__(self, top_ast, out)

    ###############################
    # Docstrings
    ###############################

    def _write_Expr(self, tree):
        """
        Write out an expression.

        Should only be called when the expression is a statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... def myfunc():
        ...     \"\"\"
        ...     I am a multiline docstring...
        ...     See!
        ...     \"\"\"
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, PrettyWriter)
        def myfunc():
            \"\"\"
            I am a multiline docstring...
            See!
        <BLANKLINE>
            \"\"\"

        """

        if self._node_type(tree.value) == "Str":
            self._write_docstring(tree.value)
        else:
            self._write(tree.value)


    def _write_docstring(self, doc : "Docstring to write"):
        """Write Str as a docstring."""

        clean = []
        for c in self._clean_docstring(doc.s):
            c = c.replace('\\', '\\\\') # first to avoid ruining later replaces
            c = c.replace('"', '\\"') # so we can enclose with """
            c = c.replace('\r', '\\r')
            c = c.replace('\t', '\\t')
            clean.append(c)

        if len(clean) == 0: # Empty
            self._write("\"\"\"\"\"\"")
        elif len(clean) < 2: # Single line
            self._write("\"\"\"")
            self._write(clean[0])
            self._write("\"\"\"")
        else: # multiline
            char_lv = self._char_level()
            if char_lv > 0:
                self._inc_indent(" "*char_lv)
            self._write("\"\"\"")
            self._next_statement()
            self._interleave_write(clean, after=self._next_statement)
            self._next_statement() # blank line
            self._write("\"\"\"")
            if char_lv > 0:
                self._dec_indent()

    def _clean_docstring(self, doc : "str to clean"):
        """
        Return a doc as a list of cleaned lines.

        Taken mostly from PEP 0257.
        """

        if not doc:
            return ['']

        # Split lines and remove tabs
        lines = doc.expandtabs(4).splitlines() # assume 4 spaces per tab

        # Figure indentation level
        indent = sys.maxsize
        for line in lines[1:]:
            stripped = line.lstrip()
            if stripped:
                indent = min(indent, len(line) - len(stripped))

        # Remove indentation
        trimmed = [lines[0].strip()]
        if indent < sys.maxsize:
            for line in lines[1:]:
                trimmed.append(line[indent:].rstrip())

        # Remove leading and trailing blank lines
        while trimmed and not trimmed[-1]:
            trimmed.pop()
        while trimmed and not trimmed[0]:
            trimmed.pop(0)

        return trimmed

    ###############################
    # Arguments
    ###############################

    def _write_arguments(self, tree):
        """
        Write out a list of arguments.

        This will prettify the output by using new lines wherever
        default values or annotations are used in the arguments.

        >>> import ast
        >>> from . import sourcewriter
        >>> a = ast.parse('def f(a): pass')
        >>> sourcewriter.printSource(a, PrettyWriter)
        def f(a):
            pass
        >>> b = ast.parse('def g(b : "hi"): pass')
        >>> sourcewriter.printSource(b, PrettyWriter)
        def g(b : 'hi'):
            pass
        >>> c = ast.parse('def h(b : "hi", c : "Bye"): pass')
        >>> sourcewriter.printSource(c, PrettyWriter)
        def h(b : 'hi',
              c : 'Bye'):
            pass

        """

        if self._has_defaults(tree) or self._has_annotations(tree):
            self._write_newlineargs(tree)
        else:
            super()._write_arguments(tree)


    def _has_defaults(self, tree):
        """
        Check if an argument object has any arguments with defaults.

        """

        return tree.defaults != None or tree.kw_defaults != None


    def _has_annotations(self, tree):
        """
        Check if an argument object has any arguments with annotations.

        """

        for arg in tree.args:
            if arg.annotation != None:
                return True

        if tree.varargannotation != None:
            return True

        for arg in tree.kwonlyargs:
            if arg.annotation != None:
                return True

        if tree.kwargannotation != None:
            return True

        return False


    def _write_newlineargs(self, tree):
        """
        Write arguments object with newlines between arguments.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... def myfunc(a, b : "Hello", c : "Goodbye" = 2):
        ...     pass
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, PrettyWriter)
        def myfunc(a,
                   b : 'Hello',
                   c : 'Goodbye' = 2):
            pass

        """

        char_lv = self._char_level()
        if char_lv > 0:
            self._inc_indent(" "*char_lv)

        had_arg = False # Cannot use _separated_write here
        n_posargs = len(tree.args) - len(tree.defaults)

        # positional args
        for arg in tree.args[:n_posargs]:
            if had_arg:
                self._write(",")
                self._next_statement()
            had_arg = True
            self._write(arg)

        # keyword args
        for (arg, default) in zip(tree.args[n_posargs:], tree.defaults):
            if had_arg:
                self._write(",")
                self._next_statement()
            had_arg = True
            self._write(arg)
            self._write(" = ")
            self._write(default)

        # variable positional args
        if tree.vararg != None:
            if had_arg:
                self._write(",")
                self._next_statement()
            had_arg = True
            self._write("*")
            self._write(tree.vararg)
            if tree.varargannotation != None:
                self._write(" : ")
                self._write(tree.varargannotation)
        elif tree.kwonlyargs:
            if had_arg:
                self._write(",")
                self._next_statement()
            had_arg = True
            self._write("*")

        # keyword only args
        for (arg, default) in zip(tree.kwonlyargs, tree.kw_defaults):
            if had_arg:
                self._write(",")
                self._next_statement()
            had_arg = True
            self._write(arg)
            self._write(" = ")
            self._write(default)

        # variable keyword args
        if tree.kwarg != None:
            if had_arg:
                self._write(",")
                self._next_statement()
            had_arg = False
            self._write("**")
            self._write(tree.kwarg)
            if tree.kwargannotation != None:
                self._write(" : ")
                self._write(tree.kwargannotation)

        if char_lv > 0:
            self._dec_indent()

    ###############################
    # Arguments
    ###############################

    def _write_block(self,
                     stmts : "List of statements inside the block.",
                     indent : "Should we be indenting?" = True):
        """Write a list of statements, each on a new line in a new indentation level."""

        if indent:
            super()._write_block(stmts, True)
        else:
            split_stmts = self._split_block(stmts)

            if split_stmts:
                # First group as before
                super()._write_block(split_stmts[0], False)

                # Other groups preceded with newline
                for group in split_stmts[1:]:
                    self._next_statement()
                    self._interleave_write(group, before=self._next_statement)

    def _split_block(self, stmts):
        """
        Take a block and split into groups of related instructions.

        >>> import ast
        >>> instructions = [
        ...     ast.Import(),
        ...     ast.Import(),
        ...     ast.FunctionDef(),
        ...     ast.ClassDef(),
        ...     ast.Return()
        ... ]
        >>> spl = PrettyWriter(ast.AST())._split_block(instructions)
        >>> for s in spl:
        ...     print([x.__class__.__name__ for x in s])
        ['Import', 'Import']
        ['FunctionDef']
        ['ClassDef']
        ['Return']

        """

        current = [] # Current statement list
        total = [] # Total statement grouping

        for stmt in stmts:
            if self._statement_new_group(current, stmt):
                if current:
                    total.append(current)
                    current = [stmt]
            else:
                current.append(stmt)

        if current: # Append last group
            total.append(current)

        return total

    def _statement_new_group(self, oldgroup, statement):
        """Check if a statement should be in the same group or a new one."""

        single_nodes = set([ # Nodes to always be in their own group
            "Module", "Interactive", "Expression", "Suite",
            "FunctionDef", "ClassDef", "Return",
            "For", "While", "If", "With",
            "TryExcept", "TryFinally"
        ])

        grouped_nodes = set([ # Nodes to group with others of the same type
            ("Import", "ImportFrom"),
            ("Global", "NonLocal")
        ])

        if not oldgroup:
            return False # Current group is empty to doesn't matter
        else:
            node_type = statement.__class__.__name__
            prev_node = oldgroup[-1].__class__.__name__

            if node_type in single_nodes:
                return True

            for group in grouped_nodes: # Look through grouped nodes
                if node_type in group: # We found our group
                    return prev_node not in group # new if we're the first in this group

            return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
