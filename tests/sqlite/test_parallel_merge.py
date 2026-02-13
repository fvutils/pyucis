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
Tests for parallel merge functionality
"""

import unittest
import tempfile
import os
import shutil

from ucis.sqlite import SqliteUCIS
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.cover_data import CoverData


class TestParallelMerge(unittest.TestCase):
    """Tests for parallel merge with ThreadPoolExecutor"""
    
    def setUp(self):
        """Create temporary directory for test databases"""
        self.tmpdir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.tmpdir)
    
    def test_merge_fast_with_multiple_workers(self):
        """Test merge_fast with workers parameter"""
        # Create three source databases with identical structure
        source_paths = []
        for i in range(3):
            db_path = os.path.join(self.tmpdir, f'source_{i}.ucis')
            db = SqliteUCIS(db_path)
            top = db.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            dut = top.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            
            cover_data = CoverData(0x01, 0)
            cover_data.data = (i + 1) * 10  # 10, 20, 30
            dut.createNextCover("bin1", cover_data, None)
            db.close()
            source_paths.append(db_path)
        
        # Merge with workers=2
        merged_path = os.path.join(self.tmpdir, 'merged.ucis')
        merged = SqliteUCIS(merged_path)
        stats = merged.merge_fast(source_paths, workers=2)
        merged.close()
        
        # Verify statistics
        # Note: merge() doesn't increment tests_merged unless squash_history=True
        # Only merge_fast() increments it, so count is 2 (sources 2 and 3)
        self.assertEqual(stats.tests_merged, 2)
        # First merge adds coveritems, then 2 more sources match and update them
        self.assertTrue(stats.coveritems_matched >= 2)
        # Total hits: 20 from source 2, 30 from source 3 (but stats may include more from merge())
        self.assertTrue(stats.total_hits_added >= 50)
        
        # Verify merged coverage
        merged = SqliteUCIS.open_readonly(merged_path)
        top = list(merged.scopes(ScopeTypeT.INSTANCE))[0]
        dut = list(top.scopes(ScopeTypeT.INSTANCE))[0]
        bin1 = list(dut.coverItems(-1))[0]
        
        self.assertEqual(bin1.getCoverData().data, 60)  # 10 + 20 + 30
        merged.close()
    
    def test_merge_fast_with_single_worker(self):
        """Test merge_fast with workers=1 (sequential)"""
        # Create two source databases
        source_paths = []
        for i in range(2):
            db_path = os.path.join(self.tmpdir, f'source_{i}.ucis')
            db = SqliteUCIS(db_path)
            top = db.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            dut = top.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            
            cover_data = CoverData(0x01, 0)
            cover_data.data = 25
            dut.createNextCover("bin1", cover_data, None)
            db.close()
            source_paths.append(db_path)
        
        # Merge with workers=1
        merged_path = os.path.join(self.tmpdir, 'merged.ucis')
        merged = SqliteUCIS(merged_path)
        stats = merged.merge_fast(source_paths, workers=1)
        merged.close()
        
        # Verify merged coverage
        merged = SqliteUCIS.open_readonly(merged_path)
        top = list(merged.scopes(ScopeTypeT.INSTANCE))[0]
        dut = list(top.scopes(ScopeTypeT.INSTANCE))[0]
        bin1 = list(dut.coverItems(-1))[0]
        
        self.assertEqual(bin1.getCoverData().data, 50)  # 25 + 25
        merged.close()
    
    def test_merge_fast_with_many_bins(self):
        """Test merge_fast with many coveritems"""
        num_bins = 100
        num_sources = 4
        
        # Create source databases
        source_paths = []
        for i in range(num_sources):
            db_path = os.path.join(self.tmpdir, f'source_{i}.ucis')
            db = SqliteUCIS(db_path)
            top = db.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            dut = top.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            
            for bin_idx in range(num_bins):
                cover_data = CoverData(0x01, 0)
                cover_data.data = 1
                dut.createNextCover(f"bin{bin_idx}", cover_data, None)
            
            db.close()
            source_paths.append(db_path)
        
        # Merge with workers=4
        merged_path = os.path.join(self.tmpdir, 'merged.ucis')
        merged = SqliteUCIS(merged_path)
        stats = merged.merge_fast(source_paths, workers=4)
        merged.close()
        
        # Verify statistics
        # Note: merge() doesn't increment tests_merged, only merge_fast() does
        # So count is num_sources - 1 (all except first)
        self.assertEqual(stats.tests_merged, num_sources - 1)
        
        # Verify merged coverage - each bin should have count = num_sources
        merged = SqliteUCIS.open_readonly(merged_path)
        top = list(merged.scopes(ScopeTypeT.INSTANCE))[0]
        dut = list(top.scopes(ScopeTypeT.INSTANCE))[0]
        bins = list(dut.coverItems(-1))
        
        self.assertEqual(len(bins), num_bins)
        for bin_item in bins:
            self.assertEqual(bin_item.getCoverData().data, num_sources)
        
        merged.close()


if __name__ == '__main__':
    unittest.main()
