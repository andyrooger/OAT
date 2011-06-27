"""
Contains valuers for the reorderer.

"""

import random
import math

from .markers import read
from .markers import write

def InvertValuer(valuer):
    """Return an inverted version of another valuer."""

    def inv(*varargs, **kwargs):
        return -valuer(*varargs, **kwargs)

    return inv

def RandomValuer(statements):
    """Give a random value, no matter the permutation."""

    return random.uniform(0, 100)

def FirstValuer(statements):
    """Give exactly the same value, no matter the permutation."""

    return 1

def WriteRangeValuer(statements):
    """Gives the sum of spread of written variables."""

    variables = {}
    # Collect ranges for all variables
    for i, s in enumerate(statements):
        stat = statements[s]
        written = write.WriteMarker(stat).get_mark()
        for w in written:
            try:
                (start, end) = variables[w]
            except KeyError:
                variables[w] = (i, i)
            else:
                variables[w] = (start, i)
    # Sum ranges (we want smallest range and valuer rates high for good)
    # (... also we don't have a limit to values output)
    return -sum(e - s for (s, e) in variables.values())

def WriteUseValuer(statements):
    """Encourages smaller distance between the write of a variable and the furthest read of that write."""

    total = 0
    variables = {} # Where written
    # Collect ranges for all variables
    for i, s in enumerate(statements):
        stat = statements[s]
        reads = read.ReadMarker(stat).get_mark()
        written = write.WriteMarker(stat).get_mark()
        for var in reads:
            try:
                (w, r) = variables[var]
            except KeyError:
                variables[var] = (-1, i) # Assume written before statements begin
            else:
                variables[var] = (w, i)
        for var in written:
            try:
                (w, r) = variables[var] # Try getting written and furthest read
            except KeyError:
                pass
            else:
                total += r - w # Add range to sum and replace write location
            # Now replace write location
            variables[var] = (i, i) # Really no reads but i is safe as adds value 0
    # Now all left in variables are furthest reads
    for (w, r) in variables.values():
        total += r - w
    return -total # Flip so smaller distance is better

def WriteUseLogValuer(statements):
    """Encourages smaller distance between the write of a variable and the furthest read of that write."""

    total = 0
    variables = {} # Where written
    # Collect ranges for all variables
    for i, s in enumerate(statements):
        stat = statements[s]
        reads = read.ReadMarker(stat).get_mark()
        written = write.WriteMarker(stat).get_mark()
        for var in reads:
            try:
                (w, r) = variables[var]
            except KeyError:
                variables[var] = (-1, i) # Assume written before statements begin
            else:
                variables[var] = (w, i)
        for var in written:
            try:
                (w, r) = variables[var] # Try getting written and furthest read
            except KeyError:
                pass
            else:
                if r-w > 0:
                    total += math.log(r - w) # Add range to sum and replace write location
            # Now replace write location
            variables[var] = (i, i) # Really no reads but i is safe as adds value 0
    # Now all left in variables are furthest reads
    for (w, r) in variables.values():
        if r-w > 0:
            total += math.log(r - w)
    return -total # Flip so smaller distance is better


def KnotValuer(statements):
    """Encourages concentration on one variable at a time."""

    providers = self._generate_providing_statements(statements)

    knots = 0
    links = []

    # Move back through statements recording links as we go
    for i, s in reversed(enumerate(statements)):
        stat = statements[s]
        # Tick off current links
        while i in links:
            knots += links.index(i)
            links.remove(i)
        ps = [p for p in providers[i]]
        ps.sort() # ascending
        for p in ps:
            links.insert(0, p) # inserted at beginning decending

    return -knots

def _generate_providing_statements(statements):
    """Generate a dictionary for each statement containing providing statements."""

    variables = {} # Where written
    providers = []
    for i, s in enumerate(statements):
        stat = statements[s]
        provided = set()
        reads = read.ReadMarker(stat).get_mark()
        written = write.WriteMarker(stat).get_mark()
        for var in reads:
            provided.add(variables.get(var, None))
        for var in written:
            variables[var] = i
        providers.append(provided)
    return providers
    

# Try all write-based valuers with read
# Dist to only nearest write?
