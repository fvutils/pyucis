#!/usr/bin/env python3
"""
Quick demo of the PyUCIS TUI.

This script creates a sample database and shows how to use the TUI.
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def create_demo_database():
    """Create a demo database with varied coverage."""
    print("Creating demo coverage database...")
    
    from ucis import (UCIS_VLOG, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_SCOPE_UNDER_DU,
                      UCIS_INST_ONCE, UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK,
                      UCIS_CVGBIN)
    from ucis.source_info import SourceInfo
    from ucis.test_data import TestData
    from ucis.mem.mem_factory import MemFactory
    from ucis.xml.xml_writer import XmlWriter
    from ucis.cover_data import CoverData
    
    # Create database
    db = MemFactory.create()
    
    # Add test metadata
    testnode = db.createHistoryNode(None, "demo_test", "demo_test", UCIS_HISTORYNODE_TEST)
    td = TestData(teststatus=UCIS_TESTSTATUS_OK, toolcategory="PyUCIS:Demo", date="20260213000000")
    testnode.setTestData(td)
    
    # Create file handle
    file_h = db.createFileHandle("design.sv", "/demo")
    
    # Create design unit
    du = db.createScope("work.top", SourceInfo(file_h, 1, 0), 1, UCIS_VLOG,
                       UCIS_DU_MODULE, UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE)
    
    # Create instance
    inst = db.createInstance("top", None, 1, UCIS_VLOG, UCIS_INSTANCE, du, UCIS_INST_ONCE)
    
    # Create covergroups directly under the instance
    # (we'll create a variety to show different coverage levels)
    covergroup_names = [
        ("cpu_ops", "CPU operation coverage"),
        ("cpu_flags", "CPU flags coverage"),
        ("memory_read", "Memory read coverage"),
        ("memory_write", "Memory write coverage"),
        ("io_control", "I/O control coverage"),
        ("io_status", "I/O status coverage"),
    ]
    
    for idx, (cg_name, desc) in enumerate(covergroup_names):
        cg = inst.createCovergroup(
            cg_name,
            SourceInfo(file_h, 20 + idx * 10, 0),
            1,
            UCIS_VLOG
        )
        
        # Create coverpoints in each covergroup
        for cp_idx in range(3):
            cp = cg.createCoverpoint(
                f"cp_{cp_idx}",
                SourceInfo(file_h, 30 + cp_idx, 0),
                1,
                UCIS_VLOG
            )
            
            # Create bins with varying coverage
            for bin_idx in range(4):
                # Create bin with source info
                bin_scope = cp.createBin(
                    f"bin_{bin_idx}",
                    SourceInfo(file_h, 40 + bin_idx, 0),
                    1, 0, f"value_{bin_idx}", UCIS_CVGBIN
                )
                
                # Set coverage by incrementing
                # CG 0: 100% coverage, CG 1: 75%, CG 2: 50%, CG 3: 25%, CG 4-5: 0%
                if idx == 0:
                    for _ in range(100 + bin_idx):  # All bins hit multiple times
                        bin_scope.incrementCover()
                elif idx == 1 and bin_idx < 3:
                    for _ in range(50 + bin_idx):  # 3/4 bins hit
                        bin_scope.incrementCover()
                elif idx == 2 and bin_idx < 2:
                    for _ in range(25 + bin_idx):  # 2/4 bins hit
                        bin_scope.incrementCover()
                elif idx == 3 and bin_idx == 0:
                    for _ in range(10):  # 1/4 bins hit
                        bin_scope.incrementCover()
                # else: leave at 0 (not hit)
    
    # Write to file
    output_path = "/tmp/pyucis_demo.xml"
    with open(output_path, 'w') as f:
        writer = XmlWriter()
        writer.write(f, db)
    
    db.close()
    
    print(f"✓ Created demo database: {output_path}")
    print(f"  - 1 top instance")
    print(f"  - 6 covergroups")
    print(f"  - 18 coverpoints")  
    print(f"  - 72 bins")
    print()
    return output_path


def show_demo_instructions(db_path):
    """Show instructions for using the TUI."""
    print("=" * 70)
    print("PyUCIS TUI Demo")
    print("=" * 70)
    print()
    print("To launch the interactive TUI:")
    print(f"  pyucis view {db_path}")
    print()
    print("Or if not installed:")
    print(f"  PYTHONPATH=src python -m ucis.tui {db_path}")
    print()
    print("Keyboard Shortcuts:")
    print("  1 - Dashboard view (coverage overview)")
    print("  2 - Hierarchy view (navigate design tree)")
    print("  3 - Gaps view (find uncovered items)")
    print("  ↑/↓ - Navigate items")
    print("  ←/→ - Collapse/expand tree (hierarchy view)")
    print("  q - Quit")
    print()
    print("Features:")
    print("  • Color-coded coverage indicators")
    print("  • Interactive tree navigation")
    print("  • Real-time gap identification")
    print("  • Fast, keyboard-driven workflow")
    print()
    print("=" * 70)


if __name__ == "__main__":
    try:
        db_path = create_demo_database()
        show_demo_instructions(db_path)
        
        print("\nPress Enter to launch the TUI (or Ctrl+C to exit)...")
        input()
        
        # Launch TUI
        from ucis.tui.app import TUIApp
        app = TUIApp(db_path)
        app.run()
        
    except KeyboardInterrupt:
        print("\n\nDemo cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
