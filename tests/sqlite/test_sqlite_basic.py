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
Basic tests for SQLite UCIS implementation
"""

import unittest
import tempfile
import os

from ucis.sqlite import SqliteUCIS
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.history_node_kind import HistoryNodeKind
from ucis.int_property import IntProperty


class TestSqliteBasic(unittest.TestCase):
    """Basic SQLite UCIS tests"""
    
    def test_create_in_memory_db(self):
        """Test creating an in-memory database"""
        ucis = SqliteUCIS()
        self.assertIsNotNone(ucis)
        self.assertEqual(ucis.getAPIVersion(), "1.0")
        ucis.close()
    
    def test_create_file_db(self):
        """Test creating a file-based database"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            ucis = SqliteUCIS(db_path)
            self.assertIsNotNone(ucis)
            ucis.close()
            
            # Verify file exists
            self.assertTrue(os.path.exists(db_path))
            
            # Reopen and verify
            ucis2 = SqliteUCIS(db_path)
            self.assertEqual(ucis2.getAPIVersion(), "1.0")
            ucis2.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_create_scope(self):
        """Test creating scopes"""
        ucis = SqliteUCIS()
        
        # Create top-level scope
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        self.assertIsNotNone(top)
        self.assertEqual(top.getScopeName(), "top")
        self.assertEqual(top.getScopeType(), ScopeTypeT.INSTANCE)
        
        # Create child scope
        sub = top.createScope("sub", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        self.assertIsNotNone(sub)
        self.assertEqual(sub.getScopeName(), "sub")
        
        ucis.close()
    
    def test_iterate_scopes(self):
        """Test iterating scopes"""
        ucis = SqliteUCIS()
        
        # Create multiple scopes
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        child1 = top.createScope("child1", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        child2 = top.createScope("child2", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Iterate children
        children = list(top.scopes(ScopeTypeT.INSTANCE))
        self.assertEqual(len(children), 2)
        
        names = [s.getScopeName() for s in children]
        self.assertIn("child1", names)
        self.assertIn("child2", names)
        
        ucis.close()
    
    def test_create_coverage(self):
        """Test creating coverage items"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Create coverage item
        cover_data = CoverData(0x01, 0)  # CVGBIN type
        cover_data.data = 100  # 100 hits
        cover = top.createNextCover("bin1", cover_data, None)
        
        self.assertIsNotNone(cover)
        self.assertEqual(cover.getName(), "bin1")
        self.assertEqual(cover.getCoverData().data, 100)
        
        ucis.close()
    
    def test_increment_coverage(self):
        """Test incrementing coverage"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        cover_data = CoverData(0x01, 0)
        cover_data.data = 10
        cover = top.createNextCover("bin1", cover_data, None)
        
        # Increment coverage
        cover.incrementCover(5)
        self.assertEqual(cover.getCoverData().data, 15)
        
        # Increment again
        cover.incrementCover()
        self.assertEqual(cover.getCoverData().data, 16)
        
        ucis.close()
    
    def test_iterate_coverage(self):
        """Test iterating coverage items"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Create multiple coverage items
        for i in range(5):
            cover_data = CoverData(0x01, 0)
            cover_data.data = i * 10
            top.createNextCover(f"bin{i}", cover_data, None)
        
        # Iterate coverage
        covers = list(top.coverItems(-1))
        self.assertEqual(len(covers), 5)
        
        names = [c.getName() for c in covers]
        self.assertEqual(names, ["bin0", "bin1", "bin2", "bin3", "bin4"])
        
        ucis.close()
    
    def test_scope_weight_goal(self):
        """Test scope weight and goal"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Test weight
        self.assertEqual(top.getWeight(), 1)
        top.setWeight(10)
        self.assertEqual(top.getWeight(), 10)
        
        # Test goal
        self.assertEqual(top.getGoal(), 100)
        top.setGoal(95)
        self.assertEqual(top.getGoal(), 95)
        
        ucis.close()
    
    def test_create_history_node(self):
        """Test creating history nodes"""
        ucis = SqliteUCIS()
        
        # Create test history node
        test = ucis.createHistoryNode(None, "test1", "test1.sv", HistoryNodeKind.TEST)
        
        self.assertIsNotNone(test)
        self.assertEqual(test.getLogicalName(), "test1")
        self.assertEqual(test.getPhysicalName(), "test1.sv")
        self.assertEqual(test.getKind(), HistoryNodeKind.TEST)
        
        ucis.close()
    
    def test_history_node_properties(self):
        """Test history node properties"""
        ucis = SqliteUCIS()
        
        test = ucis.createHistoryNode(None, "test1", None, HistoryNodeKind.TEST)
        
        # Set and get properties
        test.setSeed("12345")
        self.assertEqual(test.getSeed(), "12345")
        
        test.setCmd("run_test.sh")
        self.assertEqual(test.getCmd(), "run_test.sh")
        
        test.setCpuTime(123.45)
        self.assertEqual(test.getCpuTime(), 123.45)
        
        ucis.close()
    
    def test_iterate_history_nodes(self):
        """Test iterating history nodes"""
        ucis = SqliteUCIS()
        
        # Create multiple tests
        test1 = ucis.createHistoryNode(None, "test1", None, HistoryNodeKind.TEST)
        test2 = ucis.createHistoryNode(None, "test2", None, HistoryNodeKind.TEST)
        merge = ucis.createHistoryNode(None, "merge1", None, HistoryNodeKind.MERGE)
        
        # Iterate all history nodes
        all_nodes = list(ucis.historyNodes())
        self.assertEqual(len(all_nodes), 3)
        
        # Iterate only tests
        tests = list(ucis.historyNodes(HistoryNodeKind.TEST))
        self.assertEqual(len(tests), 2)
        
        ucis.close()
    
    def test_file_handle(self):
        """Test file handle creation"""
        ucis = SqliteUCIS()
        
        # Create file handle
        fh = ucis.createFileHandle("test.sv", None)
        self.assertIsNotNone(fh)
        self.assertEqual(fh.getFileName(), "test.sv")
        
        # Get same file handle again (should be cached)
        fh2 = ucis.createFileHandle("test.sv", None)
        self.assertEqual(fh.file_id, fh2.file_id)
        
        ucis.close()
    
    def test_source_info(self):
        """Test source info tracking"""
        ucis = SqliteUCIS()
        
        # Create file handle
        fh = ucis.createFileHandle("test.sv", None)
        srcinfo = SourceInfo(fh, 42, 10)
        
        # Create scope with source info
        top = ucis.createScope("top", srcinfo, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Verify source info
        retrieved_info = top.getSourceInfo()
        self.assertIsNotNone(retrieved_info)
        self.assertEqual(retrieved_info.line, 42)
        self.assertEqual(retrieved_info.token, 10)
        
        ucis.close()
    
    def test_properties(self):
        """Test property storage"""
        ucis = SqliteUCIS()
        
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Test int property
        top.setIntProperty(-1, IntProperty.SCOPE_WEIGHT, 42)
        self.assertEqual(top.getIntProperty(-1, IntProperty.SCOPE_WEIGHT), 42)
        
        ucis.close()
    
    def test_num_tests(self):
        """Test getNumTests"""
        ucis = SqliteUCIS()
        
        self.assertEqual(ucis.getNumTests(), 0)
        
        test1 = ucis.createHistoryNode(None, "test1", None, HistoryNodeKind.TEST)
        self.assertEqual(ucis.getNumTests(), 1)
        
        test2 = ucis.createHistoryNode(None, "test2", None, HistoryNodeKind.TEST)
        self.assertEqual(ucis.getNumTests(), 2)
        
        # Merge node shouldn't count
        merge = ucis.createHistoryNode(None, "merge", None, HistoryNodeKind.MERGE)
        self.assertEqual(ucis.getNumTests(), 2)
        
        ucis.close()
    
    def test_persistence(self):
        """Test data persistence across close/open"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            # Create and populate database
            ucis = SqliteUCIS(db_path)
            top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            cover_data = CoverData(0x01, 0)
            cover_data.data = 100
            cover = top.createNextCover("bin1", cover_data, None)
            test = ucis.createHistoryNode(None, "test1", None, HistoryNodeKind.TEST)
            ucis.close()
            
            # Reopen and verify
            ucis2 = SqliteUCIS(db_path)
            
            # Check scope exists
            scopes = list(ucis2.scopes(ScopeTypeT.INSTANCE))
            self.assertEqual(len(scopes), 1)
            self.assertEqual(scopes[0].getScopeName(), "top")
            
            # Check coverage exists
            covers = list(scopes[0].coverItems(-1))
            self.assertEqual(len(covers), 1)
            self.assertEqual(covers[0].getName(), "bin1")
            self.assertEqual(covers[0].getCoverData().data, 100)
            
            # Check history node exists
            tests = list(ucis2.historyNodes(HistoryNodeKind.TEST))
            self.assertEqual(len(tests), 1)
            self.assertEqual(tests[0].getLogicalName(), "test1")
            
            ucis2.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == '__main__':
    unittest.main()
