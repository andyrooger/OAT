#!/bin/env python3

"""
Holds the base class for source writers, it should somehow take an AST and
ouput correct source.

This should be extended for obfuscated syntax or really pretty output etc.

"""

import ast
import sys

class BasicWriter():
    """
    Writes source from an AST. Should be very simple and abide to the style guide.

    One option would have been to build an ast walker from the given walker
    classes, but I want a definite order. (None specified in the docs).

    >>> import ast
    >>> theast = None
    >>> with open("../example/startup.py") as file:
    ...     theast = ast.parse(file.read(), "startup.py", "exec")
    >>> type(theast)
    <class '_ast.Module'>
    >>> with open("../example/startup.py.basicformat") as file:
    ...         file.read() == srcToStr(theast)
    True

    """

    def __init__(self,
                 top_ast : "The AST to be printed" = None,
                 out : "Output file" = sys.stdout):
        """
        Stores the top level ast ready to proceed with writing source file.

        >>> BasicWriter("hello world").top_ast == None
        True
        >>> import ast
        >>> myast = ast.AST()
        >>> BasicWriter(myast).top_ast is myast
        True

        """

        self.out = out

        self.top_ast = top_ast
        if not isinstance(self.top_ast, ast.AST):
            self.top_ast = None

        self.indent_level = 0
        self.is_interactive = False

    def _newline(self):
        """Write out a new line."""

        self.out.write("\n")

    def _indent(self):
        """Indent to the correct level."""

        if self.is_interactive:
            if self.indent_level == 0:
                self.out.write(">>> ")
            else:
                self.out.write("... ")
        self.out.write("    " * self.indent_level)

    def write(self):
        """Dump out the entire source tree."""

        self._write(self.top_ast)

    def _write(self, tree : "The tree to write"):
        """
        Write out the given tree.

        This actually just dishes out work to the correct method.

        """

        getattr(self, "_write_" + tree.__class__.__name__)(tree)

    def _write_Module(self, tree):
        """
        Write out a Module object.

        >>> import ast
        >>> myast = ast.Module([ast.Expr(ast.Str("Hello"))])
        >>> srcToStr(myast) == repr("Hello") + "\\n"
        True

        """

        for stmt in tree.body:
            self._indent()
            self._write(stmt)
            self._newline()

    def _write_Interactive(self, tree):
        """
        Write out an interactive session.

        >>> import ast
        >>> myast = ast.Interactive([ast.Expr(ast.Str("Hello"))])
        >>> srcToStr(myast) == (">>> " + repr("Hello") + "\\n")
        True

        """

        old_interactive = self.is_interactive
        self.is_interactive = True
        self._write_Module(tree)
        self.is_interactive = old_interactive

    def _write_Expression(self, tree): pass
    def _write_Suite(self, tree): pass # For jython

    # stmt
    def _write_FunctionDef(self, tree): pass
    def _write_ClassDef(self, tree): pass
    def _write_Return(self, tree): pass

    def _write_Delete(self, tree): pass
    def _write_Assign(self, tree): pass
    def _write_AugAssign(self, tree): pass

    def _write_For(self, tree): pass
    def _write_While(self, tree): pass
    def _write_If(self, tree): pass
    def _write_With(self, tree): pass

    def _write_Raise(self, tree): pass
    def _write_TryExcept(self, tree): pass
    def _write_TryFinally(self, tree): pass
    def _write_Assert(self, tree): pass

    def _write_Import(self, tree): pass
    def _write_ImportFrom(self, tree): pass

    def _write_Global(self, tree): pass
    def _write_Nonlocal(self, tree): pass

    def _write_Expr(self, tree):
        """
        Write out an expression.

        >>> import ast
        >>> innerast = ast.Str("Hello")
        >>> outerast = ast.Expr(innerast)
        >>> srcToStr(innerast) == srcToStr(outerast)
        True

        """

        self._write(tree.value)


    def _write_Pass(self, tree): pass
    def _write_Break(self, tree): pass
    def _write_Continue(self, tree): pass

    # expr
    def _write_BoolOp(self, tree): pass
    def _write_BinOp(self, tree): pass
    def _write_UnaryOp(self, tree): pass
    def _write_Lambda(self, tree): pass
    def _write_IfExp(self, tree): pass
    def _write_Dict(self, tree): pass
    def _write_Set(self, tree): pass
    def _write_ListComp(self, tree): pass
    def _write_SetComp(self, tree): pass
    def _write_DictComp(self, tree): pass
    def _write_GeneratorExp(self, tree): pass
    def _write_Yield(self, tree): pass
    def _write_Compare(self, tree): pass
    def _write_Call(self, tree): pass
    def _write_Num(self, tree): pass

    def _write_Str(self, tree):
        """
        Write out a String object.

        >>> import ast
        >>> srcToStr(ast.Str("Hello")) == repr("Hello")
        True

        """

        self.out.write(repr(tree.s))

    def _write_Bytes(self, tree): pass
    def _write_Ellipsis(self, tree): pass

    def _write_Attribute(self, tree): pass
    def _write_Subscript(self, tree): pass
    def _write_Starred(self, tree): pass
    def _write_Name(self, tree): pass
    def _write_List(self, tree): pass
    def _write_Tuple(self, tree): pass

    # expr_context
    def _write_Load(self, tree): pass
    def _write_Store(self, tree): pass
    def _write_Del(self, tree): pass
    def _write_AugLoad(self, tree): pass
    def _write_AugStore(self, tree): pass
    def _write_Param(self, tree): pass

    # slice
    def _write_Slice(self, tree): pass
    def _write_ExtSlice(self, tree): pass
    def _write_Index(self, tree): pass

    # boolop
    def _write_And(self, tree): pass
    def _write_Or(self, tree): pass

    # operator
    def _write_Add(self, tree): pass
    def _write_Sub(self, tree): pass
    def _write_Mult(self, tree): pass
    def _write_Div(self, tree): pass
    def _write_Mod(self, tree): pass
    def _write_Pow(self, tree): pass
    def _write_LShift(self, tree): pass
    def _write_RShift(self, tree): pass
    def _write_BitOr(self, tree): pass
    def _write_BitXor(self, tree): pass
    def _write_BitAnd(self, tree): pass
    def _write_FloorDiv(self, tree): pass

    # unaryop
    def _write_Invert(self, tree): pass
    def _write_Not(self, tree): pass
    def _write_UAdd(self, tree): pass
    def _write_USub(self, tree): pass

    # cmpop
    def _write_Eq(self, tree): pass
    def _write_NotEq(self, tree): pass
    def _write_Lt(self, tree): pass
    def _write_LtE(self, tree): pass
    def _write_Gt(self, tree): pass
    def _write_GtE(self, tree): pass
    def _write_Is(self, tree): pass
    def _write_IsNot(self, tree): pass
    def _write_In(self, tree): pass
    def _write_NotIn(self, tree): pass

    # excepthandler
    def _write_ExceptHandler(self, tree): pass


def printSource(tree : "Tree to print"):
    """
    Write an AST as source to stdout. Works with doctest.

    >>> import ast
    >>> myast = ast.Str("Hello there")
    >>> printSource(myast)
    'Hello there'

    """

    print(srcToStr(tree))


def srcToStr(tree : "Tree to stringify"):
    """
    Write an AST as source to a string.

    >>> import ast
    >>> myast = ast.Str("Hello there")
    >>> srcToStr(myast)
    "'Hello there'"

    """

    import io
    out = io.StringIO()
    BasicWriter(tree, out).write()
    return out.getvalue()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
