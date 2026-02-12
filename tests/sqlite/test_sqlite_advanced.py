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
Tests for Phase 4 advanced features: merge, attributes, tags
"""

import unittest
import tempfile
import os

from ucis.sqlite import SqliteUCIS, merge_databases, ObjectKind
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.cover_data import CoverData
from ucis.history_node_kind import HistoryNodeKind


class TestSqliteMerge(unittest.TestCase):
    """Tests for database merge functionality"""
    
    def test_basic_merge(self):
        """Test basic merge of two databases"""
        # Create first database
        db1 = SqliteUCIS()
        top1 = db1.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        dut1 = top1.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        cover_data = CoverData(0x01, 0)
        cover_data.data = 50
        dut1.createNextCover("bin1", cover_data, None)
        
        # Create second database with same structure
        db2 = SqliteUCIS()
        top2 = db2.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        dut2 = top2.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        cover_data2 = CoverData(0x01, 0)
        cover_data2.data = 30
        dut2.createNextCover("bin1", cover_data2, None)
        
        # Merge db2 into db1
        stats = db1.merge(db2)
        
        # Verify merge statistics
        self.assertEqual(stats.scopes_matched, 2)  # top and dut
        self.assertEqual(stats.coveritems_matched, 1)  # bin1
        self.assertEqual(stats.total_hits_added, 30)
        
        # Verify merged coverage
        top1_merged = list(db1.scopes(ScopeTypeT.INSTANCE))[0]
        dut1_merged = list(top1_merged.scopes(ScopeTypeT.INSTANCE))[0]
        bin1_merged = list(dut1_merged.coverItems(-1))[0]
        
        self.assertEqual(bin1_merged.getCoverData().data, 80)  # 50 + 30
        
        db1.close()
        db2.close()
    
    def test_merge_new_scopes(self):
        """Test merging with new scopes in source"""
        # Create base database
        db1 = SqliteUCIS()
        top1 = db1.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        dut1 = top1.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Create source with additional scope
        db2 = SqliteUCIS()
        top2 = db2.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        dut2 = top2.createScope("dut", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        mem2 = dut2.createScope("memory", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        cover_data = CoverData(0x01, 0)
        cover_data.data = 100
        mem2.createNextCover("addr_bin", cover_data, None)
        
        # Merge
        stats = db1.merge(db2)
        
        self.assertEqual(stats.scopes_added, 1)  # memory added
        self.assertEqual(stats.coveritems_added, 1)  # addr_bin added
        
        # Verify new scope exists
        top1_merged = list(db1.scopes(ScopeTypeT.INSTANCE))[0]
        dut1_merged = list(top1_merged.scopes(ScopeTypeT.INSTANCE))[0]
        children = list(dut1_merged.scopes(ScopeTypeT.INSTANCE))
        
        self.assertEqual(len(children), 1)
        self.assertEqual(children[0].getScopeName(), "memory")
        
        db1.close()
        db2.close()
    
    def test_merge_file_databases(self):
        """Test merging file-based databases"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db1_path = os.path.join(tmpdir, "db1.cdb")
            db2_path = os.path.join(tmpdir, "db2.cdb")
            merged_path = os.path.join(tmpdir, "merged.cdb")
            
            # Create first database
            db1 = SqliteUCIS(db1_path)
            top1 = db1.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            cover_data = CoverData(0x01, 0)
            cover_data.data = 25
            top1.createNextCover("bin_a", cover_data, None)
            db1.close()
            
            # Create second database
            db2 = SqliteUCIS(db2_path)
            top2 = db2.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            cover_data2 = CoverData(0x01, 0)
            cover_data2.data = 35
            top2.createNextCover("bin_a", cover_data2, None)
            db2.close()
            
            # Merge using convenience function
            stats = merge_databases(db1_path, [db2_path], merged_path)
            
            self.assertEqual(stats.total_hits_added, 35)
            
            # Verify merged database
            merged = SqliteUCIS(merged_path)
            top_merged = list(merged.scopes(ScopeTypeT.INSTANCE))[0]
            bin_merged = list(top_merged.coverItems(-1))[0]
            
            self.assertEqual(bin_merged.getCoverData().data, 60)  # 25 + 35
            
            merged.close()
    
    def test_merge_with_tests(self):
        """Test merge preserves test history"""
        # Create database with test
        db1 = SqliteUCIS()
        test1 = db1.createHistoryNode(None, "test1", None, HistoryNodeKind.TEST)
        test1.setSeed("12345")
        
        # Create second database with test
        db2 = SqliteUCIS()
        test2 = db2.createHistoryNode(None, "test2", None, HistoryNodeKind.TEST)
        test2.setSeed("67890")
        
        # Merge
        stats = db1.merge(db2)
        
        self.assertEqual(stats.tests_merged, 1)
        
        # Verify both tests exist
        tests = list(db1.historyNodes(HistoryNodeKind.TEST))
        self.assertEqual(len(tests), 2)
        
        test_names = {t.getLogicalName() for t in tests}
        self.assertIn("test1", test_names)
        self.assertIn("test2", test_names)
        
        db1.close()
        db2.close()


