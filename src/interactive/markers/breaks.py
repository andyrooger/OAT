"""
Marker plugin for flow breaking statements.

"""

from analysis.markers import breaks
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Can this statement break from a linear flow?"""

    def parameters(self):
        return {
            "choices": ["yes", "no"]
        }

    def update(self, node, arg):
        try:
            br = {
                "yes": True,
                "no": False
            }[arg]
        except KeyError:
            return False # Unrecognised arg
        else:
            marker = breaks.BreakMarker(node)
            return marker.setBreaks(br)

    def show(self, node, title):
        marker = breaks.BreakMarker(node)

        if marker.is_marked():
            print(title + ("Yes" if marker.canBreak() else "No"))
