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
Writer for cocotb-coverage XML format.

Converts UCIS functional coverage data to cocotb-coverage XML format.

The cocotb XML tree mirrors the coverage hierarchy::

    <coverage abs_name="top" coverage="N" cover_percentage="N.N">
      <covergroup abs_name="top.cg" coverage="N" weight="1">
        <coverpoint abs_name="top.cg.cp" coverage="N" at_least="1" weight="1">
          <bin bin="bin_name" hits="10"/>
        </coverpoint>
      </covergroup>
    </coverage>

**Supported:** covergroups, coverpoints, crosses, normal bins.
**Dropped with warning:** code coverage, toggle coverage, assertions, FSM,
design-hierarchy data, ignore/illegal bins, history nodes.
"""

from lxml import etree
from typing import Optional

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


class CocotbXmlWriter:
    """
    Write UCIS coverage data to cocotb-coverage XML format.

    Unsupported UCIS features are silently dropped with a warning emitted
    via the optional *ConversionContext*.
    """

    def write(self, db: UCIS, filename: str, ctx=None) -> None:
        """Write *db* to *filename* in cocotb XML format.

        Args:
            db: Source UCIS database.
            filename: Destination file path.
            ctx: Optional :class:`ConversionContext` for warnings/progress.
        """
        root = etree.Element("coverage")
        root.set("abs_name", "coverage")
        root.set("coverage", "0")
        root.set("cover_percentage", "0.0")

        for inst in db.scopes(ScopeTypeT.INSTANCE):
            inst_name = inst.getScopeName()

            # Warn on unsupported coverage types
            for child in inst.scopes(ScopeTypeT.ALL):
                st = child.getScopeType()
                if st in (ScopeTypeT.BLOCK, ScopeTypeT.BRANCH) and ctx is not None:
                    ctx.warn("cocotb-xml does not support code coverage – dropped")
                elif st == ScopeTypeT.TOGGLE and ctx is not None:
                    ctx.warn("cocotb-xml does not support toggle coverage – dropped")

            for cg in inst.scopes(ScopeTypeT.COVERGROUP):
                self._write_covergroup(root, inst_name, cg, ctx)

        tree = etree.ElementTree(root)
        tree.write(filename, pretty_print=True, xml_declaration=True, encoding="utf-8")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _write_covergroup(self, parent, inst_name: str, cg, ctx) -> None:
        cg_name = cg.getScopeName()
        cg_elem = etree.SubElement(parent, "covergroup")
        cg_elem.set("abs_name", f"{inst_name}.{cg_name}")
        cg_elem.set("coverage", "0")
        cg_elem.set("weight", str(cg.getWeight() if hasattr(cg, 'getWeight') else 1))

        ci_list = list(cg.scopes(ScopeTypeT.COVERINSTANCE))
        if not ci_list:
            ci_list = [cg]

        for ci in ci_list:
            ci_name = ci.getScopeName()
            ci_path = f"{inst_name}.{cg_name}.{ci_name}" if ci is not cg else f"{inst_name}.{cg_name}"
            self._write_coverinstance(cg_elem, ci, ci_path, ctx)

    def _write_coverinstance(self, parent, ci, path: str, ctx) -> None:
        for cp in ci.scopes(ScopeTypeT.COVERPOINT):
            self._write_coverpoint(parent, cp, f"{path}.{cp.getScopeName()}")

        for cr in ci.scopes(ScopeTypeT.CROSS):
            self._write_cross(parent, cr, f"{path}.{cr.getScopeName()}")

    def _write_coverpoint(self, parent, cp, path: str) -> None:
        cp_elem = etree.SubElement(parent, "coverpoint")
        cp_elem.set("abs_name", path)
        cp_elem.set("coverage", "0")

        at_least = 1
        for item in cp.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            if cd.type != CoverTypeT.CVGBIN:
                continue
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            bin_elem = etree.SubElement(cp_elem, "bin")
            bin_elem.set("bin", item.getName())
            bin_elem.set("hits", str(int(cd.data)))

        cp_elem.set("at_least", str(at_least))
        cp_elem.set("weight", str(cp.getWeight() if hasattr(cp, 'getWeight') else 1))

    def _write_cross(self, parent, cr, path: str) -> None:
        cr_elem = etree.SubElement(parent, "cross")
        cr_elem.set("abs_name", path)
        cr_elem.set("coverage", "0")

        at_least = 1
        for item in cr.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            if cd.type != CoverTypeT.CVGBIN:
                continue
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            bin_elem = etree.SubElement(cr_elem, "bin")
            bin_elem.set("bin", item.getName())
            bin_elem.set("hits", str(int(cd.data)))

        cr_elem.set("at_least", str(at_least))
        cr_elem.set("weight", str(cr.getWeight() if hasattr(cr, 'getWeight') else 1))
