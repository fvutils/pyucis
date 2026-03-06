"""Unit tests for BucketWriter / BucketReader (history/NNNNNN.bin)."""
import pytest
from ucis.ncdb.history_buckets import BucketWriter, BucketReader
from ucis.ncdb.constants import (
    HIST_STATUS_OK, HIST_STATUS_FAIL,
    HIST_FLAG_IS_RERUN, HIST_FLAG_HAS_COVERAGE,
    HISTORY_BUCKET_MAX_RECORDS,
)


def _bucket(*records):
    """Write records and return a BucketReader over them.

    Each record is a (name_id, seed_id, ts, status, flags) tuple.
    """
    w = BucketWriter()
    for name_id, seed_id, ts, status, flags in records:
        w.add(name_id, seed_id, ts, status, flags)
    return BucketReader(w.seal_fast())


def test_write_read_single_record():
    r = _bucket((0, 0, 1700000000, HIST_STATUS_OK, 0))
    assert r.num_records == 1
    recs = r.records_for_name(0)
    assert len(recs) == 1
    assert recs[0].ts == 1700000000
    assert recs[0].status == HIST_STATUS_OK
    assert recs[0].flags == 0


def test_name_index_binary_search():
    records = []
    for nid in range(20):
        for i in range(5):
            records.append((nid, 0, 1700000000 + nid * 1000 + i * 100, HIST_STATUS_OK, 0))
    r = _bucket(*records)
    for nid in range(20):
        found = r.records_for_name(nid)
        assert len(found) == 5, f"name_id {nid}: expected 5, got {len(found)}"


def test_records_for_name_not_present():
    r = _bucket((0, 0, 1700000000, HIST_STATUS_OK, 0))
    assert r.records_for_name(99) == []


def test_seed_dict_mapping():
    # Two different global seed_ids should map back correctly
    w = BucketWriter()
    w.add(0, 42, 1700000000, HIST_STATUS_OK, 0)
    w.add(0, 99, 1700000001, HIST_STATUS_OK, 0)
    r = BucketReader(w.seal_fast())
    recs = r.records_for_name(0)
    seed_ids = {rec.seed_id for rec in recs}
    assert seed_ids == {42, 99}


def test_ts_delta_encoding():
    base = 1700000000
    timestamps = [base, base + 100, base + 250, base + 1000]
    records = [(0, 0, ts, HIST_STATUS_OK, 0) for ts in timestamps]
    r = _bucket(*records)
    recs = r.records_for_name(0)
    recovered = sorted(rec.ts for rec in recs)
    assert recovered == timestamps


def test_status_flags_pack_unpack():
    """All status × flag combinations round-trip through the nibble-packed byte."""
    statuses = [HIST_STATUS_OK, HIST_STATUS_FAIL]
    flags_list = [0, HIST_FLAG_IS_RERUN, HIST_FLAG_HAS_COVERAGE,
                  HIST_FLAG_IS_RERUN | HIST_FLAG_HAS_COVERAGE]
    records = []
    ts = 1700000000
    for nid, (status, flags) in enumerate(
            (s, f) for s in statuses for f in flags_list):
        records.append((nid, 0, ts + nid * 100, status, flags))
    r = _bucket(*records)
    for nid, (status, flags) in enumerate(
            (s, f) for s in statuses for f in flags_list):
        recs = r.records_for_name(nid)
        assert len(recs) == 1
        assert recs[0].status == status, f"nid={nid} status mismatch"
        assert recs[0].flags  == flags,  f"nid={nid} flags mismatch"


def test_multiple_names_correct_counts():
    w = BucketWriter()
    for i in range(10):
        w.add(0, 0, 1700000000 + i * 100, HIST_STATUS_OK, 0)
    for i in range(5):
        w.add(1, 0, 1700001000 + i * 100, HIST_STATUS_FAIL, 0)
    r = BucketReader(w.seal_fast())
    assert r.num_records == 15
    assert len(r.records_for_name(0)) == 10
    assert len(r.records_for_name(1)) == 5


def test_seal_deflate():
    w = BucketWriter()
    for i in range(100):
        w.add(0, 0, 1700000000 + i * 100, HIST_STATUS_OK, 0)
    data = w.seal_fast()
    r = BucketReader(data)
    assert r.num_records == 100


def test_seal_lzma_or_fallback():
    """seal() should succeed regardless of liblzma availability."""
    w = BucketWriter()
    for i in range(100):
        w.add(0, 0, 1700000000 + i * 100, HIST_STATUS_OK, 0)
    data = w.seal(use_lzma=True)   # lzma or deflate fallback
    r = BucketReader(data)
    assert r.num_records == 100


def test_10k_records_compressed_size():
    """10K records should compress to ≤ 50 KB (well under 5 MB design target)."""
    w = BucketWriter()
    for i in range(HISTORY_BUCKET_MAX_RECORDS):
        name_id = i % 100
        w.add(name_id, 0, 1700000000 + i * 10, HIST_STATUS_OK, 0)
    data = w.seal_fast()
    assert len(data) < 50 * 1024, f"Bucket too large: {len(data)} bytes"


def test_all_records_iteration():
    w = BucketWriter()
    for nid in range(3):
        for i in range(4):
            w.add(nid, 0, 1700000000 + nid * 10000 + i * 100, HIST_STATUS_OK, 0)
    r = BucketReader(w.seal_fast())
    all_recs = list(r.all_records())
    assert len(all_recs) == 12


def test_is_full():
    w = BucketWriter()
    assert not w.is_full()
    for i in range(HISTORY_BUCKET_MAX_RECORDS):
        w.add(0, 0, 1700000000 + i, HIST_STATUS_OK, 0)
    assert w.is_full()
