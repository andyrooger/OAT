"""
Contains code ready for reordering statements.

"""

import ast
import random

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
                if not "breaks" in stat._markings:
                    return False
                if not "visible" in stat._markings:
                    return False
        except AttributeError:
            return False

        return True

    def fill_markings(self, breaks=True, visible=False):
        """Fill in unmarked unmarked statements with the given defaults."""

        for stat in self.statements:
            if not hasattr(stat, "_markings"):
                stat._markings = {}

            if not "breaks" in stat._markings:
                stat._markings["breaks"] = breaks

            if not "visible" in stat._markings:
                stat._markings["visible"] = visible

    def permutations(self):
        """Generates all possible permutations."""

        # Temporary until we have some useful functionality
        yield list(range(0, len(self.statements)-1))

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

            


def RandomValuer(self, statements, perm):
    """Give a random value, no matter the permutation."""

    return random.uniform(0, 100)
