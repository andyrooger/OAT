"""
Searches a module for plugins.

"""

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
