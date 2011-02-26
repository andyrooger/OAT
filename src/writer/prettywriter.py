#!/usr/bin/env python3

"""
Tries to write the source in an attractive way. Most functionality comes
from basicwriter.

"""

import ast
import sys

import sourcewriter
from basicwriter import BasicWriter

class PrettyWriter(BasicWriter):
    """
    Writes pretty source from an AST.

#    Extends the basic writer's functionality to print readable code.

#    One option would have been to build an ast walker from the given walker
#    classes, but I want a definite order. (None specified in the docs).

#    >>> import ast, sourcewriter
#    >>> theast = None
#    >>> with open("../../example/startup.py") as file:
#    ...     theast = ast.parse(file.read(), "startup.py", "exec")
#    >>> type(theast)
#    <class '_ast.Module'>
#    >>> with open("../../example/startup.py.basicformat") as file:
#    ...         file.read() == sourcewriter.srcToStr(theast, BasicWriter)
#    True

    """

    def __init__(self,
                 top_ast : "The AST to be printed" = None,
                 out : "Output file" = sys.stdout):
        """
#        Create the writer.

#        >>> BasicWriter("hello world")
#        Traceback (most recent call last):
#            ...
#        TypeError: The tree needs to begin with an AST node.
#        >>> import ast
#        >>> myast = ast.AST()
#        >>> myast = BasicWriter(myast)

        """

        BasicWriter.__init__(self, top_ast, out)

    def _write_Expr(self, tree):
        """
        Write out an expression.

        Should only be called when the expression is a statement.

        >>> import ast, sourcewriter
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

        if len(clean) < 2: # Single line (or none)
            self._write("\"\"\"")
            self._write(clean)
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