class TestSqliteAttributes(unittest.TestCase):
    """Tests for user attributes"""
    
    def test_set_get_attribute(self):
        """Test setting and getting attributes"""
        ucis = SqliteUCIS()
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Set attribute
        top.setAttribute("designer", "Alice")
        top.setAttribute("version", "1.0")
        
        # Get attributes
        self.assertEqual(top.getAttribute("designer"), "Alice")
        self.assertEqual(top.getAttribute("version"), "1.0")
        self.assertIsNone(top.getAttribute("nonexistent"))
        
        ucis.close()
    
    def test_get_all_attributes(self):
        """Test getting all attributes"""
        ucis = SqliteUCIS()
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        top.setAttribute("key1", "value1")
        top.setAttribute("key2", "value2")
        top.setAttribute("key3", "value3")
        
        attrs = top.getAttributes()
        
        self.assertEqual(len(attrs), 3)
        self.assertEqual(attrs["key1"], "value1")
        self.assertEqual(attrs["key2"], "value2")
        self.assertEqual(attrs["key3"], "value3")
        
        ucis.close()
    
    def test_delete_attribute(self):
        """Test deleting attributes"""
        ucis = SqliteUCIS()
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        top.setAttribute("temp", "value")
        self.assertEqual(top.getAttribute("temp"), "value")
        
        top.deleteAttribute("temp")
        self.assertIsNone(top.getAttribute("temp"))
        
        ucis.close()
    
    def test_attribute_persistence(self):
        """Test attributes persist across database close/reopen"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            # Create and set attributes
            ucis = SqliteUCIS(db_path)
            top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            top.setAttribute("persistent", "data")
            ucis.close()
            
            # Reopen and verify
            ucis2 = SqliteUCIS(db_path)
            top2 = list(ucis2.scopes(ScopeTypeT.INSTANCE))[0]
            
            self.assertEqual(top2.getAttribute("persistent"), "data")
            
            ucis2.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


class TestSqliteTags(unittest.TestCase):
    """Tests for tags"""
    
    def test_add_remove_tag(self):
        """Test adding and removing tags"""
        ucis = SqliteUCIS()
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        # Add tags
        top.addTag("critical")
        top.addTag("reviewed")
        
        # Check tags
        self.assertTrue(top.hasTag("critical"))
        self.assertTrue(top.hasTag("reviewed"))
        self.assertFalse(top.hasTag("nonexistent"))
        
        # Remove tag
        top.removeTag("reviewed")
        self.assertFalse(top.hasTag("reviewed"))
        
        ucis.close()
    
    def test_get_tags(self):
        """Test getting all tags"""
        ucis = SqliteUCIS()
        top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        top.addTag("tag1")
        top.addTag("tag2")
        top.addTag("tag3")
        
        tags = top.getTags()
        
        self.assertEqual(len(tags), 3)
        self.assertIn("tag1", tags)
        self.assertIn("tag2", tags)
        self.assertIn("tag3", tags)
        
        ucis.close()
    
    def test_find_by_tag(self):
        """Test finding objects by tag"""
        ucis = SqliteUCIS()
        
        scope1 = ucis.createScope("scope1", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        scope2 = ucis.createScope("scope2", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        scope3 = ucis.createScope("scope3", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
        
        scope1.addTag("important")
        scope2.addTag("important")
        scope3.addTag("other")
        
        # Find scopes with "important" tag
        from ucis.sqlite.sqlite_attributes import TagManager
        tag_mgr = TagManager(ucis)
        
        important_ids = tag_mgr.findByTag(ObjectKind.SCOPE, "important")
        
        self.assertEqual(len(important_ids), 2)
        self.assertIn(scope1.scope_id, important_ids)
        self.assertIn(scope2.scope_id, important_ids)
        
        ucis.close()
    
    def test_tag_persistence(self):
        """Test tags persist across database close/reopen"""
        with tempfile.NamedTemporaryFile(suffix='.cdb', delete=False) as f:
            db_path = f.name
        
        try:
            # Create and tag
            ucis = SqliteUCIS(db_path)
            top = ucis.createScope("top", None, 1, SourceT.NONE, ScopeTypeT.INSTANCE, 0)
            top.addTag("persisted")
            ucis.close()
            
            # Reopen and verify
            ucis2 = SqliteUCIS(db_path)
            top2 = list(ucis2.scopes(ScopeTypeT.INSTANCE))[0]
            
            self.assertTrue(top2.hasTag("persisted"))
            
            ucis2.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)


if __name__ == '__main__':
    unittest.main()
