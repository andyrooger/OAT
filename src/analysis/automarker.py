"""
Contains code for auto-marking AST nodes.

"""

import ast

import analysis.markers.breaks
import analysis.markers.visible
import analysis.markers.read
import analysis.markers.write
import analysis.markers.indirectrw

class AutoMarker:
    """Tries to find correct markings for each node."""

    def __init__(self,
                 res_order : "The resolution order for calculating markings.",
                 mark : "Should we mark the nodes as we work?" = True,
                 user : "Function to allow users to manually select markings." = (lambda node, needed: {}),
                 review : "Function to review mark choices." = (lambda n, m: True),
                 defaults : "Dictionary of functions to get defaults for each marking." = {}):
        order_allowed = set(["mark", "calc", "user"])

        for res in res_order:
            try:
                order_allowed.remove(res)
            except KeyError:
                raise ValueError("Method " + res + " is invalid or specified too many times.")

        self.user_marks = user
        self.res_order = res_order
        self.mark = mark
        self.review = review
        self.defaults = defaults

        if "visible" not in self.defaults:
            self.defaults["visible"] = (lambda: analysis.markers.visible.VisibleMarker().duplicate())
        if "breaks" not in self.defaults:
            self.defaults["breaks"] = (lambda: analysis.markers.breaks.BreakMarker().duplicate())
        if "reads" not in self.defaults:
            self.defaults["reads"] = (lambda: analysis.markers.read.ReadMarker().duplicate())
        if "writes" not in self.defaults:
            self.defaults["writes"] = (lambda: analysis.markers.write.WriteMarker().duplicate())
        if "indirectrw" not in self.defaults:
            self.defaults["indirectrw"] = (lambda: analysis.markers.indirectrw.IndirectRWMarker().duplicate())

########################################################
# Resolution functions                                 #
# - Return full dicts with everything we ask for       #
# - Can throw UserStop to finish part way through      #
# - Use functions in next section to resolve           #
# - Should never alter return value from resolve_marks #
########################################################

    def resolve_marks(self, node, needed : "Set containing the markings we want." = {"visible", "breaks", "reads", "writes", "indirectrw"}):
        """Resolve markings for a given node based on the given resolution order. Can throw UserStop"""

        result = {}
        wanted = needed.copy()

        for res in self.res_order + ["default"]:
            wanted.difference_update(result) # Remove those markings we have

            if not wanted: # done
                break

            remainder = {
                "mark": self.get_marks,
                "calc": self.calculate_marks,
                "user": self.user_marks,
                "default": self.default_marks
            }[res](node, wanted)
            result.update(remainder) # should only contain as yet unmarked values

        if not self.review(node, result):
            raise UserStop

        if self.mark:
            if "visible" in needed:
                analysis.markers.visible.VisibleMarker(node).set_mark(result["visible"])
            if "breaks" in needed:
                analysis.markers.breaks.BreakMarker(node).set_mark(result["breaks"])
            if "reads" in needed:
                analysis.markers.read.ReadMarker(node).set_mark(result["reads"])
            if "writes" in needed:
                analysis.markers.write.WriteMarker(node).set_mark(result["writes"])
            if "indirectrw" in needed:
                analysis.markers.indirectrw.IndirectRWMarker(node).set_mark(result["indirectrw"])

        return result

    def resolve_group(self, nodes, needed):
        """Resolve each of the nodes in the set. Avoids pretending they are a new node."""

        result = self._base_marks(needed)
        for node in nodes:
            n_marks = self.resolve_marks(node, needed)
            self._combine_marks(result, n_marks, needed)
        return result

    def _base_marks(self, needed):
        """Get a new dictionary containing the markings for an empty list of nodes."""

        full_defs = {
            "visible": False,
            "breaks": set(),
            "reads": set(),
            "writes": set(),
            "indirectrw": {}
        }

        try:
            return {m: full_defs[m] for m in needed}
        except KeyError:
            raise ValueError("Unknown marking type")

    def _combine_marks(self, marks, addition, needed):
        """Modify marks to account for having also performed an execution resulting with the marks in addition."""

        for n in needed:
            if n == "visible":
                marks["visible"] |= addition["visible"]
            elif n == "breaks":
                marks["breaks"].update(addition["breaks"])
            elif n == "reads":
                marks["reads"].update(addition["reads"])
            elif n == "writes":
                marks["writes"].update(addition["writes"])
            elif n == "indirectrw":
                for ns in addition["indirectrw"]:
                    nr, nw = marks["indirectrw"].get(ns, (False, False))
                    r, w = addition["indirectrw"][ns]
                    marks["indirectrw"][ns] = (nr or r, nw or w)
        return marks

