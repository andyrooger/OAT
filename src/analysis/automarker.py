"""
Contains code for auto-marking AST nodes.

"""

import ast

import analysis.markers.breaks
import analysis.markers.visible

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

########################################################
# Resolution functions                                 #
# - Return full dicts with everything we ask for       #
# - Can throw UserStop to finish part way through      #
# - Use functions in next section to resolve           #
# - Should never alter return value from resolve_marks #
########################################################

    def resolve_marks(self, node, needed : "Set containing the markings we want." = {"visible", "breaks"}):
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
            "breaks": set()
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
            "breaks": analysis.markers.breaks.BreakMarker
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

        try:
            method = getattr(self, "_marks_" + node.__class__.__name__)
        except AttributeError as exc:
            return {}
        else:
            return method(node, needed)

##############################################################
# Individual node calculations                               #
# - Each is a specific calculation of markings for one node. #
# - Only creates the answers it is sure of                   #
##############################################################

    def _marks_list(self, node, needed):
        return self.resolve_group(node, needed)

    def _marks_Module(self, node, needed):
       # Could replace breaks with exception, but exception is at parse time
        return self.resolve_marks(node.body, needed)

    def _marks_Interactive(self, node, needed):
        return self.resolve_marks(node.body, needed)

    def _marks_Expression(self, node, needed):
        return self.resolve_marks(node.body, needed)

    def _marks_Suite(self, node, visible, breaks): # TODO - check what this is
        return self.resolve_marks(node.body, needed)

    # stmt
    def _marks_FunctionDef(self, node, needed):
        if node.decorator_list: # Translate for decorators
            func = ast.FunctionDef(node.name, node.args, node.body, [], node.returns)
            assname = ast.Name(node.name, ast.Store())
            calls = ast.Name(node.name, ast.Load())
            for dec in node.decorator_list.reverse():
                calls = ast.Call(dec, [calls], [], None, None)
            return self.resolve_marks([func, ast.Assign([assname], calls)], needed)
        else:
            # Commented is for the function body, this is not executed when the function is defined
            #marks = self.resolve_marks(node.body, visible, breaks).copy()
            #if breaks:
            #    marks["breaks"] = {b for b in marks["breaks"] if b not in ["return", "yield"]}
            #return marks
            if node.returns == None:
                return self._base_marks(needed)
            else:
                return self.resolve_group([node.returns, node.args], needed)

    def _marks_ClassDef(self, node, needed):
        if node.decorator_list: # Translate for decorators
            cls = ast.ClassDef(node.name, node.bases, node.keywords, node.starargs, node.kwargs, [])
            assname = ast.Name(node.name, ast.Store())
            calls = ast.Name(node.name, ast.Load())
            for dec in node.decorator_list.reverse():
                calls = ast.Call(dec, [calls], [], None, None)
            return self.resolve_marks([cls, ast.Assign([assname], calls)], needed)
        else:
            # Evaluates body as annotations
            possibles = [node.body] + node.bases + node.keywords
            if node.starargs != None:
                possibles.append(node.starargs)
            if node.kwargs != None:
                possibles.append(node.kwargs)
            return self.resolve_group(possibles, needed)

    def _marks_Return(self, node, needed):
        if node.value == None:
            marks = self._base_marks(needed)
        else:
            marks = self.resolve_marks(node.value, needed).copy()
        if "breaks" in needed:
            marks["breaks"] = marks["breaks"].copy()
            marks["breaks"].add("return")
        return marks

    def _marks_Delete(self, node, needed):
        return self.resolve_group(node.targets, needed)
        # NameError covered in ctx

    def _marks_Assign(self, node, needed):
        return self.resolve_group(node.targets + [node.value], needed)

    def _marks_AugAssign(self, node, needed):
        trans = ast.Assign([node.target], ast.BinOp(node.target, node.op, node.value)) # Transform to a binary op
        return self.resolve_marks(trans, needed)

    def _marks_For(self, node, needed):
        # for-else has same vis/break as doing for then body of else
        if node.orelse:
            n_for = ast.For(node.target, node.iter, node.body, [])
            return self.resolve_group([n_for, node.orelse], needed)
        else:
            # same vis/break as iter followed by body (break/continue) cannot be present in iter
            marks = self.resolve_group([node.iter, node.body], needed)
            if "breaks" in needed:
                marks["breaks"].remove("break")
                marks["breaks"].remove("continue")
                marks["breaks"].add("except") # in case iter is not iterable
            return marks

    def _marks_While(self, node, needed):
        # similar to for
        if node.orelse:
            n_while = ast.While(node.test, node.body, [])
            return self.resolve_group([n_while, node.orelse], needed)
        else:
            # same vis/break as test followed by body (break/continue) cannot be present in test
            marks = self.resolve_group([node.test, node.body], needed)
            if "breaks" in needed:
                marks["breaks"].remove("break")
                marks["breaks"].remove("continue")
            return marks
    
    def _marks_If(self, node, needed):
        return self.resolve_group([node.test, node.body, node.orelse], needed)

    def _marks_With(self, node, needed):
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
        return {} # For don't know

    def _marks_Raise(self, node, needed):
        # Same as evaluating the exceptions and raising
        stmts = []
        if node.exc:
            stmts.append(node.exc)
        if node.cause:
            stmts.append(node.cause)
        marks = self.resolve_group(stmts, needed)
        if "breaks" in needed:
            marks["breaks"].add("except")
        return marks

    def _marks_TryExcept(self, node, needed):
        # visible/break same as running body, running handlers, running else
        # Will not catch anything unless the handler is straight except:
        # This is because it is hard to match type for a name

        # Look for straight except:
        exc = False
        for handler in node.handlers:
            exc |= (handler.type == None)
        marks = self.resolve_marks(node.body, needed).copy()
        if "breaks" in needed and exc:
            marks["breaks"] = marks["breaks"].copy()
            marks["breaks"].remove("except")

        others = self.resolve_group(node.handlers + [node.orelse], needed) # running all handlers and else
        return self._combine_marks(marks, others, needed)

    def _marks_TryFinally(self, node, needed):
        # Same as running both try and finally body
        return self.resolve_group([node.body, node.finalbody], needed)

    def _marks_Assert(self, node, needed):
        # Eval test and msg, raise exception
        marks = self.resolve_group([node.test, node.msg], needed)
        if "breaks" in needed:
            marks["breaks"].add("except")
        return marks

    def _marks_Import(self, node, needed):
        return {} # Can do anything we could import!
        # TODO - Check imported module?

    def _marks_ImportFrom(self, node, needed):
        return {} # Again we have no idea!
        # TODO - Check imported module?

    def _marks_Global(self, node, needed):
        # Any exceptions are thrown at parsing. Not runtime.
        return self._base_marks(needed)

    def _marks_Nonlocal(self, node, needed):
        # Any exceptions are thrown at parsing. Not runtime.
        return self._base_marks(needed)
        

    def _marks_Expr(self, node, needed):
        return self.resolve_marks(node.value, needed)

    def _marks_Pass(self, node, needed):
        return self._base_marks(needed)

    def _marks_Break(self, node, needed):
        marks = self._base_marks(needed)
        if "breaks" in needed:
            marks["breaks"].add("break")
        return marks

    def _marks_Continue(self, node, needed):
        marks = self._base_marks(needed)
        if "breaks" in needed:
            marks["breaks"].add("continue")
        return marks

    # expr
    def _marks_BoolOp(self, node, needed):
        # Don't see that boolop can throw exceptions, it doesn't care about type etc
        return self.resolve_group(node.values, needed)

    def _marks_BinOp(self, node, needed):
        # As above with extra exception
        marks = self.resolve_group([node.left, node.right], needed)
        if "breaks" in needed:
            marks["breaks"].add("except")
        return marks

    def _marks_UnaryOp(self, node, needed):
        marks = self.resolve_marks(node.operand, needed).copy()
        if "breaks" in needed:
            marks["breaks"] = marks["breaks"].copy()
            marks["breaks"].add("except")
        return marks

    def _marks_Lambda(self, node, needed):
        # Doesn't run it, just defines it. Eval args.
        return self.resolve_marks(node.args, needed)

    def _marks_IfExp(self, node, needed):
        return self.resolve_group([node.test, node.body, node.orelse], needed)

    def _marks_Dict(self, node, needed):
        return self.resolve_group(node.keys + node.values, needed)

    def _marks_Set(self, node, needed):
        return self.resolve_group(node.elts, needed)

    def _marks_ListComp(self, node, needed):
        return self.resolve_group([node.elt] + node.generators, needed)

    def _marks_SetComp(self, node, needed):
        return self.resolve_group([node.elt] + node.generators, needed)

    def _marks_DictComp(self, node, needed):
        return self.resolve_group([node.key, node.value] + node.generators, needed)

    def _marks_GeneratorExp(self, node, needed):
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
        return {}

    def _marks_Yield(self, node, needed):
        # PEP 0342 describes yield expression.
        # Not mentioned to be accepted but experimentation tells me it probably was.
        results = self._base_marks(needed)
        if "breaks" in needed:
            results["breaks"].add("except")
            results["breaks"].add("yield")
        if node.value == None:
            return results
        else:
            v_marks = self.resolve_marks(node.value, needed)
            return self._combine_marks(results, v_marks, needed)

    def _marks_Compare(self, node, needed):
        results = self.resolve_group([node.left] + node.comparators, needed)
        if "breaks" in needed:
            results["breaks"].add("except")
        return results

    def _marks_Call(self, node, needed):
        # No idea what we'd be calling
        # TODO - think harder
        return {}

    def _marks_Num(self, node, needed):
        return self._base_marks(needed)

    def _marks_Str(self, node, needed):
        return self._base_marks(needed)

    def _marks_Bytes(self, node, needed):
        return self._base_marks(needed)

    def _marks_Ellipsis(self, node, needed):
        return self._base_marks(needed)

    def _marks_Attribute(self, node, needed):
        # Eval node.value
        # Now we treat like a search for a simple name in node.value
        # TODO - store and denied?
        return self.resolve_group([node.value, node.ctx], needed)

    def _marks_Subscript(self, node, needed):
        # Similar to above
        # TODO - store and denied?
        return self.resolve_group([node.value, node.slice, node.ctx], needed)

    def _marks_Starred(self, node, needed):
        return self.resolve_group([node.value, node.ctx], needed)

    def _marks_Name(self, node, needed):
        return self.resolve_marks(node.ctx, needed)

    def _marks_List(self, node, needed):
        # Normal ctx stuff plus think about unpacking
        marks = self.resolve_group(node.elts + [node.ctx], needed)
        if "breaks" in needed and isinstance(node.ctx, ast.Store):
            marks["breaks"].add("except")
        return marks

    def _marks_Tuple(self, node, needed):
        marks = self.resolve_group(node.elts + [node.ctx], needed)
        if "breaks" in needed and isinstance(node.ctx, ast.Store):
            marks["breaks"].add("except")
        return marks

    # expr_context
    def _marks_Load(self, node, needed):
        marks = self._base_marks(needed)
        if "breaks" in needed:
            marks["breaks"].add("except") # if not found
        return marks

    def _marks_Store(self, node, needed):
        return self._base_marks(needed)
        # TODO - think about storing to a class and being denied

    def _marks_Del(self, node, needed):
        marks = self._base_marks(needed)
        if "breaks" in needed:
            marks["breaks"].add("except") # if not found
        return marks

    def _marks_AugLoad(self, node, needed):
        return {} # Don't appear to be used, so don't know

    def _marks_AugStore(self, node, needed):
        return {} # Don't appear to be used, so don't know

    def _marks_Param(self, node, needed):
        return {} # Apparently used by a in 'def f(a): pass'
                  # Seems to not be though

    # slice
    def _marks_Slice(self, node, needed):
        # Context dealt with in Subscript
        m = []
        if node.lower != None:
            m.append(node.lower)
        if node.upper != None:
            m.append(node.upper)
        if node.step != None:
            m.append(node.step)
        return self.resolve_group(m, needed)

    def _marks_ExtSlice(self, node, needed):
        return self.resolve_group(node.dims, needed)

    def _marks_Index(self, node, needed):
        return self.resolve_marks(node.value, needed)

