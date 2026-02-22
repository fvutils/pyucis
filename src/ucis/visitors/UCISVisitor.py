'''
Created on Jan 12, 2020

@author: ballance
'''
from ucis.scope_type_t import ScopeTypeT


class UCISVisitor():
    """Visitor base class for traversing UCIS data model.

    Override the visit_* methods you care about.  All methods have default
    no-op implementations so you only need to override what you need.

    Use ``traverse(db)`` (from ucis.visitors.traverse) to walk the tree and
    invoke the appropriate visit_* callbacks.
    """

    def __init__(self):
        pass

    # --- Database ---

    def visit_db(self, db):
        """Called when entering the root UCIS database."""
        pass

    def leave_db(self, db):
        """Called when leaving the root UCIS database."""
        pass

    # --- History nodes ---

    def visit_history_node(self, node):
        """Called for each history (test-run) node."""
        pass

    # --- Design units ---

    def visit_du_scope(self, du):
        """Called when entering any design-unit scope (DU_MODULE, etc.)."""
        pass

    def leave_du_scope(self, du):
        """Called when leaving any design-unit scope."""
        pass

    # --- Instance scopes ---

    def visit_instance(self, inst):
        """Called when entering an INSTANCE scope."""
        pass

    def leave_instance(self, inst):
        """Called when leaving an INSTANCE scope."""
        pass

    # --- Covergroups ---

    def visit_covergroup(self, cg):
        """Called when entering a COVERGROUP scope."""
        pass

    def leave_covergroup(self, cg):
        """Called when leaving a COVERGROUP scope."""
        pass

    def visit_cover_instance(self, cgi):
        """Called when entering a COVERINSTANCE scope."""
        pass

    def leave_cover_instance(self, cgi):
        """Called when leaving a COVERINSTANCE scope."""
        pass

    # --- Coverpoints and cross ---

    def visit_coverpoint(self, cp):
        """Called when entering a COVERPOINT scope."""
        pass

    def leave_coverpoint(self, cp):
        """Called when leaving a COVERPOINT scope."""
        pass

    def visit_cross(self, cross):
        """Called when entering a CROSS scope."""
        pass

    def leave_cross(self, cross):
        """Called when leaving a CROSS scope."""
        pass

    # --- Toggle and FSM ---

    def visit_toggle(self, toggle):
        """Called when entering a TOGGLE scope."""
        pass

    def leave_toggle(self, toggle):
        """Called when leaving a TOGGLE scope."""
        pass

    def visit_fsm(self, fsm):
        """Called when entering an FSM scope."""
        pass

    def leave_fsm(self, fsm):
        """Called when leaving an FSM scope."""
        pass

    # --- Assertion / cover property ---

    def visit_assert(self, assert_scope):
        """Called when entering an ASSERT scope."""
        pass

    def leave_assert(self, assert_scope):
        """Called when leaving an ASSERT scope."""
        pass

    def visit_cover_prop(self, cover_scope):
        """Called when entering a COVER (cover-property) scope."""
        pass

    def leave_cover_prop(self, cover_scope):
        """Called when leaving a COVER scope."""
        pass

    # --- Generic / other scopes ---

    def visit_scope(self, scope):
        """Called for scopes not matched by a specific visit_* method."""
        pass

    def leave_scope(self, scope):
        """Called for scopes not matched by a specific leave_* method."""
        pass

    # --- Cover items ---

    def visit_cover_item(self, idx):
        """Called for each cover item within a scope."""
        pass

    