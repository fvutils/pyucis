"""
contrib/ — per-test coverage contribution serialization.

Each history node with non-empty contributions gets one ZIP member:
    contrib/{history_idx}.bin

Binary layout of each member:
    num_entries : varint
    For each entry (sorted by bin_index, delta-encoded):
        delta_bin_index : varint   (bin_index - previous_bin_index)
        count           : varint

Delta encoding exploits spatial locality; entries must be in ascending
bin_index order.  The file is absent when the history node has no
contributions.

The ContribWriter produces a dict {member_name: bytes} for the ZIP writer.
The ContribReader reads all contrib/* members from the ZIP and calls
db.record_test_association() to populate db._per_test_data.
"""

import io

from .constants import MEMBER_CONTRIB_DIR
from .varint import encode_varint, decode_varint


class ContribWriter:
    """Serialize per-test contributions from MemUCIS._per_test_data."""

    def serialize(self, db) -> dict:
        """Return a dict of {member_name: bytes} for all history nodes with contributions.

        Returns an empty dict when no per-test data is present.
        """
        per_test = getattr(db, '_per_test_data', {})
        members = {}
        for hist_idx, bin_counts in per_test.items():
            if not bin_counts:
                continue
            sorted_entries = sorted(bin_counts.items())  # ascending bin_index
            buf = io.BytesIO()
            buf.write(encode_varint(len(sorted_entries)))
            prev_bin = 0
            for bin_idx, count in sorted_entries:
                buf.write(encode_varint(bin_idx - prev_bin))
                buf.write(encode_varint(count))
                prev_bin = bin_idx
            members[f"{MEMBER_CONTRIB_DIR}{hist_idx}.bin"] = buf.getvalue()
        return members


class ContribReader:
    """Deserialize per-test contributions and populate MemUCIS._per_test_data."""

    def apply(self, db, contrib_members: dict) -> None:
        """Read all contrib/*.bin members and call db.record_test_association().

        Args:
            db:              MemUCIS (or NcdbUCIS) instance to populate.
            contrib_members: Dict mapping member name → bytes for all
                             contrib/* entries extracted from the ZIP.
        """
        if not contrib_members:
            return

        for member_name, data in contrib_members.items():
            if not member_name.startswith(MEMBER_CONTRIB_DIR):
                continue
            # Parse history_idx from filename: "contrib/{idx}.bin"
            basename = member_name[len(MEMBER_CONTRIB_DIR):]
            try:
                hist_idx = int(basename.rstrip(".bin").split(".")[0])
            except ValueError:
                continue  # skip malformed names

            buf = data
            offset = 0
            num_entries, offset = decode_varint(buf, offset)
            prev_bin = 0
            for _ in range(num_entries):
                delta, offset = decode_varint(buf, offset)
                count, offset = decode_varint(buf, offset)
                bin_idx = prev_bin + delta
                db.record_test_association(hist_idx, bin_idx, count)
                prev_bin = bin_idx
