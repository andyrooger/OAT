"""
Contains code ready for reordering statements.

"""

import ast
import random

def RandomValuer(self, statements, perm):
    """Give a random value, no matter the permutation."""

    return random.uniform(0, 100)


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

        #self.fill_markings() # In case
        partitions = self.partition()

        return self._permutations(self, partitions)

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
                before = list(range(begin_partition, i-1))
                if before:
                    partitions.append(before)
                partitions.append([i])
                begin_partition = i+1

        before = list(range(begin_partition, len(self.statements)))
        if before:
            partitions.append(before)

        return partitions
                


