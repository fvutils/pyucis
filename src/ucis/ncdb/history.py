"""
history.json — test and merge history serialization.

JSON array of history node records.  Each record encodes the fields
available via the MemHistoryNode API.
"""

import json
from ucis.mem.mem_history_node import MemHistoryNode
from ucis.history_node_kind import HistoryNodeKind
from ucis.test_status_t import TestStatusT


def _kind_to_str(kind) -> str:
    if kind is None:
        return "TEST"
    if isinstance(kind, HistoryNodeKind):
        return kind.name
    # SQLite backend may return bare int
    try:
        return HistoryNodeKind(int(kind)).name
    except (ValueError, TypeError):
        return "TEST"


def _kind_from_str(s: str) -> HistoryNodeKind:
    try:
        return HistoryNodeKind[s]
    except KeyError:
        return HistoryNodeKind.TEST


def _status_to_int(status) -> int:
    if status is None:
        return int(TestStatusT.OK)
    return int(status)


def _status_from_int(v: int):
    try:
        return TestStatusT(v)
    except Exception:
        return TestStatusT.OK


class HistoryWriter:
    """Serialize UCIS history nodes to a JSON bytes object."""

    def serialize(self, history_nodes: list) -> bytes:
        records = []
        for node in history_nodes:
            rec = {
                "logical_name":  node.getLogicalName(),
                "physical_name": node.getPhysicalName(),
                "kind":          _kind_to_str(node.getKind()),
                "test_status":   _status_to_int(node.getTestStatus()),
                "sim_time":      node.getSimTime(),
                "time_unit":     node.getTimeUnit(),
                "run_cwd":       node.getRunCwd(),
                "cpu_time":      node.getCpuTime(),
                "seed":          node.getSeed(),
                "cmd":           node.getCmd(),
                "args":          node.getArgs(),
                "compulsory":    node.getCompulsory(),
                "date":          node.getDate(),
                "user_name":     node.getUserName(),
                "cost":          node.getCost(),
                "tool_category": node.getToolCategory(),
                "ucis_version":  node.getUCISVersion(),
                "vendor_id":     node.getVendorId(),
                "vendor_tool":   node.getVendorTool(),
                "vendor_tool_version": node.getVendorToolVersion(),
                "same_tests":    node.getSameTests(),
                "comment":       node.getComment(),
            }
            records.append(rec)
        return json.dumps(records, indent=2).encode("utf-8")


class HistoryReader:
    """Deserialize history nodes from history.json bytes."""

    def deserialize(self, data: bytes) -> list:
        records = json.loads(data.decode("utf-8"))
        nodes = []
        for rec in records:
            node = MemHistoryNode(
                parent=None,
                logicalname=rec.get("logical_name", ""),
                physicalname=rec.get("physical_name"),
                kind=_kind_from_str(rec.get("kind", "TEST")),
            )
            node.setTestStatus(_status_from_int(rec.get("test_status", 0)))
            if rec.get("sim_time") is not None:
                node.setSimTime(rec["sim_time"])
            if rec.get("time_unit") is not None:
                node.setTimeUnit(rec["time_unit"])
            if rec.get("run_cwd") is not None:
                node.setRunCwd(rec["run_cwd"])
            if rec.get("cpu_time") is not None:
                node.setCpuTime(rec["cpu_time"])
            if rec.get("seed") is not None:
                node.setSeed(rec["seed"])
            if rec.get("cmd") is not None:
                node.setCmd(rec["cmd"])
            if rec.get("args") is not None:
                node.setArgs(rec["args"])
            if rec.get("compulsory") is not None:
                node.setCompulsory(rec["compulsory"])
            if rec.get("date") is not None:
                node.setDate(rec["date"])
            if rec.get("user_name") is not None:
                node.setUserName(rec["user_name"])
            if rec.get("cost") is not None:
                node.setCost(rec["cost"])
            if rec.get("tool_category") is not None:
                node.setToolCategory(rec["tool_category"])
            if rec.get("vendor_id") is not None:
                node.setVendorId(rec["vendor_id"])
            if rec.get("vendor_tool") is not None:
                node.setVendorTool(rec["vendor_tool"])
            if rec.get("vendor_tool_version") is not None:
                node.setVendorToolVersion(rec["vendor_tool_version"])
            if rec.get("same_tests") is not None:
                node.setSameTests(rec["same_tests"])
            if rec.get("comment") is not None:
                node.setComment(rec["comment"])
            nodes.append(node)
        return nodes
