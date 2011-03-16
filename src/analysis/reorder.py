"""
Contains code ready for reordering statements.

"""

import ast
import random

def RandomValuer(statements, perm):
    """Give a random value, no matter the permutation."""

    return random.uniform(0, 100)

def FirstValuer(statements, perm):
    """Give exactly the same value, no matter the permutation."""

    return 1

class Reorderer:
    """
    Performs calculation on a set of statements and eventually returns a generator for different permutations.

    """

    def __init__(self, statements : "List of statements"):
        """Initialise reorderer or raise TypeError."""
        # Check type
        if not isinstance(statements, list):
            raise TypeError

        for stat in statements:
            if not isinstance(stat, ast.AST):
                raise TypeError

        self.statements = statements

    def check_markings(self):
        """Check if all statements have the correct markings."""

        try:
            for stat in self.statements:
                if "breaks" not in stat._markings:
                    return False
                if "visible" not in stat._markings:
                    return False
                if "reads" not in stat._markings:
                    return False
                if "writes" not in stat._markings:
                    return False
        except AttributeError:
            return False

        return True

    def permutations(self):
        """Generates all possible permutations."""

        #self.fill_markings() # In case
        partitions = self.partition()

        return self._permutations(partitions)

    def _permutations(self, partitions : "As returned by partition()"):
        """Does the actual generation for permutations."""

        # Base, if there are no partitions left
        if not partitions:
            yield []
        else:
            head, *tail = partitions

            # Recalculate everything for each permutation? Yes
            # Difficult calculation? Hopefully not
            # Do the bigger calculation less

            for remainder in self._permutations(tail):
                for perm in self.part_permute(head):
                    yield perm + remainder

    def part_permute(self, part : "List of indices to statements"):
        """Generate all the possible permutations for a single partition."""

        # Temporary until we have some useful functionality
        yield part

    def permute(self, perm):
        """Permute the statements with the given permutation. Does not affect the original statement list."""

        return [self.statements[i] for i in perm]

    def best_permutation(self, valuer=RandomValuer):
        """Select the best permutation (with the highest value from the value function)."""

        perms = self.permutations()
        best_perm = perms.__next__()
        best_score = valuer(self.statements, best_perm)

        for perm in perms:
            score = valuer(self.statements, perm)
            if score > best_score:
                best_perm = perm
                best_score = score

        return best_perm

    def partition(self):
        """
        Partition the statement list based on the breaking statements.

        All the statements must be already marked.

        You will receive a list of permutations.

        """

        begin_partition = 0
        partitions = []

        for i in range(len(self.statements)):
            if self.statements[i]._markings['breaks'] == 'yes':
                before = list(range(begin_partition, i))
                if before:
                    partitions.append(before)
                partitions.append([i])
                begin_partition = i+1

        before = list(range(begin_partition, len(self.statements)))
        if before:
            partitions.append(before)

        return partitions