# These binary operators are not currently used by me
#  - the boolop or binop nodes already covered it
#  - TODO - Sort this out, maybe?

    # boolop
    #def _marks_And(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Or(self, node, visible, breaks): raise NotImplementedError

    # operator
    #def _marks_Add(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Sub(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Mult(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Div(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Mod(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Pow(self, node, visible, breaks): raise NotImplementedError
    #def _marks_LShift(self, node, visible, breaks): raise NotImplementedError
    #def _marks_RShift(self, node, visible, breaks): raise NotImplementedError
    #def _marks_BitOr(self, node, visible, breaks): raise NotImplementedError
    #def _marks_BitXor(self, node, visible, breaks): raise NotImplementedError
    #def _marks_BitAnd(self, node, visible, breaks): raise NotImplementedError
    #def _marks_FloorDiv(self, node, visible, breaks): raise NotImplementedError

# Same with unary and comparisons

    # unaryop
    #def _marks_Invert(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Not(self, node, visible, breaks): raise NotImplementedError
    #def _marks_UAdd(self, node, visible, breaks): raise NotImplementedError
    #def _marks_USub(self, node, visible, breaks): raise NotImplementedError

    # cmpop
    #def _marks_Eq(self, node, visible, breaks): raise NotImplementedError
    #def _marks_NotEq(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Lt(self, node, visible, breaks): raise NotImplementedError
    #def _marks_LtE(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Gt(self, node, visible, breaks): raise NotImplementedError
    #def _marks_GtE(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Is(self, node, visible, breaks): raise NotImplementedError
    #def _marks_IsNot(self, node, visible, breaks): raise NotImplementedError
    #def _marks_In(self, node, visible, breaks): raise NotImplementedError
    #def _marks_NotIn(self, node, visible, breaks): raise NotImplementedError


    # comprehension
    def _marks_comprehension(self, node, needed):
        marks = self.resolve_group([node.target, node.iter] + node.ifs, needed)
        if "breaks" in needed:
            marks["breaks"].add("except") # for non-iterable iter 
        return marks

    # excepthandler
    def _marks_ExceptHandler(self, node, needed):
        marks = self.resolve_group(node.body, needed)
        if node.type != None:
            t_marks = self.resolve_marks(node.type, needed)
            self._combine_marks(marks, t_marks, needed)
        return marks

    # arguments
    def _marks_arguments(self, node, needed):
        possibles = node.args + node.kwonlyargs + node.defaults + node.kw_defaults
        if node.varargannotation != None:
            possibles.append(node.varargannotation)
        if node.kwargannotation != None:
            possibles.append(node.kwargannotation)
        return self.resolve_group(possibles, needed)

    # arg
    def _marks_arg(self, node, needed):
        if node.annotation:
            return self.resolve_marks(node.annotation, needed)
        else:
            return self._base_marks(needed)

    # keyword
    def _marks_keyword(self, node, needed):
        return self.resolve_marks(node.value, needed)

    # alias
    def _marks_alias(self, node, needed):
        return self._base_marks(needed)


class UserStop(Exception): pass