#########################################
# Resolution Methods                    #
# - Resolve markings in a specific way  #
# - Don't return entries we do not know #
#########################################

    def get_marks(self, node, needed):
        """Get the current markings for the node if they exist, or None."""

        types = {
            "visible": analysis.markers.visible.VisibleMarker,
            "breaks": analysis.markers.breaks.BreakMarker,
            "reads": analysis.markers.read.ReadMarker,
            "writes": analysis.markers.write.WriteMarker,
            "indirectrw": analysis.markers.indirectrw.IndirectRWMarker,
        }

        result = {}
        for n in needed:
            marker = types[n](node)
            if marker.is_marked():
                result[n] = marker.get_mark()

        return result

    # Defined in the __init__
    # def user_marks(self, node, needed):

    def default_marks(self, node, needed):
        """Get the default values for markings on the current node."""

        return {n: self.defaults[n]() for n in needed}

    def calculate_marks(self, node, needed):
        """Calculate markings for the given mark types on node."""

        needed = needed.copy()
        needed.discard("reads")
        needed.discard("writes")
        needed.discard("indirectrw")

        try:
            desc = MARK_CALCULATION[node.type()]
        except KeyError:
            return {}
        else:
            return self._run_task_description(desc, node, needed)

    def _run_task_description(self, desc, node, needed):
        """Run the given task description on the node to generate a set of markings."""

        if isinstance(desc, dict):
            return self._desc_dict(desc, node, needed)
        elif hasattr(desc, "__call__"):
            return self._run_task_description(desc(node), node, needed)
        elif isinstance(desc, list):
            return self._combine_sequence((self._run_task_description(d) for d in desc), needed)
        elif isinstance(desc, set):
            return self._combine_all((self._run_task_description(d) for d in desc), needed)
        elif isinstance(desc, tuple):
            return self._combine_any((self._run_task_description(d) for d in desc), needed)
        else:
            return {} # Received an invalid task description

    def _combine_any(self, marks, needed):
        """Combine each of the given marks assuming we could choose any one of them."""

        # TODO: Correct this!
        combined = self._base_marks(needed)
        for m in marks:
            self._combine_marks(combined, m, needed)
        return combined

    def _combine_sequence(self, marks, needed):
        """Combine each of the given marks in sequence."""

        combined = self._base_marks(needed)
        for m in marks:
            self._combine_marks(combined, m, needed)
        return combined

    def _combine_all(self, marks, needed):
        """Combine each of the given marks assuming we are choosing all of them. The sets of marks should not overlap."""

        combined = {}
        for m in marks:
            if set(combined).intersection(set(m)): # Overlap = fail
                return {}
            combined.update(m)
        return combined

    def _desc_dict(self, desc, node, needed):
        """Run a dictionary task description."""

        if "transform" in desc:
            new_node = desc["transform"](node)
            if new_node != None:
                return self.resolve_marks(new_node, needed)

        if "known" in desc and "unknown" in desc:
            if desc["known"].intersect(desc["unknown"]):
                return {} # Overlap invalid

        if "known" in desc:
            needed = needed.intersection(desc["known"])
        if "unknown" in desc:
            needed = needed.difference(desc["unknown"])

        marks = self._base_marks(needed)

        if "combine" in desc:
            for field in [f for f in desc["combine"] if f in node]: # Keeps order
                child = self.resolve_marks(node[field], needed)
                self._combine_marks(marks, child)

        # Marking type specific
        if "breaks" in needed:
            if "rem_breaks" in desc:
                marks["breaks"].difference_update(desc["rem_breaks"])
            if "add_breaks" in desc:
                marks["breaks"].update(desc["add_breaks"])

        return marks

################################################
# Helping functions for auto-mark calculation. #
################################################

def _trans_func_decorators(node):
    """
    Convert a func with decorators into its equivalent code, i.e.

    @dec1
    @dec2
    def f(): pass

    -->

    def f(): pass
    f = dec2(dec1(f))

    """

    if node["decorator_list"].is_empty():
        return None

    func = CustomAST(ast.FunctionDef(
               node["name"],
               node["args"],
               node["body"],
               [],
               node["returns"]
    ))
    assname = CustomAST(ast.Name(node["name"], ast.Store()))
    calls = CustomAST(ast.Name(node["name"], ast.Load()))
    dlist = node["decorator_list"]
    for dec in reversed(dlist):
        calls = ast.Call(dlist[dec], [calls], [], None, None)
        calls = CustomAST(calls)
    return CustomAST([func, ast.Assign([assname], calls)])

