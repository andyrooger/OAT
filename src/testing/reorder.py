"""
Tools for performance analysis on statement reordering.

"""

import random
import ast
from analysis.customast import CustomAST
from analysis.markers.breaks import BreakMarker
from analysis.markers.visible import VisibleMarker
from analysis.markers.read import ReadMarker
from analysis.markers.write import WriteMarker

def create_statements(size, visible=0.1, breaking=0.1, reads={"a", "b", "c"}, writes={"a", "b", "c"}, rprob=1, wprob=1):
    # prob that at least 1 is read = 1 - prob that none get read = 1 - (1-prob1)(1-prob2)(1-prob3)
    # rprob = probability that at least one is read, convert to the probability each has
    rprob = 1 - ((1 - rprob) ** (1.0 / len(reads)))
    wprob = 1 - ((1 - wprob) ** (1.0 / len(writes)))

    statements = []
    while size > 0:
        vi = random.random() < visible
        br = random.random() < breaking

        label = str(size)
        if vi:
            label += " Visible"
        if br:
            label += " Breaks"

        statement = CustomAST(ast.Expr(ast.Str(label)))
        if vi:
            VisibleMarker(statement).setVisible(True)
        if br:
            BreakMarker(statement).addBreak("return")

        statements = [statement] + statements
        size -= 1
    return CustomAST(statements)
