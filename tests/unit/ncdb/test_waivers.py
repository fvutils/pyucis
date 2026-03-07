"""Unit tests for src/ucis/ncdb/waivers.py."""
from __future__ import annotations

import pytest

from ucis.ncdb.waivers import Waiver, WaiverSet, _glob_match


# ── _glob_match ───────────────────────────────────────────────────────────────

class TestGlobMatch:
    def test_exact_match(self):
        assert _glob_match("foo/bar", "foo/bar")

    def test_exact_no_match(self):
        assert not _glob_match("foo/bar", "foo/baz")

    def test_single_star_matches_segment(self):
        assert _glob_match("foo/*/baz", "foo/bar/baz")

    def test_single_star_does_not_cross_slash(self):
        assert not _glob_match("foo/*/baz", "foo/x/y/baz")

    def test_double_star_crosses_segments(self):
        assert _glob_match("foo/**/baz", "foo/x/y/baz")

    def test_double_star_matches_zero_segments(self):
        assert _glob_match("foo/**/baz", "foo/baz")

    def test_trailing_single_star(self):
        assert _glob_match("scope/*", "scope/uart")
        assert not _glob_match("scope/*", "scope/uart/sub")

    def test_leading_double_star(self):
        assert _glob_match("**/uart", "top/mid/uart")


# ── Waiver ────────────────────────────────────────────────────────────────────

class TestWaiver:
    def test_matches_exact_scope(self):
        w = Waiver(id="W1", scope_pattern="top/uart", bin_pattern="*")
        assert w.matches("top/uart")

    def test_no_match_wrong_scope(self):
        w = Waiver(id="W1", scope_pattern="top/uart", bin_pattern="*")
        assert not w.matches("top/spi")

    def test_matches_with_bin_wildcard(self):
        w = Waiver(id="W1", scope_pattern="top/*", bin_pattern="*")
        assert w.matches("top/uart", "some_bin")

    def test_matches_specific_bin(self):
        w = Waiver(id="W1", scope_pattern="top/uart", bin_pattern="reset_bin")
        assert w.matches("top/uart", "reset_bin")
        assert not w.matches("top/uart", "other_bin")

    def test_glob_scope_pattern(self):
        w = Waiver(id="W1", scope_pattern="**/uart", bin_pattern="*")
        assert w.matches("top/mid/uart")
        assert not w.matches("top/spi")


# ── WaiverSet ─────────────────────────────────────────────────────────────────

class TestWaiverSet:
    def test_empty_no_match(self):
        ws = WaiverSet()
        assert not ws.matches_scope("any/scope")

    def test_add_and_match(self):
        ws = WaiverSet()
        ws.add(Waiver(id="W1", scope_pattern="top/uart"))
        assert ws.matches_scope("top/uart")

    def test_get_by_id(self):
        ws = WaiverSet()
        ws.add(Waiver(id="W1", scope_pattern="a"))
        ws.add(Waiver(id="W2", scope_pattern="b"))
        assert ws.get("W1").scope_pattern == "a"
        assert ws.get("W2").scope_pattern == "b"
        assert ws.get("W3") is None

    def test_active_at_excludes_expired(self):
        ws = WaiverSet([
            Waiver(id="W1", scope_pattern="a", expires_at="2024-01-01T00:00:00"),
            Waiver(id="W2", scope_pattern="b", expires_at="2030-01-01T00:00:00"),
        ])
        active = ws.active_at("2025-06-01T00:00:00")
        assert len(active.waivers) == 1
        assert active.waivers[0].id == "W2"

    def test_active_at_includes_never_expires(self):
        ws = WaiverSet([
            Waiver(id="W1", scope_pattern="a", expires_at=""),
        ])
        active = ws.active_at("9999-12-31T00:00:00")
        assert len(active.waivers) == 1

    def test_active_at_excludes_revoked(self):
        ws = WaiverSet([
            Waiver(id="W1", scope_pattern="a", status="revoked"),
        ])
        active = ws.active_at("2025-01-01T00:00:00")
        assert len(active.waivers) == 0

    def test_serialize_roundtrip(self):
        ws = WaiverSet([
            Waiver(id="W1", scope_pattern="top/uart", bin_pattern="reset_*",
                   rationale="Known issue", approver="eng",
                   approved_at="2025-01-01T00:00:00",
                   expires_at="2026-01-01T00:00:00",
                   status="active"),
        ])
        data = ws.serialize()
        ws2 = WaiverSet.from_bytes(data)
        assert len(ws2.waivers) == 1
        w = ws2.waivers[0]
        assert w.id == "W1"
        assert w.scope_pattern == "top/uart"
        assert w.bin_pattern == "reset_*"
        assert w.rationale == "Known issue"
        assert w.approver == "eng"
        assert w.expires_at == "2026-01-01T00:00:00"

    def test_save_and_load(self, tmp_path):
        ws = WaiverSet([Waiver(id="W1", scope_pattern="**")])
        path = str(tmp_path / "waivers.json")
        ws.save(path)
        ws2 = WaiverSet.load(path)
        assert len(ws2.waivers) == 1
        assert ws2.waivers[0].id == "W1"

    def test_from_dict_missing_optional_fields(self):
        d = {"waivers": [{"id": "W1", "scope_pattern": "a"}]}
        ws = WaiverSet.from_dict(d)
        w = ws.waivers[0]
        assert w.bin_pattern == "*"
        assert w.status == "active"
        assert w.expires_at == ""
