"""Unit tests for BucketIndex (history/bucket_index.bin)."""
import pytest
from ucis.ncdb.bucket_index import BucketIndex


def _idx(*buckets):
    """Build a BucketIndex from (seq, ts_start, ts_end, records, fails, min_nid, max_nid)."""
    idx = BucketIndex()
    for seq, ts_start, ts_end, records, fails, min_nid, max_nid in buckets:
        idx.add_bucket(seq, ts_start, ts_end, records, fails, min_nid, max_nid)
    return idx


def test_add_and_query_range():
    idx = _idx(
        (0, 1000, 1999, 100, 10, 0, 5),
        (1, 2000, 2999, 200,  5, 0, 7),
        (2, 3000, 3999,  50,  0, 3, 9),
    )
    hits = idx.buckets_in_range(1500, 2500)
    seqs = [e.bucket_seq for e in hits]
    assert 0 in seqs and 1 in seqs and 2 not in seqs


def test_buckets_for_name():
    idx = _idx(
        (0, 1000, 1999, 100, 10, 0, 5),
        (1, 2000, 2999, 200,  5, 6, 9),
    )
    # name_id=3 is in bucket 0 only
    hits = idx.buckets_for_name(3)
    assert len(hits) == 1 and hits[0].bucket_seq == 0

    # name_id=7 is in bucket 1 only
    hits = idx.buckets_for_name(7)
    assert len(hits) == 1 and hits[0].bucket_seq == 1

    # name_id=10 is in neither
    assert idx.buckets_for_name(10) == []


def test_buckets_for_name_with_time_filter():
    idx = _idx(
        (0, 1000, 1999, 100, 0, 0, 9),
        (1, 2000, 2999, 100, 0, 0, 9),
    )
    hits = idx.buckets_for_name(5, ts_from=2000)
    assert len(hits) == 1 and hits[0].bucket_seq == 1


def test_pass_rate_series():
    idx = _idx(
        (0, 1000, 1999, 100, 10, 0, 5),
        (1, 2000, 2999, 200,  0, 0, 5),
    )
    series = idx.pass_rate_series()
    assert len(series) == 2
    ts0, rate0 = series[0]
    ts1, rate1 = series[1]
    assert ts0 == 1000
    assert abs(rate0 - 0.90) < 1e-6
    assert abs(rate1 - 1.00) < 1e-6


def test_serialize_deserialize_empty():
    idx = BucketIndex()
    idx2 = BucketIndex.deserialize(idx.serialize())
    assert idx2.num_buckets == 0


def test_serialize_deserialize_multiple():
    idx = _idx(
        (0, 1000, 1999, 100, 10, 0, 5),
        (1, 2000, 2999, 200,  5, 0, 7),
    )
    data = idx.serialize()
    idx2 = BucketIndex.deserialize(data)
    assert idx2.num_buckets == 2
    e = idx2.buckets_in_range(1000, 1999)
    assert len(e) == 1 and e[0].fail_count == 10


def test_serialize_3650_entries_size():
    """10 years of buckets (one per day) should be well under 200 KB."""
    idx = BucketIndex()
    for i in range(3650):
        idx.add_bucket(i, 1700000000 + i * 86400, 1700000000 + (i + 1) * 86400 - 1,
                       10000, 100, 0, 999)
    data = idx.serialize()
    assert len(data) < 200 * 1024, f"Index too large: {len(data)} bytes"


def test_next_seq():
    idx = BucketIndex()
    assert idx.next_seq() == 0
    idx.add_bucket(0, 1000, 1999, 100, 0, 0, 0)
    assert idx.next_seq() == 1
    idx.add_bucket(1, 2000, 2999, 100, 0, 0, 0)
    assert idx.next_seq() == 2


def test_add_bucket_replaces_existing():
    idx = BucketIndex()
    idx.add_bucket(0, 1000, 1999, 100, 10, 0, 5)
    idx.add_bucket(0, 1000, 1999, 200, 20, 0, 5)   # update same seq
    assert idx.num_buckets == 1
    assert idx._entries[0].num_records == 200


def test_bad_magic_raises():
    data = b"\x00\x00\x00\x00" + b"\x00" * 8
    with pytest.raises(ValueError, match="Bad magic"):
        BucketIndex.deserialize(data)
