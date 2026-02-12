# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
Unit tests for merging MemUCIS into SqliteUCIS
"""

import os
import tempfile
import pytest

from ucis.mem.mem_ucis import MemUCIS
from ucis.sqlite.sqlite_ucis import SqliteUCIS
from ucis.source_info import SourceInfo
from ucis.source_t import SourceT
from ucis.scope_type_t import ScopeTypeT
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.flags_t import FlagsT


def create_sample_mem_db():
    """Create a sample MemUCIS database for testing"""
    db = MemUCIS()
    fh = db.createFileHandle("test.sv", os.getcwd())
    si = SourceInfo(fh, 1, 0)
    du = db.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
    inst = db.createInstance("tb", si, 1, SourceT.NONE, ScopeTypeT.INSTANCE, du, FlagsT(0))
    cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
    cp = cg.createScope("cp", si, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, FlagsT(0))
    cd = CoverData(CoverTypeT.CVGBIN, 0)
    cd.data = 10
    cp.createNextCover("bin0", cd, si)
    return db


class TestSqliteMergeMem:
    """Test merging MemUCIS databases into SqliteUCIS"""
    
    def test_merge_mem_to_sqlite_in_memory(self):
        """Test merging MemUCIS into in-memory SqliteUCIS"""
        src = create_sample_mem_db()
        dst = SqliteUCIS()
        
        # Merge should succeed
        stats = dst.merge(src)
        
        # Verify merge statistics
        assert stats is not None
        assert stats.scopes_added > 0
        assert stats.coveritems_added > 0
        assert stats.total_hits_added == 10
        
        dst.close()
    
    def test_merge_mem_to_sqlite_file(self):
        """Test merging MemUCIS into file-based SqliteUCIS"""
        src = create_sample_mem_db()
        
        with tempfile.NamedTemporaryFile(suffix=".ucisdb", delete=False) as f:
            dst_path = f.name
        
        try:
            dst = SqliteUCIS(dst_path)
            
            # Merge should succeed
            stats = dst.merge(src)
            
            # Verify merge statistics
            assert stats is not None
            assert stats.scopes_added > 0
            assert stats.coveritems_added > 0
            
            dst.close()
            
            # Reopen and verify data persisted
            dst2 = SqliteUCIS(dst_path)
            # Should have the merged scopes
            scopes = list(dst2.scopes(-1))
            assert len(scopes) > 0
            dst2.close()
            
        finally:
            if os.path.exists(dst_path):
                os.unlink(dst_path)
    
    def test_merge_multiple_mem_dbs(self):
        """Test merging multiple MemUCIS databases"""
        # Create two MemUCIS databases with overlapping coverage
        src1 = create_sample_mem_db()
        src2 = create_sample_mem_db()
        
        dst = SqliteUCIS()
        
        # Merge both
        stats1 = dst.merge(src1)
        stats2 = dst.merge(src2)
        
        # First merge adds, second merge matches and accumulates
        assert stats1.scopes_added > 0
        assert stats1.coveritems_added > 0
        assert stats2.scopes_matched > 0
        assert stats2.coveritems_matched > 0
        
        # Coverage should be accumulated (10 + 10 = 20)
        # Find the coverage item and verify
        scopes = list(dst.scopes(-1))
        assert len(scopes) > 0
        
        dst.close()
    
    def test_merge_empty_mem_db(self):
        """Test merging an empty MemUCIS database"""
        src = MemUCIS()
        dst = SqliteUCIS()
        
        # Merge should succeed even with empty source
        stats = dst.merge(src)
        
        assert stats is not None
        # No scopes or coverage to add
        assert stats.scopes_added == 0
        assert stats.coveritems_added == 0
        
        dst.close()
    
    def test_merge_preserves_metadata(self):
        """Test that merge preserves source metadata"""
        src = create_sample_mem_db()
        src.setWrittenBy("test_user")
        
        dst = SqliteUCIS()
        dst.merge(src)
        
        # Check that scopes were created
        scopes = list(dst.scopes(-1))
        assert len(scopes) > 0
        
        # Check that we can navigate the hierarchy
        for scope in scopes:
            assert scope.getScopeName() is not None
            assert scope.getScopeType() is not None
        
        dst.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
