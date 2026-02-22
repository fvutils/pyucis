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
Writer for Verilator SystemC::Coverage-3 (.dat) format.

Converts UCIS code coverage (statement, branch) and toggle coverage data
back to the compact Verilator .dat format::

    # SystemC::Coverage-3
    C '\x01t\x02line\x01f\x02file.v\x01l\x0210\x01h\x02top\x01' 1

**Supported:** statement (line) coverage, branch coverage, toggle coverage.
**Dropped with warning:** functional coverage (covergroups/points/cross),
assertions, FSM, and history nodes.
"""

from typing import Optional

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


_SEP_KEY = '\x01'   # Start of key
_SEP_VAL = '\x02'   # Separator between key and value


def _encode(attrs: dict) -> str:
    """Encode a dict of attributes into Verilator compact string."""
    parts = []
    for key, value in attrs.items():
        parts.append(f"{_SEP_KEY}{key}{_SEP_VAL}{value}")
    parts.append(_SEP_KEY)
    return ''.join(parts)


def _format_line(attrs: dict, hit_count: int) -> str:
    return f"C '{_encode(attrs)}' {hit_count}"


class VltCovWriter:
    """
    Write UCIS code/toggle coverage data to Verilator .dat format.

    Unsupported UCIS features (functional coverage, assertions) are silently
    dropped with a warning emitted via the optional *ConversionContext*.
    """

    def write(self, db: UCIS, filename: str, ctx=None) -> None:
        """Write *db* to *filename* in Verilator .dat format.

        Args:
            db: Source UCIS database.
            filename: Destination file path.
            ctx: Optional :class:`ConversionContext` for warnings/progress.
        """
        lines = self._build_lines(db, ctx)
        with open(filename, 'w') as fp:
            fp.write("# SystemC::Coverage-3\n")
            for line in lines:
                fp.write(line + "\n")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_lines(self, db: UCIS, ctx) -> list:
        out_lines = []

        for inst in db.scopes(ScopeTypeT.INSTANCE):
            inst_name = inst.getScopeName()
            self._walk_scope(inst, inst_name, out_lines, ctx)

        return out_lines

    def _walk_scope(self, scope, hier: str, out_lines: list, ctx) -> None:
        """Recursively walk the scope tree extracting coverage items."""
        st = scope.getScopeType()

        if st == ScopeTypeT.COVERGROUP:
            if ctx is not None:
                ctx.warn("vltcov does not support functional coverage (covergroups) – dropped")
            return  # Don't recurse into CGs

        if st == ScopeTypeT.BLOCK:
            self._write_block(scope, hier, out_lines)
            return

        if st == ScopeTypeT.BRANCH:
            self._write_branch(scope, hier, out_lines)
            return

        if st == ScopeTypeT.TOGGLE:
            self._write_toggle(scope, hier, out_lines)
            return

        # Recurse into child scopes (INSTANCE, DU_MODULE, etc.)
        for child in scope.scopes(ScopeTypeT.ALL):
            child_name = child.getScopeName()
            child_hier = f"{hier}.{child_name}" if hier else child_name
            self._walk_scope(child, child_hier, out_lines, ctx)

    def _get_srcinfo(self, item) -> tuple:
        """Extract (filename, lineno) from a cover item's source info."""
        filename = ""
        lineno = 0
        try:
            srcinfo = item.getSourceInfo()
            if srcinfo is not None:
                fh = srcinfo.file
                if fh is not None:
                    if isinstance(fh, str):
                        filename = fh
                    elif hasattr(fh, 'getFileName'):
                        filename = fh.getFileName() or ""
                    elif hasattr(fh, 'filename'):
                        filename = fh.filename or ""
                lineno = srcinfo.line if hasattr(srcinfo, 'line') else 0
        except Exception:
            pass
        return filename, lineno

    def _write_block(self, scope, hier: str, out_lines: list) -> None:
        """Write statement (line) coverage items."""
        for item in scope.coverItems(CoverTypeT.STMTBIN):
            cd = item.getCoverData()
            filename, lineno = self._get_srcinfo(item)
            attrs = {
                "t": "line",
                "page": "v_line",
                "f": filename,
                "l": str(lineno),
                "h": hier,
                "o": item.getName(),
            }
            out_lines.append(_format_line(attrs, int(cd.data)))

    def _write_branch(self, scope, hier: str, out_lines: list) -> None:
        """Write branch coverage items."""
        for item in scope.coverItems(CoverTypeT.BRANCHBIN):
            cd = item.getCoverData()
            filename, lineno = self._get_srcinfo(item)
            attrs = {
                "t": "branch",
                "page": "v_branch",
                "f": filename,
                "l": str(lineno),
                "h": hier,
                "o": item.getName(),
            }
            out_lines.append(_format_line(attrs, int(cd.data)))

    def _write_toggle(self, scope, hier: str, out_lines: list) -> None:
        """Write toggle coverage items."""
        for item in scope.coverItems(CoverTypeT.TOGGLEBIN):
            cd = item.getCoverData()
            filename, lineno = self._get_srcinfo(item)
            attrs = {
                "t": "toggle",
                "page": "v_toggle",
                "f": filename,
                "l": str(lineno),
                "h": hier,
                "o": item.getName(),
            }
            out_lines.append(_format_line(attrs, int(cd.data)))
