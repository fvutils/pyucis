"""
Show Assertions Command

Displays assertion coverage information from the UCIS database.
Assertions are design checks that verify specific properties or conditions.
"""
from typing import Any, Dict
from ucis.cmd.show_base import ShowBase


class ShowAssertions(ShowBase):
    """
    Display assertion coverage information.
    
    Shows coverage for concurrent assertions (SVA), PSL assertions,
    and other assertion types captured in the UCIS database.
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract assertion coverage information.
        
        Returns:
            Dictionary containing assertion coverage data
        """
        from ucis import UCIS_ASSERT, UCIS_CVGBIN, HistoryNodeKind
        
        result = {
            "database": self.args.db,
            "assertions": [],
            "summary": {
                "total_assertions": 0,
                "passed_assertions": 0,
                "failed_assertions": 0,
                "coverage_percentage": 0.0
            }
        }
        
        total = 0
        passed = 0
        
        # Try to find assertion coverage in the database
        # Assertions may be stored as coveritems with type UCIS_ASSERT
        try:
            # Walk through all scopes looking for assertions
            for scope in self._walk_scopes(self.db.getDesignRoot()):
                if scope.m_type == UCIS_ASSERT:
                    assertion_data = self._process_assertion_scope(scope)
                    if assertion_data:
                        result["assertions"].append(assertion_data)
                        total += 1
                        if assertion_data.get("hit", False):
                            passed += 1
        except Exception as e:
            # If assertion coverage is not available, provide informative message
            result["note"] = "No assertion coverage data found in database. Assertions may not be enabled or database may contain only functional coverage."
            result["error"] = str(e)
        
        # Update summary
        result["summary"]["total_assertions"] = total
        result["summary"]["passed_assertions"] = passed
        result["summary"]["failed_assertions"] = total - passed
        if total > 0:
            result["summary"]["coverage_percentage"] = (passed / total) * 100.0
        
        return result
    
    def _walk_scopes(self, scope, depth=0):
        """Recursively walk through scope hierarchy."""
        if scope is None:
            return
        
        yield scope
        
        # Recursively process children
        try:
            child = scope.getChild()
            while child:
                yield from self._walk_scopes(child, depth + 1)
                child = child.getNextSibling()
        except:
            pass
    
    def _process_assertion_scope(self, scope):
        """Process an assertion scope and extract coverage data."""
        try:
            name = scope.getScopeName() if hasattr(scope, 'getScopeName') else str(scope)
            
            # Try to get assertion coverage data
            hit = False
            count = 0
            
            # Check if scope has coverage bins
            try:
                coveritem = scope.getCoveritem()
                if coveritem:
                    # Get first bin to check if assertion passed
                    bin = coveritem.getBin(0)
                    if bin:
                        count = bin.getCount()
                        hit = count > 0
            except:
                pass
            
            return {
                "name": name,
                "hit": hit,
                "count": count,
                "status": "passed" if hit else "failed"
            }
        except Exception as e:
            return None
    
    def _format_text(self, data: Dict[str, Any]) -> str:
        """Format data as human-readable text."""
        lines = []
        lines.append("=" * 60)
        lines.append("ASSERTION COVERAGE REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        summary = data.get("summary", {})
        lines.append(f"Total Assertions:  {summary.get('total_assertions', 0)}")
        lines.append(f"Passed:            {summary.get('passed_assertions', 0)}")
        lines.append(f"Failed:            {summary.get('failed_assertions', 0)}")
        lines.append(f"Coverage:          {summary.get('coverage_percentage', 0.0):.2f}%")
        lines.append("")
        
        if "note" in data:
            lines.append("Note: " + data["note"])
            lines.append("")
        
        assertions = data.get("assertions", [])
        if assertions:
            lines.append("Assertions:")
            lines.append("-" * 60)
            for assertion in assertions:
                status = "✓" if assertion.get("hit", False) else "✗"
                lines.append(f"{status} {assertion.get('name', 'unknown')}")
                lines.append(f"  Status: {assertion.get('status', 'unknown')}")
                lines.append(f"  Count:  {assertion.get('count', 0)}")
                lines.append("")
        else:
            lines.append("No assertions found.")
        
        return "\n".join(lines)
