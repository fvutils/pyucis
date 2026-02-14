"""Data structure for Verilator coverage items."""

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class VltCoverageItem:
    """Represents a single coverage entry from Verilator .dat file.
    
    Attributes:
        filename: Source file path
        lineno: Line number (0 if not specified)
        colno: Column number (0 if not specified)
        coverage_type: Type of coverage (line, branch, toggle, funccov)
        page: Coverage page identifier (e.g., v_line, v_funccov/cg1)
        hierarchy: Module hierarchy path
        comment: Additional comment/detail (block, if, else, etc.)
        bin_name: Bin name for functional coverage
        hit_count: Number of hits/samples
        attributes: All parsed key-value pairs
        line_range: Line range string (e.g., "S100-101,103")
    """
    filename: str = ""
    lineno: int = 0
    colno: int = 0
    coverage_type: str = ""
    page: str = ""
    hierarchy: str = ""
    comment: str = ""
    bin_name: str = ""
    hit_count: int = 0
    attributes: Dict[str, str] = field(default_factory=dict)
    line_range: str = ""
    
    @property
    def is_functional_coverage(self) -> bool:
        """Check if this is functional coverage."""
        return 'v_funccov' in self.page
    
    @property
    def is_line_coverage(self) -> bool:
        """Check if this is line/statement coverage."""
        return self.coverage_type == 'line' or 'v_line' in self.page
    
    @property
    def is_branch_coverage(self) -> bool:
        """Check if this is branch coverage."""
        return self.coverage_type == 'branch' or 'v_branch' in self.page
    
    @property
    def is_toggle_coverage(self) -> bool:
        """Check if this is toggle coverage."""
        return self.coverage_type == 'toggle' or 'v_toggle' in self.page
    
    @property
    def covergroup_name(self) -> Optional[str]:
        """Extract covergroup name from page if functional coverage."""
        if self.is_functional_coverage:
            # Format: v_funccov/cg_name
            parts = self.page.split('/')
            if len(parts) >= 2:
                return parts[1]
        return None
    
    def __repr__(self) -> str:
        return (f"VltCoverageItem(file={self.filename!r}, line={self.lineno}, "
                f"type={self.coverage_type!r}, hits={self.hit_count})")
