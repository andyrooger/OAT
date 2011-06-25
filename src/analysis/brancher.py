"""
Tools to allow branching sections of the source code.

"""

class Brancher:
    """Holds information used to perform a particular type of branching."""

    def __init__(self, name):
        self._name = name
        self.predicates = None
        self.exceptions = None
        self.initial = None
        self.preserving = None
        self.destroying = None
        self.randomising = None

    def if_branch(self, statements, start, end):
        pass

    def ifelse_branch(self, statements, start, end):
        pass

    def except_branch(self, statements, start, end):
        pass

    def while_branch(self, statements, start, end):
        pass

