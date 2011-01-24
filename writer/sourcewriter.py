#!/usr/bin/env python3

"""
Holds the abstract base class for source writers.

It should somehow take an AST and output correct source. This only performs
simple tasks that will be needed by all writers.

"""

import ast
import abc
import sys

class SourceWriter(metaclass = abc.ABCMeta):
    """
    Base class for creating source writers.

    This only performs basic functionality common to any writer.
    Additionally it will define abstract methods for all the types in
    the ast definition here: http://docs.python.org/py3k/library/ast.html

    """

    def __init__(self,
                 top_ast : "The AST to be printed",
                 out : "Output file" = sys.stdout):
        """Stores the top level ast ready to proceed with writing source file."""

        self.__out = out

        self.__top_ast = top_ast
        if not isinstance(self.__top_ast, ast.AST):
            raise TypeError("The tree needs to begin with an AST node.")

        self.__indentation = []
        self.__character_level = 0
        self._is_interactive = False

    def write(self):
        """Dump out the entire source tree."""

        self._write(self.__top_ast)

    def _write(self, tree : "The tree to write"):
        """
        Write out the given tree.

        This actually just dishes out work to the correct method.

        """

        try:
            method = getattr(self, "_write_" + tree.__class__.__name__)
        except AttributeError as exc:
            raise TypeError("Unknown AST node") from exc
        else:
            method(tree)

    def _write_str(self, s):
        """Write a string, all writing should be done through here."""

        self.__character_level += len(s)
        self.__out.write(s)

    def _newline(self):
        """Write out a new line."""

        self.__character_level = 0
        self._write("\n")

    def _inc_indent(self, by : "How far to indent - '' to indent to character level" = "    "):
        """Increase indentation."""

        if by == '':
            by = " " * self.__character_level
        self.__indentation.append(by)

    def _dec_indent(self):
        """Decrease indentation."""

        self.__indentation.pop()

    def _indent_level(self):
        return len(self.__indentation)

    def _indent(self):
        """Indent to the correct level."""

        self._write("".join(self.__indentation))

    def _start_line(self, nl : "Start with a new line" = False):
        """Start a new line at the correct indentation level."""

        if nl:
            self._newline()
        if self._is_interactive:
            if self._indent_level():
                self._write("... ")
            else:
                self._write(">>> ")
        self._indent()

    def _interleave_write(self,
                          exprs : "List of expressions to write",
                          before : "Write before each expr" = (lambda: None),
                          between : "Write between each expr" = (lambda: None),
                          after : "Write after each expr" = (lambda: None),
                          writer : "Optional function to write the exprs" = None):
        """
        Write a list of expressions.
        Separate them by calling the given functions with no arguments.

        """

        if not exprs:
            return
        if not writer:
            writer = self._write

        i = iter(exprs)
        before()
        writer(next(i))
        after()
        for expr in i:
            between()
            before()
            writer(expr)
            after()


    def _write_int(self, i): self._write(str(i))
    def _write_float(self, f): self._write(str(f))

    def _write_body(self,
                    stmts : "List of statements inside the block.",
                    indent : "Whether or not to indent." = True):
        """Write a list of statements, each on a new line in a new indentation level."""

        # Don't start with a new line
        if indent:
            self._inc_indent()
        self._interleave_write(stmts,
            before=self._start_line,
            between=self._newline)
        if indent:
            self._dec_indent()

    # Below are abstract methods to write all the tags listed in
    # the AST definition

    # mod
    @abc.abstractmethod
    def _write_Module(self, tree): pass
    @abc.abstractmethod
    def _write_Interactive(self, tree): pass
    @abc.abstractmethod
    def _write_Expression(self, tree): pass
    @abc.abstractmethod
    def _write_Suite(self, tree): pass

    # stmt
    @abc.abstractmethod
    def _write_FunctionDef(self, tree): pass
    @abc.abstractmethod
    def _write_ClassDef(self, tree): pass
    @abc.abstractmethod
    def _write_Return(self, tree): pass

    @abc.abstractmethod
    def _write_Delete(self, tree): pass
    @abc.abstractmethod
    def _write_Assign(self, tree): pass
    @abc.abstractmethod
    def _write_AugAssign(self, tree): pass

    @abc.abstractmethod
    def _write_For(self, tree): pass
    @abc.abstractmethod
    def _write_While(self, tree): pass
    @abc.abstractmethod
    def _write_If(self, tree): pass
    @abc.abstractmethod
    def _write_With(self, tree): pass

    @abc.abstractmethod
    def _write_Raise(self, tree): pass
    @abc.abstractmethod
    def _write_TryExcept(self, tree): pass
    @abc.abstractmethod
    def _write_TryFinally(self, tree): pass
    @abc.abstractmethod
    def _write_Assert(self, tree): pass

    @abc.abstractmethod
    def _write_Import(self, tree): pass
    @abc.abstractmethod
    def _write_ImportFrom(self, tree): pass

    @abc.abstractmethod
    def _write_Global(self, tree): pass
    @abc.abstractmethod
    def _write_Nonlocal(self, tree): pass
    @abc.abstractmethod
    def _write_Expr(self, tree): pass
    @abc.abstractmethod
    def _write_Pass(self, tree): pass
    @abc.abstractmethod
    def _write_Break(self, tree): pass
    @abc.abstractmethod
    def _write_Continue(self, tree): pass

    # expr
    @abc.abstractmethod
    def _write_BoolOp(self, tree): pass
    @abc.abstractmethod
    def _write_BinOp(self, tree): pass
    @abc.abstractmethod
    def _write_UnaryOp(self, tree): pass
    @abc.abstractmethod
    def _write_Lambda(self, tree): pass
    @abc.abstractmethod
    def _write_IfExp(self, tree): pass
    @abc.abstractmethod
    def _write_Dict(self, tree): pass
    @abc.abstractmethod
    def _write_Set(self, tree): pass
    @abc.abstractmethod
    def _write_ListComp(self, tree): pass
    @abc.abstractmethod
    def _write_SetComp(self, tree): pass
    @abc.abstractmethod
    def _write_DictComp(self, tree): pass
    @abc.abstractmethod
    def _write_GeneratorExp(self, tree): pass

    @abc.abstractmethod
    def _write_Yield(self, tree): pass

    @abc.abstractmethod
    def _write_Compare(self, tree): pass
    @abc.abstractmethod
    def _write_Call(self, tree): pass
    @abc.abstractmethod
    def _write_Num(self, tree): pass
    @abc.abstractmethod
    def _write_Str(self, tree): pass
    @abc.abstractmethod
    def _write_Bytes(self, tree): pass
    @abc.abstractmethod
    def _write_Ellipsis(self, tree): pass

    @abc.abstractmethod
    def _write_Attribute(self, tree): pass
    @abc.abstractmethod
    def _write_Subscript(self, tree): pass
    @abc.abstractmethod
    def _write_Starred(self, tree): pass
    @abc.abstractmethod
    def _write_Name(self, tree): pass
    @abc.abstractmethod
    def _write_List(self, tree): pass
    @abc.abstractmethod
    def _write_Tuple(self, tree): pass

    # expr_context
    @abc.abstractmethod
    def _write_Load(self, tree): pass
    @abc.abstractmethod
    def _write_Store(self, tree): pass
    @abc.abstractmethod
    def _write_Del(self, tree): pass
    @abc.abstractmethod
    def _write_AugLoad(self, tree): pass
    @abc.abstractmethod
    def _write_AugStore(self, tree): pass
    @abc.abstractmethod
    def _write_Param(self, tree): pass

    # slice
    @abc.abstractmethod
    def _write_Slice(self, tree): pass
    @abc.abstractmethod
    def _write_ExtSlice(self, tree): pass
    @abc.abstractmethod
    def _write_Index(self, tree): pass

    # boolop
    @abc.abstractmethod
    def _write_And(self, tree): pass
    @abc.abstractmethod
    def _write_Or(self, tree): pass

    # operator
    @abc.abstractmethod
    def _write_Add(self, tree): pass
    @abc.abstractmethod
    def _write_Sub(self, tree): pass
    @abc.abstractmethod
    def _write_Mult(self, tree): pass
    @abc.abstractmethod
    def _write_Div(self, tree): pass
    @abc.abstractmethod
    def _write_Mod(self, tree): pass
    @abc.abstractmethod
    def _write_Pow(self, tree): pass
    @abc.abstractmethod
    def _write_LShift(self, tree): pass
    @abc.abstractmethod
    def _write_RShift(self, tree): pass
    @abc.abstractmethod
    def _write_BitOr(self, tree): pass
    @abc.abstractmethod
    def _write_BitXor(self, tree): pass
    @abc.abstractmethod
    def _write_BitAnd(self, tree): pass
    @abc.abstractmethod
    def _write_FloorDiv(self, tree): pass

    # unaryop
    @abc.abstractmethod
    def _write_Invert(self, tree): pass
    @abc.abstractmethod
    def _write_Not(self, tree): pass
    @abc.abstractmethod
    def _write_UAdd(self, tree): pass
    @abc.abstractmethod
    def _write_USub(self, tree): pass

    # cmpop
    @abc.abstractmethod
    def _write_Eq(self, tree): pass
    @abc.abstractmethod
    def _write_NotEq(self, tree): pass
    @abc.abstractmethod
    def _write_Lt(self, tree): pass
    @abc.abstractmethod
    def _write_LtE(self, tree): pass
    @abc.abstractmethod
    def _write_Gt(self, tree): pass
    @abc.abstractmethod
    def _write_GtE(self, tree): pass
    @abc.abstractmethod
    def _write_Is(self, tree): pass
    @abc.abstractmethod
    def _write_IsNot(self, tree): pass
    @abc.abstractmethod
    def _write_In(self, tree): pass
    @abc.abstractmethod
    def _write_NotIn(self, tree): pass

    # comprehension
    @abc.abstractmethod
    def _write_comprehension(self, tree): pass

    # excepthandler
    @abc.abstractmethod
    def _write_ExceptHandler(self, tree): pass

    # arguments
    @abc.abstractmethod
    def _write_arguments(self, tree): pass

    # arg
    @abc.abstractmethod
    def _write_arg(self, tree): pass

    # keyword
    @abc.abstractmethod
    def _write_keyword(self, tree): pass

    # alias
    @abc.abstractmethod
    def _write_alias(self, tree): pass

def printSource(tree : "Tree to print", writer : "Type to write with"):
    """
    Write an AST as source to stdout. Works with doctest.

    >>> import ast
    >>> from basicwriter import BasicWriter
    >>> myast = ast.Str("Hello there")
    >>> printSource(myast, BasicWriter)
    'Hello there'

    """

    print(srcToStr(tree, writer))


def srcToStr(tree : "Tree to stringify", writer : "Type to write with"):
    """
    Write an AST as source to a string.

    >>> import ast
    >>> from basicwriter import BasicWriter
    >>> myast = ast.Str("Hello there")
    >>> srcToStr(myast, BasicWriter)
    "'Hello there'"

    """

    import io
    out = io.StringIO()
    writer(tree, out).write()
    return out.getvalue()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
