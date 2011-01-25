#!/usr/bin/env python3

"""
Holds the base class for source writers, it should somehow take an AST and
ouput correct source.

This should be extended for obfuscated syntax or really pretty output etc.

"""

import ast
import sys

from . import sourcewriter

class BasicWriter(sourcewriter.SourceWriter):
    """
    Writes source from an AST. Should be very simple and abide to the style guide.

    One option would have been to build an ast walker from the given walker
    classes, but I want a definite order. (None specified in the docs).

    >>> import ast, sourcewriter
    >>> theast = None
    >>> with open("../../example/startup.py") as file:
    ...     theast = ast.parse(file.read(), "startup.py", "exec")
    >>> type(theast)
    <class '_ast.Module'>
    >>> with open("../../example/startup.py.basicformat") as file:
    ...         file.read() == sourcewriter.srcToStr(theast, BasicWriter)
    True

    """

    def __init__(self,
                 top_ast : "The AST to be printed" = None,
                 out : "Output file" = sys.stdout):
        """
        Create the writer.

        >>> BasicWriter("hello world")
        Traceback (most recent call last):
            ...
        TypeError: The tree needs to begin with an AST node.
        >>> import ast
        >>> myast = ast.AST()
        >>> myast = BasicWriter(myast)

        """

        super().__init__(top_ast, out)

    def _write_Module(self, tree):
        """
        Write out a Module object.

        >>> import ast, sourcewriter
        >>> myast = ast.Module([ast.Expr(ast.Str("Hello"))])
        >>> sourcewriter.printSource(myast, BasicWriter)
        'Hello'

        """

        self._write_block(tree.body, indent = False)

    def _write_Interactive(self, tree):
        """
        Write out an interactive session.

        >>> import ast, sourcewriter
        >>> myast = ast.Interactive([ast.Expr(ast.Str("Hello"))])
        >>> sourcewriter.srcToStr(myast, BasicWriter) == ">>> 'Hello'"
        True

        """

        old_interactive = self._is_interactive()
        self._is_interactive(True)
        self._write_block(tree.body, indent = False)
        self._is_interactive(old_interactive)

    def _write_Expression(self, tree):
        """
        Write out a solo expression.

        >>> import ast, sourcewriter
        >>> myast = ast.Expression(ast.Expr(ast.Str("Hello")))
        >>> sourcewriter.printSource(myast, BasicWriter)
        'Hello'

        """

        self._write_block([tree.body], indent = False)
    

    def _write_Suite(self, tree):
        raise NotImplementedError("I have no idea what a suite is supposed to be")

    # stmt
    def _write_FunctionDef(self, tree):
        """
        Write out a function.

        >>> import ast, sourcewriter
        >>> c = '''
        ... @afunction
        ... def myfunction(arg1, arg2, arg3=None):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        @afunction
        def myfunction(arg1, arg2, arg3 = None):
            print('hi')
            print('bye')

        """

        self._interleave_write(
            tree.decorator_list,
            before = (lambda: self._write("@")),
            after = self._next_statement)

        self._write("def " + tree.name + "(")
        self._write(tree.args)
        self._write(")")
        if tree.returns != None:
            self._write(" -> ")
            self._write(tree.returns)
        self._write_block(tree.body)          

    def _write_ClassDef(self, tree):
        """
        Write out a class definition.

        >>> import ast, sourcewriter
        >>> c = '''
        ... @aclassdecorator
        ... class myclass(base1, base2, metaclass=m, *varpos, **varkey):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        @aclassdecorator
        class myclass(base1, base2, metaclass = m, *varpos, **varkey):
            print('hi')
            print('bye')

        """

        self._interleave_write(tree.decorator_list,
            before=(lambda: self._write("@")),
            after=self._next_statement)

        self._write("class " + tree.name)
        if tree.bases or tree.keywords or tree.starargs or tree.kwargs:
            self._write("(")

            self._interleave_write(tree.bases + tree.keywords,
                between=(lambda: self._write(", ")))

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

            self._write(")")
        self._write_block(tree.body)
        

    def _write_Return(self, tree):
        """
        Write out a return statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("return 'Hello there'")
        >>> sourcewriter.printSource(myast, BasicWriter)
        return 'Hello there'

        """

        self._write("return ")
        self._write(tree.value)

    def _write_Delete(self, tree):
        """
        Write out a delete statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("del myvar, yourvar")
        >>> sourcewriter.printSource(myast, BasicWriter)
        del myvar, yourvar

        """

        self._write("del ")
        self._interleave_write(tree.targets,
            between=(lambda: self._write(", ")))


    def _write_Assign(self, tree):
        """
        Write out an assignment statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("a=b=c=142")
        >>> sourcewriter.printSource(myast, BasicWriter)
        a = b = c = 142

        """

        self._interleave_write(tree.targets + [tree.value],
            between=(lambda: self._write(" = ")))


    def _write_AugAssign(self, tree):
        """
        Write out an assignment augmentation statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("a+=2")
        >>> sourcewriter.printSource(myast, BasicWriter)
        a += 2

        """

        self._write(tree.target)
        self._write(" ")
        self._write(tree.op)
        self._write("= ")
        self._write(tree.value)

    def _write_For(self, tree):
        """
        Write out a for loop.

        >>> import ast, sourcewriter
        >>> c = '''
        ... for i in range(3):
        ...     print(str(i))
        ... else:
        ...     print("I wonder how this happened...")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        for i in range(3):
            print(str(i))
        else:
            print('I wonder how this happened...')

        """

        self._write("for ")
        self._write(tree.target)
        self._write(" in ")
        self._write(tree.iter)
        self._write_block(tree.body)

        if tree.orelse:
            self._next_statement()
            self._write("else")
            self._write_block(tree.orelse)

    def _write_While(self, tree):
        """
        Write out a while loop.

        >>> import ast, sourcewriter
        >>> c = '''
        ... while True:
        ...     pass
        ... else:
        ...     print("Never get here.")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        while True:
            pass
        else:
            print('Never get here.')

        """

        self._write("while ")
        self._write(tree.test)
        self._write_block(tree.body)

        if tree.orelse:
            self._next_statement()
            self._write("else")
            self._write_block(tree.orelse)

    def _write_If(self, tree):
        """
        Write out an if statement.

        >>> import ast, sourcewriter
        >>> c = '''
        ... if "linux" in sys.platform:
        ...     print(":)")
        ... else:
        ...     print(":(")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        if 'linux' in sys.platform:
            print(':)')
        else:
            print(':(')

        """

        self._write("if ")
        self._write(tree.test)
        self._write_block(tree.body)

        if tree.orelse:
            self._next_statement()
            self._write("else")
            self._write_block(tree.orelse)


    def _write_With(self, tree):
        """
        Write out with statement.

        >>> import ast, sourcewriter
        >>> c = '''
        ... with open("/dev/null") as nothing:
        ...     nothing.write("hello")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        with open('/dev/null') as nothing:
            nothing.write('hello')

        """

        self._write("with ")
        self._write(tree.context_expr)

        if tree.optional_vars:
            self._write(" as ")
            self._write(tree.optional_vars)

        self._write_block(tree.body)


    def _write_Raise(self, tree):
        """
        Write out raise statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("raise Exception('Bad thing happened') from Exception()")
        >>> sourcewriter.printSource(myast, BasicWriter)
        raise Exception('Bad thing happened') from Exception()

        """

        self._write("raise ")
        self._write(tree.exc)

        if tree.cause != None:
            self._write(" from ")
            self._write(tree.cause)


    def _write_TryExcept(self, tree):
        """
        Write out a try catch statement.

        >>> import ast, sourcewriter
        >>> c = '''
        ... try: raise Exception
        ... except Exception: pass
        ... except: pass
        ... else: print("Oh...")
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        try:
            raise Exception
        except Exception:
            pass
        except:
            pass
        else:
            print('Oh...')

        """

        self._write("try")
        self._write_block(tree.body)

        self._interleave_write(tree.handlers,
            before = self._next_statement)

        if tree.orelse:
            self._next_statement()
            self._write("else")
            self._write_block(tree.orelse)
        

    def _write_TryFinally(self, tree):
        """
        Write out a try finally statement.

        >>> import ast, sourcewriter
        >>> c = '''
        ... try: raise Exception
        ... finally: pass
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        try:
            raise Exception
        finally:
            pass

        """

        self._write("try")
        self._write_block(tree.body)

        self._next_statement()
        self._write("finally")
        self._write_block(tree.finalbody)

    def _write_Assert(self, tree):
        """
        Write out an assert statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("assert False, 'Oh dear'")
        >>> sourcewriter.printSource(myast, BasicWriter)
        assert False, 'Oh dear'

        """

        self._write("assert ")
        self._write(tree.test)

        if tree.msg != None:
            self._write(", ")
            self._write(tree.msg)


    def _write_Import(self, tree):
        """
        Write out an import statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("import sys, os")
        >>> sourcewriter.printSource(myast, BasicWriter)
        import sys, os

        """

        self._write("import ")
        self._interleave_write(tree.names,
            between = (lambda: self._write(", ")))

    def _write_ImportFrom(self, tree):
        """
        Write out an import from statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("from .. sys import sys as sys2, os")
        >>> sourcewriter.printSource(myast, BasicWriter)
        from ..sys import sys as sys2, os

        """

        self._write("from ")
        if tree.level != None:
            self._write("." * tree.level)
        self._write(tree.module + " import ")

        self._interleave_write(tree.names,
            between = (lambda: self._write(", ")))


    def _write_Global(self, tree):
        """
        Write out a global variable.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("global g1, g2")
        >>> sourcewriter.printSource(myast, BasicWriter)
        global g1, g2

        """

        self._write("global ")
        self._interleave_write(tree.names,
            between = (lambda: self._write(", ")))


    def _write_Nonlocal(self, tree):
        """
        Write out a nonlocal variable.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("nonlocal n1, n2")
        >>> sourcewriter.printSource(myast, BasicWriter)
        nonlocal n1, n2

        """

        self._write("nonlocal ")
        self._interleave_write(tree.names,
            between = (lambda: self._write(", ")))


    def _write_Expr(self, tree):
        """
        Write out an expression.

        >>> import ast, sourcewriter
        >>> innerast = ast.Str("Hello")
        >>> outerast = ast.Expr(innerast)
        >>> sourcewriter.srcToStr(innerast, BasicWriter) == sourcewriter.srcToStr(outerast, BasicWriter)
        True

        """

        self._write(tree.value)


    # not worth testing
    def _write_Pass(self, tree): self._write("pass")
    def _write_Break(self, tree): self._write("break")
    def _write_Continue(self, tree): self._write("continue")

    # expr
    def _write_BoolOp(self, tree):
        """
        Write out a boolean operation.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("a and b or c")
        >>> sourcewriter.printSource(myast, BasicWriter)
        ((a and b) or c)

        """

        def sep():
            self._write(" ")
            self._write(tree.op)
            self._write(" ")

        self._write("(")
        self._interleave_write(tree.values, between = sep)
        self._write(")")

    def _write_BinOp(self, tree):
        """
        Write out a binary operation.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("a / 2 * 3 + 10")
        >>> sourcewriter.printSource(myast, BasicWriter)
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

        >>> import ast, sourcewriter
        >>> myast = ast.parse("not ~a")
        >>> sourcewriter.printSource(myast, BasicWriter)
        not ~ a

        """

        self._write(tree.op)
        self._write(" ")
        self._write(tree.operand)

    def _write_Lambda(self, tree):
        """
        Write out a lambda expression.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("lambda a,b,c: a + b + c")
        >>> sourcewriter.printSource(myast, BasicWriter)
        lambda a, b, c: ((a + b) + c)

        """

        self._write("lambda")
        if tree.args != None:
            self._write(" ")
            self._write(tree.args)
        self._write(": ")
        self._write(tree.body)

    def _write_IfExp(self, tree):
        """
        Write out an inline if expression.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("a if b else c")
        >>> sourcewriter.printSource(myast, BasicWriter)
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

        >>> import ast, sourcewriter
        >>> myast = ast.parse("{1 : 'partridge in a pear tree', 2: 'two turtle doves', 3: 'three french hens'}")
        >>> sourcewriter.printSource(myast, BasicWriter)
        {1: 'partridge in a pear tree', 2: 'two turtle doves', 3: 'three french hens'}

        """

        def item_writer(key_val):
            key, val = key_val
            self._write(key)
            self._write(": ")
            self._write(val)

        self._write("{")
        self._interleave_write(zip(tree.keys, tree.values),
            writer = item_writer,
            between = (lambda: self._write(", ")))
        self._write("}")


    def _write_Set(self, tree):
        """
        Write out a set object.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("{2,3,5,7,13,17,19}")
        >>> sourcewriter.printSource(myast, BasicWriter)
        {2, 3, 5, 7, 13, 17, 19}

        """

        self._write("{")
        self._interleave_write(tree.elts,
            between = (lambda: self._write(", ")))
        self._write("}")


    def _write_ListComp(self, tree):
        """
        Write out a list comprehension.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("[x*y for x in range(10) if x != 5 for y in range(10) if y != 5]")
        >>> sourcewriter.printSource(myast, BasicWriter)
        [(x * y) for x in range(10) if x != 5 for y in range(10) if y != 5]

        """

        self._write("[")
        self._write(tree.elt)
        self._interleave_write(tree.generators,
            before = (lambda: self._write(" ")))
        self._write("]")

    def _write_SetComp(self, tree):
        """
        Write out a set comprehension.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("{x*y for x in range(10) if x != 5 for y in range(10) if y != 5}")
        >>> sourcewriter.printSource(myast, BasicWriter)
        {(x * y) for x in range(10) if x != 5 for y in range(10) if y != 5}

        """

        self._write("{")
        self._write(tree.elt)
        self._interleave_write(tree.generators,
            before = (lambda: self._write(" ")))
        self._write("}")

    def _write_DictComp(self, tree):
        """
        Write out a dictionary comprehension.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("{x: y for x in range(10) if x != 5 for y in range(10) if y != 5}")
        >>> sourcewriter.printSource(myast, BasicWriter)
        {x: y for x in range(10) if x != 5 for y in range(10) if y != 5}

        """

        self._write("{")
        self._write(tree.key)
        self._write(": ")
        self._write(tree.value)
        self._interleave_write(tree.generators,
            before = (lambda: self._write(" ")))
        self._write("}")

    def _write_GeneratorExp(self, tree):
        """
        Write out a generator expression.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("(x*y for x in range(10) if x != 5 for y in range(10) if y != 5)")
        >>> sourcewriter.printSource(myast, BasicWriter)
        ((x * y) for x in range(10) if x != 5 for y in range(10) if y != 5)

        """

        self._write("(")
        self._write(tree.elt)
        self._interleave_write(tree.generators,
            before = (lambda: self._write(" ")))
        self._write(")")

    def _write_Yield(self, tree):
        """
        Write out a yield statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("yield x")
        >>> sourcewriter.printSource(myast, BasicWriter)
        yield x

        """

        self._write("yield")
        if tree.value != None:
            self._write(" ")
            self._write(tree.value)

    def _write_Compare(self, tree):
        """
        Write out a compare statement.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("a != b < c > d")
        >>> sourcewriter.printSource(myast, BasicWriter)
        a != b < c > d

        """

        self._write(tree.left)

        for op, comp in zip(tree.ops, tree.comparators):
            self._write(" ")
            self._write(op)
            self._write(" ")
            self._write(comp)

    def _write_Call(self, tree):
        """
        Write out a function call.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("print('Hello world')")
        >>> sourcewriter.printSource(myast, BasicWriter)
        print('Hello world')

        """

        self._write(tree.func)
        self._write("(")

        self._interleave_write(tree.args + tree.keywords,
            between = (lambda: self._write(", ")))

        has_arg = tree.args + tree.keywords

        if tree.starargs != None:
            if has_arg:
                self._write(", ")
            has_arg = True
            self._write("*")
            self._write(starargs)

        if tree.kwargs != None:
            if has_arg:
                self._write(", ")
            has_arg = True
            self._write("*")
            self._write(kwargs)

        self._write(")")

    def _write_Num(self, tree):
        """
        Write out a numerical object.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("1042"), BasicWriter)
        1042

        """

        self._write(repr(tree.n))

    def _write_Str(self, tree):
        """
        Write out a String object.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.Str("Hello"), BasicWriter)
        'Hello'

        """

        self._write(repr(tree.s))

    def _write_Bytes(self, tree):
        """
        Write out a Bytes object.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("b'hello world'")
        >>> sourcewriter.printSource(myast, BasicWriter)
        b'hello world'

        """

        self._write(repr(tree.s))

    def _write_Ellipsis(self, tree): self._write("...")

    def _write_Attribute(self, tree):
        """
        Write out an object attribute.

        Context is ignored.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("sys.path")
        >>> sourcewriter.printSource(myast, BasicWriter)
        sys.path

        """

        self._write(tree.value)
        self._write(".")
        self._write(tree.attr)

    def _write_Subscript(self, tree):
        """
        Write out an object subscript.

        Context is ignored.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("mylist[2]")
        >>> sourcewriter.printSource(myast, BasicWriter)
        mylist[2]

        """

        self._write(tree.value)
        self._write("[")
        self._write(tree.slice)
        self._write("]")

    def _write_Starred(self, tree):
        """
        Write out a starred object.

        Context is ignored.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("head, *tail = list(range(10))")
        >>> sourcewriter.printSource(myast, BasicWriter)
        (head, *tail) = list(range(10))

        """

        self._write("*")
        self._write(tree.value)

    def _write_Name(self, tree):
        """
        Write out a name object. We ignore context...

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("a_var_name"), BasicWriter)
        a_var_name

        """

        self._write(tree.id)

    def _write_List(self, tree):
        """
        Write out a list object.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("[1,2,3,4]"), BasicWriter)
        [1, 2, 3, 4]

        """

        self._write("[")
        self._interleave_write(tree.elts,
            between = (lambda: self._write(", ")))
        self._write("]")


    def _write_Tuple(self, tree):
        """
        Write out a tuple.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("(a,b,c)"), BasicWriter)
        (a, b, c)

        """

        self._write("(")
        self._interleave_write(tree.elts,
            between = (lambda: self._write(", ")))
        self._write(")")


    # expr_context - these should not be drawn
    def _write_Load(self, tree): raise NotImplementedError("Should not be used")
    def _write_Store(self, tree): raise NotImplementedError("Should not be used")
    def _write_Del(self, tree): raise NotImplementedError("Should not be used")
    def _write_AugLoad(self, tree): raise NotImplementedError("Should not be used")
    def _write_AugStore(self, tree): raise NotImplementedError("Should not be used")
    def _write_Param(self, tree): raise NotImplementedError("Should not be used")

    # slice
    def _write_Slice(self, tree):
        """
        Write out a slice.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("mylist[1:10:2]"), BasicWriter)
        mylist[1:10:2]

        """

        if tree.lower != None:
            self._write(tree.lower)
        self._write(":")
        if tree.upper != None:
            self._write(tree.upper)
        if tree.step != None:
            self._write(":")
            self._write(tree.step)

    def _write_ExtSlice(self, tree):
        """
        Write out an extended slice.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("mylist[:2,4:]"), BasicWriter)
        mylist[:2,4:]

        """

        self._interleave_write(tree.dims,
            between = (lambda: self._write(",")))

    def _write_Index(self, tree):
        """
        Write out an index.

        >>> import ast, sourcewriter
        >>> sourcewriter.printSource(ast.parse("mylist[1]"), BasicWriter)
        mylist[1]

        """

        self._write(tree.value)


    # boolop - too simple to test
    def _write_And(self, tree): self._write("and")
    def _write_Or(self, tree): self._write("or")

    # operator - too simple to bother testing
    def _write_Add(self, tree): self._write("+")
    def _write_Sub(self, tree): self._write("-")
    def _write_Mult(self, tree): self._write("*")
    def _write_Div(self, tree): self._write("/")
    def _write_Mod(self, tree): self._write("%")
    def _write_Pow(self, tree): self._write("**")
    def _write_LShift(self, tree): self._write("<<")
    def _write_RShift(self, tree): self._write(">>")
    def _write_BitOr(self, tree): self._write("|")
    def _write_BitXor(self, tree): self._write("^")
    def _write_BitAnd(self, tree): self._write("&")
    def _write_FloorDiv(self, tree): self._write("//")

    # unaryop - too simple
    def _write_Invert(self, tree): self._write("~")
    def _write_Not(self, tree): self._write("not")
    def _write_UAdd(self, tree): self._write("+")
    def _write_USub(self, tree): self._write("-")

    # cmpop - too simple
    def _write_Eq(self, tree): self._write("==")
    def _write_NotEq(self, tree): self._write("!=")
    def _write_Lt(self, tree): self._write("<")
    def _write_LtE(self, tree): self._write("<=")
    def _write_Gt(self, tree): self._write(">")
    def _write_GtE(self, tree): self._write(">=")
    def _write_Is(self, tree): self._write("is")
    def _write_IsNot(self, tree): self._write("is not")
    def _write_In(self, tree): self._write("in")
    def _write_NotIn(self, tree): self._write("not in")

    # comprehension
    def _write_comprehension(self, tree):
        """
        Write out one piece of a comprehension.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("[x for x in range(10) if x != 5]")
        >>> sourcewriter.printSource(myast, BasicWriter)
        [x for x in range(10) if x != 5]

        """

        self._write("for ")
        self._write(tree.target)
        self._write(" in ")
        self._write(tree.iter)

        self._interleave_write(tree.ifs,
            before = (lambda: self._write(" if ")))


    # excepthandler
    def _write_ExceptHandler(self, tree):
        """
        Write out an exception handler.

        >>> import ast, sourcewriter
        >>> c = '''
        ... try: pass
        ... except Exception as exc: pass
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        try:
            pass
        except Exception as exc:
            pass

        """

        self._write("except")

        if tree.type != None:
            self._write(" ")
            self._write(tree.type)

            if tree.name != None:
                self._write(" as " + tree.name)

        self._write_block(tree.body)


    # arguments
    def _write_arguments(self, tree):
        """
        Write out a set of arguments.

        >>> import ast, sourcewriter
        >>> c = '''
        ... def f(a : "An argument", b = None, *args, kwo = True, **kwargs): pass
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        def f(a : 'An argument', b = None, *args, kwo = True, **kwargs):
            pass

        """

        had_arg = False # Cannot use _separated_write here

        n_posargs = len(tree.args) - len(tree.defaults)

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
        if tree.vararg != None:
            if had_arg:
                self._write(", ")
            had_arg = True
            self._write("*")
            self._write(tree.vararg)
            if tree.varargannotation != None:
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
        if tree.kwarg != None:
            if had_arg:
                self._write(", ")
            had_arg = False
            self._write("**")
            self._write(tree.kwarg)
            if tree.kwargannotation != None:
                self._write(" : ")
                self._write(tree.kwargannotation)

    # arg
    def _write_arg(self, tree):
        """
        Write out a single argument.

        >>> import ast, sourcewriter
        >>> c = '''
        ... def f(a : "An argument"): pass
        ... '''
        >>> myast = ast.parse(c)
        >>> sourcewriter.printSource(myast, BasicWriter)
        def f(a : 'An argument'):
            pass

        """

        self._write(tree.arg)
        if tree.annotation != None:
            self._write(" : ")
            self._write(tree.annotation)


    # keyword
    def _write_keyword(self, tree):
        """
        Write out a keyword from an argument list.

        >>> import ast, sourcewriter
        >>> myast = ast.parse("class c(a = b): pass")
        >>> sourcewriter.printSource(myast, BasicWriter)
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

        >>> import ast, sourcewriter
        >>> myast = ast.parse("import hello as world")
        >>> sourcewriter.printSource(myast, BasicWriter)
        import hello as world

        """

        self._write(tree.name)

        if tree.asname != None:
            self._write(" as " + tree.asname)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
