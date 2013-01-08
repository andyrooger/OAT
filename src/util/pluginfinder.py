"""
Searches a module for plugins.

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

import os
import os.path
import importlib

class PluginFinder:
    """
    Sits over a module to look for all modules it contains.

    >>> import interactive
    >>> finder = PluginFinder(interactive)
    >>> plugins = finder.getPlugins()

    """

    def __init__(self,
                 module : "Module to lie over",
                 load : "Load plugins immediately" = False):
        self._module = module
        self.plugins = None
        if load:
            self.load()

    def load(self):
        """
        Load all plugins if they are not already loaded.

        Can throw IOError exception if there is a problem reading the directory.

        """

        if self.plugins != None:
            return

        mod_names = set()

        for path in self._module.__path__:
            if os.path.isdir(path):
                mod_files = os.listdir(path)
                for file in mod_files:
                    if file.endswith(".py") and file != "__init__.py":
                        mod_names.add(file[:-3])

        
        self.plugins = set()

        for mod in mod_names:
            m = importlib.import_module("."+mod, self._module.__name__)
            self.plugins.add(m)

        self.plugins = frozenset(self.plugins) # immutable now

    def getPlugins(self):
        """Get the set of plugins."""

        self.load()
        return self.plugins
