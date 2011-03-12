"""
Marker plugin for flow breaking statements.

"""

from analysis.markers import breaks
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """How can this statement break from a linear flow? 'clear' clears the following type."""

    def parameters(self):
        return {
            "nargs": "+",
            "choices": ["except", "return", "break", "continue", "yield", "clear"],
            "metavar": "TYPE"
        }

    def translate(self, node, arg):
        success = False
        clear = False

        marker = breaks.BreakMarker(node)
        marker.detach()

        for change in arg:
            if change == "clear":
                clear = True
                continue
            if clear:
                success = marker.removeBreak(change) or success
                clear = False
            else:
                success = marker.addBreak(change) or success

        return marker.get_mark()

    def update(self, node, trans):
        return breaks.BreakMarker(node).set_mark(trans)

    def show(self, node, title):
        marker = breaks.BreakMarker(node)

        if marker.is_marked():
            print(title, end="")
            if marker.canBreak():
                breakers = list(marker.get_mark())
                print("Yes (" + ", ".join(breakers) + ")")
            else:
                print("No")