def _trans_class_decorators(node):
    """
    Convert a class with decorators into its equivalent code, i.e.

    @dec1
    @dec2
    class C: pass

    -->

    class C: pass
    C = dec2(dec1(C))

    """

    if node["decorator_list"].is_empty(): # Translate for decorators
        return None

    cls = CustomAST(ast.ClassDef(
        node["name"],
        node["bases"],
        node["keywords"],
        node["starargs"],
        node["kwargs"],
        []
    ))
    assname = CustomAST(ast.Name(node["name"], ast.Store()))
    calls = CustomAST(ast.Name(node["name"], ast.Load()))
    dlist = node["decorator_list"]
    for dec in reversed(dlist):
        calls = CustomAST(ast.Call(dlist[dec], [calls], [], None, None))
    return CustomAST([cls, ast.Assign([assname], calls)])


def _trans_aug_assign(node):
    """Convert an augmented assign into a normal assignment of the operation to the target."""

    calc = CustomAST(ast.BinOp( # Transform to a binary op
        node["target"],
        node["op"],
        node["value"]
    ))
    return CustomAST(ast.Assign([node["target"]], calc))

def _try_except_dict(node):
    # visible/break same as running body, running handlers, running else
    # Will not catch anything unless the handler is straight except:
    # This is because it is hard to match type for a name

    d = {"local": {"body"}}

    for h in node["handlers"]:
        if node["handlers"][h]["type"].is_empty():
            d["rem_break"] = {"except"}
            break

    return [d, {"localg": {"handlers"}, "local": {"orelse"}}]

def _unpack_dict(self, node, needed):
    # Normal ctx stuff plus think about unpacking
    d = {"localg": {"elts"}, "local": {"ctx"}}
    if node["ctx"].type() == "Store":
        d["add_break"] = {"except"}
    return d

###################################
# Actual mark calculation methods #
###################################

