"""
Contains code for auto-marking AST nodes.

"""

import ast

import analysis.markers.breaks
import analysis.markers.visible
from writer import sourcewriter
from writer import prettywriter

class AutoMarker:
    """Tries to find correct markings for each node."""

    def __init__(self,
                 res_order : "The resolution order for calculating markings.",
                 mark : "Should we mark the nodes as we work?" = True,
                 verbose = False,
                 def_visible : "Function to get defaults from a visibility marker." = None,
                 def_break : "Function to get defaults from a break marker." = None):
        order_allowed = set(["mark", "calc", "user"])

        for res in res_order:
            try:
                order_allowed.remove(res)
            except KeyError:
                raise ValueError("Method " + res + " is invalid or specified too many times.")

        self.res_order = res_order
        self.verbose = verbose
        self.def_visible = def_visible
        self.def_breaks = def_breaks

        if self.def_visible == None:
            self.def_visible = (lambda m: return m.isVisible())
        if self.def_breaks == None:
            self.def_breaks = (lambda m: return m.breakers())

########################################################
# Resolution functions                                 #
# - Return full dicts with everything we ask for       #
# - Can throw UserStop to finish part way through      #
# - Use functions in next section to resolve           #
# - Should never alter return value from resolve_marks #
########################################################

    def resolve_marks(self, node, visible = False, breaks = False):
        """Resolve markings for a given node based on the given resolution order. Can throw UserStop"""

        result = {}

        for res in self.res_order + ["default"]:
            if visible and "visible" in result:
                visible = False
            if breaks and "breaks" in result:
                breaks = False
            if not visible and not breaks: # done
                break

            remainder = {
                "mark": self.get_marks,
                "calc": self.calculate_marks,
                "user": self.user_marks,
                "default": self.default_marks
            }[res](node, visible, breaks)
            result.update(remainder) # should only contain as yet unmarked values

        if self.mark:
            if visible:
                analysis.markers.visible.VisibleMarker(node).setVisible(result["visible"])
            if breaks:
                analysis.markers.breaks.BreakMarker(node).setBreaks(result["breaks"])

        return result

    def resolve_group(self, nodes, visible = False, breaks = False):
        """Resolve each of the nodes in the set. Avoids pretending they are a new node."""

        result = self._base_marks()
        for node in nodes:
            n_marks = self.resolve_marks(node, visible, breaks)
            self._combine_marks(result, n_marks, visible, breaks)
        return result

    def _base_marks(self, visible, breaks):
        """Get a new dictionary containing the markings for an empty list of nodes."""

        result = {}
        if visible:
            result["visible"] = False
        if breaks:
            result["breaks"] = set()
        return result

    def _combine_marks(self, marks, addition, visible, breaks):
        """Modify marks to account for having also performed an execution resulting with the marks in addition."""

        if marks == None:
            marks = self._base_marks()

        if visible:
            marks["visible"] |= addition["visible"]
        if breaks:
            marks["breaks"].update(addition["breaks"])

#########################################
# Resolution Methods                    #
# - Resolve markings in a specific way  #
# - Don't return entries we do not know #
#########################################

    def get_marks(self, node, visible, breaks):
        """Get the current markings for the node if they exist, or None."""

        result = {}
        if visible:
            marker = analysis.markers.visible.VisibleMarker(node)
            if marker.is_marked():
                result["visible"] = marker.isVisible()
        if breaks:
            marker = analysis.markers.breaks.BreakMarker(node)
            if marker.is_marked():
                result["breaks"] = marker.breakers()

        return result

    def user_marks(self, node, visible, breaks):
        """Ask the user for input on the current situation."""

        if visible:
            self._ask_user("There is no marking to indicate visibility.", node)
        if breaks:
            self._ask_user("There is no marking to indicate breaking statements.", node)

        return {}

    def _ask_user(self, question, node):
        """Print a problem and ask the user to fix it, print it or ignore it."""

        print(question)

        while True:
            print()
            print("Would you like to:")
            print("p) Print more information. This could be large.")
            print("i) Ignore the problem. Allow other mechanisms to fix it.")
            print("f) Stop and fix the problem.")

            ans = ""
            while ans not in ["p", "i", "f"]:
                ans = input("Choose an option: ")

            if ans == "p":
                sourcewriter.printSource(node, prettywriter.PrettyWriter)
            elif ans == "i":
                return
            elif ans == "f":
                raise UserStop

    def default_marks(self, node, visible, breaks):
        """Get the default values for markings on the current node."""

        result = {}
        if visible:
            m = analysis.markers.visible.VisibleMarker(node)
            result["visible"] = self.def_visible(m)
        if breaks:
            m = analysis.markers.breaks.BreakMarker(node)
            result["breaks"] = self.def_breaks(m)

        return result

    def calculate_marks(self, node, visible, breaks):
        """Calculate markings for the given mark types on node."""

        try:
            method = getattr(self, "_marks_" + node.__class__.__name__)
        except AttributeError as exc:
            return {}
        else:
            return method(node, visible, breaks)

