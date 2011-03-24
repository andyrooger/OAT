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
                 set_visible : "Function to set defaults on a visibility marker." = None,
                 set_break : "Function to set defaults on a break marker." = None):
        order_allowed = set(["mark", "calc", "user"])

        for res in res_order:
            try:
                order_allowed.remove(res)
            except KeyError:
                raise ValueError("Method " + res + " is invalid or specified too many times.")

        self.res_order = res_order
        self.verbose = verbose
        self.set_visible = set_visible
        self.set_breaks = set_breaks

        if self.set_visible == None:
            self.set_visible = (lambda m: m.setVisible(m.isVisible()))
        if self.set_breaks == None:
            self.set_breaks = (lambda m: m.setBreaks(m.breakers()))

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

    def calculate_marks(self, node, visible = False, breaks = False):
        """Calculate markings for the given mark types on node."""

        try:
            method = getattr(self, "_marks_" + node.__class__.__name__)
        except AttributeError as exc:
            return {}
        else:
            return method(node, visible, breaks)
        

    def get_marks(self, node, visible = False, breaks = False):
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

    def user_marks(self, node, visible = False, breaks = False):
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

    def default_marks(self, node, visible = False, breaks = False):
        """Get the default values for markings on the current node."""

        result = {}
        if visible:
            m = analysis.markers.visible.VisibleMarker(node)
            result["visible"] = self.set_visible(m)
        if breaks:
            m = analysis.markers.breaks.BreakMarker(node)
            result["breaks"] = self.set_breaks(m)

        return result

    def _marks_list(self, node, visible, breaks):
        """Find markings for a list of statements."""

        result = {}
        for stmt in node.body:
            marks = self.resolve_marks(stmt, visible, breaks)
            if visible and "visible" in marks:
                result["visible"] |= marks["visible"]
            if breaks and "breaks" in marks:
                result["breaks"].update(marks["breaks"])

        return result

    def _marks_Module(self, node, visible, breaks):
        marks = self.resolve_marks(node.body, visible, breaks).copy()
        if breaks and "breaks" in marks:
            # replace any break with an exception
            if marks["breaks"]:
                marks["breaks"] = {"except"}
        return marks

    def _marks_Interactive(self, node, visible, breaks):
        marks = self.resolve_marks(node.body, visible, breaks).copy()
        if breaks and "breaks" in marks:
            # replace any break with an exception
            if marks["breaks"]:
                marks["breaks"] = {"except"}
        return marks

    def _marks_Expression(self, node, visible, breaks):
        marks = self.resolve_marks(node.body, visible, breaks).copy()
        if breaks and "breaks" in marks:
            # replace any break with an exception
            if marks["breaks"]:
                marks["breaks"] = {"except"}
        return marks

    def _marks_Suite(self, node, visible, breaks): # TODO - check what this is
        marks = self.resolve_marks(node.body, visible, breaks).copy()
        if breaks and "breaks" in marks:
            # replace any break with an exception
            if marks["breaks"]:
                marks["breaks"] = {"except"}
        return marks

    # stmt
    def _marks_FunctionDef(self, node, visible, breaks):
        if node.decorator_list: # Translate for decorators
            func = ast.FunctionDef(node.name, node.args, node.body, [], node.returns)
            name = ast.Name(node.name, ast.Load())
            calls = name
            for dec in node.decorator_list.reverse():
                calls = ast.Call(dec, [calls], [], None, None)
            return self.resolve_marks([func, ast.Assign([name], calls)])
        else:
            marks = self.resolve_marks(node.body, visible, breaks).copy()
            try:
                del marks["breaks"]["return"]
            except KeyError:
                pass # No breaks marking or particular breaks not found
            return marks

    #def _marks_ClassDef(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Return(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Delete(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Assign(self, node, visible, breaks): raise NotImplementedError
    #def _marks_AugAssign(self, node, visible, breaks): raise NotImplementedError

    #def _marks_For(self, node, visible, breaks): raise NotImplementedError
    #def _marks_While(self, node, visible, breaks): raise NotImplementedError
    #def _marks_If(self, node, visible, breaks): raise NotImplementedError
    #def _marks_With(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Raise(self, node, visible, breaks): raise NotImplementedError
    #def _marks_TryExcept(self, node, visible, breaks): raise NotImplementedError
    #def _marks_TryFinally(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Assert(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Import(self, node, visible, breaks): raise NotImplementedError
    #def _marks_ImportFrom(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Global(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Nonlocal(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Expr(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Pass(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Break(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Continue(self, node, visible, breaks): raise NotImplementedError

    # expr
    #def _marks_BoolOp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_BinOp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_UnaryOp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Lambda(self, node, visible, breaks): raise NotImplementedError
    #def _marks_IfExp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Dict(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Set(self, node, visible, breaks): raise NotImplementedError
    #def _marks_ListComp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_SetComp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_DictComp(self, node, visible, breaks): raise NotImplementedError
    #def _marks_GeneratorExp(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Yield(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Compare(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Call(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Num(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Str(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Bytes(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Ellipsis(self, node, visible, breaks): raise NotImplementedError

    #def _marks_Attribute(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Subscript(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Starred(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Name(self, node, visible, breaks): raise NotImplementedError
    #def _marks_List(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Tuple(self, node, visible, breaks): raise NotImplementedError

    # expr_context
    #def _marks_Load(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Store(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Del(self, node, visible, breaks): raise NotImplementedError
    #def _marks_AugLoad(self, node, visible, breaks): raise NotImplementedError
    #def _marks_AugStore(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Param(self, node, visible, breaks): raise NotImplementedError

    # slice
    #def _marks_Slice(self, node, visible, breaks): raise NotImplementedError
    #def _marks_ExtSlice(self, node, visible, breaks): raise NotImplementedError
    #def _marks_Index(self, node, visible, breaks): raise NotImplementedError

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
