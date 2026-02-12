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
Tests for SqliteCovergroup.createCoverInstance() method.
This test verifies the fix for issue #2 where createCoverInstance was not implemented.
"""

import unittest
import tempfile
import os

from ucis.sqlite import SqliteUCIS
from ucis.mem.mem_ucis import MemUCIS
from ucis.scope_type_t import ScopeTypeT
from ucis.source_t import SourceT
from ucis.source_info import SourceInfo
from ucis.cover_data import CoverData
from ucis.cover_type_t import CoverTypeT
from ucis.flags_t import FlagsT
from ucis.xml.xml_factory import XmlFactory
from ucis.merge.db_merger import DbMerger


class TestSqliteCoverInstance(unittest.TestCase):
    """Tests for createCoverInstance implementation in SqliteCovergroup"""
    
    def test_create_cover_instance_basic(self):
        """Test basic createCoverInstance functionality"""
        ucis = SqliteUCIS()
        
        # Create basic hierarchy
        fh = ucis.createFileHandle("test.sv", os.getcwd())
        si = SourceInfo(fh, 1, 0)
        
        # Create instance scope
        du = ucis.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
        inst = ucis.createInstance("tb", si, 1, SourceT.NONE, ScopeTypeT.INSTANCE, du, FlagsT(0))
        
        # Create covergroup
        cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
        self.assertIsNotNone(cg)
        self.assertEqual(cg.getScopeName(), "cg")
        
        # Create cover instance - this is the method being tested
        cg_inst = cg.createCoverInstance("cg_inst1", si, 1, SourceT.NONE)
        self.assertIsNotNone(cg_inst)
        self.assertEqual(cg_inst.getScopeName(), "cg_inst1")
        self.assertEqual(cg_inst.getScopeType(), ScopeTypeT.COVERINSTANCE)
        
        ucis.close()
    
    def test_create_multiple_cover_instances(self):
        """Test creating multiple cover instances"""
        ucis = SqliteUCIS()
        
        fh = ucis.createFileHandle("test.sv", os.getcwd())
        si = SourceInfo(fh, 1, 0)
        du = ucis.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
        inst = ucis.createInstance("tb", si, 1, SourceT.NONE, ScopeTypeT.INSTANCE, du, FlagsT(0))
        cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
        
        # Create multiple instances
        cg_inst1 = cg.createCoverInstance("inst1", si, 1, SourceT.NONE)
        cg_inst2 = cg.createCoverInstance("inst2", si, 1, SourceT.NONE)
        cg_inst3 = cg.createCoverInstance("inst3", si, 1, SourceT.NONE)
        
        # Verify all instances were created
        instances = list(cg.scopes(ScopeTypeT.COVERINSTANCE))
        self.assertEqual(len(instances), 3)
        
        names = {inst.getScopeName() for inst in instances}
        self.assertEqual(names, {"inst1", "inst2", "inst3"})
        
        ucis.close()
    
    def test_cover_instance_with_coverpoints(self):
        """Test that cover instances can have coverpoints added"""
        ucis = SqliteUCIS()
        
        fh = ucis.createFileHandle("test.sv", os.getcwd())
        si = SourceInfo(fh, 1, 0)
        du = ucis.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
        inst = ucis.createInstance("tb", si, 1, SourceT.NONE, ScopeTypeT.INSTANCE, du, FlagsT(0))
        cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
        cg_inst = cg.createCoverInstance("cg_inst1", si, 1, SourceT.NONE)
        
        # Add coverpoint to instance
        cp = cg_inst.createCoverpoint("cp1", si, 1, SourceT.NONE)
        self.assertIsNotNone(cp)
        self.assertEqual(cp.getScopeName(), "cp1")
        
        # Add bins
        cd = CoverData(CoverTypeT.CVGBIN, 0)
        cd.data = 10
        cd.goal = 1
        cp.createNextCover("bin0", cd, si)
        
        # Verify coverpoint was added
        coverpoints = list(cg_inst.scopes(ScopeTypeT.COVERPOINT))
        self.assertEqual(len(coverpoints), 1)
        self.assertEqual(coverpoints[0].getScopeName(), "cp1")
        
        ucis.close()
    
    def test_dbmerger_with_sqlite(self):
        """Test DbMerger can merge into SqliteUCIS with cover instances"""
        # Create source MemUCIS with cover instances (via XML roundtrip)
        mem_db = MemUCIS()
        fh = mem_db.createFileHandle("test.sv", os.getcwd())
        si = SourceInfo(fh, 1, 0)
        du = mem_db.createScope("tb", si, 1, SourceT.NONE, ScopeTypeT.DU_MODULE, FlagsT(0))
        inst = mem_db.createInstance("tb", si, 1, SourceT.NONE,
                                    ScopeTypeT.INSTANCE, du, FlagsT(0))
        cg = inst.createCovergroup("cg", si, 1, SourceT.NONE)
        cp = cg.createScope("cp", si, 1, SourceT.NONE, ScopeTypeT.COVERPOINT, FlagsT(0))
        cd = CoverData(CoverTypeT.CVGBIN, 0)
        cd.data = 42
        cd.goal = 1
        cp.createNextCover("bin0", cd, si)
        
        # Roundtrip through XML to create COVERINSTANCE structure
        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False) as f:
            xml_path = f.name
        try:
            XmlFactory.write(mem_db, xml_path)
            src_db = XmlFactory.read(xml_path)
        finally:
            os.remove(xml_path)
        
        # Create destination SqliteUCIS and merge
        with tempfile.NamedTemporaryFile(suffix=".ucisdb", delete=False) as f:
            dst_path = f.name
        
        try:
            dst_db = SqliteUCIS(dst_path)
            merger = DbMerger()
            
            # This should not raise NotImplementedError anymore
            merger.merge(dst_db, [src_db])
            
            # Verify merge succeeded by checking structure
            instances = list(dst_db.scopes(ScopeTypeT.INSTANCE))
            self.assertEqual(len(instances), 1)
            self.assertEqual(instances[0].getScopeName(), "tb")
            
            dst_db.close()
        finally:
            if os.path.exists(dst_path):
                os.unlink(dst_path)


if __name__ == '__main__':
    unittest.main()
