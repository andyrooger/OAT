"""
Marker plugin for visibility.

"""

# OAT - Obfuscation and Analysis Tool
# Copyright (C) 2011  Andy Gurden
# 
#     This file is part of OAT.
# 
#     OAT is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     OAT is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with OAT.  If not, see <http://www.gnu.org/licenses/>.

from analysis.markers import visible
from .. import markcmd

class Marker(markcmd.AbstractMarker):
    """Is this a visible or invisible statement? (i.e. does it perform actions visible to the outside world?"""

    def parameters(self):
        return {
            "choices": ["yes", "no"]
        }

    def translate(self, node, arg):
        try:
            vis = {
                "yes": True,
                "no": False
            }[arg]
        except KeyError:
            return visible # Unrecognised arg
        else:
            marker = visible.VisibleMarker(node)
            marker.detach()
            marker.setVisible(vis)
            return marker.get_mark()

    def update(self, node, trans):
        visible.VisibleMarker(node).set_mark(trans)

    def show(self, node, title):
        marker = visible.VisibleMarker(node)

        if marker.is_marked():
            print(title + ("Yes" if marker.isVisible() else "No"))
