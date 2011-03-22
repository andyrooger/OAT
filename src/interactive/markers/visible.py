"""
Marker plugin for visibility.

"""

from analysis.markers import visible
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Is this a visible or invisible statement? (i.e. does it perform actions visible to the outside world?"""

    def parameters(self):
        return {
            "choices": ["yes", "no"]
        }

    def update(self, node, arg):
        try:
            vis = {
                "yes": True,
                "no": False
            }[arg]
        except KeyError:
            return False # Unrecognised arg
        else:
            marker = visible.VisibleMarker(node)
            return marker.setVisible(vis)

    def show(self, node, title):
        marker = visible.VisibleMarker(node)

        if marker.is_marked():
            print(title + ("Yes" if marker.isVisible() else "No"))
