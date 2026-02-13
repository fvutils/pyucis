#!/usr/bin/env python3
"""
Create a sample coverage database for testing the TUI.
"""
import tempfile
import os
from ucis import (UCIS_VLOG, UCIS_INSTANCE, UCIS_DU_MODULE, UCIS_SCOPE_UNDER_DU,
                  UCIS_INST_ONCE, UCIS_HISTORYNODE_TEST, UCIS_TESTSTATUS_OK,
                  UCIS_CVGBINSCOPE, UCIS_COVERGROUP, UCIS_COVERPOINT)
from ucis.source_info import SourceInfo
from ucis.test_data import TestData
from ucis.mem.mem_factory import MemFactory


def create_sample_db(output_path="sample_coverage.xml"):
    """Create a sample coverage database with covergroups and bins."""
    
    # Create in-memory database
    db = MemFactory.create()
    
    # Add test metadata
    testnode = db.createHistoryNode(
        None,
        "sample_test",
        "sample_test",
        UCIS_HISTORYNODE_TEST
    )
    td = TestData(
        teststatus=UCIS_TESTSTATUS_OK,
        toolcategory="PyUCIS:TUI",
        date="20260213000000"
    )
    testnode.setTestData(td)
    
    # Create file handle
    file_h = db.createFileHandle("design.sv", "/tmp")
    
    # Create design unit
    du = db.createScope(
        "work.top",
        SourceInfo(file_h, 1, 0),
        1,
        UCIS_VLOG,
        UCIS_DU_MODULE,
        UCIS_SCOPE_UNDER_DU | UCIS_INST_ONCE
    )
    
    # Create instance
    inst = db.createInstance(
        "top",
        None,
        1,
        UCIS_VLOG,
        UCIS_INSTANCE,
        du,
        UCIS_INST_ONCE
    )
    
    # Create some covergroups
    for i in range(3):
        cg = inst.createCovergroup(
            f"covergroup_{i}",
            SourceInfo(file_h, 10 + i * 10, 0),
            1,
            UCIS_VLOG
        )
        
        # Add coverpoints to each covergroup
        for j in range(4):
            cp = cg.createCoverpoint(
                f"coverpoint_{j}",
                SourceInfo(file_h, 10 + i * 10 + j, 0),
                1,
                UCIS_VLOG
            )
            
            # Add bins to each coverpoint
            for k in range(5):
                from ucis import UCIS_CVGBIN
                bin_item = cp.createBin(
                    f"bin_{k}",
                    SourceInfo(file_h, 10 + i * 10 + j, 0),
                    1,  # at_least
                    0,  # flags
                    f"value_{k}",  # bin_name
                    UCIS_CVGBIN
                )
                # Note: counts will be set later via API if needed
    
    # Write to XML file
    from ucis.xml.xml_writer import XmlWriter
    writer = XmlWriter()
    with open(output_path, 'w') as f:
        writer.write(f, db)
    
    print(f"Created sample database: {output_path}")
    print(f"  - 3 covergroups")
    print(f"  - 12 coverpoints")
    print(f"  - 60 bins")
    
    db.close()
    return output_path


if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "sample_coverage.xml"
    create_sample_db(output)
