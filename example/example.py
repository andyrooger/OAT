"""
I am an example file!

"""

try:
    from wikipedia import myreport
except ImportError as e:
    pass #print(e)


def a_function(arg1, arg2=None):
    """I am a function."""

    print("I don't really do anything")
    return arg1

@a_function
class a_class:
    pass

class other_class(a_class):
    """I'm empty too"""
