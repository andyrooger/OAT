"""
Just lots of stuff to try and print.

"""

import sys
from os import path
import ast

a = 42

def func(a, b, c=1, d=[], *e, f=6, g=" ", **h):
    print(a + "hello")
    pass

class myclass: pass

class otherclass(myclass):
    """
    Class docstring

    """

    def __init__(self, initparam):
        """Another one!"""

        self.a = "lalala"


    def f(self, a=1, b : "I have no purpose" = 2):
        a = [1, 2, 3, 4]
