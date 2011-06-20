"""
Tools for performance analysis on statement reordering.

"""

import multiprocessing
import timeit

import random
import ast
from analysis.reorder import Reorderer, RandomReorderer

from analysis.customast import CustomAST
from analysis.markers.breaks import BreakMarker
from analysis.markers.visible import VisibleMarker
from analysis.markers.read import ReadMarker
from analysis.markers.write import WriteMarker

def create_statements(size, visible=0.1, breaking=0.1, reads={"a", "b", "c"}, writes={"a", "b", "c"}, rprob=0.1, wprob=0.1):
    # prob that at least 1 is read = 1 - prob that none get read = 1 - (1-prob1)(1-prob2)(1-prob3)
    # rprob = probability that at least one is read, convert to the probability each has
    rprob = 1 - ((1 - rprob) ** (1.0 / len(reads)))
    wprob = 1 - ((1 - wprob) ** (1.0 / len(writes)))

    statements = []
    while size > 0:
        vi = random.random() < visible
        br = random.random() < breaking
        r = {x : (random.random() < rprob) for x in reads}
        w = {x : (random.random() < wprob) for x in writes}

        label = str(size)
        if vi:
            label += " Visible"
        if br:
            label += " Breaks"
        if r:
            label += " reads{" + ", ".join(x for x in r if r[x]) + "}"
        if w:
            label += " writes{" + ", ".join(x for x in w if w[x]) + "}"

        statement = CustomAST(ast.Expr(ast.Str(label)))
        VisibleMarker(statement).set_mark(False)
        BreakMarker(statement).set_mark(set())
        ReadMarker(statement).set_mark(set())
        WriteMarker(statement).set_mark(set())
        if vi:
            VisibleMarker(statement).setVisible(True)
        if br:
            BreakMarker(statement).addBreak("return")
        for x in r:
            if r[x]:
                ReadMarker(statement).addVariable(x)
        for x in w:
            if w[x]:
                WriteMarker(statement).addVariable(x)

        statements = [statement] + statements
        size -= 1
    return CustomAST(statements)


def timed_reorder(statements, timeout=10, rand=False, valuer=None):
    """Calculate all reorderings and record time to maximum of timeout."""

    R = RandomReorderer if rand else Reorderer

    q = multiprocessing.Queue()

    if valuer is None:
        def counter():
            """Count all reorderings and return on queue."""
            x = sum(1 for x in R(statements, safe=False, precond=False).permutations()) # limit = None
            q.put(x)
    else:
        def counter():
            """Value reorderings with valuer and return on queue."""
            x = R(statements, safe=False, precond=False).best_permutation(valuer)
            q.put(x)

    proc = multiprocessing.Process(target=counter)

    def spawn():
        """Create new process that times out at timeout to generate all reorderings."""
        proc.start()
        proc.join(timeout)
        proc.terminate()

    time = timeit.Timer(stmt=spawn, setup='gc.enable()').timeit(1)

    if q.empty():
        return None
    else:
        return (time, q.get()) 