MARK_CALCULATION = {
    "Module": {"local": {"body"}},
    "Interactive": {"local": {"body"}},
    "Expression": {"local": {"body"}},
    "Suite": {"local": {"body"}},

    # stmt
    "FunctionDef": {"transform": _trans_func_decorators, "local": {"returns", "args"}},
    "ClassDef": {"transform": _trans_class_decorators, "local": {"body", "starargs", "kwargs"}, "localg": {"bases", "keywords"}}, # Evaluates body as annotations
    "Return": {"local": {"value"}, "add_break": {"return"}},

    "Delete": {"localg": {"targets"}}, # NameError covered in ctx
    "Assign": {"localg": {"targets"}, "local": {"value"}},
    "AugAssign": {"transform": _trans_aug_assign},

    "For": [{"local": {"body"}, "rem_break": {"break", "continue"}}, {"local": {"iter", "orelse"}, "add_break": {"except"}}],
    "While": [{"local": {"body"}, "rem_break": {"break", "continue"}}, {"local": {"test", "orelse"}}],
    "If": {"local": {"test", "body", "orelse"}},

    # TODO - think about calls made, should be:
    # Evaluate node.context_expr for now I call this e
    # evaluate e.__enter__() - assign this value to name after 'as' if given
    # try:
    #     Execute node.body
    # except Exception as ex:
    #     if e.__exit__(details of ex) == False: raise ex
    # else:
    #     e.__exit__(None, None, None)
    #
    # We could assume same as evaluating ctx expression and executing body
    # but we will be safe
    "With": {"known": {}},

    "Raise": {"local": {"exc", "cause"}, "add_break": {"except"}}, # Same as evaluating the exceptions and raising
    "TryExcept": _try_except_dict,
    "TryFinally": {"local": {"body", "finalbody"}}, # Same as running both try and finally body
    "Assert": {"local": {"test", "msg"}, "add_break": {"except"}}, # Eval test and msg, raise exception

    "Import": {"known": set()}, # Can do anything we could import! # TODO - Check imported module?
    "ImportFrom": {"known": set()}, # Again we have no idea! # TODO - Check imported module?

    "Global": {}, # Any exceptions are thrown at parsing. Not runtime.
    "Nonlocal": {}, # Any exceptions are thrown at parsing. Not runtime.
    "Expr": {"local": {"value"}},
    "Pass": {},
    "Break": {"add_break": {"break"}},
    "Continue": {"add_break": {"continue"}},

    # expr
    "BoolOp": {"localg": {"values"}}, # Don't see that boolop can throw exceptions, it doesn't care about type etc
    "BinOp": {"local": {"left", "right"}, "add_break": {"except"}}, # As above with extra exception
    "UnaryOp": {"local": {"operand"}, "add_break": {"except"}},
    "Lambda": {"local": {"args"}}, # Doesn't run it, just defines it. Eval args.
    "IfExp": {"local": {"test", "body", "orelse"}},
    "Dict": {"localg": {"keys", "values"}},
    "Set": {"localg": {"elts"}},
    "ListComp": {"local": {"elt"}, "localg": {"generators"}},
    "SetComp": {"local": {"elt"}, "localg": {"generators"}},
    "DictComp": {"local": {"key", "value"}, "localg": {"generators"}},

    # Turns from: (node.elt, node.generators)
    #              where generators are for x1 in g1 if b1 for x2 in g2 if b2 ...
    # To:
    # def __gen(exp):
    #     for x1 in exp:
    #         if b1:
    #             for x2 in g2:
    #                 if b2:
    #                     yield node.elt - (expression possibly uses x1, x2)
    # g = __gen(iter(g1))
    # del __gen
    # Too difficult, say we don't know
    # TODO - check we do not have similar problems for list/set/dict comp
    "GeneratorExp": {"known": set()},

    # PEP 0342 describes yield expression.
    # Not mentioned to be accepted but experimentation tells me it probably was.
    "Yield": {"local": {"value"}, "add_break": {"except", "yield"}},

    "Compare": {"local": {"left"}, "localg": {"comparators"}, "add_break": {"except"}},
    "Call": {"known": set()}, # No idea what we'd be calling # TODO - think harder
    "Num": {},
    "Str": {},
    "Bytes": {},
    "Ellipsis": {},

    # Eval node.value
    # Now we treat like a search for a simple name in node.value
    # TODO - store and denied?
    "Attribute": {"local": {"value", "ctx"}},

    # Similar to above
    # TODO - store and denied?
    "Subscript": {"local": {"value", "slice", "ctx"}},

    "Starred": {"local": {"value", "ctx"}},
    "Name": {"local": {"ctx"}},
    "List": _unpack_dict,
    "Tuple": _unpack_dict,

    # expr_context
    "Load": {"add_break": {"except"}}, # if not found
    "Store": {}, # TODO - think about storing to a class and being denied
    "Del": {"add_break": {"except"}}, # if not found
    "AugLoad": {"known": set()}, # Don't appear to be used, so don't know
    "AugStore": {"known": set()}, # Don't appear to be used, so don't know
    "Param": {"known": set()}, # Apparently used by a in 'def f(a): pass', seems to not be though

    # slice
    "Slice": {"local": {"lower", "upper", "step"}},
    "ExtSlice": {"local": {"dims"}},
    "Index": {"local": {"value"}},

# These binary operators are not currently used by me
#  - the boolop or binop nodes already covered it
#  - TODO - Sort this out, maybe?

    # boolop
    "And": None,
    "Or": None,

    # operator
    "Add": None,
    "Sub": None,
    "Mult": None,
    "Div": None,
    "Mod": None,
    "Pow": None,
    "LShift": None,
    "RShift": None,
    "BitOr": None,
    "BitXor": None,
    "BitAnd": None,
    "FloorDiv": None,

# Same with unary and comparisons

    # unaryop
    "Invert": None,
    "Not": None,
    "UAdd": None,
    "USub": None,

    # cmpop
    "Eq": None,
    "NotEq": None,
    "Lt": None,
    "LtE": None,
    "Gt": None,
    "GtE": None,
    "Is": None,
    "IsNot": None,
    "In": None,
    "NotIn": None,

    # comprehension
    "comprehension": {"local": {"target", "iter"}, "localg": {"ifs"}, "add_break": {"except"}}, # for non-iterable iter 

    # excepthandler
    "ExceptHandler": {"local": {"type", "body"}},

    # arguments
    "arguments": {"localg": {"args", "kwonlyargs", "defaults", "kw_defaults"}, "local": {"varargannotation", "kwargannotation"}},

    # arg
    "arg": {"local": {"annotation"}},

    # keyword
    "keyword": {"local": {"value"}},

    # alias
    "alias": {},
}

class UserStop(Exception): pass
