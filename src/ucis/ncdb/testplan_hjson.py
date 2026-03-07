"""
src/ucis/ncdb/testplan_hjson.py — Import OpenTitan-style Hjson testplans.

The OpenTitan testplan format is a Hjson (human JSON) file with a ``testpoints``
list.  Each testpoint can have a ``tests`` list that uses ``{key}`` wildcards
expanded by cartesian product with a ``substitutions`` dict.  ``tests: ["N/A"]``
marks a testpoint as intentionally unmapped.

Falls back to standard ``json`` if the ``hjson`` package is not installed
(works for files that happen to be valid JSON or JSON-subset Hjson).
"""
from __future__ import annotations

import itertools
import os
import re
from typing import Dict, List, Optional

from .testplan import CovergroupEntry, Testplan, Testpoint

try:
    import hjson as _hjson
    _HJSON_AVAILABLE = True
except ImportError:
    import json as _hjson  # type: ignore[no-redef]
    _HJSON_AVAILABLE = False


# ── public API ────────────────────────────────────────────────────────────────

def import_hjson(hjson_path: str,
                 substitutions: Optional[Dict[str, object]] = None) -> Testplan:
    """Parse an OpenTitan-style Hjson testplan and return a :class:`~ucis.ncdb.testplan.Testplan`.

    Args:
        hjson_path:    Path to the ``.hjson`` (or ``.json``) file.
        substitutions: Optional dict of ``{key: value_or_list}`` pairs used
                       for wildcard expansion in test names.

    Returns:
        A fully expanded :class:`~ucis.ncdb.testplan.Testplan` with all
        ``{key}`` templates replaced.
    """
    subs = substitutions or {}
    with open(hjson_path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    if _HJSON_AVAILABLE:
        data = _hjson.loads(raw)
    else:
        import json
        data = json.loads(raw)

    plan = Testplan(source_file=os.path.abspath(hjson_path))

    for rec in data.get("testpoints", []):
        raw_tests = rec.get("tests", [])
        if raw_tests == ["N/A"]:
            plan.add_testpoint(Testpoint(
                name=rec.get("name", ""),
                stage=rec.get("stage", ""),
                desc=rec.get("desc", ""),
                tags=rec.get("tags", []),
                na=True,
                tests=[],
                source_template="",
            ))
            continue

        expanded: List[str] = []
        templates: List[str] = []
        for tmpl in raw_tests:
            results = _expand_template(tmpl, subs)
            expanded.extend(results)
            if len(results) > 1 or tmpl != results[0]:
                templates.append(tmpl)

        plan.add_testpoint(Testpoint(
            name=rec.get("name", ""),
            stage=rec.get("stage", ""),
            desc=rec.get("desc", ""),
            tags=rec.get("tags", []),
            na=False,
            tests=expanded,
            source_template=", ".join(templates),
        ))

    for rec in data.get("covergroups", []):
        plan.covergroups.append(CovergroupEntry(
            name=rec.get("name", ""),
            desc=rec.get("desc", ""),
        ))

    return plan


# ── internal helpers ──────────────────────────────────────────────────────────

def _expand_template(template: str,
                     subs: Dict[str, object]) -> List[str]:
    """Expand ``{key}`` placeholders in *template* using *subs*.

    Each ``{key}`` whose value in *subs* is a list produces multiple
    output strings (cartesian product).  Scalar values are substituted
    directly.  Keys absent from *subs* are left as-is.

    Examples::

        _expand_template("uart_{baud}_test", {"baud": ["9600", "115200"]})
        # → ["uart_9600_test", "uart_115200_test"]

        _expand_template("{mod}_{type}", {"mod": ["a", "b"], "type": "x"})
        # → ["a_x", "b_x"]
    """
    keys_found = re.findall(r'\{(\w+)\}', template)
    if not keys_found:
        return [template]

    # Build lists for each placeholder
    lists: List[List[str]] = []
    ordered_keys: List[str] = []
    for key in dict.fromkeys(keys_found):   # preserve order, deduplicate
        val = subs.get(key)
        if val is None:
            lists.append([f"{{{key}}}"])    # unknown key left verbatim
        elif isinstance(val, list):
            lists.append([str(v) for v in val])
        else:
            lists.append([str(val)])
        ordered_keys.append(key)

    results: List[str] = []
    for combo in itertools.product(*lists):
        s = template
        for key, replacement in zip(ordered_keys, combo):
            s = s.replace(f"{{{key}}}", replacement)
        results.append(s)
    return results


def _expand_tests(test_list: List[str],
                  subs: Dict[str, object]) -> List[str]:
    """Expand an entire ``tests`` list, returning the flat list of names."""
    result: List[str] = []
    for tmpl in test_list:
        result.extend(_expand_template(tmpl, subs))
    return result
