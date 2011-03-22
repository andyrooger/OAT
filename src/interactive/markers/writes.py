"""
Marker plugin for written variables.

Shares almost everything with writes.

"""

from . import reads
from analysis.markers import write

class Marker(reads.Marker):
    """Choose all the variables this node writes. Use a(g|n|l|u)-variable to add or r-variable to remove a global, nonlocal, local, or unknown variable."""

    def _get_marker(self, node):
        """Get the marker for this type of mark."""
        return write.WriteMarker(node)

    def _get_dict(self, marker):
        return marker.writes()
