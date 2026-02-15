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
        # SqliteHistoryNode doesn't have getTestData(), use individual getters
        try:
            info = {
                "name": node.getLogicalName(),
                "physical_name": node.getPhysicalName() if hasattr(node, 'getPhysicalName') else None,
                "status": node.getTestStatus() if hasattr(node, 'getTestStatus') else 0,
                "passed": True,  # Default to True if we don't have status info
            }
            
            # Get status
            if hasattr(node, 'getTestStatus'):
                from ucis import UCIS_TESTSTATUS_OK
                test_status = node.getTestStatus()
                info["status"] = test_status
                info["passed"] = test_status == UCIS_TESTSTATUS_OK
            
            # Add optional fields if available
            if hasattr(node, 'getDate'):
                date = node.getDate()
                if date:
                    info["date"] = date
            
            if hasattr(node, 'getToolCategory'):
                tool = node.getToolCategory()
                if tool:
                    info["tool"] = tool
            
            if hasattr(node, 'getSimTime'):
                simtime = node.getSimTime()
                if simtime:
                    info["simtime"] = simtime
            
            if hasattr(node, 'getTimeUnit'):
                timeunit = node.getTimeUnit()
                if timeunit:
                    info["timeunit"] = timeunit
            
            if hasattr(node, 'getCmd'):
                cmd = node.getCmd()
                if cmd:
                    info["comment"] = cmd
            
            return info
        except Exception as e:
            # If we can't get test info, return None
            return None
