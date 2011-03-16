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


     def dependencies(self, node : "AST node to check dependencies for"):
        """
        Check dependencies for some node in the AST in the form ([reads], [writes]).

        Raises TypeError if the AST node cannot be recognised.

        """

        try:
            method = getattr(self, "_depend_" + node.__class__.__name__)
        except AttributeError as exc:
            raise TypeError("Unknown AST node") from exc
        else:
            return method(node)

    def _depends_list(self, node):
        """Find dependencies for a list of statements."""

        return ([], []) # TODO

    def _depends_Module(self, node):
        return self.dependencies(node.body)

    def _depends_Interactive(self, node):
        return self.dependencies(node.body)

    def _depends_Expression(self, node):
        return self.dependencies(node.body)

    def _depends_Suite(self, node): # TODO - check what this is
        return self.dependencies(node)

    # stmt
    def _depends_FunctionDef(self, node): raise NotImplementedError
    def _depends_ClassDef(self, node): raise NotImplementedError
    def _depends_Return(self, node): raise NotImplementedError

    def _depends_Delete(self, node): raise NotImplementedError
    def _depends_Assign(self, node): raise NotImplementedError
    def _depends_AugAssign(self, node): raise NotImplementedError

    def _depends_For(self, node): raise NotImplementedError
    def _depends_While(self, node): raise NotImplementedError
    def _depends_If(self, node): raise NotImplementedError
    def _depends_With(self, node): raise NotImplementedError

    def _depends_Raise(self, node): raise NotImplementedError
    def _depends_TryExcept(self, node): raise NotImplementedError
    def _depends_TryFinally(self, node): raise NotImplementedError
    def _depends_Assert(self, node): raise NotImplementedError

    def _depends_Import(self, node): raise NotImplementedError
    def _depends_ImportFrom(self, node): raise NotImplementedError

    def _depends_Global(self, node): raise NotImplementedError
    def _depends_Nonlocal(self, node): raise NotImplementedError
    def _depends_Expr(self, node): raise NotImplementedError
    def _depends_Pass(self, node): raise NotImplementedError
    def _depends_Break(self, node): raise NotImplementedError
    def _depends_Continue(self, node): raise NotImplementedError

    # expr
    def _depends_BoolOp(self, node): raise NotImplementedError
    def _depends_BinOp(self, node): raise NotImplementedError
    def _depends_UnaryOp(self, node): raise NotImplementedError
    def _depends_Lambda(self, node): raise NotImplementedError
    def _depends_IfExp(self, node): raise NotImplementedError
    def _depends_Dict(self, node): raise NotImplementedError
    def _depends_Set(self, node): raise NotImplementedError
    def _depends_ListComp(self, node): raise NotImplementedError
    def _depends_SetComp(self, node): raise NotImplementedError
    def _depends_DictComp(self, node): raise NotImplementedError
    def _depends_GeneratorExp(self, node): raise NotImplementedError

    def _depends_Yield(self, node): raise NotImplementedError

    def _depends_Compare(self, node): raise NotImplementedError
    def _depends_Call(self, node): raise NotImplementedError
    def _depends_Num(self, node): raise NotImplementedError
    def _depends_Str(self, node): raise NotImplementedError
    def _depends_Bytes(self, node): raise NotImplementedError
    def _depends_Ellipsis(self, node): raise NotImplementedError

    def _depends_Attribute(self, node): raise NotImplementedError
    def _depends_Subscript(self, node): raise NotImplementedError
    def _depends_Starred(self, node): raise NotImplementedError
    def _depends_Name(self, node): raise NotImplementedError
    def _depends_List(self, node): raise NotImplementedError
    def _depends_Tuple(self, node): raise NotImplementedError

    # expr_context
    def _depends_Load(self, node): raise NotImplementedError
    def _depends_Store(self, node): raise NotImplementedError
    def _depends_Del(self, node): raise NotImplementedError
    def _depends_AugLoad(self, node): raise NotImplementedError
    def _depends_AugStore(self, node): raise NotImplementedError
    def _depends_Param(self, node): raise NotImplementedError

    # slice
    def _depends_Slice(self, node): raise NotImplementedError
    def _depends_ExtSlice(self, node): raise NotImplementedError
    def _depends_Index(self, node): raise NotImplementedError

    # boolop
    def _depends_And(self, node): raise NotImplementedError
    def _depends_Or(self, node): raise NotImplementedError

    # operator
    def _depends_Add(self, node): raise NotImplementedError
    def _depends_Sub(self, node): raise NotImplementedError
    def _depends_Mult(self, node): raise NotImplementedError
    def _depends_Div(self, node): raise NotImplementedError
    def _depends_Mod(self, node): raise NotImplementedError
    def _depends_Pow(self, node): raise NotImplementedError
    def _depends_LShift(self, node): raise NotImplementedError
    def _depends_RShift(self, node): raise NotImplementedError
    def _depends_BitOr(self, node): raise NotImplementedError
    def _depends_BitXor(self, node): raise NotImplementedError
    def _depends_BitAnd(self, node): raise NotImplementedError
    def _depends_FloorDiv(self, node): raise NotImplementedError

    # unaryop
    def _depends_Invert(self, node): raise NotImplementedError
    def _depends_Not(self, node): raise NotImplementedError
    def _depends_UAdd(self, node): raise NotImplementedError
    def _depends_USub(self, node): raise NotImplementedError

    # cmpop
    def _depends_Eq(self, node): raise NotImplementedError
    def _depends_NotEq(self, node): raise NotImplementedError
    def _depends_Lt(self, node): raise NotImplementedError
    def _depends_LtE(self, node): raise NotImplementedError
    def _depends_Gt(self, node): raise NotImplementedError
    def _depends_GtE(self, node): raise NotImplementedError
    def _depends_Is(self, node): raise NotImplementedError
    def _depends_IsNot(self, node): raise NotImplementedError
    def _depends_In(self, node): raise NotImplementedError
    def _depends_NotIn(self, node): raise NotImplementedError

    # comprehension
    def _depends_comprehension(self, node): raise NotImplementedError

    # excepthandler
    def _depends_ExceptHandler(self, node): raise NotImplementedError

    # arguments
    def _depends_arguments(self, node): raise NotImplementedError

    # arg
    def _depends_arg(self, node): raise NotImplementedError

    # keyword
    def _depends_keyword(self, node): raise NotImplementedError

    # alias
    def _depends_alias(self, node): raise NotImplementedError

