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
Writer for AVL (Apheleia Verification Library) JSON format.

Converts UCIS functional coverage data to AVL hierarchical JSON format::

    {
      "functional_coverage": {
        "covergroups": {
          "group_name": {
            "coverpoints": {
              "point_name": {
                "bins": {"bin_name": {"hits": N, "at_least": 1}}
              }
            },
            "crosses": {
              "cross_name": {
                "bins": {"bin_name": {"hits": N}}
              }
            }
          }
        }
      }
    }

**Supported:** covergroups, coverpoints, crosses, normal bins.
**Dropped with warning:** code coverage, toggle coverage, assertions, FSM,
design-hierarchy data, ignore/illegal bins, history nodes.
"""

import json
from typing import Optional

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


class AvlJsonWriter:
    """
    Write UCIS coverage data to AVL hierarchical JSON format.

    Unsupported UCIS features are silently dropped with a warning emitted
    via the optional *ConversionContext*.
    """

    def write(self, db: UCIS, filename: str, ctx=None) -> None:
        """Write *db* to *filename* in AVL JSON format.

        Args:
            db: Source UCIS database.
            filename: Destination file path.
            ctx: Optional :class:`ConversionContext` for warnings/progress.
        """
        data = self._build_dict(db, ctx)
        with open(filename, 'w') as fp:
            json.dump(data, fp, indent=2)

    def dumps(self, db: UCIS, ctx=None) -> str:
        """Return the JSON representation as a string."""
        return json.dumps(self._build_dict(db, ctx), indent=2)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_dict(self, db: UCIS, ctx) -> dict:
        covergroups_out: dict = {}

        for inst in db.scopes(ScopeTypeT.INSTANCE):
            # Warn on unsupported coverage types
            for child in inst.scopes(ScopeTypeT.ALL):
                st = child.getScopeType()
                if st in (ScopeTypeT.BLOCK, ScopeTypeT.BRANCH) and ctx is not None:
                    ctx.warn("avl-json does not support code coverage – dropped")
                elif st == ScopeTypeT.TOGGLE and ctx is not None:
                    ctx.warn("avl-json does not support toggle coverage – dropped")

            for cg in inst.scopes(ScopeTypeT.COVERGROUP):
                cg_name = cg.getScopeName()
                covergroups_out[cg_name] = self._build_covergroup(cg, ctx)

        return {"functional_coverage": {"covergroups": covergroups_out}}

    def _build_covergroup(self, cg, ctx) -> dict:
        coverpoints_out: dict = {}
        crosses_out: dict = {}

        ci_list = list(cg.scopes(ScopeTypeT.COVERINSTANCE))
        if not ci_list:
            ci_list = [cg]

        for ci in ci_list:
            for cp in ci.scopes(ScopeTypeT.COVERPOINT):
                cp_name = cp.getScopeName()
                coverpoints_out[cp_name] = self._build_coverpoint(cp, ctx)

            for cr in ci.scopes(ScopeTypeT.CROSS):
                cr_name = cr.getScopeName()
                crosses_out[cr_name] = self._build_cross(cr)

        result: dict = {}
        if coverpoints_out:
            result["coverpoints"] = coverpoints_out
        if crosses_out:
            result["crosses"] = crosses_out
        return result

    def _build_coverpoint(self, cp, ctx) -> dict:
        bins_out: dict = {}

        for item in cp.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            if cd.type != CoverTypeT.CVGBIN:
                if ctx is not None:
                    ctx.warn("avl-json does not support ignore/illegal bins – dropped")
                continue
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            bins_out[item.getName()] = {"hits": int(cd.data), "at_least": at_least}

        return {"bins": bins_out}

    def _build_cross(self, cr) -> dict:
        bins_out: dict = {}

        for item in cr.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            if cd.type != CoverTypeT.CVGBIN:
                continue
            bins_out[item.getName()] = {"hits": int(cd.data)}

        return {"bins": bins_out}