class AutoMarker:
    """Tries to find correct markings for each node."""

    def markings(self, node : "AST node to check for markings"):
        """
        Tries to calculate markings for some node in the AST in the form ([reads], [writes], visible, breaks).

        Raises TypeError if the AST node cannot be recognised.

        """

        try:
            method = getattr(self, "_marks_" + node.__class__.__name__)
        except AttributeError as exc:
            raise TypeError("Unknown AST node") from exc
        else:
            return method(node)

    def _marks_list(self, node):
        """Find markings for a list of statements."""

        return ([], [], True, True) # TODO

    def _marks_Module(self, node):
        return self.marks(node.body)

    def _marks_Interactive(self, node):
        return self.marks(node.body)

    def _marks_Expression(self, node):
        return self.marks(node.body)

    def _marks_Suite(self, node): # TODO - check what this is
        return self.marks(node.body)

    # stmt
    #def _marks_FunctionDef(self, node): raise NotImplementedError
    #def _marks_ClassDef(self, node): raise NotImplementedError
    #def _marks_Return(self, node): raise NotImplementedError

    #def _marks_Delete(self, node): raise NotImplementedError
    #def _marks_Assign(self, node): raise NotImplementedError
    #def _marks_AugAssign(self, node): raise NotImplementedError

    #def _marks_For(self, node): raise NotImplementedError
    #def _marks_While(self, node): raise NotImplementedError
    #def _marks_If(self, node): raise NotImplementedError
    #def _marks_With(self, node): raise NotImplementedError

    #def _marks_Raise(self, node): raise NotImplementedError
    #def _marks_TryExcept(self, node): raise NotImplementedError
    #def _marks_TryFinally(self, node): raise NotImplementedError
    #def _marks_Assert(self, node): raise NotImplementedError

    #def _marks_Import(self, node): raise NotImplementedError
    #def _marks_ImportFrom(self, node): raise NotImplementedError

    #def _marks_Global(self, node): raise NotImplementedError
    #def _marks_Nonlocal(self, node): raise NotImplementedError
    #def _marks_Expr(self, node): raise NotImplementedError
    #def _marks_Pass(self, node): raise NotImplementedError
    #def _marks_Break(self, node): raise NotImplementedError
    #def _marks_Continue(self, node): raise NotImplementedError

    # expr
    #def _marks_BoolOp(self, node): raise NotImplementedError
    #def _marks_BinOp(self, node): raise NotImplementedError
    #def _marks_UnaryOp(self, node): raise NotImplementedError
    #def _marks_Lambda(self, node): raise NotImplementedError
    #def _marks_IfExp(self, node): raise NotImplementedError
    #def _marks_Dict(self, node): raise NotImplementedError
    #def _marks_Set(self, node): raise NotImplementedError
    #def _marks_ListComp(self, node): raise NotImplementedError
    #def _marks_SetComp(self, node): raise NotImplementedError
    #def _marks_DictComp(self, node): raise NotImplementedError
    #def _marks_GeneratorExp(self, node): raise NotImplementedError

    #def _marks_Yield(self, node): raise NotImplementedError

    #def _marks_Compare(self, node): raise NotImplementedError
    #def _marks_Call(self, node): raise NotImplementedError
    #def _marks_Num(self, node): raise NotImplementedError
    #def _marks_Str(self, node): raise NotImplementedError
    #def _marks_Bytes(self, node): raise NotImplementedError
    #def _marks_Ellipsis(self, node): raise NotImplementedError

    #def _marks_Attribute(self, node): raise NotImplementedError
    #def _marks_Subscript(self, node): raise NotImplementedError
    #def _marks_Starred(self, node): raise NotImplementedError
    #def _marks_Name(self, node): raise NotImplementedError
    #def _marks_List(self, node): raise NotImplementedError
    #def _marks_Tuple(self, node): raise NotImplementedError

    # expr_context
    #def _marks_Load(self, node): raise NotImplementedError
    #def _marks_Store(self, node): raise NotImplementedError
    #def _marks_Del(self, node): raise NotImplementedError
    #def _marks_AugLoad(self, node): raise NotImplementedError
    #def _marks_AugStore(self, node): raise NotImplementedError
    #def _marks_Param(self, node): raise NotImplementedError

    # slice
    #def _marks_Slice(self, node): raise NotImplementedError
    #def _marks_ExtSlice(self, node): raise NotImplementedError
    #def _marks_Index(self, node): raise NotImplementedError

    # boolop
    #def _marks_And(self, node): raise NotImplementedError
    #def _marks_Or(self, node): raise NotImplementedError

    # operator
    #def _marks_Add(self, node): raise NotImplementedError
    #def _marks_Sub(self, node): raise NotImplementedError
    #def _marks_Mult(self, node): raise NotImplementedError
    #def _marks_Div(self, node): raise NotImplementedError
    #def _marks_Mod(self, node): raise NotImplementedError
    #def _marks_Pow(self, node): raise NotImplementedError
    #def _marks_LShift(self, node): raise NotImplementedError
    #def _marks_RShift(self, node): raise NotImplementedError
    #def _marks_BitOr(self, node): raise NotImplementedError
    #def _marks_BitXor(self, node): raise NotImplementedError
    #def _marks_BitAnd(self, node): raise NotImplementedError
    #def _marks_FloorDiv(self, node): raise NotImplementedError

    # unaryop
    #def _marks_Invert(self, node): raise NotImplementedError
    #def _marks_Not(self, node): raise NotImplementedError
    #def _marks_UAdd(self, node): raise NotImplementedError
    #def _marks_USub(self, node): raise NotImplementedError

    # cmpop
    #def _marks_Eq(self, node): raise NotImplementedError
    #def _marks_NotEq(self, node): raise NotImplementedError
    #def _marks_Lt(self, node): raise NotImplementedError
    #def _marks_LtE(self, node): raise NotImplementedError
    #def _marks_Gt(self, node): raise NotImplementedError
    #def _marks_GtE(self, node): raise NotImplementedError
    #def _marks_Is(self, node): raise NotImplementedError
    #def _marks_IsNot(self, node): raise NotImplementedError
    #def _marks_In(self, node): raise NotImplementedError
    #def _marks_NotIn(self, node): raise NotImplementedError

    # comprehension
    #def _marks_comprehension(self, node): raise NotImplementedError

    # excepthandler
    #def _marks_ExceptHandler(self, node): raise NotImplementedError

    # arguments
    #def _marks_arguments(self, node): raise NotImplementedError

    # arg
    #def _marks_arg(self, node): raise NotImplementedError

    # keyword
    #def _marks_keyword(self, node): raise NotImplementedError

    # alias
    #def _marks_alias(self, node): raise NotImplementedError

