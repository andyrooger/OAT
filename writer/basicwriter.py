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

    def _write_str(self, s): self.out.write(s)
    def _write_int(self, i): self.out.write(str(i))
    def _write_float(self, f): self.out.write(str(f))

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
        def myfunction(arg1, arg2, arg3 = None):
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

        >>> import ast
        >>> c = '''
        ... @aclassdecorator
        ... class myclass(base1, base2, metaclass=m, *varpos, **varkey):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        @aclassdecorator
        class myclass(base1, base2, metaclass = m, *varpos, **varkey):
            print('hi')
            print('bye')

        """

        self._separated_write(tree.decorator_list,
            before=(lambda: self.out.write("@")),
            after=self._indent_nl)

        self.out.write("class " + tree.name)
        if tree.bases or tree.keywords or tree.starargs or tree.kwargs:
            self.out.write("(")

            self._separated_write(tree.bases + tree.keywords,
                between=(lambda: self.out.write(", ")))

            had_arg = tree.bases or tree.keywords

            if tree.starargs:
                if had_arg:
                    self._write(", ")
                had_arg = True
                self._write("*")
                self._write(tree.starargs)

            if tree.kwargs:
                if had_arg:
                    self._write(", ")
                had_arg = True
                self._write("**")
                self._write(tree.kwargs)

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


    def _write_AugAssign(self, tree):
        """
        Write out an assignment augmentation statement.

        >>> import ast
        >>> myast = ast.parse("a+=2")
        >>> printSource(myast)
        a += 2

        """

        self._write(tree.target)
        self.out.write(" ")
        self._write(tree.op)
        self.out.write("= ")
        self._write(tree.value)

    def _write_For(self, tree):
        """
        Write out a for loop.

        >>> import ast
        >>> c = '''
        ... for i in range(3):
        ...     print(str(i))
        ... else:
        ...     print("I wonder how this happened...")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        for i in range(3):
            print(str(i))
        else:
            print('I wonder how this happened...')

        """

        self.out.write("for ")
        self._write(tree.target)
        self.out.write(" in ")
        self._write(tree.iter)
        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()

        if tree.orelse:
            self._indent_nl()
            self.out.write("else:")
            self._newline()

            self._inc_indent()
            self._write(tree.orelse)
            self._dec_indent()

    def _write_While(self, tree):
        """
        Write out a while loop.

        >>> import ast
        >>> c = '''
        ... while True:
        ...     pass
        ... else:
        ...     print("Never get here.")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        while True:
            pass
        else:
            print('Never get here.')

        """

        self.out.write("while ")
        self._write(tree.test)
        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()

        if tree.orelse:
            self._indent_nl()
            self.out.write("else:")
            self._newline()

            self._inc_indent()
            self._write(tree.orelse)
            self._dec_indent()

    def _write_If(self, tree):
        """
        Write out an if statement.

        >>> import ast
        >>> c = '''
        ... if "linux" in sys.platform:
        ...     print(":)")
        ... else:
        ...     print(":(")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        if 'linux' in sys.platform:
            print(':)')
        else:
            print(':(')

        """

        self.out.write("if ")
        self._write(tree.test)
        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()

        if tree.orelse:
            self._indent_nl()
            self.out.write("else:")
            self._newline()

            self._inc_indent()
            self._write(tree.orelse)
            self._dec_indent()


    def _write_With(self, tree):
        """
        Write out with statement.

        >>> import ast
        >>> c = '''
        ... with open("/dev/null") as nothing:
        ...     nothing.write("hello")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        with open('/dev/null') as nothing:
            nothing.write('hello')

        """

        self.out.write("with ")
        self._write(tree.context_expr)

        if tree.optional_vars:
            self.out.write(" as ")
            self._write(tree.optional_vars)
        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()


    def _write_Raise(self, tree):
        """
        Write out raise statement.

        >>> import ast
        >>> myast = ast.parse("raise Exception('Bad thing happened') from Exception()")
        >>> printSource(myast)
        raise Exception('Bad thing happened') from Exception()

        """

        self.out.write("raise ")
        self._write(tree.exc)

        if tree.cause:
            self._write(" from ")
            self._write(tree.cause)


    def _write_TryExcept(self, tree):
        """
        Write out a try catch statement.

        >>> import ast
        >>> c = '''
        ... try: raise Exception
        ... except Exception: pass
        ... except: pass
        ... else: print("Oh...")
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        try:
            raise Exception
        except Exception:
            pass
        except:
            pass
        else:
            print('Oh...')

        """

        self.out.write("try:")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()

        self._separated_write(tree.handlers,
            before = self._indent_nl)

        if tree.orelse:
            self._indent_nl()
            self.out.write("else:")
            self._newline()

            self._inc_indent()
            self._write(tree.orelse)
            self._dec_indent()
        

    def _write_TryFinally(self, tree):
        """
        Write out a try finally statement.

        >>> import ast
        >>> c = '''
        ... try: raise Exception
        ... finally: pass
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        try:
            raise Exception
        finally:
            pass

        """

        self.out.write("try:")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()

        self._indent_nl()
        self.out.write("finally:")
        self._newline()

        self._inc_indent()
        self._write(tree.finalbody)
        self._dec_indent()

    def _write_Assert(self, tree):
        """
        Write out an assert statement.

        >>> import ast
        >>> myast = ast.parse("assert False, 'Oh dear'")
        >>> printSource(myast)
        assert False, 'Oh dear'

        """

        self.out.write("assert ")
        self._write(tree.test)

        if tree.msg:
            self.out.write(", ")
            self._write(tree.msg)


    def _write_Import(self, tree):
        """
        Write out an import statement.

        >>> import ast
        >>> myast = ast.parse("import sys, os")
        >>> printSource(myast)
        import sys, os

        """

        self.out.write("import ")
        self._separated_write(tree.names,
            between = (lambda: self.out.write(", ")))

    def _write_ImportFrom(self, tree):
        """
        Write out an import from statement.

        >>> import ast
        >>> myast = ast.parse("from .. sys import sys as sys2, os")
        >>> printSource(myast)
        from .. sys import sys as sys2, os

        """

        self.out.write("from ")
        if tree.level:
            self.out.write(("." * tree.level) + " ")
        self.out.write(tree.module + " import ")

        self._separated_write(tree.names,
            between = (lambda: self.out.write(", ")))


    def _write_Global(self, tree):
        """
        Write out a global variable.

        >>> import ast
        >>> myast = ast.parse("global g1, g2")
        >>> printSource(myast)
        global g1, g2

        """

        self.out.write("global ")
        self._separated_write(tree.names,
            between = (lambda: self.out.write(", ")))


    def _write_Nonlocal(self, tree):
        """
        Write out a nonlocal variable.

        >>> import ast
        >>> myast = ast.parse("nonlocal n1, n2")
        >>> printSource(myast)
        nonlocal n1, n2

        """

        self.out.write("nonlocal ")
        self._separated_write(tree.names,
            between = (lambda: self.out.write(", ")))


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


    # not worth testing
    def _write_Pass(self, tree): self.out.write("pass")
    def _write_Break(self, tree): self.out.write("break")
    def _write_Continue(self, tree): self.out.write("continue")

    # expr
    def _write_BoolOp(self, tree):
        """
        Write out a boolean operation.

        >>> import ast
        >>> myast = ast.parse("a and b or c")
        >>> printSource(myast)
        ((a and b) or c)

        """

        def sep():
            self._write(" ")
            self._write(tree.op)
            self._write(" ")

        self._write("(")
        self._separated_write(tree.values, between = sep)
        self._write(")")

    def _write_BinOp(self, tree):
        """
        Write out a binary operation.

        >>> import ast
        >>> myast = ast.parse("a / 2 * 3 + 10")
        >>> printSource(myast)
        (((a / 2) * 3) + 10)

        """

        self._write("(")
        self._write(tree.left)
        self._write(" ")
        self._write(tree.op)
        self._write(" ")
        self._write(tree.right)
        self._write(")")

    def _write_UnaryOp(self, tree):
        """
        Write out a unary operation.

        >>> import ast
        >>> myast = ast.parse("not ~a")
        >>> printSource(myast)
        not ~ a

        """

        self._write(tree.op)
        self._write(" ")
        self._write(tree.operand)

    def _write_Lambda(self, tree):
        """
        Write out a lambda expression.

        >>> import ast
        >>> myast = ast.parse("lambda a,b,c: a + b + c")
        >>> printSource(myast)
        lambda a, b, c: ((a + b) + c)

        """

        self._write("lambda")
        if tree.args:
            self._write(" ")
            self._write(tree.args)
        self._write(": ")
        self._write(tree.body)

    def _write_IfExp(self, tree):
        """
        Write out an inline if expression.

        >>> import ast
        >>> myast = ast.parse("a if b else c")
        >>> printSource(myast)
        a if b else c

        """

        self._write(tree.body)
        self._write(" if ")
        self._write(tree.test)
        self._write(" else ")
        self._write(tree.orelse)


    def _write_Dict(self, tree):
        """
        Write out a dictionary object.

        >>> import ast
        >>> myast = ast.parse("{1 : 'partridge in a pear tree', 2: 'two turtle doves', 3: 'three french hens'}")
        >>> printSource(myast)
        {1: 'partridge in a pear tree', 2: 'two turtle doves', 3: 'three french hens'}

        """

        def item_writer(key_val):
            key, val = key_val
            self._write(key)
            self._write(": ")
            self._write(val)

        self._write("{")
        self._separated_write(zip(tree.keys, tree.values),
            writer = item_writer,
            between = (lambda: self._write(", ")))
        self._write("}")


    def _write_Set(self, tree):
        """
        Write out a set object.

        >>> import ast
        >>> myast = ast.parse("{2,3,5,7,13,17,19}")
        >>> printSource(myast)
        {2, 3, 5, 7, 13, 17, 19}

        """

        self._write("{")
        self._separated_write(tree.elts,
            between = (lambda: self._write(", ")))
        self._write("}")


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

    # boolop - too simple to test
    def _write_And(self, tree): self.out.write("and")
    def _write_Or(self, tree): self.out.write("or")

    # operator - too simple to bother testing
    def _write_Add(self, tree): self.out.write("+")
    def _write_Sub(self, tree): self.out.write("-")
    def _write_Mult(self, tree): self.out.write("*")
    def _write_Div(self, tree): self.out.write("/")
    def _write_Mod(self, tree): self.out.write("%")
    def _write_Pow(self, tree): self.out.write("**")
    def _write_LShift(self, tree): self.out.write("<<")
    def _write_RShift(self, tree): self.out.write(">>")
    def _write_BitOr(self, tree): self.out.write("|")
    def _write_BitXor(self, tree): self.out.write("^")
    def _write_BitAnd(self, tree): self.out.write("&")
    def _write_FloorDiv(self, tree): self.out.write("//")

    # unaryop - too simple
    def _write_Invert(self, tree): self.out.write("~")
    def _write_Not(self, tree): self.out.write("not")
    def _write_UAdd(self, tree): self.out.write("+")
    def _write_USub(self, tree): self.out.write("-")

    # cmpop - too simple
    def _write_Eq(self, tree): self.out.write("==")
    def _write_NotEq(self, tree): self.out.write("!=")
    def _write_Lt(self, tree): self.out.write("<")
    def _write_LtE(self, tree): self.out.write("<=")
    def _write_Gt(self, tree): self.out.write(">")
    def _write_GtE(self, tree): self.out.write(">=")
    def _write_Is(self, tree): self.out.write("is")
    def _write_IsNot(self, tree): self.out.write("is not")
    def _write_In(self, tree): self.out.write("in")
    def _write_NotIn(self, tree): self.out.write("not in")

    # comprehension
    def _write_comprehension(self, tree): pass

    # excepthandler
    def _write_ExceptHandler(self, tree):
        """
        Write out an exception handler.

        >>> import ast
        >>> c = '''
        ... try: pass
        ... except Exception as exc: pass
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        try:
            pass
        except Exception as exc:
            pass

        """

        self.out.write("except")

        if tree.type:
            self.out.write(" ")
            self._write(tree.type)

            if tree.name:
                self.out.write(" as " + tree.name)

        self.out.write(":")
        self._newline()

        self._inc_indent()
        self._write(tree.body)
        self._dec_indent()


    # arguments
    def _write_arguments(self, tree):
        """
        Write out a set of arguments.

        >>> import ast
        >>> c = '''
        ... def f(a : "An argument", b = None, *args, kwo = True, **kwargs): pass
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        def f(a : 'An argument', b = None, *args, kwo = True, **kwargs):
            pass

        """

        had_arg = False # Cannot use _separated_write here

        n_kwargs = len(tree.defaults)
        n_posargs = len(tree.args) - n_kwargs

        # positional args
        for arg in tree.args[:n_posargs]:
            if had_arg:
                self._write(", ")
            had_arg = True
            self._write(arg)

        # keyword args
        for (arg, default) in zip(tree.args[n_posargs:], tree.defaults):
            if had_arg:
                self._write(", ")
            had_arg = True
            self._write(arg)
            self._write(" = ")
            self._write(default)

        # variable positional args
        if tree.vararg:
            if had_arg:
                self._write(", ")
            had_arg = True
            self._write("*")
            self._write(tree.vararg)
            if tree.varargannotation:
                self._write(" : ")
                self._write(tree.varargannotation)
        elif tree.kwonlyargs:
            if had_arg:
                self._write(", ")
            had_arg = True
            self._write("*")

        # keyword only args
        for (arg, default) in zip(tree.kwonlyargs, tree.kw_defaults):
            if had_arg:
                self._write(", ")
            had_arg = True
            self._write(arg)
            self._write(" = ")
            self._write(default)

        # variable keyword args
        if tree.kwarg:
            if had_arg:
                self._write(", ")
            had_arg = False
            self._write("**")
            self._write(tree.kwarg)
            if tree.kwargannotation:
                self._write(" : ")
                self._write(tree.kwargannotation)

    # arg
    def _write_arg(self, tree):
        """
        Write out a single argument.

        >>> import ast
        >>> c = '''
        ... def f(a : "An argument"): pass
        ... '''
        >>> myast = ast.parse(c)
        >>> printSource(myast)
        def f(a : 'An argument'):
            pass

        """

        self._write(tree.arg)
        if tree.annotation:
            self._write(" : ")
            self._write(tree.annotation)


    # keyword
    def _write_keyword(self, tree):
        """
        Write out a keyword from an argument list.

        >>> import ast
        >>> myast = ast.parse("class c(a = b): pass")
        >>> printSource(myast)
        class c(a = b):
            pass

        """

        self._write(tree.arg)
        self._write(" = ")
        self._write(tree.value)


    # alias
    def _write_alias(self, tree):
        """
        Write out an alias.

        >>> import ast
        >>> myast = ast.parse("import hello as world")
        >>> printSource(myast)
        import hello as world

        """

        self.out.write(tree.name)

        if tree.asname:
            self.out.write(" as " + tree.asname)


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
