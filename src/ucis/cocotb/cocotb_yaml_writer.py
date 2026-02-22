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
Writer for cocotb-coverage YAML format.

Converts UCIS functional coverage data to cocotb-coverage flat YAML format.

cocotb-coverage YAML uses a flat dictionary with dot-separated paths::

    test.covergroup.coverpoint:
      at_least: 1
      bins:_hits:
        bin_name: 10
      weight: 1
      type: <class 'cocotb_coverage.coverage.CoverPoint'>

**Supported:** covergroups, coverpoints, crosses, normal bins.
**Dropped with warning:** code coverage, toggle coverage, assertions, FSM,
design-hierarchy data, ignore/illegal bins, history nodes.
"""

import yaml
from typing import Optional, List

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


class CocotbYamlWriter:
    """
    Write UCIS coverage data to cocotb-coverage YAML flat-dictionary format.

    Unsupported UCIS features are silently dropped with a warning emitted
    via the optional *ConversionContext*.
    """

    def write(self, db: UCIS, filename: str, ctx=None) -> None:
        """Write *db* to *filename* in cocotb YAML format.

        Args:
            db: Source UCIS database.
            filename: Destination file path.
            ctx: Optional :class:`ConversionContext` for warnings/progress.
        """
        data = self._build_dict(db, ctx)
        with open(filename, 'w') as fp:
            yaml.dump(data, fp, default_flow_style=False, allow_unicode=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_dict(self, db: UCIS, ctx) -> dict:
        out: dict = {}

        for inst in db.scopes(ScopeTypeT.INSTANCE):
            inst_name = inst.getScopeName()

            # Warn on non-functional coverage children
            for child in inst.scopes(ScopeTypeT.ALL):
                st = child.getScopeType()
                if st in (ScopeTypeT.BLOCK, ScopeTypeT.BRANCH) and ctx is not None:
                    ctx.warn("cocotb-yaml does not support code coverage – dropped")
                elif st == ScopeTypeT.TOGGLE and ctx is not None:
                    ctx.warn("cocotb-yaml does not support toggle coverage – dropped")

            for cg in inst.scopes(ScopeTypeT.COVERGROUP):
                cg_name = cg.getScopeName()
                cg_path = f"{inst_name}.{cg_name}"

                # CG-level entry
                out[cg_path] = {
                    "weight": cg.getWeight() if hasattr(cg, 'getWeight') else 1,
                    "type": "<class 'cocotb_coverage.coverage.CoverageGroup'>",
                }

                # Prefer COVERINSTANCE children; fall back to CG itself
                ci_list = list(cg.scopes(ScopeTypeT.COVERINSTANCE))
                if not ci_list:
                    ci_list = [cg]

                for ci in ci_list:
                    ci_name = ci.getScopeName()
                    ci_path = f"{cg_path}.{ci_name}" if ci is not cg else cg_path
                    self._write_coverinstance(out, ci, ci_path, ctx)

        return out

    def _write_coverinstance(self, out: dict, ci, path: str, ctx) -> None:
        for cp in ci.scopes(ScopeTypeT.COVERPOINT):
            cp_name = cp.getScopeName()
            cp_path = f"{path}.{cp_name}"
            self._write_coverpoint(out, cp, cp_path)

        for cr in ci.scopes(ScopeTypeT.CROSS):
            cr_name = cr.getScopeName()
            cr_path = f"{path}.{cr_name}"
            self._write_cross(out, cr, cr_path)

    def _write_coverpoint(self, out: dict, cp, path: str) -> None:
        bins_hits: dict = {}
        at_least = 1

        for item in cp.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            if cd.type != CoverTypeT.CVGBIN:
                continue  # ignore/illegal bins not representable in cocotb format
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            bins_hits[item.getName()] = int(cd.data)

        out[path] = {
            "at_least": at_least,
            "bins:_hits": bins_hits,
            "weight": cp.getWeight() if hasattr(cp, 'getWeight') else 1,
            "type": "<class 'cocotb_coverage.coverage.CoverPoint'>",
        }

    def _write_cross(self, out: dict, cr, path: str) -> None:
        bins_hits: dict = {}
        at_least = 1

        for item in cr.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            if cd.type != CoverTypeT.CVGBIN:
                continue
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            bins_hits[item.getName()] = int(cd.data)

        out[path] = {
            "at_least": at_least,
            "bins:_hits": bins_hits,
            "weight": cr.getWeight() if hasattr(cr, 'getWeight') else 1,
            "type": "<class 'cocotb_coverage.coverage.CoverCross'>",
        }
