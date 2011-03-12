#!/usr/bin/env python3

from writer import sourcewriter
from writer import basicwriter
from writer import prettywriter
from util import pluginfinder

modules = [globals()[mod] for mod in globals() if not mod.startswith("__")]

import doctest

for mod in modules:
    print("Testing module: " + mod.__name__)
    doctest.testmod(mod)