##############################################################
# Individual node calculations                               #
# - Each is a specific calculation of markings for one node. #
# - Only creates the answers it is sure of                   #
##############################################################

    def _marks_list(self, node, visible, breaks):
        return self.resolve_group(node, visible, breaks)

    def _marks_Module(self, node, visible, breaks):
       # Could replace breaks with exception, but exception is at parse time
        return self.resolve_marks(node.body, visible, breaks)

    def _marks_Interactive(self, node, visible, breaks):
        return self.resolve_marks(node.body, visible, breaks)

    def _marks_Expression(self, node, visible, breaks):
        return self.resolve_marks(node.body, visible, breaks)

    def _marks_Suite(self, node, visible, breaks): # TODO - check what this is
        return self.resolve_marks(node.body, visible, breaks)

    # stmt
    def _marks_FunctionDef(self, node, visible, breaks):
        if node.decorator_list: # Translate for decorators
            func = ast.FunctionDef(node.name, node.args, node.body, [], node.returns)
            assname = ast.Name(node.name, ast.Store())
            calls = ast.Name(node.name, ast.Load())
            for dec in node.decorator_list.reverse():
                calls = ast.Call(dec, [calls], [], None, None)
            return self.resolve_marks([func, ast.Assign([assname], calls)], visible, breaks)
        else:
            # Commented is for the function body, this is not executed when the function is defined
            #marks = self.resolve_marks(node.body, visible, breaks).copy()
            #if breaks:
            #    marks["breaks"] = {b for b in marks["breaks"] if b not in ["return", "yield"]}
            #return marks
            return self._base_marks(visible, breaks)

    def _marks_ClassDef(self, node, visible, breaks):
        if node.decorator_list: # Translate for decorators
            cls = ast.ClassDef(node.name, node.bases, node.keywords, node.starargs, node.kwargs, [])
            assname = ast.Name(node.name, ast.Store())
            calls = ast.Name(node.name, ast.Load())
            for dec in node.decorator_list.reverse():
                calls = ast.Call(dec, [calls], [], None, None)
            return self.resolve_marks([cls, ast.Assign([assname], calls)], visible, breaks)
        else:
            return self.resolve_marks(node.body)

    def _marks_Return(self, node, visible, breaks):
        if node.value == None:
            marks = self._base_marks(visible, breaks)
        else:
            marks = self.resolve_marks(node.value).copy()
        if breaks:
            marks["breaks"] = marks["breaks"].copy()
            marks["breaks"].add("return")
        return marks

    def _marks_Delete(self, node, visible, breaks):
        return self.resolve_group(node.targets, visible, breaks)
        # NameError covered in ctx

    def _marks_Assign(self, node, visible, breaks):
        return self.resolve_group(node.targets + [node.value], visible, breaks)

    def _marks_AugAssign(self, node, visible, breaks):
        trans = ast.Assign([node.target], ast.BinOp(node.target, node.op, node.value)) # Transform to a binary op
        return self.resolve_marks(trans, visible, breaks)

    def _marks_For(self, node, visible, breaks):
        # for-else has same vis/break as doing for then body of else
        if node.orelse:
            n_for = ast.For(node.target, node.iter, node.body, [])
            return self.resolve_group({n_for, node.orelse}, visible, breaks)
        else:
            # same vis/break as iter followed by body (break/continue) cannot be present in iter
            marks = self.resolve_group({node.iter, node.body}, visible, breaks)
            if breaks:
                marks["breaks"].remove("break")
                marks["breaks"].remove("continue")
            return marks

    def _marks_While(self, node, visible, breaks):
        # similar to for
        if node.orelse:
            n_while = ast.While(node.test, node.body, [])
            return self.resolve_group({n_while, node.orelse}, visible, breaks)
        else:
            # same vis/break as test followed by body (break/continue) cannot be present in test
            marks = self.resolve_group({node.test, node.body}, visible, breaks)
            if breaks:
                marks["breaks"].remove("break")
                marks["breaks"].remove("continue")
            return marks
    
    def _marks_If(self, node, visible, breaks):
        return self.resolve_group({node.test, node.body, node.orelse}, visible, breaks)

    def _marks_With(self, node, visible, breaks):
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

    def _marks_Raise(self, node, visible, breaks):
        # Same as evaluating the exceptions and raising
        stmts = set()
        if node.exc:
            stmts.add(node.exc)
        if node.cause:
            stmts.add(node.cause)
        marks = self.resolve_group(stmts, visible, breaks)
        if breaks:
            marks["breaks"].add("except")
        return marks

    def _marks_TryExcept(self, node, visible, breaks):
        # visible/break same as running body, running handlers, running else
        # Will not catch anything unless the handler is straight except:
        # This is because it is hard to match type for a name

        # Look for straight except:
        exc = False
        for handler in node.handlers:
            exc |= (handler.type == None)
        marks = self.resolve_marks(node.body, visible, breaks).copy()
        if breaks and exc:
            marks["breaks"] = marks["breaks"].copy()
            marks["breaks"].remove("except")

        others = self.resolve_group(node.handlers + [node.orelse], visible, breaks) # running all handlers and else
        return self._combine_marks(marks, others, visible, breaks)

    def _marks_TryFinally(self, node, visible, breaks):
        # Same as running both try and finally body
        return self.resolve_group({node.body, node.finalbody}, visible, breaks)

    def _marks_Assert(self, node, visible, breaks):
        # Eval test and msg, raise exception
        marks = self.resolve_group({node.test, node.msg}, visible, breaks)
        if breaks:
            marks["breaks"].add("except")
        return marks

    def _marks_Import(self, node, visible, breaks):
        return {} # Can do anything we could import!
        # TODO - Check imported module?

    def _marks_ImportFrom(self, node, visible, breaks):
        return {} # Again we have no idea!
        # TODO - Check imported module?

    def _marks_Global(self, node, visible, breaks):
        # Any exceptions are thrown at parsing. Not runtime.
        return self._base_marks(visible, breaks)

    def _marks_Nonlocal(self, node, visible, breaks):
        # Any exceptions are thrown at parsing. Not runtime.
        return self._base_marks(visible, breaks)
        

    def _marks_Expr(self, node, visible, breaks):
        return self.resolve_marks(node.value, visible, breaks)

    def _marks_Pass(self, node, visible, breaks):
        return self._base_marks(visible, breaks)

    def _marks_Break(self, node, visible, breaks):
        marks = self._base_marks(visible, breaks)
        if breaks:
            marks["breaks"].add("break")
        return marks

    def _marks_Continue(self, node, visible, breaks):
        marks = self._base_marks(visible, breaks)
        if breaks:
            marks["breaks"].add("continue")
        return marks

    # expr
    def _marks_BoolOp(self, node, visible, breaks):
        # Don't see that boolop can throw exceptions, it doesn't care about type etc
        return self.resolve_group(node.values, visible, breaks)

    def _marks_BinOp(self, node, visible, breaks):
        # As above with extra exception
        marks = self.resolve_group({node.left, node.right}, visible, breaks)
        if breaks:
            marks["breaks"].add("except")
        return marks

    def _marks_UnaryOp(self, node, visible, breaks):
        marks = self.resolve_marks(node.operand, visible, breaks).copy()
        if breaks:
            marks["breaks"] = marks["breaks"].copy()
            marks["breaks"].add("except")
        return marks

    def _marks_Lambda(self, node, visible, breaks):
        # Doesn't run it, just defines it.
        return self._base_marks(visible, breaks)

    def _marks_IfExp(self, node, visible, breaks):
        return self.resolve_group({node.test, node.body, node.orelse}, visible, breaks)

    def _marks_Dict(self, node, visible, breaks):
        return self.resolve_group(node.keys + node.values, visible, breaks)

    def _marks_Set(self, node, visible, breaks):
        return self.resolve_group(node.elts, visible, breaks)

    def _marks_ListComp(self, node, visible, breaks):
        return self.resolve_group([node.elt] + node.generators, visible, breaks)

    def _marks_SetComp(self, node, visible, breaks):
        return self.resolve_group([node.elt] + node.generators, visible, breaks)

    def _marks_DictComp(self, node, visible, breaks):
        return self.resolve_group([node.key, node.value] + node.generators, visible, breaks)

    def _marks_GeneratorExp(self, node, visible, breaks):
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

    def _marks_Yield(self, node, visible, breaks):
        # PEP 0342 describes yield expression.
        # Not mentioned to be accepted but experimentation tells me it probably was.
        results = self._base_marks(visible, marks)
        if breaks:
            results["breaks"].add("except")
            results["breaks"].add("yield")
        if node.value == None:
            return results
        else:
            v_marks = self.resolve_marks(node.value, visible, breaks)
            return self._combine_marks(results, v_marks, visible, breaks)

    def _marks_Compare(self, node, visible, breaks):
        results = self.resolve_group([node.left] + node.comparators, visible, breaks)
        if breaks:
            results["breaks"].add("except")

    def _marks_Call(self, node, visible, breaks):
        # No idea what we'd be calling
        # TODO - think harder
        return {}

    def _marks_Num(self, node, visible, breaks):
        return self._base_marks(visible, breaks)

    def _marks_Str(self, node, visible, breaks):
        return self._base_marks(visible, breaks)

    def _marks_Bytes(self, node, visible, breaks):
        return self._base_marks(visible, breaks)

    def _marks_Ellipsis(self, node, visible, breaks):
        return self._base_marks(visible, breaks)

    def _marks_Attribute(self, node, visible, breaks):
        # Eval node.value
        # Now we treat like a search for a simple name in node.value
        # TODO - store and denied?
        return self.resolve_group({node.value, node.ctx}, visible, breaks)

    def _marks_Subscript(self, node, visible, breaks):
        # Similar to above
        # TODO - store and denied?
        return self.resolve_group({node.value, node.slice, node.ctx}, visible, breaks)

    def _marks_Starred(self, node, visible, breaks):
        return self.resolve_group({node.value, node.ctx}, visible, breaks)

    def _marks_Name(self, node, visible, breaks):
        return self.resolve_marks(node.ctx, visible, breaks)

    def _marks_List(self, node, visible, breaks):
        # Normal ctx stuff plus think about unpacking
        marks = self.resolve_group(node.elts + [node.ctx], visible, breaks)
        if breaks and isinstance(node.ctx, ast.Store):
            marks["breaks"].add("except")
        return marks

    def _marks_Tuple(self, node, visible, breaks):
        marks = self.resolve_group(node.elts + [node.ctx], visible, breaks)
        if breaks and isinstance(node.ctx, ast.Store):
            marks["breaks"].add("except")
        return marks

    # expr_context
    def _marks_Load(self, node, visible, breaks):
        marks = self._base_marks(visible, breaks)
        if breaks:
            marks["breaks"].add("except") # if not found
        return marks

    def _marks_Store(self, node, visible, breaks):
        return self._base_marks(visible, breaks)
        # TODO - think about storing to a class and being denied

    def _marks_Del(self, node, visible, breaks):
        marks = self._base_marks(visible, breaks)
        if breaks:
            marks["breaks"].add("except") # if not found
        return marks

    def _marks_AugLoad(self, node, visible, breaks):
        return {} # Don't appear to be used, so don't know

    def _marks_AugStore(self, node, visible, breaks):
        return {} # Don't appear to be used, so don't know

    def _marks_Param(self, node, visible, breaks):
        return {} # Apparently used by a in 'def f(a): pass'
                  # Seems to not be though

    # slice
    def _marks_Slice(self, node, visible, breaks):
        # Context dealt with in Subscript
        m = set()
        if node.lower != None:
            m.add(node.lower)
        if node.upper != None:
            m.add(node.upper)
        if node.step != None:
            m.add(node.step)
        return self.resolve_group(m, visible, breaks)

    def _marks_ExtSlice(self, node, visible, breaks):
        return self.resolve_group(node.dims, visible, breaks)

    def _marks_Index(self, node, visible, breaks):
        return self.resolve_marks(node.value, visible, breaks)

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
    #def _marks_comprehension(self, node, visible, breaks): raise NotImplementedError

    # excepthandler
    #def _marks_ExceptHandler(self, node, visible, breaks): raise NotImplementedError

    # arguments
    #def _marks_arguments(self, node, visible, breaks): raise NotImplementedError

    # arg
    #def _marks_arg(self, node, visible, breaks): raise NotImplementedError

    # keyword
    #def _marks_keyword(self, node, visible, breaks): raise NotImplementedError

    # alias
    #def _marks_alias(self, node, visible, breaks): raise NotImplementedError


class UserStop(Exception): pass
