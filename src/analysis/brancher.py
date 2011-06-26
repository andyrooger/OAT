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

        # Create if
        predicate, value = self.predicates.any()
        if not value:
            predicate = CustomAST(ast.UnaryOp(ast.Not(), predicate))
        basic_if = CustomAST(ast.If(predicate, during, []))

        # Add initialiser
        tracker = self._insert_initialiser(before)

        # All together
        together = CustomAST(before + [basic_if] + after)
        tracker = self._inserted_statement(len(before))

        return (together, tracker)
        

    def ifelse_branch(self, statements=None, start=None, end=None):
        if not all([self.initial, self.predicates]):
            return None
        if statements == None:
            return bool(self.randomising)

        before, during, after = self._split_list(statements, start, end)

        # Create if
        predicate, value = self.predicates.any()
        basic_if = CustomAST(ast.If(predicate, during, during))

        # Add initialiser
        tracker = self._insert_initialiser(before)

        # All together
        together = CustomAST(before + [basic_if] + after)
        tracker = self._inserted_statement(len(before))

        return (together, tracker)

    def except_branch(self, statements=None, start=None, end=None):
        if not all([self.initial, self.exceptions]):
            return None
        if statements == None:
            return bool(self.preserving)

        before, during, after = self._split_list(statements, start, end)

        # Create exception
        exc, raises, names = self.exceptions.any()
        handles, orelse = (during, []) if raises else ([], during)

        # Create handler
        if not names:
            handler = None
        else:
            name_objs = [ast.Name(n, ast.Load()) for n in names]
            if len(name_objs) == 1:
                handler = name_objs[0]
            else:
                handler = ast.Tuple(name_objs, ast.Load())
        exc_handler = ast.ExceptHandler(handler, None, handles)
        basic_exc = CustomAST(ast.TryExcept([exc], [exc_handler], orelse))

        # Add initialiser
        tracker = self._insert_initialiser(before)

        # All together
        together = CustomAST(before + [basic_exc] + after)
        tracker = self._inserted_statement(len(before))

        return (together, tracker)


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

        # Double probability for closer choices
        #start = random.randint(0, containing)
        start = random.choice(list(range(containing+1)) + list(range(containing//2, containing+1)))
        #end = random.randint(containing+1, total)
        end = random.choice(list(range(containing+1, total+1)) + list(range(containing+1, (containing+total+1)//2 + 1)))
        return (start, end)

    def _insert_initialiser(self, before, tracker=None):
        # Add initialiser
        init_val = self.initial.any()
        init = CustomAST(ast.Assign([ast.Name(self._name, ast.Store())], init_val))
        init_loc = random.randint(0, len(before)//2) # first half of the before section
        before.insert(init_loc, init)
        return self._inserted_statement(init_loc, tracker)

    def _inserted_statement(self, location, tracker=None):
        """Allows us to keep track of inserted statement locations."""

        if tracker == None:
            tracker = set()

        tracker = {(s if s < location else s+1) for s in tracker}
        tracker.add(location)
        return tracker

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

    def any(self):
        """Return any item in the collection."""

        try:
            return random.choice([self._collection[k] for k in self._collection])
        except IndexError:
            return None

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
