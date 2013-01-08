"""
Holds the base class for source writers, it should somehow take an AST and
ouput correct source.

This should be extended for obfuscated syntax or really pretty output etc.

"""

# OAT - Obfuscation and Analysis Tool
# Copyright (C) 2011  Andy Gurden
# 
#     This file is part of OAT.
# 
#     OAT is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     OAT is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with OAT.  If not, see <http://www.gnu.org/licenses/>.

import ast
import sys

from . import sourcewriter
from analysis.customast import CustomAST

class BasicWriter(sourcewriter.SourceWriter):
    """
    Writes source from an AST. Should be very simple and abide to the style guide.

    One option would have been to build an ast walker from the given walker
    classes, but I want a definite order. (None specified in the docs).

    >>> import ast
    >>> from . import sourcewriter
    >>> theast = None
    >>> with open("../example/stuff.py") as file:
    ...     theast = ast.parse(file.read(), "stuff.py", "exec")
    >>> theast = CustomAST(theast)
    >>> theast.type()
    'Module'
    >>> with open("../example/stuff.py.basicformat") as file:
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
        TypeError: The tree needs to begin with a CustomAST node.
        >>> import ast
        >>> myast = CustomAST(ast.AST())
        >>> myast = BasicWriter(myast)

        """

        super().__init__(top_ast, out)

    def _write_Module(self, tree):
        """
        Write out a Module object.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.Module([ast.Expr(ast.Str("Hello"))]))
        >>> sourcewriter.printSource(myast, BasicWriter)
        'Hello'

        """

        self._write_block(tree["body"], indent = False)

    def _write_Interactive(self, tree):
        """
        Write out an interactive session.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.Interactive([ast.Expr(ast.Str("Hello"))]))
        >>> sourcewriter.srcToStr(myast, BasicWriter) == ">>> 'Hello'"
        True

        """

        old_interactive = self._is_interactive()
        self._is_interactive(True)
        self._write_block(tree["body"], indent = False)
        self._is_interactive(old_interactive)

    def _write_Expression(self, tree):
        """
        Write out a solo expression.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.Expression(ast.Expr(ast.Str("Hello"))))
        >>> sourcewriter.printSource(myast, BasicWriter)
        'Hello'

        """

        self._write_block(CustomAST([tree["body"]]), indent = False)
    

    def _write_Suite(self, tree):
        raise NotImplementedError("I have no idea what a suite is supposed to be")

    # stmt
    def _write_FunctionDef(self, tree):
        """
        Write out a function.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... @afunction
        ... def myfunction(arg1, arg2, arg3=None):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        @afunction
        def myfunction(arg1, arg2, arg3 = None):
            print('hi')
            print('bye')

        """

        self._interleave_write(
            tree["decorator_list"],
            before = (lambda: self._ground_write("@")),
            after = self._next_statement)

        self._ground_write("def ")
        self._write(tree["name"])
        self._ground_write("(")
        self._write(tree["args"])
        self._ground_write(")")
        if not tree["returns"].is_empty():
            self._ground_write(" -> ")
            self._write(tree["returns"])
        self._write_block(tree["body"])

    def _write_ClassDef(self, tree):
        """
        Write out a class definition.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... @aclassdecorator
        ... class myclass(base1, base2, metaclass=m, *varpos, **varkey):
        ...     print("hi")
        ...     print("bye")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        @aclassdecorator
        class myclass(base1, base2, metaclass = m, *varpos, **varkey):
            print('hi')
            print('bye')

        """

        self._interleave_write(tree["decorator_list"],
            before=(lambda: self._ground_write("@")),
            after=self._next_statement)

        self._ground_write("class ")
        self._write(tree["name"])
        if (not tree["bases"].is_empty() or
           not tree["keywords"].is_empty() or
           not tree["starargs"].is_empty() or
           not tree["kwargs"].is_empty()):
            self._ground_write("(")

            self._interleave_write(
                tree["bases"].temp_list(tree["keywords"]),
                between=(lambda: self._ground_write(", ")))

            had_arg = tree["bases"] or tree["keywords"]

            if not tree["starargs"].is_empty():
                if had_arg:
                    self._ground_write(", ")
                had_arg = True
                self._ground_write("*")
                self._write(tree["starargs"])

            if not tree["kwargs"].is_empty():
                if had_arg:
                    self._ground_write(", ")
                had_arg = True
                self._ground_write("**")
                self._write(tree["kwargs"])

            self._ground_write(")")
        self._write_block(tree["body"])
        

    def _write_Return(self, tree):
        """
        Write out a return statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("return 'Hello there'"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        return 'Hello there'
        >>> myast = CustomAST(ast.parse("return"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        return

        """

        self._ground_write("return")
        if not tree["value"].is_empty():
            self._ground_write(" ")
            self._write(tree["value"])

    def _write_Delete(self, tree):
        """
        Write out a delete statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("del myvar, yourvar"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        del myvar, yourvar

        """

        self._ground_write("del ")
        self._interleave_write(tree["targets"],
            between=(lambda: self._ground_write(", ")))


    def _write_Assign(self, tree):
        """
        Write out an assignment statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("a=b=c=142"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        a = b = c = 142

        """

        self._interleave_write(tree["targets"],
            between=(lambda: self._ground_write(" = ")))
        self._ground_write(" = ")
        self._write(tree["value"])


    def _write_AugAssign(self, tree):
        """
        Write out an assignment augmentation statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("a+=2"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        a += 2

        """

        self._write(tree["target"])
        self._ground_write(" ")
        self._write(tree["op"])
        self._ground_write("= ")
        self._write(tree["value"])

    def _write_For(self, tree):
        """
        Write out a for loop.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... for i in range(3):
        ...     print(str(i))
        ... else:
        ...     print("I wonder how this happened...")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        for i in range(3):
            print(str(i))
        else:
            print('I wonder how this happened...')

        """

        self._ground_write("for ")
        self._write(tree["target"])
        self._ground_write(" in ")
        self._write(tree["iter"])
        self._write_block(tree["body"])

        if not tree["orelse"].is_empty():
            self._next_statement()
            self._ground_write("else")
            self._write_block(tree["orelse"])

    def _write_While(self, tree):
        """
        Write out a while loop.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... while True:
        ...     pass
        ... else:
        ...     print("Never get here.")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        while True:
            pass
        else:
            print('Never get here.')

        """

        self._ground_write("while ")
        self._write(tree["test"])
        self._write_block(tree["body"])

        if not tree["orelse"].is_empty():
            self._next_statement()
            self._ground_write("else")
            self._write_block(tree["orelse"])

    def _write_If(self, tree):
        """
        Write out an if statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... if "linux" in sys.platform:
        ...     print(":)")
        ... else:
        ...     print(":(")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        if 'linux' in sys.platform:
            print(':)')
        else:
            print(':(')

        """

        self._ground_write("if ")
        self._write(tree["test"])
        self._write_block(tree["body"])

        if not tree["orelse"].is_empty():
            self._next_statement()
            self._ground_write("else")
            self._write_block(tree["orelse"])


    def _write_With(self, tree):
        """
        Write out with statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... with open("/dev/null") as nothing:
        ...     nothing.write("hello")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        with open('/dev/null') as nothing:
            nothing.write('hello')

        """

        self._ground_write("with ")
        self._write(tree["context_expr"])

        if not tree["optional_vars"].is_empty():
            self._ground_write(" as ")
            self._write(tree["optional_vars"])

        self._write_block(tree["body"])


    def _write_Raise(self, tree):
        """
        Write out raise statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("raise Exception('Bad thing happened') from Exception()"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        raise Exception('Bad thing happened') from Exception()
        >>> myast = CustomAST(ast.parse("raise"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        raise

        """

        self._ground_write("raise")

        if not tree["exc"].is_empty():
            self._ground_write(" ")
            self._write(tree["exc"])

            if not tree["cause"].is_empty():
                self._ground_write(" from ")
                self._write(tree["cause"])


    def _write_TryExcept(self, tree):
        """
        Write out a try catch statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... try: raise Exception
        ... except Exception: pass
        ... except: pass
        ... else: print("Oh...")
        ... '''
        >>> myast = CustomAST(ast.parse(c))
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

        self._ground_write("try")
        self._write_block(tree["body"])

        self._interleave_write(tree["handlers"],
            before = self._next_statement)

        if not tree["orelse"].is_empty():
            self._next_statement()
            self._ground_write("else")
            self._write_block(tree["orelse"])
        

    def _write_TryFinally(self, tree):
        """
        Write out a try finally statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... try: raise Exception
        ... finally: pass
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        try:
            raise Exception
        finally:
            pass

        """

        self._ground_write("try")
        self._write_block(tree["body"])

        self._next_statement()
        self._ground_write("finally")
        self._write_block(tree["finalbody"])

    def _write_Assert(self, tree):
        """
        Write out an assert statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("assert False, 'Oh dear'"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        assert False, 'Oh dear'

        """

        self._ground_write("assert ")
        self._write(tree["test"])

        if not tree["msg"].is_empty():
            self._ground_write(", ")
            self._write(tree["msg"])


    def _write_Import(self, tree):
        """
        Write out an import statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("import sys, os"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        import sys, os

        """

        self._ground_write("import ")
        self._interleave_write(tree["names"],
            between = (lambda: self._ground_write(", ")))

    def _write_ImportFrom(self, tree):
        """
        Write out an import from statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("from .. sys import sys as sys2, os"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        from ..sys import sys as sys2, os
        >>> myast = CustomAST(ast.parse("from .. import sys as sys2, os"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        from .. import sys as sys2, os

        """

        self._ground_write("from ")
        if tree["level"].node():
            self._ground_write("." * tree["level"].node())
        if not tree["module"].is_empty():
            self._write(tree["module"])
        self._ground_write(" import ")

        self._interleave_write(tree["names"],
            between = (lambda: self._ground_write(", ")))


    def _write_Global(self, tree):
        """
        Write out a global variable.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("global g1, g2"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        global g1, g2

        """

        self._ground_write("global ")
        self._interleave_write(tree["names"],
            between = (lambda: self._ground_write(", ")))


    def _write_Nonlocal(self, tree):
        """
        Write out a nonlocal variable.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("nonlocal n1, n2"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        nonlocal n1, n2

        """

        self._ground_write("nonlocal ")
        self._interleave_write(tree["names"],
            between = (lambda: self._ground_write(", ")))


    def _write_Expr(self, tree):
        """
        Write out an expression.

        >>> import ast
        >>> from . import sourcewriter
        >>> innerast = ast.Str("Hello")
        >>> outerast = CustomAST(ast.Expr(innerast))
        >>> innerast = CustomAST(innerast)
        >>> sourcewriter.srcToStr(innerast, BasicWriter) == sourcewriter.srcToStr(outerast, BasicWriter)
        True

        """

        self._write(tree["value"])


    # not worth testing
    def _write_Pass(self, tree): self._ground_write("pass")
    def _write_Break(self, tree): self._ground_write("break")
    def _write_Continue(self, tree): self._ground_write("continue")

    # expr
    def _write_BoolOp(self, tree):
        """
        Write out a boolean operation.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("a and b or c"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        ((a and b) or c)

        """

        def sep():
            self._ground_write(" ")
            self._write(tree["op"])
            self._ground_write(" ")

        self._ground_write("(")
        self._interleave_write(tree["values"], between = sep)
        self._ground_write(")")

    def _write_BinOp(self, tree):
        """
        Write out a binary operation.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("a / 2 * 3 + 10"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        (((a / 2) * 3) + 10)

        """

        self._ground_write("(")
        self._write(tree["left"])
        self._ground_write(" ")
        self._write(tree["op"])
        self._ground_write(" ")
        self._write(tree["right"])
        self._ground_write(")")

    def _write_UnaryOp(self, tree):
        """
        Write out a unary operation.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("not ~a"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        not ~ a

        """

        self._write(tree["op"])
        self._ground_write(" ")
        self._write(tree["operand"])

    def _write_Lambda(self, tree):
        """
        Write out a lambda expression.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("lambda a,b,c: a + b + c"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        lambda a, b, c: ((a + b) + c)

        """

        self._ground_write("lambda")
        if not tree["args"].is_empty():
            self._ground_write(" ")
            self._write(tree["args"])
        self._ground_write(": ")
        self._write(tree["body"])

    def _write_IfExp(self, tree):
        """
        Write out an inline if expression.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("a if b else c"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        a if b else c

        """

        self._write(tree["body"])
        self._ground_write(" if ")
        self._write(tree["test"])
        self._ground_write(" else ")
        self._write(tree["orelse"])


    def _write_Dict(self, tree):
        """
        Write out a dictionary object.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("{1 : 'partridge in a pear tree', 2: 'two turtle doves', 3: 'three french hens'}"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        {1: 'partridge in a pear tree', 2: 'two turtle doves', 3: 'three french hens'}

        """

        self._ground_write("{")

        had_arg = False
        for child in tree["keys"]:
            if had_arg:
                self._ground_write(", ")
            else:
                had_arg = True
            self._write(tree["keys"][child])
            self._ground_write(": ")
            self._write(tree["values"][child])

        self._ground_write("}")


    def _write_Set(self, tree):
        """
        Write out a set object.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("{2,3,5,7,13,17,19}"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        {2, 3, 5, 7, 13, 17, 19}

        """

        self._ground_write("{")
        self._interleave_write(tree["elts"],
            between = (lambda: self._ground_write(", ")))
        self._ground_write("}")


    def _write_ListComp(self, tree):
        """
        Write out a list comprehension.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("[x*y for x in range(10) if x != 5 for y in range(10) if y != 5]"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        [(x * y) for x in range(10) if x != 5 for y in range(10) if y != 5]

        """

        self._ground_write("[")
        self._write(tree["elt"])
        self._interleave_write(tree["generators"],
            before = (lambda: self._ground_write(" ")))
        self._ground_write("]")

    def _write_SetComp(self, tree):
        """
        Write out a set comprehension.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("{x*y for x in range(10) if x != 5 for y in range(10) if y != 5}"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        {(x * y) for x in range(10) if x != 5 for y in range(10) if y != 5}

        """

        self._ground_write("{")
        self._write(tree["elt"])
        self._interleave_write(tree["generators"],
            before = (lambda: self._ground_write(" ")))
        self._ground_write("}")

    def _write_DictComp(self, tree):
        """
        Write out a dictionary comprehension.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("{x: y for x in range(10) if x != 5 for y in range(10) if y != 5}"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        {x: y for x in range(10) if x != 5 for y in range(10) if y != 5}

        """

        self._ground_write("{")
        self._write(tree["key"])
        self._ground_write(": ")
        self._write(tree["value"])
        self._interleave_write(tree["generators"],
            before = (lambda: self._ground_write(" ")))
        self._ground_write("}")

    def _write_GeneratorExp(self, tree):
        """
        Write out a generator expression.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("(x*y for x in range(10) if x != 5 for y in range(10) if y != 5)"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        ((x * y) for x in range(10) if x != 5 for y in range(10) if y != 5)

        """

        self._ground_write("(")
        self._write(tree["elt"])
        self._interleave_write(tree["generators"],
            before = (lambda: self._ground_write(" ")))
        self._ground_write(")")

    def _write_Yield(self, tree):
        """
        Write out a yield statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("yield x"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        yield x

        """

        self._ground_write("yield")
        if not tree["value"].is_empty():
            self._ground_write(" ")
            self._write(tree["value"])

    def _write_Compare(self, tree):
        """
        Write out a compare statement.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("a != b < c > d"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        a != b < c > d

        """

        self._write(tree["left"])

        for child in tree["ops"]:
            self._ground_write(" ")
            self._write(tree["ops"][child])
            self._ground_write(" ")
            self._write(tree["comparators"][child])

    def _write_Call(self, tree):
        """
        Write out a function call.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("print('Hello world')"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        print('Hello world')

        """

        self._write(tree["func"])
        self._ground_write("(")

        allargs = tree["args"].temp_list(tree["keywords"])
        self._interleave_write(allargs,
            between = (lambda: self._ground_write(", ")))

        has_arg = bool(allargs)

        if not tree["starargs"].is_empty():
            if has_arg:
                self._ground_write(", ")
            has_arg = True
            self._ground_write("*")
            self._write(tree["starargs"])

        if not tree["kwargs"].is_empty():
            if has_arg:
                self._ground_write(", ")
            has_arg = True
            self._ground_write("*")
            self._write(tree["kwargs"])

        self._ground_write(")")

    def _write_Num(self, tree):
        """
        Write out a numerical object.

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("1042")), BasicWriter)
        1042

        """

        self._ground_write(repr(tree["n"].node()))

    def _write_Str(self, tree):
        """
        Write out a String object.

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.Str("Hello")), BasicWriter)
        'Hello'

        """

        self._ground_write(repr(tree["s"].node()))

    def _write_Bytes(self, tree):
        """
        Write out a Bytes object.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("b'hello world'"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        b'hello world'

        """

        self._ground_write(repr(tree["s"].node()))

    def _write_Ellipsis(self, tree): self._ground_write("...")

    def _write_Attribute(self, tree):
        """
        Write out an object attribute.

        Context is ignored.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("sys.path"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        sys.path

        """

        self._write(tree["value"])
        self._ground_write(".")
        self._write(tree["attr"])

    def _write_Subscript(self, tree):
        """
        Write out an object subscript.

        Context is ignored.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("mylist[2]"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        mylist[2]

        """

        self._write(tree["value"])
        self._ground_write("[")
        self._write(tree["slice"])
        self._ground_write("]")

    def _write_Starred(self, tree):
        """
        Write out a starred object.

        Context is ignored.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("head, *tail = list(range(10))"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        (head, *tail) = list(range(10))

        """

        self._ground_write("*")
        self._write(tree["value"])

    def _write_Name(self, tree):
        """
        Write out a name object. We ignore context...

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("a_var_name")), BasicWriter)
        a_var_name

        """

        self._write(tree["id"])

    def _write_List(self, tree):
        """
        Write out a list object.

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("[1,2,3,4]")), BasicWriter)
        [1, 2, 3, 4]

        """

        self._ground_write("[")
        self._interleave_write(tree["elts"],
            between = (lambda: self._ground_write(", ")))
        self._ground_write("]")


    def _write_Tuple(self, tree):
        """
        Write out a tuple.

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("(a,b,c)")), BasicWriter)
        (a, b, c)

        """

        self._ground_write("(")
        self._interleave_write(tree["elts"],
            between = (lambda: self._ground_write(", ")))
        self._ground_write(")")


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

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("mylist[1:10:2]")), BasicWriter)
        mylist[1:10:2]

        """

        if not tree["lower"].is_empty():
            self._write(tree["lower"])
        self._ground_write(":")
        if not tree["upper"].is_empty():
            self._write(tree["upper"])
        if not tree["step"].is_empty():
            self._ground_write(":")
            self._write(tree["step"])

    def _write_ExtSlice(self, tree):
        """
        Write out an extended slice.

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("mylist[:2,4:]")), BasicWriter)
        mylist[:2,4:]

        """

        self._interleave_write(tree["dims"],
            between = (lambda: self._ground_write(",")))

    def _write_Index(self, tree):
        """
        Write out an index.

        >>> import ast
        >>> from . import sourcewriter
        >>> sourcewriter.printSource(CustomAST(ast.parse("mylist[1]")), BasicWriter)
        mylist[1]

        """

        self._write(tree["value"])


    # boolop - too simple to test
    def _write_And(self, tree): self._ground_write("and")
    def _write_Or(self, tree): self._ground_write("or")

    # operator - too simple to bother testing
    def _write_Add(self, tree): self._ground_write("+")
    def _write_Sub(self, tree): self._ground_write("-")
    def _write_Mult(self, tree): self._ground_write("*")
    def _write_Div(self, tree): self._ground_write("/")
    def _write_Mod(self, tree): self._ground_write("%")
    def _write_Pow(self, tree): self._ground_write("**")
    def _write_LShift(self, tree): self._ground_write("<<")
    def _write_RShift(self, tree): self._ground_write(">>")
    def _write_BitOr(self, tree): self._ground_write("|")
    def _write_BitXor(self, tree): self._ground_write("^")
    def _write_BitAnd(self, tree): self._ground_write("&")
    def _write_FloorDiv(self, tree): self._ground_write("//")

    # unaryop - too simple
    def _write_Invert(self, tree): self._ground_write("~")
    def _write_Not(self, tree): self._ground_write("not")
    def _write_UAdd(self, tree): self._ground_write("+")
    def _write_USub(self, tree): self._ground_write("-")

    # cmpop - too simple
    def _write_Eq(self, tree): self._ground_write("==")
    def _write_NotEq(self, tree): self._ground_write("!=")
    def _write_Lt(self, tree): self._ground_write("<")
    def _write_LtE(self, tree): self._ground_write("<=")
    def _write_Gt(self, tree): self._ground_write(">")
    def _write_GtE(self, tree): self._ground_write(">=")
    def _write_Is(self, tree): self._ground_write("is")
    def _write_IsNot(self, tree): self._ground_write("is not")
    def _write_In(self, tree): self._ground_write("in")
    def _write_NotIn(self, tree): self._ground_write("not in")

    # comprehension
    def _write_comprehension(self, tree):
        """
        Write out one piece of a comprehension.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("[x for x in range(10) if x != 5]"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        [x for x in range(10) if x != 5]

        """

        self._ground_write("for ")
        self._write(tree["target"])
        self._ground_write(" in ")
        self._write(tree["iter"])

        self._interleave_write(tree["ifs"],
            before = (lambda: self._ground_write(" if ")))


    # excepthandler
    def _write_ExceptHandler(self, tree):
        """
        Write out an exception handler.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... try: pass
        ... except Exception as exc: pass
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        try:
            pass
        except Exception as exc:
            pass

        """

        self._ground_write("except")

        if not tree["type"].is_empty():
            self._ground_write(" ")
            self._write(tree["type"])

            if not tree["name"].is_empty():
                self._ground_write(" as ")
                self._write(tree["name"])

        self._write_block(tree["body"])


    # arguments
    def _write_arguments(self, tree):
        """
        Write out a set of arguments.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... def f(a : "An argument", b = None, *args, kwo = True, **kwargs): pass
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        def f(a : 'An argument', b = None, *args, kwo = True, **kwargs):
            pass

        """

        had_arg = False # Cannot use _separated_write here

        ordered_args = list(tree["args"].ordered_children())
        n_posargs = len(ordered_args) - len(tree["defaults"].node())

        # positional args
        for arg in ordered_args[:n_posargs]:
            if had_arg:
                self._ground_write(", ")
            had_arg = True
            self._write(tree["args"][arg])

        # keyword args
        for (arg, default) in zip(ordered_args[n_posargs:], tree["defaults"].ordered_children()):
            if had_arg:
                self._ground_write(", ")
            had_arg = True
            self._write(tree["args"][arg])
            self._ground_write(" = ")
            self._write(tree["defaults"][default])

        # variable positional args
        if not tree["vararg"].is_empty():
            if had_arg:
                self._ground_write(", ")
            had_arg = True
            self._ground_write("*")
            self._write(tree["vararg"])
            if not tree["varargannotation"].is_empty():
                self._ground_write(" : ")
                self._write(tree["varargannotation"])
        elif not tree["kwonlyargs"].is_empty():
            if had_arg:
                self._ground_write(", ")
            had_arg = True
            self._ground_write("*")

        # keyword only args
        for child in tree["kwonlyargs"]:
            if had_arg:
                self._ground_write(", ")
            had_arg = True
            self._write(tree["kwonlyargs"][child])
            self._ground_write(" = ")
            self._write(tree["kw_defaults"][child])

        # variable keyword args
        if not tree["kwarg"].is_empty():
            if had_arg:
                self._ground_write(", ")
            had_arg = False
            self._ground_write("**")
            self._write(tree["kwarg"])
            if not tree["kwargannotation"].is_empty():
                self._ground_write(" : ")
                self._write(tree.kwargannotation)

    # arg
    def _write_arg(self, tree):
        """
        Write out a single argument.

        >>> import ast
        >>> from . import sourcewriter
        >>> c = '''
        ... def f(a : "An argument"): pass
        ... '''
        >>> myast = CustomAST(ast.parse(c))
        >>> sourcewriter.printSource(myast, BasicWriter)
        def f(a : 'An argument'):
            pass

        """

        self._write(tree["arg"])
        if not tree["annotation"].is_empty():
            self._ground_write(" : ")
            self._write(tree["annotation"])


    # keyword
    def _write_keyword(self, tree):
        """
        Write out a keyword from an argument list.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("class c(a = b): pass"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        class c(a = b):
            pass

        """

        self._write(tree["arg"])
        self._ground_write(" = ")
        self._write(tree["value"])


    # alias
    def _write_alias(self, tree):
        """
        Write out an alias.

        >>> import ast
        >>> from . import sourcewriter
        >>> myast = CustomAST(ast.parse("import hello as world"))
        >>> sourcewriter.printSource(myast, BasicWriter)
        import hello as world

        """

        self._write(tree["name"])

        if not tree["asname"].is_empty():
            self._ground_write(" as ")
            self._write(tree["asname"])


if __name__ == "__main__":
    import doctest
    doctest.testmod()
