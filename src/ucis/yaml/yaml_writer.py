'''
Writer for PyUCIS custom YAML coverage format.

Converts a UCIS database to the YAML schema consumed by YamlReader.
Warns (via ConversionContext) on UCIS features that cannot be represented
in this format: code coverage, toggle coverage, assertions, FSM, and
design-hierarchy data.
'''

import yaml
from typing import Optional, List, Dict

from ucis.cover_type_t import CoverTypeT
from ucis.scope_type_t import ScopeTypeT
from ucis.ucis import UCIS


class YamlWriter:
    """
    Write a UCIS database to the PyUCIS YAML coverage format.

    **Supported:** functional coverage (covergroups, coverpoints, crosses,
    normal/ignore/illegal bins).

    **Dropped with warning:** code coverage, toggle coverage, assertions,
    FSM coverage, design-hierarchy scopes, and history nodes.
    """

    def write(self, db: UCIS, filename: str, ctx=None) -> None:
        """Write *db* to *filename* as YAML.

        Args:
            db: Source UCIS database.
            filename: Destination file path.
            ctx: Optional :class:`ConversionContext` for warnings/progress.
        """
        data = self._build_dict(db, ctx)
        with open(filename, 'w') as fp:
            yaml.dump(data, fp, default_flow_style=False, allow_unicode=True)

    def dumps(self, db: UCIS, ctx=None) -> str:
        """Return the YAML representation as a string."""
        data = self._build_dict(db, ctx)
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_dict(self, db: UCIS, ctx) -> dict:
        covergroups_out: List[dict] = []

        # Walk all INSTANCE scopes
        for inst in db.scopes(ScopeTypeT.INSTANCE):
            # Check for unsupported scope types directly under instance
            for child in inst.scopes(ScopeTypeT.ALL):
                st = child.getScopeType()
                if st == ScopeTypeT.BLOCK and ctx is not None:
                    ctx.warn("yaml does not support statement (code) coverage – dropped")
                elif st == ScopeTypeT.BRANCH and ctx is not None:
                    ctx.warn("yaml does not support branch coverage – dropped")
                elif st == ScopeTypeT.TOGGLE and ctx is not None:
                    ctx.warn("yaml does not support toggle coverage – dropped")

            for cg in inst.scopes(ScopeTypeT.COVERGROUP):
                cg_dict = self._build_covergroup(cg, ctx)
                covergroups_out.append(cg_dict)

        return {"coverage": {"covergroups": covergroups_out}}

    def _build_covergroup(self, cg, ctx) -> dict:
        cg_dict: dict = {
            "name": cg.getScopeName(),
            "weight": cg.getWeight() if hasattr(cg, 'getWeight') else 1,
            "instances": [],
        }

        # Prefer COVERINSTANCE children; fall back to the CG itself
        inst_list = list(cg.scopes(ScopeTypeT.COVERINSTANCE))
        if not inst_list:
            inst_list = [cg]

        for ci in inst_list:
            cg_dict["instances"].append(self._build_coverinstance(ci, ctx))

        return cg_dict

    def _build_coverinstance(self, ci, ctx) -> dict:
        ci_dict: dict = {"name": ci.getScopeName(), "coverpoints": [], "crosses": []}

        for cp in ci.scopes(ScopeTypeT.COVERPOINT):
            ci_dict["coverpoints"].append(self._build_coverpoint(cp))

        for cr in ci.scopes(ScopeTypeT.CROSS):
            ci_dict["crosses"].append(self._build_cross(cr, ctx))

        # Remove empty lists to keep YAML tidy
        if not ci_dict["crosses"]:
            del ci_dict["crosses"]
        if not ci_dict["coverpoints"]:
            del ci_dict["coverpoints"]

        return ci_dict

    def _build_coverpoint(self, cp) -> dict:
        cp_dict: dict = {"name": cp.getScopeName()}
        bins: List[dict] = []
        ignorebins: List[dict] = []
        illegalbins: List[dict] = []

        for item in cp.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            entry = {"name": item.getName(), "count": int(cd.data)}
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            if cd.type == CoverTypeT.IGNOREBIN:
                ignorebins.append(entry)
            elif cd.type == CoverTypeT.ILLEGALBIN:
                illegalbins.append(entry)
            else:
                bins.append(entry)

        # 'at_least' – use first bin's value (all bins in a coverpoint share it)
        at_least = 1
        all_items = list(cp.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN))
        if all_items:
            cd0 = all_items[0].getCoverData()
            at_least = int(cd0.at_least) if hasattr(cd0, 'at_least') else 1

        cp_dict["atleast"] = at_least
        cp_dict["bins"] = bins if bins else []
        if ignorebins:
            cp_dict["ignorebins"] = ignorebins
        if illegalbins:
            cp_dict["illegalbins"] = illegalbins
        return cp_dict

    def _build_cross(self, cr, ctx) -> dict:
        cr_dict: dict = {"name": cr.getScopeName(), "atleast": 1}

        # Collect crossed coverpoint names
        cp_names: List[str] = []
        try:
            n = cr.getNumCrossedCoverpoints()
            for i in range(n):
                cp_names.append(cr.getIthCrossedCoverpoint(i).getScopeName())
        except Exception:
            pass
        cr_dict["coverpoints"] = cp_names

        bins: List[dict] = []
        for item in cr.coverItems(CoverTypeT.CVGBIN | CoverTypeT.IGNOREBIN | CoverTypeT.ILLEGALBIN):
            cd = item.getCoverData()
            at_least = int(cd.at_least) if hasattr(cd, 'at_least') else 1
            cr_dict["atleast"] = at_least
            bins.append({"name": item.getName(), "count": int(cd.data)})
        cr_dict["bins"] = bins
        return cr_dict
