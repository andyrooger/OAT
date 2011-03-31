"""
Contains code ready for reordering statements.

"""

import ast
import random

from .markers import visible
from .markers import breaks
from .markers import read
from .markers import write
from .markers import indirectrw

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

        for stat in self.statements:
            if not breaks.BreakMarker(stat).is_marked():
                return False
            if not visible.VisibleMarker(stat).is_marked():
                return False
            if not read.ReadMarker(stat).is_marked():
                return False
            if not write.WriteMarker(stat).is_marked():
                return False
#            if not indirectrw.IndirectRWMarker(stat).is_marked():
#                return False

        return True

    def permutations(self):
        """Generates all possible permutations."""

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

        # Convert to the dependence tuple
        tuples = [self._statement_tuple(s) for s in part]
        dependence = [self._statement_dependence(tuples[i], tuples[:i]) for i in range(len(tuples))]

        # Grab the list of visible statements - saves some computation
        current = []
        rem = []
        for d in dependence:
            if visible.VisibleMarker(self.statements[d[0]]).isVisible():
                current.append(d)
            else:
                rem.append(d)

        for perm in self._insert_statements(rem, current):
            yield [s for (s, r, w) in perm]
        
    def _insert_statements(self, stats, current):
        """Find all the different ways the statements in stats can be inserted into current."""

        if not stats:
            yield current
            return

        for ins in self._insert_statement(stats[0], current):
            for perm in self._insert_statements(stats[1:], ins):
                yield perm

    def _insert_statement(self, stat, stats):
        """Yields all the ways to insert the statement stat into stats."""

        (s_stat, s_reads, s_writes) = stat

        # This new statement will be valid if it comes between the last statement we have recorded as writing for us
        # and the first statement after that point that writes to any of the variables we have recorded as writing for us
        # where the actual statement is in stats

        # Find the variables where our expected write is somewhere in stats. (i.e. The ones we will pay attention to at this point)
        pay_attention = set()
        for var in s_reads: # Look through variables we read in the insertion statement
            if s_reads[var] == None or any(s_reads[var] == s for (s, r, w) in stats): # If the value we want is never written or written in stats
                pay_attention.add(var) # Add the variable to our attention set

        ok_start = None
        ok_end = None
        waiting_to_write = {var for var in pay_attention if s_reads[var] != None} # Copy attention set and remove those who expect no writing

        if not waiting_to_write: # set ok_start if already empty
            ok_start = 0 # Insert after everything
        for i in range(len(stats)):
            (s, r, w) = stats[i]
            interference = w.intersection(pay_attention)
            # if any the var written by this statement is read by our inserted statement
            for inter in interference:
                if s_reads[inter] == s: # If this is the statement supposed to write it
                    waiting_to_write.remove(inter)
                elif inter not in waiting_to_write: # If we are overwriting an already written variable, we will never have the correct value back
                    ok_end = i
                    break # so give up
            if ok_start == None and not waiting_to_write:
                ok_start = i+1

        if ok_start == None: # Never a point after which we can insert
            return

        if ok_end == None: # Never had to stop so can insert up to the end
            ok_end = len(stats) # Last place we can insert

        # It won't break anything if for any variable we write:
        # There are no reads following the insertion point that depend on a write preceding it

        # Scan backwards through the statements to our insertion point
        # record each read, with statement it is reading from.
        # Assuming the list is already correct, the closest read after our write will be sufficient to check. If
        # a read happens after this, it must written in the same statement or one after the read, (i.e. after our insertion)

        for i in range(ok_start, ok_end+1): # +1 so last insertion point also assigned to i
        # i is places we insert stat, so before is 0->i (non-inclusive), after is i->len(stats)
        # Check insertion at each point in turn
            # Scan back
            post_read = {}
            for j in reversed(range(i, len(stats))):
                (s, r, w) = stats[j]
                post_read.update(r)
            # Retain only statement indices from variables that we write
            post_read = {post_read[k] for k in s_writes.intersection(post_read.keys())}

            # Scan forward from beginning checking for statements in post_read
            for j in range(i):
                (s, r, w) = stats[j]
                if s in post_read:
                    break
            else:
                # Only happens if the loop completed, if so we have a valid permutation!
                yield stats[:i] + [stat] + stats[i:]

    def _statement_tuple(self, s : "Index of the statement to convert",):
        """
        Create a tuple from a statement index.

        Contains (index, reads, writes). Reads and writes are sets of unique
        identifiers for the memory spaces that are accessed.

        """

        stat = self.statements[s]
        # Right now we only pay attention to locally read and written variables
        # So unique ids are just the names used
        r = read.ReadMarker(stat).get_mark()
        w = write.WriteMarker(stat).get_mark()
        return (s, r, w)

    def _statement_dependence(self,
                              t : "As returned by _statement_tuple",
                              before : "Slice of statement tuples before t"):
        """
        Returns a tuple similar to _statement_tuple but with indices where memory regions are written.

        This means we turn the read/write sets into a dict with memory regions as keys and indices where
        they were written last as values. None values will remain where the write does not exist.

        """

        t_stat, t_reads, t_writes = t
        reads = dict.fromkeys(t_reads)
        # reads will end up with non-None values as closest write to our statement
        for (b_stat, b_reads, b_writes) in before:
            # Look for common reads for us and writes for the other
            common = t_reads.intersection(b_writes)
            # dict with common read/write as keys and this statement as a value
            common_d = dict.fromkeys(common, b_stat)
            reads.update(common_d)

        return (t_stat, reads, t_writes)        

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
            if breaks.BreakMarker(self.statements[i]).canBreak():
                before = list(range(begin_partition, i))
                if before:
                    partitions.append(before)
                partitions.append([i])
                begin_partition = i+1

        before = list(range(begin_partition, len(self.statements)))
        if before:
            partitions.append(before)

        return partitions
