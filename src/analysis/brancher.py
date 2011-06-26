"""
Tools to allow branching sections of the source code.

"""

import abc
import ast
import random

from .customast import CustomAST
from writer.sourcewriter import srcToStr
from writer.prettywriter import PrettyWriter

class Brancher:
    """Holds information used to perform a particular type of branching."""

    def __init__(self, name):
        if not name.isidentifier():
            raise ValueError("Name must be a valid identifier.")
        self._name = name
        self.predicates = PredicateCollection()
        self.exceptions = ExceptionCollection()
        self.initial = ExpressionCollection()
        self.preserving = StatementCollection()
        self.destroying = StatementCollection()
        self.randomising = StatementCollection()

    def if_branch(self, statements=None, start=None, end=None):
        if not all([self.initial, self.predicates]):
            return None
        if statements == None:
            return bool(self.preserving)

        before, during, after = self._split_list(statements, start, end)

    def ifelse_branch(self, statements=None, start=None, end=None):
        if not all([self.initial, self.predicates, self.randomising]):
            return None
        if statements == None:
            return True

        before, during, after = self._split_list(statements, start, end)

    def except_branch(self, statements=None, start=None, end=None):
        if not all([self.initial, self.exceptions]):
            return None
        if statements == None:
            return bool(self.preserving)

        before, during, after = self._split_list(statements, start, end)

    def while_branch(self, statements=None, start=None, end=None):
        if not all([self.initial, self.predicates, self.destroying]):
            return None
        if statements == None:
            return bool(self.preserving)

        before, during, after = self._split_list(statements, start, end)

    def _split_list(self, statements, start, end):
        """Split a CustomAST list of statements into 3 real lists, before, during and after the given range."""

        start, end = self._choose_range(start, end, len(statements))

        children = list(statements.ordered_children())
        before = [statements[c] for c in children[:start]]
        during = [statements[c] for c in children[start:end]]
        after = [statements[c] for c in children[end:]]

        return (before, during, after)

    def _choose_range(self, start, end, total):
        """Choose a correct range from the start and end indices given."""

        if start != None and end != None:
            return (start, end)

        containing = start if start != None else random.randint(0, total-1)
        if containing >= total:
            containing = total - 1
        if containing < 0:
            containing = 0

        start = random.randint(0, containing)
        end = random.randint(containing+1, total)
        return (start, end)

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
        if not issubclass(stmt.type(asclass=True), ast.stmt):
            raise TypeError("Stmt must be a statement.")
        if "body" in stmt:
            raise ValueError("Stmt must be a simple statement.")
        return self._insert(stmt)

    def stringify(self, id):
        return srcToStr(self[id], PrettyWriter)
