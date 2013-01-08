"""
Display a view of the selected node's markings.

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

import tkinter
from tkinter import ttk

class MarkPane(ttk.Frame):
    """Create pane to display a node's markings."""

    def __init__(self, parent, node):
        # Setup
        ttk.Frame.__init__(self, parent)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)

        self.node = node

        # Create content
        cats = self._marking_categories()
        depth = len(cats) if cats else 1
        ttk.Label(self, text="Markings").grid(
            column=0, row=0, rowspan=depth, stick="nsw")

        ttk.Separator(self, orient="vertical").grid(
            column=1, row=0, stick="ns", padx=5)

        if cats:
            self._create_categories(cats).grid(column=2, row=0, stick="nsew")
        else:
            ttk.Label(self, text="None").grid(column=2, row=0, stick="ns")

    # NO NO NO THIS IS ALL WRONG!
    # BAD ANDY! WHAT IF YOU EVER WANT TO CHANGE THE WORKINGS OF MARKINGS???
    # CHANGE ALL OF THIS!!!

    def _marking_categories(self):
        """Get possible categories for markings."""

        try:
            return set(self.node._markings.keys())
        except AttributeError:
            return None

    def _create_categories(self, categories):
        """Create and return the interface for the categories."""

        fr = ttk.Frame(self)
        fr.grid_columnconfigure(1, weight=1)


        fr.grid_rowconfigure(0, weight=1)
        ttk.Separator(fr, orient="horizontal").grid(
            column=0, row=0, columnspan=2, stick="sew", pady=5)

        i = 1
        for cat in categories:
            ttk.Label(fr, text=cat.title()).grid(
                column=0, row=i, stick="nsw")
            ttk.Label(fr, text=self._mark_text(cat), relief='sunken').grid(
                column=1, row=i, stick="nsew", padx=10)
            i += 1

        fr.grid_rowconfigure(i, weight=1)
        ttk.Separator(fr, orient="horizontal").grid(
            column=0, row=i, columnspan=2, stick="new", pady=5)

        return fr

    def _mark_text(self, category=None, marks=None):
        """Return the display text for a given category."""

        if category != None:
            marks = self.node._markings[category]

        if isinstance(marks, bool):
            return "Yes" if marks else "No"

        if isinstance(marks, tuple):
            if marks:
                return " : ".join([self._mark_text(marks=x) for x in marks])
            else:
                return "-"

        if isinstance(marks, set):
            if marks:
                return ", ".join([self._mark_text(marks=x) for x in marks])
            else:
                return "None"

        if isinstance(marks, dict):
            if marks:
                return ", ".join([
                    (self._mark_text(marks=k) +
                    " (" + self._mark_text(marks=marks[k]) + ")")
                    for k in marks
                ])
            else:
                return "None"

        return str(marks)
