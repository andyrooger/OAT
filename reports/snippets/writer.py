"""
I am an example file!

And this is also a multi-line docstring.

"""

try:
    from space import aliens
except ImportError as e:
    pass #print(e)


def a_function(arg1, arg2=None):
    """I am a function."""

    print("I don't really do anything")
    return arg1

class other_class(a_class):
    """I'm empty too"""
