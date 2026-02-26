"""
manifest.json — NCDB archive manifest.

Stores format identity, version, statistics, and the schema hash that
enables the same-schema fast-merge path.
"""

import hashlib
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

from .constants import NCDB_FORMAT, NCDB_VERSION, NCDB_GENERATOR


@dataclass
class Manifest:
    format:         str = NCDB_FORMAT
    version:        str = NCDB_VERSION
    ucis_version:   str = "1.0"
    created:        str = ""
    path_separator: str = "/"
    scope_count:    int = 0
    coveritem_count:int = 0
    test_count:     int = 0
    total_hits:     int = 0
    covered_bins:   int = 0
    schema_hash:    str = ""
    generator:      str = NCDB_GENERATOR

    def serialize(self) -> bytes:
        d = asdict(self)
        return json.dumps(d, indent=2).encode("utf-8")

    @classmethod
    def from_bytes(cls, data: bytes) -> "Manifest":
        d = json.loads(data.decode("utf-8"))
        m = cls()
        for k, v in d.items():
            if hasattr(m, k):
                setattr(m, k, v)
        return m

    @staticmethod
    def compute_schema_hash(scope_tree_bytes: bytes) -> str:
        """SHA-256 of the *uncompressed* scope_tree.bin content."""
        digest = hashlib.sha256(scope_tree_bytes).hexdigest()
        return f"sha256:{digest}"

    @classmethod
    def build(cls, db, scope_tree_bytes: bytes,
              counts: list, history_nodes: list) -> "Manifest":
        """Build a Manifest from a UCIS database and serialized members."""
        from ucis.scope_type_t import ScopeTypeT
        from ucis.cover_type_t import CoverTypeT

        total_hits   = sum(counts)
        covered_bins = sum(1 for c in counts if c > 0)

        # Count history TEST nodes
        from ucis.history_node_kind import HistoryNodeKind
        test_count = sum(
            1 for n in history_nodes
            if n.getKind() == HistoryNodeKind.TEST
        )

        return cls(
            created=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            path_separator=db.getPathSeparator()
                if hasattr(db, 'getPathSeparator') else "/",
            coveritem_count=len(counts),
            test_count=test_count,
            total_hits=total_hits,
            covered_bins=covered_bins,
            schema_hash=cls.compute_schema_hash(scope_tree_bytes),
        )
