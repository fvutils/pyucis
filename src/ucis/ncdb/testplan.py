"""
src/ucis/ncdb/testplan.py — Testplan data model for NCDB.

A ``Testplan`` describes the structured set of verification tasks (testpoints)
and functional-coverage groups expected for a design.  It may be embedded
inside a ``.cdb`` file as ``testplan.json`` (Mode A) or kept as a standalone
file (Mode B).  Either way the same ``Testplan`` object is used.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


# ── leaf types ────────────────────────────────────────────────────────────────

@dataclass
class RequirementLink:
    """Reference to an external requirement item (e.g. ALM/JIRA)."""
    system:  str = ""   # e.g. "ALM", "JIRA"
    project: str = ""   # e.g. "PROJ-X"
    item_id: str = ""   # e.g. "REQ-42"
    url:     str = ""   # optional direct URL


@dataclass
class CovergroupEntry:
    """One functional-coverage group expected to be exercised by the design."""
    name: str
    desc: str = ""


@dataclass
class Testpoint:
    """One verification task (maps to one or more test names)."""
    name:            str
    stage:           str              # "V1" | "V2" | "V2S" | "V3" | custom
    desc:            str = ""
    tests:           List[str] = field(default_factory=list)
    tags:            List[str] = field(default_factory=list)
    na:              bool = False     # tests: ["N/A"] — intentionally unmapped
    source_template: str = ""         # original wildcard template before expansion
    requirements:    List[RequirementLink] = field(default_factory=list)


# ── main class ────────────────────────────────────────────────────────────────

@dataclass
class Testplan:
    """Structured verification testplan.

    Attributes:
        format_version:   Schema version (currently 1).
        source_file:      Path to the source .hjson (informational only).
        import_timestamp: ISO-8601 UTC timestamp set when embedded in a .cdb.
        testpoints:       Ordered list of :class:`Testpoint` objects.
        covergroups:      Ordered list of :class:`CovergroupEntry` objects.
    """
    format_version:   int = 1
    source_file:      str = ""
    import_timestamp: str = ""

    testpoints:  List[Testpoint]      = field(default_factory=list)
    covergroups: List[CovergroupEntry] = field(default_factory=list)

    # ── in-memory indices (built lazily) ──────────────────────────────────
    _tp_by_name: dict = field(default_factory=dict, repr=False, compare=False)
    _tp_by_test: dict = field(default_factory=dict, repr=False, compare=False)
    _indexed:    bool = field(default=False,        repr=False, compare=False)

    # ── index building ────────────────────────────────────────────────────

    def _build_indices(self) -> None:
        self._tp_by_name.clear()
        self._tp_by_test.clear()
        for tp in self.testpoints:
            self._tp_by_name[tp.name] = tp
            for t in tp.tests:
                self._tp_by_test[t] = tp
        self._indexed = True

    def _ensure_indexed(self) -> None:
        if not self._indexed:
            self._build_indices()

    def _invalidate_index(self) -> None:
        self._indexed = False

    # ── public query API ──────────────────────────────────────────────────

    def getTestpoint(self, name: str) -> Optional[Testpoint]:
        """Return the testpoint with *name*, or ``None``."""
        self._ensure_indexed()
        return self._tp_by_name.get(name)

    def testpointForTest(self, test_name: str) -> Optional[Testpoint]:
        """Return the testpoint that owns *test_name*.

        Match order:

        1. **Exact** — ``test_name`` appears literally in ``testpoint.tests``.
        2. **Seed-suffix strip** — strip a trailing ``_\\d+`` (e.g.
           ``uart_smoke_42`` → ``uart_smoke``) and retry exact match.
        3. **Wildcard** — any ``testpoint.tests`` entry ending in ``_*``
           whose prefix matches ``test_name``.

        Returns ``None`` if no testpoint matches.
        """
        self._ensure_indexed()
        tp = self._tp_by_test.get(test_name)
        if tp is not None:
            return tp
        stripped = re.sub(r'_\d+$', '', test_name)
        if stripped != test_name:
            tp = self._tp_by_test.get(stripped)
            if tp is not None:
                return tp
        for pattern, candidate in self._tp_by_test.items():
            if pattern.endswith('_*') and test_name.startswith(pattern[:-1]):
                return candidate
        return None

    def testpointsForStage(self, stage: str) -> List[Testpoint]:
        """Return all testpoints targeting *stage* (e.g. ``"V2"``)."""
        return [tp for tp in self.testpoints if tp.stage == stage]

    def stages(self) -> List[str]:
        """Return the ordered unique stages present in the testplan."""
        _ORDER = {"V1": 0, "V2": 1, "V2S": 2, "V3": 3}
        seen = dict.fromkeys(tp.stage for tp in self.testpoints)
        return sorted(seen, key=lambda s: _ORDER.get(s, 99))

    def add_testpoint(self, tp: Testpoint) -> None:
        """Append *tp* and invalidate the lookup indices."""
        self.testpoints.append(tp)
        self._invalidate_index()

    # ── serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-serialisable dict representation."""
        return {
            "format_version":   self.format_version,
            "source_file":      self.source_file,
            "import_timestamp": self.import_timestamp,
            "testpoints": [
                {
                    "name":            tp.name,
                    "stage":           tp.stage,
                    "desc":            tp.desc,
                    "tests":           tp.tests,
                    "tags":            tp.tags,
                    "na":              tp.na,
                    "source_template": tp.source_template,
                    "requirements":    [
                        {"system": r.system, "project": r.project,
                         "item_id": r.item_id, "url": r.url}
                        for r in tp.requirements
                    ],
                }
                for tp in self.testpoints
            ],
            "covergroups": [
                {"name": cg.name, "desc": cg.desc}
                for cg in self.covergroups
            ],
        }

    def serialize(self) -> bytes:
        """Serialise to compact JSON bytes (for ZIP embedding)."""
        return json.dumps(self.to_dict(), separators=(',', ':')).encode()

    @classmethod
    def from_dict(cls, d: dict) -> "Testplan":
        """Reconstruct a :class:`Testplan` from a plain dict."""
        obj = cls(
            format_version=d.get("format_version", 1),
            source_file=d.get("source_file", ""),
            import_timestamp=d.get("import_timestamp", ""),
        )
        for rec in d.get("testpoints", []):
            reqs = [
                RequirementLink(
                    system=r.get("system", ""), project=r.get("project", ""),
                    item_id=r.get("item_id", ""), url=r.get("url", ""),
                )
                for r in rec.get("requirements", [])
            ]
            obj.testpoints.append(Testpoint(
                name=rec["name"],
                stage=rec.get("stage", ""),
                desc=rec.get("desc", ""),
                tests=rec.get("tests", []),
                tags=rec.get("tags", []),
                na=rec.get("na", False),
                source_template=rec.get("source_template", ""),
                requirements=reqs,
            ))
        for rec in d.get("covergroups", []):
            obj.covergroups.append(CovergroupEntry(
                name=rec["name"], desc=rec.get("desc", ""),
            ))
        return obj

    @classmethod
    def from_bytes(cls, data: bytes) -> "Testplan":
        """Reconstruct from JSON bytes (inverse of :meth:`serialize`)."""
        return cls.from_dict(json.loads(data.decode()))

    @classmethod
    def load(cls, path: str) -> "Testplan":
        """Load a testplan from a standalone JSON/hjson file (Mode B)."""
        with open(path, "rb") as f:
            return cls.from_bytes(f.read())

    def save(self, path: str) -> None:
        """Write this testplan to a standalone JSON file (Mode B)."""
        with open(path, "wb") as f:
            f.write(self.serialize())

    def stamp_import_time(self) -> None:
        """Set :attr:`import_timestamp` to the current UTC time."""
        self.import_timestamp = datetime.now(timezone.utc).isoformat()


# ── module-level helpers ──────────────────────────────────────────────────────

def get_testplan(db) -> Optional[Testplan]:
    """Retrieve testplan from any UCIS db object (NcdbUCIS or MemUCIS).

    Works with any object that has a ``getTestplan()`` method
    (e.g. :class:`~ucis.ncdb.ncdb_ucis.NcdbUCIS`) or a ``_testplan``
    attribute (e.g. a :class:`~ucis.mem.mem_ucis.MemUCIS` returned by
    :class:`~ucis.ncdb.ncdb_reader.NcdbReader`).
    """
    if hasattr(db, "getTestplan"):
        return db.getTestplan()
    return getattr(db, "_testplan", None)


def set_testplan(db, tp: Testplan) -> None:
    """Embed *tp* into *db*.

    Works with any object that has a ``setTestplan()`` method.
    """
    if hasattr(db, "setTestplan"):
        db.setTestplan(tp)
    else:
        raise TypeError(f"{type(db).__name__} does not support setTestplan()")
