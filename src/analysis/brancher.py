"""
Tools to allow branching sections of the source code.

"""

import abc
import ast

from .customast import CustomAST
from writer.sourcewriter import srcToStr
from writer.prettywriter import PrettyWriter

class Brancher:
    """Holds information used to perform a particular type of branching."""

    def __init__(self, name):
        self._name = name
        self.predicates = PredicateCollection()
        self.exceptions = ExceptionCollection()
        self.initial = ExpressionCollection()
        self.preserving = StatementCollection()
        self.destroying = StatementCollection()
        self.randomising = StatementCollection()

    def if_branch(self, statements, start, end):
        pass

    def ifelse_branch(self, statements, start, end):
        pass

    def except_branch(self, statements, start, end):
        pass

    def while_branch(self, statements, start, end):
        pass

    def __str__(self):
        desc = "== Brancher for " + self._name + " =="
        for n in ["predicates", "exceptions", "initial",
                  "preserving", "destroying", "randomising"]:
            desc += "\n-- " + n.title() + " --\n"
            col = getattr(self, n)
            if not len(col):
                desc += "  Empty\n"
            for item in col:
                desc += "  " + str(item) + ": " + col.stringify(item) + "\n"
        return desc

class ProtectedCollection(metaclass = abc.ABCMeta):
    """Base for most of the collections in Brancher."""

    def __init__(self):
        self._collection = {}

    @abc.abstractmethod
    def add(self): pass

    @abc.abstractmethod
    def stringify(self): pass

    def _insert(self, item):
        key = 0
        if self._collection:
            key = max(self._collection.keys())+1
        self._collection[key] = item
        return key

    def __getitem__(self, key):
        return self._collection[key]

    def __delitem__(self, key):
        del self._collection[key]

    # No __setitem__, we use add for that

    def __iter__(self):
        return iter(self._collection)

    def __len__(self):
        return len(self._collection)

class PredicateCollection(ProtectedCollection):
    def add(self, pred, val):
        if not issubclass(pred.type(asclass=True), ast.expr):
            raise TypeError("Predicate must be an expression.")
        # bool(pred) should evaluate to val when name inited properly
        # Won't check
        return self._insert((pred, bool(val)))

    def stringify(self, id):
        (p, v) = self[id]
        return srcToStr(p, PrettyWriter) + " (Value: " + str(v) + ")"

class ExceptionCollection(ProtectedCollection):
    def add(self, expr, raises, *exc):
        if not issubclass(expr.type(asclass=True), ast.stmt):
            raise TypeError("Expr must be an statement.")
        # must raise/not raise (depending on raises) when name inited properly
        # Won't check
        for e in exc:
            if not isinstance(e, str):
                raise TypeError("Exception names must be strings.")
        return self._insert((expr, bool(raises), list(exc)))

    def stringify(self, id):
        (expr, raises, exc) = self[id]
        return srcToStr(expr, PrettyWriter) + (" Raises " if raises else " Avoids Raising ") + ", ".join(exc)

class ExpressionCollection(ProtectedCollection):
    def add(self, expr):
        if not issubclass(expr.type(asclass=True), ast.expr):
            raise TypeError("Expr must be an expression.")
        return self._insert(expr)

    def stringify(self, id):
        return srcToStr(self[id], PrettyWriter)

class StatementCollection(ProtectedCollection):
    def add(self, stmt):
        if not issubclass(expr.type(asclass=True), ast.stmt):
            raise TypeError("Stmt must be a statement.")
        return self._insert(stmt)

    def stringify(self, id):
        return srcToStr(self[id], PrettyWriter)
