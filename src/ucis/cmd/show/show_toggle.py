"""
Show Toggle Command

Displays toggle coverage information from the UCIS database.
Toggle coverage tracks signal transitions (0->1 and 1->0) for signals in the design.
"""
from typing import Any, Dict
from ucis.cmd.show_base import ShowBase


class ShowToggle(ShowBase):
    """
    Display toggle coverage information.
    
    Shows toggle coverage for signals, indicating which signals have
    toggled from 0 to 1 and from 1 to 0 during simulation.
    """
    
    def get_data(self) -> Dict[str, Any]:
        """
        Extract toggle coverage information.
        
        Returns:
            Dictionary containing toggle coverage data
        """
        from ucis import UCIS_TOGGLE
        
        result = {
            "database": self.args.db,
            "signals": [],
            "summary": {
                "total_signals": 0,
                "fully_toggled": 0,
                "partially_toggled": 0,
                "not_toggled": 0,
                "coverage_percentage": 0.0
            }
        }
        
        total_signals = 0
        fully_toggled = 0
        partially_toggled = 0
        
        # Try to find toggle coverage in the database
        try:
            # Walk through all scopes looking for toggle coverage
            for scope in self._walk_scopes(self.db.getDesignRoot()):
                if scope.m_type == UCIS_TOGGLE:
                    toggle_data = self._process_toggle_scope(scope)
                    if toggle_data:
                        result["signals"].append(toggle_data)
                        total_signals += 1
                        
                        # Check if both directions toggled
                        if toggle_data.get("toggle_0to1", False) and toggle_data.get("toggle_1to0", False):
                            fully_toggled += 1
                        elif toggle_data.get("toggle_0to1", False) or toggle_data.get("toggle_1to0", False):
                            partially_toggled += 1
        except Exception as e:
            # If toggle coverage is not available, provide informative message
            result["note"] = "No toggle coverage data found in database. Toggle coverage may not be enabled or database may contain only functional coverage."
            result["error"] = str(e)
        
        # Update summary
        result["summary"]["total_signals"] = total_signals
        result["summary"]["fully_toggled"] = fully_toggled
        result["summary"]["partially_toggled"] = partially_toggled
        result["summary"]["not_toggled"] = total_signals - fully_toggled - partially_toggled
        
        if total_signals > 0:
            # Coverage is based on signals that toggled in both directions
            result["summary"]["coverage_percentage"] = (fully_toggled / total_signals) * 100.0
        
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
    
    def _process_toggle_scope(self, scope):
        """Process a toggle scope and extract coverage data."""
        try:
            name = scope.getScopeName() if hasattr(scope, 'getScopeName') else str(scope)
            
            # Track toggle states
            toggle_0to1 = False
            toggle_1to0 = False
            count_0to1 = 0
            count_1to0 = 0
            
            # Try to get toggle coverage data
            try:
                coveritem = scope.getCoveritem()
                if coveritem:
                    # Toggle coverage typically has 2 bins: 0->1 and 1->0
                    num_bins = coveritem.getNumBins()
                    for i in range(num_bins):
                        bin = coveritem.getBin(i)
                        if bin:
                            count = bin.getCount()
                            # Check bin type (0->1 or 1->0)
                            # This is simplified - actual implementation would check bin flags
                            if i == 0:  # Assume first bin is 0->1
                                count_0to1 = count
                                toggle_0to1 = count > 0
                            elif i == 1:  # Assume second bin is 1->0
                                count_1to0 = count
                                toggle_1to0 = count > 0
            except:
                pass
            
            # Determine toggle status
            if toggle_0to1 and toggle_1to0:
                status = "full"
            elif toggle_0to1 or toggle_1to0:
                status = "partial"
            else:
                status = "none"
            
            return {
                "name": name,
                "toggle_0to1": toggle_0to1,
                "toggle_1to0": toggle_1to0,
                "count_0to1": count_0to1,
                "count_1to0": count_1to0,
                "status": status
            }
        except Exception as e:
            return None
    
    def _format_text(self, data: Dict[str, Any]) -> str:
        """Format data as human-readable text."""
        lines = []
        lines.append("=" * 60)
        lines.append("TOGGLE COVERAGE REPORT")
        lines.append("=" * 60)
        lines.append("")
        
        summary = data.get("summary", {})
        lines.append(f"Total Signals:      {summary.get('total_signals', 0)}")
        lines.append(f"Fully Toggled:      {summary.get('fully_toggled', 0)}")
        lines.append(f"Partially Toggled:  {summary.get('partially_toggled', 0)}")
        lines.append(f"Not Toggled:        {summary.get('not_toggled', 0)}")
        lines.append(f"Coverage:           {summary.get('coverage_percentage', 0.0):.2f}%")
        lines.append("")
        
        if "note" in data:
            lines.append("Note: " + data["note"])
            lines.append("")
        
        signals = data.get("signals", [])
        if signals:
            lines.append("Signal Toggle Status:")
            lines.append("-" * 60)
            lines.append(f"{'Signal':<30} {'0->1':<8} {'1->0':<8} Status")
            lines.append("-" * 60)
            
            for signal in signals[:50]:  # Limit to first 50 for readability
                name = signal.get('name', 'unknown')[:28]
                t01 = "✓" if signal.get('toggle_0to1', False) else "✗"
                t10 = "✓" if signal.get('toggle_1to0', False) else "✗"
                status = signal.get('status', 'unknown')
                lines.append(f"{name:<30} {t01:<8} {t10:<8} {status}")
            
            if len(signals) > 50:
                lines.append(f"... and {len(signals) - 50} more signals")
        else:
            lines.append("No toggle coverage found.")
        
        return "\n".join(lines)
