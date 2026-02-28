"""
sources.json — source file table serialization.

JSON array mapping integer IDs to file paths.  The order of entries
matches the file IDs used in scope_tree.bin source references.
"""

import json
from ucis.mem.mem_file_handle import MemFileHandle


class SourcesWriter:
    """Serialize source file handles to sources.json bytes."""

    def serialize(self, file_handles) -> bytes:
        records = []
        for fh in file_handles:
            records.append(fh.getFileName())
        return json.dumps(records, indent=2).encode("utf-8")


class SourcesReader:
    """Deserialize source file handles from sources.json bytes."""

    def deserialize(self, data: bytes) -> list:
        records = json.loads(data.decode("utf-8"))
        handles = []
        for filename in records:
            handles.append(MemFileHandle(filename))
        return handles
