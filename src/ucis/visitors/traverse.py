# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Traverse a UCIS database, invoking visitor callbacks.

Usage::

    from ucis.visitors.UCISVisitor import UCISVisitor
    from ucis.visitors.traverse import traverse

    class MyVisitor(UCISVisitor):
        def visit_instance(self, inst):
            print("instance:", inst.getScopeName())

    traverse(db, MyVisitor())
"""

from ucis.scope_type_t import ScopeTypeT
from ucis.cover_type_t import CoverTypeT


def traverse(db, visitor):
    """Walk a UCIS database depth-first, calling visitor callbacks.

    Args:
        db: A UCIS database (MemUcis, SqliteUCIS, or read-back equivalent).
        visitor: An instance of UCISVisitor (or subclass).
    """
    visitor.visit_db(db)

    # History nodes
    from ucis import UCIS_HISTORYNODE_TEST
    for node in db.historyNodes(UCIS_HISTORYNODE_TEST):
        visitor.visit_history_node(node)

    # Top-level scopes
    for scope in db.scopes(ScopeTypeT.ALL):
        _traverse_scope(scope, visitor)

    visitor.leave_db(db)


def _traverse_scope(scope, visitor):
    """Recursively traverse a scope, dispatching to the right visitor method."""
    scope_type = scope.getScopeType()

    if ScopeTypeT.DU_ANY(scope_type):
        visitor.visit_du_scope(scope)
        _traverse_children(scope, visitor)
        visitor.leave_du_scope(scope)

    elif scope_type == ScopeTypeT.INSTANCE:
        visitor.visit_instance(scope)
        _traverse_cover_items(scope, visitor)
        _traverse_children(scope, visitor)
        visitor.leave_instance(scope)

    elif scope_type == ScopeTypeT.COVERGROUP:
        visitor.visit_covergroup(scope)
        _traverse_children(scope, visitor)
        visitor.leave_covergroup(scope)

    elif scope_type == ScopeTypeT.COVERINSTANCE:
        visitor.visit_cover_instance(scope)
        _traverse_children(scope, visitor)
        visitor.leave_cover_instance(scope)

    elif scope_type == ScopeTypeT.COVERPOINT:
        visitor.visit_coverpoint(scope)
        _traverse_cover_items(scope, visitor)
        _traverse_children(scope, visitor)
        visitor.leave_coverpoint(scope)

    elif scope_type == ScopeTypeT.CROSS:
        visitor.visit_cross(scope)
        _traverse_cover_items(scope, visitor)
        _traverse_children(scope, visitor)
        visitor.leave_cross(scope)

    elif scope_type == ScopeTypeT.TOGGLE:
        visitor.visit_toggle(scope)
        _traverse_cover_items(scope, visitor)
        visitor.leave_toggle(scope)

    elif scope_type == ScopeTypeT.FSM:
        visitor.visit_fsm(scope)
        _traverse_children(scope, visitor)
        visitor.leave_fsm(scope)

    elif scope_type == ScopeTypeT.ASSERT:
        visitor.visit_assert(scope)
        _traverse_cover_items(scope, visitor)
        _traverse_children(scope, visitor)
        visitor.leave_assert(scope)

    elif scope_type == ScopeTypeT.COVER:
        visitor.visit_cover_prop(scope)
        _traverse_cover_items(scope, visitor)
        _traverse_children(scope, visitor)
        visitor.leave_cover_prop(scope)

    else:
        visitor.visit_scope(scope)
        _traverse_cover_items(scope, visitor)
        _traverse_children(scope, visitor)
        visitor.leave_scope(scope)


def _traverse_children(scope, visitor):
    """Traverse all child scopes."""
    try:
        for child in scope.scopes(ScopeTypeT.ALL):
            _traverse_scope(child, visitor)
    except (AttributeError, TypeError):
        pass


def _traverse_cover_items(scope, visitor):
    """Traverse all cover items on a scope."""
    try:
        for item in scope.coverItems(CoverTypeT.ALL):
            visitor.visit_cover_item(item)
    except (AttributeError, TypeError):
        pass
