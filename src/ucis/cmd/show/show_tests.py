"""
Show Tests Command

Displays test execution information including status, dates, and results.
"""
from typing import Any, Dict, List
from ucis.cmd.show_base import ShowBase


class ShowTests(ShowBase):
    """
    Display test execution information.
    
    Shows:
    - List of all tests
    - Test status (passed/failed)
    - Execution dates
    - Test hierarchy
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract test information from the database.
        
        Returns:
            Dictionary containing test details
        """
        from ucis.history_node_kind import HistoryNodeKind
        
        tests = []
        
        # Get all test history nodes
        try:
            for node in self.db.historyNodes(HistoryNodeKind.TEST):
                test_info = self._get_test_info(node)
                if test_info:
                    tests.append(test_info)
        except Exception as e:
            # If historyNodes fails, just return empty
            pass
        
        result = {
            "database": self.args.db,
            "tests": tests,
            "summary": {
                "total_tests": len(tests),
                "passed": sum(1 for t in tests if t.get('passed', False)),
                "failed": sum(1 for t in tests if not t.get('passed', True)),
            }
        }
        
        return result
    
    def _get_test_info(self, node) -> Dict[str, Any]:
        """Extract information from a test history node."""
        test_data = node.getTestData()
        if not test_data:
            return None
        
        from ucis import UCIS_TESTSTATUS_OK
        
        info = {
            "name": node.getLogicalName(),
            "physical_name": node.getPhysicalName() if hasattr(node, 'getPhysicalName') else None,
            "status": test_data.teststatus,
            "passed": test_data.teststatus == UCIS_TESTSTATUS_OK,
        }
        
        # Add optional fields if available
        if hasattr(test_data, 'date') and test_data.date:
            info["date"] = test_data.date
        if hasattr(test_data, 'toolcategory') and test_data.toolcategory:
            info["tool"] = test_data.toolcategory
        if hasattr(test_data, 'simtime') and test_data.simtime:
            info["simtime"] = test_data.simtime
        if hasattr(test_data, 'timeunit') and test_data.timeunit:
            info["timeunit"] = test_data.timeunit
        if hasattr(test_data, 'comment') and test_data.comment:
            info["comment"] = test_data.comment
        
        return info
