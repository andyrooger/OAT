#!/usr/bin/env python3

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

    def _inc_indent(self):
        """Increase indentation."""

        self.indent_level += 1

    def _dec_indent(self):
        """Decrease indentation."""

        self.indent_level -= 1

    def _indent(self):
        """Indent to the correct level."""

        if self.is_interactive:
            if self.indent_level == 0:
                self.out.write(">>> ")
            else:
                self.out.write("... ")
        self.out.write("    " * self.indent_level)

    def _indent_nl(self):
        """Just a shortcut for an indented newline."""

        self._newline()
        self._indent()

    def write(self):
        """Dump out the entire source tree."""

        self._write(self.top_ast)

    def _write(self, tree : "The tree to write"):
        """
        Write out the given tree.

        This actually just dishes out work to the correct method.

        """

        getattr(self, "_write_" + tree.__class__.__name__)(tree)

    def _separated_write(self,
                         exprs : "List of expressions to write",
                         before : "Write before each expr" = (lambda: None),
                         between : "Write between each expr" = (lambda: None),
                         after : "Write after each expr" = (lambda: None)):
        """
        Write a list of expressions.
        Separate them by calling the given functions with no arguments.

        """

        if not exprs:
            return
        i = iter(exprs)
        before()
        self._write(next(i))
        after()
        for expr in i:
            between()
            before()
            self._write(expr)
            after()


    def _write_list(self, stmts):
        """
        Write a list of statements, each on a new line.

        >>> import ast
        >>> stmts = [
        ...     ast.Str("hello"),
        ...     ast.Str("is it me"),
        ...     ast.Str("You're looking for?")
        ... ]
        >>> printSource(ast.Module(stmts))
        'hello'
        'is it me'
        "You're looking for?"

        """

        # Don't start with a new line
        self._separated_write(stmts,
            before=self._indent,
            between=self._newline)
            

    def _write_Module(self, tree):
        """
        Write out a Module object.

        >>> import ast
        >>> myast = ast.Module([ast.Expr(ast.Str("Hello"))])
        >>> printSource(myast)
        'Hello'

        """

        self._write(tree.body)

    def _write_Interactive(self, tree):
        """
        Write out an interactive session.

        >>> import ast
        >>> myast = ast.Interactive([ast.Expr(ast.Str("Hello"))])
        >>> srcToStr(myast) == (">>> " + repr("Hello"))
        True

        """

        old_interactive = self.is_interactive
        self.is_interactive = True
        self._write(tree.body)
        self.is_interactive = old_interactive

    def _write_Expression(self, tree):
        """
        Write out a solo expression.

        >>> import ast
        >>> myast = ast.Expression(ast.Expr(ast.Str("Hello")))
        >>> printSource(myast)
        'Hello'

        """

        self._write(tree.body)
    

    def _write_Suite(self, tree):
        raise NotImplementedError("I have no idea what a suite is supposed to be")

    # stmt
    def _write_FunctionDef(self, tree):
        """
        Write out a function.

        >>> import ast
        >>> c = '''
        ... @afunction
        ... def myfunction(arg1, arg2, arg3=None):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        @afunction
        def myfunction(arg1, arg2, arg3=None):
            print('hi')
            print('bye')

        """

        self._separated_write(
            tree.decorator_list,
            before=(lambda: self.out.write("@")),
            after=(self._indent_nl))

        self.out.write("def " + tree.name + "(")
        self._write(tree.args)
        self.out.write(")")
        if tree.returns:
            self.out.write(" -> ")
            self._write(tree.returns)
        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()
            

    def _write_ClassDef(self, tree):
        """
        Write out a class definition.

        This ignores the parameters as I cannot see where they would be used.

        >>> import ast
        >>> c = '''
        ... @aclassdecorator
        ... def myclass(base1, base2):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        @aclassdecorator
        def myclass(base1, base2):
            print('hi')
            print('bye')

        """

        self._separated_write(tree.decorator_list,
            before=(lambda: self.out.write("@")),
            after=self._indent_nl)

        self.out.write("class " + tree.name)
        if tree.bases:
            self.out.write("(")
            self._separated(tree.bases,
                between=(lambda: self.out.write(", ")))
            self.out.write(")")
        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()
        

    def _write_Return(self, tree):
        """
        Write out a return statement.

        >>> import ast
        >>> myast = ast.parse("return 'Hello there'")
        >>> printSource(myast)
        return 'Hello there'

        """

        self.out.write("return ")
        self._write(tree.value)

    def _write_Delete(self, tree):
        """
        Write out a delete statement.

        >>> import ast
        >>> myast = ast.parse("del myvar, yourvar")
        >>> printSource(myast)
        del myvar, yourvar

        """

        self.out.write("del ")
        self._separated_write(tree.targets,
            between=(lambda: self.out.write(", ")))


    def _write_Assign(self, tree):
        """
        Write out an assignment statement.

        >>> import ast
        >>> myast = ast.parse("a=b=c=142")
        >>> printSource(myast)
        a = b = c = 142

        """

        self._separated_write(tree.targets + [tree.value],
            between=(lambda: self.out.write(" = ")))


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

    def _write_Num(self, tree):
        """
        Write out a numerical object.

        >>> import ast
        >>> printSource(ast.parse("1042"))
        1042

        """

        self.out.write(repr(tree.n))

    def _write_Str(self, tree):
        """
        Write out a String object.

        >>> import ast
        >>> printSource(ast.Str("Hello"))
        'Hello'

        """

        self.out.write(repr(tree.s))

    def _write_Bytes(self, tree): pass
    def _write_Ellipsis(self, tree): pass

    def _write_Attribute(self, tree): pass
    def _write_Subscript(self, tree): pass
    def _write_Starred(self, tree): pass

    def _write_Name(self, tree):
        """
        Write out a name object. We ignore context...

        >>> import ast
        >>> printSource(ast.parse("a_var_name"))
        a_var_name

        """

        self.out.write(tree.id)

    def _write_List(self, tree): pass
    def _write_Tuple(self, tree): pass

    # expr_context - these should not be drawn
    def _write_Load(self, tree): raise NotImplementedError("Should not be used")
    def _write_Store(self, tree): raise NotImplementedError("Should not be used")
    def _write_Del(self, tree): raise NotImplementedError("Should not be used")
    def _write_AugLoad(self, tree): raise NotImplementedError("Should not be used")
    def _write_AugStore(self, tree): raise NotImplementedError("Should not be used")
    def _write_Param(self, tree): raise NotImplementedError("Should not be used")

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

    # comprehension
    def _write_comprehension(self, tree): pass

    # excepthandler
    def _write_ExceptHandler(self, tree): pass

    # arguments
    def _write_arguments(self, tree): pass

    # arg
    def _write_arg(self, tree): pass

    # keyword
    def _write_keyword(self, tree): pass

    # alias
    def _write_alias(self, tree): pass


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
