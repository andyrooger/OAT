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

    def __init__(self, statements : "List of statements", safe : "Perform sanity checks for things that won't need them if this is coded correctly" = False):
        """Initialise reorderer or raise TypeError."""
        # Check type
        if not isinstance(statements, list):
            raise TypeError

        for stat in statements:
            if not isinstance(stat, ast.AST):
                raise TypeError

        self.statements = statements
        self.safe = safe

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
        dependence = [self._statement_dependence(tuples[i], tuples[:i], tuples[(i+1):]) for i in range(len(tuples))]

        # Grab the list of visible statements - saves some computation
        current = []
        rem = []
        for d in dependence:
            if visible.VisibleMarker(self.statements[d[0]]).isVisible():
                current.append(d)
            else:
                rem.append(d)

        for perm in self._insert_statements(rem, current):
            if self.safe and not self._check_perm(perm):
                print("Failed complete permutation check.")
            else:
                yield [s for (s, r, w) in perm]

    def _dry_run(self, perm : "Tuple statement list to run through", to_i=None, from_i=None, test=None, finaltest=None):
        """
        Run through a permutation keeping track of variables and checking at each parameter with test.

        test, if it is not None, should return True to keep testing or false to immediately fail.
        finaltest is similar.

        """

        if from_i == None:
            from_i = 0
        if to_i == None:
            to_i = len(perm)
        if test == None:
            test = (lambda state, s, r, w: True)

        # Run through each statement keeping state
        state = {}
        for i in range(len(perm)):
            (stat, reads, writes) = perm[i]
            if i >= from_i and i < to_i and not test(state, stat, reads, writes):
                return False
            state.update(dict.fromkeys(writes.keys(), stat))

        # Now check final vars
        return finaltest == None or finaltest(state)

    def _check_perm(self, perm : "Permuted tuple statement list"):
        """Check a permutation for validity. These should still be in tuple style."""

        # Get a list of all the statements currently in the perm
        stats = {s for (s, r, w) in perm}
        stats.add(None)

        if len(perm) + 1 != len(stats):
            print("Failed complete statement count.")

        def test(state, s, r, w):
            return all(state.get(var, None) == r[var] for var in r)

        def finaltest(state):
            # Now make sure all final vars are supposed to be that way
            for (stat, reads, writes) in perm:
                for w in writes:
                    if writes[w] != (state[w] == stat): # Discrepancy between final var in statement and not in perm
                        return False
            return True

        return self._dry_run(perm, test = test, finaltest = finaltest)

    def _check_incomplete_perm(self, perm : "Permuted tuple statement list"):
        """Check an incomplete permutation for validity. These should still be in tuple style."""

        # Get a list of all the statements currently in the perm
        stats = {s for (s, r, w) in perm}
        stats.add(None)

        if len(perm) + 1 != len(stats):
            print("Failed incomplete statement count.")
            return

        def test(state, s, r, w):
            return all(state.get(var, None) == r[var] for var in r if r[var] in stats)

        def finaltest(state):
            # Now make sure all final vars are supposed to be that way
            for (stat, reads, writes) in perm:
                for w in writes:
                    if writes[w] and (state[w] != stat): # Discrepancy between final var in statement and not in perm
                        return False
            return True

        return self._dry_run(perm, test = test, finaltest = finaltest)

    def _insert_statements(self, stats, current):
        """Find all the different ways the statements in stats can be inserted into current."""

        if not stats:
            yield current
            return

        for sub_perm in self._insert_statements(stats[1:], current):
            if self.safe and not self._check_incomplete_perm(sub_perm):
                print("Failed outer incomplete permutation check.")
            else:
                for perm in self._insert_statement(stats[0], sub_perm):
                    if self.safe and not self._check_incomplete_perm(perm):
                        print("Failed inner incomplete permutation check.")
                    else:
                        yield perm

    def _insert_statement(self, stat, stats):
        """Yields all the ways to insert the statement stat into stats."""

        (s_stat, s_reads, s_writes) = stat

        try:
            (ok_start, ok_end) = self._get_correct_state_range(s_reads, stats) # Period where our reads will receive correct values
        except TypeError: # Got None
            return

        if self.safe and not self._check_correct_state_range(s_reads, stats, ok_start, ok_end):
            print("Failed state range check.")
            return

        try:
            (pos_start, pos_end) = self._get_possible_insert_range(s_stat, s_writes, stats) # Period where anything that reads us can get to us
        except TypeError: # Got None
            return

        if self.safe and not self._check_insert_range(stats, stat, pos_start, pos_end):
            print("Failed insert range check.")
            return

        start = max(ok_start, pos_start)
        end = min(ok_end, pos_end)

        if start > end:
            return

        for i in range(start, end+1): # +1 so last insertion point also assigned to i
        # i is places we insert stat, so before is 0->i (non-inclusive), after is i->len(stats)
        # Check insertion at each point in turn

            cuts = self._cuts_read_write(i, set(s_writes.keys()), stats)
            if self.safe and not self._check_read_write_cuts(i, s_writes, stats, cuts):
                print("Failed cuts check.")
                return
            if not cuts:
                yield stats[:i] + [stat] + stats[i:]

    def _check_read_write_cuts(self, pos, writes, stats, ans : "Calculated answer from other func"):
        """Calculate _cuts_read_write without shortcuts to test."""

        # Wow long one now, calculate ALL read/write links between variables
        links = {} # var -> set((write, read)), read/write are indices where the variable is read and written

        state = {}
        for i in range(len(stats)):
            (s, r, w) = stats[i]
            for var in r: # All read variables
                if var not in links:
                    links[var] = set()
                reads_from = state.get(var, -1)
                from_stat = None if reads_from == -1 else stats[reads_from][0]
                if from_stat == r[var]: # Currently reading correctly
                    links[var].add((reads_from, i))
            state.update(dict.fromkeys(w.keys(), i)) # Use position in list rather than statement id
        for var in state:
            (from_s, from_r, from_w) = stats[state[var]]
            if var not in links:
                links[var] = set()
            if from_w[var]: # Really should be a final write
                links[var].add((state[var], len(stats)))

        # Keep all the links for variables we will write
        links = {v for var in links if var in writes for v in links[var]}

        # Now check none are broken
        broken = any(frm < pos and to >= pos for (frm, to) in links)
        return broken == ans

    def _cuts_read_write(self, pos : "Point to chop", writes : "Variables we write", stats : "List of statements"):
        """Check if inserting writes at pos will cut the link between any reads and writes."""

        # Find writes for variables we overwrite, we want to make sure these writes do not precede us
        # In a correct stats, we only need to check the closest following reads.
        # If a read happens after this, it must written in the same statement or one after the closest, (i.e. after our insertion)
        post_read = self._closest_reads(pos, writes, stats)

        if None in post_read:
            return True # broken link between pre-block write and a read

        # Check link between a real write and a post-block reads
        # Only happens if write before pos is a final write for variable we write
        for (s, r, w) in stats[:pos]:
            if any(w[var] for var in writes.intersection(w.keys())):
                return True

        # If we find a statement in post_read before pos then we have broken a link
        return bool(post_read.intersection({s for (s, r, w) in stats[:pos]}))


    def _closest_reads(self, pos : "Point to check from", ours : "Variables we write", stats : "List of statements"): 
        """
        Generate a dictionary of the closest reads of any variable that occur after pos, along with the statement indices they read from.

        Only entries for variables we write to are returned. Also it is only the statement indices we receieve.

        """

        post_read = {}
        for i in reversed(range(pos, len(stats))):
            (s, r, w) = stats[i]
            post_read.update(r)
        # Retain only statement indices from variables that we write
        return {post_read[var] for var in ours.intersection(post_read.keys())}

    def _get_relevant_read_vars(self, reads : "var -> statement", stats : "list of statements like from statement_dependence"):
        """
        Get a set of variables where the needed writes are in stats.

        For any statement in this set, we read in (according to reads), and the statement we expect to have written it exists in stats.
        Bear in mind that the statement we expect to have written it could be None - meaning it happened before we enter the block.

        """

        pay_attention = set()
        for var in reads: # Look through variables we read in the insertion statement
            if reads[var] == None or any(reads[var] == s for (s, r, w) in stats): # If the value we want is never written or written in stats
                pay_attention.add(var) # Add the variable to our attention set
        return pay_attention

    def _check_correct_state_range(self, reads, perm, start, end):
        """Check that any reads between start and end reads the correct values if they have been written."""

        # Get a list of all the statements currently in the perm
        stats = {s for (s, r, w) in perm}
        stats.add(None)

        def test(state, s, r, w):
            return all(state.get(var, None) == r[var] for var in r if r[var] in stats)

        return self._dry_run(perm, from_i = start, to_i = end+1, test = test) # Add 1 to end as it is inclusive, we expect exclusive


    def _get_correct_state_range(self,
                                 reads : "Set of vars we read and the statement we expect to read from",
                                 stats : "Set of statements we are inserting into"):
        """
        Get a range of indices where we could insert the statement that reads was generated from.

        This actually calculates the period in which all the writes we rely on have happened and have not been overwritten yet.

        The range is given from the first to the last possible index we could insert at, all-inclusive.
        Insert at i means stats = stats[:i] + [stat] + stats[i:]

        """

        # Find the variables where our expected write is somewhere in stats. (i.e. The ones we will pay attention to at this point)
        attention = self._get_relevant_read_vars(reads, stats)

        start = None
        end = None
        # Copy attention set and remove those who have been implicitly written before the block
        # These will be taken away each time we see the statement we want to write it
        waiting_to_write = {var for var in attention if reads[var] != None}

        # We can start inserting anywhere if everything already written
        if not waiting_to_write:
            start = 0

        # Check each statement
        for i in range(len(stats)):
            (s, r, w) = stats[i]
            # Take the writes at statement i which we are paying attention to
            interference = attention.intersection(w.keys())
            for inter in interference:
                if reads[inter] == s: # If this is the statement expected to write it
                    waiting_to_write.remove(inter)
                elif inter not in waiting_to_write: # If we are overwriting an already written variable, we have missed our chance
                    end = i
                    break # so give up, doesn't matter about start as it would be after end
            # Check if this is the first statement where we have been ready to start
            if start == None and not waiting_to_write:
                start = i+1

        if start == None:
            return None

        if end == None:
            end = len(stats) # after the last statement

        if start > end:
            return None

        return (start, end)

    def _get_relevant_written_vars(self,
                                   stat : "Current statment",
                                   writes : "List of variables that statement writes to and whether they are the final write",
                                   stats : "list of statements like from statement_dependence"):
        """Get a dict of variables which are read from statement stat with values as the first point they are read from stat."""

        pay_attention = dict.fromkeys({w for w in writes if writes[w]}) # All final writes
        # Look through statements for reads of this statement
        for i in reversed(range(len(stats))):
            (c_s, c_r, c_v) = stats[i]
            for r in c_r:
                if c_r[r] == stat:
                    pay_attention[r] = i
        return pay_attention

    def _check_insert_range(self, perm, stat, start, end):
        """For each index we could insert, check anything reading our statement finds it."""

        (s_s, s_r, s_w) = stat

        def test(state, s, r, w):
            if s_s in r.values(): # If this node reads from our new statement
                reads_from_us = {var for var in r if r[var] == s_s} # variables read from us
                return all(state.get(var, None) == s_s for var in reads_from_us) # For any read variable expecting to read from us, check that it is doing so
            else:
                return True

        for i in range(start, end+1):
            if not self._dry_run(perm[:i] + [stat] + perm[i:], test = test):
                return False
        return True

    def _get_possible_insert_range(self,
                                   stat : "The current statement number",
                                   writes : "Set of vars we write to and whether it is the last write of this variable.",
                                   stats : "Set of statements we are inserting into"):
        """
        Get a range of indices where we could insert the statement that reads and attention were generated from.

        This actually calculates the period in which we could insert the statement and have all reads that rely on us actually read from us.

        The range is given from the first to the last possible index we could insert at, all-inclusive.
        Insert at i means stats = stats[:i] + [stat] + stats[i:]

        """

        # PLAN -
        # - Find first statement to read something from us, we must be behind this
        # - Proceed forward from this, keeping track of any variables written. If a statement tries to read ours and it's been written since, die.
        # - Proceed backward from this until a variable we write is overwritten, we have to start after this

        # Find the variables that actually get read from us
        attention = self._get_relevant_written_vars(stat, writes, stats)

        try:
            end = min((attention[k] if attention[k] != None else len(stats)) for k in attention)
        except ValueError: # Attention empty
            end = len(stats)

        # Iterate forward
        overwritten_vars = set()
        for (s, r, w) in stats[end:]: # scan from the first point after our last insertion point to end
            # statement reads our var?
            for var in overwritten_vars.intersection(r.keys()):
                if r[var] == stat:
                    return None # Can insert nowhere
            # statement writes our var
            overwritten_vars.update(w.keys())

        # Check final writes
        if overwritten_vars.intersection(var for var in writes if writes[var]):
            return None

        # Now backward for the next written var, only stop if we get to a var that is actually read
        start = None
        for i in reversed(range(end)): # Just before end and backwards
            (s, r, w) = stats[i]
            if set(attention.keys()).intersection(w.keys()):
                start = i+1
                break

        if start == None:
            start = 0

        return (start, end)


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
                              before : "Slice of statement tuples before t",
                              after : "Slice of statement tuples after t"):
        """
        Returns a tuple similar to _statement_tuple but with indices where memory regions are written.

        This means we turn the read sets into a dict with memory regions as keys and indices where
        they were written last as values. None values will remain where the write does not exist.
        Write set becomes set with true of false indicating if they are the last write of the variable.

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

        writes = dict.fromkeys(t_writes, True)
        for (a_stat, a_reads, a_writes) in after:
            common = t_writes.intersection(a_writes)
            common_d = dict.fromkeys(common, False)
            writes.update(common_d)

        return (t_stat, reads, writes)        

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
