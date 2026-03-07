"""
src/ucis/ncdb/waivers.py — Coverage and test-failure waivers.

A :class:`WaiverSet` contains zero or more :class:`Waiver` objects.  Each
waiver suppresses a known failure or uncovered bin so that reports distinguish
*known* issues from new regressions.

Waivers are stored as ``waivers.json`` inside the NCDB ZIP (optional member)
or as a standalone JSON file.

Expiry enforcement is the **caller's responsibility** — :meth:`WaiverSet.matches`
performs only pattern matching.  To filter out expired waivers call
:meth:`WaiverSet.active_at` first.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Waiver:
    """A single waiver entry.

    Attributes:
        id:            Unique identifier (e.g. ``"W-001"``).
        scope_pattern: Glob-style pattern matched against UCIS scope paths.
                       ``*`` matches any single path segment; ``**`` matches
                       any number of segments.
        bin_pattern:   Glob-style pattern matched against bin names within the
                       matched scope.  Use ``"*"`` to waive the entire scope.
        rationale:     Human-readable explanation.
        approver:      Name/username of approver.
        approved_at:   ISO-8601 UTC timestamp of approval.
        expires_at:    ISO-8601 UTC timestamp after which this waiver expires.
                       Empty string means "never expires".
        status:        ``"active"`` | ``"expired"`` | ``"revoked"``.
    """
    id:            str
    scope_pattern: str
    bin_pattern:   str = "*"
    rationale:     str = ""
    approver:      str = ""
    approved_at:   str = ""
    expires_at:    str = ""
    status:        str = "active"

    def matches(self, scope_path: str, bin_name: str = "") -> bool:
        """Return True if this waiver covers *scope_path* / *bin_name*.

        Pattern matching uses simple glob rules:
        - ``*`` matches any characters within a single ``/``-delimited segment.
        - ``**`` matches any number of segments (including zero).

        Expiry is **not** checked here — use :meth:`WaiverSet.active_at` first
        if you want to exclude expired waivers.
        """
        if not _glob_match(self.scope_pattern, scope_path):
            return False
        if bin_name and self.bin_pattern != "*":
            return _glob_match(self.bin_pattern, bin_name)
        return True


class WaiverSet:
    """Collection of :class:`Waiver` objects.

    Attributes:
        waivers: Ordered list of waivers.
    """

    def __init__(self, waivers: Optional[List[Waiver]] = None) -> None:
        self.waivers: List[Waiver] = waivers or []

    def add(self, waiver: Waiver) -> None:
        """Append *waiver* to the set."""
        self.waivers.append(waiver)

    def matches_scope(self, scope_path: str, bin_name: str = "") -> bool:
        """Return True if any waiver covers *scope_path* / *bin_name*."""
        return any(w.matches(scope_path, bin_name) for w in self.waivers)

    def active_at(self, timestamp: str) -> "WaiverSet":
        """Return a new :class:`WaiverSet` containing only waivers that are
        active at *timestamp* (ISO-8601 string).

        A waiver is active when:

        * ``status == "active"``
        * ``expires_at`` is empty OR ``expires_at > timestamp``
        """
        active = [
            w for w in self.waivers
            if w.status == "active" and
               (not w.expires_at or w.expires_at > timestamp)
        ]
        return WaiverSet(active)

    def get(self, waiver_id: str) -> Optional[Waiver]:
        """Return the waiver with *waiver_id*, or ``None``."""
        for w in self.waivers:
            if w.id == waiver_id:
                return w
        return None

    # ── serialization ─────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "format_version": 1,
            "waivers": [
                {
                    "id":            w.id,
                    "scope_pattern": w.scope_pattern,
                    "bin_pattern":   w.bin_pattern,
                    "rationale":     w.rationale,
                    "approver":      w.approver,
                    "approved_at":   w.approved_at,
                    "expires_at":    w.expires_at,
                    "status":        w.status,
                }
                for w in self.waivers
            ],
        }

    def serialize(self) -> bytes:
        """Serialise to compact JSON bytes (for ZIP embedding)."""
        return json.dumps(self.to_dict(), separators=(',', ':')).encode()

    @classmethod
    def from_dict(cls, d: dict) -> "WaiverSet":
        ws = cls()
        for rec in d.get("waivers", []):
            ws.add(Waiver(
                id=rec["id"],
                scope_pattern=rec.get("scope_pattern", "**"),
                bin_pattern=rec.get("bin_pattern", "*"),
                rationale=rec.get("rationale", ""),
                approver=rec.get("approver", ""),
                approved_at=rec.get("approved_at", ""),
                expires_at=rec.get("expires_at", ""),
                status=rec.get("status", "active"),
            ))
        return ws

    @classmethod
    def from_bytes(cls, data: bytes) -> "WaiverSet":
        return cls.from_dict(json.loads(data.decode()))

    @classmethod
    def load(cls, path: str) -> "WaiverSet":
        """Load from a standalone JSON file."""
        with open(path, "rb") as f:
            return cls.from_bytes(f.read())

    def save(self, path: str) -> None:
        """Write to a standalone JSON file."""
        with open(path, "wb") as f:
            f.write(self.serialize())


# ── glob matching helper ──────────────────────────────────────────────────────

def _glob_match(pattern: str, text: str) -> bool:
    """Simple glob match: ``*`` = single-segment wildcard, ``**`` = multi-segment."""
    import fnmatch
    # Replace '**' with a temporary token, expand, then match
    # Use fnmatch with '**' expanded to match any path
    # Strategy: convert glob to regex
    import re
    regex = _glob_to_regex(pattern)
    return bool(re.fullmatch(regex, text))


def _glob_to_regex(pattern: str) -> str:
    """Convert a glob pattern to a regex string."""
    import re
    # Parse pattern left-to-right, emitting regex pieces
    result = []
    i = 0
    while i < len(pattern):
        if pattern[i:i+3] == '**/':
            result.append('(?:.+/)?')
            i += 3
        elif pattern[i:i+2] == '**':
            result.append('.*')
            i += 2
        elif pattern[i] == '*':
            result.append('[^/]*')
            i += 1
        else:
            result.append(re.escape(pattern[i]))
            i += 1
    return ''.join(result)
